"""HyDE: search with a made-up answer instead of the question.

    python 10-query-rewriting/imagined_answer.py "your question\""""
import sys
import textwrap

from rewriters import imagine_answer
from searching import fuse, keyword_search, search, show, vector_search

question = sys.argv[1] if len(sys.argv) > 1 else "How long does delivery of a bike to the Republic of Ireland take?"
needed = sys.argv[2:]

print(textwrap.fill(f"Question: {question}", 52, subsequent_indent="  "))
print("As asked:")
show(search(question), needed)

imagined = imagine_answer(question)
print("\nImagined answer (never shown to the user):")
print(textwrap.fill(imagined, 52, initial_indent="  ", subsequent_indent="  "))

# The meaning side searches with the imagined answer; the keyword side keeps the question.
print("Searching with the imagined answer:")
show(fuse(vector_search(imagined), keyword_search(question)), needed)
