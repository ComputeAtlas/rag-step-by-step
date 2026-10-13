"""Brute force: compare the question with every chunk. How does the time grow with the number of chunks?"""
import time

import numpy as np

from made_up_vectors import make_vectors


def search(vectors, question, k=10):
    scores = vectors @ question  # a score for every chunk
    best = np.argpartition(-scores, k)[:k]  # the k highest
    return best[np.argsort(-scores[best])]  # best first


def time_per_question(vectors, questions):
    times = []
    for question in questions:
        start = time.perf_counter()
        search(vectors, question)
        times.append(time.perf_counter() - start)
    return np.median(times) * 1000  # in milliseconds


vectors = make_vectors(1_000_000, 384, seed=1)
questions = make_vectors(200, 384, seed=2)
print("Made-up vectors:", vectors.shape[0], "x", vectors.shape[1])

for count in [1_000, 10_000, 100_000, 1_000_000]:
    ms = time_per_question(vectors[:count], questions)
    print(f"{count:>9,} chunks: {ms:8.3f} ms per question")
