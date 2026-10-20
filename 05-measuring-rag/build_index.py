import json
from pathlib import Path

import numpy as np
from openai import OpenAI

client = OpenAI()

DOCUMENTS_FOLDER = Path("data/fernhill")
INDEX_FOLDER = Path(__file__).parent / "index"  # saved next to this script
WORDS_PER_CHUNK = 200


def load_documents():
    documents = []
    for path in sorted(DOCUMENTS_FOLDER.rglob("*.md")):
        if path.name == "README.md":
            continue  # the README describes the folder; it is not a document
        name = str(path.relative_to(DOCUMENTS_FOLDER))
        documents.append({"source": name, "text": path.read_text()})
    return documents


def split_into_chunks(text):
    words = text.split()
    chunks = []
    for start in range(0, len(words), WORDS_PER_CHUNK):
        chunk = " ".join(words[start:start + WORDS_PER_CHUNK])
        chunks.append(chunk)
    return chunks


def embed(texts):
    response = client.embeddings.create(model="text-embedding-3-small", input=texts)
    return np.array([item.embedding for item in response.data])


documents = load_documents()
print("Loaded", len(documents), "documents")

chunks = []
for document in documents:
    for text in split_into_chunks(document["text"]):
        chunks.append({"source": document["source"], "text": text})
print("Split them into", len(chunks), "chunks")

vectors = embed([chunk["text"] for chunk in chunks])
print("Embedded every chunk:", vectors.shape[1], "numbers each")

INDEX_FOLDER.mkdir(exist_ok=True)
with open(INDEX_FOLDER / "chunks.json", "w") as file:
    json.dump(chunks, file)
np.save(INDEX_FOLDER / "vectors.npy", vectors)
print("Saved", len(chunks), "chunks and their vectors in", INDEX_FOLDER.name)
