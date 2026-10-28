# 12 · Generation: grounded answers, citations, "I don't know"

Retrieval finds the pages. **Generation** is the last step: the model reads the chunks and writes the answer. What it
writes depends on the **prompt**, the one block of text it reads, built from a **prompt template** (a form with blanks
for the chunks and the question). This lesson changes nothing in the search: the same four chunks from the hybrid
search of `08-hybrid-search/`, the same model. Only the words around the chunks change.

- `prompts.py` holds the three templates and the helpers the other files import:
  - `bare_prompt`: the chunks and the question, no rules at all;
  - `plain_prompt`: the baseline's template ("answer using only the passages… say that you don't know");
  - `SYSTEM_PROMPT` + `grounded_prompt`: house rules sent as the **system prompt** (only the passages, cite them, you
    may combine facts and do simple sums, say when passages disagree and use the one that applies, and only then
    "I don't know"), and the chunks **numbered**, each with its file and its date (`document_date` reads it from the
    top of the document: effective, published, released, last updated, opened).
  - `find_chunks` (hybrid search, top 4), `ask` (one chat call; returns the answer and the tokens used) and
    `says_i_dont_know`.
- `citations.py` checks an answer's citations with no model call: every cited `[n]` must be a passage we sent, and
  every number in the answer must appear in a passage it cites (or in the question). A failed check flags the answer
  for a person; it doesn't prove it wrong (a sum like £109 + £34 = £143 is flagged too).
- `ask_one.py` asks one question with the plain prompt (three times) and with the grounded prompt. The default:
  `I bought my Ridge 500 on 10 December 2025. How long is its battery covered?`
- `show_prompt.py` prints the grounded prompt exactly as the model reads it.
- `conflict.py` asks about a battery at 65% on a bike bought in 2025: the 2025 policy (defective below 60%) and the 2026
  policy (below 70%) disagree.
- `unanswerable.py` asks the 10 questions the documents cannot answer with the bare, plain and grounded templates. Its
  count looks for the words "don't know", so a bare answer that declines in other words ("the documents don't state…")
  isn't counted: read the answers themselves.
- `two_orders.py` tests "lost in the middle": the same 20 chunks with the one that holds the answer first, in the
  middle or last (about 300 short chat calls).
- `token_budget.py` sends the grounded prompt with 4, 8 and 20 chunks and prints the tokens and the price.
- `show_answer.py` prints one graded answer from the saved results with its citation check (no API call), for
  example `python 12-generation/show_answer.py q081`.
- `judge_answers.py` answers all 100 test questions with one template (`grounded` or `plain`) and grades them with the
  baseline's judge prompt, word for word (200 chat calls). It also counts "I don't know" answers and runs the citation
  check. Answers are saved in `12-generation/results/` (generated files, not part of the repository).

You need `openai`, `numpy` and `rank_bm25` and your key in `OPENAI_API_KEY`. Build the baseline index first
(`python 05-measuring-rag/build_index.py`), then run from the repository root:

```bash
python 12-generation/ask_one.py
python 12-generation/show_prompt.py
python 12-generation/conflict.py
python 12-generation/unanswerable.py
python 12-generation/two_orders.py
python 12-generation/token_budget.py
python 12-generation/judge_answers.py plain
python 12-generation/judge_answers.py grounded
python 12-generation/show_answer.py q055
```

What we measured (gpt-5.4-mini, hybrid search top 4, 100 test questions): correct answers 75 with the plain prompt and
81 with the grounded prompt (the same plain setup scored 80 on another day, so a few points are run-to-run noise).
"I don't know" on questions the documents DO answer fell from 13 to 5; both templates refused all 10 unanswerable
questions, while the bare prompt with no rules made up 3 of those 10 answers. 76 of the 85 grounded answers passed the
citation check; 4 of the 9 it flagged were wrong. Four chunks cost about 1,100 tokens a question (about a tenth of a
cent); twenty chunks almost 6,000. Moving the chunk with the answer to the first, middle or last of 20 places barely
mattered for this model: 55, 54 and 57 right of 58 (no "lost in the middle" at this length).
