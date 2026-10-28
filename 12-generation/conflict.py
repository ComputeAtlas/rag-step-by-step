"""Two warranty policies that disagree: 2025 (defective below 60%) and 2026 (below 70%).
One question, the same four chunks, the plain prompt and the grounded prompt. Two chat calls."""
from prompts import SYSTEM_PROMPT, ask, document_date, find_chunks, grounded_prompt, plain_prompt

question = "I bought my Ridge 500 in June 2025. Its battery now holds 65% of its capacity. Is that a warranty defect?"

found = find_chunks(question)
print("Question:", question)
print()
print("Found by hybrid search, with each document's date:")
for place, c in enumerate(found, start=1):
    print(f"  [{place}] {c['source']} ({document_date(c['source'])})")
print()

answer, tokens = ask(plain_prompt(question, found))
print("Plain prompt:")
print("  " + " ".join(answer.split()))
print()
answer, tokens = ask(grounded_prompt(question, found), SYSTEM_PROMPT)
print("Grounded prompt:")
print("  " + " ".join(answer.split()))
