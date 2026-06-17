import os
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.drawing.image import Image as ExcelImage
from core.config import LAYOUT_PRESETS
from core.image_processor import compress_image


class ExcelProcessor:
    def __init__(self, template_bytes, sheet_name, layout_name):
        self.template_bytes = template_bytes
        self.sheet_name = sheet_name
        self.layout = LAYOUT_PRESETS.get(layout_name, LAYOUT_PRESETS["LGJA"])

    def get_capacity(self):
        rows = self.layout["rows"]
        cols = self.layout["cols"]
        return len(rows) * len(cols)

    def get_cell_list(self):
        rows = self.layout["rows"]
        cols = self.layout["cols"]
        return [f"{chr(64 + col)}{row}" for row in rows for col in cols]

    def process(self, photo_paths, progress_callback=None):
        self.template_bytes.seek(0)
        wb = load_workbook(self.template_bytes)
        ws = wb[self.sheet_name]

        for c in self.layout["cols"]:
            ws.column_dimensions[chr(64 + c)].width = self.layout["col_w"]
        for r in self.layout["rows"]:
            ws.row_dimensions[r].height = self.layout["row_h"]

        all_cells = self.get_cell_list()
        total = min(len(photo_paths), len(all_cells))
        success = 0

        for i in range(total):
            try:
                buf = compress_image(photo_paths[i])
                img = ExcelImage(buf)
                img.width = int(self.layout["img_w"] * 37.8)
                img.height = int(self.layout["img_h"] * 37.8)
                ws.add_image(img, all_cells[i])
                success += 1
            except Exception as e:
                print(f"Error foto {i}: {e}")

            if progress_callback:
                progress_callback(i + 1, total)

        output = BytesIO()
        wb.save(output)
        wb.close()
        output.seek(0)
        return output, success
