"""The same question, asked by a customer and by the support team.

Every chunk carries a label from its file: staff-only (support tickets, dealer files) or for everyone.
The filter runs inside the search, before the best four are picked, so a customer still gets four
chunks: four they are allowed to see.

    python 18-rag-in-production/permissions_demo.py"""
import sys

from pipeline import answer, load_baseline_index, may_see

question = sys.argv[1] if len(sys.argv) > 1 else "My Metro 300 charger gets very hot. What should I do?"
index = load_baseline_index()

print("Question:", question)
for role in ["staff", "customer"]:
    text, found, trace = answer(question, index, role)
    print()
    print(f"As {role}: the four chunks the model reads")
    for chunk in found:
        label = "everyone" if may_see(chunk, "customer") else "STAFF ONLY"
        print(f"  {label:<10}  {chunk['source']}")
    print("Answer:", text)
