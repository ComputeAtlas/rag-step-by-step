import json
import sys
from pathlib import Path

import numpy as np

INDEX_FOLDER = Path(__file__).parent / "index"
# The baseline by default; pass another file (made by save_results.py) to score a new run.
results_name = sys.argv[1] if len(sys.argv) > 1 else "results.json"
RESULTS_FILE = INDEX_FOLDER / results_name

with open(RESULTS_FILE) as file:
    results = json.load(file)

single = [r for r in results if r["category"] not in ("whole-corpus", "unanswerable")]

print("Fernhill RAG Baseline Scoreboard (200-word chunks, top-4 cosine search)\n")
print(f"{'Category':24s} {'N':>4s} {'Hit@4':>7s} {'Recall@4':>9s} {'MRR@4':>7s} {'Faithful':>9s} {'Correct':>9s}")
print("-" * 75)

for category in [
    "lookup",
    "part-number/error-code",
    "table",
    "multi-document",
    "conflicting-versions",
    "whole-corpus",
    "unanswerable",
]:
    sub = [r for r in results if r["category"] == category]
    n = len(sub)
    if category == "unanswerable":
        hit_s, rec_s, mrr_s = "    —", "       —", "    —"
    else:
        hit_s = f"{np.mean([r['hit'] for r in sub]):7.2f}"
        rec_s = f"{np.mean([r['recall'] for r in sub]):9.2f}"
        mrr_s = f"{np.mean([r['mrr'] for r in sub]):7.2f}"
    faith_s = f"{np.mean([r['faithful'] for r in sub]):9.2f}"
    corr_s = f"{np.mean([r['correct'] for r in sub]):9.2f}"
    print(f"{category:24s} {n:4d} {hit_s} {rec_s} {mrr_s} {faith_s} {corr_s}")

print("-" * 75)
print(
    f"{'Single-search (80)':24s} {len(single):4d} "
    f"{np.mean([r['hit'] for r in single]):7.2f} "
    f"{np.mean([r['recall'] for r in single]):9.2f} "
    f"{np.mean([r['mrr'] for r in single]):7.2f} "
    f"{np.mean([r['faithful'] for r in single]):9.2f} "
    f"{np.mean([r['correct'] for r in single]):9.2f}"
)
print(
    f"{'All questions (100)':24s} {len(results):4d} "
    f"{'    —':>7s} {'       —':>9s} {'    —':>7s} "
    f"{np.mean([r['faithful'] for r in results]):9.2f} "
    f"{np.mean([r['correct'] for r in results]):9.2f}"
)

misses = [r for r in single if not r["correct"]]
no_file = [r for r in misses if r["hit"] == 0]
partial_files = [r for r in misses if r["hit"] == 1 and r["recall"] < 1.0]
all_files_missed_ans = [r for r in misses if r["recall"] == 1.0]

print(f"\nWhere the {len(misses)} single-search failures come from:")
print(f"  1. Right file never retrieved (hit = 0)          : {len(no_file):2d}")
print(f"  2. Only some required files retrieved (recall<1) : {len(partial_files):2d}")
print(f"  3. Right file(s) retrieved, answer still wrong   : {len(all_files_missed_ans):2d}  (wrong chunk or missed by generator)")
