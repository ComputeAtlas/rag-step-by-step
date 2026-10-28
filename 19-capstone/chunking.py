"""Cut a document into sections, and each section into small pieces.

We SEARCH the small pieces (a 50-word piece is about one thing, so it matches a question well),
but we HAND THE MODEL the whole section around a piece (up to 400 words), so it gets the context
too. This is "small-to-big". Sizes are counted in words.

The cutting is recursive: cut at the biggest natural break (a blank line, then a line break,
then the end of a sentence, then a space) that keeps every chunk small enough."""

SECTION_WORDS = 400
PIECE_WORDS = 50

# The natural breaks in a text, biggest first.
BREAKS = ["\n\n", "\n", ". ", " "]


def recursive(text, max_words, breaks=BREAKS):
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


def cut_document(source, text):
    """One document -> its sections, and the pieces of every section."""
    sections = []
    pieces = []
    for section_text in recursive(text, SECTION_WORDS):
        section_number = len(sections)
        sections.append({"source": source, "text": section_text})
        for piece_text in recursive(section_text, PIECE_WORDS):
            # Each piece remembers which section it came from.
            pieces.append({"source": source, "text": piece_text, "section": section_number})
    return sections, pieces
