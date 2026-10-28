"""Plain RAG on a global question: hybrid search (from the hybrid-search lesson) finds the
four best chunks, and the model answers from them. One embedding request and one chat call.
Usage: python 15-graphrag/plain_rag.py "What do customers complain about most?" """
import sys

sys.path.append("08-hybrid-search")  # reuse the hybrid search from the hybrid-search lesson
from searches import chunks, hybrid_search

from answers import ask_rag

question = sys.argv[1] if len(sys.argv) > 1 else "What do customers complain about most?"
found = [chunks[number] for score, number in hybrid_search(question)[:4]]

print("Question:", question)
print("The four chunks it found:")
for chunk in found:
    print("  ", chunk["source"])
print("Answer:", ask_rag(question, found))
