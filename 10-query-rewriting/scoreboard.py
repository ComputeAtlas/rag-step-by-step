"""The retrieval scoreboard for every way of asking, from the rewrites saved by make_rewrites.py.
No chat calls here, only embeddings (one per text we search with).

1. The 20 follow-up questions: the last message alone, the whole chat glued on, the rewrite.
2. The 20 questions in a customer's own words: as asked, rewritten, many ways, an imagined answer.
3. The 80 single-search test questions: hybrid search as it is, then four ways to change
   the question first: many ways to ask, an imagined answer, sub-questions, routing.

The four chunks each one finds are saved in 10-query-rewriting/results/found.json."""
import json
import statistics
from pathlib import Path

import numpy as np

from searching import chunks, fuse, fuse_lists, in_sections, keyword_search, section_of, top_files, vector_search

RESULTS = Path(__file__).parent / "results"
with open(RESULTS / "rewrites.json") as file:
    rewrites = json.load(file)
with open("data/fernhill-questions.json") as file:
    golden = {q["id"]: q for q in json.load(file)}
with open(Path(__file__).parent / "follow_up_questions.json") as file:
    follow_ups = json.load(file)
with open(Path(__file__).parent / "own_words_questions.json") as file:
    own_words = json.load(file)
questions = [q for q in golden.values() if q["category"] not in ("unanswerable", "whole-corpus")]

remembered = {}  # each text is embedded once, even if we search with it twice


def vector_once(text):
    """Every chunk ranked by meaning (all 288 of them)."""
    if text not in remembered:
        remembered[text] = vector_search(text, how_many=len(chunks))
    return remembered[text]


def search(text):
    """Hybrid search, as built for keywords and vectors: the top 50 of each, merged by places."""
    return fuse(vector_once(text)[:50], keyword_search(text))


def score_retrieval(required_sources, found_files):
    """Hit, recall and reciprocal rank for one question (the baseline's scoring)."""
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


def report(title, rows, names):
    n = len(rows)
    print(title)
    print(f"  {'way of asking':22s} {'hit rate @ 4':>14s} {'recall @ 4':>11s} {'MRR @ 4':>8s}")
    for name in names:
        hits = sum(r[name][0] for r in rows)
        recall = np.mean([r[name][1] for r in rows])
        mrr = np.mean([r[name][2] for r in rows])
        print(f"  {name:22s} {hits:4d} / {n:2d} ({hits / n:.2f}) {recall:9.2f} {mrr:9.2f}")
    print()


found = {}

# 1. Follow-up questions
rows = []
for f in follow_ups:
    sources = golden[f["same_as"]]["sources"]
    whole_chat = " ".join(turn["text"] for turn in f["chat"]) + " " + f["message"]
    ways = {
        "last message only": search(f["message"]),
        "whole chat glued on": search(whole_chat),
        "rewritten": search(rewrites["follow_ups"][f["id"]]["rewritten"]),
        "asked in full": search(golden[f["same_as"]]["question"]),  # the test's own wording
    }
    row = {}
    for name, results in ways.items():
        row[name] = score_retrieval(sources, top_files(results))
        found.setdefault(name, {})[f["id"]] = [number for score, number in results[:4]]
    rows.append(row)
report("Follow-up questions (20 chats)", rows,
       ["last message only", "whole chat glued on", "rewritten", "asked in full"])

# 2. Questions in a customer's own words
names = ["as asked", "rewritten", "many ways to ask", "imagined answer", "asked in full"]
rows = []
for o in own_words:
    saved = rewrites["own_words"][o["id"]]
    as_asked = search(o["question"])
    ways = {
        "as asked": as_asked,
        "rewritten": search(saved["rewritten"]),
        "many ways to ask": fuse_lists([as_asked] + [search(other) for other in saved["many_ways"]]),
        "imagined answer": fuse(vector_once(saved["imagined"])[:50], keyword_search(o["question"])),
        "asked in full": search(golden[o["same_as"]]["question"]),
    }
    row = {}
    for name, results in ways.items():
        row[name] = score_retrieval(golden[o["same_as"]]["sources"], top_files(results))
        found.setdefault(name, {})[o["id"]] = [number for score, number in results[:4]]
    rows.append(row)
report("Questions in a customer's own words (20)", rows, names)

# 3. The 80 single-search questions
names = ["hybrid, as asked", "many ways to ask", "imagined answer", "sub-questions", "routing"]
rows = []
for q in questions:
    saved = rewrites["questions"][q["id"]]
    question = q["question"]
    as_asked = search(question)
    many_ways = fuse_lists([as_asked] + [search(other) for other in saved["many_ways"]])
    imagined = fuse(vector_once(saved["imagined"])[:50], keyword_search(question))
    if len(saved["sub_questions"]) > 1:
        sub_questions = fuse_lists([search(sub) for sub in saved["sub_questions"]])
    else:
        sub_questions = as_asked
    sections = saved["sections"]
    routed = fuse(in_sections(vector_once(question), sections)[:50],
                  in_sections(keyword_search(question, how_many=len(chunks)), sections)[:50])
    ways = {
        "hybrid, as asked": as_asked, "many ways to ask": many_ways, "imagined answer": imagined,
        "sub-questions": sub_questions, "routing": routed,
    }
    row = {"id": q["id"], "category": q["category"],
           "vector, as asked": score_retrieval(q["sources"], top_files(vector_once(question))),
           "vector, imagined": score_retrieval(q["sources"], top_files(vector_once(saved["imagined"]))),
           "split": len(saved["sub_questions"]) > 1,
           "route ok": all(section_of(s) in sections for s in q["sources"])}
    for name, results in ways.items():
        row[name] = score_retrieval(q["sources"], top_files(results))
        found.setdefault(name, {})[q["id"]] = [number for score, number in results[:4]]
    rows.append(row)

report(f"Retrieval @ top 4, {len(rows)} single-search questions", rows, names)
report("Vector search alone: the question vs an imagined answer", rows, ["vector, as asked", "vector, imagined"])
multi = [r for r in rows if r["category"] == "multi-document"]
report(f"Questions that need two documents ({len(multi)})", multi, names)

print("Hit rate @ 4 by category")
print(f"  {'category':24s} {'n':>3s}" + "".join(f" {name[:9]:>9s}" for name in names))
for category in ["lookup", "part-number/error-code", "table", "multi-document", "conflicting-versions"]:
    sub = [r for r in rows if r["category"] == category]
    print(f"  {category:24s} {len(sub):3d}" + "".join(f" {sum(r[name][0] for r in sub):9d}" for name in names))

split = [r for r in rows if r["split"]]
print(f"\nSub-questions: the model split {len(split)} of {len(rows)} questions "
      f"({sum(r['category'] == 'multi-document' for r in split)} of them need two documents)")
print(f"Routing: the picked sections held every needed file for {sum(r['route ok'] for r in rows)} of {len(rows)}")

print("\nSeconds per chat call before the search (median)")
print(f"  rewrite a follow-up    {statistics.median(f['seconds']['rewritten'] for f in rewrites['follow_ups'].values()):.2f}")
for key, name in [("many_ways", "many ways to ask"), ("imagined", "imagined answer"),
                  ("sub_questions", "sub-questions"), ("sections", "routing")]:
    seconds = [saved["seconds"][key] for saved in rewrites["questions"].values()]
    print(f"  {name:22s} {statistics.median(seconds):.2f}")

with open(RESULTS / "found.json", "w") as file:
    json.dump(found, file)
