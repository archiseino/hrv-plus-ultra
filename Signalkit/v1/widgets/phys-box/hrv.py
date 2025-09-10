from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
import kivy.properties as props

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
    
    def update_value(self, hrv_value):
        """Update the HRV display with a calculated HRV value from camera"""
        if hrv_value is None:
            self.value = "No Signal"
            self.status = "No Data"
            return
            
        # hrv_value is already calculated in camera.py (RMSSD in ms)
        hrv = float(hrv_value)
        self.value = f"{hrv:.1f}"

        # Update status based on HRV ranges (RMSSD values)
        if hrv < 20:
            self.status = "Low Variability"
        elif hrv > 50:
            self.status = "High Variability"
        else:
            self.status = "Normal"
