"""One chunk, before and after contextual retrieval. It needs results/ from add_context.py.

The question is from the test set. The chunk that answers it is a table from the Metro 300
owner's manual, but the table itself never says which bike it is for."""
import textwrap

from searches import embed, load_contextual_index, load_plain_index, vector_search

QUESTION = "What torque is specified for the front axle nuts of the Metro 300?"
CHUNK = 59  # the torque table of manuals/metro-300-owners-manual.md

plain = load_plain_index()
contextual = load_contextual_index()
chunk = contextual["chunks"][CHUNK]


def place(index, question_vector):
    for number, (score, chunk_number) in enumerate(vector_search(index, question_vector), start=1):
        if chunk_number == CHUNK:
            return number


print("Question:", QUESTION)
print()
print(f"The chunk with the answer, from {chunk['source']}:")
print("  " + chunk["text"][:72] + " ...")
print("  ... | Front axle nuts | 25 Nm | ...")
print("Does the chunk say which bike?", "yes" if "Metro" in chunk["text"] else "no")
print()
print("The context gpt-5.4-mini wrote for it:")
for line in textwrap.wrap(chunk["context"], 72):
    print("  " + line)
print()
question_vector = embed([QUESTION])[0]
print("Its place in vector search:")
print(f"  without the context: {place(plain, question_vector)}")
print(f"  with the context:    {place(contextual, question_vector)}")
