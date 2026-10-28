"""Score the three multimodal approaches against the text baseline on 20 questions whose answers sit in pictures.

- 14 table questions from data/fernhill-questions.json (every table question whose document we have as scanned pages:
  the 15th, about firmware dates, comes from release notes that were never printed). On the scans, the tables are
  pictures of tables.
- 6 figure questions from 16-multimodal-rag/figure-questions.json, answered only by the figures made for this lesson.

For each approach: was the right document in the top 4 pages, and was the answer right (graded by gpt-5.4-mini against
the reference answer)? The baseline is the frozen text RAG of 05-measuring-rag: its table answers come from
05-measuring-rag/index/results.json, and its figure answers are run here with the same index and prompt.
About 140 chat calls. Run from the repository root, after caption_pages.py:
    python 16-multimodal-rag/scoreboard.py
"""
import json
import time
from pathlib import Path

from openai import OpenAI

import ask_text_rag
import caption_search
import clip_search
import page_search
from vision import answer_from_pictures

client = OpenAI()
PAGE_FOLDER = Path("16-multimodal-rag/results/pages")

with open("16-multimodal-rag/results/pages.json") as file:
    printed = {page["source"] for page in json.load(file)}
with open("data/fernhill-questions.json") as file:
    table_questions = [q for q in json.load(file)
                       if q["category"] == "table" and all(s in printed for s in q["sources"])]
with open("16-multimodal-rag/figure-questions.json") as file:
    figure_questions = json.load(file)
questions = table_questions + figure_questions

with open("05-measuring-rag/index/results.json") as file:
    baseline = {row["id"]: row for row in json.load(file)}


def judge(question, expected, system_answer):
    prompt = f"""You are grading an answer against a reference answer.

Question: {question}
Reference answer: {expected}
System answer: {system_answer}

Return JSON with two keys:
- "correct": true ONLY if the system answer gives the same factual answer as the reference answer. If the system says "I don't know", "correct" MUST be false.
- "reason": one short sentence.
Return only raw JSON."""
    response = client.responses.create(model="gpt-5.4-mini", input=prompt)
    text = response.output_text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(text)["correct"]


def run_baseline(q):
    if q["category"] == "table":                      # the frozen run of the baseline scoreboard
        row = baseline[q["id"]]
        found = [c["source"] for c in row["retrieved"][:4]]
        return found, row["answer"], row["correct"], 0.0
    found = ask_text_rag.find_best_chunks(q["question"])
    answer = ask_text_rag.ask_rag(q["question"], found)
    return [c["source"] for score, c in found], answer, judge(q["question"], q["answer"], answer), 0.0


def run_captions(q):
    found = caption_search.search_pages(q["question"])
    answer, usage = caption_search.answer_from_captions(q["question"], found)
    dollars = usage.input_tokens * 0.75 / 1_000_000 + usage.output_tokens * 4.50 / 1_000_000
    return [p["source"] for score, p in found], answer, judge(q["question"], q["answer"], answer), dollars


def run_on_pictures(search):
    def run(q):
        found = search(q["question"])
        pictures = [PAGE_FOLDER / page["file"] for score, page in found]
        answer, cost = answer_from_pictures(q["question"], pictures)
        return [p["source"] for score, p in found], answer, judge(q["question"], q["answer"], answer), cost["dollars"]
    return run


approaches = {
    "text baseline": run_baseline,
    "captions": run_captions,
    "one space (CLIP)": run_on_pictures(clip_search.search_pages),
    "page pictures (ColQwen2)": run_on_pictures(page_search.search_pages),
}

rows = []
for name, run in approaches.items():
    print(f"\n== {name}")
    for q in questions:
        start = time.perf_counter()
        found, answer, correct, dollars = run(q)
        hit = any(source in found for source in q["sources"])
        rows.append({"approach": name, "id": q["id"], "category": q["category"], "question": q["question"],
                     "expected": q["answer"], "found": found, "hit": hit, "answer": answer, "correct": correct,
                     "answer_dollars": dollars, "seconds": time.perf_counter() - start})
        print(f"{q['id']}  page found: {'yes' if hit else 'no '}  answer: {'right' if correct else 'WRONG'}"
              f"  | {answer[:70]}")

with open("16-multimodal-rag/results/scoreboard.json", "w") as file:
    json.dump(rows, file, indent=1)

print(f"\n{'approach':26s} {'right page':>12s} {'right answer':>14s} {'tables':>8s} {'figures':>8s}  answer cost")
for name in approaches:
    mine = [r for r in rows if r["approach"] == name]
    tables = sum(r["correct"] for r in mine if r["category"] == "table")
    figures = sum(r["correct"] for r in mine if r["category"] == "figure")
    cost = sum(r["answer_dollars"] for r in mine) / len(mine)
    print(f"{name:26s} {sum(r['hit'] for r in mine):6d} / {len(mine)} {sum(r['correct'] for r in mine):8d} / {len(mine)}"
          f" {tables:5d}/{len(table_questions)} {figures:5d}/{len(figure_questions)}   ${cost:.4f} a question")
