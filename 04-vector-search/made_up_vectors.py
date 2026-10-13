"""Made-up vectors for the speed tests.

Embedding a million real chunks would take hours and cost money, so the speed tests use made-up
(synthetic) vectors instead. Like real embeddings, they bunch together in groups (topics) instead of
being spread out evenly, and every vector has length 1.
"""
import numpy as np

TOPICS = 2000  # how many groups the vectors bunch into


def make_vectors(count, size, seed):
    # The topic centres are the same every time (seed 0), so questions and chunks share the same topics.
    centres = np.random.default_rng(0).standard_normal((TOPICS, size), dtype=np.float32)

    random = np.random.default_rng(seed)
    vectors = np.empty((count, size), dtype=np.float32)
    for start in range(0, count, 100_000):  # 100,000 at a time, to save memory
        end = min(start + 100_000, count)
        topic = random.integers(0, TOPICS, end - start)  # pick a topic for each vector
        noise = random.standard_normal((end - start, size), dtype=np.float32)
        batch = centres[topic] + noise  # a point somewhere near its topic's centre
        # Give every vector length 1, like OpenAI's embeddings: then the dot product is the similarity score.
        vectors[start:end] = batch / np.linalg.norm(batch, axis=1, keepdims=True)
    return vectors
