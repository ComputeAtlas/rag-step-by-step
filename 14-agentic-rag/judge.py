"""The baseline's judge, unchanged: gpt-5.4-mini grades an answer against the reference answer."""
import json

from openai import OpenAI

from costs import add_usage
from search_tool import as_text

client = OpenAI()


def judge_answer(question, expected, read, system_answer, usage):
    prompt = f"""You are grading a RAG system on two separate criteria.

Question: {question}
Reference answer: {expected}

Retrieved passages:
{as_text(read)}

System answer: {system_answer}

Return JSON with three keys:
- "faithful": true if the system answer only states facts supported by the retrieved passages (or says it does not know when the passages lack the answer), false if it invents or extrapolates facts not in the passages.
- "correct": true ONLY if the system answer gives the same factual answer as the reference answer. If the reference answer is a specific fact (not "Not in the documents") and the system says "I don't know", "correct" MUST be false.
- "reason": one short sentence explaining both grades.
Return only raw JSON."""
    response = client.responses.create(model="gpt-5.4-mini", input=prompt)
    add_usage(usage, response.usage)
    text = response.output_text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(text)
