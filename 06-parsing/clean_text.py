"""Clean the text a simple parser got from a PDF: drop the running header and the page numbers, join words that a
line break cut in two, and turn ligatures (one character for "fi") back into plain letters.

Run from the repository root:  python 06-parsing/clean_text.py
"""
import re
import unicodedata
from pathlib import Path

from pypdf import PdfReader

PDF = Path(__file__).parent / "pdfs" / "store-locations.pdf"


def clean_text(pages):
    # The running header: the line that starts (almost) every page
    first_lines = [page.splitlines()[0] for page in pages]
    header = max(first_lines, key=first_lines.count)
    text = "\n".join(pages)
    text = text.replace(header + "\n", "")
    text = re.sub(r"Page \d+ of \d+\n?", "", text)
    # "docu-" at a line end + "ment" on the next line -> "document"
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    # One character for "fi" -> the two plain letters "f" and "i"
    text = unicodedata.normalize("NFKC", text)
    return text


def show(text, first, last):
    """Print the lines from the one containing `first` to the one containing `last`."""
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if first in line)
    end = next(i for i, line in enumerate(lines) if last in line and i >= start)
    print("\n".join(lines[start:end + 1]))


pages = [page.extract_text() for page in PdfReader(PDF).pages]
before = "\n".join(pages)
after = clean_text(pages)

print("BEFORE:", len(before.split()), "words")
show(before, "(the levels", "Dealer Town")
print()
print("AFTER:", len(after.split()), "words")
show(after, "(the levels", "Dealer Town")
