from app import MainApp
import os, sys
from kivy.resources import resource_add_path

"""Instantiate kivy_matplotlib_widget to register all widgets to kivy register."""
import kivy_matplotlib_widget #register all widgets to kivy register

if __name__ == "__main__":
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    MainApp().run()
