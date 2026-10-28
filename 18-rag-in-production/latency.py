"""Time 40 real questions from the test set and report the typical and the slow wait.

- p50 (the median): half the questions were faster than this, half slower.
- p95: 95 of every 100 questions were faster than this; it is the wait of the slowest 1 in 20.
It also adds up the tokens, to work out what one question costs.

    python 18-rag-in-production/latency.py"""
import json
from pathlib import Path

from pipeline import answer, load_baseline_index
from tracer import total_ms

# Prices in dollars per million tokens (OpenAI pricing page, standard tier).
PRICE_INPUT = 0.75       # gpt-5.4-mini, tokens we send
PRICE_OUTPUT = 4.50      # gpt-5.4-mini, tokens it writes
PRICE_EMBEDDING = 0.02   # text-embedding-3-small


def percentile(values, p):
    values = sorted(values)
    position = round(p / 100 * (len(values) - 1))
    return values[position]


with open("data/fernhill-questions.json") as file:
    questions = json.load(file)
single_search = [q for q in questions if q["category"] in ("lookup", "part-number/error-code", "table")]
chosen = single_search[:40]

index = load_baseline_index()
answer("warm-up", index)  # connect to the API once before timing

traces = []
for q in chosen:
    text, found, trace = answer(q["question"], index)
    traces.append(trace)
    print(f"{q['id']}  {total_ms(trace):>6,.0f} ms")

print()
print(f"{len(traces)} questions        p50        p95")
for name in [span["name"] for span in traces[0]["spans"]]:
    times = [span["ms"] for t in traces for span in t["spans"] if span["name"] == name]
    print(f"  {name:<18} {percentile(times, 50):>7,.1f} ms {percentile(times, 95):>7,.1f} ms")
totals = [total_ms(t) for t in traces]
print(f"  {'whole question':<18} {percentile(totals, 50):>7,.1f} ms {percentile(totals, 95):>7,.1f} ms")
print(f"  slowest: {max(totals):,.0f} ms   average: {sum(totals) / len(totals):,.0f} ms")

tokens_in = sum(t["tokens"]["input"] for t in traces) / len(traces)
tokens_out = sum(t["tokens"]["output"] for t in traces) / len(traces)
tokens_embed = sum(t["tokens"]["embedding"] for t in traces) / len(traces)
dollars = (tokens_in * PRICE_INPUT + tokens_out * PRICE_OUTPUT + tokens_embed * PRICE_EMBEDDING) / 1_000_000
print()
print(f"Tokens per question: {tokens_in:,.0f} in, {tokens_out:,.0f} out, {tokens_embed:,.0f} to embed")
print(f"Cost per question: ${dollars:.5f}")
print(f"  of it, the chunks we send: {tokens_in * PRICE_INPUT / 1_000_000 / dollars * 100:.0f}%")
print(f"10,000 questions a day: ${dollars * 10_000:,.2f} a day, ${dollars * 10_000 * 30:,.0f} a month")

Path("18-rag-in-production/results").mkdir(exist_ok=True)
with open("18-rag-in-production/results/latency.json", "w") as file:
    json.dump(traces, file, indent=1)
