# 02 · Your first RAG, end to end

A complete, working RAG over all of Fernhill Bikes' documents, in two short programs.

- `build_index.py` runs once. It loads every Markdown file in `data/fernhill/` (skipping its `README.md`), cuts each
  one into chunks of 200 words, turns every chunk into an embedding (a list of 1,536 numbers) with OpenAI's
  `text-embedding-3-small` model, and saves the chunks and their vectors in `02-first-rag/index/`.
- `ask.py` runs for every question. It reads the saved chunks and vectors, embeds your question with the same model,
  scores every chunk with cosine similarity (a dot product, because OpenAI's vectors have length 1), keeps the 4 best,
  puts them in the prompt with their file names, and asks `gpt-5.4-mini` for the answer. It prints the 4 chunks it
  found (their scores and files: the sources), the answer and the time it took.
- `check_retrieval.py` is a first score. For the 80 test questions in `data/fernhill-questions.json` that one search
  can answer (it leaves out the 10 "unanswerable" ones and the 10 "whole-corpus" ones), it checks whether a right
  source file is among the 4 best chunks. It only searches, so it makes one embedding request and no chat calls.

You need the `openai` and `numpy` packages (`pip install openai numpy`) and your key in `OPENAI_API_KEY`.

```bash
python 02-first-rag/build_index.py      # once (again only if the documents change)
python 02-first-rag/ask.py              # then ask as many questions as you like
python 02-first-rag/check_retrieval.py
```

Try `How long is the battery warranty on a Fernhill e-bike?`, then
`Within how many hours of delivery must damage to a bike be reported?`: the second one is a real miss. The answer
(48 hours) is in `policies/shipping-and-delivery.md`, but none of the 4 chunks found contains it, so the model says
it doesn't know. With this simple version, a right file is in the top 4 for 62 of the 80 questions.

`02-first-rag/index/` holds generated files (`chunks.json`, `vectors.npy`); they are not part of the repository. Run
`build_index.py` to make them.
