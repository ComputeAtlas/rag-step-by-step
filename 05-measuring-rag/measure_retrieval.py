import json
from pathlib import Path

import numpy as np
from openai import OpenAI

client = OpenAI()

INDEX_FOLDER = Path(__file__).parent / "index"  # made by build_index.py

with open(INDEX_FOLDER / "chunks.json") as file:
    chunks = json.load(file)
vectors = np.load(INDEX_FOLDER / "vectors.npy")

with open("data/fernhill-questions.json") as file:
    all_questions = json.load(file)

# Leave out "unanswerable" (no source file) and "whole-corpus" (needs all 44 tickets).
questions = [
    q for q in all_questions
    if q["category"] not in ("unanswerable", "whole-corpus")
]


def find_best_files(question_vector, how_many=4):
    results = []
    for number, vector in enumerate(vectors):
        score = float(np.dot(question_vector, vector))
        results.append((score, number))
    results.sort(reverse=True)
    return [chunks[number]["source"] for score, number in results[:how_many]]


def score_retrieval(required_sources, found_files):
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


response = client.embeddings.create(
    model="text-embedding-3-small",
    input=[q["question"] for q in questions],
)

rows = []
for q, item in zip(questions, response.data):
    found_files = find_best_files(np.array(item.embedding))
    hit, recall, mrr = score_retrieval(q["sources"], found_files)
    rows.append({**q, "found": found_files, "hit": hit, "recall": recall, "mrr": mrr})

print(f"Retrieval @ top 4 across {len(rows)} single-search questions:\n")
print(f"  Hit rate @ 4 : {sum(r['hit'] for r in rows):2d} / {len(rows)}  ({np.mean([r['hit'] for r in rows]):.2f})")
print(f"  Recall @ 4   : {np.mean([r['recall'] for r in rows]):.2f}  (all sources found: {sum(r['recall'] == 1.0 for r in rows)} / {len(rows)})")
print(f"  MRR @ 4      : {np.mean([r['mrr'] for r in rows]):.2f}\n")

print(f"{'Category':24s} {'Questions':>9s} {'Hit@4':>8s} {'Recall@4':>9s} {'MRR@4':>7s}")
print("-" * 61)
for category in ["lookup", "part-number/error-code", "table", "multi-document", "conflicting-versions"]:
    sub = [r for r in rows if r["category"] == category]
    n = len(sub)
    print(
        f"{category:24s} {n:9d} "
        f"{np.mean([r['hit'] for r in sub]):8.2f} "
        f"{np.mean([r['recall'] for r in sub]):9.2f} "
        f"{np.mean([r['mrr'] for r in sub]):7.2f}"
    )

example = next(r for r in rows if r["id"] == "q064")
print(f"\nExample of partial retrieval ({example['id']}):")
print(f"  Question : {example['question']}")
print(f"  Required : {example['sources']}")
print(f"  Top 4    : {example['found']}")
print(f"  Scores   : hit={example['hit']}  recall={example['recall']:.2f}  mrr={example['mrr']:.2f}")
