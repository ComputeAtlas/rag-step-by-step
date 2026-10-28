"""Print one community's report, and its most mentioned things (no model calls).
Usage: python 15-graphrag/show_report.py 2"""
import json
import sys
import textwrap

import networkx as nx

number = int(sys.argv[1]) if len(sys.argv) > 1 else 2
with open("15-graphrag/results/graph.json") as file:
    graph = nx.node_link_graph(json.load(file), edges="edges")
with open("15-graphrag/results/communities.json") as file:
    members = json.load(file)[number]
with open("15-graphrag/results/reports.json") as file:
    report = [r for r in json.load(file) if r["community"] == number][0]

top = sorted(members, key=lambda n: -len(graph.nodes[n]["sources"]))[:5]
print(f"Community {number}: {len(members)} entities. The most mentioned:")
print("  " + ", ".join(graph.nodes[n]["name"] for n in top))
print(f"Report: {report['title']}")
for line in textwrap.wrap(report["summary"], 76):
    print("  " + line)
