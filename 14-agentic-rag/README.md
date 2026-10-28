# 14 · Agentic RAG: letting the model decide when to search

Plain RAG searches **once**, with the question exactly as it was typed, and the model answers from whatever came back.
Some questions need more: two facts from two documents, or a second search that depends on what the first one found
("the motor is 1.5 hours of labour... so what is the hourly rate?").

Agentic RAG gives the model the search as a **tool**. The model never runs our code: it answers with a request
("please run `search_documents` with this query"), our code runs the search, and the passages go back to the model.
Then it decides again: search once more, or answer. That loop (think, search, read, decide) runs until the model
answers, or until a **hard cap** of six model calls, where the last call must answer.

The search tool is the hybrid search from `08-hybrid-search/` (vectors + keywords, merged with Reciprocal Rank Fusion),
four chunks per search, on the same 288 chunks as the baseline. Build that index first with
`python 05-measuring-rag/build_index.py`.

- `search_tool.py` describes the tool to the model (`SEARCH_TOOL`: a name, what it does, and its one parameter,
  `query`) and runs it (`search_documents`).
- `agent.py` is the loop (`run_agent`), with OpenAI's tool calling (function calling) and no agent framework.
  `MAX_STEPS = 6`; `parallel_tool_calls=False` so the model reads each search before asking for the next.
  `show_steps` prints a run step by step.
- `plain_rag.py` is plain RAG for comparison: one search, one answer, the baseline's prompt.
- `ask_both.py` asks one question both ways and prints every step. Try the default, then your own:
  `python 14-agentic-rag/ask_both.py "What does a Metro 300 owner pay to replace the hub motor at the service exchange price, including labour?"`
- `grade_chunks.py` grades what a search found (one model call per passage: copy the words that answer the question,
  or say NONE) and, when nothing helps, writes a new search and tries again. This is the idea behind corrective RAG.
- `check_answer.py` checks an answer before it goes out (is every fact in the passages? does it answer the whole
  question?) and, if the check fails, lets the agent try once more with the check's note.
- `costs.py` adds up tokens and turns them into dollars (gpt-5.4-mini prices).
- `judge.py` is the baseline's judge, unchanged.
- `scoreboard.py` answers all 100 test questions with plain RAG and with the agent, grades both, and prints correct
  answers, cost, time and how many searches the agent chose. About 600 model calls (roughly a dollar). Answers are saved
  in `14-agentic-rag/results/` (generated files, not part of the repository).

You need `openai`, `numpy` and `rank_bm25` (`pip install openai numpy rank_bm25`) and your key in `OPENAI_API_KEY`.

```bash
python 14-agentic-rag/ask_both.py
python 14-agentic-rag/grade_chunks.py
python 14-agentic-rag/check_answer.py
python 14-agentic-rag/scoreboard.py
```
