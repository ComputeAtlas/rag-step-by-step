import json
import time
from pathlib import Path

import numpy as np
from openai import OpenAI

client = OpenAI()

INDEX_FOLDER = Path(__file__).parent / "index"  # made by build_index.py

with open(INDEX_FOLDER / "chunks.json") as file:
    chunks = json.load(file)
vectors = np.load(INDEX_FOLDER / "vectors.npy")


def embed(text):
    response = client.embeddings.create(model="text-embedding-3-small", input=text)
    return np.array(response.data[0].embedding)


def find_best_chunks(question_vector, how_many=4):
    results = []
    for number, vector in enumerate(vectors):
        score = np.dot(question_vector, vector)  # 1 = same meaning, 0 = unrelated
        results.append((score, number))
    results.sort(reverse=True)  # highest score first
    return [(score, chunks[number]) for score, number in results[:how_many]]


def build_prompt(question, found):
    passages = ""
    for score, chunk in found:
        passages += f"From {chunk['source']}:\n{chunk['text']}\n\n"
    return f"""Answer the question using only the passages below.
If they don't contain the answer, say that you don't know.

{passages}Question: {question}"""


def answer(prompt):
    response = client.responses.create(model="gpt-5.4-mini", input=prompt)
    return response.output_text


question = input("Your question: ")
start = time.time()

found = find_best_chunks(embed(question))
print(f"\nThe {len(found)} best chunks (found in {time.time() - start:.1f} s):")
for score, chunk in found:
    print(f"  {score:.2f}  {chunk['source']}")

print("\nAnswer:")
print(answer(build_prompt(question, found)))
print(f"\nDone in {time.time() - start:.1f} s")
