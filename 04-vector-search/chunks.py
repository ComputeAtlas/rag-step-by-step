"""Load Fernhill's documents and cut them into chunks.
Each chunk gets two labels: the file it came from, and its document type."""
from pathlib import Path

FOLDER = Path("data/fernhill")

# Each folder holds one type of document.
FOLDER_TYPES = {
    "manuals": "manual",
    "parts": "parts",
    "policies": "policy",
    "release-notes": "release-note",
    "support": "ticket",
}
# The four files at the top of the folder get their type from this list.
TOP_FILE_TYPES = {
    "warranty-policy.md": "policy",
    "faq.md": "faq",
    "company.md": "company",
    "store-locations.md": "company",
}


def document_type(path):
    if path.parent == FOLDER:
        return TOP_FILE_TYPES[path.name]
    return FOLDER_TYPES[path.parent.name]


def split_into_chunks(text, max_words=150):
    """Cut a text into pieces of up to about max_words words, without splitting a paragraph."""
    chunks = []
    current = ""
    for paragraph in text.split("\n\n"):
        if current and len(current.split()) + len(paragraph.split()) > max_words:
            chunks.append(current)
            current = paragraph
        else:
            current = (current + "\n\n" + paragraph).strip()
    if current:
        chunks.append(current)
    return chunks


def load_chunks():
    chunks = []
    for path in sorted(FOLDER.rglob("*.md")):
        if path.name == "README.md":  # it describes the documents; it isn't one of them
            continue
        file = str(path.relative_to(FOLDER))
        for number, text in enumerate(split_into_chunks(path.read_text())):
            chunks.append({
                "id": f"{file}#{number}",  # e.g. "faq.md#3"
                "text": text,
                "file": file,
                "type": document_type(path),
            })
    return chunks
