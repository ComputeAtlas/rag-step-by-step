"""Check an answer's citations, the simple way, with no model call:

1. every cited number, like [3], must be a passage we really sent;
2. every number in the answer (a price, a percentage, a cycle count) must appear in a passage
   it cites, or in the question itself.

A failed check doesn't prove the answer wrong. It flags the answer for a person to look at."""
import re


def check_citations(question, answer, found):
    problems = []
    cited = [int(n) for n in re.findall(r"\[(\d+)\]", answer)]
    if not cited:
        problems.append("no citation")
    for n in cited:
        if n < 1 or n > len(found):
            problems.append(f"[{n}] is not one of the passages")

    cited_text = " ".join(found[n - 1]["text"] for n in cited if 1 <= n <= len(found))
    answer_without_citations = re.sub(r"\[\d+\]", "", answer)
    for number in re.findall(r"\d[\d,.]*\d|\d", answer_without_citations):
        if number not in cited_text and number not in question:
            problems.append(f"{number} is not in the cited passages")
    return problems
