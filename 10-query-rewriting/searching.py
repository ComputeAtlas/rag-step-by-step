"""The search we start from: hybrid search (vector + keyword, merged by their places),
over the same 288 Fernhill chunks as the baseline. This file adds two small helpers:

- fuse_lists: merge any number of ranked lists by their places;
- in_sections: keep only the chunks from some parts of the library (for routing).

Run everything from the repository root, e.g. python 10-query-rewriting/follow_up.py"""
import sys

sys.path.append("08-hybrid-search")  # reuse the hybrid search built there
from searches import chunks, fuse, hybrid_search, keyword_search, vector_search  # noqa: E402


def fuse_lists(lists, k=60):
    """Reciprocal Rank Fusion for any number of lists: each list gives a chunk 1 / (k + its place)."""
    points = {}
    for results in lists:
        for place, (score, number) in enumerate(results, start=1):
            points[number] = points.get(number, 0) + 1 / (k + place)
    merged = []
    for number, total in points.items():
        merged.append((total, number))
    merged.sort(reverse=True)  # most points first
    return merged


def search(question):
    return hybrid_search(question)


def section_of(source):
    """Which part of the library a file belongs to, e.g. 'parts/brakes-and-tyres.md' -> 'parts'."""
    if "/" in source:
        return source.split("/")[0]
    if source == "warranty-policy.md":
        return "policies"
    return "company"  # company.md, faq.md, store-locations.md


def in_sections(results, sections):
    kept = []
    for score, number in results:
        if section_of(chunks[number]["source"]) in sections:
            kept.append((score, number))
    return kept


def top_files(results, how_many=4):
    return [chunks[number]["source"] for score, number in results[:how_many]]


def show(results, needed=()):
    """Print the four best files; a file the question needs gets a '+' in front."""
    for place, source in enumerate(top_files(results), start=1):
        mark = "+" if source in needed else " "
        print(f" {mark}{place}. {source}")
