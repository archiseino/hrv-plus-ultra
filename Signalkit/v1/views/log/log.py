from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from datetime import datetime
from widgets.buttons import FlatButton, IconButton

Builder.load_file("views/log/log.kv")

class DataRow(RecycleDataViewBehavior, BoxLayout):
    datetime = StringProperty("")
    heart_rate = StringProperty("")
    rmssd = StringProperty("")
    sdnn = StringProperty("")
    index = NumericProperty(0)
    is_even = BooleanProperty(False)

    def refresh_view_attrs(self, rv, index, data):
        """Called when view is created or when data changes."""
        self.index = index
        self.is_even = index % 2 == 0
        self.datetime = data.get('datetime', '')
        self.heart_rate = data.get('heart_rate', '')
        self.rmssd = data.get('rmssd', '')
        self.sdnn = data.get('sdnn', '')
        return super(DataRow, self).refresh_view_attrs(rv, index, data)


class DataView(RecycleView):
    data = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Log(Screen):
    def __init__(self, **kwargs):
        super(Log, self).__init__(**kwargs)
        self.total_entries = 150

    def on_enter(self):
        """Called when the screen is displayed."""
        print("Log screen entered")

    def get_log_widget(self):
        """Get the data_view widget directly from the current screen."""
        if 'data_view' not in self.ids:
            print("Error: data_view ID not found in Log screen")
            return None
        return self.ids.data_view

    def add_data_point_to_log_with_data(self, heart_rate, rmssd, sdnn):
        """Add a data point with specific physiological values from the camera feed."""
        data_view = self.get_log_widget()
        if not data_view:
            return False

        new_data = {
            'datetime': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'heart_rate': f"{heart_rate} BPM" if heart_rate else "No Signal",
            'rmssd': f"{rmssd:.1f} ms" if rmssd else "No Data",
            'sdnn': f"{sdnn:.1f} ms" if sdnn else "No Data",
            'index': len(data_view.data)
        }

        data_view.data = data_view.data + [new_data]
        data_view.refresh_from_data()

        if 'counter_label' in self.ids:
            self.ids.counter_label.text = f"Showing {len(data_view.data)} of {self.total_entries} entries"

        return True