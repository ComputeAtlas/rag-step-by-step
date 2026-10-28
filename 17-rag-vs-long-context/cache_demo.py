"""Prompt caching, shown with four calls that each send all 87 documents.

1. the first call: nothing is cached yet;
2. the same question again: the documents at the start were read a moment ago, so they are cached;
3. a different question: the start of the prompt is still the same, so it is still cached;
4. the question moved to the top: the prompt now starts differently, so nothing is cached.

    python 17-rag-vs-long-context/cache_demo.py"""
from two_ways import ask_with_everything, ask_with_everything_question_first

calls = [
    ("1. first call", ask_with_everything, "What is the latest Fernhill firmware version?"),
    ("2. same question", ask_with_everything, "What is the latest Fernhill firmware version?"),
    ("3. new question", ask_with_everything, "Which courier partner delivers Fernhill bikes?"),
    ("4. question first", ask_with_everything_question_first, "Which courier partner delivers Fernhill bikes?"),
]

print(f"{'call':20s} {'tokens in':>10s} {'cached':>8s} {'seconds':>8s} {'cost':>9s}")
for title, way, question in calls:
    result = way(question)
    print(f"{title:20s} {result['input_tokens']:>10,} {result['cached_tokens']:>8,} "
          f"{result['seconds']:>8.1f} {'$' + format(result['dollars'], '.4f'):>9s}")
