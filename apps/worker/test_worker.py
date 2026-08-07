import io
from PIL import Image
from worker import process_image


def _sample_png(w=1000, h=1000):
    img = Image.new("RGB", (w, h), (120, 60, 200))
    buf = io.BytesIO(); img.save(buf, format="PNG"); return buf.getvalue()


def test_produces_three_variants():
    variants = process_image(_sample_png())
    assert set(variants) == {"thumbnail.jpg", "medium.jpg", "image.webp"}


def test_thumbnail_is_downscaled():
    blob, ctype = process_image(_sample_png(1000, 1000))["thumbnail.jpg"]
    img = Image.open(io.BytesIO(blob))
    assert max(img.size) <= 150
    assert ctype == "image/jpeg"


def test_outputs_are_valid_images():
    for blob, _ in process_image(_sample_png()).values():
        Image.open(io.BytesIO(blob)).verify()   # ném lỗi nếu ảnh hỏng