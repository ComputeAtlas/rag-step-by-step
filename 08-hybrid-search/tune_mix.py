"""Tuning the mix: give the keyword list more (or less) say in the fusion, and measure.
Each search runs once per question; only the merge is repeated for every weight."""
import json

from searches import chunks, fuse, keyword_search, vector_search

WEIGHTS = [0.5, 1, 2, 3]  # how much the keyword list counts, next to the vector list's 1

with open("data/fernhill-questions.json") as file:
    all_questions = json.load(file)
questions = [
    q for q in all_questions
    if q["category"] not in ("unanswerable", "whole-corpus")
]


def found_right_file(q, results):
    top_files = [chunks[number]["source"] for score, number in results[:4]]
    return any(source in top_files for source in q["sources"])


def place_of(file, results):
    for place, (score, number) in enumerate(results, start=1):
        if chunks[number]["source"] == file:
            return place
    return None


both_lists = []
for q in questions:
    both_lists.append((q, vector_search(q["question"]), keyword_search(q["question"])))

hook = "What fits part FH-2291-B?"
hook_vector, hook_keyword = vector_search(hook), keyword_search(hook)

print(f"{'keyword weight':>14s} {'hit rate @ 4':>13s} {'part numbers':>13s}   battery page for '{hook}'")
for weight in WEIGHTS:
    hits = 0
    part_hits = 0
    for q, vector_results, keyword_results in both_lists:
        if found_right_file(q, fuse(vector_results, keyword_results, weight)):
            hits += 1
            if q["category"] == "part-number/error-code":
                part_hits += 1
    place = place_of("parts/batteries-and-chargers.md", fuse(hook_vector, hook_keyword, weight))
    print(f"{weight:14} {hits:8d} / {len(questions)} {part_hits:9d} / 15   place {place}")
