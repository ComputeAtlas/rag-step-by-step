"""Redact personal details from the 44 support tickets, and from a question before it is logged.

    python 18-rag-in-production/pii_demo.py"""
from pathlib import Path

from pii import redact, redact_ticket


def shorten(line, width=46):
    if len(line) > width:
        return line[:width] + "…"
    return line


tickets = sorted(Path("data/fernhill/support").glob("ticket-*.md"))
names_removed = 0
for path in tickets:
    names_removed += redact_ticket(path.read_text()).count("[CUSTOMER]")
print(f"{len(tickets)} tickets: {names_removed} mentions of a customer's name replaced")

text = Path("data/fernhill/support/ticket-1010-metro-charger-hot-recall.md").read_text()
original = text.splitlines()
cleaned = redact_ticket(text).splitlines()  # same lines, same order
with_name = [number for number, line in enumerate(original) if "Jonas" in line][:3]
print()
print("ticket-1010, before:")
for number in with_name:
    print("  " + shorten(original[number]))
print("after:")
for number in with_name:
    print("  " + shorten(cleaned[number]))

question = "I'm sam.k@example.com, phone 07700 900123. Why won't my Metro charge?"
print()
print("Typed: ", question)
print("Logged:", redact(question))
