"""Make "scanned" copies of the Fernhill PDFs: every page becomes a picture, slightly tilted and grainy, the way a
printed page looks after it goes through a scanner. A scanned PDF holds no text at all, only pictures of text.

Run from the repository root, after make_pdfs.py:  python 06-parsing/make_scans.py
"""
import io
import random
from pathlib import Path

import pymupdf
from PIL import Image, ImageFilter

PDF_FOLDER = Path(__file__).parent / "pdfs"
SCAN_FOLDER = Path(__file__).parent / "scans"


def scan_page(page, seed):
    picture = page.get_pixmap(dpi=200, colorspace=pymupdf.csGRAY)
    image = Image.open(io.BytesIO(picture.tobytes("png")))
    shaky = random.Random(seed)
    image = image.rotate(shaky.uniform(-0.8, 0.8), fillcolor=245, resample=Image.BICUBIC)  # paper never lies flat
    image = image.filter(ImageFilter.GaussianBlur(0.5))                                     # a slightly soft focus
    pixels = image.load()
    for _ in range(image.width * image.height // 400):                                      # specks of dust
        x, y = shaky.randrange(image.width), shaky.randrange(image.height)
        pixels[x, y] = shaky.randrange(90, 200)
    jpeg = io.BytesIO()
    image.save(jpeg, "JPEG", quality=75)
    return jpeg.getvalue()


for pdf_path in sorted(PDF_FOLDER.rglob("*.pdf")):
    original = pymupdf.open(pdf_path)
    scanned = pymupdf.open()
    for number, page in enumerate(original):
        new_page = scanned.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(new_page.rect, stream=scan_page(page, seed=number))
    out_path = SCAN_FOLDER / pdf_path.relative_to(PDF_FOLDER)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    scanned.save(out_path)
    print("Scanned", out_path.relative_to(SCAN_FOLDER))
