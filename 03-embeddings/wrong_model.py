import numpy as np
from openai import OpenAI

client = OpenAI()


def embed(text, model):
    response = client.embeddings.create(model=model, input=text)
    return np.array(response.data[0].embedding)


page = "Tyre puncture repair: take the wheel off, find the hole and patch the inner tube."
question = "How do I fix a flat?"

# The mistake: the page was embedded with the large model, the question with the small one.
page_vector = embed(page, "text-embedding-3-large")
question_vector = embed(question, "text-embedding-3-small")

print("Page:", len(page_vector), "numbers")
print("Question:", len(question_vector), "numbers")
print("Score:", np.dot(question_vector, page_vector))
