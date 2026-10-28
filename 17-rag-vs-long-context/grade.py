"""Grade the answers saved by compare.py: a second model compares each answer with the test set's answer.
Then print the scoreboard: correct answers, time and cost per question, for each way.

    python 17-rag-vs-long-context/grade.py

It makes one small chat call per answer (105 in all)."""
import json
import statistics
from pathlib import Path

from openai import OpenAI

client = OpenAI()
RESULTS_FOLDER = Path(__file__).parent / "results"
WAYS = ["rag", "everything", "question_first"]


def is_correct(question, expected, answer):
    prompt = f"""You are grading an answer to a question about a company's documents.

Question: {question}
Reference answer: {expected}
System answer: {answer}

Return JSON with two keys:
- "correct": true ONLY if the system answer gives the same factual answer as the reference answer. If the reference answer is "Not in the documents", it is correct only if the system says it doesn't know. If the reference answer is a fact and the system says it doesn't know, it is false.
- "reason": one short sentence.
Return only raw JSON."""
    response = client.responses.create(model="gpt-5.4-mini", input=prompt)
    text = response.output_text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(text)


with open(RESULTS_FOLDER / "answers.json") as file:
    rows = json.load(file)

for row in rows:
    for name in WAYS:
        verdict = is_correct(row["question"], row["expected"], row[name]["answer"])
        row[name]["correct"] = bool(verdict["correct"])
        row[name]["reason"] = verdict["reason"]

with open(RESULTS_FOLDER / "graded.json", "w") as file:
    json.dump(rows, file, indent=1)

kinds = []
for row in rows:
    if row["category"] not in kinds:
        kinds.append(row["category"])

print(f"Correct answers ({len(rows)} questions, graded by gpt-5.4-mini)\n")
print(f"  {'':24s} {'RAG':>8s} {'everything':>11s} {'question first':>15s}")
for kind in kinds + ["all"]:
    sub = [r for r in rows if kind == "all" or r["category"] == kind]
    counts = [sum(r[name]["correct"] for r in sub) for name in WAYS]
    print(f"  {kind:24s} {counts[0]:4d} / {len(sub):<3d}"
          f" {counts[1]:5d} / {len(sub):<3d} {counts[2]:7d} / {len(sub):<3d}")

print()
print(f"  {'':24s} {'RAG':>8s} {'everything':>11s} {'question first':>15s}")
seconds = [statistics.median(r[name]["seconds"] for r in rows) for name in WAYS]
print(f"  {'seconds (median)':24s} {seconds[0]:8.2f} {seconds[1]:11.2f} {seconds[2]:15.2f}")
tokens = [statistics.mean(r[name]["input_tokens"] for r in rows) for name in WAYS]
print(f"  {'tokens in (mean)':24s} {tokens[0]:8,.0f} {tokens[1]:11,.0f} {tokens[2]:15,.0f}")
dollars = [statistics.mean(r[name]["dollars"] for r in rows) for name in WAYS]
print(f"  {'dollars per question':24s} {dollars[0]:8.4f} {dollars[1]:11.4f} {dollars[2]:15.4f}")
