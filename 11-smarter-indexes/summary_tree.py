"""A summary tree, in the spirit of RAPTOR: summaries of summaries, searched next to the chunks.

- level 0: the baseline's 288 chunks;
- level 1: one short summary per document (87);
- level 2: one summary per group of documents (6: the manuals, the parts catalogue, the
  policies, the support tickets, the release notes, and the general pages);
- level 3: one summary of everything.

RAPTOR groups pieces by meaning (it clusters their embeddings). Our documents already sit in
folders by kind, so we group by folder: simpler, and the idea is the same.
About 94 chat calls, run once. Saved in 11-smarter-indexes/results/."""
import json
import time
from pathlib import Path

import numpy as np
from openai import OpenAI

from searches import embed
from small_to_big import load_documents

client = OpenAI()

RESULTS_FOLDER = Path(__file__).parent / "results"
PRICE_INPUT = 0.75   # gpt-5.4-mini, dollars per million input tokens (October 2026)
PRICE_OUTPUT = 4.50  # gpt-5.4-mini, dollars per million output tokens
tokens = {"input": 0, "output": 0}


def summarise(instruction, text):
    response = client.responses.create(model="gpt-5.4-mini", input=f"{instruction}\n\n{text}")
    tokens["input"] += response.usage.input_tokens
    tokens["output"] += response.usage.output_tokens
    return response.output_text.strip()


def group_name(source):
    if "/" not in source:
        return "general"  # company.md, faq.md, store-locations.md, warranty-policy.md
    return source.split("/")[0]  # manuals, parts, policies, support, release-notes


start_time = time.time()
documents = load_documents()
with open("05-measuring-rag/index/chunks.json") as file:
    chunks = json.load(file)

tree = []
for chunk in chunks:
    tree.append({"level": 0, "source": chunk["source"], "text": chunk["text"]})

# Level 1: one summary per document.
document_summaries = {}
for document in documents:
    summary = summarise(
        "Summarise this document from Fernhill Bikes in at most 80 words: what it is and its main points.",
        document["text"])
    document_summaries[document["source"]] = summary
    tree.append({"level": 1, "source": document["source"], "text": summary})
print(f"Level 1: {len(document_summaries)} document summaries")

# Level 2: one summary per group, written from the document summaries in that group.
group_summaries = {}
for group in ["manuals", "parts", "policies", "support", "release-notes", "general"]:
    summaries = [s for source, s in document_summaries.items() if group_name(source) == group]
    summary = summarise(
        f"Here are summaries of the {len(summaries)} documents in one group of Fernhill Bikes' files "
        f"(the {group} group). In at most 150 words, sum up the whole group: what it holds, "
        "the main themes, and what comes up most often.",
        "\n\n".join(summaries))
    group_summaries[group] = summary
    tree.append({"level": 2, "source": f"summary of the {group} group", "text": summary})
print(f"Level 2: {len(group_summaries)} group summaries")

# Level 3: one summary of everything.
summary = summarise(
    "Here are summaries of every group of Fernhill Bikes' files. "
    "In at most 150 words, sum up everything they hold.",
    "\n\n".join(group_summaries.values()))
tree.append({"level": 3, "source": "summary of everything", "text": summary})
print("Level 3: 1 summary of everything")

vectors = embed([piece["text"] for piece in tree])
RESULTS_FOLDER.mkdir(exist_ok=True)
with open(RESULTS_FOLDER / "tree.json", "w") as file:
    json.dump(tree, file, indent=1)
np.save(RESULTS_FOLDER / "tree-vectors.npy", vectors)

cost = (tokens["input"] * PRICE_INPUT + tokens["output"] * PRICE_OUTPUT) / 1_000_000
minutes = (time.time() - start_time) / 60
print(f"\nThe tree: {len(tree)} pieces to search ({len(chunks)} chunks + {len(tree) - len(chunks)} summaries)")
print(f"Built in {minutes:.1f} minutes: {tokens['input']:,} input and {tokens['output']:,} output tokens, ${cost:.2f}")
print("\nThe support tickets, summed up:")
print(group_summaries["support"])
