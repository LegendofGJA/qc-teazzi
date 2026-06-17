import os
import requests
from core.config import (
    PRESETS_DIR, OUTPUT_DIR, DATA_DIR, UPDATE_DIR,
    PRESET_FILES, NETWORK_TIMEOUT,
)


class SetupManager:
    def __init__(self):
        self.dirs = [PRESETS_DIR, OUTPUT_DIR, DATA_DIR, UPDATE_DIR]

    def is_first_run(self):
        if not os.path.isdir(PRESETS_DIR):
            return True
        cached = [
            f for f in PRESET_FILES
            if os.path.exists(os.path.join(PRESETS_DIR, f))
        ]
        return len(cached) == 0

    def create_directories(self):
        for d in self.dirs:
            os.makedirs(d, exist_ok=True)

    def download_all_presets(self, progress_callback=None):
        results = {}
        total = len(PRESET_FILES)
        for i, (filename, url) in enumerate(PRESET_FILES.items()):
            if progress_callback:
                progress_callback(i + 1, total, filename, "downloading")
            try:
                resp = requests.get(url, timeout=30)
                resp.raise_for_status()
                dest = os.path.join(PRESETS_DIR, filename)
                with open(dest, "wb") as f:
                    f.write(resp.content)
                results[filename] = True
                if progress_callback:
                    progress_callback(i + 1, total, filename, "success")
            except Exception as e:
                results[filename] = False
                if progress_callback:
                    progress_callback(i + 1, total, filename, f"error: {e}")
        return results

    def has_any_preset(self):
        for f in PRESET_FILES:
            path = os.path.join(PRESETS_DIR, f)
            if os.path.exists(path) and os.path.getsize(path) > 0:
                return True
        return False
