"""
Test Suite for Deduplication Engine
Covers: Content hashing, n-gram Jaccard similarity, and cross-run duplicate prevention.
"""

from src.deduplication import calculate_content_hash, compute_jaccard_similarity, check_for_duplicates


def test_hash_stability():
    t1 = "Stop wasting 18 hours per week on manual repurposing!"
    t2 = "stop  wasting 18 hours per week on manual repurposing. "
    assert calculate_content_hash(t1) == calculate_content_hash(t2)


def test_jaccard_similarity_near_duplicates():
    base = "How creators can turn 1 core blog post into 30 platform-native assets without burning out."
    near_dup = "How creators can turn 1 long blog post into 30 platform-native assets without burning out."
    different = "The fundamentals of database indexing in PostgreSQL and SQLite architecture."

    sim_high = compute_jaccard_similarity(base, near_dup)
    sim_low = compute_jaccard_similarity(base, different)

    assert sim_high > 0.85
    assert sim_low < 0.25


def test_duplicate_prevention_check():
    existing_pool = [
        "Stop wasting 18 hours every single week on manual formatting.",
        "The 1-to-30 multiplication framework for solo creators and digital agencies."
    ]

    is_dup, score, matched = check_for_duplicates(
        "Stop wasting 18 hours every single week on manual formatting!",
        existing_pool
    )
    assert is_dup is True
    assert score >= 0.90

    is_dup2, score2, _ = check_for_duplicates(
        "A completely brand new guide to newsletter growth via Substack recommendations.",
        existing_pool
    )
    assert is_dup2 is False
    assert score2 < 0.50
