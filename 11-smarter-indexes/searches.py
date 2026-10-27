"""The three searches of the hybrid-search lesson (vector, keyword with BM25, and the two
merged with Reciprocal Rank Fusion), written so they work on any index:

- the plain index: the baseline's 288 chunks (05-measuring-rag/build_index.py);
- the contextual index: the same chunks with their context in front (add_context.py).

Each search returns a list of (score, chunk number) pairs, best first."""
import json
import re
from pathlib import Path

import numpy as np
from openai import OpenAI
from rank_bm25 import BM25Okapi

client = OpenAI()


def embed(texts):
    vectors = []
    for start in range(0, len(texts), 500):  # at most 500 texts per request
        response = client.embeddings.create(model="text-embedding-3-small", input=texts[start:start + 500])
        vectors += [item.embedding for item in response.data]
    return np.array(vectors)


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


def load_plain_index():
    folder = Path("05-measuring-rag/index")
    with open(folder / "chunks.json") as file:
        chunks = json.load(file)
    texts = [chunk["text"] for chunk in chunks]
    return {"chunks": chunks, "vectors": np.load(folder / "vectors.npy"),
            "bm25": BM25Okapi([words(text) for text in texts])}


def load_contextual_index():
    folder = Path("11-smarter-indexes/results")
    with open(folder / "contextual-chunks.json") as file:
        chunks = json.load(file)
    texts = [chunk["context"] + "\n\n" + chunk["text"] for chunk in chunks]  # context in front
    return {"chunks": chunks, "vectors": np.load(folder / "contextual-vectors.npy"),
            "bm25": BM25Okapi([words(text) for text in texts])}


def vector_search(index, question_vector, how_many=50):
    scores = index["vectors"] @ question_vector  # one similarity score per chunk
    results = [(float(score), number) for number, score in enumerate(scores)]
    results.sort(reverse=True)  # highest score first
    return results[:how_many]


def keyword_search(index, question, how_many=50):
    scores = index["bm25"].get_scores(words(question))  # one BM25 score per chunk
    results = [(float(score), number) for number, score in enumerate(scores)]
    results.sort(reverse=True)  # highest score first
    return results[:how_many]


def fuse(vector_results, keyword_results, k=60):
    """Reciprocal Rank Fusion: each list gives a chunk 1 / (k + its place)."""
    points = {}
    for results in [vector_results, keyword_results]:
        for place, (score, number) in enumerate(results, start=1):
            points[number] = points.get(number, 0) + 1 / (k + place)
    fused = [(total, number) for number, total in points.items()]
    fused.sort(reverse=True)  # most points first
    return fused


def hybrid_search(index, question, question_vector):
    return fuse(vector_search(index, question_vector), keyword_search(index, question))
