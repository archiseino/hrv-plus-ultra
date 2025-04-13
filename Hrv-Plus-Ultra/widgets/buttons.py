from kivy.lang import Builder
from kivy.uix.button import Button

## Import Properties for Button Attribute
from kivy.properties import ColorProperty, ListProperty, StringProperty
from kivy.graphics import RoundedRectangle, Color
from kivy.metrics import dp

Builder.load_string("""
<FlatButton>:
    text_size: self.size
    valign: "middle"
    halign: "center"

<IconButton>:
    size_hint: 0, None
    size: 16, 16
    on_press: self.on_click()
    valign: "middle"
    canvas.after:
        Color:
            rgba: [1,1,1,1]
        Rectangle:
            pos: self.pos
            size: self.size
            source: self.source
                    
<CustomButton>:
    size_hint: None, None
    size: 150, 50
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [20,]
    background_color: 0.2, 0.6, 1, 1
    font_size: '16sp'
    background_normal: ''
    background_down: ''
    on_press: root.on_click()

""")

class FlatButton(Button):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.background_color = [0,0,0,0]
        self.background_down = ""
        self.background_normal = ""
        self.background_disabled = ""
        self.markup = True

class IconButton(FlatButton):
    source = StringProperty("")
    def __init__(self, **kw):
        super().__init__(**kw)

    def on_click(self):
        print("Jawa")

class CustomButton(FlatButton):
    def __init__(self, text="Jawa", **kwargs):
        super().__init__(text=text, **kwargs)
    
    def on_click(self):
        print(f"{self.text} button clicked!")
