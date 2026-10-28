"""Four questions through the bot with a semantic cache in front of it.

A hit skips the search and the model: only the question's embedding is needed.

    python 18-rag-in-production/cache_demo.py"""
from pipeline import answer, embed, load_baseline_index
from semantic_cache import THRESHOLD, look_up, remember
from tracer import end_span, new_trace, print_trace, start_span

questions = [
    "How long is the battery warranty on a new bike?",
    "What's the warranty on the battery of a new bike?",     # same meaning, other words
    "How long is the motor warranty on a new bike?",         # similar words, another answer
    "For how many years is a new bike's battery covered?",   # same meaning, fewer shared words
]

index = load_baseline_index()
answer("warm-up", index)  # connect to the API once before timing
role = "customer"

for question in questions:
    trace = new_trace(question)
    started = start_span()
    question_vector = embed(question, trace)
    end_span(trace, "embed question", started)

    started = start_span()
    entry, similarity = look_up(question_vector, role)
    end_span(trace, "cache look-up", started, f"best match {similarity:.2f}")

    print("Question:", question)
    if entry:
        print(f"CACHE HIT (similarity {similarity:.2f}, threshold {THRESHOLD})")
        print("  remembered from:", entry["question"])
        text = entry["answer"]
    else:
        print(f"cache miss (best similarity {similarity:.2f}, threshold {THRESHOLD})")
        text, found, trace = answer(question, index, role, trace, question_vector)
        remember(question_vector, question, text, role)
    print_trace(trace)
    print("Answer:", text)
    print()
