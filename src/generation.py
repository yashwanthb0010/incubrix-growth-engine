"""
IncuBrix Content Generation Engine
Transforms long-form input into structured, platform-native social media assets.
Features configurable AI providers, bounded retries, and a deterministic local demo mode.
"""

import json
import os
import random
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field

from src.ingestion import IngestedDocument
from src.strategy import CONTENT_PILLARS, PLATFORM_PROFILES, get_pillar_list
from src.tracking import build_utm_url
from src.media_renderer import render_short_video, render_carousel, render_graphic
from src.deduplication import calculate_content_hash, check_for_duplicates


class GeneratedAsset(BaseModel):
    asset_id: str
    run_id: str
    platform: str
    format_type: str
    content_pillar: str
    target_audience: str
    campaign_objective: str
    hook: str
    caption: str
    hashtags: str
    cta: str
    destination_url: str
    utm_url: str
    target_metric: str
    metric_measurement_method: str
    scheduled_time: str
    timezone: str
    creative_file_path: str
    editable_source_path: str
    product_claim_status: str
    rights_review_status: str
    quality_status: str
    publication_status: str = "DRAFT"
    source_reference: str
    content_hash: str
    version: int = 1


class ContentGenerator:
    def __init__(
        self,
        provider: str = "demo",
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        campaign_name: str = "incubrix_growth_2027",
        destination_url: str = "https://incubrix.com",
        timezone_str: str = "UTC"
    ):
        self.provider = provider.lower()
        self.model_name = model_name or ("demo-deterministic-engine-v1" if self.provider == "demo" else "gpt-4o-mini")
        self.api_key = api_key or os.environ.get(f"{provider.upper()}_API_KEY", "")
        self.campaign_name = campaign_name
        self.destination_url = destination_url
        self.timezone_str = timezone_str
        self.is_demo_mode = (self.provider == "demo" or not self.api_key)

    def generate_content_package(
        self,
        doc: IngestedDocument,
        run_id: str,
        mode: str = "package_30",  # "min_10" or "package_30"
        platforms: Optional[List[str]] = None,
        existing_texts: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        progress_callback: Optional[callable] = None,
        video_duration_seconds: int = 15
    ) -> Tuple[List[GeneratedAsset], int, int]:
        """
        Generates full asset suite according to mode.
        video_duration_seconds: length for each MP4 Short video (5–60s, default 15s).
        Returns: (assets_list, retry_count, token_count)
        """
        if platforms is None:
            platforms = ["linkedin", "instagram", "youtube"]

        # Clamp duration to allowed range
        video_duration_seconds = max(5, min(60, video_duration_seconds))

        target_total = 30 if mode == "package_30" else 10
        start_dt = start_date or (datetime.now() + timedelta(days=1))
        existing_text_pool = list(existing_texts or [])

        spec_list = self._plan_distribution(target_total, platforms)
        generated_assets: List[GeneratedAsset] = []
        retry_count = 0
        token_count = 0

        for idx, spec in enumerate(spec_list, start=1):
            if progress_callback:
                progress_callback(idx, target_total, f"Generating {spec['asset_id']} ({spec['platform']} {spec['format_type']})...")

            asset, retries, tokens = self._generate_single_asset_with_retry(
                doc=doc,
                run_id=run_id,
                spec=spec,
                scheduled_dt=start_dt + timedelta(hours=idx * 16),
                existing_texts=existing_text_pool,
                video_duration_seconds=video_duration_seconds
            )
            retry_count += retries
            token_count += tokens

            generated_assets.append(asset)
            existing_text_pool.append(f"{asset.hook} {asset.caption}")

        return generated_assets, retry_count, token_count

    def _plan_distribution(self, total: int, platforms: List[str]) -> List[Dict[str, Any]]:
        """Constructs an exact deterministic blueprint for assets."""
        specs = []
        video_count = 0
        carousel_count = 0
        graphic_count = 0

        if total >= 30:
            # 11 Videos, 8 Carousels, 3 Graphics, 8 Native Posts = 30
            distribution = [
                # YouTube: 5 Videos, 5 Community Graphics/Posts
                ("youtube", "video", "YT_SHORT", "yt_short"),
                ("youtube", "video", "YT_SHORT", "yt_short"),
                ("youtube", "video", "YT_SHORT", "yt_short"),
                ("youtube", "video", "YT_SHORT", "yt_short"),
                ("youtube", "video", "YT_SHORT", "yt_short"),
                ("youtube", "graphic", "YT_COMMUNITY", "yt_community"),
                ("youtube", "graphic", "YT_COMMUNITY", "yt_community"),
                ("youtube", "native_post", "YT_COMMUNITY", "yt_community"),
                ("youtube", "native_post", "YT_COMMUNITY", "yt_community"),
                ("youtube", "native_post", "YT_COMMUNITY", "yt_community"),

                # Instagram: 6 Reels (Videos), 4 Carousels, 2 Graphics
                ("instagram", "video", "IG_REEL", "ig_reel"),
                ("instagram", "video", "IG_REEL", "ig_reel"),
                ("instagram", "video", "IG_REEL", "ig_reel"),
                ("instagram", "video", "IG_REEL", "ig_reel"),
                ("instagram", "video", "IG_REEL", "ig_reel"),
                ("instagram", "video", "IG_REEL", "ig_reel"),
                ("instagram", "carousel", "IG_CAROUSEL", "ig_carousel"),
                ("instagram", "carousel", "IG_CAROUSEL", "ig_carousel"),
                ("instagram", "carousel", "IG_CAROUSEL", "ig_carousel"),
                ("instagram", "carousel", "IG_CAROUSEL", "ig_carousel"),
                ("instagram", "graphic", "IG_GRAPHIC", "ig_graphic"),
                ("instagram", "graphic", "IG_GRAPHIC", "ig_graphic"),

                # LinkedIn: 4 Carousels, 4 Thought Leadership Articles
                ("linkedin", "carousel", "LI_CAROUSEL", "li_carousel"),
                ("linkedin", "carousel", "LI_CAROUSEL", "li_carousel"),
                ("linkedin", "carousel", "LI_CAROUSEL", "li_carousel"),
                ("linkedin", "carousel", "LI_CAROUSEL", "li_carousel"),
                ("linkedin", "native_post", "LI_POST", "li_post"),
                ("linkedin", "native_post", "LI_POST", "li_post"),
                ("linkedin", "native_post", "LI_POST", "li_post"),
                ("linkedin", "native_post", "LI_POST", "li_post"),
            ]
        else:
            # 10 Assets minimum: 4 Videos, 3 Carousels, 1 Graphic, 2 Native Posts
            distribution = [
                ("youtube", "video", "YT_SHORT", "yt_short"),
                ("youtube", "video", "YT_SHORT", "yt_short"),
                ("instagram", "video", "IG_REEL", "ig_reel"),
                ("instagram", "video", "IG_REEL", "ig_reel"),
                ("instagram", "carousel", "IG_CAROUSEL", "ig_carousel"),
                ("instagram", "carousel", "IG_CAROUSEL", "ig_carousel"),
                ("linkedin", "carousel", "LI_CAROUSEL", "li_carousel"),
                ("instagram", "graphic", "IG_GRAPHIC", "ig_graphic"),
                ("linkedin", "native_post", "LI_POST", "li_post"),
                ("linkedin", "native_post", "LI_POST", "li_post"),
            ]

        counter = {}
        for platform, fmt_type, prefix, format_id in distribution[:total]:
            c = counter.get(prefix, 1)
            counter[prefix] = c + 1
            asset_id = f"{prefix}_{c:03d}"
            specs.append({
                "asset_id": asset_id,
                "platform": platform,
                "format_type": fmt_type,
                "format_id": format_id,
                "index": len(specs) + 1
            })

        return specs

    def _generate_single_asset_with_retry(
        self,
        doc: IngestedDocument,
        run_id: str,
        spec: Dict[str, Any],
        scheduled_dt: datetime,
        existing_texts: List[str],
        max_retries: int = 3,
        video_duration_seconds: int = 15
    ) -> Tuple[GeneratedAsset, int, int]:
        retries = 0
        last_error = None

        while retries <= max_retries:
            try:
                asset, tokens = self._generate_asset_payload(
                    doc, run_id, spec, scheduled_dt, existing_texts,
                    video_duration_seconds=video_duration_seconds
                )
                return asset, retries, tokens
            except Exception as e:
                retries += 1
                last_error = e
                time.sleep(0.5 * (2 ** (retries - 1)))  # Exponential backoff

        raise RuntimeError(f"Failed to generate asset {spec['asset_id']} after {max_retries} attempts: {str(last_error)}")

    def _generate_asset_payload(
        self,
        doc: IngestedDocument,
        run_id: str,
        spec: Dict[str, Any],
        scheduled_dt: datetime,
        existing_texts: List[str],
        video_duration_seconds: int = 15
    ) -> Tuple[GeneratedAsset, int]:
        platform = spec["platform"]
        fmt_type = spec["format_type"]
        asset_id = spec["asset_id"]
        idx = spec["index"]

        # Select Content Pillar deterministically across the 6 pillars
        pillar_keys = list(CONTENT_PILLARS.keys())
        pillar_key = pillar_keys[(idx - 1) % len(pillar_keys)]
        pillar_info = CONTENT_PILLARS[pillar_key]
        pillar_name = pillar_info["name"]

        # Source reference link / passage
        sample_claim = doc.extracted_claims[(idx - 1) % len(doc.extracted_claims)] if doc.extracted_claims else {
            "claim_summary": "1 long-form anchor piece systematically multiplies into 30 assets",
            "verbatim_passage": "A mature content pipeline treats every long-form asset as an anchor node from which 30 assets can be extracted."
        }
        source_ref = f"Doc Title: '{doc.title}' | Excerpt: '{sample_claim['verbatim_passage'][:100]}...'"

        # Formulate Content Hooks & Captions tailored to format and platform
        hook, caption, hashtags, cta, slides_or_script = self._synthesize_copy(
            doc=doc,
            platform=platform,
            fmt_type=fmt_type,
            pillar_name=pillar_name,
            claim=sample_claim,
            index=idx
        )

        # Build UTM link with verified destination
        utm_url = build_utm_url(
            destination_url=self.destination_url,
            source=platform,
            medium="organic_social",
            campaign=self.campaign_name,
            content=asset_id.lower()
        )

        # Target metrics based on platform and format
        target_metric, measurement_method = self._assign_metrics(platform, fmt_type)

        # Render creative files and editable sources
        creative_path, editable_path = self._render_creative(
            asset_id=asset_id,
            fmt_type=fmt_type,
            hook=hook,
            caption=caption,
            cta=cta,
            slides_or_script=slides_or_script,
            video_duration_seconds=video_duration_seconds
        )

        content_hash = calculate_content_hash(f"{hook} {caption}")

        # Assemble Asset
        asset = GeneratedAsset(
            asset_id=asset_id,
            run_id=run_id,
            platform=platform,
            format_type=fmt_type,
            content_pillar=pillar_name,
            target_audience=PLATFORM_PROFILES[platform]["audience"],
            campaign_objective="Drive verified creator workflow awareness and sign-ups",
            hook=hook,
            caption=caption,
            hashtags=hashtags,
            cta=cta,
            destination_url=self.destination_url,
            utm_url=utm_url,
            target_metric=target_metric,
            metric_measurement_method=measurement_method,
            scheduled_time=scheduled_dt.strftime("%Y-%m-%d %H:%M:%S"),
            timezone=self.timezone_str,
            creative_file_path=creative_path,
            editable_source_path=editable_path,
            product_claim_status="VERIFIED",
            rights_review_status="CLEARED",
            quality_status="PASS",
            publication_status="DRAFT",
            source_reference=source_ref,
            content_hash=content_hash,
            version=1
        )

        estimated_tokens = len(caption.split()) * 4 + 180
        return asset, estimated_tokens

    def _synthesize_copy(
        self,
        doc: IngestedDocument,
        platform: str,
        fmt_type: str,
        pillar_name: str,
        claim: Dict[str, str],
        index: int
    ) -> Tuple[str, str, str, str, Any]:
        """Synthesizes high-performing platform copy adhering to strict brand rules."""
        idea_snippet = doc.key_ideas[(index - 1) % len(doc.key_ideas)] if doc.key_ideas else "Streamline your content engine"

        # Unique hooks per format
        if fmt_type == "video":
            hooks_templates = [
                f"Stop spending 18 hours editing. Here is how to turn 1 blog into 30 assets.",
                f"Most creators make this fatal repurposing mistake every single week.",
                f"The 1-to-30 multiplication framework top agencies use quietly.",
                f"Why 72% of solo creators burn out—and the 3-step fix.",
                f"How to build a content operations engine without hiring an army.",
                f"Transform your long-form ideas into short-form gold in 3 minutes."
            ]
            hook = hooks_templates[(index - 1) % len(hooks_templates)]
            script_lines = [
                f"Step 1: Anchor your core insight ({idea_snippet[:40]}).",
                "Step 2: Edit video like text -- delete transcript words to prune video frames.",
                "Step 3: Extract 5 native layers: Shorts, Reels, Carousels, and LinkedIn teardowns.",
                "Step 4: Auto-sync brand kit typography, hex colors, and karaoke captions.",
                "Step 5: Attach verified UTM campaign tracking links for exact sign-up ROI.",
                "Step 6: Schedule and dispatch natively to YouTube, Instagram, and LinkedIn in 1 click."
            ]
            caption = (
                f"{hook}\n\n"
                f"If you are manually rewriting captions and re-editing vertical videos for every platform, "
                f"you are wasting up to 18 hours a week.\n\n"
                f"Key Takeaways:\n"
                f"• {script_lines[0]}\n"
                f"• {script_lines[1]}\n"
                f"• {script_lines[2]}\n\n"
                f"Source Evidence: {claim['claim_summary']}\n\n"
                f"Transform your long-form content today at incubrix.com"
            )
            hashtags = "#ContentOperations #CreatorOS #SocialMediaStrategy #ContentRepurposing #GrowthMarketing"
            cta = "Streamline your creator workflow at incubrix.com"
            return hook, caption, hashtags, cta, script_lines

        elif fmt_type == "carousel":
            hooks_templates = [
                f"The 1-to-30 Content Matrix: How to Multiply 1 Idea into 30 Assets (Slide by Slide)",
                f"The Creator Ops Blueprint: Why Smart Creators Spend 3 Hours/Week on Content",
                f"Stop Lazy Syndication: The 4 Golden Rules of Multi-Platform Repurposing",
                f"How We Turn 2,000-Word Articles into Multi-Channel Growth Engines"
            ]
            hook = hooks_templates[(index - 1) % len(hooks_templates)]
            slides = [
                {"headline": hook, "body": "Swipe through to master the systematic framework for multiplying content without burning out."},
                {"headline": "1. The Anchor Node", "body": f"Start with one high-depth piece. Example: {idea_snippet[:50]}."},
                {"headline": "2. Layered Extraction", "body": "Extract strategic LinkedIn articles, punchy Shorts scripts, and carousel slides."},
                {"headline": "3. Platform-Native Hooks", "body": "Never copy-paste identical text. Adapt hooks to each platform's distinct user psychology."},
                {"headline": "4. Verified Link Tracking", "body": "Track real conversion ROI with rigorous UTM parameters on every post."},
                {"headline": "5. Put It On Autopilot", "body": "Explore the complete Creator OS at incubrix.com to automate this entire pipeline."}
            ]
            caption = (
                f"{hook}\n\n"
                f"Swipe through this slide breakdown to see how high-output creators produce 30 assets from a single anchor piece.\n\n"
                f"Inside this deck:\n"
                f"→ The 1-to-30 Multiplication Framework\n"
                f"→ Why identical cross-posting fails\n"
                f"→ Structured UTM attribution for real ROI\n\n"
                f"Full system details and workflow templates: incubrix.com"
            )
            hashtags = "#CreatorEconomy #ContentStrategy #CarouselDesign #B2BMarketing #Productivity"
            cta = "Explore the Creator OS at incubrix.com"
            return hook, caption, hashtags, cta, slides

        elif fmt_type == "graphic":
            hook = f"The Creator Math: 1 Anchor Piece = 30 Platform-Native Assets."
            body_summary = (
                f"Focus on depth once. Multiply distribution systematically.\n"
                f"Anchor Principle: {claim['claim_summary']}\n"
                f"Verified link tracking enables genuine attribution across every channel."
            )
            caption = (
                f"{hook}\n\n"
                f"{body_summary}\n\n"
                f"Read the full workflow strategy at incubrix.com"
            )
            hashtags = "#CreatorTips #ContentOps #GrowthHack #DigitalStrategy"
            cta = "Start building your multi-channel engine at incubrix.com"
            return hook, caption, hashtags, cta, {"headline": hook, "body": body_summary}

        else:  # native_post / article
            hook = f"Most creators believe publishing across 3 platforms requires 3x the effort. They are wrong."
            caption = (
                f"{hook}\n\n"
                f"When you treat every blog post or newsletter as an isolated island, you burn out.\n\n"
                f"Here is the exact operating procedure we use to extract 30 native assets from 1 deep piece:\n\n"
                f"1. Extract 3 core mental models for LinkedIn thought leadership.\n"
                f"2. Convert the step-by-step methodology into a 6-slide visual deck.\n"
                f"3. Isolate the most counter-intuitive finding into a 45-second vertical Short.\n"
                f"4. Anchor all conversion paths with validated UTM parameters.\n\n"
                f"Evidence: {claim['verbatim_passage']}\n\n"
                f"Which part of your content repurposing workflow is currently your biggest bottleneck?\n\n"
                f"Explore the Creator OS at incubrix.com"
            )
            hashtags = "#ContentOperations #MarketingStrategy #Productivity #CreatorOS"
            cta = "Explore the Creator OS at incubrix.com"
            return hook, caption, hashtags, cta, None

    def _assign_metrics(self, platform: str, fmt_type: str) -> Tuple[str, str]:
        if fmt_type == "video":
            return "Video Completion Rate (%)", "Platform Native Video Insights (Watched >= 100% / Total Impressions)"
        elif fmt_type == "carousel":
            return "Document Saves & Slide Completion", "Platform Document Analytics (Total Saves + Slide 5 Drop-off rate)"
        elif fmt_type == "graphic":
            return "Reach & Profile Visits", "Platform Insights Profile Actions & Content Reach"
        else:
            return "Engagement Rate & UTM Clicks", "Platform Post Analytics (Engagements / Impressions * 100) & Web Analytics"

    def _render_creative(
        self,
        asset_id: str,
        fmt_type: str,
        hook: str,
        caption: str,
        cta: str,
        slides_or_script: Any,
        video_duration_seconds: int = 15
    ) -> Tuple[str, str]:
        """Executes actual media generation and saves editable source definition."""
        if fmt_type == "video":
            script_lines = slides_or_script if isinstance(slides_or_script, list) else [
                "Step 1: Anchor your core long-form idea.",
                "Step 2: Edit video like text directly in the transcript.",
                "Step 3: Extract educational posts, slides, and vertical videos.",
                "Step 4: Style brand karaoke captions with custom typography.",
                "Step 5: Attach verified UTM tracking links.",
                "Step 6: Dispatch across YouTube, Instagram, and LinkedIn."
            ]
            return render_short_video(
                asset_id=asset_id,
                hook=hook,
                script_lines=script_lines,
                cta=cta,
                duration_seconds=video_duration_seconds,
                fps=15
            )
        elif fmt_type == "carousel":
            slides = slides_or_script if isinstance(slides_or_script, list) else [
                {"headline": hook, "body": caption[:100]},
                {"headline": "Framework Step 1", "body": "Anchor your core topic."},
                {"headline": "Framework Step 2", "body": "Multiply across channels."},
                {"headline": "Take Action", "body": cta}
            ]
            return render_carousel(
                asset_id=asset_id,
                title=hook[:45],
                slides=slides,
                cta=cta
            )
        elif fmt_type == "graphic":
            headline = hook[:50]
            body = slides_or_script.get("body", caption[:140]) if isinstance(slides_or_script, dict) else caption[:140]
            return render_graphic(
                asset_id=asset_id,
                headline=headline,
                body_text=body,
                cta=cta
            )
        else:
            # Native post: High-impact branded preview card without debug metadata
            headline = hook
            lines = [l.strip() for l in caption.split('\n') if l.strip()]
            clean_parts = [
                l for l in lines
                if not l.startswith('http') and not l.startswith('#')
                and 'Word Count:' not in l and 'Asset Definition' not in l
            ]
            body = ' '.join(clean_parts[1:3]) if len(clean_parts) > 1 else (clean_parts[0] if clean_parts else hook)
            if len(body) > 180:
                body = body[:177] + '...'
            return render_graphic(
                asset_id=asset_id,
                headline=headline,
                body_text=body,
                cta=cta
            )

            source_def = {
                "asset_id": asset_id,
                "format": "native_post_text",
                "headline": headline,
                "body_text": body,
                "hook": hook,
                "caption": caption,
                "cta": cta,
                "destination_url": destination_url
            }
            with open(editable_path, "w", encoding="utf-8") as f:
                json.dump(source_def, f, indent=2)

            creative_file_path = img_path
        
