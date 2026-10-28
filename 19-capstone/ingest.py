"""The ingestion job: turn the folder of documents into an index the app can search.

Run it once to build the index, and again whenever the documents change. It only does the
work that is needed: each document has a fingerprint (a short code computed from its text);
a document whose fingerprint hasn't changed keeps its pieces and vectors from last time.

For every new or changed document it:
1. cuts it into sections and small pieces (chunking.py);
2. checks every section for hidden instructions aimed at a chatbot, and keeps flagged ones out;
3. embeds the pieces with text-embedding-3-small.

Run from the repository root:  python 19-capstone/ingest.py"""
import hashlib
import json
import re
import time
from pathlib import Path

import numpy as np
from openai import OpenAI

from chunking import cut_document

client = OpenAI()
EMBEDDING_MODEL = "text-embedding-3-small"

HERE = Path(__file__).parent
DOCUMENTS_FOLDER = HERE.parent / "data" / "fernhill"
INDEX_FOLDER = HERE / "results" / "index"

# Words aimed at an assistant, not at a person. Free and instant: no model call.
SUSPICIOUS = [
    r"ignore (the |your |all |any )?(previous|earlier|old|above|prior)",
    r"\b(ai|assistant|chatbot)\b.{0,40}\b(reads?|answers?|tell|say)\b",
    r"do not (mention|reveal) this",
]

DATE_WORDS = ["Effective", "Published", "Released", "Last updated", "Issued", "Opened"]


def fingerprint(text):
    return hashlib.sha256(text.encode()).hexdigest()[:12]


def read_documents():
    documents = {}
    for path in sorted(DOCUMENTS_FOLDER.rglob("*.md")):
        if path.name == "README.md":
            continue  # the README describes the folder; it is not a document
        documents[str(path.relative_to(DOCUMENTS_FOLDER))] = path.read_text()
    return documents


def document_date(text):
    """The date a document gives near its top, such as 'effective 1 January 2026'."""
    for line in text.splitlines()[:12]:
        for word in DATE_WORDS:
            date = re.search(r"\d{1,2} [A-Z][a-z]+ \d{4}", line)
            if word in line and date:
                return f"{word.lower()} {date.group()}"
    return "no date"


def looks_like_instructions(text):
    for pattern in SUSPICIOUS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return True
    return False


def embed(texts):
    vectors = []
    for start in range(0, len(texts), 500):  # up to 500 pieces per request
        response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts[start:start + 500])
        vectors += [item.embedding for item in response.data]
    return np.array(vectors).reshape(len(texts), -1)


def load_old_index():
    """Last run's index, or an empty one the first time."""
    if not (INDEX_FOLDER / "documents.json").exists():
        return {}, [], [], np.zeros((0, 1536))
    with open(INDEX_FOLDER / "documents.json") as file:
        fingerprints = json.load(file)
    with open(INDEX_FOLDER / "sections.json") as file:
        sections = json.load(file)
    with open(INDEX_FOLDER / "pieces.json") as file:
        pieces = json.load(file)
    return fingerprints, sections, pieces, np.load(INDEX_FOLDER / "vectors.npy")


def main():
    documents = read_documents()
    old_fingerprints, old_sections, old_pieces, old_vectors = load_old_index()
    new = [s for s in documents if s not in old_fingerprints]
    changed = [s for s in documents if s in old_fingerprints and fingerprint(documents[s]) != old_fingerprints[s]]
    deleted = [s for s in old_fingerprints if s not in documents]
    print(f"Reading {len(documents)} documents from data/fernhill")
    print(f"  new {len(new)} · changed {len(changed)} · deleted {len(deleted)} · "
          f"unchanged {len(documents) - len(new) - len(changed)}")

    sections = []
    pieces = []
    vectors = []
    to_embed = []  # positions in `pieces` that still need a vector
    checked = 0
    flagged = []
    for source, text in documents.items():
        if source not in new and source not in changed:
            # Unchanged: copy its sections, pieces and vectors from last time.
            renumber = {}
            for number, section in enumerate(old_sections):
                if section["source"] == source:
                    renumber[number] = len(sections)
                    sections.append(section)
            for number, piece in enumerate(old_pieces):
                if piece["source"] == source:
                    pieces.append(dict(piece, section=renumber[piece["section"]]))
                    vectors.append(old_vectors[number])
            continue
        # New or changed: cut it, check it, and mark its pieces for embedding.
        doc_sections, doc_pieces = cut_document(source, text)
        date = document_date(text)
        renumber = {}
        for number, section in enumerate(doc_sections):
            checked += 1
            if looks_like_instructions(section["text"]):
                flagged.append(source)
                continue  # kept out of the index until a person has looked at it
            renumber[number] = len(sections)
            sections.append(dict(section, date=date))
        for piece in doc_pieces:
            if piece["section"] in renumber:
                to_embed.append(len(pieces))
                pieces.append(dict(piece, section=renumber[piece["section"]]))
                vectors.append(None)

    print(f"Cut into {len(sections):,} sections and {len(pieces):,} pieces")
    print(f"Checked {checked} new sections for hidden instructions: {len(flagged)} flagged")
    for source in flagged:
        print(f"  kept out, for a person to look at: {source}")

    started = time.time()
    if to_embed:
        fresh = embed([pieces[n]["text"] for n in to_embed])
        for n, vector in zip(to_embed, fresh):
            vectors[n] = vector
        print(f"Embedded {len(to_embed):,} pieces with {EMBEDDING_MODEL} in {time.time() - started:.1f} s")
    else:
        print("Nothing to embed: every document is unchanged")

    INDEX_FOLDER.mkdir(parents=True, exist_ok=True)
    with open(INDEX_FOLDER / "documents.json", "w") as file:
        json.dump({source: fingerprint(text) for source, text in documents.items()}, file, indent=1)
    with open(INDEX_FOLDER / "sections.json", "w") as file:
        json.dump(sections, file)
    with open(INDEX_FOLDER / "pieces.json", "w") as file:
        json.dump(pieces, file)
    np.save(INDEX_FOLDER / "vectors.npy", np.array(vectors).reshape(len(pieces), -1))
    print(f"Saved the index to {INDEX_FOLDER.relative_to(HERE)}")


main()
