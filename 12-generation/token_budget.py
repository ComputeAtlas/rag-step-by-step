"""What does a bigger context cost? The grounded prompt with 4, 8 and 20 chunks
for the same question: the tokens the model read and wrote, and the price. Three chat calls."""
from prompts import SYSTEM_PROMPT, ask, find_chunks, grounded_prompt

# OpenAI's published prices for gpt-5.4-mini, US dollars per million tokens (checked 28 October 2026).
PRICE_IN = 0.75
PRICE_OUT = 4.50

question = "I bought my Ridge 500 on 10 December 2025. How long is its battery covered?"

print("Question:", question)
print()
print(f"  {'chunks':>6s} {'tokens in':>10s} {'tokens out':>11s} {'cost':>10s} {'per 1,000 questions':>20s}")
for how_many in [4, 8, 20]:
    found = find_chunks(question, how_many)
    answer, tokens = ask(grounded_prompt(question, found), SYSTEM_PROMPT)
    cost = tokens["in"] * PRICE_IN / 1_000_000 + tokens["out"] * PRICE_OUT / 1_000_000
    print(f"  {how_many:6d} {tokens['in']:10,d} {tokens['out']:11,d} {'$' + format(cost, '.5f'):>10s} {'$' + format(cost * 1000, '.2f'):>20s}")
