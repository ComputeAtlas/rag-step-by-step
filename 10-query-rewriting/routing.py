"""Routing: the model picks which part of the library to search, and we search only there.

    python 10-query-rewriting/routing.py "your question\""""
import sys
import textwrap

from rewriters import pick_sections
from searching import chunks, fuse, in_sections, keyword_search, search, show, vector_search

question = sys.argv[1] if len(sys.argv) > 1 else "In which firmware version did Battery care mode (the 80% charge limit) actually arrive?"
needed = sys.argv[2:]

print(textwrap.fill(f"Question: {question}", 52, subsequent_indent="  "))
print("Searching everything:")
show(search(question), needed)

sections = pick_sections(question)
print(f"\nThe model picked: {', '.join(sections)}")
everything = len(chunks)
print("Searching only there:")
show(fuse(in_sections(vector_search(question, everything), sections)[:50],
          in_sections(keyword_search(question, everything), sections)[:50]), needed)
