from app import MainApp
import os
import sys
from kivy.resources import resource_add_path
import kivy_matplotlib_widget

if __name__ == "__main__":
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    MainApp().run()
