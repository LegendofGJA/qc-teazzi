import threading
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from core.setup_manager import SetupManager
from core.updater import Updater


class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup = SetupManager()
        self.updater = Updater()
        self.download_results = {}

    def on_enter(self):
        Clock.schedule_once(self._start, 0.5)

    def _start(self, dt):
        self.ids.splash_status.text = "Mengecek template..."
        self.ids.splash_progress.value = 0
        self.ids.splash_buttons.opacity = 0
        self.ids.splash_buttons.disabled = True

        if self.setup.has_any_preset():
            self.ids.splash_status.text = "Template ditemukan. Memuat..."
            self.ids.splash_progress.value = 100
            Clock.schedule_once(lambda dt: self._go_home(), 0.5)
        else:
            self._download_presets()

    def _download_presets(self):
        self.ids.splash_status.text = "Mengunduh template dari GitHub..."
        threading.Thread(target=self._download_worker, daemon=True).start()

    def _download_worker(self):
        def progress(current, total, filename, status):
            pct = int((current / total) * 100)
            Clock.schedule_once(
                lambda dt: self._update_progress(pct, current, total, filename, status)
            )

        self.download_results = self.setup.download_all_presets(progress)
        Clock.schedule_once(lambda dt: self._on_download_done(), 0.5)

    def _update_progress(self, pct, current, total, filename, status):
        self.ids.splash_progress.value = pct
        if status == "downloading":
            self.ids.splash_status.text = (
                f"Mengunduh {current}/{total}: {filename}..."
            )
        elif status == "success":
            self.ids.splash_status.text = (
                f"✓ {current}/{total}: {filename}"
            )

    def _on_download_done(self):
        success = sum(1 for v in self.download_results.values() if v)
        total = len(self.download_results)

        if success == total:
            self.ids.splash_status.text = f"Semua {total} template berhasil diunduh!"
            self.ids.splash_progress.value = 100
            Clock.schedule_once(lambda dt: self._go_home(), 0.8)
        elif success > 0:
            self.ids.splash_status.text = (
                f"{success}/{total} template berhasil. Sisa gagal."
            )
            self.ids.splash_progress.value = int((success / total) * 100)
            self._show_buttons(retry=True, skip=True)
        else:
            self.ids.splash_status.text = "Gagal mengunduh template. Periksa internet."
            self._show_buttons(retry=True, skip=True)

    def _show_buttons(self, retry=True, skip=True):
        self.ids.btn_retry.opacity = 1 if retry else 0
        self.ids.btn_retry.disabled = not retry
        self.ids.btn_skip.opacity = 1 if skip else 0
        self.ids.btn_skip.disabled = not skip
        self.ids.splash_buttons.opacity = 1
        self.ids.splash_buttons.disabled = False

    def retry_download(self):
        self.ids.splash_buttons.opacity = 0
        self.ids.splash_buttons.disabled = True
        self._download_presets()

    def skip_download(self):
        self._go_home()

    def _go_home(self):
        self.updater.check_async()
        self.manager.current = "home"
