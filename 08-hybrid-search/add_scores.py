"""The common mistake: merging two searches by adding their scores.
A cosine score sits between 0 and 1; a BM25 score can be 5, 10 or 30. Added together, the
bigger numbers decide almost everything, so the "merged" list is the keyword list again."""
import json

import numpy as np
from openai import OpenAI

from searches import bm25, chunks, vectors, words

client = OpenAI()


def both_scores(question_vector, question):
    vector_scores = vectors @ question_vector  # 0 to 1
    keyword_scores = bm25.get_scores(words(question))  # 0 to 30 or more
    return vector_scores, keyword_scores


# One question, up close.
question = "What fits part FH-2291-B?"
response = client.embeddings.create(model="text-embedding-3-small", input=question)
vector_scores, keyword_scores = both_scores(np.array(response.data[0].embedding), question)
added = vector_scores + keyword_scores
print("Question:", question)
print("  vector + keyword = added")
for number in np.argsort(-added)[:4]:
    file_name = chunks[number]["source"].split("/")[-1]
    print(f"  {vector_scores[number]:.2f}  + {keyword_scores[number]:5.2f} = {added[number]:5.2f}  {file_name}")

# The 80 test questions.
with open("data/fernhill-questions.json") as file:
    all_questions = json.load(file)
questions = [
    q for q in all_questions
    if q["category"] not in ("unanswerable", "whole-corpus")
]
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=[q["question"] for q in questions],
)
same = 0
highest = 0
for q, item in zip(questions, response.data):
    vector_scores, keyword_scores = both_scores(np.array(item.embedding), q["question"])
    added = vector_scores + keyword_scores
    highest = max(highest, keyword_scores.max())
    if set(np.argsort(-added)[:4]) == set(np.argsort(-keyword_scores)[:4]):
        same += 1
print(f"\nHighest keyword score in the 80 questions: {highest:.1f}")
print(f"Same 4 chunks as keyword search alone: {same} of {len(questions)} questions")
