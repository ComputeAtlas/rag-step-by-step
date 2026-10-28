"""The scoreboard: all 100 test questions, answered by plain RAG and by the agent,
both graded by the baseline's judge. It also counts what each one costs.

About 600 model calls in total (roughly $1). Every answer is saved in 14-agentic-rag/results/."""
import json
import statistics
from pathlib import Path

from agent import MAX_STEPS, run_agent
from costs import dollars, new_usage
from judge import judge_answer
from plain_rag import ask_plain_rag

RESULTS_FOLDER = Path(__file__).parent / "results"
BASELINE_FILE = Path("05-measuring-rag/index/results.json")  # the frozen baseline's graded answers

with open("data/fernhill-questions.json") as file:
    questions = json.load(file)
with open(BASELINE_FILE) as file:
    baseline = {r["id"]: r for r in json.load(file)}


def without_repeats(read):
    """The chunks a system read, each once."""
    seen = []
    for chunk in read:
        if chunk not in seen:
            seen.append(chunk)
    return seen


rows = []
judge_usage = new_usage()
for number, q in enumerate(questions, start=1):
    row = {"id": q["id"], "category": q["category"], "question": q["question"]}
    for name, system in [("plain", ask_plain_rag), ("agent", run_agent)]:
        result = system(q["question"])
        read = without_repeats(result["read"])
        verdict = judge_answer(q["question"], q["answer"], read, result["answer"], judge_usage)
        files = {chunk["source"] for chunk in read}
        row[name] = {
            "answer": result["answer"], "correct": bool(verdict["correct"]),
            "reason": verdict["reason"], "searches": result["searches"],
            "steps": result.get("steps", []), "usage": result["usage"],
            "dollars": dollars(result["usage"]), "seconds": result["seconds"],
            "found_all_files": set(q["sources"]) <= files,
        }
    rows.append(row)
    print(f"{number:3d} {q['id']}  plain {'yes' if row['plain']['correct'] else 'no '}  "
          f"agent {'yes' if row['agent']['correct'] else 'no '}  searches {len(row['agent']['searches'])}",
          flush=True)

RESULTS_FOLDER.mkdir(exist_ok=True)
with open(RESULTS_FOLDER / "scoreboard.json", "w") as file:
    json.dump(rows, file, indent=1, default=str)

groups = [
    ("Two-document questions", lambda r: r["category"] == "multi-document"),
    ("Single-search questions", lambda r: r["category"] not in ("unanswerable", "whole-corpus")),
    ("All questions", lambda r: True),
]
print("\nCorrect answers (judged by gpt-5.4-mini)")
print(f"  {'':26s} {'baseline':>9s} {'plain':>9s} {'agent':>9s}")
for title, belongs in groups:
    sub = [r for r in rows if belongs(r)]
    before = sum(baseline[r["id"]]["correct"] for r in sub)
    plain = sum(r["plain"]["correct"] for r in sub)
    agent = sum(r["agent"]["correct"] for r in sub)
    n = len(sub)
    print(f"  {title:26s} {before:3d} / {n:<3d} {plain:3d} / {n:<3d} {agent:3d} / {n:<3d}")

print("\nCorrect answers by category")
print(f"  {'category':24s} {'n':>3s} {'plain':>6s} {'agent':>6s}")
for category in ["lookup", "part-number/error-code", "table", "multi-document",
                 "conflicting-versions", "whole-corpus", "unanswerable"]:
    sub = [r for r in rows if r["category"] == category]
    print(f"  {category:24s} {len(sub):3d} {sum(r['plain']['correct'] for r in sub):6d} "
          f"{sum(r['agent']['correct'] for r in sub):6d}")

two = [r for r in rows if r["category"] == "multi-document"]
print(f"\nTwo-document questions where both needed files were read: "
      f"plain {sum(r['plain']['found_all_files'] for r in two)} / {len(two)}, "
      f"agent {sum(r['agent']['found_all_files'] for r in two)} / {len(two)}")

print("\nWhat one question costs (averages over all 100)")
print(f"  {'':22s} {'plain':>9s} {'agent':>9s}")
for title, value in [
    ("model calls", lambda s: s["usage"]["calls"]),
    ("searches", lambda s: len(s["searches"])),
    ("tokens", lambda s: s["usage"]["input"] + s["usage"]["output"]),
]:
    plain = statistics.mean(value(r["plain"]) for r in rows)
    agent = statistics.mean(value(r["agent"]) for r in rows)
    print(f"  {title:22s} {plain:9.1f} {agent:9.1f}")
plain_cost = sum(r["plain"]["dollars"] for r in rows)
agent_cost = sum(r["agent"]["dollars"] for r in rows)
print(f"  {'dollars, 100 questions':22s} {plain_cost:9.3f} {agent_cost:9.3f}")
plain_time = statistics.median(r["plain"]["seconds"] for r in rows)
agent_time = statistics.median(r["agent"]["seconds"] for r in rows)
print(f"  {'median seconds':22s} {plain_time:9.1f} {agent_time:9.1f}")
slowest = max(r["agent"]["seconds"] for r in rows)
print(f"  {'slowest agent answer':22s} {'':9s} {slowest:9.1f}")

searches = [len(r["agent"]["searches"]) for r in rows]
print("\nHow many searches the agent chose")
for count in sorted(set(searches)):
    print(f"  {count} searches: {searches.count(count):3d} questions")
capped = sum(1 for r in rows if r["agent"]["steps"] and r["agent"]["steps"][-1].get("forced"))
print(f"  stopped by the cap of {MAX_STEPS} steps: {capped}")
print(f"\nThe judge's own calls: {judge_usage['calls']}, ${dollars(judge_usage):.3f}")
