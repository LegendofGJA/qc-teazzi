import os
import threading
import requests
from core.config import (
    APP_VERSION_CODE, UPDATE_DIR, VERSION_CHECK_URL, NETWORK_TIMEOUT,
)


class Updater:
    def __init__(self, on_update_available=None):
        self.on_update_available = on_update_available
        self.update_info = None

    def check_async(self):
        threading.Thread(target=self._check, daemon=True).start()

    def _check(self):
        try:
            resp = requests.get(VERSION_CHECK_URL, timeout=NETWORK_TIMEOUT)
            if resp.status_code != 200:
                return
            info = resp.json()
            remote_code = info.get("version_code", 0)
            if remote_code > APP_VERSION_CODE:
                self.update_info = info
                if self.on_update_available:
                    self.on_update_available(info)
        except Exception:
            pass

    def download_update(self, progress_callback=None):
        if not self.update_info:
            return None
        url = self.update_info.get("download_url", "")
        if not url:
            return None
        try:
            os.makedirs(UPDATE_DIR, exist_ok=True)
            filename = url.split("/")[-1]
            dest = os.path.join(UPDATE_DIR, filename)
            resp = requests.get(url, stream=True, timeout=60)
            total = int(resp.headers.get("content-length", 0))
            downloaded = 0
            with open(dest, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total > 0:
                        progress_callback(downloaded, total)
            return dest
        except Exception:
            return None

    @staticmethod
    def install_apk(apk_path):
        from kivy.utils import platform

        if platform != "android":
            return
        try:
            from jnius import autoclass

            Intent = autoclass("android.content.Intent")
            Uri = autoclass("android.net.Uri")
            File = autoclass("java.io.File")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")

            activity = PythonActivity.mActivity
            f = File(apk_path)
            uri = Uri.fromFile(f)

            intent = Intent(Intent.ACTION_VIEW)
            intent.setDataAndType(uri, "application/vnd.android.package-archive")
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            activity.startActivity(intent)
        except Exception as e:
            print(f"Install error: {e}")
