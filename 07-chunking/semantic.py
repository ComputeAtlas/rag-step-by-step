"""Semantic chunking: start a new chunk where the meaning changes.

Each sentence gets an embedding. We compare every sentence with the one before it.
Where that similarity drops the most, the topic has probably changed, so we cut there.
"""
import re

import numpy as np
from openai import OpenAI

client = OpenAI()


def split_into_sentences(text):
    """Headings, table rows and list items each on their own; prose cut after each full stop."""
    sentences = []
    for block in text.split("\n\n"):  # a blank line separates paragraphs, tables and lists
        lines = []
        for line in block.split("\n"):
            line = line.strip()
            if not line:
                continue
            starts_new_item = line.startswith(("#", "|", "-", "**")) or line[:1].isdigit()
            if lines and not starts_new_item:
                lines[-1] += " " + line  # the same sentence, wrapped onto the next line
            else:
                lines.append(line)
        for line in lines:
            # Cut after ". ", "? " or "! " when a word ends there (not after "1." of a numbered list).
            sentences += re.split(r"(?<=\w\w[.!?])\s+", line)
    return sentences


def embed(texts):
    vectors = []
    for start in range(0, len(texts), 500):  # at most 500 texts per request
        response = client.embeddings.create(model="text-embedding-3-small", input=texts[start:start + 500])
        vectors += [item.embedding for item in response.data]
    return np.array(vectors)


def neighbour_similarities(vectors):
    """How close each sentence is in meaning to the one before it (one score per pair)."""
    scores = []
    for i in range(1, len(vectors)):
        scores.append(float(np.dot(vectors[i - 1], vectors[i])))
    return scores


def semantic_chunks(sentences, vectors, drop_percent=5, max_words=200):
    """Cut at the biggest drops in meaning: the lowest `drop_percent` of the neighbour scores
    in this document. Also cut when a chunk would grow past max_words."""
    scores = neighbour_similarities(vectors)
    if not scores:
        return [" ".join(sentences)]
    cut_below = np.percentile(scores, drop_percent)
    chunks = []
    current = [sentences[0]]
    for i in range(1, len(sentences)):
        too_long = len(" ".join(current + [sentences[i]]).split()) > max_words
        if scores[i - 1] <= cut_below or too_long:
            chunks.append(" ".join(current))
            current = []
        current.append(sentences[i])
    chunks.append(" ".join(current))
    return chunks
