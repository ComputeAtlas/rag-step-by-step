"""Answer all 100 test questions with the four chunks a search finds, and let gpt-5.4-mini judge
each answer against the reference answer (the same prompts as the baseline's judge).

    python 08-hybrid-search/judge_answers.py            # hybrid search
    python 08-hybrid-search/judge_answers.py vector     # vector search, to re-check the baseline

It makes 200 chat calls (one answer and one grade per question) and saves every answer
in 08-hybrid-search/results/."""
import json
import sys
from pathlib import Path

from openai import OpenAI

from searches import chunks, hybrid_search, vector_search

client = OpenAI()

search_name = sys.argv[1] if len(sys.argv) > 1 else "hybrid"
search = {"hybrid": hybrid_search, "vector": vector_search}[search_name]

RESULTS_FOLDER = Path(__file__).parent / "results"
BASELINE_FILE = Path("05-measuring-rag/index/results.json")  # the baseline's graded answers

with open("data/fernhill-questions.json") as file:
    questions = json.load(file)


def ask_rag(question, found):
    passages = "\n\n".join(f"From {c['source']}:\n{c['text']}" for c in found)
    prompt = f"""Answer the question using only the passages below.
If they don't contain the answer, say that you don't know.

{passages}

Question: {question}"""
    response = client.responses.create(model="gpt-5.4-mini", input=prompt)
    return response.output_text.strip()


def judge_answer(question, expected, found, system_answer):
    passages = "\n\n".join(f"From {c['source']}:\n{c['text']}" for c in found)
    prompt = f"""You are grading a RAG system on two separate criteria.

Question: {question}
Reference answer: {expected}

Retrieved passages:
{passages}

System answer: {system_answer}

Return JSON with three keys:
- "faithful": true if the system answer only states facts supported by the retrieved passages (or says it does not know when the passages lack the answer), false if it invents or extrapolates facts not in the passages.
- "correct": true ONLY if the system answer gives the same factual answer as the reference answer. If the reference answer is a specific fact (not "Not in the documents") and the system says "I don't know", "correct" MUST be false.
- "reason": one short sentence explaining both grades.
Return only raw JSON."""
    response = client.responses.create(model="gpt-5.4-mini", input=prompt)
    text = response.output_text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(text)


rows = []
for q in questions:
    found = [chunks[number] for score, number in search(q["question"])[:4]]
    answer = ask_rag(q["question"], found)
    verdict = judge_answer(q["question"], q["answer"], found, answer)
    rows.append({
        "id": q["id"], "category": q["category"], "question": q["question"],
        "found": [c["source"] for c in found], "answer": answer,
        "correct": bool(verdict["correct"]), "faithful": bool(verdict["faithful"]),
        "reason": verdict["reason"],
    })

RESULTS_FOLDER.mkdir(exist_ok=True)
with open(RESULTS_FOLDER / f"answers-{search_name}.json", "w") as file:
    json.dump(rows, file, indent=1)

with open(BASELINE_FILE) as file:
    baseline = {r["id"]: r for r in json.load(file)}

groups = [
    ("Part numbers and error codes", lambda r: r["category"] == "part-number/error-code"),
    ("Single-search questions", lambda r: r["category"] not in ("unanswerable", "whole-corpus")),
    ("All questions", lambda r: True),
]
print(f"Correct answers (top 4 chunks, judged by gpt-5.4-mini)\n")
print(f"  {'':30s} {'baseline':>10s} {search_name:>10s}")
for title, belongs in groups:
    sub = [r for r in rows if belongs(r)]
    before = sum(baseline[r["id"]]["correct"] for r in sub)
    after = sum(r["correct"] for r in sub)
    print(f"  {title:30s} {before:4d} / {len(sub):<3d} {after:4d} / {len(sub):<3d}")
