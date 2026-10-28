"""The judge from the measuring lesson, unchanged: gpt-5.4-mini grades an answer against the
reference answer of a test question. The same judge graded every system on the scoreboard."""
import json

from openai import OpenAI

client = OpenAI()


def judge_answer(question, expected, found, system_answer, usage):
    passages = "\n\n".join(f"From {s['source']}:\n{s['text']}" for s in found)
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
    usage["in"] += response.usage.input_tokens
    usage["out"] += response.usage.output_tokens
    text = response.output_text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(text)
