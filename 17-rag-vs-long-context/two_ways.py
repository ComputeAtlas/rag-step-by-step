"""Answer a question two ways, and measure each one: time, tokens and cost.

- with RAG: search for the best 4 chunks (the hybrid search), then answer from them;
- with everything: put all 87 documents in the prompt, then answer.

The other files in this folder import this one."""
import sys
import time

from openai import OpenAI

from whole_corpus import load_all_documents

sys.path.append("08-hybrid-search")  # reuse the hybrid search from the hybrid-search lesson
from searches import chunks, hybrid_search

client = OpenAI()
MODEL = "gpt-5.4-mini"

# Prices in dollars per million tokens, from OpenAI's pricing page (gpt-5.4-mini, 28 October 2026).
PRICE_INPUT = 0.75
PRICE_CACHED_INPUT = 0.075  # input it read a moment ago: 90% cheaper
PRICE_OUTPUT = 4.50

INSTRUCTIONS = """Answer the question using only the documents below.
If they don't contain the answer, say that you don't know."""

ALL_DOCUMENTS = "\n\n".join(load_all_documents())


def cost_in_dollars(usage):
    cached = usage.input_tokens_details.cached_tokens
    not_cached = usage.input_tokens - cached
    return (not_cached * PRICE_INPUT + cached * PRICE_CACHED_INPUT
            + usage.output_tokens * PRICE_OUTPUT) / 1_000_000


def ask(prompt, cache_key=None):
    start = time.perf_counter()
    if cache_key:
        response = client.responses.create(model=MODEL, input=prompt, prompt_cache_key=cache_key)
    else:
        response = client.responses.create(model=MODEL, input=prompt)
    seconds = time.perf_counter() - start
    usage = response.usage
    return {
        "answer": response.output_text.strip(),
        "seconds": round(seconds, 2),
        "input_tokens": usage.input_tokens,
        "cached_tokens": usage.input_tokens_details.cached_tokens,
        "output_tokens": usage.output_tokens,
        "dollars": cost_in_dollars(usage),
    }


def ask_with_rag(question):
    start = time.perf_counter()
    found = [chunks[number] for score, number in hybrid_search(question)[:4]]
    search_seconds = time.perf_counter() - start
    passages = "\n\n".join(f"From {c['source']}:\n{c['text']}" for c in found)
    result = ask(f"{INSTRUCTIONS}\n\n{passages}\n\nQuestion: {question}")
    result["search_seconds"] = round(search_seconds, 2)
    result["seconds"] = round(result["seconds"] + search_seconds, 2)  # the whole wait
    result["found"] = [c["source"] for c in found]
    return result


def ask_with_everything(question):
    # Documents first, question last: the start never changes, so it can be cached.
    prompt = f"{INSTRUCTIONS}\n\n{ALL_DOCUMENTS}\n\nQuestion: {question}"
    return ask(prompt, cache_key="fernhill-all-documents")


def ask_with_everything_question_first(question):
    # The question at the top: every prompt starts differently, so nothing can be cached.
    prompt = f"{INSTRUCTIONS}\n\nQuestion: {question}\n\n{ALL_DOCUMENTS}"
    return ask(prompt)
