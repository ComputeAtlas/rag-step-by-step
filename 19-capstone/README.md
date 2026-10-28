# 19 · Capstone: a complete "chat with your docs" app

Everything that earned its place on the course's scoreboard, in one small app you can run: a web page where you ask
Fernhill Bikes' documents a question, watch the answer arrive word by word, and click any citation to see the exact
section it came from.

**What's in it, and why** (each choice was measured on the 100 test questions in `data/fernhill-questions.json`):

- **Hybrid search** (meaning + keywords, merged with Reciprocal Rank Fusion): finds exact codes like `FH-2291-B` and
  different wordings alike.
- **Small-to-big**: search small pieces (up to 50 words), hand the model the whole section around each one (up to 400
  words).
- **A grounded prompt with citations**: numbered, dated passages and five rules (only the passages, cite every fact,
  use the policy in force, otherwise "I don't know. The documents don't say."), then a citation check with no model call.
- **Follow-up rewriting**, only when there is a chat before the question ("and on the Ridge?" becomes a question that
  stands on its own).
- From production: an **ingestion job** that only re-embeds documents whose fingerprint changed, and a free check
  that keeps sections with instructions aimed at a chatbot out of the index.

Left out, because they didn't move the score on these questions or cost much more than they gave: a reranker, rewriting
every question, contextual notes, an agent loop, GraphRAG, putting every document in the prompt. Add one back when
your own scoreboard says it helps.

## The files

- `chunking.py` cuts a document into sections and pieces (recursive splitting at natural breaks).
- `ingest.py` is the **ingestion job**: reads `data/fernhill/`, cuts, checks, embeds (`text-embedding-3-small`) and
  saves the index in `19-capstone/results/index/`. Run it again after the documents change: unchanged documents keep
  their vectors.
- `search.py` finds the four best sections for a question (hybrid search over the pieces, then small-to-big).
- `answer.py` holds everything the chat model (`gpt-5.4-mini`) does: rewrite a follow-up, stream the answer, and
  `check_citations`.
- `app.py` is the web server (Python's standard library only) and `index.html` the page. The answer is **streamed**:
  each piece goes to the browser as soon as the model writes it.
- `evaluate.py` runs the 100-question scoreboard through the app's own search and answer, graded by the course's judge
  (`judge.py`, unchanged). It lists the questions that were right last time and are wrong now (regressions), and exits
  with an error when the score falls below `MIN_CORRECT` (78), so an automatic check can stop a change that made the
  app worse. About 200 model calls.
- `ci/scoreboard.yml` is a sample GitHub Actions workflow that runs the ingestion job and the scoreboard. It is not
  active: copy it to `.github/workflows/` in your own repository and add your key as the secret `OPENAI_API_KEY`.

You need `openai`, `numpy` and `rank_bm25` (`pip install openai numpy rank_bm25`) and your key in `OPENAI_API_KEY`.

```bash
python 19-capstone/ingest.py          # build the index (about 11 seconds, under a cent)
python 19-capstone/app.py             # then open http://localhost:8000
python 19-capstone/evaluate.py        # the scoreboard (a few minutes)
```

What we measured (Apple M4 Pro, one run each, all 100 questions, the same judge): the simplest RAG (vector search on
200-word chunks, a plain prompt) 74 correct; with hybrid search 79; plus small-to-big 81; the finished app 82 (a second
run, nothing changed: 85). "I don't know" on questions the documents can answer: 16, 10, 8, then 4 of 90. On 20 follow-up
chats, rewriting took right answers from 8 to 14. An answer costs about $0.0017 and takes about 1.6 s; with streaming
the first words appear after about 1.25 s. A re-run of the same system moves by a few points, which is why the line
in `evaluate.py` sits a few points under the score.
