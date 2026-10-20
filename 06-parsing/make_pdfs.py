"""Turn Fernhill's published documents into PDF files, laid out like a real company's manuals.

The Fernhill documents are written in Markdown, but a real company ships its manuals, parts lists and policies as
PDFs: a header and a footer on every page, text in two columns, tables. This script makes those PDFs, so the
parsers in this folder have something real to read. It uses Google Chrome to print each page to PDF.

Run it once from the repository root:  python 06-parsing/make_pdfs.py
"""
import subprocess
import tempfile
from pathlib import Path

import markdown

DOCUMENTS_FOLDER = Path("data/fernhill")
PDF_FOLDER = Path(__file__).parent / "pdfs"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"  # change this on Windows or Linux

# The documents a company prints and ships as PDFs. Support tickets, release notes, the FAQ and the company page stay
# as they are: those live on a help desk or a web site.
PUBLISHED = ["manuals", "parts", "policies", "store-locations.md", "warranty-policy.md"]

PAGE_STYLE = """
@page {
  size: A4;
  margin: 24mm 16mm 20mm 16mm;
  @top-left { content: "HEADER_TEXT"; font: 8.5pt Helvetica, Arial, sans-serif; color: #555; }
  @top-right { content: "Fernhill Bikes Ltd"; font: 8.5pt Helvetica, Arial, sans-serif; color: #555; }
  @bottom-center { content: "Page " counter(page) " of " counter(pages); font: 8.5pt Helvetica, Arial, sans-serif; color: #555; }
}
body { font: 9.5pt/1.35 Georgia, "Times New Roman", serif; color: #111; margin: 0; }
h1 { font: bold 20pt Helvetica, Arial, sans-serif; margin: 0 0 4mm 0; column-span: all; }
h2 { font: bold 12.5pt Helvetica, Arial, sans-serif; margin: 4mm 0 2mm 0; break-after: avoid; }
h3 { font: bold 10pt Helvetica, Arial, sans-serif; margin: 3mm 0 1.5mm 0; break-after: avoid; }
p, li { margin: 0 0 2mm 0; text-align: justify; hyphens: auto; }
.columns { column-count: 2; column-gap: 8mm; }
table { border-collapse: collapse; width: 100%; break-inside: avoid; margin: 1mm 0 3mm 0; font: 8.5pt/1.3 Helvetica, Arial, sans-serif; }
table.wide { column-span: all; }
th { background: #e6e6e6; text-align: left; }
th, td { border: 0.5pt solid #999; padding: 1.2mm 1.6mm; vertical-align: top; }
code { font: 8.5pt Courier, monospace; }
"""


def find_published_documents():
    paths = []
    for name in PUBLISHED:
        path = DOCUMENTS_FOLDER / name
        if path.is_dir():
            paths.extend(sorted(path.glob("*.md")))
        else:
            paths.append(path)
    return paths


def markdown_to_html(text):
    title = text.splitlines()[0].lstrip("# ").strip()
    body = markdown.markdown(text, extensions=["tables"])
    # Narrow tables (two columns) sit inside a text column; wider ones span the whole page.
    parts = body.split("<table>")
    html = parts[0]
    for part in parts[1:]:
        header_row = part.split("</tr>")[0]
        if header_row.count("</th>") > 2:
            html += '<table class="wide">' + part
        else:
            html += "<table>" + part
    style = PAGE_STYLE.replace("HEADER_TEXT", title.replace('"', "'"))
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><style>{style}</style></head>' \
           f'<body><div class="columns">{html}</div></body></html>'


def print_to_pdf(html, pdf_path):
    with tempfile.TemporaryDirectory() as folder:
        html_path = Path(folder) / "page.html"
        html_path.write_text(html)
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf_path.resolve()}", html_path.as_uri()],
                       check=True, capture_output=True)


for path in find_published_documents():
    pdf_path = PDF_FOLDER / path.relative_to(DOCUMENTS_FOLDER).with_suffix(".pdf")
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    print_to_pdf(markdown_to_html(path.read_text()), pdf_path)
    print("Made", pdf_path.relative_to(PDF_FOLDER))
