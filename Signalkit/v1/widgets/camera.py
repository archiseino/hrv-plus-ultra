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

        ## OpenCv Props
        self.signal_value = 0
        self.fps = 30
        self.face_detector = self.setup_face_detector()
        self.capture = cv2.VideoCapture(0)
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
        Send a data point to the log widget with actual HR and HRV values.
        Only sends data when camera is active and face is detected.
        Returns True if successful, None otherwise.
        """
        # Don't send data if camera is paused or no face detected
        if not self.camera_active:
            print("Camera is paused - not sending data to log")
            return None
            
        if not self.face_detected:
            print("No face detected - not sending data to log")
            return None
            
        # Don't send data if there's insufficient rPPG buffer
        if not self.emitting_rppg_buffer or len(self.emitting_rppg_buffer) < 60:
            print("Insufficient rPPG data - not sending to log")
            return None
        
        app = App.get_running_app()
        if not app or not hasattr(app, 'root') or not app.root:
            print("No running app or root widget found")
            return None

        # Access screen manager from root
        scrn_manager = app.root.ids.get('scrn_manager', None)
        if not scrn_manager:
            print("Screen manager not found in root.ids")
            print(f"Available root ids: {list(app.root.ids.keys())}")
            return None

        try:
            # Get the log screen
            log_screen = scrn_manager.get_screen('scrn_log')
            
            # The Log widget is a direct child of the Screen, not in screen.ids
            # Look for the Log widget in screen's children
            log_widget = None
            if hasattr(log_screen, 'children') and log_screen.children:
                # Screen children are in reverse order, so the first child is the Log widget
                for child in log_screen.children:
                    if hasattr(child, 'add_data_point_to_log_with_data'):
                        log_widget = child
                        break
            
            if log_widget:
                # Calculate current HR and HRV from the buffer
                heart_rate = self.calculate_current_hr()
                hrv_value = self.calculate_current_hrv()
                
                # Only send if we have valid physiological data
                if heart_rate is not None or hrv_value is not None:
                    success = log_widget.add_data_point_to_log_with_data(heart_rate, hrv_value)
                    if success:
                        print(f"Data point added successfully - HR: {heart_rate}, HRV: {hrv_value}")
                        return True
                    else:
                        print("Failed to add data point to log")
                else:
                    print("No valid HR/HRV data calculated - not sending to log")
            else:
                print("Log widget not found in screen children")
                print(f"Available children: {[type(child).__name__ for child in log_screen.children]}")
                    
        except Exception as e:
            print(f"Error accessing log screen: {e}")
            
        return None

    def calculate_current_hr(self):
        """Calculate current heart rate from the rPPG buffer"""
        if not self.emitting_rppg_buffer:
            print("HR: No rPPG buffer")
            return None
            
        if len(self.emitting_rppg_buffer) < 30:
            print(f"HR: Insufficient data - buffer length: {len(self.emitting_rppg_buffer)}")
            return None
            
        # Simple peak detection for HR calculation
        try:
            signal_array = np.array(self.emitting_rppg_buffer)
            print(f"HR: Processing signal array of length {len(signal_array)}")
            
            # Find peaks with fixed prominence
            peaks, _ = scipy_signal.find_peaks(signal_array, prominence=0.5)
            print(f"HR: Found {len(peaks)} peaks")
            
            if len(peaks) > 1:
                # Calculate RR intervals and heart rate (same logic as hr.py)
                rr = np.diff(peaks) / self.fps  # Convert to seconds
                rr = np.asarray(rr, dtype=float)
                rr_intervals = rr[(rr >= 0.3) & (rr <= 2.0)]  # Clean RR interval outside 0.3 - 2.0 seconds
                print(f"HR: Valid RR intervals: {len(rr_intervals)} out of {len(rr)}")
                
                if len(rr_intervals) > 0:
                    heart_rate = int(60.0 / np.mean(rr_intervals))
                    print(f"HR: Calculated heart rate: {heart_rate} BPM")
                    return heart_rate if 40 <= heart_rate <= 200 else None
            else:
                print("HR: Not enough peaks found")
        except Exception as e:
            print(f"Error calculating HR: {e}")
            
        return None

    def calculate_current_hrv(self):
        """Calculate current HRV (RMSSD) from the rPPG buffer"""
        if not self.emitting_rppg_buffer:
            print("HRV: No rPPG buffer")
            return None
            
        if len(self.emitting_rppg_buffer) < 100:  # Need more data for HRV
            print(f"HRV: Insufficient data - buffer length: {len(self.emitting_rppg_buffer)}")
            return None
            
        try:
            signal_array = np.array(self.emitting_rppg_buffer)
            print(f"HRV: Processing signal array of length {len(signal_array)}")
            
            # Find peaks with adaptive prominence
            prominence = np.std(signal_array) * 0.3
            peaks, _ = scipy_signal.find_peaks(signal_array, prominence=prominence)
            print(f"HRV: Found {len(peaks)} peaks with prominence {prominence:.3f}")

            if len(peaks) > 3:  # Need at least 4 peaks for 3+ RR intervals
                # Calculate RR intervals
                rr = np.diff(peaks) / self.fps  # Convert to seconds
                rr = np.asarray(rr, dtype=float)
                print(f"HRV: Raw RR intervals range: {np.min(rr):.3f} - {np.max(rr):.3f} seconds")
                
                # Clean RR intervals (more lenient for HRV)
                rr_intervals = rr[(rr >= 0.4) & (rr <= 1.8)]  # 33-150 BPM range
                print(f"HRV: Cleaned RR intervals: {len(rr_intervals)} valid out of {len(rr)}")
                
                if len(rr_intervals) > 2:  # Need at least 3 RR intervals for RMSSD
                    rr_intervals = rr_intervals * 1000  # Convert to milliseconds
                    print(f"HRV: RR intervals (ms): {rr_intervals[:5]}...")  # Show first 5
                    
                    # Calculate RMSSD (Root Mean Square of Successive Differences)
                    successive_diffs = np.diff(rr_intervals)
                    rmssd = np.sqrt(np.mean(successive_diffs**2))
                    print(f"HRV: Calculated RMSSD: {rmssd:.2f} ms")
                    
                    # Validate RMSSD range
                    if 5 <= rmssd <= 300:  # More realistic range for RMSSD
                        return rmssd
                    else:
                        print(f"HRV: RMSSD {rmssd:.2f} ms out of valid range (5-300 ms)")
                else:
                    print(f"HRV: Not enough valid RR intervals: {len(rr_intervals)}")
            else:
                print(f"HRV: Not enough peaks detected: {len(peaks)}")
                
        except Exception as e:
            print(f"Error calculating HRV: {e}")
            import traceback
            traceback.print_exc()
            
        return None
    
    def _update_phys_box(self, box_id, value):
        """Update physiological box with calculated value"""
        home = self.get_home_widget()
        if home and hasattr(home, 'ids') and hasattr(home.ids, box_id):
            # Call update_value with just the calculated value
            home.ids[box_id].update_value(value)
        else:
            print(f"Cannot update {box_id}: home widget or box not found")

    def update_heart_rate(self, dt):
        """Update heart rate box with calculated HR value."""
        if self.face_detected and self.emitting_rppg_buffer:
            hr_value = self.calculate_current_hr()
            if hr_value is not None:
                self._update_phys_box('hr_box', hr_value)
            else:
                # Send None to indicate no valid data
                self._update_phys_box('hr_box', None)

    def update_hrv(self, dt):
        """Update HRV box with calculated HRV value."""
        if self.face_detected and self.emitting_rppg_buffer:
            hrv_value = self.calculate_current_hrv()
            if hrv_value is not None:
                self._update_phys_box('hrv_box', hrv_value)
            else:
                # Send None to indicate no valid data
                self._update_phys_box('hrv_box', None)

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
