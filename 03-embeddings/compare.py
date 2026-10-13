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


def embed(text):
    response = client.embeddings.create(model="text-embedding-3-small", input=text)
    return np.array(response.data[0].embedding)


def similarity(a, b):
    # OpenAI's vectors all have length 1, so the dot product is the cosine similarity.
    return np.dot(a, b)


question = input("Your question: ")
question_vector = embed(question)

results = []
for page in pages:
    score = similarity(question_vector, embed(page))
    results.append((score, page))

results.sort(reverse=True)  # highest score first

for score, page in results:
    print(f"{score:.2f}  {page}")
