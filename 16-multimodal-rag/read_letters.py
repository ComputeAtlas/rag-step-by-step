"""Read the letters of a figure with OCR (Tesseract), the way the parsing lesson read scanned pages.

OCR finds the letters and numbers in a picture and types them out. It does not see the drawing: which arrow points
where, which line a value sits on. Needs Tesseract installed (macOS: brew install tesseract).
Run from the repository root:  python 16-multimodal-rag/read_letters.py
"""
import subprocess
import sys
from pathlib import Path

figure = "16-multimodal-rag/figures/battery-capacity.png"
if len(sys.argv) > 1:
    figure = sys.argv[1]

result = subprocess.run(["tesseract", figure, "-"], capture_output=True, text=True)
print("Figure:", Path(figure).name)
print("What OCR read:")
for line in result.stdout.splitlines():
    if line.strip():
        print("  " + line.strip())
