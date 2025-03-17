from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.switch import Switch

Builder.load_string("""
<Text>:
    text_size: self.size
    valign: "middle"
    font_name: app.fonts.subheading
    shorten_from: "right"
    shorten: True
    color: [0,0,0, 1]
    markup: True
                    
<CustomTextInput>:
    size_hint: None, None
    size: 200, 50
    font_size: '16sp'
    multiline: False
    padding: [10, 10]
    background_normal: ''
    background_color: 1, 1, 1, 1
    foreground_color: 0, 0, 0, 1

<LiveDataLabel>:
    size_hint: None, None
    size: 150, 50
    Label:
        id: data_label
        text: "Data: 0"

<ToggleSwitch>:
    size_hint: None, None
    size: 100, 50
    Switch:
        id: toggle_switch

""")

class Text(Label):
    def __init__(self, **keywords):
        super().__init__(**keywords)

class CustomTextInput(TextInput):
    pass

class LiveDataLabel(BoxLayout):
    def update_data(self, data):
        self.ids.data_label.text = f"Data: {data}"

class ToggleSwitch(Switch):
    def is_active(self):
        return self.active
