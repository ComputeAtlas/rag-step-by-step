"""Search the pages through their text: the captions from caption_pages.py, embedded like any other text.

Once a page is text, everything else is the RAG you already know: one embedding per page
(text-embedding-3-small), the closest pages win, and the model answers from their text.
Run from the repository root, after caption_pages.py:  python 16-multimodal-rag/caption_search.py
"""
import json
import sys
from pathlib import Path

import numpy as np
from openai import OpenAI

client = OpenAI()
VECTOR_FILE = Path("16-multimodal-rag/results/caption-vectors.npy")

with open("16-multimodal-rag/results/captions.json") as file:
    captions = json.load(file)


def embed(texts):
    response = client.embeddings.create(model="text-embedding-3-small", input=texts)
    return np.array([item.embedding for item in response.data])


if VECTOR_FILE.exists():
    caption_vectors = np.load(VECTOR_FILE)
else:
    caption_vectors = embed([c["text"] for c in captions])
    np.save(VECTOR_FILE, caption_vectors)


def search_pages(question, how_many=4):
    scores = caption_vectors @ embed([question])[0]
    best = np.argsort(-scores)[:how_many]
    return [(float(scores[number]), captions[number]) for number in best]


def answer_from_captions(question, found):
    passages = "\n\n".join(f"From {c['source']}, page {c['page']}:\n{c['text']}" for score, c in found)
    prompt = f"""Answer the question using only the passages below.
If they don't contain the answer, say that you don't know.
Reply in plain text, without formatting.

{passages}

Question: {question}"""
    response = client.responses.create(model="gpt-5.4-mini", input=prompt)
    return response.output_text.strip(), response.usage


if __name__ == "__main__":
    question = "What torque do the clamp screws of the Ridge 500's display bracket need?"
    if len(sys.argv) > 1:
        question = sys.argv[1]
    found = search_pages(question)
    print("Question:", question)
    print("Pages found:")
    for score, page in found:
        print(f"  {score:.2f}  {page['file']}")
    answer, usage = answer_from_captions(question, found)
    print("Answer:", answer)
