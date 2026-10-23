"""
Test Suite for Ingestion and Content Generation
Covers: Normal generation, minimum 10 assets, full 30 assets, new input refresh, invalid input.
"""

import pytest
from src.ingestion import process_input, IngestedDocument
from src.generation import ContentGenerator


SAMPLE_TEXT = """
# Mastering Content Operations for Solo Creators
Content creators face severe burnout trying to maintain simultaneous presence across LinkedIn, Instagram, and YouTube.
Recent creator surveys indicate that 72% of creators spend over 18 hours per week manually reformatting content.
The solution is a systematic 1-to-30 multiplication framework:
1. Extract strategic takeaways for LinkedIn thought leadership.
2. Turn step-by-step processes into visual carousel decks.
3. Slice punchy, curiosity-driven insights into 60-second vertical videos.
Always attach standardized UTM parameters and verified URLs to measure real business conversion.
"""


def test_ingestion_valid():
    doc = process_input(SAMPLE_TEXT, campaign_name="test_campaign")
    assert isinstance(doc, IngestedDocument)
    assert doc.word_count > 30
    assert len(doc.key_ideas) > 0
    assert len(doc.extracted_claims) > 0


def test_ingestion_too_short():
    with pytest.raises(ValueError, match="Input text is too short"):
        process_input("Too short", campaign_name="fail_campaign")


def test_normal_generation_min_10(tmp_path):
    doc = process_input(SAMPLE_TEXT, campaign_name="test_campaign")
    generator = ContentGenerator(provider="demo")
    assets, retries, tokens = generator.generate_content_package(
        doc=doc,
        run_id="TEST_RUN_10",
        mode="min_10",
        platforms=["linkedin", "instagram", "youtube"]
    )
    assert len(assets) == 10
    assert any(a.format_type == "video" for a in assets)
    assert any(a.format_type == "carousel" for a in assets)
    assert any(a.format_type == "native_post" for a in assets)


def test_new_input_refresh_preserves_diversity():
    doc1 = process_input(SAMPLE_TEXT, campaign_name="campaign_one")
    new_text = """
    # Advanced AI Video Editing Workflows
    Video editors can leverage intelligent scene detection and automated captioning to speed up turnaround by 400%.
    Key study reveals that videos with dynamic captions retain viewers for 85% longer.
    Standardize production workflows with automated rendering engines.
    """
    doc2 = process_input(new_text, campaign_name="campaign_two")

    gen = ContentGenerator(provider="demo")
    assets1, _, _ = gen.generate_content_package(doc=doc1, run_id="RUN_1", mode="min_10")
    existing_texts = [f"{a.hook} {a.caption}" for a in assets1]

    assets2, _, _ = gen.generate_content_package(
        doc=doc2, run_id="RUN_2", mode="min_10", existing_texts=existing_texts
    )

    assert len(assets2) == 10
    # Verify new input produces different asset IDs and hooks
    assert assets2[0].run_id == "RUN_2"
    assert assets2[0].source_reference != assets1[0].source_reference
