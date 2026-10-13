# 04 · Vector search and vector databases

Comparing a question with every chunk (brute force) is exact and simple, but its time grows with the number of chunks.
An index such as HNSW finds almost the same top ten in a fraction of the time. A vector database keeps the vectors on
disk with their text and labels, lets you add, update and delete them, and filters by labels while it searches.

**The speed tests** use made-up (synthetic) vectors, because embedding a million real chunks would take hours and cost
money. They need about 3 GB of memory.

- `made_up_vectors.py` makes the vectors: a million of them, 384 numbers each, bunched into topics, each of length 1.
- `brute_force.py` times brute force for 1,000, 10,000, 100,000 and 1,000,000 vectors. Twice the vectors, twice the time.
- `hnsw_vs_brute_force.py` builds an HNSW index (with `hnswlib`) over the million vectors and compares it with brute
  force: time per question, and recall@10 (how many of the true ten closest it found) for four settings of `ef`.
  Building the index takes a minute or two.

**The Fernhill demo** stores Fernhill's documents in Chroma, a vector database that runs inside your Python program.

- `chunks.py` loads every document (not the README), cuts it into chunks of up to about 150 words and gives each chunk
  two labels: its file and its document type (manual, parts, policy, release-note, ticket, faq, company).
- `build_db.py` embeds the chunks with OpenAI's `text-embedding-3-small` and stores them, with their text and labels, in
  a Chroma database in the folder `chroma_db` (created in the folder you run it from).
- `search.py` opens that database and asks for the three chunks closest to a question.
- `search_policies.py` asks the same question, but only searches chunks whose type is `policy` (a metadata filter).

You need `openai`, `numpy`, `hnswlib` and `chromadb` (`pip install openai numpy hnswlib chromadb`) and your key in
`OPENAI_API_KEY`.

```bash
python 04-vector-search/brute_force.py
python 04-vector-search/hnsw_vs_brute_force.py
python 04-vector-search/build_db.py
python 04-vector-search/search.py
python 04-vector-search/search_policies.py
```

The rule to remember: brute force is exact but grows with your data; an index is fast but approximate, so measure its
recall on your own data and tune it (in HNSW, a bigger `ef` finds more of the true top ten, a little more slowly).
