# 01 · Why ChatGPT needs RAG

- `hello.py` is the first call: it asks the model a general question (what an electric bike is) and prints the
  answer.
- `ask.py` asks the model about Fernhill Bikes' battery warranty with no documents. The model has never seen this
  company's policy, so it either says it doesn't know or guesses.
- `ask_with_document.py` puts the warranty policy into the prompt and asks again. Now the model answers from the
  document.

```bash
python 01-why-rag/hello.py
python 01-why-rag/ask.py
python 01-why-rag/ask_with_document.py
```

The real answer, from `data/fernhill/warranty-policy.md`: 3 years or 800 full charge cycles, whichever comes first,
and 4 years if the bike is registered within 30 days.
