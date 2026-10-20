"""Build the same index as the first RAG (200-word chunks, text-embedding-3-small), but read the published documents
from their PDFs, through one parser. Only the parser changes; everything else stays the same.

Run from the repository root with the name of a folder in parsed/ (or "markdown" for the original clean text):
    python 06-parsing/build_index.py pdfs-pypdf
"""
import json
import sys
from pathlib import Path

import numpy as np
from openai import OpenAI

client = OpenAI()

DOCUMENTS_FOLDER = Path("data/fernhill")
PARSED_FOLDER = Path(__file__).parent / "parsed"
WORDS_PER_CHUNK = 200

parser_name = sys.argv[1]  # markdown, or a folder in parsed/ such as pdfs-pypdf
INDEX_FOLDER = Path(__file__).parent / "index" / parser_name


def load_documents():
    documents = []
    for path in sorted(DOCUMENTS_FOLDER.rglob("*.md")):
        if path.name == "README.md":
            continue
        name = str(path.relative_to(DOCUMENTS_FOLDER))
        text = path.read_text()
        parsed_path = PARSED_FOLDER / parser_name / Path(name).with_suffix(".txt")
        if parsed_path.exists():
            text = parsed_path.read_text()  # this document was published as a PDF: use what the parser read
        documents.append({"source": name, "text": text})
    return documents


def split_into_chunks(text):
    words = text.split()
    chunks = []
    for start in range(0, len(words), WORDS_PER_CHUNK):
        chunks.append(" ".join(words[start:start + WORDS_PER_CHUNK]))
    return chunks


def embed(texts):
    response = client.embeddings.create(model="text-embedding-3-small", input=texts)
    return np.array([item.embedding for item in response.data])


documents = load_documents()
chunks = []
for document in documents:
    for text in split_into_chunks(document["text"]):
        chunks.append({"source": document["source"], "text": text})
vectors = embed([chunk["text"] for chunk in chunks])

INDEX_FOLDER.mkdir(parents=True, exist_ok=True)
with open(INDEX_FOLDER / "chunks.json", "w") as file:
    json.dump(chunks, file)
np.save(INDEX_FOLDER / "vectors.npy", vectors)
print(f"{parser_name}: {len(documents)} documents, {len(chunks)} chunks, saved in index/{parser_name}")
