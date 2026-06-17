import re
import os
from datetime import datetime, timedelta, timezone
from core.config import MONTH_MAP, OUTPUT_DIR


def convert_date_to_english(date_str):
    if not date_str or not date_str.strip():
        return ""
    date_str = date_str.strip()
    parts = date_str.split()
    if len(parts) == 3:
        day, month_abbr, year = parts
        month_key = month_abbr.lower()
        if month_key in MONTH_MAP:
            month_full = MONTH_MAP[month_key]
            if len(year) == 2 and year.isdigit():
                year = "20" + year
            return f"{day} {month_full} {year}"
    return date_str


def extract_datetime_from_filename(filename):
    match = re.search(r"(\d{4}-\d{2}-\d{2}) at (\d{2}\.\d{2}\.\d{2})", filename)
    if match:
        try:
            return datetime.strptime(
                f"{match.group(1)} {match.group(2).replace('.', ':')}",
                "%Y-%m-%d %H:%M:%S",
            )
        except Exception:
            pass
    return datetime.min


def generate_filename(toko, tanggal):
    toko_clean = toko.strip() if toko else "QC"
    tgl_clean = tanggal.strip() if tanggal else "Report"
    return f"{toko_clean} {tgl_clean}.xlsx"


def sort_photos_by_datetime(photo_paths):
    return sorted(
        photo_paths,
        key=lambda x: (
            extract_datetime_from_filename(os.path.basename(x)),
            os.path.getmtime(x) if os.path.exists(x) else 0,
        ),
        reverse=True,
    )


def format_timestamp():
    tz_jkt = timezone(timedelta(hours=7))
    return datetime.now(tz_jkt).strftime("%d %B %y / %H:%M")


def get_output_path(filename):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    return os.path.join(OUTPUT_DIR, filename)
