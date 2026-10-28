"""Local search: start from the things in the graph that best match the question, and read
around them: their descriptions, their strongest links, their community's report, and a few
of the chunks that mention them. Then the model answers from that.
Needs results/ from build_graph.py and summarize_communities.py.
Usage: python 15-graphrag/local_search.py "What should owners know about the FH-2310-A charger?" """
import json
import sys
from pathlib import Path

import networkx as nx
import numpy as np
from openai import OpenAI

from model import ask, usage_line

client = OpenAI()
RESULTS = Path("15-graphrag/results")
with open(RESULTS / "graph.json") as file:
    graph = nx.node_link_graph(json.load(file), edges="edges")
with open(RESULTS / "reports.json") as file:
    reports = {report["community"]: report for report in json.load(file)}
with open("05-measuring-rag/index/chunks.json") as file:
    chunks = json.load(file)

names = list(graph.nodes)


def embed(texts):
    vectors = []
    for start in range(0, len(texts), 500):  # at most 500 texts per request
        response = client.embeddings.create(model="text-embedding-3-small", input=texts[start:start + 500])
        vectors += [item.embedding for item in response.data]
    return np.array(vectors)


# One vector per entity: its name and first description (made once, then saved).
VECTORS = RESULTS / "entity-vectors.npy"
if not VECTORS.exists():
    texts = [f"{graph.nodes[n]['name']}: {graph.nodes[n]['descriptions'][0]}" for n in names]
    np.save(VECTORS, embed(texts))
entity_vectors = np.load(VECTORS)


def find_start(question, how_many_entities=3):
    """First the things the question names exactly, then the closest in meaning."""
    words = " " + " ".join(question.lower().replace("?", " ").split()) + " "
    named = [name for name in names if len(name) >= 3 and f" {name} " in words]
    named.sort(key=len, reverse=True)  # the most specific name first
    scores = entity_vectors @ embed([question])[0]
    closest = [names[i] for i in scores.argsort()[::-1]]
    start_names = []
    for name in named + closest:
        if name not in start_names:
            start_names.append(name)
    return start_names[:how_many_entities]


def local_search(question):
    start_names = find_start(question)
    parts = []
    chunk_numbers = []
    for name in start_names:
        node = graph.nodes[name]
        parts.append(f"{node['name']} ({node['type']}): {' '.join(node['descriptions'][:3])}")
        links = sorted(graph.edges(name, data=True), key=lambda edge: -edge[2]["weight"])[:10]
        for a, b, data in links:
            parts.append(f"- linked to {graph.nodes[b]['name']}: {data['descriptions'][0]}")
        report = reports.get(node["community"])
        if report:
            parts.append(f"Its community: {report['title']}. {report['summary']}")
        for number in node["chunks"][:2]:
            if number not in chunk_numbers:
                chunk_numbers.append(number)
    for number in chunk_numbers[:4]:
        parts.append(f"From {chunks[number]['source']}:\n{chunks[number]['text']}")
    context = "\n\n".join(parts)
    prompt = f"""Answer the question using only the information below.
If it doesn't contain the answer, say that you don't know.

{context}

Question: {question}"""
    return ask(prompt), start_names


if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else "What should owners know about the FH-2310-A charger?"
    answer, start_names = local_search(question)
    print("Question:", question)
    print("Starts from:", ", ".join(graph.nodes[n]["name"] for n in start_names))
    print("Answer:", answer)
    print(f"Model: {usage_line()}")
