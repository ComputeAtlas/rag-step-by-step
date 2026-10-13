from openai import OpenAI

# The client reads your API key from the OPENAI_API_KEY environment variable.
client = OpenAI()

response = client.embeddings.create(
    model="text-embedding-3-small",
    input="How do I fix a flat?",
)

vector = response.data[0].embedding

print("How many numbers:", len(vector))
print("The first five:", vector[:5])
