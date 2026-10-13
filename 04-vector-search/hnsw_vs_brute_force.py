"""A million made-up vectors: brute force against an HNSW index. Time per question, and recall@10."""
import time

import hnswlib
import numpy as np

from made_up_vectors import make_vectors

SIZE = 384
COUNT = 1_000_000

vectors = make_vectors(COUNT, SIZE, seed=1)
questions = make_vectors(1000, SIZE, seed=2)
print("Made-up vectors:", COUNT, "x", SIZE, "| questions:", len(questions))

# Brute force: compare each question with every vector. Its top ten is the true top ten.
times = []
true_top_ten = []
for question in questions:
    start = time.perf_counter()
    scores = vectors @ question
    best = np.argpartition(-scores, 10)[:10]
    times.append(time.perf_counter() - start)
    true_top_ten.append(set(best))
print(f"Brute force:    {np.median(times) * 1000:7.3f} ms per question, recall@10 = 1.000")

# Build the HNSW index: every vector is added to the layered graph.
start = time.perf_counter()
index = hnswlib.Index(space="ip", dim=SIZE)  # "ip": the dot product
index.init_index(max_elements=COUNT, M=16, ef_construction=200)
index.add_items(vectors)
print(f"Built the index in {time.perf_counter() - start:.0f} s ({index.index_file_size() / 1e9:.2f} GB)")

index.set_num_threads(1)  # one question at a time
for ef in [10, 40, 100, 400]:
    index.set_ef(ef)  # candidates kept in view
    times = []
    found = 0
    for question, truth in zip(questions, true_top_ten):
        start = time.perf_counter()
        labels, distances = index.knn_query(question, k=10)
        times.append(time.perf_counter() - start)
        found += len(truth & set(labels[0]))
    recall = found / (10 * len(questions))
    print(f"HNSW, ef = {ef:3}: {np.median(times) * 1000:7.3f} ms per question, recall@10 = {recall:.3f}")
