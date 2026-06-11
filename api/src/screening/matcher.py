"""
Name normalisation and two-stage matching engine.

Stage 1 — Exact match: normalised query == normalised primary_name or any alias.
Stage 2 — Fuzzy composite: JaroWinkler + token_sort_ratio average, threshold
configurable.
"""

import re

from rapidfuzz import fuzz
from rapidfuzz.distance import JaroWinkler

from src.ingestion.models import SanctionEntry


def normalise(name: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    lowered = name.lower()
    stripped = re.sub(r"[^\w\s]", " ", lowered)
    return re.sub(r"\s+", " ", stripped).strip()


def _composite_score(query: str, candidate: str) -> float:
    jaro = JaroWinkler.similarity(query, candidate)
    tsort = fuzz.token_sort_ratio(query, candidate) / 100.0
    return (jaro + tsort) / 2.0


def find_top_match(
    normalised_query: str,
    candidates: list[SanctionEntry],
    threshold: float = 0.85,
) -> tuple[SanctionEntry | None, float]:
    """
    Find the best-matching SanctionEntry from the candidate list.

    Returns (entry, score) for the top scorer above `threshold`,
    or (None, 0.0) if no candidate clears the threshold.
    """
    # Stage 1: exact match
    for entry in candidates:
        names = [normalise(entry.primary_name)] + [normalise(a) for a in entry.aliases]
        if normalised_query in names:
            return entry, 1.0

    # Stage 2: fuzzy composite
    best_entry: SanctionEntry | None = None
    best_score = 0.0

    for entry in candidates:
        names = [normalise(entry.primary_name)] + [normalise(a) for a in entry.aliases]
        entry_score = max(_composite_score(normalised_query, n) for n in names)
        if entry_score > best_score:
            best_score = entry_score
            best_entry = entry

    if best_score >= threshold:
        return best_entry, best_score

    return None, 0.0
