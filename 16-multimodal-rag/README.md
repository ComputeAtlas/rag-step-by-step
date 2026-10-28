# 16 · Multimodal RAG: images, charts and scanned pages

Some answers are not written down: they are drawn. A torque value in a diagram, a value on a chart, a page that was
scanned. A text-only RAG system cannot see them, because a parser keeps text and leaves pictures behind. This lesson
tries three ways to search pictures, and measures them on the same 20 questions.

Fernhill's documents are text, so **we drew three manual figures for this lesson** (`make_figures.py` -> `figures/`).
Each one holds facts written only in the drawing. `figure-questions.json` has six questions about them. The other
pictures are the scanned copies of 33 Fernhill documents from `06-parsing/` (69 pages, no text inside).

- `make_figures.py` draws the three figures: a diagram (the Ridge 500 display bracket), a chart (battery capacity
  after charge cycles) and a side view (the Metro 300 rear carrier).
- `make_pages.py` turns every scanned page into a picture and adds the figures: 72 page pictures in
  `16-multimodal-rag/results/pages/`, listed in `results/pages.json`.
- `vision.py` holds the helpers for a **vision-language model** (`gpt-5.4-mini` reads pictures as well as text): send a
  prompt with pictures, answer a question from pictures, and the caption prompt. The other files import it.
- `ask_text_rag.py` asks the baseline text RAG (the index from `05-measuring-rag/`) about the display bracket: it
  answers "I don't know", because the figure was never text.
- `see_figure.py` shows the figure itself to the model: it reads the answer, and prints what the picture cost in tokens.
- `read_letters.py` reads a figure with **OCR** (Tesseract): it finds letters, but on a chart it loses the values and
  which value belongs where.

Approach 1, **turn pictures into text (image captioning)**:
- `two_prompts.py` captions the chart twice: with "describe this picture" (the values get lost) and with our prompt
  (copy every label and value).
- `caption_pages.py` captions all 72 pages (72 chat calls) and saves the text in `results/captions.json`.
- `caption_search.py` embeds one caption per page with `text-embedding-3-small`, searches them and answers from the text.

Approach 2, **one embedding space for pictures and text (CLIP)**:
- `clip_search.py` embeds every page picture with CLIP (`clip-ViT-B-32` from sentence-transformers, about 600 MB, runs
  on your own computer) and searches them with a text question in the same space.

Approach 3, **search the page pictures themselves (late interaction, the ColPali way)**:
- `page_search.py` embeds every page with ColQwen2 (`vidore/colqwen2-v1.0-hf`, about 4.4 GB, runs on your own computer:
  an Apple-silicon GPU, an NVIDIA GPU or, slowly, the CPU): one list of 128 numbers for every patch of the page. A
  question gets one list per token; each token takes its best-matching patch and the page's score adds them up
  (`late_interaction_score`, three lines).
- `ask_pages.py` searches with it and lets the vision-language model read the best four pages as pictures.

- `scoreboard.py` scores all three against the text baseline on 20 questions (14 table questions on the scanned pages
  and the 6 figure questions): was a right page in the top 4, and was the answer right (graded by `gpt-5.4-mini`)?
  About 140 chat calls. Generated files go to `16-multimodal-rag/results/` (not part of the repository).

Before you start: build the baseline index (`python 05-measuring-rag/build_index.py`) and the scans
(`python 06-parsing/make_pdfs.py` then `python 06-parsing/make_scans.py`). You need `openai`, `numpy`, `pymupdf`,
`pillow`, `sentence-transformers` (it brings `transformers` and `torch`, which ColQwen2 uses) and your key in
`OPENAI_API_KEY`; `read_letters.py` needs Tesseract installed (macOS: `brew install tesseract`).

```bash
python 16-multimodal-rag/make_figures.py
python 16-multimodal-rag/make_pages.py
python 16-multimodal-rag/ask_text_rag.py
python 16-multimodal-rag/see_figure.py
python 16-multimodal-rag/read_letters.py
python 16-multimodal-rag/two_prompts.py
python 16-multimodal-rag/caption_pages.py
python 16-multimodal-rag/caption_search.py
python 16-multimodal-rag/clip_search.py
python 16-multimodal-rag/page_search.py
python 16-multimodal-rag/ask_pages.py
python 16-multimodal-rag/scoreboard.py
```

What we measured (Apple M4 Pro), on 20 questions:

| Approach | Right page in the top 4 | Right answers | Cost per page (indexing) | Answer cost per question |
|---|---|---|---|---|
| Text only (the baseline) | 14 | 12 (no figure) | | |
| Captions | 20 | 18 | $0.0044 (72 pages: $0.32, 4 minutes) | $0.0017 |
| One space (CLIP) | 9 | 8 | free, ~20 ms | $0.0075 (reads 4 pictures) |
| Page pictures (ColQwen2) | 20 | 19 | free, 2-3 s, 747 vectors of 128 numbers | $0.0077 (reads 4 pictures) |

CLIP found every figure but only 3 of the 14 table pages: it sees what a page looks like (shrunk to 224 x 224 pixels),
not the small print. The chart tripped up the other two: in the full captioning run the same prompt wrote the chart as a
bare list of numbers, with nothing pairing them, so "how much capacity after 400 cycles?" was answered 86% (the chart
says 90%). Read your captions. With 20 questions, a difference of one or two is within the noise of a re-run.
