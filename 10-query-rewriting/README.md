# 10 · Asking better questions: query rewriting, HyDE, multi-query

The search only ever sees the words it is given. Real users type follow-ups ("it broke again??"), use their own words
("where can i watch the bikes being built") or ask two things at once. This lesson changes the question **before** the
search, with one small model call each:

- **Rewriting a follow-up**: the model reads the chat so far and turns the last message into a question that makes
  sense on its own.
- **Many ways to ask (multi-query)**: the model writes three other versions of the question; we search with all four
  and merge the lists by their places (Reciprocal Rank Fusion).
- **An imagined answer (HyDE)**: the model writes a made-up answer; we search for real chunks that look like it. The
  made-up answer is only used for searching, never shown.
- **Sub-questions**: a question that needs two facts becomes two simple questions, each searched on its own.
- **Routing**: the model picks the part of the library to search (manuals, parts, policies, support tickets, release
  notes, company), and we search only there.

Everything builds on the hybrid search of `08-hybrid-search` (keyword + vector search, merged by places) over the
same 288 chunks as the baseline. Build that index first with `python 05-measuring-rag/build_index.py`.

- `searching.py` reuses the hybrid search and adds `fuse_lists` (merge any number of ranked lists), `in_sections`
  (keep one part of the library) and `show` (print the four best files; a file the question needs gets a `+`).
- `rewriters.py` holds the five prompts, one short function each, all on `gpt-5.4-mini`.
- `follow_up.py`, `many_ways.py`, `imagined_answer.py`, `sub_questions.py`, `routing.py` each show one technique on one
  question: the search as asked, what the model wrote, and the search after it. Pass your own question in quotes,
  optionally followed by the files it needs (to mark them with `+`).
- `follow_up_questions.json`: 20 short chats whose last message only makes sense with the chat before it.
  `own_words_questions.json`: 20 questions in a customer's own words. Both were written for this lesson; each one
  means the same as a question of the test set (`same_as`), so it has a known answer and known source files.
- `make_rewrites.py` asks the model once for every rewrite the scoreboard needs (about 400 chat calls) and saves them
  in `10-query-rewriting/results/rewrites.json`, with how long each call took. A second run skips what is saved.
- `scoreboard.py` scores every way of asking (hit rate, recall and MRR at 4): on the follow-ups, on the questions in
  the customer's own words, and on the 80 single-search test questions. Only embedding calls.
- `judge_answers.py` answers the 20 follow-ups like a chat bot would (the chat, the last message, four chunks) with the
  chunks from the last message alone and from the rewrite, and grades both with the baseline's judge (80 chat calls).

Generated files go to `10-query-rewriting/results/` (not part of the repository).

You need `openai`, `numpy` and `rank_bm25` (`pip install openai numpy rank_bm25`) and your key in `OPENAI_API_KEY`.

```bash
python 10-query-rewriting/follow_up.py
python 10-query-rewriting/many_ways.py "where can i watch the bikes being built"
python 10-query-rewriting/imagined_answer.py "do you charge anything to take my old battery off my hands"
python 10-query-rewriting/sub_questions.py
python 10-query-rewriting/routing.py
python 10-query-rewriting/make_rewrites.py
python 10-query-rewriting/scoreboard.py
python 10-query-rewriting/judge_answers.py
```

What we measured (right file in the top 4):

| Questions | As typed | After the fix |
|---|---|---|
| 20 follow-ups | 10 | 15 rewritten (the same questions asked in full: 18) |
| 20 in a customer's own words | 14 | 15 rewritten, 15 many ways, 16 imagined answer |
| 80 test questions, already clear | 67 | 64 many ways, 65 imagined answer, 66 sub-questions, 65 routing |

Correct answers to the 20 follow-ups went from 10 to 15. Vector search alone went from 62 to 66 of 80 when it searched
with an imagined answer. On questions that are already clear, none of the five beat plain hybrid search: change the
question only when it needs it. Each fix costs one extra model call, about a second (median 1.0 to 1.4 s). With 20
questions, one question is five points: read those rows as a direction, not a precise score.
