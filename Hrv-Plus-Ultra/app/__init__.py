from kivy.app import App
from kivy.utils import QueryDict, rgba
from kivy.metrics import dp
import os
import sys

from .view import StressMonitorLayout

class MainApp(App):
    colors = QueryDict()
    colors.primary = rgba("#2D9CDB")
    colors.secondary = rgba("#16213E")
    colors.success = rgba("#1FC98E")
    colors.warning = rgba("#F2C94C")
    colors.danger = rgba("#EB5757")
    colors.grey_dark = rgba("#c4c4c4")
    colors.grey_light = rgba("#f5f5f5")
    colors.black = rgba("#000000")
    colors.white = rgba("#ffffff")

    fonts = QueryDict()
    fonts.size = QueryDict()
    fonts.size.h1 = dp(24)
    fonts.size.h2 = dp(22)
    fonts.size.h3 = dp(18)
    fonts.size.h4 = dp(16)
    fonts.size.h5 = dp(14)
    fonts.size.h6 = dp(12)

    fonts.heading = 'assets/fonts/Roboto/Roboto-Bold.ttf'
    fonts.subheading = 'assets/fonts/Roboto/Roboto-Regular.ttf'
    fonts.body = 'assets/fonts/Roboto/Roboto-Light.ttf'

    def build(self):
        return StressMonitorLayout()
    
    @staticmethod
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)