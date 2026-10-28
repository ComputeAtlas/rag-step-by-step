"""Step 1 of building the graph: a model reads every chunk of the baseline index and lists
the things it mentions (entities) and how they are linked (relations).

288 chat calls, one per chunk. Saves 15-graphrag/results/extracted.json after every chunk,
so if it stops halfway, run it again and it carries on where it stopped."""
import json
import time
from pathlib import Path

from model import ask_for_json, usage_line

RESULTS = Path("15-graphrag/results")
RESULTS.mkdir(exist_ok=True)
SAVED = RESULTS / "extracted.json"

with open("05-measuring-rag/index/chunks.json") as file:
    chunks = json.load(file)

PROMPT = """You are building a knowledge graph of Fernhill Bikes, an electric-bike company.
Read the text below and list the things it mentions, and how they are linked.

A thing (an entity) is one of these types: bike model, part, error code, problem,
firmware version, policy, support ticket, person, place.
Give each thing a short name, written the way the documents usually write it,
for example "Ridge 500", "E03", "FH-3105-A", "firmware v2.4", "ticket FH-T-1004".
Name a problem by its general topic, the way a customer would, for example
"battery range", "brake noise", "charging".

A link (a relation) joins two things from your list, with one sentence saying how.

Return JSON like this:
{{"entities": [{{"name": "...", "type": "...", "description": "one sentence, from this text"}}],
 "relations": [{{"source": "...", "target": "...", "description": "one sentence"}}]}}

Text (from {source}):
{text}"""

extracted = []
if SAVED.exists():
    with open(SAVED) as file:
        extracted = json.load(file)  # carry on after a stop

start = time.time()
for number, chunk in enumerate(chunks):
    if number < len(extracted):
        continue  # already done
    found = ask_for_json(PROMPT.format(source=chunk["source"], text=chunk["text"]))
    extracted.append({"chunk": number, "source": chunk["source"],
                      "entities": found.get("entities", []), "relations": found.get("relations", [])})
    with open(SAVED, "w") as file:
        json.dump(extracted, file, indent=1)
    if (number + 1) % 24 == 0:
        print(f"  {number + 1} of {len(chunks)} chunks read")

entities = sum(len(item["entities"]) for item in extracted)
relations = sum(len(item["relations"]) for item in extracted)
print(f"Read {len(extracted)} chunks: {entities} entities and {relations} relations found")
print(f"Time: {(time.time() - start) / 60:.1f} minutes")
print(f"Model: {usage_line()}")
