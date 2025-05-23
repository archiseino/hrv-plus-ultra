from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.widget import Widget
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from kivy.graphics.texture import Texture
import kivy.properties as props
from scipy.signal import find_peaks
import numpy as np


Builder.load_string("""
<StatusIndicator>:
    size_hint: None, None
    size: 150, 50
    Label:
        id: status_label
        text: "Status: Normal"
        color: 0, 1, 0, 1

<ProgressBarWidget>:
    orientation: 'vertical'
    BoxLayout:
        Text:
            text:"Stress Indicator"
            halign: "left"
        
        Text:
            id: stress_label
            text: f"Sress level: {root.value} {root.unit}"
            font_name: app.fonts.body
            halign: "right"
            color: app.colors.success
            
    ProgressBar:
        id: progress_bar
        max: 100
        value: root.bar_value

""")

class StatusIndicator(BoxLayout):
    def update_status(self, status):
        color_map = {
            'Normal': (0, 1, 0, 1),
            'Alert': (1, 0.5, 0, 1),
            'Critical': (1, 0, 0, 1)
        }
        self.ids.status_label.text = f"Status: {status}"
        self.ids.status_label.color = color_map.get(status, (1, 1, 1, 1))

class ProgressBarWidget(BoxLayout):
    bar_value = props.NumericProperty(float(20.00))
    value = props.StringProperty("50")
    unit = props.StringProperty("%")
    def set_level(self, stress_level):
        print(f"Setting stress level to: {stress_level}")  # Debugging
        self.bar_value = max(0, min(stress_level, 100))
        self.value = str(self.bar_value)
        # if stress_level < 34:
        #     self.bar_color = [0, 1, 0, 1]  # Green
        #     self.ids.status_label.text = "Stress Level: Low"
        # elif stress_level < 67:
        #     self.bar_color = [1, 1, 0, 1]  # Yellow
        #     self.ids.status_label.text = "Stress Level: Medium"
        # else:
        #     self.bar_color = [1, 0, 0, 1]  # Red
        #     self.ids.status_label.text = "Stress Level: High"

    def update_value(self, rppg_value):
        # 1. Find peaks (assume peaks = heart beats)
        rppg_signals = np.asarray(rppg_value).flatten()
        peaks, _ = find_peaks(rppg_signals)  # ~60 BPM
        if len(peaks) < 2:
            return 0

        # 2. RR intervals (in seconds)
        rr_intervals = np.diff(peaks) / 30

        # 3. Compute HRV - RMSSD (Root Mean Square of Successive Differences)
        diff_rr = np.diff(rr_intervals)
        hrv_value = np.sqrt(np.mean(diff_rr**2)) if len(diff_rr) > 0 else 0

        if hrv_value > 0.2:
            hrv_value = 0.2  # Clamp

        stress_level = (1 - (hrv_value / 0.2)) * 100
        self.set_level(int(np.clip(stress_level, 0, 100)))
