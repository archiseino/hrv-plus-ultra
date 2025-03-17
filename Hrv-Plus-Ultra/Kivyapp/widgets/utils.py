from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.widget import Widget
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from kivy.graphics.texture import Texture


Builder.load_string("""
<StatusIndicator>:
    size_hint: None, None
    size: 150, 50
    Label:
        id: status_label
        text: "Status: Normal"
        color: 0, 1, 0, 1

<ProgressBarWidget>:
    size_hint: None, None
    size: 200, 30

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

class ProgressBarWidget(ProgressBar):
    def update_progress(self, value):
        self.value = value
