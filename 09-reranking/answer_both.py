"""Answer one question twice: from the first stage's top 4, and from the reranker's top 4.
Two chat calls."""
from openai import OpenAI

from reranker import chunks, first_stage, rerank

client = OpenAI()

question = "On what date was firmware v2.1 released?"


def ask(question, found):
    passages = "\n\n".join(f"From {c['source']}:\n{c['text']}" for c in found)
    prompt = f"""Answer the question using only the passages below.
If they don't contain the answer, say that you don't know.

{passages}

Question: {question}"""
    response = client.responses.create(model="gpt-5.4-mini", input=prompt)
    return response.output_text.strip()


candidates = first_stage(question)
before = [chunks[number] for score, number in candidates[:4]]
after = [chunks[number] for score, number in rerank(question, candidates)]

print("Question:", question)
print()
print("Without the reranker:", ask(question, before))
print("With the reranker:   ", ask(question, after))
