"""The search tool the agent can use: the hybrid search from the hybrid-search lesson
(vectors + keywords, merged with Reciprocal Rank Fusion), described so a model can ask for it."""
import sys

sys.path.append("08-hybrid-search")  # reuse the hybrid search from the hybrid-search lesson
from searches import chunks, hybrid_search

# The model never sees our Python code. It only sees this description,
# and it answers with a request: "please run search_documents with this query".
SEARCH_TOOL = {
    "type": "function",
    "name": "search_documents",
    "description": "Search Fernhill Bikes' documents (manuals, parts, "
                   "prices, policies, release notes, support tickets). "
                   "Returns the four best passages.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "What to look for. One fact per search.",
            },
        },
        "required": ["query"],
        "additionalProperties": False,
    },
    "strict": True,
}


def search_documents(query, how_many=4):
    """Run the hybrid search and return the best chunks."""
    found = []
    for points, number in hybrid_search(query)[:how_many]:
        found.append(chunks[number])
    return found


def as_text(found):
    """The passages as one text, the way the model reads them."""
    return "\n\n".join(f"From {c['source']}:\n{c['text']}" for c in found)
