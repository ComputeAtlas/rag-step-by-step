from pathlib import Path

from chunkers import fixed_size, fixed_size_with_overlap, recursive, by_headings

text = Path("data/fernhill/warranty-policy.md").read_text()
print(f"warranty-policy.md: {len(text.split())} words\n")

ways = [
    ("fixed size", fixed_size),
    ("fixed size, 50 words overlap", fixed_size_with_overlap),
    ("recursive", recursive),
    ("by headings", by_headings),
]
for name, cut in ways:
    chunks = cut(text, 200)  # every way: up to 200 words a chunk
    print(f"{name}: {len(chunks)} chunks")
    for number, chunk in enumerate(chunks, start=1):
        words = chunk.split()
        print(f"  {number}. ({len(words)} words) {' '.join(words[:5])}")
        print(f"       ... {' '.join(words[-6:])}")
    print()
