"""Answer the same 35 test questions three ways, and save every answer with its time, tokens and cost.

- RAG: the hybrid search's best 4 chunks;
- everything: all 87 documents first, the question last (the documents can be cached);
- everything, question first: the same documents, but nothing can be cached.

The 35 questions are the first five of each of the seven kinds in the test set.
It makes 105 chat calls (70 of them send about 70,000 tokens each: about $2.50 in all).

    python 17-rag-vs-long-context/compare.py
    python 17-rag-vs-long-context/grade.py      # then grade the answers"""
import json
import statistics
from pathlib import Path

from two_ways import ask_with_everything, ask_with_everything_question_first, ask_with_rag

RESULTS_FOLDER = Path(__file__).parent / "results"

with open("data/fernhill-questions.json") as file:
    all_questions = json.load(file)

# The first five questions of each kind (lookup, part number, table, multi-document, ...).
questions = []
taken = {}
for q in all_questions:
    if taken.get(q["category"], 0) < 5:
        questions.append(q)
        taken[q["category"]] = taken.get(q["category"], 0) + 1

WAYS = [
    ("rag", ask_with_rag),
    ("everything", ask_with_everything),
    ("question_first", ask_with_everything_question_first),
]

rows = []
for number, q in enumerate(questions, start=1):
    row = {"id": q["id"], "category": q["category"], "question": q["question"], "expected": q["answer"]}
    for name, way in WAYS:
        row[name] = way(q["question"])
    rows.append(row)
    print(f"{number:2d}/{len(questions)}  {q['id']}  rag {row['rag']['seconds']:.1f} s"
          f"   everything {row['everything']['seconds']:.1f} s"
          f"   question first {row['question_first']['seconds']:.1f} s")

RESULTS_FOLDER.mkdir(exist_ok=True)
with open(RESULTS_FOLDER / "answers.json", "w") as file:
    json.dump(rows, file, indent=1)

print()
print(f"{'':16s} {'seconds (median)':>17s} {'tokens in (mean)':>17s} {'cost per question':>18s}")
for name, way in WAYS:
    seconds = statistics.median(r[name]["seconds"] for r in rows)
    tokens = statistics.mean(r[name]["input_tokens"] for r in rows)
    dollars = statistics.mean(r[name]["dollars"] for r in rows)
    print(f"{name:16s} {seconds:>17.2f} {tokens:>17,.0f} {'$' + format(dollars, '.4f'):>18s}")
