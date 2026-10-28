"""Print the grounded prompt for one question: the passages as the model sees them.
No chat call (one embedding request for the search)."""
import sys

from prompts import find_chunks, grounded_prompt

question = "I bought my Ridge 500 on 10 December 2025. How long is its battery covered?"
if len(sys.argv) > 1:
    question = sys.argv[1]

prompt = grounded_prompt(question, find_chunks(question))
print(prompt)
print()
print(f"{len(prompt):,} characters")
