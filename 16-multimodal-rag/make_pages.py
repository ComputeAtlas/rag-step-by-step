"""Turn the scanned PDFs into page pictures, and add the three figures as pages of their own.

The scans come from the parsing lesson (06-parsing/make_scans.py): 33 Fernhill documents, printed and "scanned", with no
text inside, only pictures of text. Every page becomes one JPEG picture in 16-multimodal-rag/results/pages/, and
16-multimodal-rag/results/pages.json lists them all with the document each one came from.

Run from the repository root, after 06-parsing/make_pdfs.py, 06-parsing/make_scans.py and make_figures.py:
    python 16-multimodal-rag/make_pages.py
"""
import json
import shutil
from pathlib import Path

import pymupdf

SCAN_FOLDER = Path("06-parsing/scans")
FIGURE_FOLDER = Path("16-multimodal-rag/figures")
PAGE_FOLDER = Path("16-multimodal-rag/results/pages")
PAGE_FOLDER.mkdir(parents=True, exist_ok=True)

pages = []
for pdf_path in sorted(SCAN_FOLDER.rglob("*.pdf")):
    source = str(pdf_path.relative_to(SCAN_FOLDER).with_suffix(".md"))   # e.g. manuals/metro-300-owners-manual.md
    document = pymupdf.open(pdf_path)
    for number, page in enumerate(document, start=1):
        name = source.replace("/", "__").replace(".md", f"-p{number}.jpg")
        picture = page.get_pixmap(dpi=150)        # 150 dots per inch: about 1240 x 1754 pixels for an A4 page
        picture.save(PAGE_FOLDER / name, jpg_quality=85)
        pages.append({"file": name, "source": source, "page": number})

for figure_path in sorted(FIGURE_FOLDER.glob("*.png")):
    name = "figure__" + figure_path.name
    shutil.copy(figure_path, PAGE_FOLDER / name)
    pages.append({"file": name, "source": f"figures/{figure_path.name}", "page": 1})

with open("16-multimodal-rag/results/pages.json", "w") as file:
    json.dump(pages, file, indent=1)

documents = len({p["source"] for p in pages})
print(f"{len(pages)} page pictures from {documents} documents and figures, in {PAGE_FOLDER}")
