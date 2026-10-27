"""The retrieval scoreboard: the same 80 test questions as the baseline (the ones a single
search can answer), searched in six ways: vector, keyword and hybrid search, each on the
plain chunks and on the chunks with their context in front. A hit = a right file among
the four best chunks. Only one embedding request (for the questions), no chat calls."""
import json

import numpy as np

from searches import embed, hybrid_search, keyword_search, load_contextual_index, load_plain_index, vector_search

with open("data/fernhill-questions.json") as file:
    all_questions = json.load(file)
# Leave out "unanswerable" (no source file) and "whole-corpus" (needs all 44 tickets).
questions = [q for q in all_questions if q["category"] not in ("unanswerable", "whole-corpus")]
question_vectors = embed([q["question"] for q in questions])

plain = load_plain_index()
contextual = load_contextual_index()


def score_retrieval(required_sources, found_files):
    """The baseline's scoring: hit, recall and reciprocal rank for one question."""
    required = set(required_sources)
    matched = required.intersection(found_files)
    hit = 1 if matched else 0
    recall = len(matched) / len(required)
    mrr = 0.0
    for rank, source in enumerate(found_files, start=1):
        if source in required:
            mrr = 1.0 / rank
            break
    return hit, recall, mrr


setups = [
    ("vector", plain, "vector"), ("keyword", plain, "keyword"), ("hybrid", plain, "hybrid"),
    ("vector + context", contextual, "vector"), ("keyword + context", contextual, "keyword"),
    ("hybrid + context", contextual, "hybrid"),
]

rows = []
for q, question_vector in zip(questions, question_vectors):
    row = {"id": q["id"], "category": q["category"], "question": q["question"]}
    for name, index, search in setups:
        if search == "vector":
            results = vector_search(index, question_vector)
        elif search == "keyword":
            results = keyword_search(index, q["question"])
        else:
            results = hybrid_search(index, q["question"], question_vector)
        found_files = [index["chunks"][number]["source"] for score, number in results[:4]]
        row[name] = score_retrieval(q["sources"], found_files)
    rows.append(row)

print(f"Retrieval @ top 4, {len(rows)} single-search questions")
print(f"  {'search':18s} {'hit rate @ 4':>14s} {'recall @ 4':>11s} {'MRR @ 4':>8s}")
for name, index, search in setups:
    hits = sum(r[name][0] for r in rows)
    recall = np.mean([r[name][1] for r in rows])
    mrr = np.mean([r[name][2] for r in rows])
    print(f"  {name:18s} {hits:4d} / {len(rows)} ({hits / len(rows):.2f}) {recall:9.2f} {mrr:9.2f}")
    if name == "hybrid":
        print()

print("\nHit rate @ 4 by category (vector -> vector + context, hybrid -> hybrid + context)")
for category in ["lookup", "part-number/error-code", "table", "multi-document", "conflicting-versions"]:
    sub = [r for r in rows if r["category"] == category]
    hits = {name: sum(r[name][0] for r in sub) for name, index, search in setups}
    print(f"  {category:24s} {len(sub):3d}   {hits['vector']:3d} -> {hits['vector + context']:3d}"
          f"   {hits['hybrid']:3d} -> {hits['hybrid + context']:3d}")

for before, after in [("vector", "vector + context"), ("hybrid", "hybrid + context")]:
    gained = [r["id"] for r in rows if r[after][0] and not r[before][0]]
    lost = [r["id"] for r in rows if r[before][0] and not r[after][0]]
    print(f"\n{before} -> {after}: found now {len(gained)} {gained}, lost {len(lost)} {lost}")
