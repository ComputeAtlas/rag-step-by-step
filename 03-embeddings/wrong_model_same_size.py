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


def embed(text, model, size):
    # `dimensions` asks for a vector of that many numbers.
    response = client.embeddings.create(model=model, input=text, dimensions=size)
    return np.array(response.data[0].embedding)


question = "How do I fix a flat?"

# The quiet mistake: the question comes from the small model, the pages from the
# large one, cut down to 1536 numbers. Same length, so nothing complains.
question_vector = embed(question, "text-embedding-3-small", 1536)

results = []
for page in pages:
    score = np.dot(question_vector, embed(page, "text-embedding-3-large", 1536))
    results.append((score, page))
results.sort(reverse=True)  # highest score first

for score, page in results:
    print(f"{score:.2f}  {page}")
