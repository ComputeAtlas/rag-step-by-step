"""Keep an index in step with a folder of documents that keeps changing.

The index remembers a fingerprint of every document: a short code computed from its text.
If the text changes by even one letter, the fingerprint changes. sync_index() compares the
folder with the index and only does the work that is needed:
- a new document: chunk it, embed the chunks, add them;
- a changed document: remove its old chunks, then chunk and embed it again;
- a deleted document: remove its chunks (otherwise the index keeps answering from it)."""
import hashlib
from pathlib import Path

import numpy as np

from pipeline import EMBEDDING_MODEL, client, make_index

WORDS_PER_CHUNK = 200  # the same 200-word chunks as the baseline


def fingerprint(text):
    return hashlib.sha256(text.encode()).hexdigest()[:12]


def read_documents(folder):
    documents = {}
    for path in sorted(Path(folder).rglob("*.md")):
        if path.name == "README.md":
            continue
        documents[str(path.relative_to(folder))] = path.read_text()
    return documents


def split_into_chunks(source, text):
    words = text.split()
    chunks = []
    for start in range(0, len(words), WORDS_PER_CHUNK):
        chunks.append({"source": source, "text": " ".join(words[start:start + WORDS_PER_CHUNK])})
    return chunks


def embed_chunks(chunks):
    if not chunks:
        return np.zeros((0, 1536))
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=[c["text"] for c in chunks])
    return np.array([item.embedding for item in response.data])


def build_index(folder):
    documents = read_documents(folder)
    chunks = []
    for source, text in documents.items():
        chunks += split_into_chunks(source, text)
    index = make_index(chunks, embed_chunks(chunks))
    index["fingerprints"] = {source: fingerprint(text) for source, text in documents.items()}
    return index


def sync_index(index, folder):
    """Bring the index up to date with the folder. Returns what changed."""
    documents = read_documents(folder)
    old = index["fingerprints"]
    new = [s for s in documents if s not in old]
    changed = [s for s in documents if s in old and fingerprint(documents[s]) != old[s]]
    deleted = [s for s in old if s not in documents]
    unchanged = len(documents) - len(new) - len(changed)

    # 1. Remove the chunks of changed and deleted documents.
    remove = set(changed + deleted)
    keep = [n for n, chunk in enumerate(index["chunks"]) if chunk["source"] not in remove]
    removed = len(index["chunks"]) - len(keep)
    chunks = [index["chunks"][n] for n in keep]
    vectors = index["vectors"][keep]

    # 2. Chunk and embed new and changed documents: only those.
    fresh = []
    for source in new + changed:
        fresh += split_into_chunks(source, documents[source])
    chunks += fresh
    vectors = np.vstack([vectors, embed_chunks(fresh)])

    # 3. Rebuild the keyword index and remember the new fingerprints.
    updated = make_index(chunks, vectors)
    updated["fingerprints"] = {source: fingerprint(text) for source, text in documents.items()}
    index.clear()
    index.update(updated)
    return {"unchanged": unchanged, "new": new, "changed": changed, "deleted": deleted,
            "removed": removed, "embedded": len(fresh)}
