"""Everything the chat model does in the app:

- rewrite_follow_up: turn a follow-up like "and on the Ridge?" into a question that stands alone
  (only when there is a chat before it);
- stream_answer: answer from the numbered sections, word by word as the model writes;
- check_citations: check the finished answer's citations, with no model call."""
import re

from openai import OpenAI

client = OpenAI()
CHAT_MODEL = "gpt-5.4-mini"

SYSTEM_PROMPT = """You answer questions about Fernhill Bikes for its customers.

Rules:
1. Use only the numbered passages. Never use what you know from anywhere else.
2. After every fact, cite the passage it comes from, like [2].
3. You may combine facts from several passages and do simple arithmetic with them.
4. If passages disagree, say so in one sentence. Then use the one that applies:
   for a policy, the version in force on the purchase date; otherwise the newest document.
5. If the passages do not contain the answer, reply exactly: I don't know. The documents don't say.
Keep the answer short."""


def rewrite_follow_up(chat, message):
    """Turn a follow-up into one standalone question for the search."""
    history = "\n".join(f"{turn['role']}: {turn['text']}" for turn in chat)
    prompt = f"""Here is a chat with an e-bike company's support assistant:

{history}
customer: {message}

Rewrite the customer's last message as one standalone question for a search engine.
Keep every bike model, part number and error code. Write the question only."""
    response = client.responses.create(model=CHAT_MODEL, input=prompt)
    return response.output_text.strip()


def build_prompt(question, found):
    """Number the sections and put each document's date next to it."""
    passages = []
    for number, section in enumerate(found, start=1):
        passages.append(f"[{number}] {section['source']} ({section['date']})\n{section['text']}")
    return "Passages:\n\n" + "\n\n".join(passages) + f"\n\nQuestion: {question}"


def stream_answer(question, found, usage=None):
    """Yield the answer piece by piece, as the model writes it."""
    stream = client.responses.create(model=CHAT_MODEL, instructions=SYSTEM_PROMPT,
                                     input=build_prompt(question, found), stream=True)
    for event in stream:
        if event.type == "response.output_text.delta":
            yield event.delta
        if event.type == "response.completed" and usage is not None:
            usage["in"] = event.response.usage.input_tokens
            usage["out"] = event.response.usage.output_tokens


def check_citations(question, answer, found):
    """1. every cited [n] must be a passage we sent;
    2. every number in the answer must appear in a passage it cites, or in the question.
    A problem doesn't prove the answer wrong: it flags it for a person to look at."""
    if "I don't know" in answer:
        return []  # nothing to check
    problems = []
    cited = [int(n) for n in re.findall(r"\[(\d+)\]", answer)]
    if not cited:
        problems.append("no citation")
    for n in cited:
        if n < 1 or n > len(found):
            problems.append(f"[{n}] is not one of the passages")

    cited_text = " ".join(found[n - 1]["text"] for n in cited if 1 <= n <= len(found))
    answer_without_citations = re.sub(r"\[\d+\]", "", answer)
    for number in re.findall(r"\d[\d,.]*\d|\d", answer_without_citations):
        if number not in cited_text and number not in question:
            problems.append(f"{number} is not in the cited passages")
    return problems
