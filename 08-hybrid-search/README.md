# 08 · Hybrid search: when keywords beat vectors

Vector search finds chunks with the same **meaning** as your question. It is weak at exact strings: part numbers,
error codes, names and rare words. Keyword search (BM25) finds the **exact words**, but misses meaning. Hybrid search
runs both and merges the two ranked lists with **Reciprocal Rank Fusion** (each list gives a chunk 1 / (60 + its place);
the scores themselves are never added).

Everything here searches the same 288 chunks as the baseline, so the vector column is the baseline score. Build that
index first with `python 05-measuring-rag/build_index.py`.

- `searches.py` holds the three searches: `vector_search`, `keyword_search` (with `words`, the BM25 word splitting:
  lower case, part numbers kept whole, small words dropped) and `fuse` / `hybrid_search`. The other files import it.
- `compare.py` searches one question three ways and prints the four best chunks of each, plus where the page with the
  answer ended up. Try the default (`What fits part FH-2291-B?`), then
  `python 08-hybrid-search/compare.py "How do I fix a flat?" support/ticket-1006-ridge-puncture.md`.
- `similar_codes.py` shows why vectors blur part numbers: to the embedding model, `FH-2291-B` is far closer to its
  twin `FH-2219-B` than to the words "battery pack".
- `how_rare.py` counts how many chunks contain a word (rare words count for more in BM25).
- `add_scores.py` shows the common mistake: adding a cosine score (0 to 1) to a BM25 score (up to 30 or more) just
  gives you the keyword ranking again.
- `scoreboard.py` scores vector, keyword and hybrid search on the 80 single-search test questions (hit rate, recall and
  MRR at 4, by category). One embedding request per question, no chat calls.
- `tune_mix.py` gives the keyword list more or less weight in the fusion and measures each setting.
- `judge_answers.py` answers all 100 test questions from the four chunks hybrid search finds and grades them with the
  same judge and prompts as the baseline (200 chat calls). Pass `vector` to re-check the baseline. Answers are saved in
  `08-hybrid-search/results/` (generated files, not part of the repository).

You need `openai`, `numpy` and `rank_bm25` (`pip install openai numpy rank_bm25`) and your key in `OPENAI_API_KEY`.

```bash
python 08-hybrid-search/compare.py
python 08-hybrid-search/similar_codes.py
python 08-hybrid-search/how_rare.py
python 08-hybrid-search/add_scores.py
python 08-hybrid-search/scoreboard.py
python 08-hybrid-search/tune_mix.py
python 08-hybrid-search/judge_answers.py
```

What we measured: a right file in the top 4 for 62 of 80 questions with vector search, 66 with keyword search and 67
with hybrid search. On the 7 questions that name a part number, keyword search found all 7 and vector search 4. Correct
answers went from 61 to 69 of 80 (a re-run of plain vector search scored 64, so a few points are run-to-run noise).
