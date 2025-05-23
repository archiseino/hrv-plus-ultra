from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
import kivy.properties as props
from scipy.signal import find_peaks
import numpy as np

kv = """
<HrBox>:
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: dp(100)
        padding: [dp(10), dp(8)]
        spacing: dp(4)

        canvas.before:
            Color:
                rgba: root.bcolor
            RoundedRectangle:
                size: self.size
                pos: self.pos
                radius: root.radius


        BoxLayout:
            size_hint_y: 0.4
            spacing: dp(4)
            IconButton:
                size_hint: None, None
                size: dp(20), dp(20)
                source: app.resource_path('assets/icons/heart-pulse-solid.png')
            Text:
                text: root.label
                valign: "bottom"
                halign: "left"
                font_size: app.fonts.size.h4
                font_name: app.fonts.body

        BoxLayout:
            size_hint_y: 0.4
            Text:
                text: f"{root.value} {root.unit}"
                font_size: app.fonts.size.h3
                valign: "bottom"
                halign: "left"
                font_name: app.fonts.body

        BoxLayout:
            size_hint_y: 0.2
            Text:
                text: root.status
                font_size: app.fonts.size.h5
                font_name: app.fonts.body
                valign: "bottom"
                halign: "left"
                color: app.colors.success


"""

Builder.load_string(kv)


class HrBox(ButtonBehavior, BoxLayout):
    label = props.StringProperty("Heart Rate")
    value = props.StringProperty("0")
    unit = props.StringProperty("BPM")
    status = props.StringProperty("Normal")
    bcolor = props.ColorProperty("#f5f5f5")
    radius = props.ListProperty([16])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def update_value(self, rppg_value):
        peaks, _ = find_peaks(rppg_value, distance=30/2)
        peak_intervals = np.diff(peaks) / 30
        heart_rate = 60.0 / np.mean(peak_intervals) if len(peak_intervals) > 0 else 0

        self.value = f"{heart_rate:.2f}"

        if heart_rate < 60:
            self.status = "Low Heart Rate"
        elif heart_rate > 100:
            self.status = "High Heart Rate"

