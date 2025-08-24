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
class PhysMonitoringApp(BoxLayout):
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
    
    def on_state(self, instance, value):
        """ Called when the state of the toggle button changes. (Navigate Home-Log, vice versa) """
        if value == 'down':
            # Only switch screen when button is pressed down
            self.switch_screen(self.screen_name)
    
    def switch_screen(self, screen_name):
        """
        Switches the current screen in the app to the one specified by screen_name.

        Steps:
        1. Get the running Kivy App instance.
        2. Check if the app and its root widget exist. If not, log an error and exit.
        3. Try to access the ScreenManager via the root widget's ids dictionary (if defined in .kv file).
           - If found, set its current screen and log the action.
        4. If not found via ids, search the widget tree for a ScreenManager instance using walk().
           - If found, set its current screen and log the action.
        5. If no ScreenManager is found, log an error.
        """
        app = App.get_running_app()
        if not app or not hasattr(app, 'root') or app.root is None:
            logger.error("No running app or root widget found")
            return

        # Try to get ScreenManager via ids (recommended if using .kv file)
        scrn_manager = getattr(app.root, 'ids', {}).get('scrn_manager', None) if hasattr(app.root, 'ids') else None
        if scrn_manager:
            # Found ScreenManager via ids
            scrn_manager.current = screen_name
            logger.debug(f"Switched screen to: {screen_name} via ids")
            return

        # Fallback: search widget tree for ScreenManager
        sm = self.find_screen_manager(app.root)
        if sm:
            # Found ScreenManager via walk
            sm.current = screen_name
            logger.debug(f"Switched screen to: {screen_name} via walk")
        else:
            # No ScreenManager found
            logger.error("Screen manager not found in app.root.ids or widget tree")
    
    def find_screen_manager(self, widget):
        """
        Searches the widget tree starting from the given widget for a ScreenManager instance.
        Uses Kivy's walk() method to traverse all descendants.
        Returns the first ScreenManager found, or None if not found.
        """
        from kivy.uix.screenmanager import ScreenManager
        for child in widget.walk():
            if isinstance(child, ScreenManager):
                logger.debug(f"Found screen manager via walk: {child}")
                return child
        return None