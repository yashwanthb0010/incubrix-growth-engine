"""
IncuBrix Deduplication Module
Detects exact and near-duplicate assets across runs to prevent spam and preserve diversity.
"""

import hashlib
import re
from typing import List, Tuple, Set


def normalize_for_comparison(text: str) -> str:
    """Lowercase and strip all punctuation and excess spaces."""
    cleaned = re.sub(r"[^\w\s]", "", text.lower())
    return " ".join(cleaned.split())


def calculate_content_hash(text: str) -> str:
    """Generates a stable SHA256 hex digest for normalized text."""
    normalized = normalize_for_comparison(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def compute_jaccard_similarity(text1: str, text2: str, n: int = 3) -> float:
    """Computes character n-gram Jaccard similarity between two texts."""
    norm1 = normalize_for_comparison(text1)
    norm2 = normalize_for_comparison(text2)
    if not norm1 or not norm2:
        return 0.0

    if norm1 == norm2:
        return 1.0

    ngrams1: Set[str] = {norm1[i:i + n] for i in range(max(1, len(norm1) - n + 1))}
    ngrams2: Set[str] = {norm2[i:i + n] for i in range(max(1, len(norm2) - n + 1))}

    intersection = len(ngrams1.intersection(ngrams2))
    union = len(ngrams1.union(ngrams2))
    return intersection / union if union > 0 else 0.0


def check_for_duplicates(
    new_text: str,
    existing_texts: List[str],
    threshold: float = 0.82
) -> Tuple[bool, float, str]:
    """
    Checks if new_text is an exact or near duplicate of any text in existing_texts.
    Returns: (is_duplicate, max_similarity, matched_sample)
    """
    new_norm = normalize_for_comparison(new_text)
    new_hash = calculate_content_hash(new_text)

    for existing in existing_texts:
        if calculate_content_hash(existing) == new_hash:
            return True, 1.0, existing[:80]

        sim = compute_jaccard_similarity(new_text, existing)
        if sim >= threshold:
            return True, sim, existing[:80]

    return False, 0.0, ""
