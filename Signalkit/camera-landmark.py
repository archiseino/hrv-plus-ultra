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
    def __init__(self, **keyargs):
        super().__init__(**keyargs) 

        ## OpenCv Props
        self.signal_value = 0
        self.fps = 30
        self.face_landmarker = self.setup_face_landmarker()
        self.capture = cv2.VideoCapture(0)  
        Clock.schedule_interval(self.update, 1.0 / 30) # Update the Camera feed at 30 FPS
        Clock.schedule_interval(self.emit_rppg_signal, 1.0/ 10) # Emit the signal at 10 Hz
        Clock.schedule_interval(self.send_data_log, 20) # Update the Log every 1 minute

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
    def get_home_widget(self):
        """Helper method to get the Home widget"""
        app = App.get_running_app()
        if not app:
            print("No running app found")
            return None
            
        try:
            # Check if root exists
            if not hasattr(app, 'root') or not app.root:
                print("App root not found")
                return None
                
            # Check if scrn_manager exists in ids
            if not hasattr(app.root, 'ids'):
                print("Root has no ids attribute")
                return None
                
            if 'scrn_manager' not in app.root.ids:
                print("scrn_manager not found in root.ids")
                print(f"Available ids: {list(app.root.ids.keys())}")
                return None
                
            # Get the screen manager
            scrn_manager = app.root.ids.scrn_manager
            
            # Check if scrn_home exists
            if not scrn_manager.has_screen('scrn_home'):
                print("Screen 'scrn_home' not found")
                print(f"Available screens: {scrn_manager.screen_names}")
                return None
                
            # Get the home screen
            home_screen = scrn_manager.get_screen('scrn_home')
            
            # Check if home widget exists in the screen
            if not hasattr(home_screen, 'ids') or not home_screen.ids or 'home' not in home_screen.ids:
                # print("Home widget not found in home screen")
                # if hasattr(home_screen, 'ids'):
                    # print(f"Available ids in home screen: {list(home_screen.ids.keys())}")
                # Try to find the first child of the screen which might be the home widget
                if hasattr(home_screen, 'children') and home_screen.children:
                    # print("Returning first child of home screen as fallback")
                    return home_screen.children[0]
                return None
                
            return home_screen.ids.home
            
        except Exception as e:
            print(f"Error in get_home_widget: {e}")
            return None

    def send_data_log(self, dt):
        ## Getting the Log Widget
        app = App.get_running_app()
        if not app:
            print("No running app found")
            return None
        
        # Get the screen manager
        try:
            # Make sure we use the correct ID for the screen manager
            # screen_manager = app.root.ids.scrn_manager
            # Access the log widget directly from the root
            if 'log' in app.root.ids:
                log_widget = app.root.ids.log
                print(f"Found log widget directly in root.ids: {type(log_widget).__name__}")
                
                # If log widget has the data_view
                if hasattr(log_widget, 'ids') and 'data_view' in log_widget.ids:
                    data_view = log_widget.ids.data_view
                    data_view.add_data_point()
                    print("Data point added successfully to log via direct access")
                    return True
                
                # If log widget has the method we need
                elif hasattr(log_widget, 'add_data_point_to_log'):
                    log_widget.add_data_point_to_log()
                    print("Data point added successfully to log via method")
                    return True
                    
                else:
                    print(f"Log widget found but missing required attributes")
                    if hasattr(log_widget, 'ids'):
                        print(f"Available ids in log widget: {list(log_widget.ids.keys())}")
            else:
                print("Log widget not found in root.ids")
            
        except Exception as e:
            print(f"Error in send_data_log: {str(e)}")
            # Print more details to help debug
            if app and hasattr(app.root, 'ids'):
                print(f"Available root ids: {list(app.root.ids.keys())}")
            return None

    def update_heart_rate(self, dt):
        if len(self.rppg_buffer) > 0:
            home = self.get_home_widget()
            if home and hasattr(home, 'ids') and hasattr(home.ids, 'hr_box'):
                home.ids.hr_box.update_value(np.array(self.emitting_rppg_buffer))
            else:
                print("Cannot update heart rate: home widget or hr_box not found")

    def update_hrv(self, dt):
        if len(self.rppg_buffer) > 0:
            home = self.get_home_widget()
            if home and hasattr(home, 'ids') and hasattr(home.ids, 'hrv_box'):
                home.ids.hrv_box.update_value(np.array(self.rppg_buffer))
            else:
                print("Cannot update HRV: home widget or hrv_box not found")

    def update_resp(self, dt):
        if len(self.rppg_buffer) > 0:
            home = self.get_home_widget()
            if home and hasattr(home, 'ids') and hasattr(home.ids, 'resp_box'):
                home.ids.resp_box.update_value(np.array(self.resp_buffer))
            else:
                print("Cannot update respiration: home widget or resp_box not found")

    def update_spo2(self, dt):
        if len(self.rppg_buffer) > 0:
            home = self.get_home_widget()
            if home and hasattr(home, 'ids') and hasattr(home.ids, 'spo2_box'):
                home.ids.spo2_box.update_value(np.array(self.r_buffer), np.array(self.g_buffer), np.array(self.b_buffer))
            else:
                print("Cannot update SpO2: home widget or spo2_box not found")

    def update_bar(self, dt):
        if len(self.rppg_buffer) > 0:
            home = self.get_home_widget()
            if home and hasattr(home, 'ids') and hasattr(home.ids, 'stress_bar'):
                home.ids.stress_bar.update_value(np.array(self.rppg_buffer))
            else:
                print("Cannot update stress bar: home widget or stress_bar not found")

    def emit_rppg_signal(self, dt):
        """ Emitting the rPPG signal for Preview """
        if self.emitting_rppg_buffer:
            home = self.get_home_widget()
            if home and hasattr(home, 'update_stress_signal'):
                self.signal_value = self.emitting_rppg_buffer.pop(0) 
                home.update_stress_signal(self.signal_value)
            else:
                # Just pop the value to avoid buffer overflow even if we can't update the UI
                if self.emitting_rppg_buffer:
                    self.signal_value = self.emitting_rppg_buffer.pop(0)
                print("Cannot emit rPPG signal: home widget not found or missing update_stress_signal method")

    def update(self, dt):

        """ Update the camera feed """
        
        ret, frame = self.capture.read()
        if ret:

            # First detect the face (this modifies frame by drawing rectangles)
            self.detect_face(frame)

            frame = cv2.flip(frame, 0)            
            
            # Then create the buffer from the modified frame
            buffer = frame.tobytes()
            
            # Create texture from the buffer of the modified frame
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
        # Convert the frame to RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        left_r_signal, left_g_signal, left_b_signal = [], [], []
        right_r_signal, right_g_signal, right_b_signal = [], [], []

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=image_rgb
        )

        # Get the landkmarks
        result = self.face_landmarker.detect(mp_image)

        if not result.face_landmarks:
            print("No face landmarks detected")

        if result.face_landmarks:
            for face_landmark in result.face_landmarks:
                # Get cheek ROIs
                left_cheek_rect, right_cheek_rect = self.get_cheek_rois(face_landmark, frame.shape)

                # Draw both cheek ROIs with rectangles
                cv2.rectangle(frame, (left_cheek_rect[0], left_cheek_rect[1]), (left_cheek_rect[2], left_cheek_rect[3]), (0, 255, 0), 2)
                cv2.rectangle(frame, (right_cheek_rect[0], right_cheek_rect[1]), (right_cheek_rect[2], right_cheek_rect[3]), (0, 255, 0), 2)

                # Extract the left and right cheek ROIs
                left_cheek_roi = self.extract_rgb_from_rect(left_cheek_rect, frame)
                right_cheek_roi = self.extract_rgb_from_rect(right_cheek_rect, frame)

                # Calculate mean pixel values for the RGB channels
                left_cheek_rgb = cv2.mean(left_cheek_roi)[:3]
                right_cheek_rgb = cv2.mean(right_cheek_roi)[:3]

                # Append the RGB values to the respective lists
                left_r_signal.append(left_cheek_rgb[0])
                left_g_signal.append(left_cheek_rgb[1])
                left_b_signal.append(left_cheek_rgb[2])

                right_r_signal.append(right_cheek_rgb[0])
                right_g_signal.append(right_cheek_rgb[1])
                right_b_signal.append(right_cheek_rgb[2])

                # Combine and average the RGB values from both cheeks
                combined_r = (left_cheek_rgb[0] + right_cheek_rgb[0]) / 2
                combined_g = (left_cheek_rgb[1] + right_cheek_rgb[1]) / 2
                combined_b = (left_cheek_rgb[2] + right_cheek_rgb[2]) / 2

                # Append the combined RGB values to the respective lists
                self.combined_r_signal.append(combined_r)
                self.combined_g_signal.append(combined_g)
                self.combined_b_signal.append(combined_b)


    def process_rppg_signal(self, r, g, b):

        ## Convert the RGB signals to numpy arrays
        rgb_signal = np.array([r, g, b])
        rgb_signal = rgb_signal.reshape(1, 3, - 1) ## Flatten
        rppg_signal = POS(rgb_signal, fps=self.fps) ## Calculate the rPPG signal
        rppg_signal = rppg_signal.reshape(-1) ## Flatten

        rppg_signal = preprocess_ppg(rppg_signal, fs=self.fps) ## Preprocess the rPPG signal

        self.rppg_buffer.append(rppg_signal)  ## Store the rPPG signal

        self.emitting_rppg_buffer.extend(rppg_signal)  ## Emit the rPPG signal

    def setup_face_landmarker(self):
        ## Create Facelandmarker Object
        base_options = python.BaseOptions(model_asset_path="models/face_landmarker.task")
        VisionRunningMode = mp.tasks.vision.RunningMode
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            num_faces=1,
            running_mode = VisionRunningMode.IMAGE,
        )
        landmarker = vision.FaceLandmarker.create_from_options(options)   
        return landmarker
    
    def extract_rgb_from_rect(self, rect, image):
        x_min, y_min, x_max, y_max = rect
        roi = image[y_min:y_max, x_min:x_max]
        return roi

    def get_cheek_rois(self, landmarks, image_shape):
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

        
""" For building reference path PyInstaller"""
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
