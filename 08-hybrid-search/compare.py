"""Search one question three ways and print the four best chunks of each search.
Also print where the page that holds the answer ended up in each list.

    python 08-hybrid-search/compare.py
    python 08-hybrid-search/compare.py "your question" folder/file-with-the-answer.md"""
import sys

from searches import chunks, fuse, keyword_search, vector_search, words

question = "What fits part FH-2291-B?"
answer_file = "parts/batteries-and-chargers.md"  # the price list that says which bikes it fits
if len(sys.argv) == 3:
    question = sys.argv[1]
    answer_file = sys.argv[2]


def file_name(number):
    return chunks[number]["source"].split("/")[-1]  # without the folder


def show(title, results, decimals):
    print(title)
    for place, (score, number) in enumerate(results[:4], start=1):
        print(f"  {place}.  {score:.{decimals}f}  {file_name(number)}")
    for place, (score, number) in enumerate(results, start=1):
        if chunks[number]["source"] == answer_file:
            print(f"  {answer_file.split('/')[-1]} is at place {place}\n")
            return
    print(f"  {answer_file.split('/')[-1]} is not in the list\n")


vector_results = vector_search(question)
keyword_results = keyword_search(question)
hybrid_results = fuse(vector_results, keyword_results)

print("Question:", question)
print("Words for the keyword search:", words(question))
print()
show("Vector search", vector_results, 2)
show("Keyword search (BM25)", keyword_results, 2)
show("Hybrid search (Reciprocal Rank Fusion)", hybrid_results, 4)
