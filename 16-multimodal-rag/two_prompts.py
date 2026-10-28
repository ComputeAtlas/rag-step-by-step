"""Caption one figure twice: with a plain "describe this picture" prompt, and with the prompt from caption_pages.py.

Run from the repository root:  python 16-multimodal-rag/two_prompts.py
"""
from vision import CAPTION_PROMPT, ask_with_pictures

figure = "16-multimodal-rag/figures/battery-capacity.png"

plain, cost = ask_with_pictures("Describe this picture in two or three sentences.", [figure])
print("Prompt: Describe this picture in two or three sentences.")
print(plain)
print()
careful, cost = ask_with_pictures(CAPTION_PROMPT, [figure])
print("Prompt: copy every label and value (caption_pages.py)")
print(careful)
