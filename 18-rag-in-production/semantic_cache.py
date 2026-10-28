"""A semantic cache: remember answers, and reuse one when a new question means the same thing.

An exact cache only helps when someone types the very same words again. This one compares
meaning instead: it embeds every question, and if a remembered question is close enough
(similarity at or above THRESHOLD), it hands back the remembered answer without asking the model.

Cached answers are kept per role, so a customer is never handed an answer written from staff-only documents."""
import numpy as np

THRESHOLD = 0.90  # picked by testing pairs of our own questions (see cache_demo.py)

cache = []  # one entry per remembered answer


def look_up(question_vector, role):
    """The closest remembered question for this role. Returns (entry or None, similarity)."""
    best_entry = None
    best_score = 0.0
    for entry in cache:
        if entry["role"] != role:
            continue
        score = float(np.dot(question_vector, entry["vector"]))  # 1.0 = the same meaning
        if score > best_score:
            best_entry = entry
            best_score = score
    if best_score >= THRESHOLD:
        return best_entry, best_score
    return None, best_score


def remember(question_vector, question, answer, role):
    cache.append({"vector": question_vector, "question": question, "answer": answer, "role": role})


def forget_everything():
    """Call this whenever the documents change: old answers may now be wrong."""
    cache.clear()
