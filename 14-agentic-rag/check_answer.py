"""Self-checking: before the answer goes out, one more model call checks it.

1. the agent answers the question
2. a check reads the question, the passages the agent read, and the answer:
   is every fact in the passages (supported)? does it answer the whole question (complete)?
3. if the check fails, the agent tries once more, with the check's note

Pass your own question to try another."""
import json
import sys

from openai import OpenAI

from agent import run_agent, show_steps, wrap
from search_tool import as_text

client = OpenAI()
MODEL = "gpt-5.4-mini"

DEFAULT = ("A customer returns a new Ridge 500 within 30 days and Fernhill collects it by courier. "
           "How much is refunded if the bike cost the list price?")


def check_answer(question, read, answer):
    prompt = f"""Question: {question}

Passages:
{as_text(read)}

Answer: {answer}

Check the answer. Return only JSON with three keys:
- "supported": true if every fact in the answer is in the passages
- "complete": true if it answers the whole question (a number when the question asks for one)
- "problem": one short sentence about what is wrong or missing, or "" if nothing is"""
    response = client.responses.create(model=MODEL, input=prompt)
    text = response.output_text.strip()
    if text.startswith("```"):  # the model sometimes wraps JSON in a code block
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(text)


def show_check(verdict):
    print(f"CHECK   supported: {verdict['supported']}   complete: {verdict['complete']}")
    if verdict["problem"]:
        print(wrap(f"        {verdict['problem']}", 8))


question = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
result = run_agent(question)
show_steps(question, result)
print()
verdict = check_answer(question, result["read"], result["answer"])
show_check(verdict)

if not (verdict["supported"] and verdict["complete"]):
    print()
    print("The check failed: one more try, with its note.")
    print()
    retry = f"{question}\n(A check of a first answer said: {verdict['problem']})"
    result = run_agent(retry)
    show_steps(question, result)
    print()
    show_check(check_answer(question, result["read"], result["answer"]))
