"""Two ways to score the same two chunks for one question:
- the embedding (a bi-encoder): question and chunk are turned into numbers separately;
- the reranker (a cross-encoder): it reads the question and the chunk together."""
from reranker import chunks, reranker
from searches import vector_search

question = "On what date was firmware v2.1 released?"
answer_file = "release-notes/firmware-v2.1.md"  # the page with the answer

vector_results = vector_search(question, how_many=len(chunks))
vector_place = {}
vector_score = {}
for place, (score, number) in enumerate(vector_results, start=1):
    vector_place[number] = place
    vector_score[number] = score

top_by_vector = vector_results[0][1]  # the chunk the embeddings like best

answer_chunk = None
for number, chunk in enumerate(chunks):
    if chunk["source"] == answer_file:
        answer_chunk = number  # the first chunk of that page: it holds the release date
        break

print("Question:", question)
for number in [top_by_vector, answer_chunk]:
    reranker_score = reranker.predict([(question, chunks[number]["text"])])[0]
    print()
    print(chunks[number]["source"].split("/")[-1])
    print("  ", chunks[number]["text"][:29], "...")  # how the chunk starts
    print(f"   embedding score {vector_score[number]:.2f}  (place {vector_place[number]})")
    print(f"   reranker score  {reranker_score:.3f}")
