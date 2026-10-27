"""Five ways to change a question before we search with it. Each one is a single call to a
small chat model, gpt-5.4-mini, with a short prompt."""
from openai import OpenAI

client = OpenAI()


def ask(prompt):
    response = client.responses.create(model="gpt-5.4-mini", input=prompt)
    return response.output_text.strip()


def lines_of(text):
    """The non-empty lines of the model's answer."""
    return [line.strip() for line in text.splitlines() if line.strip()]


def rewrite_follow_up(chat, message):
    """Turn a follow-up like 'it broke again??' into a question that stands alone."""
    history = "\n".join(f"{turn['role']}: {turn['text']}" for turn in chat)
    prompt = f"""Here is a chat with an e-bike company's support assistant:

{history}
customer: {message}

Rewrite the customer's last message as one standalone question for a search engine.
Keep every bike model, part number and error code. Write the question only."""
    return ask(prompt)


def other_ways_to_ask(question):
    """Multi-query: the same question, asked three other ways."""
    prompt = f"""Write three different versions of this question, using other words
a document about e-bikes might use. One question per line, nothing else.

Question: {question}"""
    return lines_of(ask(prompt))[:3]


def imagine_answer(question):
    """HyDE: a made-up passage that looks like the answer. Only used for searching."""
    prompt = f"""Write a short passage (about 60 words) from an e-bike company's documents
that answers this question. If you don't know the facts, make them up.

Question: {question}"""
    return ask(prompt)


def split_question(question):
    """Sub-questions: one simple question for each thing the question asks."""
    prompt = f"""If answering this question needs more than one fact (for example a price
and a labour cost), write one simple sub-question per fact, one per line.
Each sub-question must make sense on its own: repeat the bike model or part it is about.
Otherwise write the question unchanged. Write nothing else.

Question: {question}"""
    return lines_of(ask(prompt))


SECTIONS = {
    "manuals": "owner's manuals: how to ride, charge and care for a bike, error codes, torques",
    "parts": "the parts catalogue: part numbers, prices, what fits which bike",
    "policies": "warranty, returns, delivery, service prices, business plans, safety notices",
    "support": "past support tickets: what customers asked and how it was solved",
    "release-notes": "firmware versions and what each one changed",
    "company": "the company, its stores and contact details, frequently asked questions",
}


def pick_sections(question):
    """Routing: which part of the library should we search?"""
    menu = "\n".join(f"- {name}: {about}" for name, about in SECTIONS.items())
    prompt = f"""Which part of the library should we search to answer this question?

{menu}

Pick one, or two if the question needs both. Write only the names, separated by commas.

Question: {question}"""
    answer = ask(prompt)
    return [name.strip() for name in answer.split(",") if name.strip() in SECTIONS]
