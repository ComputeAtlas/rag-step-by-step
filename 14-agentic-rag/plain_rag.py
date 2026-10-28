"""Plain RAG, for comparison: one search with the question as it is, then one answer
from the four chunks it found (the same prompt as the baseline)."""
import time

from openai import OpenAI

from costs import add_usage, new_usage
from search_tool import as_text, search_documents

client = OpenAI()
MODEL = "gpt-5.4-mini"


def ask_plain_rag(question):
    start = time.time()
    usage = new_usage()
    found = search_documents(question)
    prompt = f"""Answer the question using only the passages below.
If they don't contain the answer, say that you don't know.

{as_text(found)}

Question: {question}"""
    response = client.responses.create(model=MODEL, input=prompt)
    add_usage(usage, response.usage)
    return {"answer": response.output_text.strip(), "read": found, "searches": [question],
            "usage": usage, "seconds": time.time() - start}
