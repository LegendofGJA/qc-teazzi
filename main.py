import os
import sys

# Tambahkan folder project ke path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.app import App
from kivy.core.window import Window
from kivy.utils import platform
from kivy.lang import Builder

# Load KV
Builder.load_file(os.path.join(os.path.dirname(__file__), "kv", "app.kv"))

from screens.splash_screen import SplashScreen
from screens.home_screen import HomeScreen


class QCteazziApp(App):
    title = "QC Teazzi"
    icon = "assets/icon.png"

    def build(self):
        Window.softinput_mode = "below_target"
        if platform == "android":
            self._request_permissions()
        from kivy.uix.screenmanager import ScreenManager
        sm = ScreenManager()
        sm.add_widget(SplashScreen())
        sm.add_widget(HomeScreen())
        return sm

    def _request_permissions(self):
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.INTERNET,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_MEDIA_IMAGES,
            ])
        except Exception:
            pass


if __name__ == "__main__":
    QCteazziApp().run()
