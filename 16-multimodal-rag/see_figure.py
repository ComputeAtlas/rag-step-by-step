"""Show one figure to a vision-language model and ask about it.

Run from the repository root:  python 16-multimodal-rag/see_figure.py
"""
from pathlib import Path

from vision import answer_from_pictures

question = "What torque do the clamp screws of the Ridge 500's display bracket need?"
figure = "16-multimodal-rag/figures/display-bracket.png"

answer, cost = answer_from_pictures(question, [figure])
print("Question:", question)
print("Picture: ", Path(figure).name)
print("Answer:  ", answer)
print(f"Tokens:   {cost['input_tokens']} in, {cost['output_tokens']} out  (${cost['dollars']:.4f})")
