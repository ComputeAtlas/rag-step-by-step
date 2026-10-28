"""Agentic RAG: the model decides when to search, what to search for, and when it has enough.

One step = one model call. At each step the model either asks for searches or answers:
  think -> search -> read -> decide (search again, or answer)
A hard cap stops a loop that goes wrong: on the last step the model must answer."""
import json
import textwrap
import time

from openai import OpenAI

from costs import add_usage, dollars, new_usage
from search_tool import SEARCH_TOOL, as_text, search_documents

client = OpenAI()
MODEL = "gpt-5.4-mini"
MAX_STEPS = 6  # at most six model calls per question

INSTRUCTIONS = """You answer questions about Fernhill Bikes, a maker of electric bikes.
Use the search_documents tool to find facts in Fernhill's documents, and answer only from what it returns.
A question may need several facts: search for each one.
Before each search, say in one short sentence what you still need to find.
After each search, check the passages: if a fact you need is missing, search again with different words.
When you have every fact, answer in one or two sentences. If the documents still don't contain the answer
after a few tries, say that you don't know."""


def run_agent(question):
    conversation = [
        {"role": "system", "content": INSTRUCTIONS},
        {"role": "user", "content": question},
    ]
    steps = []   # what happened at each step, for printing
    read = []    # every chunk the model has read
    usage = new_usage()
    start = time.time()
    for step in range(1, MAX_STEPS + 1):
        last_step = step == MAX_STEPS
        response = client.responses.create(
            model=MODEL,
            input=conversation,
            tools=[SEARCH_TOOL],
            parallel_tool_calls=False,  # one search per step
            tool_choice="none" if last_step else "auto",  # last step: answer
        )
        add_usage(usage, response.usage)
        conversation += response.output  # what it said and asked for
        said = response.output_text.strip()
        requests = []
        for item in response.output:
            if item.type == "function_call":
                requests.append(item)

        if not requests:  # no search asked for: this is the answer
            steps.append({"step": step, "answer": said, "forced": last_step})
            break

        searches = []
        for request in requests:
            query = json.loads(request.arguments)["query"]
            found = search_documents(query)
            read += found
            searches.append({"query": query, "files": [c["source"] for c in found]})
            conversation.append({
                "type": "function_call_output",
                "call_id": request.call_id,
                "output": as_text(found),
            })
        steps.append({"step": step, "think": said, "searches": searches})

    return {
        "answer": steps[-1].get("answer", ""),
        "steps": steps,
        "read": read,
        "searches": [s["query"] for step in steps for s in step.get("searches", [])],
        "usage": usage,
        "seconds": time.time() - start,
    }


def short_name(source):
    return source.split("/")[-1]


def wrap(text, indent):
    """Wrap a long line to 64 characters, indenting the lines after the first."""
    return textwrap.fill(text, 64, subsequent_indent=" " * indent, break_on_hyphens=False)


def show_steps(question, result):
    """Print the run step by step, the way the lesson shows it."""
    print(wrap(f"Question: {question}", 10))
    for step in result["steps"]:
        print()
        label = f"Step {step['step']}"
        if "answer" in step:
            print(wrap(f"{label}  answer  {step['answer']}", 16))
            continue
        print(wrap(f"{label}  think   {step['think'] or '(no words)'}", 16))
        for search in step["searches"]:
            print(wrap(f"        search  \"{search['query']}\"", 17))
            files = []
            for source in search["files"]:
                if short_name(source) not in files:
                    files.append(short_name(source))
            print(wrap(f"        found   {', '.join(files)}", 16))
    u = result["usage"]
    print()
    print(f"{u['calls']} model calls · {len(result['searches'])} searches · "
          f"{u['input'] + u['output']:,} tokens · ${dollars(u):.4f} · {result['seconds']:.1f} s")
