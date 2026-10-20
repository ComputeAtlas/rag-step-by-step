import json
from pathlib import Path

import numpy as np
from openai import OpenAI

from chunkers import fixed_size, fixed_size_with_overlap, recursive, by_headings
from semantic import split_into_sentences, semantic_chunks

client = OpenAI()

DOCUMENTS_FOLDER = Path("data/fernhill")


def load_documents():
    documents = []
    for path in sorted(DOCUMENTS_FOLDER.rglob("*.md")):
        if path.name == "README.md":
            continue  # the README describes the folder; it is not a document
        name = str(path.relative_to(DOCUMENTS_FOLDER))
        documents.append({"source": name, "text": path.read_text()})
    return documents


def embed(texts):
    vectors = []
    for start in range(0, len(texts), 500):  # at most 500 texts per request
        response = client.embeddings.create(model="text-embedding-3-small", input=texts[start:start + 500])
        vectors += [item.embedding for item in response.data]
    return np.array(vectors)


def by_meaning(text, max_words=200):
    sentences = split_into_sentences(text)
    return semantic_chunks(sentences, embed(sentences), max_words=max_words)


def make_chunks(documents, cut, size):
    chunks = []
    for document in documents:
        for text in cut(document["text"], size):
            chunks.append({"source": document["source"], "text": text})
    return chunks


def search(chunks, questions, question_vectors):
    """For every question: the four best chunks, and whether a right file is among them."""
    vectors = embed([chunk["text"] for chunk in chunks])
    hits = 0
    words_read = []
    for question, question_vector in zip(questions, question_vectors):
        scores = vectors @ question_vector
        best = np.argsort(-scores)[:4]  # the four highest scores
        found_files = [chunks[number]["source"] for number in best]
        if any(source in found_files for source in question["sources"]):
            hits += 1
        words_read.append(sum(len(chunks[number]["text"].split()) for number in best))
    return hits, round(np.mean(words_read))


documents = load_documents()

with open("data/fernhill-questions.json") as file:
    questions = json.load(file)
# Leave out "unanswerable" (no source file) and "whole-corpus" (needs all 44 tickets).
questions = [q for q in questions if q["category"] not in ("unanswerable", "whole-corpus")]
question_vectors = embed([q["question"] for q in questions])

print(f"A right file in the top 4, for {len(questions)} test questions\n")

print(f"{'Way to cut (up to 200 words)':30s} {'Chunks':>6s}   Hits")
ways = [
    ("fixed size", fixed_size),
    ("fixed size, 50 words overlap", fixed_size_with_overlap),
    ("recursive", recursive),
    ("by headings", by_headings),
    ("by meaning (semantic)", by_meaning),
]
for name, cut in ways:
    chunks = make_chunks(documents, cut, 200)
    hits, words = search(chunks, questions, question_vectors)
    print(f"{name:30s} {len(chunks):6d}   {hits} / {len(questions)}")

print(f"\n{'Recursive, three sizes':30s} {'Hits':>7s}   Words the model reads")
for size in [50, 200, 800]:
    chunks = make_chunks(documents, recursive, size)
    hits, words = search(chunks, questions, question_vectors)
    print(f"{'up to ' + str(size) + ' words':30s} {hits:2d} / {len(questions)}   {words}")
