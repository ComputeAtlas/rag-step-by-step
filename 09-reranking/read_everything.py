"""Why not let the reranker read every chunk? Time it: 30 candidates, then all 288 chunks."""
import statistics
import time

from reranker import chunks, first_stage, rerank

question = "On what date was firmware v2.1 released?"

candidates = first_stage(question)  # 30 chunks
every_chunk = []
for number in range(len(chunks)):
    every_chunk.append((0.0, number))  # all 288, in no order


def seconds_to_rerank(chunk_list, repeats=5):
    times = []
    for repeat in range(repeats):
        start = time.perf_counter()
        rerank(question, chunk_list)
        times.append(time.perf_counter() - start)
    return statistics.median(times)


rerank(question, candidates)  # warm the model up once
thirty = seconds_to_rerank(candidates)
everything = seconds_to_rerank(every_chunk)
per_chunk = everything / len(chunks)

print(f"Rerank 30 candidates:  {thirty * 1000:6.0f} ms")
print(f"Rerank all {len(chunks)} chunks: {everything * 1000:6.0f} ms")
print(f"Per chunk:             {per_chunk * 1000:6.2f} ms")
hours = per_chunk * 10_000_000 / 3600
print(f"10 million chunks, at the same speed: {hours:.0f} hours for one question")
