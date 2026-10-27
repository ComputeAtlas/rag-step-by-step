"""Ask one broad question twice: from the four best chunks, and from the four best pieces of
the summary tree (chunks and summaries searched together). It needs results/ from summary_tree.py.

    python 11-smarter-indexes/ask_tree.py
    python 11-smarter-indexes/ask_tree.py "What are the main topics of the release notes?"
"""
import json
import sys
import textwrap

import numpy as np

from answers import ask_rag
from searches import embed

question = sys.argv[1] if len(sys.argv) > 1 else "What kinds of problems do customers contact support about?"

with open("11-smarter-indexes/results/tree.json") as file:
    tree = json.load(file)
tree_vectors = np.load("11-smarter-indexes/results/tree-vectors.npy")

question_vector = embed([question])[0]
scores = tree_vectors @ question_vector
chunk_numbers = [n for n, piece in enumerate(tree) if piece["level"] == 0]
best_chunks = sorted(chunk_numbers, key=lambda n: -scores[n])[:4]  # chunks only
best_in_tree = list(scores.argsort()[::-1][:4])                     # any level

print("Question:", question)
for name, numbers in [("Chunks only", best_chunks), ("The summary tree", best_in_tree)]:
    found = [tree[n] for n in numbers]
    print(f"\n{name} found:")
    for piece in found:
        print(f"  level {piece['level']}  {piece['source']}")
    print("Answer:")
    for line in textwrap.wrap(ask_rag(question, found), 72):
        print("  " + line)
