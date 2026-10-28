"""Search pictures and words in ONE shared space, with CLIP.

CLIP (OpenAI, 2021) is two embedding models trained together on hundreds of millions of pictures with their captions,
so that a picture and a sentence that describes it end up close together. Here every page picture gets one list of
512 numbers from CLIP's picture side, and the question gets one from its text side. Then it is an ordinary vector
search: the closest pages win.

The model is clip-ViT-B-32 from sentence-transformers (about 600 MB, downloaded the first time).
Run from the repository root, after make_pages.py:  python 16-multimodal-rag/clip_search.py
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image
from sentence_transformers import SentenceTransformer

PAGE_FOLDER = Path("16-multimodal-rag/results/pages")
clip = SentenceTransformer("clip-ViT-B-32")

with open("16-multimodal-rag/results/pages.json") as file:
    pages = json.load(file)

pictures = [Image.open(PAGE_FOLDER / page["file"]).convert("RGB") for page in pages]
clip.encode(pictures[:4])                       # a warm-up run, so the timing below is fair
start = time.perf_counter()
page_vectors = clip.encode(pictures, normalize_embeddings=True)
seconds = time.perf_counter() - start


def search_pages(question, how_many=4):
    question_vector = clip.encode(question, normalize_embeddings=True)
    scores = page_vectors @ question_vector
    best = np.argsort(-scores)[:how_many]
    return [(float(scores[number]), pages[number]) for number in best]


if __name__ == "__main__":
    print(f"Embedded {len(pages)} pages in {seconds:.1f} s ({1000 * seconds / len(pages):.0f} ms a page),"
          f" {page_vectors.shape[1]} numbers a page")
    questions = ["What torque do the clamp screws of the Ridge 500's display bracket need?",
                 "a line chart", "a drawing of a bicycle wheel"]
    if len(sys.argv) > 1:
        questions = sys.argv[1:]
    for question in questions:
        print("\nQuestion:", question)
        for score, page in search_pages(question):
            print(f"  {score:.3f}  {page['file']}")
