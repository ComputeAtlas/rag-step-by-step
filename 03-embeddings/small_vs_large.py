import numpy as np
from openai import OpenAI

client = OpenAI()

pages = [
    "Tyre puncture repair: take the wheel off, find the hole and patch the inner tube.",
    "Delivery: we charge a flat fee of 25 euros on every order.",
    "Battery warranty: 3 years or 800 full charge cycles, whichever comes first.",
    "Brakes: if the lever feels soft, tighten the brake cable.",
    "Charging: plug the charger into the battery and wait for the green light.",
]


def embed(text, model):
    response = client.embeddings.create(model=model, input=text)
    return np.array(response.data[0].embedding)


question = input("Your question: ")

# The same question and pages, once with each model.
for model in ["text-embedding-3-small", "text-embedding-3-large"]:
    question_vector = embed(question, model)

    results = []
    for page in pages:
        score = np.dot(question_vector, embed(page, model))
        results.append((score, page))
    results.sort(reverse=True)  # highest score first

    print()
    print(model)
    for score, page in results:
        print(f"{score:.2f}  {page}")
