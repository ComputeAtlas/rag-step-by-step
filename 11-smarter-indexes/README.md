# 11 · Smarter indexes: contextual retrieval, parent-child, summaries

A chunk only knows the words inside it. When we cut it out of a long document, the title, the headings and the
sentences around it stay behind. The torque table of the Metro 300 owner's manual never says "Metro 300", so a
question about the Metro 300 finds it only in fifth place. Three ways to build a smarter index:

- **Contextual retrieval:** a model reads the whole document and the chunk, and writes one or two sentences that say
  where the chunk comes from. That note goes in front of the chunk, for the embedding and for the keyword search.
- **Small-to-big (parent-child):** cut each document into parents (up to 400 words) and each parent into children (up
  to 50 words). Search the children, but give the model their parents. **Sentence windows** are the extreme version:
  search single sentences, give the model each sentence with two before and two after.
- **A summary tree** (in the spirit of RAPTOR): a summary per document, a summary per group of documents and one
  summary of everything, searched together with the chunks, for broad questions.

Everything here starts from the same 288 chunks as the baseline, so build that index first with
`python 05-measuring-rag/build_index.py`. The chunkers come from `07-chunking/`.

- `add_context.py` writes the note for each of the 288 chunks with `gpt-5.4-mini` (288 chat calls, about 30 cents and
  6 minutes, run once) and embeds note and chunk together. It prints what it cost. The document goes first in the
  prompt, so OpenAI's prompt caching charges a tenth for the part it has already seen.
- `show_context.py` shows one chunk before and after: the torque table, its note, and its place in vector search
  without and with the note (one embedding request).
- `searches.py` holds the searches of the hybrid-search lesson (vector, keyword with BM25, Reciprocal Rank Fusion),
  written to work on the plain index or on the contextual one.
- `scoreboard.py` scores six setups on the 80 single-search test questions: vector, keyword and hybrid search, each
  without and with the notes. One embedding request, no chat calls.
- `small_to_big.py` makes parents and children and sentence windows, and holds `small_to_big()`, the search.
  `measure_small_to_big.py` compares children only, parents only, small-to-big and sentence windows: is a right file
  among the four pieces the model gets, and how many words does it read? Embedding requests only.
- `summary_tree.py` builds the summary tree (94 chat calls, about 10 cents, run once). `ask_tree.py` asks one broad
  question from the chunks only and from the tree. `broad_questions.py` answers the 10 test questions about all the
  support tickets both ways and grades them (40 chat calls).
- `judge_answers.py` answers all 100 test questions and grades them with the baseline's judge (200 chat calls per
  run): `context` (hybrid search on the chunks with notes), `children` or `small-to-big`. `answers.py` holds the
  answer and judge prompts.

Everything these scripts make is saved in `11-smarter-indexes/results/` (generated files, not part of the repository).

You need `openai`, `numpy` and `rank_bm25` and your key in `OPENAI_API_KEY`. Run from the repository root:

```bash
python 11-smarter-indexes/add_context.py
python 11-smarter-indexes/show_context.py
python 11-smarter-indexes/scoreboard.py
python 11-smarter-indexes/measure_small_to_big.py
python 11-smarter-indexes/summary_tree.py
python 11-smarter-indexes/ask_tree.py
python 11-smarter-indexes/broad_questions.py
python 11-smarter-indexes/judge_answers.py context
python 11-smarter-indexes/judge_answers.py children
python 11-smarter-indexes/judge_answers.py small-to-big
```

What we measured, a right file among the top 4, out of 80 single-search questions: vector search 62, with the notes
67; hybrid search 67, with the notes 69. 28 of the 59 chunks from the six bike manuals never name their bike; with the
notes, all 59 do. Small-to-big found 68 (children only 65, parents searched directly 70; sentence windows 61), and the
model reads about 1,360 words per question instead of about 140. Correct answers out of 80, with the baseline's judge: children only 63, small-to-big 70, hybrid search with the notes 66 (the baseline scored 61 and plain hybrid search 69; a re-run moves these by about three, so more right pages did not mean more right answers here). The summary tree answers "what do
customers contact support about?" from the summary of all 44 tickets, but it does not count: of the 10 questions that
count things across the tickets, chunks got 0 right and the tree 1. The models are not deterministic: run the judge
again and a few marks change.

On some Macs, NumPy prints `RuntimeWarning: divide by zero encountered in matmul` for the `@` lines. It is a known
false alarm of NumPy with Apple's Accelerate library; the scores are correct.
