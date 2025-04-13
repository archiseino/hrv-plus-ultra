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

<StatusBox>:
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

<HrBox>:
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: dp(100)
        padding: dp(8)
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
                font_size: app.fonts.size.h4
                font_name: app.fonts.body

        BoxLayout:
            size_hint_y: 0.4
            Text:
                text: f"{root.value} {root.unit}"
                font_size: app.fonts.size.h3
                font_name: app.fonts.body

        BoxLayout:
            size_hint_y: 0.2
            Text:
                text: root.status
                font_size: app.fonts.size.h5
                font_name: app.fonts.body
                color: app.colors.success

<SpO2Box>:
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: dp(100)
        padding: dp(8)
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
                source: app.resource_path('assets/icons/droplet-solid.png')
            Text:
                text: root.label
                font_size: app.fonts.size.h4
                font_name: app.fonts.body

        BoxLayout:
            size_hint_y: 0.4
            Text:
                text: f"{root.value} {root.unit}"
                font_size: app.fonts.size.h3
                font_name: app.fonts.body

        BoxLayout:
            size_hint_y: 0.2
            Text:
                text: root.status
                font_size: app.fonts.size.h5
                font_name: app.fonts.body
                color: app.colors.success
<HrvBox>:
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: dp(100)
        padding: dp(8)
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

        BoxLayout:
            size_hint_y: 0.4
            Text:
                text: f"{root.value} {root.unit}"
                font_size: app.fonts.size.h3
                font_name: app.fonts.body

        BoxLayout:
            size_hint_y: 0.2
            Text:
                text: root.status
                font_size: app.fonts.size.h5
                font_name: app.fonts.body
                color: app.colors.success

<RespBox>:
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: dp(100)
        padding: dp(8)
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

        BoxLayout:
            size_hint_y: 0.4
            Text:
                text: f"{root.value} {root.unit}"
                font_size: app.fonts.size.h3
                font_name: app.fonts.body

        BoxLayout:
            size_hint_y: 0.2
            Text:
                text: root.status
                font_size: app.fonts.size.h5
                font_name: app.fonts.body
                color: app.colors.success


<OverlayContainer>:
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: 0, 0, 0, 0.5
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: self.radius

<RoundedCard>:
    canvas.before:
        Color:
            rgba: 0, 0, 0, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [20,]

<GraphContainer>:
    Label:
        text: "Graph Placeholder"
"""

Builder.load_string(kv)

class RoundedCard(BoxLayout):
    pass

class HrBox(ButtonBehavior, BoxLayout):
    label = props.StringProperty("Heart Rate")
    value = props.StringProperty("")
    unit = props.StringProperty("BPM")
    status = props.StringProperty("Normal")
    bcolor = props.ColorProperty("#f5f5f5")
    radius = props.ListProperty([16])

    def __init__(self, **kwargs):
        super(HrBox, self).__init__(**kwargs)
    
    def update_value(self, rppg_value):
        peaks, _ = find_peaks(rppg_value, distance=30/2)
        peak_intervals = np.diff(peaks) / 30
        heart_rate = 60.0 / np.mean(peak_intervals) if len(peak_intervals) > 0 else 0

        self.value = f"{heart_rate:.2f}"

        if heart_rate < 60:
            self.status = "Low Heart Rate"
        elif heart_rate > 100:
            self.status = "High Heart Rate"

class SpO2Box(ButtonBehavior, BoxLayout):
    label = props.StringProperty("SpO2")
    value = props.StringProperty("")
    unit = props.StringProperty("BPM")
    status = props.StringProperty("Normal")
    bcolor = props.ColorProperty("#f5f5f5")
    radius = props.ListProperty([16])

    def __init__(self, **kwargs):
        super(SpO2Box, self).__init__(**kwargs)
    
    def update_value(self, rppg_value):
        spo2 = 95 + np.random.normal(0, 1)
        spo2_status = "OK" if spo2 >= 95 else "Low"
        self.value = f"{spo2:.2f}"  
        self.status = spo2_status


class HrvBox(ButtonBehavior, BoxLayout):
    label = props.StringProperty("HRV")
    value = props.StringProperty("")
    unit = props.StringProperty("ms")
    status = props.StringProperty("Normal")
    bcolor = props.ColorProperty("#f5f5f5")
    radius = props.ListProperty([16])

    def __init__(self, **kwargs):
        super(HrvBox, self).__init__(**kwargs)
    
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

class RespBox(ButtonBehavior, BoxLayout):
    label = props.StringProperty("Resp")
    value = props.StringProperty("")
    unit = props.StringProperty("BPM")
    status = props.StringProperty("Normal")
    bcolor = props.ColorProperty("#f5f5f5")
    radius = props.ListProperty([16])

    def __init__(self, **kwargs):
        super(RespBox, self).__init__(**kwargs)
    
    def update_value(self, rppg_value, fps=30):
        rppg_signal = np.asarray(rppg_value).flatten()
        peaks, _ = find_peaks(rppg_signal, distance=fps)
        if len(peaks) > 1:
            intervals = np.diff(peaks) / fps
            resp_rate = 60 / np.mean(intervals)
        else:
            resp_rate = 0
        self.value = f"{resp_rate:.2f}"
        self.status = "Normal" if resp_rate < 20 else "High Resp Rate"


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

class StatusBox(ButtonBehavior, BoxLayout):
    radius = props.ListProperty([1])
    bcolor = props.ColorProperty("#f5f5f5")

    def __init__(self, *args, **kwargs):
        super(StatusBox, self).__init__(*args, **kwargs)

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


class OverlayContainer(BoxLayout):
        radius = props.ListProperty([1])

class GraphContainer(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.counter = 0
        # Clock.schedule_interval(self.update_graph, 1)

    # def update_graph(self, dt):
    #     self.counter += 1
    #     self.ids.graph_placeholder.text = f"Graph updated: {self.counter}"
