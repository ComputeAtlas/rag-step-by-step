"""Small-to-big: search small pieces, but hand the model the bigger piece around them.

- parent-child: each document is cut into parents of up to 400 words, and each parent into
  children of up to 50 words. We search the children; for every child we find, the model
  gets its whole parent.
- sentence windows: we search single sentences; for every sentence we find, the model gets
  that sentence with the two sentences before it and the two after it.

The cutting is the recursive chunking of the chunking lesson (07-chunking/chunkers.py)."""
import sys
from pathlib import Path

sys.path.append("07-chunking")  # reuse the chunkers from the chunking lesson
from chunkers import recursive
from semantic import split_into_sentences

DOCUMENTS_FOLDER = Path("data/fernhill")


def load_documents():
    documents = []
    for path in sorted(DOCUMENTS_FOLDER.rglob("*.md")):
        if path.name == "README.md":
            continue  # the README describes the folder; it is not a document
        name = str(path.relative_to(DOCUMENTS_FOLDER))
        documents.append({"source": name, "text": path.read_text()})
    return documents


def make_parents_and_children(documents, parent_words=400, child_words=50):
    parents = []
    children = []
    for document in documents:
        for parent_text in recursive(document["text"], parent_words):
            parent_number = len(parents)
            parents.append({"source": document["source"], "text": parent_text})
            for child_text in recursive(parent_text, child_words):
                # Each child remembers which parent it came from.
                children.append({"source": document["source"], "text": child_text, "parent": parent_number})
    return parents, children


def make_sentence_windows(documents, before=2, after=2):
    sentences = []
    for document in documents:
        found = split_into_sentences(document["text"])
        for number, sentence in enumerate(found):
            window = found[max(0, number - before):number + after + 1]
            sentences.append({"source": document["source"], "text": sentence, "window": " ".join(window)})
    return sentences


def small_to_big(children, child_vectors, question_vector, how_many_parents=4):
    """Search the children; return the numbers of the first few different parents."""
    scores = child_vectors @ question_vector
    best_children = scores.argsort()[::-1]  # highest score first
    parent_numbers = []
    for child_number in best_children:
        parent = children[child_number]["parent"]
        if parent not in parent_numbers:  # two children of one parent: hand it over once
            parent_numbers.append(parent)
        if len(parent_numbers) == how_many_parents:
            break
    return parent_numbers
