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
    camera_active = BooleanProperty(True)  # Track camera state

    def __init__(self, **keyargs):
        super().__init__(**keyargs)

        ## OpenCv Props
        self.signal_value = 0
        self.fps = 30
        self.face_detector = self.setup_face_detector()
        self.capture = cv2.VideoCapture(1)
        self._camera_event = Clock.schedule_interval(self.update, 1.0 / 30) # Update the Camera feed at 30 FPS
        self._rppg_event = Clock.schedule_interval(self.emit_rppg_signal, 1.0 / 10) # Emit the signal at 10 Hz
        Clock.schedule_interval(self.send_data_log, 20) # Update the Log every 1 minute

        ## Set schedule for Phys signal
        Clock.schedule_interval(self.update_heart_rate, 10)      # every 10s
        Clock.schedule_interval(self.update_hrv, 15)            # every 15s

        ## Phys signal buffer
        # Buffers for raw RGB signals (per frame)
        self.combined_r_signal = []
        self.combined_g_signal = []
        self.combined_b_signal = []

        # Buffer for emitting rPPG values to UI (real-time preview)
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
      ⭐ Signature Methods

      Metode ini merupakan metode untuk mengirimkan data phyisologi ke widget masing masing untuk ditampilkan.

      Widget sendiri terdapat pada file widgets/phys-box.

    """ 
    def send_data_log(self, dt):
        """
        Attempts to send a data point to the log widget.
        Tries to access the log widget from root.ids, then update its data_view or call its method.
        Returns True if successful, None otherwise.
        """
        app = App.get_running_app()
        if not app or not hasattr(app, 'root') or not app.root:
            print("No running app or root widget found")
            return None

        root_ids = getattr(app.root, 'ids', {})
        log_widget = root_ids.get('log', None)
        if not log_widget:
            print("Log widget not found in root.ids")
            print(f"Available root ids: {list(root_ids.keys())}")
            return None

        # Try to update data_view if present
        if hasattr(log_widget, 'ids') and 'data_view' in log_widget.ids:
            data_view = log_widget.ids.data_view
            data_view.add_data_point()
            print("Data point added successfully to log via direct access")
            return True

        # Try to call add_data_point_to_log if present
        if hasattr(log_widget, 'add_data_point_to_log'):
            log_widget.add_data_point_to_log()
            print("Data point added successfully to log via method")
            return True

        print("Log widget found but missing required attributes")
        if hasattr(log_widget, 'ids'):
            print(f"Available ids in log widget: {list(log_widget.ids.keys())}")
        return None
    
    def _update_phys_box(self, box_id, value):
        home = self.get_home_widget()
        if home and hasattr(home, 'ids') and hasattr(home.ids, box_id):
            home.ids[box_id].update_value(value)
        else:
            print(f"Cannot update {box_id}: home widget or box not found")

    def update_heart_rate(self, dt):
        """Update heart rate box with the latest rPPG values (real-time preview)."""
        if self.emitting_rppg_buffer:
            self._update_phys_box('hr_box', np.array(self.emitting_rppg_buffer))

    def update_hrv(self, dt):
        """Update HRV box with the full rPPG buffer (for batch HRV analysis)."""
        if self.emitting_rppg_buffer:
            self._update_phys_box('hrv_box', np.array(self.emitting_rppg_buffer))

    def emit_rppg_signal(self, dt):
        """Emit one rPPG value for real-time preview to the home screen."""
        if not self.camera_active or not self.emitting_rppg_buffer:
            return
        value = self.emitting_rppg_buffer.pop(0)
        home = self.get_home_widget()
        if home and hasattr(home, 'update_rppg_signal'):
            self.signal_value = value
            home.update_rppg_signal(value)

    def update(self, dt):
        if not self.camera_active:
            return
        
        # Acquire frame
        ret, frame = self.capture.read()
        if not ret:
            print("Camera frame not acquired")
            return
        
        self.detect_face(frame)

        ## If the duration sample 10 seconds long, calculate the rPPG signal
        if len(self.combined_r_signal) >= 10 * self.fps: # 10 seconds * 30 fps
            temp_r = np.array(self.combined_r_signal)
            temp_g = np.array(self.combined_g_signal)
            temp_b = np.array(self.combined_b_signal)
            self.combined_r_signal.clear()
            self.combined_g_signal.clear()
            self.combined_b_signal.clear()
            self.process_rppg_signal(temp_r, temp_g, temp_b)

        # Update Kivy texture
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
            print("No face detected")
            return None

        for detection in result.detections:
            bboxC = detection.bounding_box

            x, y, w, h = bboxC.origin_x, bboxC.origin_y, bboxC.width, bboxC.height
            new_x = int(x + margin_x)
            new_w = int(w * scaling_factor)
            new_h = int(h * scaling_factor)

            face_roi = image_rgb[y:y+new_h, new_x:new_x+new_w]
            if face_roi.size == 0:
                print("Invalid ROI")
                return None
            
            cv2.rectangle(frame, (int(x), int(y)), (int(x + new_w), int(y + new_h)), (0, 255, 0), 2)
            mean_rgb = cv2.mean(face_roi)[:3]

            ## Append mean RGB values to the buffer
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
    
    def get_home_widget(self):
        """
        Helper method to get the Home widget from the app's screen manager.
        Returns the home widget instance or None if not found.
        """
        app = App.get_running_app()
        if not app:
            print("No running app or root widget found")
            return None

        scrn_manager = app.root.ids.get('scrn_manager', None)
        if not scrn_manager:
            print("scrn_manager not found in root.ids")
            print(f"Available ids: {list(app.root.ids.keys())}")
            return None

        home_screen = scrn_manager.get_screen('scrn_home')
        # Get the home screen widget
        if hasattr(home_screen, 'ids') and 'home' in home_screen.ids:
            return home_screen.ids['home']
        
        # Fallback: return first child if available
        if hasattr(home_screen, 'children') and home_screen.children:
            return home_screen.children[0]
        
        print("Home widget not found in home screen")
        return None

""" For building reference path PyInstaller"""
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
