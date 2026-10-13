from openai import OpenAI

# The client reads your API key from the OPENAI_API_KEY environment variable.
client = OpenAI()

question = "How long is the battery warranty on a Fernhill e-bike?"

response = client.responses.create(
    model="gpt-5.4-mini",
    input=question,
)

print(response.output_text)
