from pathlib import Path

import numpy as np

from semantic import split_into_sentences, embed, neighbour_similarities, semantic_chunks

text = Path("data/fernhill/warranty-policy.md").read_text()
sentences = split_into_sentences(text)
vectors = embed(sentences)
scores = neighbour_similarities(vectors)
print(f"warranty-policy.md: {len(sentences)} sentences, {len(scores)} neighbour scores\n")

print("Each sentence compared with the one before it:")
for start in range(0, len(scores), 9):
    print("  " + "  ".join(f"{score:.3f}" for score in scores[start:start + 9]))

cut_below = np.percentile(scores, 5)
print(f"\nCut where the score is {cut_below:.3f} or lower:")
for i, score in enumerate(scores):
    if score <= cut_below:
        print(f"  {score:.3f}  before: {sentences[i + 1]}")

chunks = semantic_chunks(sentences, vectors)
print(f"\n{len(chunks)} chunks: " + ", ".join(f"{len(chunk.split())} words" for chunk in chunks))
