"""The scoreboard for generation: answer all 100 test questions from the same four chunks
hybrid search finds, with one prompt template, and grade each answer with the same judge and
judge prompt as the baseline.

    python 12-generation/judge_answers.py grounded   # the grounded prompt (system prompt, citations, dates)
    python 12-generation/judge_answers.py plain      # the baseline's prompt, re-run today for comparison

200 chat calls. The graded answers are saved in 12-generation/results/."""
import json
import sys
from pathlib import Path

from citations import check_citations
from prompts import MODEL, SYSTEM_PROMPT, ask, client, find_chunks, grounded_prompt, plain_prompt, says_i_dont_know

template = sys.argv[1] if len(sys.argv) > 1 else "grounded"

RESULTS_FOLDER = Path(__file__).parent / "results"
BASELINE_FILE = Path("05-measuring-rag/index/results.json")  # the frozen baseline
HYBRID_FILE = Path("08-hybrid-search/results/answers-hybrid.json")  # hybrid search, plain prompt

with open("data/fernhill-questions.json") as file:
    questions = json.load(file)


def answer_question(question, found):
    if template == "grounded":
        return ask(grounded_prompt(question, found), SYSTEM_PROMPT)
    return ask(plain_prompt(question, found))


def judge_answer(question, expected, found, system_answer):
    """The baseline's judge, word for word."""
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
    response = client.responses.create(model=MODEL, input=prompt)
    text = response.output_text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(text)


rows = []
for q in questions:
    found = find_chunks(q["question"])
    answer, tokens = answer_question(q["question"], found)
    verdict = judge_answer(q["question"], q["answer"], found, answer)
    refused = says_i_dont_know(answer)
    rows.append({
        "id": q["id"], "category": q["category"], "question": q["question"],
        "found": [c["source"] for c in found], "answer": answer,
        "correct": bool(verdict["correct"]), "faithful": bool(verdict["faithful"]),
        "refused": refused, "reason": verdict["reason"], "tokens": tokens,
        "citation_problems": check_citations(q["question"], answer, found) if template == "grounded" and not refused else [],
    })

RESULTS_FOLDER.mkdir(exist_ok=True)
with open(RESULTS_FOLDER / f"answers-{template}.json", "w") as file:
    json.dump(rows, file, indent=1)

with open(BASELINE_FILE) as file:
    baseline = {r["id"]: r for r in json.load(file)}
with open(HYBRID_FILE) as file:
    hybrid = {r["id"]: r for r in json.load(file)}

groups = [
    ("Single-search questions", lambda r: r["category"] not in ("unanswerable", "whole-corpus")),
    ("Conflicting versions", lambda r: r["category"] == "conflicting-versions"),
    ("Unanswerable", lambda r: r["category"] == "unanswerable"),
    ("All questions", lambda r: True),
]
print(f"Correct answers (top 4 chunks, judged by {MODEL})\n")
print(f"  {'':26s} {'baseline':>10s} {'hybrid':>10s} {template:>10s}")
for title, belongs in groups:
    sub = [r for r in rows if belongs(r)]
    n = len(sub)
    before = sum(baseline[r["id"]]["correct"] for r in sub)
    middle = sum(hybrid[r["id"]]["correct"] for r in sub)
    after = sum(r["correct"] for r in sub)
    print(f"  {title:26s} {before:4d} / {n:<3d} {middle:4d} / {n:<3d} {after:4d} / {n:<3d}")

answerable = [r for r in rows if r["category"] != "unanswerable"]
unanswerable = [r for r in rows if r["category"] == "unanswerable"]
print()
print(f"\"I don't know\" on the 10 unanswerable questions: {sum(r['refused'] for r in unanswerable)}")
print(f"\"I don't know\" on the 90 answerable questions:   {sum(r['refused'] for r in answerable)}")
print(f"Faithful answers: {sum(r['faithful'] for r in rows)} / {len(rows)}")
if template == "grounded":
    answered = [r for r in rows if not r["refused"]]
    clean = [r for r in answered if not r["citation_problems"]]
    print(f"Answers whose citations pass the check: {len(clean)} / {len(answered)}")
tokens_in = sum(r["tokens"]["in"] for r in rows)
tokens_out = sum(r["tokens"]["out"] for r in rows)
print(f"Answer tokens: {tokens_in / len(rows):,.0f} in, {tokens_out / len(rows):,.0f} out per question")
