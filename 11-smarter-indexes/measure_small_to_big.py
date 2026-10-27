"""Search small, hand over big. For the 80 test questions a single search can answer:
is a right file among the four pieces the model gets, and how many words does it read?
Embedding requests only (about two cents), no chat calls."""
import json

import numpy as np

from searches import embed
from small_to_big import load_documents, make_parents_and_children, make_sentence_windows, small_to_big

with open("data/fernhill-questions.json") as file:
    all_questions = json.load(file)
questions = [q for q in all_questions if q["category"] not in ("unanswerable", "whole-corpus")]
question_vectors = embed([q["question"] for q in questions])

documents = load_documents()
parents, children = make_parents_and_children(documents)
sentences = make_sentence_windows(documents)
print(f"{len(documents)} documents -> {len(parents)} parents (up to 400 words)"
      f" -> {len(children)} children (up to 50 words); {len(sentences)} sentences\n")

parent_vectors = embed([p["text"] for p in parents])
child_vectors = embed([c["text"] for c in children])
sentence_vectors = embed([s["text"] for s in sentences])


def top_four(vectors, question_vector):
    return list((vectors @ question_vector).argsort()[::-1][:4])


def top_four_windows(question_vector):
    """The best sentences, skipping one whose window is the same text as one already chosen."""
    chosen = []
    for number in (sentence_vectors @ question_vector).argsort()[::-1]:
        if sentences[number]["window"] not in [sentences[c]["window"] for c in chosen]:
            chosen.append(number)
        if len(chosen) == 4:
            break
    return chosen


ways = {"search children, read children": [], "search parents, read parents": [],
        "search children, read parents": [], "search sentences, read windows": []}
for q, question_vector in zip(questions, question_vectors):
    found = {
        "search children, read children": [children[n] for n in top_four(child_vectors, question_vector)],
        "search parents, read parents": [parents[n] for n in top_four(parent_vectors, question_vector)],
        "search children, read parents": [parents[n] for n in small_to_big(children, child_vectors, question_vector)],
        "search sentences, read windows": [{"source": sentences[n]["source"], "text": sentences[n]["window"]}
                                           for n in top_four_windows(question_vector)],
    }
    for way, pieces in found.items():
        hit = any(piece["source"] in q["sources"] for piece in pieces)
        words = sum(len(piece["text"].split()) for piece in pieces)
        ways[way].append((hit, words))

print(f"{'For ' + str(len(questions)) + ' test questions':34s} {'right file in top 4':>20s}   words the model reads")
for way, results in ways.items():
    hits = sum(hit for hit, words in results)
    words = round(np.mean([words for hit, words in results]))
    print(f"{way:34s} {hits:11d} / {len(questions)}   {words:8d}")
