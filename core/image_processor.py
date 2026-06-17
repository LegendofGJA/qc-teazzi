import os
from io import BytesIO
from PIL import Image as PILImage, ExifTags


def correct_orientation(img):
    try:
        if hasattr(img, "_getexif") and img._getexif() is not None:
            exif = img._getexif()
            orientation = exif.get(ExifTags.Base.Orientation)
            if orientation == 3:
                img = img.rotate(180, expand=True)
            elif orientation == 6:
                img = img.rotate(270, expand=True)
            elif orientation == 8:
                img = img.rotate(90, expand=True)
    except Exception:
        pass
    return img


def compress_image(source_path):
    buf = BytesIO()
    with PILImage.open(source_path) as img_pil:
        img_pil = correct_orientation(img_pil)
        if img_pil.mode in ("RGBA", "P"):
            img_pil = img_pil.convert("RGB")
        img_pil.thumbnail((1280, 1280), PILImage.Resampling.LANCZOS)
        img_pil.save(buf, format="JPEG", quality=82, optimize=True, subsampling=0)
    buf.seek(0)
    return buf


def get_image_info(source_path):
    try:
        size_kb = round(os.path.getsize(source_path) / 1024, 1)
        with PILImage.open(source_path) as img:
            w, h = img.size
        return {
            "filename": os.path.basename(source_path),
            "size_kb": size_kb,
            "dimensions": f"{w}x{h}",
        }
    except Exception:
        return {
            "filename": os.path.basename(source_path),
            "size_kb": 0,
            "dimensions": "unknown",
        }
