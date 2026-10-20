# 05 · Measuring a RAG system

Short programs that turn "I tried five questions and it looked good" into a repeatable scoreboard over the 100 test questions in `data/fernhill-questions.json`.

- `build_index.py` builds the same baseline index as Lesson 2 (288 chunks of 200 words from the 87 Fernhill files, embedded with `text-embedding-3-small`) and saves `chunks.json` and `vectors.npy` in `05-measuring-rag/index/`.
- `measure_retrieval.py` scores **retrieval** alone on the 80 single-search questions (one embedding call, zero chat calls). It prints three metrics overall and by category: **Hit rate @ 4** (`0.78`), **Recall @ 4** (`0.67`), and **MRR @ 4** (`0.64`).
- `judge_answers.py` runs the full RAG pipeline and grades **generation** with `gpt-5.4-mini` as an LLM judge on two separate criteria: **faithfulness** (did the answer stick to the retrieved passages?) and **answer correctness** (did it match the reference answer?). Run it with default diagnostic questions (`q001`, `q010`, `q064`, `q046`, `q029`) or pass any question IDs on the command line.
- `scoreboard.py` prints the full 100-question baseline scoreboard from `05-measuring-rag/index/results.json` and breaks the 19 single-search failures into retrieval misses, partial multi-document hits, and chunk/generator misses. Pass another results file name to score a new run: `python 05-measuring-rag/scoreboard.py results-new.json`.
- `save_results.py` runs all 100 questions through the bot and the judge and saves every result (question, retrieved chunks, answer, marks) in `05-measuring-rag/index/results-new.json`. It never overwrites `results.json`, the baseline. Run it twice and a few marks change: the model and the judge are not deterministic, the search is.

```bash
python 05-measuring-rag/build_index.py
python 05-measuring-rag/measure_retrieval.py
python 05-measuring-rag/judge_answers.py
python 05-measuring-rag/scoreboard.py
python 05-measuring-rag/save_results.py      # optional: a fresh full run, about 200 model calls
```
