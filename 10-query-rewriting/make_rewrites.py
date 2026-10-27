"""Ask the model once for every rewrite the scoreboard needs, and save them in
10-query-rewriting/results/rewrites.json, with how long each call took.

- the 20 follow-up questions: one standalone rewrite each;
- the 20 questions in a customer's own words: a rewrite, other ways to ask, an imagined answer;
- the 80 single-search test questions: other ways to ask, an imagined answer,
  sub-questions and the sections to search.

About 400 chat calls. Anything already in the file is skipped, so a second run is free."""
import json
import time
from pathlib import Path

from rewriters import imagine_answer, other_ways_to_ask, pick_sections, rewrite_follow_up, split_question

HERE = Path(__file__).parent
RESULTS_FILE = HERE / "results" / "rewrites.json"
RESULTS_FILE.parent.mkdir(exist_ok=True)

saved = {}
if RESULTS_FILE.exists():
    with open(RESULTS_FILE) as file:
        saved = json.load(file)


def rewrite_alone(question):
    return rewrite_follow_up([], question)  # no chat before it


def fill(group, items, jobs):
    """Run every job on every item that doesn't have its answer yet, timing each call."""
    rows = saved.setdefault(group, {})
    for item_id, text in items:
        row = rows.setdefault(item_id, {"seconds": {}})
        for name, job in jobs.items():
            if name in row:
                continue
            start = time.perf_counter()
            row[name] = job(*text) if isinstance(text, tuple) else job(text)
            row["seconds"][name] = round(time.perf_counter() - start, 2)
            print(item_id, name, "|", row[name])
            with open(RESULTS_FILE, "w") as file:
                json.dump(saved, file, indent=1)


with open("data/fernhill-questions.json") as file:
    questions = [q for q in json.load(file) if q["category"] not in ("unanswerable", "whole-corpus")]
with open(HERE / "follow_up_questions.json") as file:
    follow_ups = json.load(file)
with open(HERE / "own_words_questions.json") as file:
    own_words = json.load(file)

fill("follow_ups", [(f["id"], (f["chat"], f["message"])) for f in follow_ups],
     {"rewritten": rewrite_follow_up})
fill("own_words", [(o["id"], o["question"]) for o in own_words],
     {"rewritten": rewrite_alone, "many_ways": other_ways_to_ask, "imagined": imagine_answer})
fill("questions", [(q["id"], q["question"]) for q in questions],
     {"many_ways": other_ways_to_ask, "imagined": imagine_answer,
      "sub_questions": split_question, "sections": pick_sections})

print("saved", {group: len(rows) for group, rows in saved.items()})
