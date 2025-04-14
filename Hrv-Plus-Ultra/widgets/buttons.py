from kivy.lang import Builder
from kivy.uix.button import Button

## Import Properties for Button Attribute
from kivy.properties import StringProperty
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
        """ Add your click action here  """
        print("IconButton clicked")
