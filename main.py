# Mengimport library yang diperlukan untuk tugas besar ini
import sys
import numpy as np
import cv2
import mediapipe as mp
from collections import Counter
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
import pyqtgraph as pg
import scipy
from scipy.signal import butter, filtfilt, find_peaks
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from utils.rppg_method import POS

class HRVMonitoring(QWidget):
    """
    Main Kelas untuk menampilkan GUI dan menghitung detak jantung dan pernapasan secara real-time.
    Kelas ini akan menyimpan nilai sinyal rppg dan nilai sinyal pernafasan dari pose detection
    """
    def __init__(self):
        super().__init__()
        self.initUI()

        ## Platform Specific Camera Backend
        video_backend = cv2.CAP_DSHOW if sys.platform == 'win32' else cv2.CAP_AVFOUNDATION # Menggunakan CAP_DSHOW untuk Windows dan CAP_AVFOUNDATION untuk macOS
        self.cap = cv2.VideoCapture(0, video_backend)  
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        if self.fps == 0:
            self.fps = 30  

        ## Properties HRV Features  
        self.baevsky_index = None
        self.len_cleaned_rr_peaks = None
        self.rmssd = None
        self.sdnn = None
        self.freq_ratio = None

        ## Properties Mediapipe
        self.window_size = self.fps * 120 # 2 minutes
        self.face_landmarker = self.initialize_face_landmarker()
        self.f_count = 0
        
        ## Properties List RGB Value
        self.baevsky_r_signal, self.baevsky_g_signal, self.baevsky_b_signal = [], [], [] 
        self.baevsky_rppg_signal = None

        ## Properties Window
        self.window_0_r, self.window_0_g, self.window_0_b = [], [], [] # 0 Seconds Start
        self.window_1_r, self.window_1_g, self.window_1_b = [], [], [] # 30 Seconds Start   
        self.window_2_r, self.window_2_g, self.window_2_b = [], [], [] # 60 Seconds Start
        self.window_3_r, self.window_3_g, self.window_3_b = [], [], [] # 90 Seconds Start
        
        self.window_0_combined, self.window_1_combined, self.window_2_combined, self.window_3_combined = [], [], [], []

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1000 // int(self.fps))

    def initUI(self):
        """
        Metode untuk mempersiapkan kelas PyQT sebagai GUI untuk overlay dari feed live time video dan sinyal (rppg + resp)
        Karena kelas merupakan anak dari QWidget, untuk insialisasi tidak perlu menggunakan keyword QWidget.
        """
        self.setWindowTitle('HRV Stress Monitor')
        self.setGeometry(100, 100, 1200, 800)

        ## Prepare Plot for Combining with Layout 
        self.video_label = QLabel(self)
        self.hr_label = QLabel('Heart Rate: -- BPM (Beat Per Minute)', self)
        self.hr_label.setAlignment(Qt.AlignCenter)
        self.baevsky_label = QLabel('Baevsky Stress Index', self)
        self.baevsky_label.setAlignment(Qt.AlignCenter)
        self.rr_interval_label = QLabel('Len RR-Interval', self)
        self.rr_interval_label.setAlignment(Qt.AlignCenter)
        self.rmssd_label = QLabel('RMSSD', self)
        self.rmssd_label.setAlignment(Qt.AlignCenter)
        self.sdnn_label = QLabel('SDNN', self)
        self.sdnn_label.setAlignment(Qt.AlignCenter)
        self.freq_ratio_label = QLabel('Frequency Ratio', self)
        self.freq_ratio_label.setAlignment(Qt.AlignCenter)

        # self.plot_widget_hr = pg.PlotWidget()
        # self.plot_widget_hr.setYRange(-3, 3)
        # self.plot_curve_hr = self.plot_widget_hr.plot()

        ## Making Layout instance and insert the plot into the layout
        left_layout = QVBoxLayout()
        # left_layout.addWidget(self.plot_widget_hr)
        left_layout.addWidget(self.baevsky_label)
        left_layout.addWidget(self.rr_interval_label)
        left_layout.addWidget(self.rmssd_label)
        left_layout.addWidget(self.sdnn_label)
        left_layout.addWidget(self.freq_ratio_label)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.video_label)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)
    
    def initialize_face_landmarker(self):
        ## Create Facelandmarker Object
        base_options = python.BaseOptions(model_asset_path="Models/face_landmarker.task")
        VisionRunningMode = mp.tasks.vision.RunningMode
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            num_faces=1,
            running_mode = VisionRunningMode.IMAGE,
        )
        detector = vision.FaceLandmarker.create_from_options(options)
        return detector

    def update_frame(self):
        """
        Metode penting dalam kelas ini, akan diambi frame orng lalu ditentukan beberapa proses seperti 
        deteksi wajah dengan mediapipe dan pose detection, lalu menentukan bounding box untuk proses selanjutnya.
        Untuk RPPG ditetapkan daerah dahi sebagai ROI, dan untuk Resp signal ditetapkan daerah sekitar baru sebagai ROI.
        Untuk Pose Detection akan diterapkan Optical Flow untuk mengurangi kinerja beban tracking setiap frame.
        """

        ret, frame = self.cap.read()
        if not ret:
            return
        
        current_time = self.f_count / self.fps
        print("Current Time:", current_time)

        self.f_count += 1
        print

        ### 3. Mendeteksi area wajah menggunakan mediapipe
        h, w, _ = frame.shape
        
        ### 3.1 Mengkonversi frame ke RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=frame_rgb
        )

        result = self.face_landmarker.detect(mp_image)

        if result.face_landmarks:
            for face_landmark in result.face_landmarks:
                # Get cheek ROIs
                left_cheek_rect, right_cheek_rect = get_cheek_rois(face_landmark, frame.shape)

                # Draw ROI rectangles
                cv2.rectangle(frame, (left_cheek_rect[0], left_cheek_rect[1]), (left_cheek_rect[2], left_cheek_rect[3]), (0, 255, 0), 2)
                cv2.rectangle(frame, (right_cheek_rect[0], right_cheek_rect[1]), (right_cheek_rect[2], right_cheek_rect[3]), (0, 255, 0), 2)

                # Extract RGB values from ROIs
                left_cheek_roi = extract_rgb_from_rect(left_cheek_rect, frame)
                right_cheek_roi = extract_rgb_from_rect(right_cheek_rect, frame)

                # Calculate mean RGB values
                left_cheek_rgb = cv2.mean(left_cheek_roi)[:3]
                right_cheek_rgb = cv2.mean(right_cheek_roi)[:3]

                ## Combined and average from both cheeks
                combined_r = (left_cheek_rgb[0] + right_cheek_rgb[0]) / 2
                combined_g = (left_cheek_rgb[1] + right_cheek_rgb[1]) / 2
                combined_b = (left_cheek_rgb[2] + right_cheek_rgb[2]) / 2

                ## Append RGB values to the baevsky
                self.baevsky_r_signal.append(combined_r)
                self.baevsky_g_signal.append(combined_g)
                self.baevsky_b_signal.append(combined_b)

                ## Calculate the Baevsky Stress Index every 30 seconds
                if self.f_count != 0 and self.f_count % (self.fps * 30) == 0:
                    self.baevsky_rppg_signal = np.array([self.baevsky_r_signal, self.baevsky_g_signal, self.baevsky_b_signal])
                    self.baevsky_rppg_signal = self.baevsky_rppg_signal.reshape(1, 3, -1)
                    self.baevsky_rppg_signal = POS(self.baevsky_rppg_signal, fps=35)
                    self.baevsky_rppg_signal = self.baevsky_rppg_signal.reshape(-1)

                    ## Reset the RGB Signal
                    self.baevsky_r_signal, self.baevsky_g_signal, self.baevsky_b_signal = [], [], []

                                        # Preprocess the PPG signal
                    ppg_signal = preprocess_ppg(self.baevsky_rppg_signal, fs=35)

                    ## Clean the RR Interval
                    rr_intervals = clean_rr_adaptive(ppg_signal)

                    # Get the RR intervals
                    rr_intervals = get_rr_interval(ppg_signal, fs=35) * 1000.0  # Convert to milliseconds

                    # Step 1: Calculate Mode (Mo)
                    # unique_rr, counts = np.unique(rr_intervals, return_counts=True)
                    # mode_rr = unique_rr[np.argmax(counts)]
                    rounded_intervals = np.round(rr_intervals / 50) * 50
                    mode_value = Counter(rounded_intervals).most_common(1)[0][0]

                    # Calculate AMo (Amplitude of Mode)
                    # Count intervals within ±50ms of mode
                    intervals_in_mode_range = np.sum(
                        (rr_intervals >= mode_value - 50) & 
                        (rr_intervals <= mode_value + 50)
                    )
                    amo_percent = (intervals_in_mode_range / len(rr_intervals)) * 100

                    # Calculate MxDMn (Variation Range)
                    variation_range = np.max(rr_intervals) - np.min(rr_intervals)

                    # Calculate Stress Index
                    # Note: AMo is already in percentage, so we don't multiply by 100 again
                    baevsky_stress_index = amo_percent / (2 * mode_value * variation_range)

                    ## Scale by 10^6 since the units are % / (ms * ms)
                    baevsky_stress_index *= 10**6

                    ## Set the Baevsky Stress Index to the Label
                    self.baevsky_label.setText(f'Baevsky Stress Index: {baevsky_stress_index:.2f}')

                ## Window 0 (Starts at 00:00)
                if current_time >= 0:
                    self.window_0_r.append(combined_r)
                    self.window_0_g.append(combined_g)
                    self.window_0_b.append(combined_b)

                    if len(self.window_0_r) >= self.window_size:
                        self.window_0_combined = np.array([self.window_0_r, self.window_0_g, self.window_0_b])
                        self.window_0_combined = self.window_0_combined.reshape(1, 3, -1)
                        self.window_0_combined = POS(self.window_0_combined, fps=35)
                        self.window_0_combined = self.window_0_combined.reshape(-1)
                    
                        self.window_0_r, self.window_0_g, self.window_0_b = [], [], []

                        ## Preprocess the signal
                        self.window_0_combined = preprocess_ppg(self.window_0_combined, fs=35)

                        ## Get and Clean the RR Interval
                        self.len_cleaned_rr_peaks = get_rr_interval(self.window_0_combined)
                        self.len_cleaned_rr_peaks = clean_rr_adaptive(self.len_cleaned_rr_peaks)

                        ## Put the Label on the RR Peaks
                        self.rr_interval_label.setText(f'Len RR-Interval: {len(self.len_cleaned_rr_peaks)}')    

                        ## Extract Time Features
                        time_features = extract_time_features(self.len_cleaned_rr_peaks)
                        self.rmssd = time_features['rmssd']
                        self.sdnn = time_features['sdnn']
                        
                        ## Put the label on the RMSSD and SDNN
                        self.rmssd_label.setText(f'RMSSD: {self.rmssd:.2f} ms')
                        self.sdnn_label.setText(f'SDNN: {self.sdnn:.2f} ms')

                        ## Extract Frequency Features
                        freq_features = frequency_analysis(self.len_cleaned_rr_peaks, fs_interp=4.0)
                        self.freq_ratio = freq_features['lf_hf_ratio']

                        ## Put the label on the Frequency Ratio
                        self.freq_ratio_label.setText(f'Frequency Ratio: {self.freq_ratio:.2f}')
                
                ## Window 1 (Starts at 00:30)
                if current_time >= 30:
                    self.window_1_r.append(combined_r)
                    self.window_1_g.append(combined_g)
                    self.window_1_b.append(combined_b)

                    if len(self.window_1_r) >= self.window_size:
                        self.window_1_combined = np.array([self.window_1_r, self.window_1_g, self.window_1_b])
                        self.window_1_combined = self.window_1_combined.reshape(1, 3, -1)
                        self.window_1_combined = POS(self.window_1_combined, fps=35)
                        self.window_1_combined = self.window_1_combined.reshape(-1)
                    
                        self.window_1_r, self.window_1_g, self.window_1_b = [], [], []

                        ## Preprocess the signal
                        self.window_1_combined = preprocess_ppg(self.window_1_combined, fs=35)

                        ## Get and Clean the RR Interval
                        self.len_cleaned_rr_peaks = get_rr_interval(self.window_1_combined)
                        self.len_cleaned_rr_peaks = clean_rr_adaptive(self.len_cleaned_rr_peaks)

                        ## Put the Label on the RR Peaks
                        self.rr_interval_label.setText(f'Len RR-Interval: {len(self.len_cleaned_rr_peaks)}')    

                        ## Extract Time Features
                        time_features = extract_time_features(self.len_cleaned_rr_peaks)
                        self.rmssd = time_features['rmssd']
                        self.sdnn = time_features['sdnn']
                        
                        ## Put the label on the RMSSD and SDNN
                        self.rmssd_label.setText(f'RMSSD: {self.rmssd:.2f} ms')
                        self.sdnn_label.setText(f'SDNN: {self.sdnn:.2f} ms')

                        ## Extract Frequency Features
                        freq_features = frequency_analysis(self.len_cleaned_rr_peaks, fs_interp=4.0)
                        self.freq_ratio = freq_features['lf_hf_ratio']

                        ## Put the label on the Frequency Ratio
                        self.freq_ratio_label.setText(f'Frequency Ratio: {self.freq_ratio:.2f}')

                ## Window 2 (Starts at 01:00)
                if current_time >= 60:
                    self.window_2_r.append(combined_r)
                    self.window_2_g.append(combined_g)
                    self.window_2_b.append(combined_b)

                    if len(self.window_2_r) >= self.window_size:
                        self.window_2_combined = np.array([self.window_2_r, self.window_2_g, self.window_2_b])
                        self.window_2_combined = self.window_2_combined.reshape(1, 3, -1)
                        self.window_2_combined = POS(self.window_2_combined, fps=35)
                        self.window_2_combined = self.window_2_combined.reshape(-1)
                    
                        self.window_2_r, self.window_2_g, self.window_2_b = [], [], []

                        ## Preprocess the signal
                        self.window_2_combined = preprocess_ppg(self.window_2_combined, fs=35)

                        ## Get and Clean the RR Interval
                        self.len_cleaned_rr_peaks = get_rr_interval(self.window_2_combined)
                        self.len_cleaned_rr_peaks = clean_rr_adaptive(self.len_cleaned_rr_peaks)

                        ## Put the Label on the RR Peaks
                        self.rr_interval_label.setText(f'Len RR-Interval: {len(self.len_cleaned_rr_peaks)}')    

                        ## Extract Time Features
                        time_features = extract_time_features(self.len_cleaned_rr_peaks)
                        self.rmssd = time_features['rmssd']
                        self.sdnn = time_features['sdnn']
                        
                        ## Put the label on the RMSSD and SDNN
                        self.rmssd_label.setText(f'RMSSD: {self.rmssd:.2f} ms')
                        self.sdnn_label.setText(f'SDNN: {self.sdnn:.2f} ms')

                        ## Extract Frequency Features
                        freq_features = frequency_analysis(self.len_cleaned_rr_peaks, fs_interp=4.0)
                        self.freq_ratio = freq_features['lf_hf_ratio']

                        ## Put the label on the Frequency Ratio
                        self.freq_ratio_label.setText(f'Frequency Ratio: {self.freq_ratio:.2f}')

                ## Window 3 (Starts at 01:30)
                if current_time >= 90:
                    self.window_3_r.append(combined_r)
                    self.window_3_g.append(combined_g)
                    self.window_3_b.append(combined_b)

                    if len(self.window_3_r) >= self.window_size:
                        self.window_3_combined = np.array([self.window_3_r, self.window_3_g, self.window_3_b])
                        self.window_3_combined = self.window_3_combined.reshape(1, 3, -1)
                        self.window_3_combined = POS(self.window_3_combined, fps=35)
                        self.window_3_combined = self.window_3_combined.reshape(-1)
                    
                        self.window_3_r, self.window_3_g, self.window_3_b = [], [], []

                        ## Preprocess the signal
                        self.window_3_combined = preprocess_ppg(self.window_3_combined, fs=35)

                        ## Get and Clean the RR Interval
                        self.len_cleaned_rr_peaks = get_rr_interval(self.window_1_combined)
                        self.len_cleaned_rr_peaks = clean_rr_adaptive(self.len_cleaned_rr_peaks)

                        ## Put the Label on the RR Peaks
                        self.rr_interval_label.setText(f'Len RR-Interval: {len(self.len_cleaned_rr_peaks)}')    

                        ## Extract Time Features
                        time_features = extract_time_features(self.len_cleaned_rr_peaks)
                        self.rmssd = time_features['rmssd']
                        self.sdnn = time_features['sdnn']
                        
                        ## Put the label on the RMSSD and SDNN
                        self.rmssd_label.setText(f'RMSSD: {self.rmssd:.2f} ms')
                        self.sdnn_label.setText(f'SDNN: {self.sdnn:.2f} ms')

                        ## Extract Frequency Features
                        freq_features = frequency_analysis(self.len_cleaned_rr_peaks, fs_interp=4.0)
                        self.freq_ratio = freq_features['lf_hf_ratio']

                        ## Put the label on the Frequency Ratio
                        self.freq_ratio_label.setText(f'Frequency Ratio: {self.freq_ratio:.2f}')

        # Convert frame to RGB for displaying in video_label
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(image))

    def closeEvent(self, event):
        """
        Metode turunan dari kelas QWidget untuk melepaskan resource yang tidak dibutuhkan lagi.
        """
        self.cap.release()
        cv2.destroyAllWindows()
        event.accept()

""" Helper Method 

Collection of helper methods for the main class
Before doing Refactoring

"""
def preprocess_ppg(signal, fs = 35):
    """ Computes the Preprocessed PPG Signal, this steps include the following:
        1. Moving Average Smoothing
        2. Bandpass Filtering
        3. Normalization
        
        Parameters:
        ----------
        signal (numpy array): 
            The PPG Signal to be preprocessed
        fs (float): 
            The Sampling Frequency of the Signal
            
        Returns:
        --------
        numpy array: 
            The Preprocessed PPG Signal
    
    """ 

    ## Moving Average Smoothing
    window = int(fs * 0.15)  # 150ms window
    smoothed_signal = np.convolve(signal, np.ones(window)/window, mode='same')

    b, a = scipy.signal.butter(3, [0.8, 2.0], btype='band', fs=fs)
    filtered = scipy.signal.filtfilt(b, a, smoothed_signal)
    
    # Additional lowpass to remove high-frequency noise
    b2, a2 = scipy.signal.butter(3, 2.5, btype='low', fs=fs)
    filtered = scipy.signal.filtfilt(b2, a2, filtered)
    
    # Moving average smoothing
    window = int(fs * 0.15)  # 150ms window
    filtered_signal = np.convolve(filtered, np.ones(window)/window, mode='same')

    # Normalize using Standard Deviation
    normalized_signal = (filtered_signal - filtered_signal.mean()) / filtered_signal.std()

    return normalized_signal

def get_rr_interval(signal, fs = 35):
    """Computes the distance between each peak in the signal

    Parameters:
    ----------
    signal (numpy array): 
        The PPG Signal to be preprocessed
    fs (float):
        The Sampling Frequency of the Signal
    
    Returns:
    --------
    numpy array: 
        The RR Interval Signal
    
    Notes:
    ------
    Since the signal is already being preprocessed and normalize around 0 and 1, 
    It suppose have the maximum amplitude peak at 1. 
    .
    Using the adaptive thresholding method to detect the peaks in the signal
    should potentially give a better result with different threshold on the moving window.

    """

    ## Adaptive thresholding
    window_size = fs * 2  # 2-second window
    rolling_mean = np.convolve(signal,
                              np.ones(window_size)/window_size, 
                              mode='same')
    adaptive_threshold = rolling_mean + 0.5 * np.std(signal)

    peaks, properties = scipy.signal.find_peaks(signal,
                                               distance=fs * 0.5, # 0.5-second distance between peaks   
                                               prominence=0.1,  # Consider peak prominence
                                               height=adaptive_threshold)
    ## Convert into time
    rr_interval = np.diff(peaks) / fs # * 1000.0 - in milliseconds

    return rr_interval

def clean_rr_adaptive(rr_intervals, quality_metric=None):
    """
    Adaptive RR interval cleaning based on signal quality
    """
    # Initial basic range (conservative)
    MIN_RR = 0.6  # 100 BPM
    MAX_RR = 1.2  # 50 BPM
    
    # Step 1: Remove extreme outliers
    valid_rr = rr_intervals[(rr_intervals >= MIN_RR) & (rr_intervals <= MAX_RR)]
    
    if len(valid_rr) < 3:
        return valid_rr
        
    # Step 2: Statistical validation
    mean_rr = np.mean(valid_rr)
    std_rr = np.std(valid_rr)
    
    # Adjust thresholds based on signal quality
    if quality_metric is None:
        # Use coefficient of variation as quality metric
        quality_metric = std_rr / mean_rr
    
    # Adaptive thresholds
    threshold_multiplier = 1.0 + quality_metric
    valid_range = threshold_multiplier * std_rr
    
    # Step 3: Remove statistical outliers
    valid_rr = valid_rr[np.abs(valid_rr - mean_rr) <= valid_range]
    
    # Step 4: Check sequential differences
    if len(valid_rr) >= 2:
        diff_threshold = 0.3 * mean_rr  # Allow 30% change
        rr_diff = np.abs(np.diff(valid_rr))
        valid_indices = np.where(rr_diff < diff_threshold)[0]
        valid_rr = valid_rr[valid_indices]
    
    return valid_rr

def get_cheek_rois(landmarks, image_shape):
    h, w, _ = image_shape
    left_cheek_indices = [111, 121, 50, 142]
    right_cheek_indices = [350, 340, 355, 280]

    left_cheek_points = [(int(landmarks[idx].x * w), int(landmarks[idx].y * h)) for idx in left_cheek_indices]
    right_cheek_points = [(int(landmarks[idx].x * w), int(landmarks[idx].y * h)) for idx in right_cheek_indices]

    left_cheek_rect = (
        min([pt[0] for pt in left_cheek_points]), min([pt[1] for pt in left_cheek_points]),
        max([pt[0] for pt in left_cheek_points]), max([pt[1] for pt in left_cheek_points])
    )
    # print("Left Cheek Rect:", left_cheek_rect)
    right_cheek_rect = (
        min([pt[0] for pt in right_cheek_points]), min([pt[1] for pt in right_cheek_points]),
        max([pt[0] for pt in right_cheek_points]), max([pt[1] for pt in right_cheek_points])
    )
    # print("Right Cheek Rect:", right_cheek_rect)

    return left_cheek_rect, right_cheek_rect

def extract_rgb_from_rect(rect, image):
    x_min, y_min, x_max, y_max = rect
    roi = image[y_min:y_max, x_min:x_max]
    return roi

def extract_time_features(rr_intervals):
    """Extract time-domain features from the RR intervals

    Parameters:
    ----------
    rr_intervals (numpy array): 
        The RR Interval Signal

    Returns:    
    --------
    dict: 
        Dictionary containing the extracted features

    """
    features = { # Convert into seconds
        'mean_rr': np.mean(rr_intervals) * 1000,
        'sdnn': np.std(rr_intervals) * 1000,
        'rmssd': np.sqrt(np.mean(np.diff(rr_intervals)**2)) * 1000,
        'pnn50': (np.diff(rr_intervals) > 0.05).mean() * 100,
        'hr': 60 / np.mean(rr_intervals)
    }
    return features

def frequency_analysis(rr_intervals, fs_interp=4.0):
    """Extract frequency-domain features from the RR intervals

    Parameters:
    ----------
    rr_intervals (numpy array): 
        The RR Interval Signal
    fs_interp (float):
        The Interpolated Sampling Frequency

    Returns:
    --------
    dict: 
        Dictionary containing the extracted features

    """
    # Interpolate to uniform sampling
    time_points = np.cumsum(rr_intervals)
    f_interp = scipy.interpolate.interp1d(time_points, rr_intervals, kind='cubic')
    
    # Create uniform time axis
    t_uniform = np.arange(time_points[0], time_points[-1], 1/fs_interp)
    rr_uniform = f_interp(t_uniform)
    
    # Welch's method
    frequencies, psd = scipy.signal.welch(rr_uniform, fs=fs_interp, nperseg=256)
    
    # Calculate frequency bands
    vlf = np.trapz(psd[(frequencies >= 0.0033) & (frequencies < 0.04)])
    lf = np.trapz(psd[(frequencies >= 0.04) & (frequencies < 0.15)])
    hf = np.trapz(psd[(frequencies >= 0.15) & (frequencies < 0.4)])

    ## Plot the PSD in more detail for each frequency band
    # plt.figure(figsize=(20, 5))
    # plt.plot(frequencies, psd)
    # plt.fill_between(frequencies, psd, where=(frequencies >= 0.0033) & (frequencies < 0.04), color='red', alpha=0.5)
    # plt.fill_between(frequencies, psd, where=(frequencies >= 0.04) & (frequencies < 0.15), color='green', alpha=0.5)
    # plt.fill_between(frequencies, psd, where=(frequencies >= 0.15) & (frequencies < 0.4), color='blue', alpha=0.5)
    # plt.title("Power Spectral Density")
    # plt.xlabel("Frequency (Hz)")
    # plt.ylabel("Power")
    # plt.show()
    
    
    return {'vlf': vlf, 'lf': lf, 'hf': hf, 'lf_hf_ratio': lf/hf}

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = HRVMonitoring()
    ex.show()
    sys.exit(app.exec_())