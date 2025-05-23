from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.properties import StringProperty
from kivy.app import App
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

"""
🚪 Root Container for Future build.

This is the main container for the App. 

Kivy can be scaled as Desktop app, so one potential update is making a Navigation for other feature. 
But I'll leave as a Trivia for you

"""
class StressMonitorLayout(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)

class NavTab(ToggleButtonBehavior, BoxLayout):
    """ A tab for the navigation bar. """
    text = StringProperty("")
    icon = StringProperty("")
    icon_active = StringProperty("")
    screen_name = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.debug(f"NavTab initialized with screen_name: {self.screen_name}")
    
    def on_state(self, instance, value):
        """ Called when the state of the toggle button changes. """
        logger.debug(f"NavTab state changed to: {value} for screen: {self.screen_name}")
        if value == 'down':
            # Only switch screen when button is pressed down
            self.switch_screen(self.screen_name)
    
    def switch_screen(self, screen_name):
        """ Switch to the screen associated with this tab. """
        logger.debug(f"Attempting to switch to screen: {screen_name}")
        app = App.get_running_app()
        logger.debug(f"Got app instance: {app}")
        
        if app:
            logger.debug(f"App root: {app.root}")
            logger.debug(f"App root ids: {app.root.ids if hasattr(app.root, 'ids') else 'No ids attribute'}")
            
            if hasattr(app.root, 'ids') and 'scrn_manager' in app.root.ids:
                logger.debug(f"Screen manager found: {app.root.ids.scrn_manager}")
                current_screen = app.root.ids.scrn_manager.current
                logger.debug(f"Current screen before switch: {current_screen}")
                app.root.ids.scrn_manager.current = screen_name
                logger.debug(f"Switched screen to: {screen_name}")
            else:
                logger.error("Screen manager not found in app.root.ids")
                # Try to find the screen manager by iterating through the widget tree
                self.find_screen_manager(app.root, screen_name)
        else:
            logger.error("No running app found")
    
    def find_screen_manager(self, widget, screen_name):
        """Recursively search for the screen manager in the widget tree"""
        logger.debug(f"Searching in widget: {widget}")
        if hasattr(widget, 'children'):
            for child in widget.children:
                logger.debug(f"Checking child: {child}")
                if hasattr(child, 'id') and child.id == 'scrn_manager':
                    logger.debug(f"Found screen manager: {child}")
                    child.current = screen_name
                    return True
                if self.find_screen_manager(child, screen_name):
                    return True
        return False