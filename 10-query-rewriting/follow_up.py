"""A follow-up question, searched as typed and after the model rewrites it.

    python 10-query-rewriting/follow_up.py          # the first chat: "it broke again??"
    python 10-query-rewriting/follow_up.py f02      # any id from follow_up_questions.json"""
import json
import sys
import textwrap
from pathlib import Path

from rewriters import rewrite_follow_up
from searching import search, show

chat_id = sys.argv[1] if len(sys.argv) > 1 else "f01"
with open(Path(__file__).parent / "follow_up_questions.json") as file:
    follow_up = [f for f in json.load(file) if f["id"] == chat_id][0]
with open("data/fernhill-questions.json") as file:
    needed = [q for q in json.load(file) if q["id"] == follow_up["same_as"]][0]["sources"]

print("Chat so far:")
for turn in follow_up["chat"]:
    print(textwrap.fill(f"{turn['role']}: {turn['text']}", 52, initial_indent="  ", subsequent_indent="    "))
print(f"Last message: {follow_up['message']}\n")

print("Searching with the last message:")
show(search(follow_up["message"]), needed)

rewritten = rewrite_follow_up(follow_up["chat"], follow_up["message"])
print("\n" + textwrap.fill(f"Rewritten: {rewritten}", 52, subsequent_indent="  "))
print("Searching with the rewrite:")
show(search(rewritten), needed)
