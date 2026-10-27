"""Contextual retrieval: before a chunk is embedded, a model writes one or two sentences
that say where the chunk comes from and what it is about. We put those sentences in front
of the chunk, then embed the two together.

We do it for the same 288 chunks as the baseline (05-measuring-rag/build_index.py), so the
only thing that changes is the added context. One chat call per chunk, run once.
Everything it makes is saved in 11-smarter-indexes/results/."""
import json
import time
from pathlib import Path

import numpy as np
from openai import OpenAI

client = OpenAI()

DOCUMENTS_FOLDER = Path("data/fernhill")
BASELINE_FOLDER = Path("05-measuring-rag/index")
RESULTS_FOLDER = Path(__file__).parent / "results"

# Published prices in dollars per million tokens (OpenAI pricing page, October 2026).
PRICE_INPUT = 0.75          # gpt-5.4-mini, new input tokens
PRICE_CACHED_INPUT = 0.075  # gpt-5.4-mini, input tokens it has seen before (the same document again)
PRICE_OUTPUT = 4.50         # gpt-5.4-mini, the sentences it writes
PRICE_EMBEDDING = 0.02      # text-embedding-3-small


def write_context(document, chunk):
    # The document goes first: for the next chunk of the same document, the start of the
    # prompt is the same, so OpenAI can reuse it (cached input costs a tenth).
    prompt = f"""<document>
{document}
</document>

Here is a chunk from that document:
<chunk>
{chunk}
</chunk>

Write one or two short sentences that place this chunk within the whole document,
to help a search find it. Say which document it is from and what the chunk is about.
Answer with those sentences only."""
    response = client.responses.create(model="gpt-5.4-mini", input=prompt)
    return response.output_text.strip(), response.usage


with open(BASELINE_FOLDER / "chunks.json") as file:
    chunks = json.load(file)

start_time = time.time()
new_tokens = cached_tokens = output_tokens = 0
contextual_chunks = []
for number, chunk in enumerate(chunks):
    document = (DOCUMENTS_FOLDER / chunk["source"]).read_text()
    context, usage = write_context(document, chunk["text"])
    cached = usage.input_tokens_details.cached_tokens
    new_tokens += usage.input_tokens - cached
    cached_tokens += cached
    output_tokens += usage.output_tokens
    contextual_chunks.append({"source": chunk["source"], "context": context, "text": chunk["text"]})
    if number % 25 == 0:
        print(f"chunk {number:3d} of {len(chunks)}: {context[:70]}...")
minutes = (time.time() - start_time) / 60

# Embed the context and the chunk together.
texts = [c["context"] + "\n\n" + c["text"] for c in contextual_chunks]
response = client.embeddings.create(model="text-embedding-3-small", input=texts)
vectors = np.array([item.embedding for item in response.data])
embedding_tokens = response.usage.total_tokens

RESULTS_FOLDER.mkdir(exist_ok=True)
with open(RESULTS_FOLDER / "contextual-chunks.json", "w") as file:
    json.dump(contextual_chunks, file, indent=1)
np.save(RESULTS_FOLDER / "contextual-vectors.npy", vectors)

chat_cost = (new_tokens * PRICE_INPUT + cached_tokens * PRICE_CACHED_INPUT
             + output_tokens * PRICE_OUTPUT) / 1_000_000
embedding_cost = embedding_tokens * PRICE_EMBEDDING / 1_000_000
context_words = [len(c["context"].split()) for c in contextual_chunks]
print()
print(f"Added context to {len(contextual_chunks)} chunks with gpt-5.4-mini in {minutes:.1f} minutes")
print(f"  input tokens: {new_tokens + cached_tokens:,} ({cached_tokens:,} of them cached)")
print(f"  output tokens: {output_tokens:,} (about {np.mean(context_words):.0f} words of context per chunk)")
print(f"  cost of the chat calls: ${chat_cost:.2f}")
print(f"  cost of embedding them again: ${embedding_cost:.4f}")
print(f"Saved in {RESULTS_FOLDER.name}/contextual-chunks.json and contextual-vectors.npy")
