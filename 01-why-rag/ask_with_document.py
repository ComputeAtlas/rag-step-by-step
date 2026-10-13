from openai import OpenAI

client = OpenAI()

question = "How long is the battery warranty on a Fernhill e-bike?"

# Read the company's warranty policy from a text file.
with open("data/fernhill/warranty-policy.md") as file:
    policy = file.read()

# Put the document and the question together in one prompt.
prompt = f"""Answer the question using only the document below.

Document:
{policy}

Question: {question}"""

response = client.responses.create(
    model="gpt-5.4-mini",
    input=prompt,
)

print(response.output_text)
