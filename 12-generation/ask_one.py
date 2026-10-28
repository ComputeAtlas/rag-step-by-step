"""Ask one question with the plain prompt (three times) and with the grounded prompt.
The chunks are the same four that hybrid search finds. Four chat calls.

    python 12-generation/ask_one.py
    python 12-generation/ask_one.py "Your own question?" """
import sys

from prompts import SYSTEM_PROMPT, ask, find_chunks, grounded_prompt, plain_prompt

question = "I bought my Ridge 500 on 10 December 2025. How long is its battery covered?"
if len(sys.argv) > 1:
    question = sys.argv[1]

found = find_chunks(question)
print("Question:", question)
print()
print("Found by hybrid search:")
for place, c in enumerate(found, start=1):
    print(f"  {place}. {c['source']}")
print()

print("Plain prompt, three tries:")
for attempt in range(3):
    answer, tokens = ask(plain_prompt(question, found))
    print("  " + answer)
print()

answer, tokens = ask(grounded_prompt(question, found), SYSTEM_PROMPT)
print("Grounded prompt:")
print("  " + answer)
