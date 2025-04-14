from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.app import App
from kivy.graphics.texture import Texture

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

## Import Signal Processing
import matplotlib.pyplot as plt

"""
🚪 Root Container for Future build.

This is the main container for the App. 

Kivy can be scaled as Desktop app, so one potential update is making a Navigation for other feature. 
But I'll leave as a Trivia for you

"""
class StressMonitorLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)  

        """ Matplotlib graph maker. """
        self.lines = []
        self.signal_values = []  # Store rPPG values
        self.samples = []  # Time tracking
        self.time_index  = 0
        self.figure_wgt = self.ids.figure_hr
        self.fig, self.ax1 = plt.subplots(1, 1)
        self.fig.subplots_adjust(left=0.13, top=0.96, right=0.93, bottom=0.2)
        self.figure_wgt.figure = self.fig

        Clock.schedule_interval(self.update_graph, 1.0 / 0.5) ## 300 Frame in 30 Fps = 10 second
 
    def update_stress_signal(self, value):
        """ This method receives the rPPG signal and updates the graph """
        self.signal_values.append(value)
        self.samples.append(self.time_index)
        self.time_index += 1

        if len(self.signal_values) > 300:
            self.signal_values.pop(0)
            self.samples.pop(0)

    def update_graph(self, dt):
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