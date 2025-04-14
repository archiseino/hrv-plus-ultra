from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
import kivy.properties as props
from scipy.signal import find_peaks
import numpy as np

kv = """
<HrvBox>:
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
                source: app.resource_path('assets/icons/wave-square-solid.png')
            Text:
                text: root.label
                font_size: app.fonts.size.h4
                font_name: app.fonts.body
                valign: "bottom"
                halign: "left"


        BoxLayout:
            size_hint_y: 0.4
            Text:
                text: f"{root.value} {root.unit}"
                font_size: app.fonts.size.h3
                font_name: app.fonts.body
                valign: "bottom"
                halign: "left"


        BoxLayout:
            size_hint_y: 0.2
            Text:
                text: root.status
                font_size: app.fonts.size.h5
                font_name: app.fonts.body
                color: app.colors.success
                valign: "bottom"
                halign: "left"


"""

Builder.load_string(kv)

class HrvBox(ButtonBehavior, BoxLayout):
    label = props.StringProperty("HRV")
    value = props.StringProperty("0")
    unit = props.StringProperty("ms")
    status = props.StringProperty("Normal")
    bcolor = props.ColorProperty("#f5f5f5")
    radius = props.ListProperty([16])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def update_value(self, rppg_value, fps=30):
        rppg_signal = np.asarray(rppg_value).flatten()
        peaks, _ = find_peaks(rppg_signal, distance=fps/2)
        if len(peaks) > 2:
            intervals = np.diff(peaks) / fps
            hrv = np.std(intervals) * 1000  # in ms
        else:
            hrv = 0
        hrv_status = "Stable" if hrv > 30 else "Unstable"
        self.value = f"{hrv:.2f}"
        self.status = hrv_status
