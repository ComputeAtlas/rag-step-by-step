# 06 · Getting text out of PDFs

Fernhill's documents are Markdown files, but real companies ship manuals, parts lists and policies as PDFs. These
programs turn 33 of Fernhill's documents into real PDFs (and scanned copies), read them with three parsers, and measure
whether the parser changes the score on the 15 table questions of `data/fernhill-questions.json`.

- `make_pdfs.py` prints the manuals, parts lists, policies, the store guide and the warranty policy to PDF with Google
  Chrome (a header and page numbers on every page, two columns, tables): 33 PDFs, 69 pages, in `06-parsing/pdfs/`.
- `make_scans.py` makes a "scanned" copy of every PDF: each page becomes a slightly tilted, grainy picture with no text
  inside (`06-parsing/scans/`).
- `three_parsers.py` reads page one of the store guide with **pypdf**, **pdfplumber** and **pymupdf4llm** (layout-aware)
  and prints what each one gets. Run it with `pdfs` or `scans`.
- `parse_pdfs.py` reads every PDF with one parser and saves the text in `06-parsing/parsed/<folder>-<parser>/`.
- `build_index.py` builds the same index as the first RAG (200-word chunks, `text-embedding-3-small`), with the published
  documents read from the parser's text. Only the parser changes.
- `score_tables.py` scores an index on the 15 table questions: was the right file in the top 4, and was the answer right
  (graded by `gpt-5.4-mini` with the same prompt as the baseline scoreboard)?
- `ask.py` asks one question against one index and prints the chunks it found and the answer.
- `clean_text.py` removes the page header, the page numbers, words split by a hyphen and ligatures from pypdf's text.

```bash
python 06-parsing/make_pdfs.py
python 06-parsing/make_scans.py
python 06-parsing/three_parsers.py pdfs
python 06-parsing/three_parsers.py scans
python 06-parsing/parse_pdfs.py pdfplumber pdfs          # also: pypdf pdfs, pymupdf4llm pdfs, pypdf scans, pymupdf4llm scans
python 06-parsing/build_index.py pdfs-pdfplumber         # or markdown, pdfs-pypdf, scans-pymupdf4llm, ...
python 06-parsing/score_tables.py pdfs-pdfplumber
python 06-parsing/ask.py pdfs-pdfplumber "What is the telephone number of the Wexcombe Service Centre?"
python 06-parsing/clean_text.py
```

Right answers on the 15 table questions: clean Markdown 12, pypdf 12, pdfplumber 12, pymupdf4llm 11; on the scanned
copies, pypdf 2 (no text at all) and pymupdf4llm with OCR 10.

Packages: `pypdf`, `pdfplumber`, `pymupdf4llm` (it installs PyMuPDF and its layout model), `markdown` (for
`make_pdfs.py`), `pillow`. OCR of scanned pages needs **Tesseract** installed on your computer (macOS: `brew install
tesseract`; Ubuntu: `sudo apt install tesseract-ocr`); pymupdf4llm uses it for pages that have no text. `make_pdfs.py`
needs Google Chrome; change `CHROME` at the top of the file on Windows or Linux.
