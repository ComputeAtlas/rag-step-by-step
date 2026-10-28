"""A day of document changes, and what the bot answers before and after the index is synced.

It works on a copy of the documents in 18-rag-in-production/results/docs/ (the course's own
documents are never changed). Three changes, like a real day:
- changed: the delivery surcharge for the Scottish Highlands goes up from 49 to 59 pounds;
- deleted: a customer asked us to delete their support ticket (ticket 1010);
- new: a winter service offer.

    python 18-rag-in-production/freshness_demo.py"""
import shutil
from pathlib import Path

from fresh_index import build_index, sync_index
from pipeline import answer

DOCS = Path("18-rag-in-production/results/docs")
shutil.rmtree(DOCS, ignore_errors=True)
shutil.copytree("data/fernhill", DOCS)

index = build_index(DOCS)
print(f"Index built: {len(index['fingerprints'])} documents, {len(index['chunks'])} chunks")

q_price = "How much is the delivery surcharge to the Scottish Highlands?"
q_ticket = "What did the customer in ticket FH-T-1010 report?"


def ask(question, role):
    text, found, trace = answer(question, index, role)
    print(f"  Q: {question}")
    print(f"  A: {text}")


print()
print("Before the changes:")
ask(q_price, "customer")
ask(q_ticket, "staff")

# The day's changes, made to the copy of the documents.
shipping = DOCS / "policies/shipping-and-delivery.md"
shipping.write_text(shipping.read_text().replace("| Scottish Highlands and islands | £49 |",
                                                 "| Scottish Highlands and islands | £59 |"))
(DOCS / "support/ticket-1010-metro-charger-hot-recall.md").unlink()
(DOCS / "policies/winter-service-offer.md").write_text(
    "# Winter service offer\n\nFrom 1 November 2026 to 28 February 2027, a full service at any Fernhill "
    "service centre is 20% off. Book in the Fernhill Service app.\n")

print()
print("After the changes, index NOT synced:")
ask(q_price, "customer")
ask(q_ticket, "staff")

report = sync_index(index, DOCS)
print()
print("Sync:")
print(f"  unchanged  {report['unchanged']}")
print(f"  changed    {len(report['changed'])}  {', '.join(report['changed'])}")
print(f"  deleted    {len(report['deleted'])}  {', '.join(report['deleted'])}")
print(f"  new        {len(report['new'])}  {', '.join(report['new'])}")
print(f"  removed {report['removed']} old chunks, embedded {report['embedded']} new chunks"
      f" (not all {len(index['chunks'])})")

print()
print("After the sync:")
ask(q_price, "customer")
ask(q_ticket, "staff")
