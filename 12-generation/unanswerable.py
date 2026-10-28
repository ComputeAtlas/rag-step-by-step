"""The 10 test questions the documents cannot answer, asked three ways:
with no rules (bare), with the baseline's rule (plain), and with the grounded prompt.
How often does the model admit it doesn't know? 30 chat calls."""
import json

from prompts import SYSTEM_PROMPT, ask, bare_prompt, find_chunks, grounded_prompt, plain_prompt, says_i_dont_know

with open("data/fernhill-questions.json") as file:
    questions = [q for q in json.load(file) if q["category"] == "unanswerable"]

refused = {"bare": 0, "plain": 0, "grounded": 0}
for q in questions:
    found = find_chunks(q["question"])
    answers = {
        "bare": ask(bare_prompt(q["question"], found))[0],
        "plain": ask(plain_prompt(q["question"], found))[0],
        "grounded": ask(grounded_prompt(q["question"], found), SYSTEM_PROMPT)[0],
    }
    print(q["question"])
    for name, answer in answers.items():
        if says_i_dont_know(answer):
            refused[name] += 1
        short = " ".join(answer.split())[:110]
        print(f"  {name:9s} {short}")
    print()

print("Said they don't know, out of", len(questions))
for name, count in refused.items():
    print(f"  {name:9s} {count}")
