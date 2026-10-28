# 15 · GraphRAG: questions about everything at once

Some questions are **local**: the answer sits in one place ("What torque for the Metro's front axle nuts?").
Others are **global**: the answer is spread over the whole collection ("What do customers complain about most?").
Plain RAG hands the model the four closest chunks, which is a keyhole view of a global question.

GraphRAG does the reading once, before anyone asks:

1. **Extraction:** a model reads every chunk and lists the things in it (**entities**: bikes, parts, error codes,
   problems, support tickets, people) and how they are linked (**relations**).
2. **Merging:** the same name from many chunks becomes one entity that keeps every description and every document
   that mentions it; a link seen again gets stronger. That is the **knowledge graph**.
3. **Communities:** the Leiden algorithm finds groups of entities that link mostly to each other.
4. **Community reports:** a model writes a short report on each group (what it is about, and what comes up in the
   most documents and support tickets).

Then a question is answered in one of two ways:

- **Global search** (map-reduce): every report answers the question with points and a 0-100 importance score (map),
  and the best points are combined into one answer (reduce).
- **Local search**: start from the entities the question names, and read their links, their community's report and
  the chunks that mention them.

The files (run them in this order; the first three build the index and save it in `15-graphrag/results/`, which is
not part of the repository):

- `model.py` holds the chat model (`gpt-5.4-mini`) and counts what the calls cost. The other files import it.
- `extract_graph.py` reads the 288 chunks of the baseline index and saves what the model found (288 chat calls). If
  it stops halfway, run it again: it carries on.
- `build_graph.py` merges everything into one graph with `networkx` and finds its communities with Leiden
  (no model calls).
- `summarize_communities.py` writes a report on every community of 3 or more entities (one chat call each).
- `show_extraction.py` prints what the model found in one chunk (default: chunk 203, a support ticket), and
  `show_report.py` prints one community's report (default: community 2). No model calls.
- `global_search.py` answers a global question by map-reduce over the reports. Try the default
  (`What do customers complain about most?`) or pass your own question.
- `local_search.py` answers a question about one thing. Try the default
  (`What should owners know about the FH-2310-A charger?`).
- `plain_rag.py` answers the same global question with plain RAG (the hybrid search from `08-hybrid-search/`, four
  chunks), for comparison.
- `scoreboard.py` answers the 10 whole-corpus test questions with global search and grades them with the baseline's
  judge (about 290 chat calls); `answers.py` holds the answering prompt and the judge.

Build the baseline index first (`python 05-measuring-rag/build_index.py`). You need `openai`, `numpy`, `rank_bm25` and
`networkx` 3.7 or newer (for `leiden_communities`) (`pip install openai numpy rank_bm25 networkx`) and your key in
`OPENAI_API_KEY`.

```bash
python 15-graphrag/extract_graph.py
python 15-graphrag/build_graph.py
python 15-graphrag/summarize_communities.py
python 15-graphrag/show_extraction.py 203
python 15-graphrag/show_report.py 2
python 15-graphrag/global_search.py
python 15-graphrag/local_search.py
python 15-graphrag/plain_rag.py
python 15-graphrag/scoreboard.py
```

What we measured (`gpt-5.4-mini`, October 2026): extraction read 288 chunks in 12.7 minutes for $0.91 and found
3,103 entity mentions, which merged into 1,231 entities and 2,142 relations. Leiden found 150 communities; 27 have 3
or more entities and hold 89% of them. The 27 reports took under a minute and $0.06. The whole graph index cost $0.97,
about 700 times the embeddings of the same chunks ($0.0014). Plain RAG answered "What do customers complain about
most?" with "I don't know"; global search answered "battery and range issues, with charging problems close behind",
which matches the tickets (battery range 9 of 44, charging 6), but it also claimed the Metro 300 leads in support
tickets (the Ridge 500 does, 16). One global question took 28 calls, 43 seconds and $0.02. On the 10 whole-corpus
test questions, global search got 1 right (the baseline 0, hybrid search 2): nine of them need an exact count of
tickets, and community reports describe themes, not every ticket. GraphRAG is for questions about themes; for exact
counts, keep the data in a table and count.

Names matter: the same thing under two names becomes two entities (we found 30 pairs that differ only by a plural
"s", such as "brake lever" and "brake levers"). Tell the model how to write names, and merge look-alikes after.

Microsoft's GraphRAG (Edge et al., 2024) builds communities at several levels; LightRAG (Guo et al., 2024) keeps the
graph but skips the communities, which makes questions and updates cheaper.
