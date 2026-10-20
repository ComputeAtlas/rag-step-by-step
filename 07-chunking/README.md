# 07 · Chunking: how you cut decides what you find

Five ways to cut Fernhill's documents into chunks, and a test that shows what each one is worth.

- `chunkers.py` holds the ways to cut, every size counted in words: `fixed_size()` (count off 200 words, cut),
  `fixed_size_with_overlap()` (each chunk repeats the last 50 words of the one before), `recursive()` (cut at the
  biggest natural break that keeps chunks small enough: paragraphs, then lines, then sentences, then words) and
  `by_headings()` (one chunk per Markdown section; a long section is cut at its own natural breaks).
- `semantic.py` is semantic chunking: it embeds every sentence, compares each one with the one before it, and cuts at
  the biggest drops in meaning (the lowest 5% of those scores in each document).
- `show_chunks.py` cuts `warranty-policy.md` the four ways and prints where each chunk starts and ends (no API calls).
- `show_semantic.py` runs semantic chunking on the same document and prints the scores and the two cuts it chose.
- `measure_chunking.py` is the test. For the 80 test questions that one search can answer, it checks whether a right
  source file is among the 4 best chunks, for each way to cut, and for recursive chunks of three sizes (with how many
  words the model would have to read). It only makes embedding requests (a cent or two), no chat calls.
- `ask.py` answers one question with the documents cut one way: `python 07-chunking/ask.py fixed`, `recursive` or
  `headings`.

You need the `openai` and `numpy` packages and your key in `OPENAI_API_KEY`. Run from the repository root:

```bash
python 07-chunking/show_chunks.py
python 07-chunking/show_semantic.py
python 07-chunking/measure_chunking.py
python 07-chunking/ask.py recursive
```

Try `What is part FH-6290-A?` with `fixed`, then with `recursive`. With fixed-size chunks, that part's table row is
cut in two (`FH-6290-A | Speed` ends one chunk, `sensor with wheel magnet` starts the next) and the model says it
doesn't know. With recursive chunks the row stays whole, it is found first, and the answer is right.

What we measured (a right file in the top 4, out of 80): fixed size 62, fixed size with overlap 62, recursive 71,
by headings 69, by meaning 67. Recursive at three sizes: up to 50 words 65, up to 200 words 71, up to 800 words 71
(but the model reads about 2,000 words per question instead of about 600). Small differences of two or three
questions are within the noise of a test this size; run it again and one or two can change.

On some Macs, NumPy prints `RuntimeWarning: divide by zero encountered in matmul` for the `@` lines. It is a known
false alarm of NumPy with Apple's Accelerate library; the scores are correct.
