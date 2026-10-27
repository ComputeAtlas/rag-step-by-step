"""Search in two stages.

- First stage: hybrid search (vectors + keywords, merged with Reciprocal Rank Fusion)
  quickly finds 30 candidate chunks out of all 288.
- Second stage: a reranker (a cross-encoder) reads the question together with each
  candidate, gives each pair a score, and we keep the best four.

The other files in this folder import this one."""
import sys

from sentence_transformers import CrossEncoder

sys.path.append("08-hybrid-search")  # reuse the hybrid search from the hybrid-search lesson
from searches import chunks, hybrid_search

# An open reranker (about 1.1 GB), downloaded the first time you run this.
reranker = CrossEncoder("BAAI/bge-reranker-base")


def first_stage(question, how_many=30):
    """Fast but rough: the hybrid search's best 30 chunks."""
    return hybrid_search(question)[:how_many]


def rerank(question, candidates, how_many=4):
    """Slow but careful: score every (question, chunk) pair, best first."""
    pairs = []
    for score, number in candidates:
        pairs.append((question, chunks[number]["text"]))
    scores = reranker.predict(pairs)  # one score per pair: higher = more relevant
    results = []
    for (old_score, number), new_score in zip(candidates, scores):
        results.append((float(new_score), number))
    results.sort(reverse=True)  # highest score first
    return results[:how_many]


def search_and_rerank(question, how_many=4):
    return rerank(question, first_stage(question), how_many)
