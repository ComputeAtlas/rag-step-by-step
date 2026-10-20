"""Three ways to search the same 288 Fernhill chunks:

- vector search: the closest meaning (embeddings, as in the baseline);
- keyword search: the exact words (BM25);
- hybrid search: both lists, merged with Reciprocal Rank Fusion.

Each search returns a list of (score, chunk number) pairs, best first.
The chunks and their vectors are the baseline index made by 05-measuring-rag/build_index.py."""
import json
import re
from pathlib import Path

import numpy as np
from openai import OpenAI
from rank_bm25 import BM25Okapi

client = OpenAI()

INDEX_FOLDER = Path("05-measuring-rag/index")  # the baseline index (run from the repository root)
with open(INDEX_FOLDER / "chunks.json") as file:
    chunks = json.load(file)
vectors = np.load(INDEX_FOLDER / "vectors.npy")


def vector_search(question, how_many=50):
    response = client.embeddings.create(model="text-embedding-3-small", input=question)
    question_vector = np.array(response.data[0].embedding)
    results = []
    for number, vector in enumerate(vectors):
        score = float(np.dot(question_vector, vector))
        results.append((score, number))
    results.sort(reverse=True)  # highest score first
    return results[:how_many]


# Small words that tell a keyword search nothing.
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "did", "do", "does", "for", "from",
    "has", "have", "how", "i", "in", "is", "it", "its", "my", "of", "on", "or", "that", "the",
    "this", "to", "was", "were", "what", "when", "where", "which", "who", "why", "will", "with",
    "you", "your",
}


def words(text):
    found = re.findall(r"[a-z0-9-]+", text.lower())  # keeps fh-2291-b in one piece
    return [word for word in found if word not in STOP_WORDS]


bm25 = BM25Okapi([words(chunk["text"]) for chunk in chunks])


def keyword_search(question, how_many=50):
    scores = bm25.get_scores(words(question))  # one BM25 score per chunk
    results = []
    for number, score in enumerate(scores):
        results.append((float(score), number))
    results.sort(reverse=True)  # highest score first
    return results[:how_many]


def fuse(vector_results, keyword_results, keyword_weight=1, k=60):
    """Reciprocal Rank Fusion: each list gives a chunk 1 / (k + its place)."""
    points = {}  # only the places count, never the scores
    for place, (score, number) in enumerate(vector_results, start=1):
        points[number] = points.get(number, 0) + 1 / (k + place)
    for place, (score, number) in enumerate(keyword_results, start=1):
        points[number] = points.get(number, 0) + keyword_weight / (k + place)
    results = []
    for number, total in points.items():
        results.append((total, number))
    results.sort(reverse=True)  # most points first
    return results


def hybrid_search(question, keyword_weight=1):
    return fuse(vector_search(question), keyword_search(question), keyword_weight)
