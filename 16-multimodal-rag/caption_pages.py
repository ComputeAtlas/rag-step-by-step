"""Turn every page picture into text with a vision-language model, so the usual text search can find it.

For each page, gpt-5.4-mini copies out every word, table and number, and describes any drawing or chart together with
every label and value on it. The text is saved in 16-multimodal-rag/results/captions.json, with what each page cost.
72 pictures, 72 chat calls. Run from the repository root, after make_pages.py:
    python 16-multimodal-rag/caption_pages.py
"""
import json
import time
from pathlib import Path

from vision import CAPTION_PROMPT, ask_with_pictures

PAGE_FOLDER = Path("16-multimodal-rag/results/pages")

with open("16-multimodal-rag/results/pages.json") as file:
    pages = json.load(file)

captions = []
start = time.perf_counter()
for page in pages:
    text, cost = ask_with_pictures(CAPTION_PROMPT, [PAGE_FOLDER / page["file"]])
    captions.append({**page, "text": text, **cost})
    print(f"{page['file']:55s} {cost['input_tokens']:5d} in {cost['output_tokens']:5d} out  ${cost['dollars']:.4f}")
seconds = time.perf_counter() - start

with open("16-multimodal-rag/results/captions.json", "w") as file:
    json.dump(captions, file, indent=1)

dollars = sum(c["dollars"] for c in captions)
words = sum(len(c["text"].split()) for c in captions)
print(f"\n{len(captions)} pages in {seconds / 60:.1f} minutes, {words} words of text")
print(f"Cost: ${dollars:.2f} in all, ${dollars / len(captions):.4f} a page")
