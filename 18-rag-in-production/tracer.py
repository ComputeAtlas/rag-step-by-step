"""A tiny tracer: it writes down how long each step of one question takes.

- A trace is the record of one question, from the moment it arrives to the answer.
- A span is one step inside it: its name and how long it took.

Real tracing tools (Langfuse, LangSmith, OpenTelemetry) record the same two things,
and give you a web page to look through them."""
import time
import uuid


def new_trace(question):
    return {"id": uuid.uuid4().hex[:6], "question": question, "spans": [],
            "tokens": {"embedding": 0, "input": 0, "output": 0}}


def start_span():
    return time.perf_counter()


def end_span(trace, name, started, note=""):
    milliseconds = (time.perf_counter() - started) * 1000
    trace["spans"].append({"name": name, "ms": milliseconds, "note": note})


def total_ms(trace):
    return sum(span["ms"] for span in trace["spans"])


def print_trace(trace):
    total = total_ms(trace)
    print(f"trace {trace['id']}   total {total:,.0f} ms")
    for span in trace["spans"]:
        share = span["ms"] / total * 100
        print(f"  {span['name']:<18} {span['ms']:>7,.1f} ms {share:>4.0f}%  {span['note']}")
