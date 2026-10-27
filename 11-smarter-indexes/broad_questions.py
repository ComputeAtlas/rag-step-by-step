"""Broad questions: the 10 test questions about all the support tickets at once
("What is the most common topic across the resolved support tickets?").
Each one is answered twice: from the four best chunks, and from the four best pieces of the
summary tree (chunks and summaries searched together). It needs results/ from summary_tree.py.
40 chat calls (an answer and a grade each), with the same judge as judge_answers.py."""
import json

import numpy as np

from answers import ask_rag, judge_answer
from searches import embed

with open("data/fernhill-questions.json") as file:
    questions = [q for q in json.load(file) if q["category"] == "whole-corpus"]
question_vectors = embed([q["question"] for q in questions])

with open("11-smarter-indexes/results/tree.json") as file:
    tree = json.load(file)
tree_vectors = np.load("11-smarter-indexes/results/tree-vectors.npy")
chunk_numbers = [n for n, piece in enumerate(tree) if piece["level"] == 0]  # the plain chunks only

totals = {"chunks": 0, "tree": 0}
for q, question_vector in zip(questions, question_vectors):
    scores = tree_vectors @ question_vector
    best_chunks = sorted(chunk_numbers, key=lambda n: -scores[n])[:4]
    best_in_tree = list(scores.argsort()[::-1][:4])  # any level of the tree
    print(q["question"])
    print(f"  reference answer: {q['answer']}")
    for name, numbers in [("chunks", best_chunks), ("tree", best_in_tree)]:
        found = [tree[n] for n in numbers]
        answer = ask_rag(q["question"], found)
        verdict = judge_answer(q["question"], q["answer"], found, answer)
        totals[name] += verdict["correct"]
        levels = ", ".join(f"level {piece['level']}" for piece in found)
        mark = "right" if verdict["correct"] else "wrong"
        print(f"  {name:6s} ({levels}): {mark}: {answer[:90]}")
    print()

print(f"Correct, out of {len(questions)}:  chunks only {totals['chunks']}   summary tree {totals['tree']}")
