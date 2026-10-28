"""Lost in the middle? The same 20 chunks in three orders: the chunk with the answer
first, in the middle (place 10) or last. Only the order changes.

For each single-search test question:
- the answer chunk = the best-ranked chunk from a file that answers it;
- the other 19 = the next best chunks from other files (close, but not the answer);
- questions are kept only if the model answers right from the answer chunk alone.
About 300 chat calls (answers and short grades)."""
import json

from prompts import ask, chunks, hybrid_search, plain_prompt

PLACES = {"first": 1, "middle": 10, "last": 20}

with open("data/fernhill-questions.json") as file:
    questions = [
        q for q in json.load(file)
        if q["category"] not in ("unanswerable", "whole-corpus")
    ]


def same_answer(question, expected, answer):
    """A short grade: does the answer give the reference fact?"""
    prompt = f"""Question: {question}
Reference answer: {expected}
System answer: {answer}

Does the system answer give the same fact as the reference answer? Reply only yes or no."""
    reply, tokens = ask(prompt)
    return reply.lower().startswith("yes")


tested = 0
right = {name: 0 for name in PLACES}
for q in questions:
    ranked = [chunks[number] for score, number in hybrid_search(q["question"])]
    answer_chunks = [c for c in ranked if c["source"] in q["sources"]]
    others = [c for c in ranked if c["source"] not in q["sources"]][:19]
    if not answer_chunks:
        continue
    answer_chunk = answer_chunks[0]

    alone, tokens = ask(plain_prompt(q["question"], [answer_chunk]))
    if not same_answer(q["question"], q["answer"], alone):
        continue  # the answer isn't in this one chunk, so the test would tell us nothing
    tested += 1

    marks = []
    for name, place in PLACES.items():
        context = others[:place - 1] + [answer_chunk] + others[place - 1:]
        answer, tokens = ask(plain_prompt(q["question"], context))
        ok = same_answer(q["question"], q["answer"], answer)
        right[name] += ok
        marks.append(f"{name} {'ok' if ok else 'WRONG'}")
    print(q["id"], " · ".join(marks))

print()
print(f"Right answers, {tested} questions, 20 chunks each")
for name, place in PLACES.items():
    print(f"  answer chunk {name:6s} (place {place:2d}): {right[name]} / {tested}")
