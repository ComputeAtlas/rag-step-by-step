"""Small helpers for sending pictures to a vision-language model (a chat model that can also look at pictures).

gpt-5.4-mini accepts pictures in the same message as text. A picture is sent as a "data URL": the file's bytes written
out as base64 text. The other files of this lesson import this one.
"""
import base64
from pathlib import Path

from openai import OpenAI

client = OpenAI()
MODEL = "gpt-5.4-mini"
PRICE_INPUT = 0.75 / 1_000_000    # dollars per input token (OpenAI price list, October 2026)
PRICE_OUTPUT = 4.50 / 1_000_000   # dollars per output token

CAPTION_PROMPT = """This picture is one page of Fernhill Bikes' documents.
Write out everything on it as plain text, so that it can be searched:
- copy every heading, sentence, table row and number exactly;
- if there is a drawing, a diagram or a chart, describe it in two or three sentences
  and copy every label and value it shows, saying which part each one belongs to.
Write only the page's text and descriptions, no comments of your own."""


def picture_as_data_url(path):
    path = Path(path)
    kind = "png" if path.suffix == ".png" else "jpeg"
    data = base64.b64encode(path.read_bytes()).decode()
    return f"data:image/{kind};base64,{data}"


def ask_with_pictures(prompt, picture_paths):
    """Send one prompt and some pictures; return the answer and what it cost."""
    content = [{"type": "input_text", "text": prompt}]
    for path in picture_paths:
        content.append({"type": "input_image", "image_url": picture_as_data_url(path)})
    response = client.responses.create(model=MODEL, input=[{"role": "user", "content": content}])
    usage = response.usage
    dollars = usage.input_tokens * PRICE_INPUT + usage.output_tokens * PRICE_OUTPUT
    return response.output_text.strip(), {"input_tokens": usage.input_tokens,
                                          "output_tokens": usage.output_tokens, "dollars": dollars}


def answer_from_pictures(question, picture_paths):
    prompt = f"""Answer the question using only the pages in the pictures.
If they don't contain the answer, say that you don't know.
Reply in plain text, without formatting.

Question: {question}"""
    return ask_with_pictures(prompt, picture_paths)
