"""Search the page pictures with ColQwen2, then let the vision-language model read the best four pages and answer.

Run from the repository root, after page_search.py has embedded the pages:  python 16-multimodal-rag/ask_pages.py
"""
import sys
from pathlib import Path

from page_search import search_pages
from vision import answer_from_pictures

PAGE_FOLDER = Path("16-multimodal-rag/results/pages")

question = "What torque do the clamp screws of the Ridge 500's display bracket need?"
if len(sys.argv) > 1:
    question = sys.argv[1]

found = search_pages(question)
print("Question:", question)
print("Pages found:")
for score, page in found:
    print(f"  {score:6.2f}  {page['file']}")
answer, cost = answer_from_pictures(question, [PAGE_FOLDER / page["file"] for score, page in found])
print("Answer:", answer)
print(f"Tokens: {cost['input_tokens']} in, {cost['output_tokens']} out  (${cost['dollars']:.4f})")
