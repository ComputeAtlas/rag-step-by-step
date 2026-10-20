"""Score one index on the 15 table questions of the test set: retrieval (was the right file in the top 4?) and the
answer (graded by gpt-5.4-mini against the reference answer), with the same prompts as the baseline scoreboard.

Run from the repository root:  python 06-parsing/score_tables.py pdfs-pypdf
"""
import json
import sys
from pathlib import Path

import numpy as np
from openai import OpenAI

client = OpenAI()

parser_name = sys.argv[1]
INDEX_FOLDER = Path(__file__).parent / "index" / parser_name

with open(INDEX_FOLDER / "chunks.json") as file:
    chunks = json.load(file)
vectors = np.load(INDEX_FOLDER / "vectors.npy")

with open("data/fernhill-questions.json") as file:
    questions = [q for q in json.load(file) if q["category"] == "table"]


def embed(text):
    response = client.embeddings.create(model="text-embedding-3-small", input=text)
    return np.array(response.data[0].embedding)


def find_best_chunks(question_vector, how_many=4):
    results = []
    for number, vector in enumerate(vectors):
        score = float(np.dot(question_vector, vector))
        results.append((score, number))
    results.sort(reverse=True)
    return [chunks[number] for score, number in results[:how_many]]


def ask_rag(question, found):
    passages = "\n\n".join(f"From {c['source']}:\n{c['text']}" for c in found)
    prompt = f"""Answer the question using only the passages below.
If they don't contain the answer, say that you don't know.

{passages}

Question: {question}"""
    response = client.responses.create(model="gpt-5.4-mini", input=prompt)
    return response.output_text.strip()


def judge_answer(question, expected, found, system_answer):
    passages = "\n\n".join(f"From {c['source']}:\n{c['text']}" for c in found)
    prompt = f"""You are grading a RAG system on two separate criteria.

Question: {question}
Reference answer: {expected}

Retrieved passages:
{passages}

System answer: {system_answer}

Return JSON with three keys:
- "faithful": true if the system answer only states facts supported by the retrieved passages (or says it does not know when the passages lack the answer), false if it invents or extrapolates facts not in the passages.
- "correct": true ONLY if the system answer gives the same factual answer as the reference answer. If the reference answer is a specific fact (not "Not in the documents") and the system says "I don't know", "correct" MUST be false.
- "reason": one short sentence explaining both grades.
Return only raw JSON."""
    response = client.responses.create(model="gpt-5.4-mini", input=prompt)
    text = response.output_text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(text)


results = []
for q in questions:
    found = find_best_chunks(embed(q["question"]))
    found_files = [c["source"] for c in found]
    hit = any(source in found_files for source in q["sources"])
    answer = ask_rag(q["question"], found)
    verdict = judge_answer(q["question"], q["answer"], found, answer)
    results.append({**q, "found": found_files, "hit": hit, "system_answer": answer, **verdict})
    mark = "right" if verdict["correct"] else "WRONG"
    print(f"{q['id']}  file found: {'yes' if hit else 'no '}  answer: {mark}  | {answer[:70]}")

right_file = sum(r["hit"] for r in results)
right_answer = sum(r["correct"] for r in results)
print(f"\n{parser_name}: right file in the top 4 for {right_file} of {len(results)} table questions,"
      f" right answer for {right_answer} of {len(results)}")

with open(INDEX_FOLDER / "table-results.json", "w") as file:
    json.dump(results, file, indent=1)
