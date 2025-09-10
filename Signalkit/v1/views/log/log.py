from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from datetime import datetime
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder

import random

# Import button classes from the widgets.buttons module
from widgets.buttons import FlatButton, IconButton

# Load KV file with correct path and case
Builder.load_file("views/log/log.kv")

class DataRow(RecycleDataViewBehavior, BoxLayout):
    datetime = StringProperty("")
    heart_rate = StringProperty("")
    hrv = StringProperty("")
    index = NumericProperty(0)
    is_even = BooleanProperty(False)
    
    def refresh_view_attrs(self, rv, index, data):
        """Called when view is created or when data changes"""
        # Set all properties from the data dictionary
        self.index = index
        self.is_even = index % 2 == 0
        
        # Explicitly set properties from data dictionary
        self.datetime = data.get('datetime', '')
        self.heart_rate = data.get('heart_rate', '')
        self.hrv = data.get('hrv', '')
        
        return super(DataRow, self).refresh_view_attrs(rv, index, data)
    
class DataView(RecycleView):
    data = ListProperty([])  # This now properly triggers updates
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.add_initial_data()
    
    def add_initial_data(self):
        """Add 3 initial sample rows"""
        for i in range(3):
            self.add_data_point()
    
    def add_data_point(self):
        """Add a single data point with current timestamp"""
        new_data = {
            'datetime': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'heart_rate': f"{random.randint(60, 100)} BPM",
            'hrv': f"{random.uniform(20.0, 80.0):.1f} ms",
            'index': len(self.data)
        }
        
        # Create new list to trigger property change
        self.data = self.data + [new_data]
        self.refresh_from_data()

class Log(Screen):
    def __init__(self, **kwargs):
        super(Log, self).__init__(**kwargs)
        self.total_entries = 150  # Simulate having 150 total entries
        print("Log screen initialized")
    
    def on_enter(self):
        """Called when the screen is displayed"""
        print("Log screen entered")
        print(f"Available IDs in Log screen: {list(self.ids.keys())}")
        
        # Try to access data_view directly
        if 'data_view' in self.ids:
            print(f"data_view found: {self.ids.data_view}, type: {type(self.ids.data_view).__name__}")
            print(f"Current data items: {len(self.ids.data_view.data)}")
        else:
            print("data_view not found in self.ids")
    
    def get_log_widget(self):
        """Get the data_view widget directly from the current screen"""
        if 'data_view' not in self.ids:
            print("Error: data_view ID not found in Log screen")
            print(f"Available IDs: {list(self.ids.keys())}")
            return None
        return self.ids.data_view
    
            
    def add_data_point_to_log_with_data(self, heart_rate, hrv=None):
        """Add a data point with specific physiological values from the camera feed"""
        print("add_data_point_to_log_with_data called")
        data_view = self.get_log_widget()
        if data_view:
            new_data = {
                'datetime': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'heart_rate': f"{heart_rate} BPM" if heart_rate else "No Signal",
                'hrv': f"{hrv:.1f} ms" if hrv else "No Data",
                'index': len(data_view.data)
            }
            
            # Add to data_view and trigger update
            data_view.data = data_view.data + [new_data]
            data_view.refresh_from_data()
            print(f"Added custom data point. Total entries: {len(data_view.data)}")
            
            # Update counter label if it exists
            if 'counter_label' in self.ids:
                self.ids.counter_label.text = f"Showing {len(data_view.data)} of {self.total_entries} entries"
            
            return True
        print("Could not get data_view widget")
        return False