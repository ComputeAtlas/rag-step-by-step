import json
import sys
from pathlib import Path

import numpy as np
from openai import OpenAI

client = OpenAI()

INDEX_FOLDER = Path(__file__).parent / "index"

# A new run gets its own file, so the baseline (index/results.json) is never overwritten.
output_name = sys.argv[1] if len(sys.argv) > 1 else "results-new.json"
OUTPUT_FILE = INDEX_FOLDER / output_name

with open(INDEX_FOLDER / "chunks.json") as file:
    chunks = json.load(file)
vectors = np.load(INDEX_FOLDER / "vectors.npy")

with open("data/fernhill-questions.json") as file:
    questions = json.load(file)


def embed(text):
    response = client.embeddings.create(model="text-embedding-3-small", input=text)
    return np.array(response.data[0].embedding)


def find_best_chunks(question_vector, how_many=4):
    results = []
    for number, vector in enumerate(vectors):
        score = float(np.dot(question_vector, vector))
        results.append((score, number))
    results.sort(reverse=True)
    return [(score, chunks[number]) for score, number in results[:how_many]]


def score_retrieval(required_sources, found_files):
    if not required_sources:
        return 0, 0.0, 0.0  # an unanswerable question has no file to find
    required = set(required_sources)
    matched = required.intersection(found_files)
    hit = 1 if matched else 0
    recall = len(matched) / len(required)
    mrr = 0.0
    for rank, source in enumerate(found_files, start=1):
        if source in required:
            mrr = 1.0 / rank
            break
    return hit, recall, mrr


def ask_rag(question, found):
    passages = "\n\n".join(f"From {c['source']}:\n{c['text']}" for _, c in found)
    prompt = f"""Answer the question using only the passages below.
If they don't contain the answer, say that you don't know.

{passages}

Question: {question}"""
    response = client.responses.create(model="gpt-5.4-mini", input=prompt)
    return response.output_text.strip()


def judge_answer(question, expected, found, system_answer):
    passages = "\n\n".join(f"From {c['source']}:\n{c['text']}" for _, c in found)
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
    found_files = [c["source"] for _, c in found]
    hit, recall, mrr = score_retrieval(q["sources"], found_files)
    answer = ask_rag(q["question"], found)
    verdict = judge_answer(q["question"], q["answer"], found, answer)
    results.append({
        "id": q["id"],
        "category": q["category"],
        "question": q["question"],
        "expected": q["answer"],
        "sources": q["sources"],
        "retrieved": [{"score": round(s, 4), "source": c["source"], "text": c["text"]} for s, c in found],
        "answer": answer,
        "faithful": verdict["faithful"],
        "correct": verdict["correct"],
        "reason": verdict["reason"],
        "hit": hit,
        "recall": recall,
        "mrr": mrr,
    })
    print(q["id"], "correct" if verdict["correct"] else "wrong")

with open(OUTPUT_FILE, "w") as file:
    json.dump(results, file, indent=1)
print("Saved", len(results), "results in", OUTPUT_FILE.name)
