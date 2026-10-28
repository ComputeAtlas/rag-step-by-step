"""Answer one question and print its trace: every step, how long it took, and its share.

    python 18-rag-in-production/trace_one.py
    python 18-rag-in-production/trace_one.py "How do I fix a flat?" """
import sys

from pipeline import answer, load_baseline_index
from tracer import print_trace

question = sys.argv[1] if len(sys.argv) > 1 else "How long is the battery warranty on a new bike?"
index = load_baseline_index()

answer(question, index)  # a warm-up call, so the trace below doesn't include connecting to the API
text, found, trace = answer(question, index)

print("Question:", question)
print_trace(trace)
print("Answer:", text)
