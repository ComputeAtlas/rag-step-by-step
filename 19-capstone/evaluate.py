"""The scoreboard for the app: all 100 test questions, through the app's own search and answer,
graded by the same judge as every other system in the course.

It prints the score, saves every answer in results/scoreboard.json, and lists the questions that
were right last time and are wrong now (a regression). If the score falls below MIN_CORRECT it
exits with an error, so an automatic check (CI) can stop a change that made the app worse.

Run from the repository root:  python 19-capstone/evaluate.py   (about 300 model calls, ~6 minutes)"""
import json
import statistics
import sys
import time
from pathlib import Path

from answer import stream_answer
from judge import judge_answer
from search import find_sections

MIN_CORRECT = 78  # out of 100: a few points under our measured 82, because a re-run wobbles

HERE = Path(__file__).parent
QUESTIONS_FILE = HERE.parent / "data" / "fernhill-questions.json"
RESULTS_FILE = HERE / "results" / "scoreboard.json"
# Published prices for gpt-5.4-mini, dollars per million tokens (input, output).
PRICE_IN, PRICE_OUT = 0.75, 4.50

with open(QUESTIONS_FILE) as file:
    questions = json.load(file)

previous = {}
if RESULTS_FILE.exists():
    with open(RESULTS_FILE) as file:
        previous = {row["id"]: row["correct"] for row in json.load(file)}

rows = []
answer_usage = {"in": 0, "out": 0}
judge_usage = {"in": 0, "out": 0}
for number, q in enumerate(questions, start=1):
    started = time.time()
    found = find_sections(q["question"])
    usage = {}
    answer = "".join(stream_answer(q["question"], found, usage))
    seconds = time.time() - started
    answer_usage["in"] += usage["in"]
    answer_usage["out"] += usage["out"]
    verdict = judge_answer(q["question"], q["answer"], found, answer, judge_usage)
    rows.append({"id": q["id"], "category": q["category"], "question": q["question"],
                 "expected": q["answer"], "answer": answer, "sources": [s["source"] for s in found],
                 "hit": any(s["source"] in q["sources"] for s in found),
                 "correct": bool(verdict["correct"]), "faithful": bool(verdict["faithful"]),
                 "reason": verdict["reason"], "seconds": round(seconds, 2)})
    print(f"{number:3d}/100 {q['id']} {'right' if verdict['correct'] else 'WRONG'}", flush=True)

RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(RESULTS_FILE, "w") as file:
    json.dump(rows, file, indent=1)

print("\nScoreboard: the finished app on 100 test questions\n")
for category in ["lookup", "part-number/error-code", "table", "multi-document",
                 "conflicting-versions", "whole-corpus", "unanswerable"]:
    sub = [r for r in rows if r["category"] == category]
    print(f"  {category:24s} {sum(r['correct'] for r in sub):3d} / {len(sub)}")
correct = sum(r["correct"] for r in rows)
single = [r for r in rows if r["category"] not in ("whole-corpus", "unanswerable")]
answerable = [r for r in rows if r["category"] != "unanswerable"]
print(f"\n  correct answers          {correct:3d} / 100")
print(f"  right page found         {sum(r['hit'] for r in single):3d} / {len(single)}  (single-search questions)")
gave_up = [r for r in answerable if "don't know" in r["answer"].replace("’", "'")]
print(f"  'I don't know' wrongly   {len(gave_up):3d} / {len(answerable)}")
cost = (answer_usage["in"] * PRICE_IN + answer_usage["out"] * PRICE_OUT) / 1_000_000
print(f"  answers cost             ${cost:.3f} for 100 questions (judge not included)")
print(f"  time per answer          {statistics.median(r['seconds'] for r in rows):.1f} s median")

regressions = [r["id"] for r in rows if previous.get(r["id"]) is True and not r["correct"]]
if previous:
    print(f"\nRight last time, wrong now: {', '.join(regressions) if regressions else 'none'}")

if correct < MIN_CORRECT:
    print(f"\nFAIL: {correct} correct is below the line of {MIN_CORRECT}.")
    sys.exit(1)
print(f"\nPASS: {correct} correct (the line is {MIN_CORRECT}).")
