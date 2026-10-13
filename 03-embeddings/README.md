# 03 · Embeddings: turning text into searchable meaning

An embedding is a list of numbers that captures what a text means. Texts with similar meanings get similar lists, so a
computer can find the right page even when it shares no words with the question.

- `embed_one.py` asks OpenAI's `text-embedding-3-small` model for the embedding of one question and prints how many
  numbers came back (1536) and the first five.
- `compare.py` embeds five short pages from Fernhill Bikes and your question, scores each page against the question
  with cosine similarity (a dot product, because OpenAI's vectors have length 1) and prints them, best first.
  Try `How do I fix a flat?`: the tyre puncture page wins, although it shares no word with the question.
- `small_vs_large.py` runs the same comparison with `text-embedding-3-small` and `text-embedding-3-large`. Try a
  question in another language, for example `¿Cómo arreglo un pinchazo?`.
- `wrong_model.py` shows a common mistake: the page embedded by one model, the question by another. The lists have
  different lengths, so NumPy stops with an error.
- `wrong_model_same_size.py` shows the quiet version of that mistake: both lists have 1536 numbers, so nothing
  complains, but the scores are meaningless and the right page comes last.

You need the `openai` and `numpy` packages (`pip install openai numpy`) and your key in `OPENAI_API_KEY`.

```bash
python 03-embeddings/embed_one.py
python 03-embeddings/compare.py
python 03-embeddings/small_vs_large.py
python 03-embeddings/wrong_model.py
python 03-embeddings/wrong_model_same_size.py
```

The rule to remember: embed your documents and your questions with the same model. If you change the model, embed
every document again.
