"""Ask one question with RAG and with every document in the prompt.

    python 17-rag-vs-long-context/ask_one.py
    python 17-rag-vs-long-context/ask_one.py 'How many support tickets are about brakes?'"""
import sys

from two_ways import ask_with_everything, ask_with_rag

question = "How many support tickets are about brakes?"
if len(sys.argv) > 1:
    question = sys.argv[1]


def show(title, result):
    print(title)
    print("  answer:", result["answer"])
    print(f"  {result['input_tokens']:,} tokens in, {result['seconds']:.1f} s, ${result['dollars']:.4f}")


print("Question:", question)
print()
show("With RAG (4 chunks):", ask_with_rag(question))
print()
show("With all 87 documents:", ask_with_everything(question))
