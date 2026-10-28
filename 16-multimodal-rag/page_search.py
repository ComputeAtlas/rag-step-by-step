"""Search the page pictures themselves, the way ColPali does ("late interaction" over page patches).

The model is ColQwen2 (vidore/colqwen2-v1.0-hf, about 4.4 GB, downloaded the first time), an open model built on a small
vision-language model. It cuts each page picture into small squares, called patches, and gives every patch its own
list of 128 numbers. A question gets one list of numbers per word piece (token). To score a page, every question token
looks for its best-matching patch on that page; the page's score is the sum of those best matches.

Run from the repository root, after make_pages.py:  python 16-multimodal-rag/page_search.py
The first run embeds all the pages and saves them in 16-multimodal-rag/results/page-vectors.npz.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from transformers import ColQwen2ForRetrieval, ColQwen2Processor

MODEL_NAME = "vidore/colqwen2-v1.0-hf"
PAGE_FOLDER = Path("16-multimodal-rag/results/pages")
VECTOR_FILE = Path("16-multimodal-rag/results/page-vectors.npz")

device = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
model = ColQwen2ForRetrieval.from_pretrained(MODEL_NAME, dtype=torch.bfloat16).to(device).eval()
processor = ColQwen2Processor.from_pretrained(MODEL_NAME)

with open("16-multimodal-rag/results/pages.json") as file:
    pages = json.load(file)


def embed_page(path):
    """One page picture -> one row of 128 numbers for every patch of the page."""
    inputs = processor(images=[Image.open(path).convert("RGB")], return_tensors="pt").to(device)
    with torch.no_grad():
        vectors = model(**inputs).embeddings[0]
    return vectors.float().cpu().numpy()


def embed_question(question):
    """One question -> one row of 128 numbers for every token of the question."""
    inputs = processor(text=[question], return_tensors="pt").to(device)
    with torch.no_grad():
        vectors = model(**inputs).embeddings[0]
    return vectors.float().cpu().numpy()


def late_interaction_score(question_vectors, page_vectors):
    """Each question token takes its best match among the patches; add them all up."""
    # one row per question token, one column per patch
    similarities = question_vectors @ page_vectors.T
    best_match_per_token = similarities.max(axis=1)
    return float(best_match_per_token.sum())


def load_or_build_page_vectors():
    if VECTOR_FILE.exists():
        saved = np.load(VECTOR_FILE)
        return [saved[f"page{number}"] for number in range(len(pages))]
    all_vectors = []
    embed_page(PAGE_FOLDER / pages[0]["file"])      # a warm-up run, so the timing below is fair
    start = time.perf_counter()
    for page in pages:
        all_vectors.append(embed_page(PAGE_FOLDER / page["file"]))
    seconds = time.perf_counter() - start
    np.savez(VECTOR_FILE, **{f"page{number}": v for number, v in enumerate(all_vectors)})
    patches = sum(len(v) for v in all_vectors)
    print(f"Embedded {len(pages)} pages in {seconds:.0f} s ({seconds / len(pages):.2f} s a page) on {device}")
    print(f"{patches / len(pages):.0f} vectors a page on average, 128 numbers each")
    return all_vectors


page_vectors = load_or_build_page_vectors()


def search_pages(question, how_many=4):
    question_vectors = embed_question(question)
    results = []
    for number, vectors in enumerate(page_vectors):
        results.append((late_interaction_score(question_vectors, vectors), number))
    results.sort(reverse=True)
    return [(score, pages[number]) for score, number in results[:how_many]]


if __name__ == "__main__":
    question = "What torque do the clamp screws of the Ridge 500's display bracket need?"
    if len(sys.argv) > 1:
        question = sys.argv[1]
    print("Question:", question)
    print(f"Question vectors: {len(embed_question(question))} (one per token)")
    for score, page in search_pages(question):
        print(f"  {score:6.2f}  {page['file']}")
