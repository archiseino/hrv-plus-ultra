from app import MainApp
import kivy_matplotlib_widget #register all widgets to kivy register
import os, sys
from kivy.resources import resource_add_path

if __name__ == "__main__":
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    MainApp().run()
