import sys
import os
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.app import App
from kivy.graphics.texture import Texture
from kivy.lang import Builder

from utils.POS import POS
from utils.filtering import preprocess_ppg

Builder.load_string("""
<CameraLayout>:
    allow_stretch: True
    size_hint: 1,1
    keep_ratio: True
    canvas.before:
        StencilPush
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10]  # Adjust for roundness
        StencilUse

    canvas:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            texture: self.texture  # Keeps the camera feed
            pos: self.pos
            size: self.size

    canvas.after:
        StencilUnUse
        StencilPop
    
""")

class CameraLayout(Image):
    def __init__(self, **keyargs):
        super().__init__(**keyargs) 

        ## OpenCv Props
        self.signal_value = 0
        self.fps = 30
        self.face_detector = self.setup_face_landmarker()
        self.pose_landmarker = self.setup_pose_landmarker()
        self.capture = cv2.VideoCapture(0)  
        Clock.schedule_interval(self.update, 1.0 / 30) # Update the Camera feed at 30 FPS
        Clock.schedule_interval(self.emit_rppg_signal, 1.0/ 10) # Emit the signal at 10 Hz

        ## Pose Landmarker Props
        self.features = None  # Initialize features attribute
        self.left_x = None
        self.top_y = None
        self.right_x = None
        self.bottom_y = None

        ## Set schedule for Phys signal
        Clock.schedule_interval(self.update_heart_rate, 2)      # every 2s
        Clock.schedule_interval(self.update_hrv, 30)            # every 30s
        Clock.schedule_interval(self.update_resp, 15)           # every 15s
        Clock.schedule_interval(self.update_spo2, 30)           # every 30s
        Clock.schedule_interval(self.update_bar, 30)          # every 30s

        ## Phys signal buffer
        self.combined_r_signal = []
        self.combined_g_signal = []
        self.combined_b_signal = []
        self.r_buffer = []
        self.g_buffer = []
        self.b_buffer = []
        self.rppg_buffer = []
        self.emitting_rppg_buffer = []
        self.resp_buffer = []

    """
      ⭐ Signature Methods

      Metode ini merupakan metode untuk mengirimkan data phyisologi ke widget masing masing untuk ditampilkan.

      Widget sendiri terdapat pada file widgets/phys-box.

    """
    def update_heart_rate(self, dt):
        if len(self.rppg_buffer) > 0:
            app = App.get_running_app()
            app.root.ids.hr_box.update_value(np.array(self.emitting_rppg_buffer))

    def update_hrv(self, dt):
        if len(self.rppg_buffer) > 0:
            app = App.get_running_app()
            app.root.ids.hrv_box.update_value(np.array(self.rppg_buffer))

    def update_resp(self, dt):
        if len(self.rppg_buffer) > 0:
            app = App.get_running_app()
            app.root.ids.resp_box.update_value(np.array(self.resp_buffer))

    def update_spo2(self, dt):
        if len(self.rppg_buffer) > 0:
            app = App.get_running_app()
            app.root.ids.spo2_box.update_value(np.array(self.r_buffer), np.array(self.g_buffer), np.array(self.b_buffer))

    def update_bar(self, dt):
        if len(self.rppg_buffer) > 0:
            app = App.get_running_app()
            app.root.ids.stress_bar.update_value(np.array(self.rppg_buffer))

    def update(self, dt):

        """ Update the camera feed """
        
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.flip(frame, 0)
            ## Store the buffer before displaying into the Kivy
            buffer = frame.tobytes()

            self.detect_face(frame)

            # self.detect_pose(frame)

            ## Texture.create config:
            ## size: The size of the texture in pixels (width, height)
            ## colorfmt: The color format of the texture (one of rgba, rgb, or bgr)
            ## bufferfmt: The buffer format of the texture (one of ‘ubyte’, ‘ushort’, ‘float’)
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt="bgr")
            texture.blit_buffer(buffer, colorfmt="bgr", bufferfmt="ubyte")
            self.texture = texture

            ## If the sample is 30 or 10 seconds long, calculate the rPPG signal
            if len(self.combined_r_signal) == 10 * self.fps:
                temp_r = self.combined_r_signal[:]
                temp_g = self.combined_g_signal[:]
                temp_b = self.combined_b_signal[:]

                self.r_buffer.append(temp_r)
                self.g_buffer.append(temp_g)
                self.b_buffer.append(temp_b)

                self.combined_r_signal.clear()
                self.combined_g_signal.clear()
                self.combined_b_signal.clear()

                self.process_rppg_signal(temp_r, temp_g, temp_b)

    def detect_face(self, frame):
        margin_x = 10  # Adjust horizontally
        scaling_factor = 0.8
        
        ## Detect the face area using shape
        h, w, _ = frame.shape

        ## Converting into RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        ## Seting up the Mediapipe Image
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=image_rgb
        )

        # ## Get the landmarks
        result = self.face_detector.detect(mp_image)

        if result.detections:
            for detection in result.detections:

                ## Get the Bounding box
                bboxC = detection.bounding_box
                x, y, w, h = bboxC.origin_x, bboxC.origin_y, bboxC.width, bboxC.height

                new_x = int(x + margin_x)

                new_w = int(w * scaling_factor)
                new_h = int(h * scaling_factor)

                ## Get the ROI
                face_roi = image_rgb[y:y+new_h, new_x:new_x+new_w]

                ## Calculate the Mean
                mean_rgb = cv2.mean(face_roi)[:3]
                
                # Append the combined RGB values to the respective lists
                self.combined_r_signal.append(mean_rgb[0])
                self.combined_g_signal.append(mean_rgb[1])
                self.combined_b_signal.append(mean_rgb[2])

    def detect_pose(self, frame):
        ## Mediapipe Pose Detection with Optical Flow
        if self.features is None:
            # Initialize ROI and feature detection
            self.initialize_features(frame)

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if len(self.features) > 10:
            new_features, status, error = cv2.calcOpticalFlowPyrLK(self.old_gray, frame_gray, self.features, None, **self.lk_params)
            good_old = self.features[status == 1]
            good_new = new_features[status == 1]
            mask = np.zeros_like(frame)
            for i, (new, old) in enumerate(zip(good_new, good_old)):
                a, b = new.ravel()
                c, d = old.ravel()
                mask = cv2.line(mask, (int(a), int(b)), (int(c), int(d)), (0, 255, 0), 2)
                frame = cv2.circle(frame, (int(a), int(b)), 3, (0, 255, 0), -1)
            frame = cv2.add(frame, mask)
            if len(good_new) > 0:
                avg_y = np.mean(good_new[:, 1])
                self.resp_buffer.append(avg_y)
                self.features = good_new.reshape(-1, 1, 2)
            self.old_gray = frame_gray.copy()
        else:
            # Reinitialize features if tracking fails
            self.initialize_features(frame)


    def process_rppg_signal(self, r, g, b):

        ## Convert the RGB signals to numpy arrays
        rgb_signal = np.array([r, g, b])
        rgb_signal = rgb_signal.reshape(1, 3, - 1) ## Flatten
        rppg_signal = POS(rgb_signal, fps=self.fps) ## Calculate the rPPG signal
        rppg_signal = rppg_signal.reshape(-1) ## Flatten

        rppg_signal = preprocess_ppg(rppg_signal, fs=self.fps) ## Preprocess the rPPG signal

        self.rppg_buffer.append(rppg_signal)  ## Store the rPPG signal

        self.emitting_rppg_buffer.extend(rppg_signal)  ## Emit the rPPG signal

    def setup_pose_landmarker(self):
        """
        Metode untuk menginisialisasi fungsi pose detection dari mediapipe untuk proses resp signal
        """
        model_path = resource_path("models/pose_landmarker.task")
        BaseOptions = mp.tasks.BaseOptions
        PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options_image = PoseLandmarkerOptions(
            base_options=BaseOptions(
                model_asset_path=model_path,
            ),
            running_mode=VisionRunningMode.IMAGE,
            num_poses=1,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            output_segmentation_masks=False
        )
        
        return mp.tasks.vision.PoseLandmarker.create_from_options(options_image)


    def setup_face_landmarker(self):
        ## Create faceDetector Object
        base_model=resource_path("models/blaze_face_short_range.tflite")

        base_options = python.BaseOptions(model_asset_path=base_model)
        FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
        VisionRunningMode = mp.tasks.vision.RunningMode
        options = FaceDetectorOptions(
            base_options=base_options,
            running_mode = VisionRunningMode.IMAGE,
        )
        detector = vision.FaceDetector.create_from_options(options)
        return detector

    def emit_rppg_signal(self, dt):
        """ Emitting the rPPG signal for Preview """
        if self.emitting_rppg_buffer:
            app = App.get_running_app()
            self.signal_value = self.emitting_rppg_buffer.pop(0) 
            app.root.update_stress_signal(self.signal_value)

    def initialize_features(self, frame):
        """
        Metode untuk mendapatkan nilai features untuk keperluan optical flow dan membuat object Lucas Kanade sebagai argument dari optical flow itu sendiri.
        frame: cv2Object = frame sumber dari kamera untuk melakukan deteksi ROI dada dan bahu
        """

        roi_coords = get_initial_roi(frame, self.pose_landmarker)
        self.left_x, self.top_y, self.right_x, self.bottom_y = roi_coords
        old_frame = frame.copy()
        old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
        roi_chest = old_gray[self.top_y:self.bottom_y, self.left_x:self.right_x]
        self.features = cv2.goodFeaturesToTrack(roi_chest, maxCorners=50, qualityLevel=0.2, minDistance=5, blockSize=3)
        if self.features is None:
            raise ValueError("No features found to track!")
        self.features = np.float32(self.features)
        self.features[:,:,0] += self.left_x
        self.features[:,:,1] += self.top_y
        self.old_gray = old_gray
        self.lk_params = dict(winSize=(15, 15), maxLevel=2, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

## The length to be around should width to ensure the landmarks are detected and can proceed to optical flow 
def get_initial_roi(image, landmarker, x_size=100, y_size=30, shift_x=0, shift_y=-30):

    """
    Mengambil ROI dari webcam untuk mendeteksi sinyal respirasi berdasarkan pergerakan posisi bahu pasien.

    Args:
        image (np.ndarray): Frame dari webcam
        pose_landmarker (task): MediaPipe pose detector yang sudah didownload
        x_size (int): Ukuran ROI pada sumbu x
        y_size (int): Ukuran ROI pada sumbu y
        shift_x (int): Pergeseran ROI pada sumbu x (dimana nilai positif akan menggeser ROI ke kanan dan sebaliknya)
        shift_y (int): Pergeseran ROI pada sumbu y (dimana nilai positif akan menggeser ROI ke bawah dan sebaliknya)

    Returns:
        tuple: Koordinat ROI (left_x, top_y, right_x, bottom_y)
    """
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # Mengubah warna BGR ke RGB
    height, width = image.shape[:2] # Mengambil dimensi frame webcam
    
    # Membuat gambar MediaPipe dari frame webcam
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=image_rgb
    )
    
    # Mendeteksi pose dari frame webcam
    detection_result = landmarker.detect(mp_image)
    
    if not detection_result.pose_landmarks:
        raise ValueError("No pose detected in first frame!")
    
    # Mendeteksi tubuh pengguna dari landmark pertama
    landmarks = detection_result.pose_landmarks[0]
    
    # Mengambil landmark bahu kiri dan kanan
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]
    
    # Menghitung posisi tengah dari bahu kiri dan bahu kanan
    center_x = int((left_shoulder.x + right_shoulder.x) * width / 2)
    center_y = int((left_shoulder.y + right_shoulder.y) * height / 2)
    
    # Mengaplikasikan shift terhadap titik tengah
    center_x += shift_x
    center_y += shift_y
    
    # Manghitung batasan ROI berdasarkan posisi tengah dan ukuran ROI
    left_x = max(0, center_x - x_size)
    right_x = min(width, center_x + x_size)
    top_y = max(0, center_y - y_size)
    bottom_y = min(height, center_y + y_size)
    
    # Mevalidasi ukuran ROI
    if (right_x - left_x) <= 0 or (bottom_y - top_y) <= 0:
        raise ValueError("Invalid ROI dimensions")
        
    return (left_x, top_y, right_x, bottom_y)


""" For building reference path PyInstaller"""
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
