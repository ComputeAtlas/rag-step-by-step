"""Every Fernhill document, joined into one long text: the "put it all in the prompt" approach.

    python 17-rag-vs-long-context/whole_corpus.py      # how big is it?"""
from pathlib import Path

DATA_FOLDER = Path("data/fernhill")  # run from the repository root


def load_all_documents():
    """All 87 documents in one text, each one starting with the file it came from."""
    parts = []
    for path in sorted(DATA_FOLDER.rglob("*.md")):
        if path.name == "README.md":
            continue  # the README describes the data set; it is not a company document
        text = path.read_text()
        parts.append(f"From {path.relative_to(DATA_FOLDER)}:\n{text}")
    return parts


if __name__ == "__main__":
    documents = load_all_documents()
    everything = "\n\n".join(documents)
    print("Documents:", len(documents))
    print("Words:    ", f"{len(everything.split()):,}")
    print("Letters:  ", f"{len(everything):,}")
