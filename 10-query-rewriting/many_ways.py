"""Multi-query: ask the model for three other ways to ask, search with all four, merge the lists.

    python 10-query-rewriting/many_ways.py "your question\""""
import sys
import textwrap

from rewriters import other_ways_to_ask
from searching import fuse_lists, search, show

question = sys.argv[1] if len(sys.argv) > 1 else "How long does delivery of a bike to the Republic of Ireland take?"
needed = sys.argv[2:]  # optional: the files the question needs, to mark them with +

print(textwrap.fill(f"Question: {question}", 52, subsequent_indent="  "))
print("As asked:")
as_asked = search(question)
show(as_asked, needed)

others = other_ways_to_ask(question)
print("\nOther ways to ask:")
for other in others:
    print(textwrap.fill(f"- {other}", 52, subsequent_indent="  "))

lists = [as_asked]
for other in others:
    lists.append(search(other))
print("All four, merged by their places:")
show(fuse_lists(lists), needed)
