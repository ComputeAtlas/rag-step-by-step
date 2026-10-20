import sys
from pathlib import Path

import numpy as np
from openai import OpenAI

from chunkers import fixed_size, recursive, by_headings

client = OpenAI()

DOCUMENTS_FOLDER = Path("data/fernhill")
WAYS = {"fixed": fixed_size, "recursive": recursive, "headings": by_headings}


def load_documents():
    documents = []
    for path in sorted(DOCUMENTS_FOLDER.rglob("*.md")):
        if path.name == "README.md":
            continue  # the README describes the folder; it is not a document
        name = str(path.relative_to(DOCUMENTS_FOLDER))
        documents.append({"source": name, "text": path.read_text()})
    return documents


def embed(texts):
    response = client.embeddings.create(model="text-embedding-3-small", input=texts)
    return np.array([item.embedding for item in response.data])


def build_prompt(question, found):
    passages = ""
    for score, chunk in found:
        passages += f"From {chunk['source']}:\n{chunk['text']}\n\n"
    return f"""Answer the question using only the passages below.
If they don't contain the answer, say that you don't know.

{passages}Question: {question}"""


# Which way to cut: python 07-chunking/ask.py recursive   (fixed, recursive or headings)
way = sys.argv[1] if len(sys.argv) > 1 else "recursive"
cut = WAYS[way]

chunks = []
for document in load_documents():
    for text in cut(document["text"], 200):
        chunks.append({"source": document["source"], "text": text})
vectors = embed([chunk["text"] for chunk in chunks])
print(f"Cut {way}: {len(chunks)} chunks of up to 200 words")

question = input("Your question: ")
scores = vectors @ embed([question])[0]
best = np.argsort(-scores)[:4]  # the four highest scores
found = [(scores[number], chunks[number]) for number in best]

print("\nThe 4 best chunks:")
for score, chunk in found:
    print(f"  {score:.2f}  {chunk['source']}")

response = client.responses.create(model="gpt-5.4-mini", input=build_prompt(question, found))
print("\nAnswer:")
print(response.output_text)
