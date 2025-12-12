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
from kivy.properties import BooleanProperty
import datetime
from scipy import signal as scipy_signal

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

        # Overlay when paused
        Color:
            rgba: (0, 0, 0, 0.6) if not self.camera_active else (0, 0, 0, 0)
        Rectangle:
            pos: self.pos
            size: self.size

    canvas.after:
        StencilUnUse
        StencilPop
    
""")

class CameraLayout(Image):
    camera_active = BooleanProperty(True)  # Track camera state
    face_detected = BooleanProperty(True)

    def __init__(self, **keyargs):
        super().__init__(**keyargs)
        self.signal_value = 0
        self.fps = 30
        self.face_detector = self.setup_face_detector()
        self.capture = cv2.VideoCapture(0)
        self._camera_event = Clock.schedule_interval(self.update, 1.0 / 30)
        self._rppg_event = Clock.schedule_interval(self.emit_rppg_signal, 1.0 / 10)
        Clock.schedule_interval(self.send_data_log, 20)
        Clock.schedule_interval(self.update_heart_rate, 10)
        Clock.schedule_interval(self.update_hrv, 15)

        self.combined_r_signal = []
        self.combined_g_signal = []
        self.combined_b_signal = []
        self.emitting_rppg_buffer = []

    def toggle_camera(self):
        self.camera_active = not self.camera_active
        if self.camera_active:
            if not self._camera_event:
                self._camera_event = Clock.schedule_interval(self.update, 1.0 / 30)
            if not self._rppg_event:
                self._rppg_event = Clock.schedule_interval(self.emit_rppg_signal, 1.0 / 10)
        else:
            if self._camera_event:
                self._camera_event.cancel()
                self._camera_event = None
            if self._rppg_event:
                self._rppg_event.cancel()
                self._rppg_event = None

    """
    Signature Methods - Data Physiological Signal Emission

    These methods send physiological data to the corresponding widget displays.
    Widget definitions are in widgets/phys-box.
    """

    def send_data_log(self, dt):
        """Send a data point to the log widget with HR and HRV values."""
        if not self.camera_active or not self.face_detected:
            return None

        if not self.emitting_rppg_buffer or len(self.emitting_rppg_buffer) < 60:
            return None

        app = App.get_running_app()
        log_widget = self._get_log_widget(app)
        if not log_widget:
            return None

        try:
            heart_rate = self.calculate_current_hr()
            rmssd, sdnn = self.calculate_current_hrv()

            if heart_rate is not None or rmssd is not None:
                return log_widget.add_data_point_to_log_with_data(heart_rate, rmssd, sdnn)
        except Exception as e:
            print(f"Error sending data to log: {e}")

        return None

    def _get_log_widget(self, app):
        """Helper to get the log widget from screen manager."""
        if not app or not hasattr(app, 'root') or not app.root:
            return None

        scrn_manager = app.root.ids.get('scrn_manager')
        if not scrn_manager:
            return None

        try:
            log_screen = scrn_manager.get_screen('scrn_log')
            for child in log_screen.children:
                if hasattr(child, 'add_data_point_to_log_with_data'):
                    return child
        except Exception as e:
            print(f"Error accessing log screen: {e}")

        return None

    def calculate_current_hr(self):
        """Calculate current heart rate from the rPPG buffer."""
        if not self.emitting_rppg_buffer or len(self.emitting_rppg_buffer) < 30:
            return None

        try:
            signal_array = np.array(self.emitting_rppg_buffer)
            peaks, _ = scipy_signal.find_peaks(signal_array, prominence=0.5)

            if len(peaks) <= 1:
                return None

            rr = np.diff(peaks) / self.fps
            rr_intervals = rr[(rr >= 0.3) & (rr <= 2.0)]

            if len(rr_intervals) > 0:
                heart_rate = int(60.0 / np.mean(rr_intervals))
                return heart_rate if 40 <= heart_rate <= 200 else None
        except Exception as e:
            print(f"Error calculating HR: {e}")

        return None

    def calculate_current_hrv(self):
        """Calculate current HRV (RMSSD) from the rPPG buffer."""
        if not self.emitting_rppg_buffer or len(self.emitting_rppg_buffer) < 100:
            return None, None

        try:
            signal_array = np.array(self.emitting_rppg_buffer)
            prominence = np.std(signal_array) * 0.3
            peaks, _ = scipy_signal.find_peaks(signal_array, prominence=prominence)

            if len(peaks) <= 3:
                return None, None

            rr = np.diff(peaks) / self.fps
            rr = np.asarray(rr, dtype=float)
            rr_intervals = rr[(rr >= 0.4) & (rr <= 1.8)]

            if len(rr_intervals) <= 2:
                return None, None

            rr_intervals = rr_intervals * 1000
            sdnn = np.std(rr_intervals)
            successive_diffs = np.diff(rr_intervals)
            rmssd = np.sqrt(np.mean(successive_diffs**2))

            if 5 <= rmssd <= 300:
                return rmssd, sdnn
        except Exception as e:
            print(f"Error calculating HRV: {e}")

        return None, None
    
    def _update_phys_box(self, box_id, value):
        """Update physiological box with calculated value."""
        home = self.get_home_widget()
        if home and hasattr(home, 'ids') and hasattr(home.ids, box_id):
            home.ids[box_id].update_value(value)

    def update_heart_rate(self, dt):
        """Update heart rate box with calculated HR value."""
        if self.face_detected and self.emitting_rppg_buffer:
            hr_value = self.calculate_current_hr()
            self._update_phys_box('hr_box', hr_value)

    def update_hrv(self, dt):
        """Update HRV box with calculated HRV value."""
        if self.face_detected and self.emitting_rppg_buffer:
            rmssd, sdnn = self.calculate_current_hrv()
            if rmssd is not None:
                self._update_phys_box('sdnn_box', sdnn)
                self._update_phys_box('rmssd_box', rmssd)
            else:
                self._update_phys_box('rmssd_box', None)
                self._update_phys_box('sdnn_box', None)

    def emit_rppg_signal(self, dt):
        """Emit one rPPG value for real-time preview to the home screen."""
        if not self.camera_active or not self.emitting_rppg_buffer or not self.face_detected:
            # Optionally, update UI to show "No Signal"
            home = self.get_home_widget()
            if home and hasattr(home, 'update_rppg_signal'):
                home.update_rppg_signal(None)  # Or a custom "no signal" value
            return
        value = self.emitting_rppg_buffer.pop(0)
        home = self.get_home_widget()
        if home and hasattr(home, 'update_rppg_signal'):
            self.signal_value = value
            home.update_rppg_signal(value)

    def update(self, dt):
        if not self.camera_active:
            return

        ret, frame = self.capture.read()
        if not ret:
            return

        self.detect_face(frame)

        if len(self.combined_r_signal) >= 10 * self.fps:
            temp_r = np.array(self.combined_r_signal)
            temp_g = np.array(self.combined_g_signal)
            temp_b = np.array(self.combined_b_signal)
            self.combined_r_signal.clear()
            self.combined_g_signal.clear()
            self.combined_b_signal.clear()
            self.process_rppg_signal(temp_r, temp_g, temp_b)

        frame = cv2.flip(frame, 0)
        buffer = frame.tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt="bgr")
        texture.blit_buffer(buffer, colorfmt="bgr", bufferfmt="ubyte")
        self.texture = texture

    def detect_face(self, frame):
        """Detect face in the frame."""
        margin_x = 10
        scaling_factor = 0.8
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        result = self.face_detector.detect(mp_image)

        if not result.detections:
            self.face_detected = False
            return None

        self.face_detected = True

        for detection in result.detections:
            bboxC = detection.bounding_box
            x, y, w, h = bboxC.origin_x, bboxC.origin_y, bboxC.width, bboxC.height
            new_x = int(x + margin_x)
            new_w = int(w * scaling_factor)
            new_h = int(h * scaling_factor)

            face_roi = image_rgb[y:y+new_h, new_x:new_x+new_w]
            if face_roi.size == 0:
                return None

            cv2.rectangle(frame, (int(x), int(y)), (int(x + new_w), int(y + new_h)), (0, 255, 0), 2)
            mean_rgb = cv2.mean(face_roi)[:3]

            self.combined_r_signal.append(mean_rgb[0])
            self.combined_g_signal.append(mean_rgb[1])
            self.combined_b_signal.append(mean_rgb[2])

    def process_rppg_signal(self, r, g, b):
        # Convert the RGB signals to numpy arrays
        rgb_signal = np.array([r, g, b])
        rgb_signal = rgb_signal.reshape(1, 3, -1)
        rppg_signal = POS(rgb_signal, fps=self.fps)
        rppg_signal = rppg_signal.reshape(-1)
        rppg_signal = preprocess_ppg(rppg_signal, fs=self.fps)
        self.emitting_rppg_buffer.extend(rppg_signal)

    def setup_face_detector(self):
        """Setup MediaPipe face detector."""
        base_model = resource_path("models/blaze_face_short_range.tflite")
        base_options = python.BaseOptions(model_asset_path=base_model)
        options = vision.FaceDetectorOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
        )
        return vision.FaceDetector.create_from_options(options)
    
    def get_home_widget(self):
        """Get the Home widget from the app's screen manager."""
        app = App.get_running_app()
        if not app or not hasattr(app, 'root') or not app.root:
            return None

        scrn_manager = app.root.ids.get('scrn_manager')
        if not scrn_manager:
            return None

        try:
            home_screen = scrn_manager.get_screen('scrn_home')
            if hasattr(home_screen, 'ids') and 'home' in home_screen.ids:
                return home_screen.ids['home']
            if hasattr(home_screen, 'children') and home_screen.children:
                return home_screen.children[0]
        except Exception as e:
            print(f"Error accessing home screen: {e}")

        return None


def resource_path(relative_path):
    """Get absolute path to resource for PyInstaller."""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)
