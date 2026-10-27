"""How many candidates should the first stage hand to the reranker?
Each search runs once per question; only the reranking is repeated."""
import json
import statistics
import time

from reranker import chunks, first_stage, rerank

HOW_MANY = [4, 10, 20, 30, 50]  # candidates given to the reranker

with open("data/fernhill-questions.json") as file:
    all_questions = json.load(file)
questions = [
    q for q in all_questions
    if q["category"] not in ("unanswerable", "whole-corpus")
]


def found_right_file(q, results):
    top_files = [chunks[number]["source"] for score, number in results[:4]]
    return any(source in top_files for source in q["sources"])


lists = []
for q in questions:
    lists.append((q, first_stage(q["question"], how_many=50)))

rerank(questions[0]["question"], lists[0][1])  # warm the model up once

print(f"{'candidates':>10s} {'hit rate @ 4':>13s} {'ms per question':>16s}")
for how_many in HOW_MANY:
    hits = 0
    seconds = []
    for q, candidates in lists:
        start = time.perf_counter()
        results = rerank(q["question"], candidates[:how_many])
        seconds.append(time.perf_counter() - start)
        if found_right_file(q, results):
            hits += 1
    milliseconds = 1000 * statistics.median(seconds)
    print(f"{how_many:10d} {hits:8d} / {len(questions)} {milliseconds:12.0f}")
