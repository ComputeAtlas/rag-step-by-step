"""Show one graded answer from the scoreboard run (no API call): the question, the files the
four chunks came from, the grounded answer and what the citation check said.

    python 12-generation/show_answer.py q055"""
import json
import sys

from pathlib import Path

question_id = sys.argv[1] if len(sys.argv) > 1 else "q055"

with open(Path(__file__).parent / "results" / "answers-grounded.json") as file:
    rows = {row["id"]: row for row in json.load(file)}
row = rows[question_id]

print("Question:", row["question"])
print()
for number, source in enumerate(row["found"], start=1):
    print(f"  [{number}] {source}")
print()
print("Answer:", row["answer"])
print("Citation check:", "; ".join(row["citation_problems"]) or "passed")
