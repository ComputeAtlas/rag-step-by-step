"""Ask the baseline text RAG (the index from 05-measuring-rag) a question whose answer is only in a figure.

The baseline read Fernhill's documents as text. A picture has no text to read, so the figure never made it into the
index. Run from the repository root:  python 16-multimodal-rag/ask_text_rag.py
"""
import json
import sys

import numpy as np
from openai import OpenAI

client = OpenAI()

with open("05-measuring-rag/index/chunks.json") as file:
    chunks = json.load(file)
vectors = np.load("05-measuring-rag/index/vectors.npy")


def embed(text):
    response = client.embeddings.create(model="text-embedding-3-small", input=text)
    return np.array(response.data[0].embedding)


def find_best_chunks(question, how_many=4):
    scores = vectors @ embed(question)
    best = np.argsort(-scores)[:how_many]
    return [(float(scores[number]), chunks[number]) for number in best]


def ask_rag(question, found):
    passages = "\n\n".join(f"From {c['source']}:\n{c['text']}" for score, c in found)
    prompt = f"""Answer the question using only the passages below.
If they don't contain the answer, say that you don't know.

{passages}

Question: {question}"""
    response = client.responses.create(model="gpt-5.4-mini", input=prompt)
    return response.output_text.strip()


if __name__ == "__main__":
    question = "What torque do the clamp screws of the Ridge 500's display bracket need?"
    if len(sys.argv) > 1:
        question = sys.argv[1]
    found = find_best_chunks(question)
    print("Question:", question)
    print("Chunks found:")
    for score, chunk in found:
        print(f"  {score:.2f}  {chunk['source']}")
    print("Answer:", ask_rag(question, found))
