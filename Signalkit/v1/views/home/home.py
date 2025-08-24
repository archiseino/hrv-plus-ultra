from kivy.lang import Builder
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.app import App

## Import Signal Processing
import matplotlib.pyplot as plt

Builder.load_file('views/home/home.kv')
class Home(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)  
        self.app = App.get_running_app()

        # Matplotlib graph properties
        self.signal_values = []  # y-axis data
        self.samples = []        # x-axis data
        self.time_index = 0      # x-axis counter
        self.figure_wgt = None   # Kivy widget for matplotlib
        self.fig = None          # matplotlib Figure
        self.ax1 = None         # matplotlib Axes
        self.line = None        # matplotlib Line2D
        
        # Defer initialization until after the widgets are created and added to the tree
        Clock.schedule_once(self._init_graph, 0)
        
    def _init_graph(self, dt):
        """Initialize the graph after the widget tree is built"""
        # Try to get the Widget MatplotFigure from the most direct path

        # if hasattr(self.ids, 'figure_rppg'):
        #     self.figure_wgt = self.ids.figure_rppg
        # elif self.app.root and hasattr(self.app.root.ids, 'figure_rppg'):
        #     self.figure_wgt = self.app.root.ids.figure_rppg
        # elif self.app.root and hasattr(self.app.root.ids, 'home') and hasattr(self.app.root.ids.home.ids, 'figure_rppg'):
        #     self.figure_wgt = self.app.root.ids.home.ids.figure_rppg
        # else:
        #     # Last resort - look for it in the current screen
        #     screen_mgr = self.app.root.ids.get('scrn_manager')
        #     if screen_mgr:
        #         home_screen = screen_mgr.get_screen('scrn_home')
        #         if home_screen and hasattr(home_screen.ids, 'figure_hr'):
        #             self.figure_wgt = home_screen.ids.figure_hr

        try:
            self.figure_wgt = self.app.root.ids.home.ids.figure_rppg       
            print("[Home] Tried self.app.root.ids.home.ids.figure_rppg")
        except Exception as e:
            print(f"[Home] Error accessing figure_rppg: {e}")
            self.figure_wgt = None

        if not self.figure_wgt:
            print("Warning: Could not find figure_rppg widget, graph will not be initialized")
            # Try again after a short delay
            Clock.schedule_once(self._init_graph, 0.5)
            return
        
        self.fig, self.ax1 = plt.subplots(1, 1)
        self.fig.subplots_adjust(left=0.13, top=0.96, right=0.93, bottom=0.2)
        self.figure_wgt.figure = self.fig
        Clock.schedule_interval(self.update_graph, 1.0 / 0.5)  # 300 Frame in 30 Fps = 10 second

    def update_graph(self, dt):
        # Using Matplotlb Aggregator Library from
        # https://mp-007.github.io/kivy_matplotlib_widget/
        if not self.fig or not self.ax1 or not self.figure_wgt:
            return
        
        # Receive data emitter from camera
        if len(self.signal_values) > 1:
            if not self.line:
                # Create the line if it doesn't exist
                self.line, = self.ax1.plot(self.samples, self.signal_values, color='b', label='rPPG Signal')
            else:
                # Update the existing line
                self.line.set_data(self.samples, self.signal_values)

            # Adjust the x and y axis scales
            self.ax1.relim()
            self.ax1.autoscale_view()

            # Refresh the figure
            self.figure_wgt.figure.canvas.draw_idle()


    # Consumer Emitter from Camera.py
    def update_rppg_signal(self, value):
        """ This method receives the rPPG signal and updates the graph """
        self.signal_values.append(value)
        self.samples.append(self.time_index)
        self.time_index += 1

        ## Cut the data to the last 300 samples
        if len(self.signal_values) > 300:
            self.signal_values.pop(0)
            self.samples.pop(0)

