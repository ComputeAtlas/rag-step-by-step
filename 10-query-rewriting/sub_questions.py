"""Split a question that needs two facts into sub-questions, search each, merge the lists.

    python 10-query-rewriting/sub_questions.py "your question\""""
import sys
import textwrap

from rewriters import split_question
from searching import fuse_lists, search, show

question = sys.argv[1] if len(sys.argv) > 1 else (
    "What does a Metro 300 owner pay to replace the hub motor at the service exchange price, including labour?")
needed = sys.argv[2:]

print(textwrap.fill(f"Question: {question}", 52, subsequent_indent="  "))
print("As asked:")
show(search(question), needed)

subs = split_question(question)
print("\nSub-questions:")
lists = []
for sub in subs:
    print(textwrap.fill(f"- {sub}", 52, subsequent_indent="  "))
    lists.append(search(sub))
print("Each one searched, merged by their places:")
show(fuse_lists(lists), needed)
