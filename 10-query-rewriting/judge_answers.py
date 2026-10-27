"""Answer the 20 follow-up questions the way a chat bot would (the chat so far, the last
message, four chunks), once with the chunks found by the last message alone and once with
the chunks found by the rewrite. gpt-5.4-mini grades each answer against the reference
answer, with the same grading prompt as the baseline. 80 chat calls.

Run scoreboard.py first: it saves the chunks each search found."""
import json
from pathlib import Path

from rewriters import ask
from searching import chunks

HERE = Path(__file__).parent
with open(HERE / "results" / "found.json") as file:
    found = json.load(file)
with open(HERE / "follow_up_questions.json") as file:
    follow_ups = json.load(file)
with open("data/fernhill-questions.json") as file:
    golden = {q["id"]: q for q in json.load(file)}


def passages_of(numbers):
    return "\n\n".join(f"From {chunks[n]['source']}:\n{chunks[n]['text']}" for n in numbers)


def answer(follow_up, numbers):
    history = "\n".join(f"{turn['role']}: {turn['text']}" for turn in follow_up["chat"])
    prompt = f"""You are Fernhill Bikes' support assistant. Answer the customer's last message
using only the passages below. If they don't contain the answer, say that you don't know.

{passages_of(numbers)}

{history}
customer: {follow_up['message']}"""
    return ask(prompt)


def judge(question, expected, numbers, system_answer):
    prompt = f"""You are grading a RAG system on two separate criteria.

Question: {question}
Reference answer: {expected}

Retrieved passages:
{passages_of(numbers)}

System answer: {system_answer}

Return JSON with three keys:
- "faithful": true if the system answer only states facts supported by the retrieved passages (or says it does not know when the passages lack the answer), false if it invents or extrapolates facts not in the passages.
- "correct": true ONLY if the system answer gives the same factual answer as the reference answer. If the reference answer is a specific fact (not "Not in the documents") and the system says "I don't know", "correct" MUST be false.
- "reason": one short sentence explaining both grades.
Return only raw JSON."""
    text = ask(prompt)
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(text)


rows = []
correct = {"last message only": 0, "rewritten": 0}
for f in follow_ups:
    q = golden[f["same_as"]]
    for way in correct:
        numbers = found[way][f["id"]]
        reply = answer(f, numbers)
        verdict = judge(q["question"], q["answer"], numbers, reply)
        correct[way] += bool(verdict["correct"])
        rows.append({"id": f["id"], "way": way, "answer": reply, "correct": bool(verdict["correct"]),
                     "reason": verdict["reason"]})

with open(HERE / "results" / "answers-follow-ups.json", "w") as file:
    json.dump(rows, file, indent=1)

print("Correct answers to the 20 follow-up questions (judged by gpt-5.4-mini)")
for way, count in correct.items():
    print(f"  search: {way:18s} {count:2d} / 20")
