"""One question, asked two ways: plain RAG (one search, then answer) and the agent
(it searches as often as it needs, then answers). Pass your own question to try another."""
import sys

from agent import run_agent, short_name, show_steps, wrap
from costs import dollars
from plain_rag import ask_plain_rag

DEFAULT = ("A customer returns a new Ridge 500 within 30 days and Fernhill collects it by courier. "
           "How much is refunded if the bike cost the list price?")
question = sys.argv[1] if len(sys.argv) > 1 else DEFAULT

plain = ask_plain_rag(question)
files = []
for chunk in plain["read"]:
    if short_name(chunk["source"]) not in files:
        files.append(short_name(chunk["source"]))
print("PLAIN RAG (one search)")
print(wrap(f"found   {', '.join(files)}", 8))
print(wrap(f"answer  {plain['answer']}", 8))
u = plain["usage"]
print(f"{u['calls']} model call · 1 search · {u['input'] + u['output']:,} tokens · "
      f"${dollars(u):.4f} · {plain['seconds']:.1f} s")
print()
print("AGENT (it decides when to search)")
show_steps(question, run_agent(question))
