from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.image import Image
import cv2
from kivy.app import App
from kivy.graphics.texture import Texture

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

## Import Signal Processing
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

from utils.filtering import preprocess_ppg

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class CameraLayout(Image):
    def __init__(self, **keyargs):
        super().__init__(**keyargs) ## KV Files config
        self.signal_value = 0
        self.fps = 30
        self.detector = self.setup_face_landmarker()
        self.capture = cv2.VideoCapture(0)  ## Start the Camera
        Clock.schedule_interval(self.update, 1.0 / 30) ## Update the Camera feed at 30 FPS
        Clock.schedule_interval(self.emit_rppg_signal, 1.0/ 10) ## Emit the signal at 10 Hz


        ## Set schedule for Phys signal
        Clock.schedule_interval(self.update_heart_rate, 2)      # every 2s
        Clock.schedule_interval(self.update_hrv, 30)            # every 30s
        Clock.schedule_interval(self.update_resp, 15)           # every 15s
        Clock.schedule_interval(self.update_spo2, 30)           # every 30s

        self.combined_r_signal = []
        self.combined_g_signal = []
        self.combined_b_signal = []
        self.rppg_buffer = []
        self.emitting_rppg_buffer = []

    def update_heart_rate(self, dt):
        if len(self.rppg_buffer) > 0:
            app = App.get_running_app()
            app.root.ids.hr_box.update_value(np.array(self.emitting_rppg_buffer))

    def update_hrv(self, dt):
        if len(self.rppg_buffer) > 0:
            app = App.get_running_app()
            app.root.ids.hrv_box.update_value(np.array(self.emitting_rppg_buffer))

    def update_resp(self, dt):
        if len(self.rppg_buffer) > 0:
            app = App.get_running_app()
            app.root.ids.resp_box.update_value(np.array(self.emitting_rppg_buffer))

    def update_spo2(self, dt):
        if len(self.rppg_buffer) > 0:
            app = App.get_running_app()
            app.root.ids.spo2_box.update_value(np.array(self.emitting_rppg_buffer))

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

        # ## Get the landkmarks
        result = self.detector.detect(mp_image)

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

    def emit_rppg_signal(self, dt):
        if self.emitting_rppg_buffer:
            app = App.get_running_app()
            self.signal_value = self.emitting_rppg_buffer.pop(0) # Emit the rPPG signal
            app.root.update_stress_signal(self.signal_value)


    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.flip(frame, 0)
            ## Store the buffer before displaying into the Kivy
            buffer = frame.tobytes()

            self.detect_face(frame)

            ## Texture.create config:
            ## size: The size of the texture in pixels (width, height)
            ## colorfmt: The color format of the texture (one of rgba, rgb, or bgr)
            ## bufferfmt: The buffer format of the texture (one of ‘ubyte’, ‘ushort’, ‘float’)
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt="bgr")
            texture.blit_buffer(buffer, colorfmt="bgr", bufferfmt="ubyte")
            self.texture = texture

            ## If the sample is 30 or 10 seconds long, calculate the rPPG signal
            if len(self.combined_r_signal) == 5 * self.fps:
                temp_r = self.combined_r_signal[:]
                temp_g = self.combined_g_signal[:]
                temp_b = self.combined_b_signal[:]

                self.combined_r_signal.clear()
                self.combined_g_signal.clear()
                self.combined_b_signal.clear()

                self.process_rppg_signal(temp_r, temp_g, temp_b)

    def process_rppg_signal(self, r, g, b):

        ## Convert the RGB signals to numpy arrays
        rgb_signal = np.array([r, g, b])
        rgb_signal = rgb_signal.reshape(1, 3, - 1) ## Flatten
        rppg_signal = POS(rgb_signal, fps=self.fps) ## Calculate the rPPG signal
        rppg_signal = rppg_signal.reshape(-1) ## Flatten

        rppg_signal = preprocess_ppg(rppg_signal, fs=self.fps) ## Preprocess the rPPG signal

        self.rppg_buffer.append(rppg_signal)  ## Store the rPPG signal

        self.emitting_rppg_buffer.extend(rppg_signal)  ## Emit the rPPG signal

class StressMonitorLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)  

        self.lines = []
        self.signal_values = []  # Store rPPG values
        self.time_values = []  # Time tracking
        self.time_index  = 0

        ## Getting the ID
        self.figure_wgt = self.ids.figure_hr

        ## Generate figure
        self.fig, self.ax1 = plt.subplots(1, 1)
        self.fig.subplots_adjust(left=0.13, top=0.96, right=0.93, bottom=0.2)
        self.figure_wgt.figure = self.fig

        Clock.schedule_interval(self.update_graph, 1.0 / 0.5) ## 300 Frame in 30 Fps = 10 second
 
    def update_stress_signal(self, value):
        """ This method receives the simulated rPPG signal and updates the graph """
        self.signal_values.append(value)
        self.time_values.append(self.time_index)
        self.time_index += 1

        ## Keep only the last 100 points for a rolling window effect

        ## Store only for 30 seconds?
        if len(self.signal_values) > 1800:
            self.signal_values.pop(0)
            self.lines.pop(0)
            self.time_values.pop(0)

    def update_graph(self, dt):

        if len(self.signal_values) > 1:
            line = self.ax1.plot(self.time_values, self.signal_values, color='b', label='rPPG Signal')
            self.lines.append(line)
            self.figure_wgt.register_lines(self.lines)
            self.figure_wgt.figure.canvas.draw_idle()  # Refresh the figure            

## Core method POS 
def POS(signal, **kargs):
    """
    POS method on CPU using Numpy.

    The dictionary parameters are: {'fps':float}.

    Wang, W., den Brinker, A. C., Stuijk, S., & de Haan, G. (2016). Algorithmic principles of remote PPG. IEEE Transactions on Biomedical Engineering, 64(7), 1479-1491. 
    """
    """
    eps: A small constant (10^-9) used to prevent division by zero in normalization steps.
    X: The input signal, which is a 3D array where:
    e: Number of estimators or regions in the frame (like different parts of the face).
    c: Color channels (3 for RGB).
    f: Number of frames.
    w: Window length, determined by the camera's frame rate (fps). For example, at 20 fps, w would be 32 (which corresponds to about 1.6 seconds of video).
    """
    eps = 10**-9
    X = signal
    e, c, f = X.shape # Number of estimators, color channels, and frames
    w = int(1.6 * kargs['fps']) # Window length in frames

    """
    P: A fixed 2x3 matrix used for the projection step. It defines how to transform the color channels (RGB) into a new space.
    Q: This is a stack of the matrix P repeated e times, where each P corresponds to an estimator (region of interest) in the video.
    """
    P = np.array([[0, 1, -1], [-2, 1, 1]]) ## Pulse Rate Matricies
    Q = np.stack([P for _ in range(e)], axis = 0)

    """
    H: A matrix to store the estimated heart rate signal over time for each estimator.
    n: The current frame in the sliding window.
    m: The start index of the sliding window (calculating which frames are part of the current window).
    """
    H = np.zeros((e, f))
    for n in np.arange(w, f):
        # Start index of sliding window 
        m = n - w + 1

        """
        Temporal Normalization (Equation 5 from the paper): This step ensures that the signal is invariant to global lighting changes and other noise factors.
        """
        Cn = X[:, :, m:(n+1)]
        M = 1.0 / (np.mean(Cn, axis = 2) + eps)
        M = np.expand_dims(M, axis=2) # shape [e, c, w]
        Cn = np.multiply(Cn, M)

        """
        Projection (Equation 6 from the paper): This step transforms the RGB values into a space where the signal from blood flow (heart rate) is more distinct.
        """
        S = np.dot(Q, Cn)
        S = S[0, :, :, :]
        S = np.swapaxes(S, 0, 1) 

        """
        Tuning (Equation 7 from the paper): This step adjusts the projected components to make the heart rate signal clearer.
        """
        S1 = S[:, 0, :]
        S2 = S[:, 1, :]
        alpha = np.std(S1, axis=1) / (eps + np.std(S2, axis=1))
        alpha - np.expand_dims(alpha, axis=1)
        Hn = np.add(S1, alpha * S2)
        Hnm = Hn - np.expand_dims(np.mean(Hn, axis=1), axis=1)

        """
        Overlap-Adding (Equation 8 from the paper): This step combines the processed signals from each frame to form the final output heart rate signal.
        """
        H[:, m:(n + 1)] = np.add(H[:, m:(n + 1)], Hnm)  # Add the tuned signal to the output matrix

    return H