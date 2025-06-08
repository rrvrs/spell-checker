import os
from collections import deque


def load_medical_terms(filepath):
    if not os.path.exists(filepath):
        return set()

    with open(filepath, 'r', encoding='utf-8') as f:
        return set(line.strip().lower() for line in f if line.strip())


def edit_distance_candidates(word, vocab, config):
    max_distance = config.get("max_distance", 2)
    max_candidates = config.get("max_candidates", 20)

    candidates = []
    for v in vocab:
        d = levenshtein(word, v)
        if d <= max_distance:
            candidates.append((v, d))

    # Sort by distance then alphabetically
    candidates.sort(key=lambda x: (x[1], x[0]))
    return [w for w, _ in candidates[:max_candidates]]


def levenshtein(a, b):
    if len(a) < len(b):
        return levenshtein(b, a)

    if len(b) == 0:
        return len(a)

    previous_row = range(len(b) + 1)
    for i, c1 in enumerate(a):
        current_row = [i + 1]
        for j, c2 in enumerate(b):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]
