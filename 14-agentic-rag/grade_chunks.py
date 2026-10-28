"""Grading what a search found, and searching again when it isn't good enough
(the idea behind corrective RAG). Pass your own question to try another.

1. search with the question
2. a model grades each passage: it copies the words that answer the question, or says NONE
3. if no passage helps, the model writes a new search, and we search again"""
import sys

from openai import OpenAI

from agent import short_name
from search_tool import search_documents

client = OpenAI()
MODEL = "gpt-5.4-mini"


def ask(prompt):
    response = client.responses.create(model=MODEL, input=prompt)
    return response.output_text.strip()


def grade_passage(question, chunk):
    """One model call grades one passage: it copies the words that answer the question,
    or says NONE. NONE = the passage doesn't help."""
    prompt = f"""Question: {question}

Passage:
{chunk['text']}

Copy the exact words from the passage that answer the question.
If the passage does not answer it, reply with just: NONE"""
    words = ask(prompt)
    if words.upper().startswith("NONE"):
        return ""
    return words


def grade_passages(question, found):
    return [grade_passage(question, chunk) for chunk in found]


def new_search(question, found):
    """One model call writes a better search for the documents."""
    prompt = f"""A search for this question found nothing useful: {question}
It found passages from: {', '.join(c['source'] for c in found)}.
Write one new search query, in the words a company document would use.
Reply with the query only, without quote marks."""
    return ask(prompt).replace('"', "")


def show(found, quotes):
    for chunk, quote in zip(found, quotes):
        if quote:
            print(f"  yes  {short_name(chunk['source'])}")
            print(f'       "{quote[:48]}"')
        else:
            print(f"  no   {short_name(chunk['source'])}")


question = sys.argv[1] if len(sys.argv) > 1 else "On what date was firmware v2.1 released?"
print(f"Question: {question}")
print()
print(f'search  "{question}"')
found = search_documents(question)
quotes = grade_passages(question, found)
show(found, quotes)

if not any(quotes):
    query = new_search(question, found)
    print()
    print("No passage helps: search again.")
    print(f'search  "{query}"')
    found = search_documents(query)
    quotes = grade_passages(question, found)
    show(found, quotes)
