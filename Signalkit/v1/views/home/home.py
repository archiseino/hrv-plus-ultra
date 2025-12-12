from kivy.lang import Builder
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.screenmanager import Screen
import matplotlib.pyplot as plt

Builder.load_file('views/home/home.kv')

class Home(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.signal_values = []
        self.samples = []
        self.time_index = 0
        self.figure_wgt = None
        self.fig = None
        self.ax1 = None
        self.line = None

        Clock.schedule_once(self._init_graph, 0)

    def _init_graph(self, dt):
        """Initialize the graph after the widget tree is built."""
        try:
            self.figure_wgt = self.app.root.ids.home.ids.figure_rppg
        except Exception as e:
            print(f"Error accessing figure_rppg: {e}")
            self.figure_wgt = None

        if not self.figure_wgt:
            Clock.schedule_once(self._init_graph, 0.5)
            return

        self.fig, self.ax1 = plt.subplots(1, 1)
        self.fig.subplots_adjust(left=0.13, top=0.96, right=0.93, bottom=0.2)
        self.figure_wgt.figure = self.fig
        Clock.schedule_interval(self.update_graph, 1.0 / 0.5)

    def update_graph(self, dt):
        """Update graph with latest rPPG signal data."""
        if not self.fig or not self.ax1 or not self.figure_wgt:
            return

        if len(self.signal_values) <= 1:
            return

        if not self.line:
            self.line, = self.ax1.plot(self.samples, self.signal_values, color='b', label='rPPG Signal')
        else:
            self.line.set_data(self.samples, self.signal_values)

        self.ax1.relim()
        self.ax1.autoscale_view()
        self.figure_wgt.figure.canvas.draw_idle()

    def update_rppg_signal(self, value):
        """Receive rPPG signal from camera and update graph."""
        self.signal_values.append(value)
        self.samples.append(self.time_index)
        self.time_index += 1

        if len(self.signal_values) > 300:
            self.signal_values.pop(0)
            self.samples.pop(0)

