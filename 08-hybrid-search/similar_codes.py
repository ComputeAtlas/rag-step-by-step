"""How similar does the embedding model think two part numbers are?
A score of 1 means "the same meaning"; unrelated texts score much lower."""
import numpy as np
from openai import OpenAI

client = OpenAI()

pairs = [
    ("FH-2291-B", "FH-2219-B"),  # two batteries for two different bikes
    ("FH-2291-B", "FH-3105-A"),  # a battery and a brake pad
    ("FH-2291-B", "battery pack"),  # what FH-2291-B really is
    ("What fits part FH-2291-B?", "What fits part FH-2219-B?"),
]

texts = []
for first, second in pairs:
    texts.append(first)
    texts.append(second)
response = client.embeddings.create(model="text-embedding-3-small", input=texts)
vectors = [np.array(item.embedding) for item in response.data]

print("Similarity (text-embedding-3-small):\n")
for i, (first, second) in enumerate(pairs):
    score = np.dot(vectors[2 * i], vectors[2 * i + 1])
    print(f"  {score:.2f}  {first}  vs  {second}")
