"""Global search, in two steps:
- map: every community report gets the question, and gives back the points that help answer
  it, each with a score from 0 to 100 (one chat call per report);
- reduce: the best points, most important first, are combined into one answer (one more call).
Needs results/reports.json from summarize_communities.py.
Usage: python 15-graphrag/global_search.py "What do customers complain about most?" """
import json
import sys
import time
from pathlib import Path

from model import ask, ask_for_json, usage_line

RESULTS = Path("15-graphrag/results")
with open(RESULTS / "reports.json") as file:
    reports = json.load(file)

MAP_PROMPT = """Below is a report on one part of Fernhill Bikes' documents.
Using only this report, list the points that help answer the question. Give each point a
score from 0 to 100: how important it is for the answer. A point that only says the report
doesn't answer the question gets 0. If nothing in it helps, return {{"points": []}}.

Return JSON like this: {{"points": [{{"point": "...", "score": 50}}]}}

Report: {title}
{summary}

Question: {question}"""

REDUCE_PROMPT = """Below are points taken from reports on different parts of Fernhill Bikes'
documents, the most important first. Combine them into one answer to the question: weigh
the points against each other, and give numbers where the points give them. Use only these
points. If none of them is about the question, say that you don't know.

{points}

Question: {question}"""


def map_prompt(report, question):
    return MAP_PROMPT.format(title=report["title"], summary=report["summary"], question=question)


def global_search(question, how_many_points=20):
    points = []
    for report in reports:  # map: ask every community report
        reply = ask_for_json(map_prompt(report, question))
        for point in reply.get("points", []):
            if point["score"] > 0:
                point["from"] = report["title"]
                points.append(point)
    points.sort(key=lambda point: -point["score"])  # most important first
    best = points[:how_many_points]
    listed = "\n".join(f"- ({p['score']}) {p['point']}" for p in best)
    # reduce: one answer from the best points
    answer = ask(REDUCE_PROMPT.format(points=listed, question=question))
    return answer, best


if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else "What do customers complain about most?"
    start = time.time()
    answer, best = global_search(question)
    print("Question:", question)
    print(f"Asked {len(reports)} community reports. The best points:")
    for point in best[:6]:
        print(f"  {point['score']:3d}  {point['point'][:88]}")
    print("Answer:", answer)
    print(f"Time: {time.time() - start:.0f} seconds. Model: {usage_line()}")
