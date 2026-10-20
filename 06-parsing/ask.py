"""Ask one question against one of the indexes built by build_index.py, and print what the search found and the
answer. The same search and the same prompt as the first RAG.

Run from the repository root:
    python 06-parsing/ask.py pdfs-pdfplumber "What is the telephone number of the Wexcombe Service Centre?"
"""
import json
import sys
from pathlib import Path

import numpy as np
from openai import OpenAI

client = OpenAI()

index_name = sys.argv[1]
question = sys.argv[2]
INDEX_FOLDER = Path(__file__).parent / "index" / index_name

with open(INDEX_FOLDER / "chunks.json") as file:
    chunks = json.load(file)
vectors = np.load(INDEX_FOLDER / "vectors.npy")


def embed(text):
    response = client.embeddings.create(model="text-embedding-3-small", input=text)
    return np.array(response.data[0].embedding)


def find_best_chunks(question_vector, how_many=4):
    results = []
    for number, vector in enumerate(vectors):
        score = float(np.dot(question_vector, vector))
        results.append((score, number))
    results.sort(reverse=True)
    return [(score, chunks[number]) for score, number in results[:how_many]]


found = find_best_chunks(embed(question))
for score, chunk in found:
    print(f"{score:.2f}  {chunk['source']}")

passages = "\n\n".join(f"From {chunk['source']}:\n{chunk['text']}" for score, chunk in found)
prompt = f"""Answer the question using only the passages below.
If they don't contain the answer, say that you don't know.

{passages}

Question: {question}"""
response = client.responses.create(model="gpt-5.4-mini", input=prompt)
print("\nAnswer:", response.output_text.strip())
