import json
import sys
from pathlib import Path

import numpy as np
from openai import OpenAI

client = OpenAI()

INDEX_FOLDER = Path(__file__).parent / "index"

with open(INDEX_FOLDER / "chunks.json") as file:
    chunks = json.load(file)
vectors = np.load(INDEX_FOLDER / "vectors.npy")

with open("data/fernhill-questions.json") as file:
    questions_by_id = {q["id"]: q for q in json.load(file)}


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


sample_ids = sys.argv[1:] or ["q001", "q010", "q064", "q046", "q029"]

for qid in sample_ids:
    q = questions_by_id[qid]
    found = find_best_chunks(embed(q["question"]))
    found_files = [c["source"] for _, c in found]
    required = set(q["sources"])
    recall = len(required.intersection(found_files)) / len(required) if required else 0.0

    system_answer = ask_rag(q["question"], found)
    verdict = judge_answer(q["question"], q["answer"], found, system_answer)

    print(f"=== {q['id']} ({q['category']}) ===")
    print(f"Question  : {q['question']}")
    print(f"Expected  : {q['answer']}")
    print(f"Top 4     : {found_files}  (recall={recall:.2f})")
    print(f"Answer    : {system_answer}")
    print(f"Faithful  : {verdict['faithful']}   Correct: {verdict['correct']}")
    print(f"Reason    : {verdict['reason']}\n")
