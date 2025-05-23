from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
import kivy.properties as props
from scipy.signal import find_peaks
from scipy.signal import butter, filtfilt

import numpy as np

kv = """
<RespBox>:
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
                source: app.resource_path('assets/icons/lungs-solid.png')
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


class RespBox(ButtonBehavior, BoxLayout):
    label = props.StringProperty("Resp")
    value = props.StringProperty("0")
    unit = props.StringProperty("BPM")
    status = props.StringProperty("Normal")
    bcolor = props.ColorProperty("#f5f5f5")
    radius = props.ListProperty([16])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def update_value(self, resp_signal, fps=30):
        """ Metode implementasi """
        resp_signal = np.asarray(resp_signal).flatten()

        resp_peaks, _ = find_peaks(resp_signal, distance=fps)
        resp_intervals = np.diff(resp_peaks) / fps
        respiration_rate = 60.0 / np.mean(resp_intervals) if len(resp_intervals) > 0 else 0
        self.value = f"{int(respiration_rate)}"
