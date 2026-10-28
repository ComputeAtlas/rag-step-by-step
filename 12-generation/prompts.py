"""The prompt templates: the same passages, handed to the model in different ways.

- bare_prompt: just the passages and the question, no rules at all.
- plain_prompt: the baseline's template (answer only from the passages, or say you don't know).
- grounded_prompt: a system prompt with the rules, plus numbered passages with their dates,
  so the model can cite them and can tell an old document from a new one.

Also: the hybrid search from 08-hybrid-search, and ask(), which sends a prompt to the model."""
import re
import sys
from pathlib import Path

from openai import OpenAI

sys.path.insert(0, "08-hybrid-search")  # reuse lesson 08's search (run from the repository root)
from searches import chunks, hybrid_search  # noqa: E402

client = OpenAI()
MODEL = "gpt-5.4-mini"
DATA_FOLDER = Path("data/fernhill")


def find_chunks(question, how_many=4):
    """The best chunks for a question, from hybrid search."""
    return [chunks[number] for score, number in hybrid_search(question)[:how_many]]


def bare_prompt(question, found):
    passages = "\n\n".join(f"From {c['source']}:\n{c['text']}" for c in found)
    return f"""{passages}

Question: {question}"""


def plain_prompt(question, found):
    passages = "\n\n".join(f"From {c['source']}:\n{c['text']}" for c in found)
    return f"""Answer the question using only the passages below.
If they don't contain the answer, say that you don't know.

{passages}

Question: {question}"""


SYSTEM_PROMPT = """You answer questions about Fernhill Bikes for its customers.

Rules:
1. Use only the numbered passages. Never use what you know from anywhere else.
2. After every fact, cite the passage it comes from, like [2].
3. You may combine facts from several passages and do simple arithmetic with them.
4. If passages disagree, say so in one sentence. Then use the one that applies:
   for a policy, the version in force on the purchase date; otherwise the newest document.
5. If the passages do not contain the answer, reply exactly: I don't know. The documents don't say.
Keep the answer short."""

DATE_WORDS = ["Effective", "Published", "Released", "Last updated", "Issued", "Opened"]


def document_date(source):
    """The date a document gives near its top, such as 'effective 1 January 2026'."""
    text = (DATA_FOLDER / source).read_text()
    for line in text.splitlines()[:12]:
        for word in DATE_WORDS:
            date = re.search(r"\d{1,2} [A-Z][a-z]+ \d{4}", line)
            if word in line and date:
                return f"{word.lower()} {date.group()}"
    return "no date"


def grounded_prompt(question, found):
    passages = []
    for number, c in enumerate(found, start=1):
        heading = f"[{number}] {c['source']} ({document_date(c['source'])})"
        passages.append(heading + "\n" + c["text"])
    return "Passages:\n\n" + "\n\n".join(passages) + f"\n\nQuestion: {question}"


def ask(prompt, system_prompt=None):
    """Send one prompt to the model. Returns the answer and the tokens it used."""
    response = client.responses.create(model=MODEL, instructions=system_prompt, input=prompt)
    tokens = {"in": response.usage.input_tokens, "out": response.usage.output_tokens}
    return response.output_text.strip(), tokens


def says_i_dont_know(answer):
    answer = answer.lower().replace("’", "'")
    return "don't know" in answer or "do not know" in answer
