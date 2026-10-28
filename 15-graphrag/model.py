"""The chat model every script here calls, and a running count of what the calls cost."""
import json

from openai import OpenAI

client = OpenAI()

MODEL = "gpt-5.4-mini"
# OpenAI's published prices for gpt-5.4-mini, in dollars per million tokens (October 2026).
PRICE_INPUT = 0.75
PRICE_CACHED_INPUT = 0.075
PRICE_OUTPUT = 4.50

usage = {"calls": 0, "input": 0, "cached": 0, "output": 0}


def ask(prompt, want_json=False):
    if want_json:
        response = client.responses.create(model=MODEL, input=prompt, text={"format": {"type": "json_object"}})
    else:
        response = client.responses.create(model=MODEL, input=prompt)
    usage["calls"] += 1
    usage["input"] += response.usage.input_tokens
    usage["cached"] += response.usage.input_tokens_details.cached_tokens
    usage["output"] += response.usage.output_tokens
    return response.output_text.strip()


def ask_for_json(prompt):
    return json.loads(ask(prompt, want_json=True))


def cost():
    """Dollars spent so far by this script."""
    uncached = usage["input"] - usage["cached"]
    dollars = uncached * PRICE_INPUT + usage["cached"] * PRICE_CACHED_INPUT + usage["output"] * PRICE_OUTPUT
    return dollars / 1_000_000


def usage_line():
    return (f"{usage['calls']} calls, {usage['input']:,} input tokens ({usage['cached']:,} cached), "
            f"{usage['output']:,} output tokens, ${cost():.2f}")
