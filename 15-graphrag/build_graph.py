"""Step 2: merge everything extract_graph.py found into one graph, then find its communities:
groups of things that link mostly to each other. No model calls.

Two mentions with the same name (ignoring capitals and spaces) become one thing. The graph and
its communities are saved in 15-graphrag/results/."""
import json
from pathlib import Path

import networkx as nx

RESULTS = Path("15-graphrag/results")
with open(RESULTS / "extracted.json") as file:
    extracted = json.load(file)


def key(name):
    return " ".join(name.lower().split())  # "Ridge  500" and "ridge 500" are the same thing


graph = nx.Graph()
for item in extracted:  # one item per chunk
    for entity in item["entities"]:
        name = key(entity["name"])
        if name not in graph:
            graph.add_node(name, name=entity["name"], type=entity["type"], descriptions=[], sources=[], chunks=[])
        node = graph.nodes[name]
        node["descriptions"].append(entity["description"])
        if item["source"] not in node["sources"]:
            node["sources"].append(item["source"])  # which documents mention it
        if item["chunk"] not in node["chunks"]:
            node["chunks"].append(item["chunk"])  # and which chunks
    for relation in item["relations"]:
        a, b = key(relation["source"]), key(relation["target"])
        if a == b or a not in graph or b not in graph:
            continue  # a link to something that was never listed: skip it
        if graph.has_edge(a, b):
            graph.edges[a, b]["weight"] += 1  # the same link, seen again
            graph.edges[a, b]["descriptions"].append(relation["description"])
        else:
            graph.add_edge(a, b, weight=1, descriptions=[relation["description"]])

print(f"The graph: {graph.number_of_nodes()} entities, {graph.number_of_edges()} relations")

print("Mentioned in the most documents:")
by_documents = sorted(graph.nodes, key=lambda n: -len(graph.nodes[n]["sources"]))
for name in by_documents[:8]:
    node = graph.nodes[name]
    print(f"  {node['name']:24s} {node['type']:14s} in {len(node['sources'])} documents, {graph.degree[name]} links")

# Community detection with Leiden: groups whose things link more inside than outside
# ("modularity"). The seed makes the result the same on every run.
communities = nx.community.leiden_communities(graph, weight="weight", metric="modularity", seed=42)
communities = sorted(communities, key=len, reverse=True)
for number, members in enumerate(communities):
    for name in members:
        graph.nodes[name]["community"] = number

sizes = [len(members) for members in communities]
big = [size for size in sizes if size >= 3]
print(f"Communities: {len(communities)} ({len(big)} with 3 or more entities); the biggest: {sizes[:6]}")

with open(RESULTS / "graph.json", "w") as file:
    json.dump(nx.node_link_data(graph, edges="edges"), file)
with open(RESULTS / "communities.json", "w") as file:
    json.dump([sorted(members) for members in communities], file, indent=1)
print("Saved the graph and its communities in", RESULTS)
