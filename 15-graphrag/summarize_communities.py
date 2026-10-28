"""Step 3: a model writes a short report for every community of 3 or more entities: a title,
and a summary of what the group is about. Global search reads these reports.
Needs results/graph.json from build_graph.py."""
import json
import time
from pathlib import Path

import networkx as nx

from model import ask_for_json, usage_line

RESULTS = Path("15-graphrag/results")
with open(RESULTS / "graph.json") as file:
    graph = nx.node_link_graph(json.load(file), edges="edges")
with open(RESULTS / "communities.json") as file:
    communities = json.load(file)

PROMPT = """Below are the things (entities) in one group of a knowledge graph of Fernhill Bikes,
an electric-bike company, and the links (relations) between them. Each thing says how many
of the company's documents mention it, and how many of those are customer support tickets.

Write a report on this group. Return JSON like this:
{{"title": "a short title", "summary": "4 to 6 sentences: what the group is about, and the
most important facts. Say which things come up in the most documents and support tickets."}}

Things:
{things}

Links:
{links}"""


def describe_community(members):
    members = sorted(members, key=lambda n: -len(graph.nodes[n]["sources"]))[:40]  # the 40 most mentioned
    things = []
    for name in members:
        node = graph.nodes[name]
        tickets = [source for source in node["sources"] if source.startswith("support/")]
        things.append(f"- {node['name']} ({node['type']}, in {len(node['sources'])} documents, "
                      f"{len(tickets)} of them support tickets): "
                      f"{' '.join(node['descriptions'][:2])}")
    links = []
    inside = graph.subgraph(members).edges(data=True)
    for a, b, data in sorted(inside, key=lambda edge: -edge[2]["weight"])[:40]:
        links.append(f"- {graph.nodes[a]['name']} -> {graph.nodes[b]['name']}: {data['descriptions'][0]}")
    return "\n".join(things), "\n".join(links)


start = time.time()
reports = []
for number, members in enumerate(communities):
    if len(members) < 3:
        continue  # too small to be worth a report
    things, links = describe_community(members)
    report = ask_for_json(PROMPT.format(things=things, links=links))
    reports.append({"community": number, "size": len(members),
                    "title": report["title"], "summary": report["summary"]})
    print(f"community {number:3d} ({len(members):3d} entities): {report['title']}")

with open(RESULTS / "reports.json", "w") as file:
    json.dump(reports, file, indent=1)
print(f"Wrote {len(reports)} community reports in {(time.time() - start) / 60:.1f} minutes")
print(f"Model: {usage_line()}")
