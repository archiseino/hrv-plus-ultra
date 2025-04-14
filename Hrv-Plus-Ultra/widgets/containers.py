from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
import kivy.properties as props
from scipy.signal import find_peaks
import numpy as np

kv = """
<ShadowBox>:
    BoxLayout:
        id: main
        orientation: root.orientation
        size_hint: root.size_hint
        canvas.before:
            Color:
                rgba: root.bcolor
            RoundedRectangle:
                size: self.size
                pos: self.pos
                radius: root.radius

"""

Builder.load_string(kv)


class ShadowBox(ButtonBehavior, BoxLayout):
    radius = props.ListProperty([1])
    bcolor = props.ColorProperty([1,1,1,1])

    def __init__(self, *args, **kwargs):
        super(ShadowBox, self).__init__(*args, **kwargs)

    def on_padding(self, inst, value):
        self.padding = 0
        self.ids.main.padding = value

    def on_spacing(self, inst, value):
        self.spacing = 0
        self.ids.main.spacing = value

    def add_widget(self, widget, index=0):
        if len(self.children) == 0:
            super().add_widget(widget, index=index)
        else:
            self.ids.main.add_widget(widget, index=index)

    def remove_widget(self, widget):
        self.ids.main.remove_widget(widget)

    def clear_widgets(self):
        self.ids.main.clear_widgets()
