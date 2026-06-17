import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.app import App
from kivy.core.window import Window
from kivy.utils import platform
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.logger import Logger


class QCteazziApp(App):
    title = "QC Teazzi"
    icon = "assets/icon.png"

    def build(self):
        Window.softinput_mode = "below_target"

        if platform == "android":
            self._request_permissions()
            self._setup_fileprovider()

        # Load KV
        kv_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "kv", "app.kv"
        )
        if not os.path.exists(kv_path):
            kv_path = "/data/data/com.lgja.qcteazzi/files/app/kv/app.kv"

        Logger.info(f"QC Teazzi: Loading KV from {kv_path}")
        Builder.load_file(kv_path)

        from screens.splash_screen import SplashScreen
        from screens.home_screen import HomeScreen

        sm = ScreenManager()
        sm.add_widget(SplashScreen())
        sm.add_widget(HomeScreen())
        return sm

    def _request_permissions(self):
        try:
            from android.permissions import request_permissions, Permission
            perms = [
                Permission.INTERNET,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
            ]
            # Android 13+ needs READ_MEDIA_IMAGES
            try:
                perms.append(Permission.READ_MEDIA_IMAGES)
            except Exception:
                pass
            request_permissions(perms)
            Logger.info("QC Teazzi: Permissions requested")
        except Exception as e:
            Logger.error(f"QC Teazzi: Permission error: {e}")

    def _setup_fileprovider(self):
        """Create file_paths.xml for FileProvider."""
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            activity = PythonActivity.mActivity

            # Create file_paths.xml in res/xml/
            res_dir = os.path.join(activity.getFilesDir().getParent(), "res", "xml")
            os.makedirs(res_dir, exist_ok=True)

            xml_content = """<?xml version="1.0" encoding="utf-8"?>
<paths>
    <external-path name="external" path="." />
    <cache-path name="cache" path="." />
    <files-path name="files" path="." />
</paths>"""

            xml_path = os.path.join(res_dir, "file_paths.xml")
            with open(xml_path, "w") as f:
                f.write(xml_content)

            Logger.info("QC Teazzi: FileProvider configured")
        except Exception as e:
            Logger.error(f"QC Teazzi: FileProvider setup error: {e}")


if __name__ == "__main__":
    QCteazziApp().run()
