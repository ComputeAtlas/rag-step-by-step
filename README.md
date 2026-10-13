# RAG, Step by Step

Code for the course **RAG, Step by Step**: how retrieval-augmented generation (RAG) works, and how to build it, one
small step at a time. Every lesson has its own folder. The code is written to be easy to read, even if you have only
just started with Python.

## Setup

1. Install Python 3.10 or newer.
2. Create a virtual environment and install the packages:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate        # on Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create an API key on the OpenAI platform (API keys page) and put it in an environment variable:

   ```bash
   export OPENAI_API_KEY="your-key-here"     # on Windows: set OPENAI_API_KEY=your-key-here
   ```

   Keep your key secret. Never commit it to Git.

4. Run every script from this folder (the repository root), for example:

   ```bash
   python 01-why-rag/ask.py
   ```

## Lessons

| Folder | Lesson |
|---|---|
| `01-why-rag/` | Why ChatGPT needs RAG |
| `02-first-rag/` | Your first RAG, end to end |
| `03-embeddings/` | Embeddings: turning text into searchable meaning |
| `04-vector-search/` | Vector search and vector databases |

## The data

`data/fernhill/` holds the documents of **Fernhill Bikes**, a made-up electric-bike company. Its documents were
written for this course, so no language model has seen them during training. That is what lets us show what RAG does.
