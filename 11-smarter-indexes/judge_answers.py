"""Answer all 100 test questions with what one setup hands the model, and let gpt-5.4-mini
judge each answer against the reference answer (the same prompts as the baseline's judge).

    python 11-smarter-indexes/judge_answers.py context        # hybrid search, chunks with context
    python 11-smarter-indexes/judge_answers.py children       # search 50-word children, read them
    python 11-smarter-indexes/judge_answers.py small-to-big   # search the children, read their parents

Each run makes 200 chat calls (one answer and one grade per question) and saves every answer
in 11-smarter-indexes/results/."""
import json
import sys
from pathlib import Path

from answers import ask_rag, judge_answer
from searches import embed, hybrid_search, load_contextual_index
from small_to_big import load_documents, make_parents_and_children, small_to_big

setup = sys.argv[1] if len(sys.argv) > 1 else "context"
RESULTS_FOLDER = Path(__file__).parent / "results"
BASELINE_FILE = Path("05-measuring-rag/index/results.json")       # vector search, plain chunks
HYBRID_FILE = Path("08-hybrid-search/results/answers-hybrid.json")  # hybrid search, plain chunks

with open("data/fernhill-questions.json") as file:
    questions = json.load(file)
question_vectors = embed([q["question"] for q in questions])

if setup == "context":
    index = load_contextual_index()
else:
    parents, children = make_parents_and_children(load_documents())
    child_vectors = embed([child["text"] for child in children])


def find_pieces(question, question_vector):
    """The four pieces of text the model gets, each with the file it came from."""
    if setup == "context":
        found = [index["chunks"][number] for score, number in hybrid_search(index, question, question_vector)[:4]]
        return [{"source": c["source"], "text": c["context"] + "\n\n" + c["text"]} for c in found]
    if setup == "children":
        best = (child_vectors @ question_vector).argsort()[::-1][:4]
        return [children[number] for number in best]
    return [parents[number] for number in small_to_big(children, child_vectors, question_vector)]


rows = []
for q, question_vector in zip(questions, question_vectors):
    found = find_pieces(q["question"], question_vector)
    answer = ask_rag(q["question"], found)
    verdict = judge_answer(q["question"], q["answer"], found, answer)
    rows.append({
        "id": q["id"], "category": q["category"], "question": q["question"],
        "found": [c["source"] for c in found], "words_read": sum(len(c["text"].split()) for c in found),
        "answer": answer, "correct": bool(verdict["correct"]), "faithful": bool(verdict["faithful"]),
        "reason": verdict["reason"],
    })

RESULTS_FOLDER.mkdir(exist_ok=True)
with open(RESULTS_FOLDER / f"answers-{setup}.json", "w") as file:
    json.dump(rows, file, indent=1)

with open(BASELINE_FILE) as file:
    baseline = {r["id"]: r for r in json.load(file)}
columns = [("baseline", baseline)]
if HYBRID_FILE.exists():  # made by 08-hybrid-search/judge_answers.py
    with open(HYBRID_FILE) as file:
        columns.append(("hybrid", {r["id"]: r for r in json.load(file)}))

groups = [
    ("Single-search questions", lambda r: r["category"] not in ("unanswerable", "whole-corpus")),
    ("All questions", lambda r: True),
]
print("Correct answers (top 4 pieces, judged by gpt-5.4-mini)\n")
print(f"  {'':26s}" + "".join(f"{name:>12s}" for name, results in columns) + f"{setup:>14s}")
for title, belongs in groups:
    sub = [r for r in rows if belongs(r)]
    line = f"  {title:26s}"
    for name, results in columns:
        line += f"{sum(results[r['id']]['correct'] for r in sub):5d} / {len(sub):<4d}"
    line += f"{sum(r['correct'] for r in sub):7d} / {len(sub):<4d}"
    print(line)
words = sum(r["words_read"] for r in rows) / len(rows)
print(f"\nWords the model reads per question: about {words:.0f}")
