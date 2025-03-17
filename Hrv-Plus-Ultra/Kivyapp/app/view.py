from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.image import Image
import cv2
from kivy.graphics.texture import Texture

## Import Signal Processing
import numpy as np
import matplotlib.pyplot as plt

class CameraLayout(Image):
    def __init__(self, **keyargs):
        super().__init__(**keyargs) ## KV Files config
        self.capture = cv2.VideoCapture(0)  ## Start the Camera
        Clock.schedule_interval(self.update, 1.0 / 30) ## Update the Camera feed at 30 FPS

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.flip(frame, 0)
            ## Store the buffer before displaying into the Kivy
            buffer = frame.tobytes()

            ## Texture.create config:
            ## size: The size of the texture in pixels (width, height)
            ## colorfmt: The color format of the texture (one of rgba, rgb, or bgr)
            ## bufferfmt: The buffer format of the texture (one of ‘ubyte’, ‘ushort’, ‘float’)
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt="bgr")
            texture.blit_buffer(buffer, colorfmt="bgr", bufferfmt="ubyte")
            self.texture = texture

class StressMonitorLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)  

        self.lines = []
        self.line_index = 0

        ## Getting the ID
        self.figure_wgt = self.ids.figure_hr

        ## Generate figure
        self.fig, self.ax1 = plt.subplots(1, 1)
        self.fig.subplots_adjust(left=0.13, top=0.96, right=0.93, bottom=0.2)
        self.figure_wgt.figure = self.fig
        
        Clock.schedule_interval(self.update_graph, 1)

    def update_graph(self, dt):
        if self.line_index < 5:
            x = [j for j in range(5)]
            y = [j * (self.line_index + 1) for j in range(5)]
            line, = self.ax1.plot(x, y, label=f'line{self.line_index + 1}')
            self.lines.append(line)
            self.figure_wgt.register_lines(self.lines)
            self.line_index += 1
            self.figure_wgt.figure.canvas.draw_idle()  # Refresh the figure 