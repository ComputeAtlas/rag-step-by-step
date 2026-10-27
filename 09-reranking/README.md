# 09 · Reranking: the second look

A search often finds the right chunk but ranks it too low, and the model only reads the top few. Reranking adds a
**second stage**: the first stage (here, the hybrid search from `08-hybrid-search/`) quickly finds 30 candidate chunks,
then a **reranker** reads the question together with each candidate, gives every pair a score, and keeps the best four.

A reranker is a **cross-encoder**: it reads the question and the chunk *together*, so it is more careful than an
embedding search (a **bi-encoder**, which turns the question and each chunk into numbers *separately*), but it cannot
prepare anything ahead of time, so it only reads a short list.

- `reranker.py` holds the two stages: `first_stage` (the hybrid search's best 30), `rerank` (score every
  `(question, chunk)` pair with `sentence_transformers.CrossEncoder`, sort, keep four) and `search_and_rerank`.
  The reranker is the open model `BAAI/bge-reranker-base` (about 1.1 GB, downloaded the first time). The other files
  import this one.
- `rerank_one.py` reranks one question and shows where each chunk was before (`was 10`). Try the default
  (`On what date was firmware v2.1 released?`), or pass your own question and the file that answers it.
- `answer_both.py` answers that question twice: from the first stage's top four and from the reranker's top four
  (two chat calls).
- `two_scores.py` scores the same two chunks both ways: with the embeddings (bi-encoder) and with the reranker
  (cross-encoder).
- `read_everything.py` times the reranker on the 30 candidates and on all 288 chunks, and works out what ten million
  chunks would take.
- `how_many.py` hands the reranker 4, 10, 20, 30 or 50 candidates and measures the hit rate and the time.
- `scoreboard.py` scores vector search, hybrid search and both of them followed by the reranker on the 80
  single-search test questions (hit rate, recall and MRR at 4). Pass another model name to try another reranker, for
  example `python 09-reranking/scoreboard.py cross-encoder/ms-marco-MiniLM-L6-v2`.
- `judge_answers.py` answers all 100 test questions from the four chunks the reranker keeps and grades them with the
  same judge and prompts as the baseline (200 chat calls). It also takes a model name. Answers are saved in
  `09-reranking/results/` (generated files, not part of the repository).

Build the baseline index first (`python 05-measuring-rag/build_index.py`). You need `openai`, `numpy`, `rank_bm25` and
`sentence-transformers` (`pip install openai numpy rank_bm25 sentence-transformers`) and your key in
`OPENAI_API_KEY`. The reranker runs on your own computer (on an Apple-silicon GPU, an NVIDIA GPU or the CPU).

```bash
python 09-reranking/rerank_one.py
python 09-reranking/answer_both.py
python 09-reranking/two_scores.py
python 09-reranking/read_everything.py
python 09-reranking/how_many.py
python 09-reranking/scoreboard.py
python 09-reranking/judge_answers.py
```

What we measured (Apple M4 Pro): a right file in the top 4 for 62 of 80 questions with vector search, 67 with hybrid
search, and 72 with hybrid search plus the reranker (reranking plain vector search also reaches 72). The 30 candidates
held a right file for all 80: a reranker can only re-sort what the first stage found. Reranking 30 chunks took about
0.64 s per question. Correct answers: 69 of 80 without the reranker, 70 with it (within the run-to-run noise of about
three). A smaller reranker, `cross-encoder/ms-marco-MiniLM-L6-v2` (about 90 MB, 7 times faster), also found 72 right
files, but correct answers fell to 60: it pushed down chunks that are mostly tables. Measure the answers, not only the
ranking.
