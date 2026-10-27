"""Rerank one question and show where the chunks were before and after.

    python 09-reranking/rerank_one.py
    python 09-reranking/rerank_one.py "your question" file-with-the-answer.md"""
import sys

from reranker import chunks, first_stage, rerank

question = "On what date was firmware v2.1 released?"
answer_file = "release-notes/firmware-v2.1.md"  # the page with the answer
if len(sys.argv) == 3:
    question = sys.argv[1]
    answer_file = sys.argv[2]


def file_name(number):
    return chunks[number]["source"].split("/")[-1]  # without the folder


candidates = first_stage(question)  # 30 chunks, best first
old_place = {}
for place, (score, number) in enumerate(candidates, start=1):
    old_place[number] = place

print("Question:", question)
print()
print("First stage (hybrid search), top 4 of 30:")
for place, (score, number) in enumerate(candidates[:4], start=1):
    print(f"  {place}.  {file_name(number)}")
for place, (score, number) in enumerate(candidates, start=1):
    if chunks[number]["source"] == answer_file:
        print(f"  {answer_file.split('/')[-1]} is at place {place}")
        break

print()
print("Second stage (reranker), top 4:")
for place, (score, number) in enumerate(rerank(question, candidates), start=1):
    print(f"  {place}.  {score:5.2f}  {file_name(number)}  (was {old_place[number]})")
