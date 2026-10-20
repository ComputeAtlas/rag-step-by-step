"""The retrieval scoreboard for vector, keyword and hybrid search, on the same 80 test questions
as the baseline (the ones a single search can answer). It only searches: one embedding request per
question and no chat calls."""
import json

import numpy as np

from searches import chunks, fuse, keyword_search, vector_search

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


def top_files(results, how_many=4):
    return [chunks[number]["source"] for score, number in results[:how_many]]


rows = []
for q in questions:
    vector_results = vector_search(q["question"])
    keyword_results = keyword_search(q["question"])
    hybrid_results = fuse(vector_results, keyword_results)
    row = {"id": q["id"], "category": q["category"], "question": q["question"]}
    for name, results in [("vector", vector_results), ("keyword", keyword_results), ("hybrid", hybrid_results)]:
        row[name] = score_retrieval(q["sources"], top_files(results))
    rows.append(row)

searches = ["vector", "keyword", "hybrid"]


def report(title, subset):
    n = len(subset)
    print(title)
    print(f"  {'search':9s} {'hit rate @ 4':>14s} {'recall @ 4':>11s} {'MRR @ 4':>8s}")
    for name in searches:
        hits = sum(r[name][0] for r in subset)
        recall = np.mean([r[name][1] for r in subset])
        mrr = np.mean([r[name][2] for r in subset])
        print(f"  {name:9s} {hits:4d} / {n:2d} ({hits / n:.2f}) {recall:9.2f} {mrr:9.2f}")
    print()


report(f"Retrieval @ top 4, {len(rows)} single-search questions", rows)
part_rows = [r for r in rows if r["category"] == "part-number/error-code"]
report("Part numbers and error codes", part_rows)
report("  ...with a part number in the question (FH-...)", [r for r in part_rows if "FH-" in r["question"]])
report("  ...without one (mostly error codes)", [r for r in part_rows if "FH-" not in r["question"]])

print("Hit rate @ 4 by category")
print(f"  {'category':24s} {'n':>3s} {'vector':>7s} {'keyword':>8s} {'hybrid':>7s}")
for category in ["lookup", "part-number/error-code", "table", "multi-document", "conflicting-versions"]:
    sub = [r for r in rows if r["category"] == category]
    hits = [sum(r[name][0] for r in sub) for name in searches]
    print(f"  {category:24s} {len(sub):3d} {hits[0]:7d} {hits[1]:8d} {hits[2]:7d}")

both = sum(1 for r in rows if r["vector"][0] and r["keyword"][0])
vector_only = sum(1 for r in rows if r["vector"][0] and not r["keyword"][0])
keyword_only = sum(1 for r in rows if r["keyword"][0] and not r["vector"][0])
neither = len(rows) - both - vector_only - keyword_only
found_by_one = [r for r in rows if r["vector"][0] or r["keyword"][0]]
print("\nWhich search found a right file in its top 4?")
print(f"  both: {both}   vector only: {vector_only}   keyword only: {keyword_only}   neither: {neither}")
print(f"  hybrid found {sum(r['hybrid'][0] for r in found_by_one)} of the {len(found_by_one)} that either one found")
