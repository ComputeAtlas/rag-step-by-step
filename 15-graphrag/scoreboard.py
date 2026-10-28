"""The 10 whole-corpus test questions ("How many support tickets are about brakes?"),
answered by global search and graded by the same judge as the baseline.
The baseline's grades come from 05-measuring-rag/index/results.json (frozen), and hybrid
search's from 08-hybrid-search/results/answers-hybrid.json, if you ran that lesson.
About 10 x 40 chat calls (every report, for every question), plus 10 to grade."""
import json
import time
from pathlib import Path

from answers import judge_answer
from global_search import global_search
from model import usage_line

RESULTS = Path("15-graphrag/results")

with open("data/fernhill-questions.json") as file:
    questions = [q for q in json.load(file) if q["category"] == "whole-corpus"]
with open("05-measuring-rag/index/results.json") as file:
    baseline = {r["id"]: r for r in json.load(file)}
hybrid = {}
if Path("08-hybrid-search/results/answers-hybrid.json").exists():
    with open("08-hybrid-search/results/answers-hybrid.json") as file:
        hybrid = {r["id"]: r for r in json.load(file)}

start = time.time()
graded = []
totals = {"baseline": 0, "hybrid": 0, "global": 0}
for q in questions:
    answer, points = global_search(q["question"])
    found = [{"source": point["from"], "text": point["point"]} for point in points]
    verdict = judge_answer(q["question"], q["answer"], found, answer)
    graded.append({"id": q["id"], "question": q["question"], "answer": answer, **verdict})
    totals["baseline"] += baseline[q["id"]]["correct"] in (True, "True")
    totals["hybrid"] += hybrid.get(q["id"], {}).get("correct") in (True, "True")
    totals["global"] += verdict["correct"]
    mark = "right" if verdict["correct"] else "wrong"
    print(f"{q['id']} {q['question']}")
    print(f"     reference: {q['answer']}")
    print(f"     global search ({mark}): {answer[:110]}")

with open(RESULTS / "answers-global.json", "w") as file:
    json.dump(graded, file, indent=1)
print()
print(f"Correct, out of {len(questions)}:  baseline {totals['baseline']}   hybrid {totals['hybrid']}   "
      f"global search {totals['global']}")
print(f"Time: {(time.time() - start) / 60:.1f} minutes. Model: {usage_line()}")
