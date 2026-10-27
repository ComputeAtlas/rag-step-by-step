"""The retrieval scoreboard on the 80 single-search test questions (as in the baseline):
vector search, hybrid search, and hybrid search followed by the reranker.
It only searches: one embedding request per question and no chat calls.

    python 09-reranking/scoreboard.py
    python 09-reranking/scoreboard.py cross-encoder/ms-marco-MiniLM-L6-v2     # try another reranker"""
import json
import statistics
import sys
import time

import numpy as np
from sentence_transformers import CrossEncoder

import reranker
from reranker import chunks, rerank
from searches import fuse, keyword_search, vector_search

if len(sys.argv) > 1:
    reranker.reranker = CrossEncoder(sys.argv[1])  # swap in another reranker model

with open("data/fernhill-questions.json") as file:
    all_questions = json.load(file)

# Leave out "unanswerable" (no source file) and "whole-corpus" (needs all 44 tickets).
questions = [
    q for q in all_questions
    if q["category"] not in ("unanswerable", "whole-corpus")
]


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


def files(results):
    return [chunks[number]["source"] for score, number in results]


rows = []
rerank_seconds = []
for q in questions:
    vector_results = vector_search(q["question"])
    candidates = fuse(vector_results, keyword_search(q["question"]))[:30]  # the first stage
    start = time.perf_counter()
    reranked = rerank(q["question"], candidates)  # the second stage
    rerank_seconds.append(time.perf_counter() - start)
    rows.append({
        "category": q["category"],
        "vector": score_retrieval(q["sources"], files(vector_results[:4])),
        "vector + rerank": score_retrieval(q["sources"], files(rerank(q["question"], vector_results[:30]))),
        "hybrid": score_retrieval(q["sources"], files(candidates[:4])),
        "reranked": score_retrieval(q["sources"], files(reranked)),
        "all 30": score_retrieval(q["sources"], files(candidates)),
    })

print(f"Retrieval on {len(rows)} single-search questions (a right file in the chunks kept)")
print(f"  {'search':22s} {'hit rate':>14s} {'recall':>7s} {'MRR':>6s}")
for name, label in [("vector", "vector, top 4"), ("vector + rerank", "vector + rerank, top 4"),
                    ("hybrid", "hybrid, top 4"), ("reranked", "hybrid + rerank, top 4"),
                    ("all 30", "hybrid, all 30")]:
    hits = sum(r[name][0] for r in rows)
    recall = np.mean([r[name][1] for r in rows])
    mrr = np.mean([r[name][2] for r in rows])
    print(f"  {label:22s} {hits:4d} / {len(rows)} ({hits / len(rows):.2f}) {recall:6.2f} {mrr:6.2f}")

print("\nHit rate @ 4 by category")
print(f"  {'category':24s} {'n':>3s} {'vector':>7s} {'hybrid':>7s} {'reranked':>9s}")
for category in ["lookup", "part-number/error-code", "table", "multi-document", "conflicting-versions"]:
    sub = [r for r in rows if r["category"] == category]
    hits = [sum(r[name][0] for r in sub) for name in ["vector", "hybrid", "reranked"]]
    print(f"  {category:24s} {len(sub):3d} {hits[0]:7d} {hits[1]:7d} {hits[2]:9d}")

up = sum(1 for r in rows if r["reranked"][0] > r["hybrid"][0])
down = sum(1 for r in rows if r["reranked"][0] < r["hybrid"][0])
print(f"\nReranking found a right file for {up} more questions and lost {down}")
milliseconds = 1000 * statistics.median(rerank_seconds[1:])  # the first call warms the model up
print(f"Reranking 30 chunks took {milliseconds:.0f} ms per question (median)")
