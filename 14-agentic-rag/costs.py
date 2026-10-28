"""Counting tokens and money. Every model call reports how many tokens it read and wrote."""

# gpt-5.4-mini, dollars per million tokens (OpenAI's pricing page, October 2026).
# "Cached" input is text the model has just seen at the start of an earlier call: it costs a tenth.
PRICE_INPUT = 0.75
PRICE_CACHED_INPUT = 0.075
PRICE_OUTPUT = 4.50


def new_usage():
    return {"calls": 0, "input": 0, "cached": 0, "output": 0}


def add_usage(total, usage):
    """Add one response's usage to the running total."""
    total["calls"] += 1
    total["input"] += usage.input_tokens
    total["cached"] += usage.input_tokens_details.cached_tokens
    total["output"] += usage.output_tokens


def dollars(total):
    fresh_input = total["input"] - total["cached"]
    cost = fresh_input * PRICE_INPUT + total["cached"] * PRICE_CACHED_INPUT + total["output"] * PRICE_OUTPUT
    return cost / 1_000_000
