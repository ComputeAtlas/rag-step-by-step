"""Embed every Fernhill chunk with OpenAI and store it in a Chroma database on disk, with its labels."""
import chromadb
from openai import OpenAI

from chunks import load_chunks

client = OpenAI()
chunks = load_chunks()
print("Chunks:", len(chunks))

# Embed the chunks, 100 at a time (one request for each batch of 100).
vectors = []
for start in range(0, len(chunks), 100):
    batch = [chunk["text"] for chunk in chunks[start:start + 100]]
    response = client.embeddings.create(model="text-embedding-3-small", input=batch)
    vectors += [item.embedding for item in response.data]

# Open the database (Chroma keeps it in the folder chroma_db) and a collection inside it.
db = chromadb.PersistentClient(path="chroma_db")
collection = db.get_or_create_collection(
    name="fernhill",
    configuration={"hnsw": {"space": "cosine"}},  # compare by cosine similarity
)

# Upsert = add each chunk, or update it if a chunk with that id is already stored.
collection.upsert(
    ids=[chunk["id"] for chunk in chunks],
    documents=[chunk["text"] for chunk in chunks],
    embeddings=vectors,
    metadatas=[{"file": chunk["file"], "type": chunk["type"]} for chunk in chunks],
)
print("Stored in chroma_db:", collection.count(), "chunks")
