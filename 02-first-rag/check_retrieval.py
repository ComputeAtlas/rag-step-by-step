import json
from pathlib import Path

import numpy as np
from openai import OpenAI

client = OpenAI()

INDEX_FOLDER = Path(__file__).parent / "index"  # made by build_index.py

with open(INDEX_FOLDER / "chunks.json") as file:
    chunks = json.load(file)
vectors = np.load(INDEX_FOLDER / "vectors.npy")

with open("data/fernhill-questions.json") as file:
    questions = json.load(file)

# One search can't answer two kinds of question, so we leave them out here:
# "unanswerable" ones have no source, "whole-corpus" ones need all 44 tickets at once.
questions = [q for q in questions if q["category"] not in ("unanswerable", "whole-corpus")]


def find_best_files(question_vector, how_many=4):
    results = []
    for number, vector in enumerate(vectors):
        score = np.dot(question_vector, vector)
        results.append((score, number))
    results.sort(reverse=True)  # highest score first
    return [chunks[number]["source"] for score, number in results[:how_many]]


# Embed all the questions in one request.
response = client.embeddings.create(model="text-embedding-3-small", input=[q["question"] for q in questions])

hits = 0
for q, item in zip(questions, response.data):
    found_files = find_best_files(np.array(item.embedding))
    if any(source in found_files for source in q["sources"]):
        hits += 1
    else:
        print("Missed:", q["question"])

print(f"\nA right file was in the top 4 for {hits} of {len(questions)} questions.")
