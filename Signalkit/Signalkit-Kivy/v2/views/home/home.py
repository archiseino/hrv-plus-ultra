from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.app import App
from kivy.graphics.texture import Texture
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.app import App

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

## Import Signal Processing
import matplotlib.pyplot as plt

Builder.load_file('views/home/home.kv')
class Home(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)  
        self.app = App.get_running_app()

        """ Matplotlib graph maker. """
        self.lines = []
        self.signal_values = []  # Store rPPG values
        self.samples = []  # Time tracking
        self.time_index = 0
        self.figure_wgt = None  # Will be set in _init_graph
        self.fig = None
        self.ax1 = None
        
        # Defer initialization until after the widgets are created and added to the tree
        Clock.schedule_once(self._init_graph, 0)
        
    def _init_graph(self, dt):
        """Initialize the graph after the widget tree is built"""
        try:
            # Try to get the figure widget from various paths
            if hasattr(self.ids, 'figure_hr'):
                self.figure_wgt = self.ids.figure_hr
            elif self.app.root and hasattr(self.app.root.ids, 'figure_hr'):
                self.figure_wgt = self.app.root.ids.figure_hr
            elif self.app.root and hasattr(self.app.root.ids, 'home') and hasattr(self.app.root.ids.home.ids, 'figure_hr'):
                self.figure_wgt = self.app.root.ids.home.ids.figure_hr
            else:
                # Last resort - look for it in the current screen
                screen_mgr = self.app.root.ids.get('scrn_manager')
                if screen_mgr:
                    home_screen = screen_mgr.get_screen('scrn_home')
                    if home_screen and hasattr(home_screen.ids, 'figure_hr'):
                        self.figure_wgt = home_screen.ids.figure_hr
                    
            if self.figure_wgt:
                self.fig, self.ax1 = plt.subplots(1, 1)
                self.fig.subplots_adjust(left=0.13, top=0.96, right=0.93, bottom=0.2)
                self.figure_wgt.figure = self.fig
                
                # Start the graph update clock only if we successfully got the figure widget
                Clock.schedule_interval(self.update_graph, 1.0 / 0.5)  # 300 Frame in 30 Fps = 10 second
            else:
                print("Warning: Could not find figure_hr widget, graph will not be initialized")
                # Try again after a short delay
                Clock.schedule_once(self._init_graph, 0.5)
        except Exception as e:
            print(f"Error initializing graph: {e}")
            # Try again after a delay
            Clock.schedule_once(self._init_graph, 0.5)

    def update_stress_signal(self, value):
        """ This method receives the rPPG signal and updates the graph """
        self.signal_values.append(value)
        self.samples.append(self.time_index)
        self.time_index += 1

        if len(self.signal_values) > 300:
            self.signal_values.pop(0)
            self.samples.pop(0)

    def update_graph(self, dt):
        if not self.fig or not self.ax1 or not self.figure_wgt:
            return
            
        if len(self.signal_values) > 1:
            if not self.lines:
                # Create the line if it doesn't exist
                [line] = self.ax1.plot(self.samples, self.signal_values, color='b', label='rPPG Signal')
                self.lines.append(line)
            else:
                # Update the existing line
                self.lines[0].set_data(self.samples, self.signal_values)

            # Adjust the x and y limits to fit the new data
            self.ax1.relim()
            self.ax1.autoscale_view()

            # Refresh the figure
            self.figure_wgt.figure.canvas.draw_idle()

    # def on_leave(self):
    #     # Release the camera and unschedule the Clock event when leaving the screen
    #     if hasattr(self, 'capture') and self.capture:
    #         self.capture.release()
    #         self.capture = None
    #     Clock.unschedule(self.update_graph)  # Stop the update method from being called
