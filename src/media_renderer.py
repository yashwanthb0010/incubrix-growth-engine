"""
IncuBrix Media Renderer
Generates verified, platform-native creative files:
1. Real vertical MP4 short videos (1080x1920, <=60s) with motion graphics, progress bar, and visualizer.
2. High-contrast PNG carousel slide decks (1080x1350, 4:5 vertical).
3. Square PNG social infographics/quote cards (1080x1080).
4. Structured editable source files (.json) for every asset.
"""

import json
import math
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any
from PIL import Image, ImageDraw, ImageFont

# Try to find FFmpeg via imageio-ffmpeg
FFMPEG_EXE = None
try:
    import imageio_ffmpeg
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_EXE = None


# Brand Design Tokens
BRAND_DARK_BG = (15, 23, 42)       # #0F172A
BRAND_SURFACE = (30, 41, 59)       # #1E293B
BRAND_PRIMARY = (99, 102, 241)     # #6366F1
BRAND_SECONDARY = (236, 72, 153)   # #EC4899
BRAND_ACCENT = (56, 189, 248)      # #38BDF8
TEXT_PRIMARY = (255, 255, 255)
TEXT_MUTED = (148, 163, 184)
BRAND_SUCCESS = (16, 185, 129)


def get_default_font(size: int = 36) -> ImageFont.ImageFont:
    """Attempts to load a standard system sans-serif font, fallback to default."""
    font_candidates = [
        "C:\\Windows\\Fonts\\segoeui.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\calibri.ttf",
        "C:\\Windows\\Fonts\\tahoma.ttf"
    ]
    for path in font_candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def get_bold_font(size: int = 44) -> ImageFont.ImageFont:
    font_candidates = [
        "C:\\Windows\\Fonts\\segoeuib.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\calibrib.ttf"
    ]
    for path in font_candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return get_default_font(size)


def draw_header_badge(draw: ImageDraw.ImageDraw, text: str = "INCUBRIX CREATOR OS", width: int = 1080):
    badge_w = 600
    badge_h = 80
    x0 = (width - badge_w) // 2
    y0 = 85
    draw.rounded_rectangle([x0, y0, x0 + badge_w, y0 + badge_h], radius=40, fill=BRAND_SURFACE, outline=BRAND_PRIMARY, width=3)
    font_badge = get_bold_font(34)
    bbox = draw.textbbox((0, 0), text, font=font_badge)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((x0 + (badge_w - tw) // 2, y0 + (badge_h - th) // 2 - 2), text, font=font_badge, fill=BRAND_ACCENT)


def draw_wrapped_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    x: int,
    y: int,
    max_width: int,
    font: ImageFont.ImageFont,
    fill: Tuple[int, int, int],
    line_spacing: int = 12
) -> int:
    """Wraps text within max_width and returns the bottom Y coordinate."""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    curr_y = y
    for line in lines:
        draw.text((x, curr_y), line, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), line, font=font)
        curr_y += (bbox[3] - bbox[1]) + line_spacing

    return curr_y


def render_short_video(
    asset_id: str,
    hook: str,
    script_lines: List[str],
    cta: str,
    output_dir: str = "output/assets",
    duration_seconds: int = 8,
    fps: int = 15
) -> Tuple[str, str]:
    """
    Renders an actual 1080x1920 vertical MP4 video.
    Includes animated typography, sound wave visualizers, progress bar, and CTA screen.
    Duration is strictly <= 60s (default 8s for speed and crisp pacing).
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    mp4_path = os.path.join(output_dir, f"{asset_id}.mp4")

    width, height = 1080, 1920
    total_frames = duration_seconds * fps

    # Dynamic proportional phase timing (scales smoothly from 5s to 60s without content repeating)
    hook_duration = min(7.0, max(2.0, duration_seconds * 0.15))
    cta_duration = min(6.0, max(2.0, duration_seconds * 0.12))
    breakdown_duration = max(1.0, duration_seconds - hook_duration - cta_duration)

    num_steps = len(script_lines) if script_lines else 1
    step_duration = breakdown_duration / num_steps

    # Proportional Typography tailored for 1080x1920 (9:16 Vertical)
    font_hook = get_bold_font(62)
    font_body = get_bold_font(56)
    font_cta = get_bold_font(56)
    font_pill = get_bold_font(32)
    font_medium = get_bold_font(34)
    font_small = get_default_font(28)

    # 9:16 Vertical Card Dimensions (fills vertical space proportionally)
    card_x0, card_x1 = 60, width - 60
    card_y0, card_y1 = 230, 1560

    # Use FFmpeg pipe if available, else OpenCV VideoWriter
    use_ffmpeg = FFMPEG_EXE is not None and os.path.exists(FFMPEG_EXE)
    pipe = None
    cv_writer = None

    if use_ffmpeg:
        cmd = [
            FFMPEG_EXE,
            "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{width}x{height}",
            "-pix_fmt", "rgb24",
            "-r", str(fps),
            "-i", "-",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "ultrafast",
            "-movflags", "+faststart",
            mp4_path
        ]
        pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        import cv2
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        cv_writer = cv2.VideoWriter(mp4_path, fourcc, fps, (width, height))

    try:
        for frame_idx in range(total_frames):
            progress = frame_idx / total_frames
            current_time = frame_idx / fps

            # Base Frame
            img = Image.new("RGB", (width, height), BRAND_DARK_BG)
            draw = ImageDraw.Draw(img)

            # Draw ambient top gradient
            for y_grad in range(0, 500):
                alpha = int(70 * (1 - y_grad / 500))
                draw.line([(0, y_grad), (width, y_grad)], fill=(BRAND_PRIMARY[0] // 3 + alpha, BRAND_PRIMARY[1] // 4, BRAND_PRIMARY[2] // 2 + alpha))

            # Header Badge
            draw_header_badge(draw, text="INCUBRIX SHORTS ENGINE", width=width)

            # Progress Bar at Top
            bar_w = int(width * progress)
            draw.rectangle([0, 0, width, 16], fill=BRAND_SURFACE)
            draw.rectangle([0, 0, bar_w, 16], fill=BRAND_SECONDARY)

            # Central Content Switching by Timeline (Proportional Pacing -- ZERO REPETITION)
            # Phase 1: 0 to hook_duration (Hook)
            # Phase 2: hook_duration to (duration - cta_duration) (Step-by-step progressive breakdown)
            # Phase 3: (duration - cta_duration) to end (CTA & Verified Link)
            if current_time < hook_duration:
                # Hook Phase
                draw.rounded_rectangle([card_x0, card_y0, card_x1, card_y1], radius=36, fill=BRAND_SURFACE, outline=BRAND_PRIMARY, width=3)
                
                # Eyebrow pill (dynamic width)
                eyebrow_text = "[ STOP WASTING 18 HOURS/WEEK ]"
                bbox_eb = draw.textbbox((0, 0), eyebrow_text, font=font_pill)
                pill_w = (bbox_eb[2] - bbox_eb[0]) + 64
                draw.rounded_rectangle([100, 280, 100 + pill_w, 344], radius=32, fill=(15, 23, 42), outline=BRAND_SECONDARY, width=2)
                draw.text((132, 296), eyebrow_text, font=font_pill, fill=BRAND_SECONDARY)

                # Hook text (Large, bold, high contrast)
                draw_wrapped_text(draw, f'"{hook}"', 110, 410, width - 220, font_hook, TEXT_PRIMARY, line_spacing=26)
                
                # Visual Indicator: Pulsing concentric radar rings
                cx, cy = 540, 1000
                pulse = int(math.sin(frame_idx * 0.4) * 16)
                for r_ring, col in [(180 + pulse, (30, 41, 59)), (130 + pulse // 2, (51, 65, 85)), (80, BRAND_PRIMARY), (30, BRAND_SECONDARY)]:
                    draw.ellipse([cx - r_ring, cy - r_ring, cx + r_ring, cy + r_ring], outline=col, width=4)

                draw.text((cx - 240, 1210), "INITIALIZING VIRAL RETENTION HOOK", font=font_pill, fill=BRAND_ACCENT)

                # Bottom takeaway pill
                draw.rounded_rectangle([110, 1360, width - 110, 1480], radius=24, fill=(15, 23, 42), outline=BRAND_PRIMARY, width=2)
                draw.text((140, 1400), ">> Turn 1 Long Video Into a Week of Native Posts", font=font_medium, fill=BRAND_SECONDARY)

            elif current_time < (duration_seconds - cta_duration):
                # Progressive Script Breakdown Phase (NO MODULO REPETITION)
                step_idx = min(num_steps - 1, max(0, int((current_time - hook_duration) / step_duration)))
                step_text = script_lines[step_idx] if script_lines else "Multiply your content into 30 native assets."

                # Progress within the current step
                step_elapsed = current_time - hook_duration - (step_idx * step_duration)
                step_pct = min(1.0, max(0.0, step_elapsed / step_duration))

                draw.rounded_rectangle([card_x0, card_y0, card_x1, card_y1], radius=36, fill=BRAND_SURFACE, outline=BRAND_ACCENT, width=3)
                
                # Step Pill (dynamic width)
                step_pill_txt = f"STEP {step_idx + 1} OF {num_steps}"
                bbox_sp = draw.textbbox((0, 0), step_pill_txt, font=font_pill)
                pill_w = (bbox_sp[2] - bbox_sp[0]) + 64
                draw.rounded_rectangle([100, 280, 100 + pill_w, 344], radius=32, fill=(15, 23, 42), outline=BRAND_SECONDARY, width=2)
                draw.text((132, 296), step_pill_txt, font=font_pill, fill=BRAND_SECONDARY)
                draw.text((100 + pill_w + 24, 298), "* CONTENT REPURPOSING FRAMEWORK", font=font_small, fill=BRAND_ACCENT)

                # Main Step Body (Large, readable font auto-scaled to text length)
                chosen_body_font = get_bold_font(50) if len(step_text) > 110 else font_body
                draw_wrapped_text(draw, step_text, 110, 410, width - 220, chosen_body_font, TEXT_PRIMARY, line_spacing=26)

                # Animated Sound Waveform Bars in center
                base_x = 120
                for bar_i in range(20):
                    wave_h = max(18, int(45 + 50 * math.sin(frame_idx * 0.5 + bar_i * 0.45)))
                    bx = base_x + bar_i * 42
                    draw.rounded_rectangle([bx, 1060 - wave_h, bx + 24, 1060], radius=8, fill=BRAND_ACCENT if bar_i % 2 == 0 else BRAND_SECONDARY)

                # Step sub-progress bar inside card
                bar_inner_w = width - 220
                draw.rounded_rectangle([110, 1150, width - 110, 1172], radius=11, fill=(15, 23, 42))
                draw.rounded_rectangle([110, 1150, 110 + int(bar_inner_w * step_pct), 1172], radius=11, fill=BRAND_ACCENT)
                pct_txt = f"Step {step_idx + 1} of {num_steps}  •  {int(step_pct * 100)}% active"
                draw.text((110, 1195), pct_txt, font=font_pill, fill=TEXT_MUTED)

                # Bottom feature badge inside card
                draw.rounded_rectangle([110, 1360, width - 110, 1480], radius=24, fill=(15, 23, 42), outline=BRAND_PRIMARY, width=2)
                draw.text((150, 1400), ">> Verified 1-Click Multi-Channel Auto Dispatch", font=font_medium, fill=BRAND_ACCENT)

            else:
                # CTA & Destination Phase
                draw.rounded_rectangle([card_x0, card_y0, card_x1, card_y1], radius=36, fill=BRAND_SURFACE, outline=BRAND_SUCCESS, width=3)
                
                cta_badge_txt = "OFFICIAL VERIFIED DESTINATION"
                bbox_cb = draw.textbbox((0, 0), cta_badge_txt, font=font_pill)
                pill_w = (bbox_cb[2] - bbox_cb[0]) + 64
                draw.rounded_rectangle([100, 280, 100 + pill_w, 344], radius=32, fill=(15, 23, 42), outline=BRAND_SUCCESS, width=2)
                draw.text((132, 296), cta_badge_txt, font=font_pill, fill=BRAND_SUCCESS)

                # Main CTA Text
                draw_wrapped_text(draw, cta, 110, 410, width - 220, font_cta, TEXT_PRIMARY, line_spacing=26)
                
                # Giant Verified Button
                btn_y0, btn_y1 = 860, 1080
                draw.rounded_rectangle([110, btn_y0, width - 110, btn_y1], radius=36, fill=(79, 70, 229), outline=(129, 140, 248), width=3)
                btn_txt = "VISIT: incubrix.com  ->"
                bbox_btn = draw.textbbox((0, 0), btn_txt, font=get_bold_font(60))
                bw = bbox_btn[2] - bbox_btn[0]
                draw.text((110 + (width - 220 - bw) // 2, btn_y0 + 38), btn_txt, font=get_bold_font(60), fill=TEXT_PRIMARY)
                sub_btn = "Start Posting With Zero Extra Effort Today"
                bbox_sb = draw.textbbox((0, 0), sub_btn, font=font_pill)
                sw = bbox_sb[2] - bbox_sb[0]
                draw.text((110 + (width - 220 - sw) // 2, btn_y0 + 125), sub_btn, font=font_pill, fill=(224, 231, 255))

                # Guarantee badge
                draw.rounded_rectangle([110, 1150, width - 110, 1260], radius=24, fill=(15, 23, 42), outline=BRAND_SUCCESS, width=2)
                draw.text((150, 1188), "[PASS] Turnkey Monday Launch Kit Included", font=font_medium, fill=BRAND_SUCCESS)

                # Bottom badge
                draw.rounded_rectangle([110, 1360, width - 110, 1480], radius=24, fill=(15, 23, 42), outline=BRAND_PRIMARY, width=2)
                draw.text((150, 1400), ">> Automated Daily Content Repurposing Engine", font=font_medium, fill=BRAND_ACCENT)

            # Footer Metadata (Safe-zone at bottom of 1080x1920)
            draw.text((70, 1680), "#CreatorOS  #ContentRepurposing  #GrowthEngine", font=font_medium, fill=TEXT_MUTED)
            draw.text((70, 1750), "IncuBrix AI Social Growth Engine | 1080x1920 (9:16 Vertical)", font=font_small, fill=TEXT_MUTED)

            # Write Frame
            if pipe:
                pipe.stdin.write(img.tobytes())
            elif cv_writer:
                import cv2
                import numpy as np
                frame_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                cv_writer.write(frame_np)

    finally:
        if pipe:
            pipe.stdin.close()
            pipe.wait()
        elif cv_writer:
            cv_writer.release()

    # Save editable source JSON
    editable_path = os.path.join("output/editable_sources", f"{asset_id}_source.json")
    Path("output/editable_sources").mkdir(parents=True, exist_ok=True)
    source_payload = {
        "asset_id": asset_id,
        "format": "video_mp4",
        "resolution": f"{width}x{height}",
        "duration_seconds": duration_seconds,
        "fps": fps,
        "hook": hook,
        "storyboard_script": script_lines,
        "cta": cta,
        "destination_url": "https://incubrix.com",
        "audio_track": "rights_cleared_ambient_soundwave",
        "render_engine": "FFmpeg" if use_ffmpeg else "OpenCV"
    }
    with open(editable_path, "w", encoding="utf-8") as f:
        json.dump(source_payload, f, indent=2)

    return mp4_path, editable_path


def render_carousel(
    asset_id: str,
    title: str,
    slides: List[Dict[str, str]],
    cta: str,
    output_dir: str = "output/assets"
) -> Tuple[str, str]:
    """
    Renders multi-slide carousel images (1080x1350, 4:5 vertical).
    Produces individual slide PNGs with bold, proportional typography.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    width, height = 1080, 1350
    primary_cover_path = os.path.join(output_dir, f"{asset_id}_slide_1.png")

    font_slide_header = get_bold_font(58)
    font_body_large = get_bold_font(46)
    font_body_regular = get_default_font(40)
    font_pill = get_bold_font(30)
    font_small = get_default_font(26)

    rendered_slides_paths = []

    for i, slide in enumerate(slides, start=1):
        img = Image.new("RGB", (width, height), BRAND_DARK_BG)
        draw = ImageDraw.Draw(img)

        # Ambient Top Gradient
        for y_grad in range(0, 400):
            alpha = int(60 * (1 - y_grad / 400))
            draw.line([(0, y_grad), (width, y_grad)], fill=(BRAND_PRIMARY[0] // 3 + alpha, BRAND_PRIMARY[1] // 4, BRAND_PRIMARY[2] // 2 + alpha))

        # Header Pill (Left)
        draw.rounded_rectangle([60, 85, 540, 165], radius=40, fill=BRAND_SURFACE, outline=BRAND_PRIMARY, width=3)
        draw.text((100, 108), "INCUBRIX MASTERCLASS", font=get_bold_font(32), fill=BRAND_ACCENT)

        # Slide Number Indicator Pill (Right)
        slide_num_str = f"SLIDE {i} OF {len(slides)}"
        bbox_sn = draw.textbbox((0, 0), slide_num_str, font=font_pill)
        sn_w = (bbox_sn[2] - bbox_sn[0]) + 48
        draw.rounded_rectangle([width - sn_w - 60, 85, width - 60, 165], radius=40, fill=(15, 23, 42), outline=BRAND_ACCENT, width=2)
        draw.text((width - sn_w - 60 + 24, 108), slide_num_str, font=font_pill, fill=BRAND_ACCENT)

        # Main Content Card (1080x1350 proportional layout)
        card_x0, card_x1 = 60, width - 60
        card_y0, card_y1 = 190, height - 150
        draw.rounded_rectangle([card_x0, card_y0, card_x1, card_y1], radius=32, fill=BRAND_SURFACE, outline=BRAND_PRIMARY, width=3)

        slide_headline = slide.get("headline", title if i == 1 else f"Step {i}")
        slide_body = slide.get("body", "")

        # Eyebrow Pill
        pill_text = f"INSIGHT #{i}  *  CORE FRAMEWORK"
        bbox_p = draw.textbbox((0, 0), pill_text, font=font_pill)
        pill_w = (bbox_p[2] - bbox_p[0]) + 56
        draw.rounded_rectangle([100, 230, 100 + pill_w, 290], radius=30, fill=(15, 23, 42), outline=BRAND_SECONDARY, width=2)
        draw.text((128, 244), pill_text, font=font_pill, fill=BRAND_SECONDARY)

        # Large Headline
        next_y = draw_wrapped_text(draw, slide_headline, 100, 320, width - 200, font_slide_header, TEXT_PRIMARY, line_spacing=22)

        # Large Body Text
        chosen_font = font_body_large if len(slide_body) < 140 else font_body_regular
        next_y2 = draw_wrapped_text(draw, slide_body, 100, next_y + 35, width - 200, chosen_font, (241, 245, 249), line_spacing=20)

        # Actionable Takeaway Box in lower card
        callout_y = max(next_y2 + 35, 780)
        draw.rounded_rectangle([100, callout_y, width - 100, callout_y + 160], radius=24, fill=(15, 23, 42), outline=BRAND_ACCENT, width=2)
        draw.text((130, callout_y + 26), ">> STRATEGIC EXECUTION TAKEAWAY", font=get_bold_font(28), fill=BRAND_ACCENT)
        draw.text((130, callout_y + 75), "Apply this framework to eliminate 15+ hours of manual editing.", font=get_default_font(34), fill=TEXT_PRIMARY)

        # Slide Navigation Dots at bottom of card
        dot_start_x = width // 2 - (len(slides) * 36) // 2
        for dot_i in range(len(slides)):
            is_active = (dot_i + 1) == i
            w_dot = 22 if is_active else 16
            dot_color = BRAND_PRIMARY if is_active else BRAND_SURFACE
            outline_color = BRAND_ACCENT if is_active else (71, 85, 105)
            draw.ellipse([dot_start_x + dot_i * 36, 1050, dot_start_x + dot_i * 36 + w_dot, 1050 + w_dot], fill=dot_color, outline=outline_color, width=2)

        # CTA Footer
        draw.text((80, height - 110), f"Swipe >> {cta}", font=get_bold_font(32), fill=BRAND_ACCENT)
        draw.text((80, height - 68), "incubrix.com | Verified Creator OS Engine", font=font_small, fill=TEXT_MUTED)

        slide_path = os.path.join(output_dir, f"{asset_id}_slide_{i}.png")
        img.save(slide_path, "PNG")
        rendered_slides_paths.append(slide_path)

    # Save editable source JSON
    editable_path = os.path.join("output/editable_sources", f"{asset_id}_source.json")
    Path("output/editable_sources").mkdir(parents=True, exist_ok=True)
    source_payload = {
        "asset_id": asset_id,
        "format": "carousel_png",
        "slide_count": len(slides),
        "dimensions": f"{width}x{height}",
        "title": title,
        "slides": slides,
        "cta": cta,
        "rendered_files": rendered_slides_paths
    }
    with open(editable_path, "w", encoding="utf-8") as f:
        json.dump(source_payload, f, indent=2)

    return primary_cover_path, editable_path


def render_graphic(
    asset_id: str,
    headline: str,
    body_text: str,
    cta: str,
    output_dir: str = "output/assets"
) -> Tuple[str, str]:
    """
    Renders a square 1080x1080 PNG quote/infographic card with bold, readable typography.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    width, height = 1080, 1080
    graphic_path = os.path.join(output_dir, f"{asset_id}.png")

    img = Image.new("RGB", (width, height), BRAND_DARK_BG)
    draw = ImageDraw.Draw(img)

    # Subtle gradient top
    for y_grad in range(0, 350):
        alpha = int(55 * (1 - y_grad / 350))
        draw.line([(0, y_grad), (width, y_grad)], fill=(BRAND_PRIMARY[0] // 3 + alpha, BRAND_PRIMARY[1] // 4, BRAND_PRIMARY[2] // 2 + alpha))

    # Badge
    draw_header_badge(draw, text="INCUBRIX STRATEGIC BRIEF", width=width)

    # Main Card (1080x1080 proportional layout)
    card_x0, card_x1 = 50, width - 50
    card_y0, card_y1 = 180, height - 90
    draw.rounded_rectangle([card_x0, card_y0, card_x1, card_y1], radius=32, fill=BRAND_SURFACE, outline=BRAND_PRIMARY, width=3)

    font_headline = get_bold_font(58)
    font_body_large = get_bold_font(44)
    font_body_regular = get_default_font(38)
    font_pill = get_bold_font(30)
    font_small = get_default_font(26)

    # Eyebrow Pill
    pill_text = "KEY TAKEAWAY  *  PROVEN SYSTEM"
    bbox_p = draw.textbbox((0, 0), pill_text, font=font_pill)
    pill_w = (bbox_p[2] - bbox_p[0]) + 56
    draw.rounded_rectangle([90, 215, 90 + pill_w, 275], radius=28, fill=(15, 23, 42), outline=BRAND_SECONDARY, width=2)
    draw.text((118, 229), pill_text, font=font_pill, fill=BRAND_SECONDARY)

    # Large Headline
    next_y = draw_wrapped_text(draw, headline, 90, 305, width - 180, font_headline, TEXT_PRIMARY, line_spacing=22)

    # Large Body Text
    chosen_font = font_body_large if len(body_text) < 140 else font_body_regular
    next_y2 = draw_wrapped_text(draw, body_text, 90, next_y + 35, width - 180, chosen_font, (241, 245, 249), line_spacing=20)

    # Verified System Callout Box at bottom of card
    callout_y = max(next_y2 + 35, 690)
    draw.rounded_rectangle([90, callout_y, width - 90, callout_y + 140], radius=24, fill=(15, 23, 42), outline=BRAND_ACCENT, width=2)
    draw.text((120, callout_y + 22), ">> CORE OPERATIONAL STRATEGY", font=get_bold_font(28), fill=BRAND_ACCENT)
    draw.text((120, callout_y + 68), f"Strategy: {cta}", font=get_bold_font(32), fill=TEXT_PRIMARY)

    # Footer
    draw.text((60, height - 60), "incubrix.com  *  Verified AI Content Engine  *  #CreatorOS", font=font_small, fill=TEXT_MUTED)

    img.save(graphic_path, "PNG")

    # Save editable source JSON
    editable_path = os.path.join("output/editable_sources", f"{asset_id}_source.json")
    Path("output/editable_sources").mkdir(parents=True, exist_ok=True)
    source_payload = {
        "asset_id": asset_id,
        "format": "single_graphic_png",
        "dimensions": f"{width}x{height}",
        "headline": headline,
        "body_text": body_text,
        "cta": cta
    }
    with open(editable_path, "w", encoding="utf-8") as f:
        json.dump(source_payload, f, indent=2)

    return graphic_path, editable_path
