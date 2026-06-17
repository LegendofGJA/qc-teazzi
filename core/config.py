import os
from kivy.utils import platform

# ═══════════════════════════════════════════
# VERSI APLIKASI
# ═══════════════════════════════════════════
APP_VERSION = "1.0.0"
APP_VERSION_CODE = 1

# ═══════════════════════════════════════════
# GITHUB (PRESET + UPDATE)
# ═══════════════════════════════════════════
GITHUB_RAW_BASE = (
    "https://raw.githubusercontent.com/LegendofGJA/QC-excel-inserter-exe/main/presets"
)
PRESET_FILES = {
    "QC_LGJA.xlsx": f"{GITHUB_RAW_BASE}/QC_LGJA.xlsx",
    "QC_Sultan.xlsx": f"{GITHUB_RAW_BASE}/QC_Sultan.xlsx",
    "QC_Vano.xlsx": f"{GITHUB_RAW_BASE}/QC_Vano.xlsx",
}

VERSION_CHECK_URL = (
    "https://raw.githubusercontent.com/LegendofGJA/qc-teazzi/main/version.json"
)

# ═══════════════════════════════════════════
# TRAFFIC LOG API
# ═══════════════════════════════════════════
TRAFFIC_API_URL = (
    "https://jsonblob.com/api/jsonBlob/019e8740-72c4-7731-8328-0e2c67465233"
)
NETWORK_TIMEOUT = 5

# ═══════════════════════════════════════════
# PATH DI ANDROID
# ═══════════════════════════════════════════
if platform == "android":
    from jnius import autoclass

    Environment = autoclass("android.os.Environment")
    _ext = Environment.getExternalStorageDirectory().getAbsolutePath()
    BASE_DIR = os.path.join(_ext, "Download", "QCTeazzi")
else:
    BASE_DIR = os.path.join(os.path.expanduser("~"), "QCTeazzi")

PRESETS_DIR = os.path.join(BASE_DIR, "presets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DATA_DIR = os.path.join(BASE_DIR, "data")
UPDATE_DIR = os.path.join(BASE_DIR, "update")
DB_PATH = os.path.join(DATA_DIR, "traffic.db")

# ═══════════════════════════════════════════
# LAYOUT PRESETS
# ═══════════════════════════════════════════
LAYOUT_PRESETS = {
    "LGJA": {
        "rows": [2, 4, 6, 8, 10, 12],
        "cols": list(range(1, 13)),
        "col_w": 41,
        "row_h": 246,
        "img_w": 6.4,
        "img_h": 8.30,
    },
    "Sultan": {
        "rows": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30],
        "cols": [1, 2, 3, 4, 5, 6],
        "col_w": 20.43,
        "row_h": 123.75,
        "img_w": 3.2,
        "img_h": 4.10,
    },
    "Vano": {
        "rows": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30],
        "cols": [1, 2, 3, 4, 5, 6],
        "col_w": 20.43,
        "row_h": 123.75,
        "img_w": 3.2,
        "img_h": 4.10,
    },
}

# ═══════════════════════════════════════════
# KONVERSI BULAN
# ═══════════════════════════════════════════
MONTH_MAP = {
    "jan": "January",
    "januari": "January",
    "feb": "February",
    "februari": "February",
    "mar": "March",
    "maret": "March",
    "apr": "April",
    "mei": "May",
    "may": "May",
    "jun": "June",
    "juni": "June",
    "jul": "July",
    "juli": "July",
    "agu": "August",
    "agustus": "August",
    "aug": "August",
    "sep": "September",
    "okt": "October",
    "oktober": "October",
    "oct": "October",
    "nov": "November",
    "des": "December",
    "dec": "December",
}

# ═══════════════════════════════════════════
# WARNA UI
# ═══════════════════════════════════════════
COLORS = {
    "bg": (0.043, 0.043, 0.071, 1),
    "surface": (0.071, 0.071, 0.125, 1),
    "surface2": (0.098, 0.098, 0.188, 1),
    "border": (0.118, 0.118, 0.208, 1),
    "text": (0.918, 0.918, 0.949, 1),
    "text_sec": (0.533, 0.533, 0.647, 1),
    "text_muted": (0.314, 0.314, 0.416, 1),
    "accent": (0.898, 0.196, 0.176, 1),
    "accent_soft": (0.898, 0.196, 0.176, 0.10),
    "green": (0.063, 0.725, 0.506, 1),
    "yellow": (0.961, 0.620, 0.043, 1),
    "white": (1, 1, 1, 1),
}
