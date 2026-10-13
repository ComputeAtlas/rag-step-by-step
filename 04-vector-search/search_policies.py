"""Ask the Chroma database for the three closest chunks, searching only the policies."""
import chromadb
from openai import OpenAI

client = OpenAI()
db = chromadb.PersistentClient(path="chroma_db")  # the database build_db.py saved
collection = db.get_collection(name="fernhill")

question = "How much does a brake service cost?"
response = client.embeddings.create(model="text-embedding-3-small", input=question)
question_vector = response.data[0].embedding

results = collection.query(
    query_embeddings=[question_vector],
    n_results=3,
    where={"type": "policy"},  # only chunks whose type label is "policy"
)

print("Question:", question)
texts = results["documents"][0]
labels = results["metadatas"][0]
distances = results["distances"][0]
for text, label, distance in zip(texts, labels, distances):
    # Chroma gives a distance: smaller is closer. 1 - distance is the similarity score.
    score = 1 - distance
    print(f"{score:.2f}  {label['type']:<7} {label['file']}")
    print("     ", text.split("\n")[0][:55])  # the first line of the chunk
