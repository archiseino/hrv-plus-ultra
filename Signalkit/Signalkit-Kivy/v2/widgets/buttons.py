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

<RoundedButton>:
    text_size: self.size
    halign: "center"
    valign: "middle"
    color: self.color_text
    canvas.before:
        Color:
            rgba: self.color_normal if self.state == 'normal' else self.color_down
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.border_radius]
        Color:
            rgba: self.border_color
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, self.border_radius)
            width: 1

<DarkRoundedButton>:
    # DarkRoundedButton inherits styling from RoundedButton with custom colors

<CircleButton>:
    text_size: self.size
    halign: "center"
    valign: "middle"
    color: self.color_text
    canvas.before:
        Color:
            rgba: self.color_normal if self.state == 'normal' else self.color_down
        RoundedRectangle:
            pos: self.pos[0] + dp(12), self.pos[1] + dp(15)
            size: dp(16), dp(16) 
            radius: [self.border_radius]
                    
""")

from kivy.uix.button import Button
from kivy.properties import ListProperty, ColorProperty, NumericProperty
from kivy.lang import Builder

# Load KV file
Builder.load_file('d:/Stuff That I Need to Do/Template-Phys/Aleph0/widgets/rounded_buttons.kv')

class RoundedButton(Button):
    """A button with rounded corners."""
    color_normal = ColorProperty([0.9, 0.9, 0.9, 1])
    color_down = ColorProperty([0.8, 0.8, 0.8, 1])
    color_text = ColorProperty([0.3, 0.3, 0.3, 1])
    border_radius = NumericProperty(18)
    border_color = ColorProperty([0.8, 0.8, 0.8, 1])
    
    def __init__(self, **kwargs):
        super(RoundedButton, self).__init__(**kwargs)
        self.background_color = [0, 0, 0, 0]  # Transparent background
        self.background_normal = ''
        self.background_down = ''
        
class DarkRoundedButton(RoundedButton):
    """A dark-themed rounded button."""
    def __init__(self, **kwargs):
        super(DarkRoundedButton, self).__init__(**kwargs)
        self.color_normal = [0.2, 0.2, 0.2, 1]
        self.color_down = [0.3, 0.3, 0.3, 1]
        self.color_text = [1, 1, 1, 1]
        self.border_color = [0.2, 0.2, 0.2, 1]

class CircleButton(Button):
    """A small circular button, typically used for actions."""
    color_normal = ColorProperty([0.95, 0.95, 0.95, 1])
    color_down = ColorProperty([0.85, 0.85, 0.85, 1])
    color_text = ColorProperty([0.5, 0.5, 0.5, 1])
    border_radius = NumericProperty(10)
    
    def __init__(self, **kwargs):
        super(CircleButton, self).__init__(**kwargs)
        self.background_color = [0, 0, 0, 0]  # Transparent background
        self.background_normal = ''
        self.background_down = ''

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
