"""How many of the 288 chunks contain a word? Rare words count for much more in BM25.

    python 08-hybrid-search/how_rare.py
    python 08-hybrid-search/how_rare.py puncture flat"""
import sys

from searches import chunks, words

to_check = sys.argv[1:] or ["battery", "part", "fits", "fh-2291-b", "assisting", "helping"]

chunk_words = [set(words(chunk["text"])) for chunk in chunks]
for word in to_check:
    count = 0
    for found in chunk_words:
        if word in found:
            count += 1
    print(f"  {word:10s} in {count:3d} of {len(chunks)} chunks")
