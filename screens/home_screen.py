import os
import threading
from io import BytesIO
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.utils import platform
from core.config import LAYOUT_PRESETS, OUTPUT_DIR
from core.preset_loader import PresetLoader
from core.excel_processor import ExcelProcessor
from core.traffic_logger import TrafficLogger
from core.utils import (
    convert_date_to_english,
    generate_filename,
    sort_photos_by_datetime,
    format_timestamp,
    get_output_path,
)


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.preset_loader = PresetLoader()
        self.traffic = TrafficLogger()
        self.photo_paths = []
        self.output_path = None
        self.sheet_names = []
        self.temp_dir = None
        self._temp_counter = 0

    def on_enter(self):
        self.traffic.sync_on_startup()
        self._init_temp()
        self._setup_template_dropdown()
        self._setup_layout_dropdown()

    def _init_temp(self):
        self.temp_dir = os.path.join(
            os.path.dirname(OUTPUT_DIR), "temp_photos"
        )
        os.makedirs(self.temp_dir, exist_ok=True)

    # ── TEMPLATE DROPDOWN ──
    def _setup_template_dropdown(self):
        options = self.preset_loader.get_dropdown_options()
        self.ids.dd_template.values = options
        cached = self.preset_loader.list_cached()
        if cached:
            self.ids.dd_template.text = f"{cached[0]} ✓"
            self._on_template_change(cached[0])
        else:
            self.ids.dd_template.text = "Upload Manual"

    def _on_template_selected(self, value):
        real = self.preset_loader.get_real_filename(value)
        if real == "Upload Manual":
            self._pick_template_file()
            return
        if real == "─────────────":
            return
        self._on_template_change(real)

    def _on_template_change(self, filename):
        self.sheet_names = self.preset_loader.get_sheet_names(filename)
        self.ids.dd_sheet.values = self.sheet_names
        if self.sheet_names:
            default = "ATTACHMENT" if "ATTACHMENT" in self.sheet_names else self.sheet_names[0]
            self.ids.dd_sheet.text = default

    def _pick_template_file(self):
        if platform == "android":
            try:
                from plyer import filechooser
                filechooser.open_file(
                    on_selection=self._on_template_picked,
                    filters=["*.xlsx"],
                )
            except Exception:
                pass
        else:
            from plyer import filechooser
            filechooser.open_file(
                on_selection=self._on_template_picked,
                filters=["*.xlsx"],
            )

    def _on_template_picked(self, selection):
        if not selection:
            return
        path = selection[0]
        if platform == "android" and path.startswith("content://"):
            path = self._resolve_content_uri(path)
        if path and os.path.exists(path):
            self.sheet_names = self.preset_loader.get_sheet_names(file_bytes=None)
            try:
                from openpyxl import load_workbook
                wb = load_workbook(path, read_only=True)
                self.sheet_names = wb.sheetnames
                wb.close()
            except Exception:
                pass
            self._manual_template_path = path
            self.ids.dd_template.text = os.path.basename(path)
            self.ids.dd_sheet.values = self.sheet_names
            if self.sheet_names:
                self.ids.dd_sheet.text = self.sheet_names[0]

    # ── LAYOUT DROPDOWN ──
    def _setup_layout_dropdown(self):
        self.ids.dd_layout.values = list(LAYOUT_PRESETS.keys()) + ["Custom"]
        self.ids.dd_layout.text = "LGJA"
        self._update_layout_info("LGJA")

    def _on_layout_selected(self, value):
        self._update_layout_info(value)

    def _update_layout_info(self, name):
        if name in LAYOUT_PRESETS:
            p = LAYOUT_PRESETS[name]
            rows = len(p["rows"])
            cols = len(p["cols"])
            self.ids.lbl_layout_info.text = (
                f"{rows} baris x {cols} kolom | {p['img_w']} x {p['img_h']} cm"
            )
        else:
            self.ids.lbl_layout_info.text = "Atur manual di Custom"

    # ── FOTO PICKER ──
    def pick_photos(self):
        if platform == "android":
            try:
                from plyer import filechooser
                filechooser.open_file(
                    on_selection=self._on_photos_picked, multiple=True
                )
            except Exception:
                pass
        else:
            from plyer import filechooser
            filechooser.open_file(
                on_selection=self._on_photos_picked, multiple=True
            )

    def _on_photos_picked(self, selection):
        if not selection:
            return
        paths = []
        for item in selection:
            if platform == "android" and str(item).startswith("content://"):
                resolved = self._resolve_content_uri(str(item))
                if resolved:
                    paths.append(resolved)
            else:
                paths.append(str(item))
        self.photo_paths = sort_photos_by_datetime(paths)
        self.ids.lbl_photo_count.text = f"{len(self.photo_paths)} foto dipilih"

    def _resolve_content_uri(self, uri_string):
        try:
            from jnius import autoclass

            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Uri = autoclass("android.net.Uri")

            activity = PythonActivity.mActivity
            uri = Uri.parse(uri_string)
            cursor = activity.getContentResolver().query(
                uri, ["_data"], None, None, None
            )
            if cursor:
                idx = cursor.getColumnIndexOrThrow("_data")
                cursor.moveToFirst()
                path = cursor.getString(idx)
                cursor.close()
                if path and os.path.exists(path):
                    return path
            return self._copy_uri_to_temp(uri_string)
        except Exception:
            return self._copy_uri_to_temp(uri_string)

    def _copy_uri_to_temp(self, uri_string):
        try:
            from jnius import autoclass

            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Uri = autoclass("android.net.Uri")

            activity = PythonActivity.mActivity
            cr = activity.getContentResolver()
            uri = Uri.parse(uri_string)
            istream = cr.openInputStream(uri)

            temp_path = os.path.join(self.temp_dir, f"photo_{self._temp_counter}.jpg")
            self._temp_counter += 1

            with open(temp_path, "wb") as f:
                while True:
                    b = istream.read()
                    if b == -1:
                        break
                    f.write(bytes([b]))

            istream.close()
            return temp_path
        except Exception as e:
            print(f"Copy URI error: {e}")
            return None

    # ── PROSES ──
    def start_process(self):
        user = self.ids.inp_user.text.strip()
        toko = self.ids.inp_toko.text.strip()
        tanggal = self.ids.inp_tanggal.text.strip()

        if not user:
            self.ids.lbl_status.text = "[color=ff6b6b]Isi Nama Pengguna![/color]"
            return
        if not toko or not tanggal:
            self.ids.lbl_status.text = "[color=ff6b6b]Isi Nama Toko dan Tanggal![/color]"
            return
        if not self.photo_paths:
            self.ids.lbl_status.text = "[color=ff6b6b]Pilih foto terlebih dahulu![/color]"
            return

        template_text = self.ids.dd_template.text
        sheet = self.ids.dd_sheet.text
        layout = self.ids.dd_layout.text

        if not sheet:
            self.ids.lbl_status.text = "[color=ff6b6b]Pilih Target Sheet![/color]"
            return

        self.ids.btn_process.disabled = True
        self.ids.progress_bar.value = 0
        self.ids.lbl_status.text = "Memproses..."

        threading.Thread(
            target=self._process_worker,
            args=(user, toko, tanggal, template_text, sheet, layout),
            daemon=True,
        ).start()

    def _process_worker(self, user, toko, tanggal, template_text, sheet, layout):
        try:
            real_name = self.preset_loader.get_real_filename(template_text)

            if hasattr(self, "_manual_template_path"):
                template_bytes = BytesIO(open(self._manual_template_path, "rb").read())
            else:
                template_bytes = self.preset_loader.load_preset(real_name)

            if not template_bytes:
                Clock.schedule_once(
                    lambda dt: self._set_status("Template tidak ditemukan!"), 0
                )
                return

            processor = ExcelProcessor(template_bytes, sheet, layout)

            def on_progress(current, total):
                pct = int((current / total) * 100)
                Clock.schedule_once(
                    lambda dt: self._update_progress(pct, current, total), 0
                )

            output_bytes, success = processor.process(self.photo_paths, on_progress)

            filename = generate_filename(toko, tanggal)
            self.output_path = get_output_path(filename)
            with open(self.output_path, "wb") as f:
                f.write(output_bytes.getvalue())

            self.traffic.log(user, toko, tanggal, layout)

            Clock.schedule_once(
                lambda dt: self._on_process_done(success), 0
            )
        except Exception as e:
            Clock.schedule_once(
                lambda dt: self._set_status(f"Error: {e}"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self._enable_button(), 0
            )

    def _update_progress(self, pct, current, total):
        self.ids.progress_bar.value = pct
        self.ids.lbl_status.text = f"Mengompres foto {current}/{total}..."

    def _on_process_done(self, count):
        fname = os.path.basename(self.output_path) if self.output_path else ""
        self.ids.lbl_status.text = (
            f"[color=6ee7b7]Berhasil! {count} foto disusun.[/color]"
        )
        self.ids.lbl_output_path.text = fname
        self.ids.result_box.opacity = 1
        self.ids.result_box.disabled = False

    def _set_status(self, text):
        self.ids.lbl_status.text = text

    def _enable_button(self):
        self.ids.btn_process.disabled = False

    # ── OUTPUT ACTIONS ──
    def share_file(self):
        if not self.output_path:
            return
        if platform == "android":
            try:
                from plyer import share
                share.share(
                    title="Share QC Report",
                    text="Laporan QC dari QC Teazzi",
                    filepath=self.output_path,
                )
            except Exception as e:
                print(f"Share error: {e}")

    def open_folder(self):
        if not self.output_path:
            return
        folder = os.path.dirname(self.output_path)
        if platform == "android":
            try:
                from jnius import autoclass

                Intent = autoclass("android.content.Intent")
                Uri = autoclass("android.net.Uri")
                File = autoclass("java.io.File")
                PythonActivity = autoclass("org.kivy.android.PythonActivity")

                activity = PythonActivity.mActivity
                uri = Uri.fromFile(File(folder))
                intent = Intent(Intent.ACTION_VIEW)
                intent.setDataAndType(uri, "resource/folder")
                intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                activity.startActivity(intent)
            except Exception:
                pass

    def open_file(self):
        if not self.output_path:
            return
        if platform == "android":
            try:
                from jnius import autoclass

                Intent = autoclass("android.content.Intent")
                Uri = autoclass("android.net.Uri")
                File = autoclass("java.io.File")
                PythonActivity = autoclass("org.kivy.android.PythonActivity")

                activity = PythonActivity.mActivity
                uri = Uri.fromFile(File(self.output_path))
                intent = Intent(Intent.ACTION_VIEW)
                intent.setDataAndType(
                    uri,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
                intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                activity.startActivity(intent)
            except Exception:
                pass
