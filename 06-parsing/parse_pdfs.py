"""Read every Fernhill PDF with one parser and save the text it gets, one text file per PDF.

Run from the repository root, once per parser and folder ("pdfs" or "scans"):
    python 06-parsing/parse_pdfs.py pypdf pdfs
    python 06-parsing/parse_pdfs.py pdfplumber pdfs
    python 06-parsing/parse_pdfs.py pymupdf4llm pdfs
    python 06-parsing/parse_pdfs.py pymupdf4llm scans
"""
import sys
from pathlib import Path

import pdfplumber
import pymupdf4llm
from pypdf import PdfReader

HERE = Path(__file__).parent


def read_with_pypdf(path):
    reader = PdfReader(path)
    return "\n".join(page.extract_text() for page in reader.pages)


def read_with_pdfplumber(path):
    with pdfplumber.open(path) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages)


def read_with_pymupdf4llm(path):
    # Layout-aware: headings and tables come back as Markdown; the page header and footer are left out.
    # A page with no text at all (a scan) is read with OCR, if Tesseract is installed.
    return pymupdf4llm.to_markdown(str(path), header=False, footer=False)


PARSERS = {"pypdf": read_with_pypdf, "pdfplumber": read_with_pdfplumber, "pymupdf4llm": read_with_pymupdf4llm}

parser_name = sys.argv[1]
folder_name = sys.argv[2]
read = PARSERS[parser_name]
pdf_folder = HERE / folder_name
out_folder = HERE / "parsed" / f"{folder_name}-{parser_name}"

for pdf_path in sorted(pdf_folder.rglob("*.pdf")):
    text = read(pdf_path)
    out_path = out_folder / pdf_path.relative_to(pdf_folder).with_suffix(".txt")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text)
    print(f"{len(text.split()):6d} words  {pdf_path.relative_to(pdf_folder)}")
