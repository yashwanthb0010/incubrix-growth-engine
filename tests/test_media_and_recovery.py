"""
Test Suite for Media Rendering and Failure Recovery
Covers: Video specs (<=60s, aspect ratio), carousel generation, AI provider failure recovery, and partial failure resilience.
"""

import os
import pytest
from unittest.mock import patch
from src.media_renderer import render_short_video, render_carousel, render_graphic
from src.ingestion import process_input
from src.generation import ContentGenerator


def test_video_rendering_specs(tmp_path):
    out_dir = str(tmp_path / "assets")
    edit_dir = str(tmp_path / "sources")

    video_path, source_path = render_short_video(
        asset_id="UNIT_TEST_REEL",
        hook="High Impact Video Hook",
        script_lines=["Step 1", "Step 2"],
        cta="incubrix.com",
        output_dir=out_dir,
        duration_seconds=3,
        fps=10
    )

    assert os.path.exists(video_path)
    assert os.path.exists(source_path)
    assert os.path.getsize(video_path) > 1000

    import cv2
    cap = cv2.VideoCapture(video_path)
    assert cap.isOpened()
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.release()

    duration = frames / fps if fps > 0 else 0
    assert width == 1080
    assert height == 1920
    assert duration <= 60.0
    assert height > width  # Strict vertical aspect ratio check!


def test_carousel_rendering(tmp_path):
    out_dir = str(tmp_path / "assets")
    slides = [
        {"headline": "Slide 1", "body": "Overview of system"},
        {"headline": "Slide 2", "body": "Tactical execution"}
    ]
    cover_path, edit_path = render_carousel(
        asset_id="UNIT_TEST_CAROUSEL",
        title="Test Carousel Deck",
        slides=slides,
        cta="incubrix.com",
        output_dir=out_dir
    )

    assert os.path.exists(cover_path)
    assert os.path.exists(edit_path)
    assert cover_path.endswith(".png")


def test_failure_recovery_on_provider_transient_error():
    doc = process_input(
        "Standard test content about digital creator growth and operational leverage in 2027. We extract structured social assets from one single core input article systematically.",
        campaign_name="recovery_test"
    )
    gen = ContentGenerator(provider="demo")

    call_count = 0
    original_synth = gen._synthesize_copy

    def mock_synth_with_flaky_first_call(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ConnectionError("Simulated transient AI Provider Timeout")
        return original_synth(*args, **kwargs)

    with patch.object(gen, "_synthesize_copy", side_effect=mock_synth_with_flaky_first_call):
        assets, retries, _ = gen.generate_content_package(
            doc=doc,
            run_id="RECOVERY_RUN",
            mode="min_10"
        )
        assert len(assets) == 10
        assert retries >= 1  # Verified retry mechanism triggered and recovered!
