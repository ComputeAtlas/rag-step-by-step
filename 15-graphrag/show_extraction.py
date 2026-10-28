"""Print what the model found in one chunk (from results/extracted.json; no model calls).
Usage: python 15-graphrag/show_extraction.py 203"""
import json
import sys

number = int(sys.argv[1]) if len(sys.argv) > 1 else 203
with open("15-graphrag/results/extracted.json") as file:
    item = json.load(file)[number]

print(f"Chunk {number}, from {item['source']}")
print("Entities:")
for entity in item["entities"]:
    print(f"  {entity['name']} ({entity['type']})")
print("Relations:")
for relation in item["relations"]:
    print(f"  {relation['source']} -- {relation['target']}")
