"""Four ways to cut a document into chunks.

Every size here is counted in words, like the rest of the course.
(Libraries often count characters or tokens instead. The ideas are the same.)
"""


def fixed_size(text, size=200):
    """Count off `size` words, cut, start the next chunk."""
    words = text.split()
    chunks = []
    for start in range(0, len(words), size):
        chunks.append(" ".join(words[start:start + size]))
    return chunks


def fixed_size_with_overlap(text, size=200, overlap=50):
    """Each chunk repeats the end of the one before it."""
    words = text.split()
    step = size - overlap  # where the next chunk starts
    chunks = []
    for start in range(0, len(words), step):
        chunks.append(" ".join(words[start:start + size]))
        if start + size >= len(words):
            break  # this chunk already reaches the end
    return chunks


# The natural breaks in a text, biggest first: a blank line (a new paragraph),
# a line break, the end of a sentence, and a space between two words.
BREAKS = ["\n\n", "\n", ". ", " "]


def recursive(text, max_words=200, breaks=BREAKS):
    """Cut at the biggest break that keeps chunks small enough."""
    if len(text.split()) <= max_words:
        return [text.strip()] if text.strip() else []

    this_break = breaks[0]
    pieces = text.split(this_break)
    chunks = []
    current = ""
    for piece in pieces:
        if current:
            joined = current + this_break + piece
        else:
            joined = piece
        if len(joined.split()) <= max_words:
            current = joined  # it still fits: keep filling
            continue
        if current.strip():
            chunks.append(current.strip())  # the chunk is full
        if len(piece.split()) > max_words:
            # Too long on its own: cut it at the next break.
            chunks += recursive(piece, max_words, breaks[1:])
            current = ""
        else:
            current = piece
    if current.strip():
        chunks.append(current.strip())
    return chunks


def by_headings(text, max_words=200):
    """One chunk per section: a heading and everything under it.
    A section longer than max_words is cut at its own natural breaks."""
    sections = []
    lines = []
    for line in text.split("\n"):
        if line.startswith("#") and lines:  # a Markdown heading starts a new section
            sections.append("\n".join(lines))
            lines = []
        lines.append(line)
    sections.append("\n".join(lines))

    chunks = []
    for section in sections:
        chunks += recursive(section, max_words)
    return chunks
