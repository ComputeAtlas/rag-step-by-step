# 17 · RAG vs long context vs fine-tuning

Models can now read a whole book in one prompt. So why search at all? This folder answers the same questions two
ways and measures both:

- **RAG:** the hybrid search from `08-hybrid-search/` finds the best four chunks, and the model answers from them;
- **long context:** all 87 Fernhill documents (about 70,600 tokens) go into the prompt, and the model answers from
  everything.

It also shows **prompt caching**: when many prompts start with exactly the same text (here, all the documents), OpenAI
keeps the model's work on that beginning for a few minutes and bills it at a tenth of the price. Only an identical
beginning counts, so put the fixed part first and the question last.

- `whole_corpus.py` joins every document into one text and prints its size.
- `two_ways.py` holds the two ways (`ask_with_rag`, `ask_with_everything`, and `ask_with_everything_question_first`,
  the same prompt with the question at the top, which cannot be cached). Each returns the answer, the time, the tokens
  (and how many were cached) and the cost, from the prices at the top of the file. The other files import this one.
- `ask_one.py` asks one question both ways (pass your own question in quotes).
- `cache_demo.py` sends all the documents four times and prints the cached tokens, the time and the cost of each call.
- `compare.py` answers 35 test questions (the first five of each of the seven kinds) three ways and saves everything in
  `17-rag-vs-long-context/results/` (generated files, not part of the repository). It sends about 70,000 tokens in 70
  of its 105 calls: about two dollars.
- `grade.py` grades those answers with a second model and prints correct answers, time and cost per question.

Fine-tuning is explained in the lesson, not run here.

Build the baseline index first (`python 05-measuring-rag/build_index.py`). You need `openai`, `numpy` and `rank_bm25`
and your key in `OPENAI_API_KEY`.

```bash
python 17-rag-vs-long-context/whole_corpus.py
python 17-rag-vs-long-context/ask_one.py
python 17-rag-vs-long-context/cache_demo.py
python 17-rag-vs-long-context/compare.py
python 17-rag-vs-long-context/grade.py
```

What we measured (gpt-5.4-mini, Apple M4 Pro over the internet, one run): both ways answered **28 of 35** questions
correctly. The median wait was 1.49 s with RAG (0.41 s of it the search) and 1.13 s with everything in the prompt.
The cost per question was $0.0009 with RAG, $0.0055 with everything and the cache (about 6 times RAG), and $0.053
without the cache (about 60 times). Reading everything fixed a question RAG got wrong (the latest firmware version),
but it picked a look-alike table row for a torque value that RAG got right, and neither way could count across the 44
support tickets. Long context works for a small set of documents that rarely changes; RAG keeps working when the
documents are too many to fit, change often, or when every question has to be cheap.
