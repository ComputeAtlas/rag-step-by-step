"""Read the same PDF page with three different parsers and print what each one gets.

Run from the repository root:  python 06-parsing/three_parsers.py pdfs
                       or, for the scanned copy:  python 06-parsing/three_parsers.py scans
"""
import sys
from pathlib import Path

import pdfplumber
import pymupdf4llm
from pypdf import PdfReader

folder_name = sys.argv[1]
PDF = Path(__file__).parent / folder_name / "store-locations.pdf"
PAGE = 1  # the page with the table of stores


def read_with_pypdf(path, page_number):
    reader = PdfReader(path)
    return reader.pages[page_number - 1].extract_text()


def read_with_pdfplumber(path, page_number):
    with pdfplumber.open(path) as pdf:
        return pdf.pages[page_number - 1].extract_text()


def read_with_pymupdf4llm(path, page_number):
    # Layout-aware: Markdown out, without the page header and footer
    return pymupdf4llm.to_markdown(str(path), pages=[page_number - 1],
                                   header=False, footer=False)


for name, read in [("pypdf", read_with_pypdf),
                   ("pdfplumber", read_with_pdfplumber),
                   ("pymupdf4llm", read_with_pymupdf4llm)]:
    print(f"===== {name} =====")
    print(read(PDF, PAGE))
    print()
