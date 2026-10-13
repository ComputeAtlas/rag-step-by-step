from openai import OpenAI

# The client reads your API key from the OPENAI_API_KEY environment variable.
client = OpenAI()

response = client.responses.create(
    model="gpt-5.4-mini",
    input="In one sentence, what is an electric bike?",
)

print(response.output_text)
