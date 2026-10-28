"""Find the sections that answer a question.

1. Hybrid search over the small pieces: a meaning search (embeddings) and a keyword search
   (BM25), merged with Reciprocal Rank Fusion. Keywords catch exact codes like FH-2291-B;
   meaning catches "flat tyre" for "puncture".
2. Small-to-big: walk down the merged list and hand over the whole section around each piece,
   until we have four different sections.

The index is the one ingest.py saved."""
import json
import re
from pathlib import Path

import numpy as np
from openai import OpenAI
from rank_bm25 import BM25Okapi

client = OpenAI()
EMBEDDING_MODEL = "text-embedding-3-small"
INDEX_FOLDER = Path(__file__).parent / "results" / "index"

with open(INDEX_FOLDER / "sections.json") as file:
    sections = json.load(file)
with open(INDEX_FOLDER / "pieces.json") as file:
    pieces = json.load(file)
vectors = np.load(INDEX_FOLDER / "vectors.npy")

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


bm25 = BM25Okapi([words(piece["text"]) for piece in pieces])


def vector_search(question, how_many=50):
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=question)
    question_vector = np.array(response.data[0].embedding)
    scores = vectors @ question_vector  # one similarity score per piece
    best = scores.argsort()[::-1][:how_many]  # highest score first
    return [int(number) for number in best]


def keyword_search(question, how_many=50):
    scores = bm25.get_scores(words(question))  # one BM25 score per piece
    best = scores.argsort()[::-1][:how_many]
    return [int(number) for number in best]


def fuse(vector_results, keyword_results, k=60):
    """Reciprocal Rank Fusion: each list gives a piece 1 / (k + its place)."""
    points = {}  # only the places count, never the scores
    for place, number in enumerate(vector_results, start=1):
        points[number] = points.get(number, 0) + 1 / (k + place)
    for place, number in enumerate(keyword_results, start=1):
        points[number] = points.get(number, 0) + 1 / (k + place)
    return sorted(points, key=points.get, reverse=True)  # most points first


def find_sections(question, how_many=4):
    """The four best sections for a question: search small, read big."""
    found = []
    for piece_number in fuse(vector_search(question), keyword_search(question)):
        section_number = pieces[piece_number]["section"]
        if section_number not in found:  # two pieces of one section: hand it over once
            found.append(section_number)
        if len(found) == how_many:
            break
    return [dict(sections[n], number=n) for n in found]
