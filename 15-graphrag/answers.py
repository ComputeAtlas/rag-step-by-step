"""The answering prompt and the judge, with the same prompts as the baseline
(05-measuring-rag/judge_answers.py), so the scores can be compared."""
from model import ask, ask_for_json


def ask_rag(question, found):
    passages = "\n\n".join(f"From {c['source']}:\n{c['text']}" for c in found)
    prompt = f"""Answer the question using only the passages below.
If they don't contain the answer, say that you don't know.

{passages}

Question: {question}"""
    return ask(prompt)


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
    return ask_for_json(prompt)
