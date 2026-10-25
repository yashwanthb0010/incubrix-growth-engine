"""
IncuBrix Media Renderer - Real-Time Social Motion Engine
Generates verified, platform-native creative files:
1. Real vertical MP4 short videos (1080x1920, 9:16) with authentic social UI overlay,
   kinetic extra-bold typography (64-74px), animated audio visualizer, and live engagement metrics.
2. High-contrast square PNG executive graphics/quote cards (1080x1080) with large bold typography
   and structured 3-step value blocks.
3. Multi-slide vertical PNG carousel decks (1080x1350, 4:5 vertical).
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
BRAND_DARK_BG = (10, 15, 30)       # Deep space dark #0A0F1E
BRAND_SURFACE = (19, 27, 46)       # Surface card #131B2E
BRAND_PRIMARY = (99, 102, 241)     # Electric Indigo #6366F1
BRAND_SECONDARY = (236, 72, 153)   # Neon Pink #EC4899
BRAND_ACCENT = (56, 189, 248)      # Vivid Sky Blue #38BDF8
BRAND_YELLOW = (250, 204, 21)      # High-Visibility Yellow #FACC15
BRAND_SUCCESS = (16, 185, 129)     # Emerald Green #10B981
TEXT_PRIMARY = (255, 255, 255)
TEXT_MUTED = (148, 163, 184)


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
        "C:\\Windows\\Fonts\\calibrib.ttf",
        "C:\\Windows\\Fonts\\trebucbd.ttf"
    ]
    for path in font_candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return get_default_font(size)


def draw_wrapped_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    x: int,
    y: int,
    max_width: int,
    font: ImageFont.ImageFont,
    fill: Tuple[int, int, int],
    line_spacing: int = 14,
    draw_shadow: bool = False
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
        if draw_shadow:
            draw.text((x + 4, curr_y + 4), line, font=font, fill=(0, 0, 0))
        draw.text((x, curr_y), line, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), line, font=font)
        curr_y += (bbox[3] - bbox[1]) + line_spacing

    return curr_y


# Clean vector helpers to avoid missing Unicode glyph boxes on Windows
def draw_vector_heart(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int = 24, fill=(236, 72, 153)):
    r = size // 3
    draw.ellipse([cx - size // 2, cy - size // 2, cx, cy - size // 2 + size // 2], fill=fill)
    draw.ellipse([cx, cy - size // 2, cx + size // 2, cy - size // 2 + size // 2], fill=fill)
    draw.polygon([(cx - size // 2, cy - size // 6), (cx + size // 2, cy - size // 6), (cx, cy + size // 2)], fill=fill)


def draw_vector_chat(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int = 24, fill=(255, 255, 255)):
    draw.rounded_rectangle([cx - size // 2, cy - size // 2, cx + size // 2, cy + size // 4], radius=6, fill=fill)
    draw.polygon([(cx - size // 4, cy + size // 4), (cx, cy + size // 4), (cx - size // 3, cy + size // 2)], fill=fill)


def draw_vector_share(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int = 24, fill=(56, 189, 248)):
    draw.line([(cx - size // 3, cy + size // 3), (cx + size // 4, cy - size // 4)], fill=fill, width=4)
    draw.polygon([(cx + size // 4, cy - size // 4), (cx, cy - size // 4), (cx + size // 4, cy)], fill=fill)


def draw_vector_bookmark(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int = 24, fill=(250, 204, 21)):
    w, h = size // 2, size * 2 // 3
    draw.polygon([(cx - w, cy - h // 2), (cx + w, cy - h // 2), (cx + w, cy + h // 2), (cx, cy + h // 4), (cx - w, cy + h // 2)], fill=fill)


def draw_vector_check(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int = 16, fill=(255, 255, 255), width=3):
    draw.line([(cx - size // 2, cy), (cx - size // 6, cy + size // 3), (cx + size // 2, cy - size // 2)], fill=fill, width=width)


def draw_vector_lightning(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int = 20, fill=(250, 204, 21)):
    pts = [
        (cx + size // 4, cy - size // 2),
        (cx - size // 3, cy),
        (cx, cy),
        (cx - size // 4, cy + size // 2),
        (cx + size // 3, cy - size // 6),
        (cx, cy - size // 6)
    ]
    draw.polygon(pts, fill=fill)


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
    Renders high-production vertical short video (1080x1920, 9:16) with
    authentic social video interface overlay, kinetic extra-bold captions (64-74px),
    animated multi-color audio visualizer, and proportional pacing.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    mp4_path = os.path.join(output_dir, f"{asset_id}.mp4")

    width, height = 1080, 1920
    total_frames = int(duration_seconds * fps)

    # Proportional Timeline Segmentation
    hook_duration = min(6.0, max(2.5, duration_seconds * 0.16))
    cta_duration = min(6.0, max(2.0, duration_seconds * 0.14))
    breakdown_duration = max(1.0, duration_seconds - hook_duration - cta_duration)

    num_steps = len(script_lines) if script_lines else 1
    step_duration = breakdown_duration / num_steps

    font_hook = get_bold_font(72)
    font_step = get_bold_font(64)
    font_cta = get_bold_font(60)
    font_pill_large = get_bold_font(32)
    font_pill_medium = get_bold_font(28)
    font_sub = get_default_font(26)

    content_max_w = width - 260  # Room for right engagement sidebar

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
        pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    else:
        try:
            import cv2
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            cv_writer = cv2.VideoWriter(mp4_path, fourcc, fps, (width, height))
        except Exception:
            pass

    for frame_idx in range(total_frames):
        current_time = frame_idx / fps

        img = Image.new("RGB", (width, height), BRAND_DARK_BG)
        draw = ImageDraw.Draw(img)

        # 1. Atmospheric Ambient Glow
        glow_y = int(380 + 90 * math.sin(frame_idx * 0.12))
        for r in range(450, 0, -30):
            alpha = int(45 * (1 - r / 450))
            draw.ellipse(
                [540 - r, glow_y - r, 540 + r, glow_y + r],
                fill=(BRAND_PRIMARY[0] // 4 + alpha, 10, BRAND_SECONDARY[2] // 4 + alpha)
            )

        # 2. Authentic Social Header Overlay
        # Avatar
        draw.ellipse([50, 60, 130, 140], fill=BRAND_PRIMARY)
        draw.text((72, 82), "IX", font=get_bold_font(36), fill=TEXT_PRIMARY)
        # Handle
        draw.text((150, 72), "incubrix.growth", font=get_bold_font(34), fill=TEXT_PRIMARY)
        # Verified Badge
        draw.ellipse([395, 78, 427, 110], fill=BRAND_ACCENT)
        draw_vector_check(draw, 411, 94, size=14, fill=TEXT_PRIMARY, width=3)
        # Audio track info
        draw.text((150, 114), "Original Audio • IncuBrix Growth OS", font=font_sub, fill=BRAND_ACCENT)

        # Top real-time progress bar (0 to 100%)
        overall_pct = min(1.0, max(0.0, current_time / duration_seconds))
        draw.rectangle([0, 0, width, 12], fill=(30, 41, 59))
        draw.rectangle([0, 0, int(width * overall_pct), 12], fill=BRAND_SECONDARY)

        # 3. Right-Side Social Engagement Bar (Reels / TikTok / Shorts)
        side_x = width - 110
        side_start_y = 750
        icons_def = [
            ("heart", "38.4K", BRAND_SECONDARY),
            ("chat", "1,240", TEXT_PRIMARY),
            ("share", "4.9K", BRAND_ACCENT),
            ("bookmark", "2.1K", BRAND_YELLOW)
        ]
        for i, (itype, count, icol) in enumerate(icons_def):
            iy = side_start_y + i * 140
            draw.ellipse([side_x - 32, iy - 32, side_x + 32, iy + 32], fill=(25, 33, 56), outline=(51, 65, 85), width=2)
            if itype == "heart":
                draw_vector_heart(draw, side_x, iy, size=24, fill=icol)
            elif itype == "chat":
                draw_vector_chat(draw, side_x, iy, size=24, fill=icol)
            elif itype == "share":
                draw_vector_share(draw, side_x, iy, size=24, fill=icol)
            elif itype == "bookmark":
                draw_vector_bookmark(draw, side_x, iy, size=24, fill=icol)
            draw.text((side_x - 22, iy + 40), count, font=get_bold_font(20), fill=TEXT_PRIMARY)

        # 4. Phased Content
        if current_time < hook_duration:
            # ---------------- HOOK PHASE ----------------
            draw.rounded_rectangle([60, 220, 520, 290], radius=35, fill=(30, 27, 75), outline=BRAND_YELLOW, width=3)
            draw_vector_lightning(draw, 90, 255, size=22, fill=BRAND_YELLOW)
            draw.text((115, 238), "ATTENTION CREATORS", font=font_pill_large, fill=BRAND_YELLOW)

            # Giant kinetic captions with drop shadow
            hook_y = draw_wrapped_text(draw, hook, 60, 330, content_max_w, font_hook, TEXT_PRIMARY, line_spacing=20, draw_shadow=True)

            # Animated Radar Graphic in Center
            cx, cy = 460, 960
            r_pulse = int(18 * math.sin(frame_idx * 0.4))
            draw.ellipse([cx - 150 - r_pulse, cy - 150 - r_pulse, cx + 150 + r_pulse, cy + 150 + r_pulse], outline=BRAND_PRIMARY, width=4)
            draw.ellipse([cx - 95, cy - 95, cx + 95, cy + 95], outline=BRAND_SECONDARY, width=5)
            draw.ellipse([cx - 45 + r_pulse, cy - 45 + r_pulse, cx + 45 - r_pulse, cy + 45 - r_pulse], fill=BRAND_YELLOW)
            draw.text((cx - 165, cy + 175), "AI REPURPOSING MATRIX", font=get_bold_font(28), fill=BRAND_ACCENT)

        elif current_time < (duration_seconds - cta_duration):
            # ---------------- STEP BREAKDOWN PHASE ----------------
            step_idx = min(num_steps - 1, max(0, int((current_time - hook_duration) / step_duration)))
            step_text = script_lines[step_idx] if script_lines else "Multiply your content into 30 native assets."
            step_elapsed = current_time - hook_duration - (step_idx * step_duration)
            step_pct = min(1.0, max(0.0, step_elapsed / step_duration))

            step_txt = f"STEP {step_idx + 1} OF {num_steps}"
            draw.rounded_rectangle([60, 220, 370, 290], radius=35, fill=BRAND_SECONDARY)
            draw.text((95, 238), step_txt, font=font_pill_large, fill=TEXT_PRIMARY)
            draw.text((390, 242), "• OPERATIONAL FRAMEWORK", font=font_pill_medium, fill=BRAND_ACCENT)

            step_y = draw_wrapped_text(draw, step_text, 60, 330, content_max_w, font_step, TEXT_PRIMARY, line_spacing=18, draw_shadow=True)

            # Dynamic 22-Bar Audio Visualizer
            base_x = 70
            for b in range(22):
                h_bar = max(30, int(90 + 75 * math.sin(frame_idx * 0.5 + b * 0.48)))
                b_col = BRAND_ACCENT if b % 2 == 0 else BRAND_YELLOW
                draw.rounded_rectangle([base_x + b * 36, 1050 - h_bar, base_x + b * 36 + 24, 1050], radius=10, fill=b_col)

            # Step Progress Scrubber
            draw.rounded_rectangle([60, 1100, width - 200, 1122], radius=11, fill=(30, 41, 59))
            draw.rounded_rectangle([60, 1100, 60 + int((width - 260) * step_pct), 1122], radius=11, fill=BRAND_ACCENT)
            draw.text((60, 1135), f"Step Progress: {int(step_pct * 100)}%", font=font_pill_medium, fill=TEXT_MUTED)

        else:
            # ---------------- CTA & FINALE PHASE ----------------
            draw.rounded_rectangle([60, 220, 480, 290], radius=35, fill=(6, 78, 59), outline=BRAND_SUCCESS, width=3)
            draw_vector_check(draw, 90, 255, size=18, fill=BRAND_SUCCESS, width=4)
            draw.text((115, 238), "READY TO LAUNCH", font=font_pill_large, fill=BRAND_SUCCESS)

            cta_y = draw_wrapped_text(draw, cta, 60, 330, content_max_w, font_cta, TEXT_PRIMARY, line_spacing=18, draw_shadow=True)

            # Giant Action Button
            btn_y = 800
            draw.rounded_rectangle([60, btn_y, width - 200, btn_y + 140], radius=40, fill=(79, 70, 229), outline=BRAND_YELLOW, width=4)
            btn_str = "VISIT: incubrix.com ->"
            bbox_b = draw.textbbox((0, 0), btn_str, font=get_bold_font(52))
            bw = bbox_b[2] - bbox_b[0]
            draw.text((60 + (width - 260 - bw) // 2, btn_y + 42), btn_str, font=get_bold_font(52), fill=TEXT_PRIMARY)

        # 5. Bottom Anchored Callout Banner
        bot_y0, bot_y1 = height - 320, height - 160
        draw.rounded_rectangle([50, bot_y0, width - 180, bot_y1], radius=28, fill=(15, 23, 42), outline=BRAND_PRIMARY, width=3)
        draw_vector_lightning(draw, 78, bot_y0 + 40, size=20, fill=BRAND_YELLOW)
        draw.text((100, bot_y0 + 26), "INCUBRIX CREATOR OS", font=font_pill_large, fill=BRAND_YELLOW)
        draw.text((80, bot_y0 + 74), "1 Input -> 30 Ready-to-Publish Assets Weekly", font=get_bold_font(32), fill=TEXT_PRIMARY)

        # Caption snippet
        draw.text((50, height - 130), "#ContentRepurposing #GrowthOS #SocialEngine", font=font_sub, fill=BRAND_ACCENT)

        # Output frame
        if pipe:
            pipe.stdin.write(img.tobytes())
        elif cv_writer:
            import numpy as np
            import cv2
            frame_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            cv_writer.write(frame_cv)

    if pipe:
        pipe.stdin.close()
        pipe.wait()
    elif cv_writer:
        cv_writer.release()

    # Save editable source JSON
    source_path = os.path.join("output/editable_sources", f"{asset_id}_source.json")
    Path("output/editable_sources").mkdir(parents=True, exist_ok=True)
    source_data = {
        "asset_id": asset_id,
        "format": "vertical_video_9_16",
        "duration_seconds": duration_seconds,
        "fps": fps,
        "dimensions": f"{width}x{height}",
        "hook": hook,
        "script_lines": script_lines,
        "cta": cta
    }
    with open(source_path, "w", encoding="utf-8") as f:
        json.dump(source_data, f, indent=2)

    return mp4_path, source_path


def render_graphic(
    asset_id: str,
    headline: str,
    body_text: str,
    cta: str,
    output_dir: str = "output/assets"
) -> Tuple[str, str]:
    """
    Renders a square 1080x1080 PNG executive graphic/quote card with large,
    high-impact typography and structured 3-step value blocks.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    width, height = 1080, 1080
    graphic_path = os.path.join(output_dir, f"{asset_id}.png")

    img = Image.new("RGB", (width, height), BRAND_DARK_BG)
    draw = ImageDraw.Draw(img)

    # Gradient top glow
    for y_grad in range(0, 420):
        alpha = int(60 * (1 - y_grad / 420))
        draw.line([(0, y_grad), (width, y_grad)], fill=(BRAND_PRIMARY[0] // 3 + alpha, 15, BRAND_SECONDARY[2] // 3 + alpha))

    # Header Badge: IncuBrix Verified Channel
    bx, by, bw, bh = 60, 60, width - 120, 90
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=24, fill=BRAND_SURFACE, outline=BRAND_PRIMARY, width=2)
    draw.ellipse([bx + 18, by + 18, bx + 72, by + 72], fill=BRAND_PRIMARY)
    draw.text((bx + 32, by + 28), "IX", font=get_bold_font(28), fill=TEXT_PRIMARY)
    draw.text((bx + 90, by + 30), "INCUBRIX CREATOR OPERATIONS", font=get_bold_font(28), fill=TEXT_PRIMARY)
    draw.ellipse([bx + bw - 55, by + 28, bx + bw - 23, by + 60], fill=BRAND_ACCENT)
    draw_vector_check(draw, bx + bw - 39, by + 44, size=14, fill=TEXT_PRIMARY, width=3)

    # Eyebrow Pill
    eyebrow_text = "STRATEGIC BLUEPRINT • ZERO EXTRA EFFORT"
    bbox_e = draw.textbbox((0, 0), eyebrow_text, font=get_bold_font(26))
    ew = (bbox_e[2] - bbox_e[0]) + 50
    draw.rounded_rectangle([60, 185, 60 + ew, 245], radius=30, fill=(30, 27, 75), outline=BRAND_YELLOW, width=2)
    draw_vector_lightning(draw, 80, 215, size=18, fill=BRAND_YELLOW)
    draw.text((100, 202), eyebrow_text, font=get_bold_font(26), fill=BRAND_YELLOW)

    # Large, bold, non-truncated headline (60px)
    font_hl = get_bold_font(60)
    cur_y = draw_wrapped_text(draw, headline, 60, 275, width - 120, font_hl, TEXT_PRIMARY, line_spacing=16)

    # 3-Step Systematic Value Blocks
    bullets = [
        ("01", "Turn 1 Long-Form Piece Into 30 Native Assets"),
        ("02", "Native Video, Carousel Decks & Short Posts"),
        ("03", "Full Attribution with Tracked UTMs at incubrix.com")
    ]
    cur_y += 28
    for num, b_txt in bullets:
        draw.rounded_rectangle([60, cur_y, width - 60, cur_y + 80], radius=18, fill=BRAND_SURFACE, outline=(51, 65, 85), width=2)
        draw.rounded_rectangle([75, cur_y + 16, 125, cur_y + 64], radius=12, fill=BRAND_PRIMARY)
        draw.text((85, cur_y + 24), num, font=get_bold_font(22), fill=TEXT_PRIMARY)
        draw.text((145, cur_y + 26), b_txt, font=get_bold_font(28), fill=(241, 245, 249))
        cur_y += 98

    # CTA Banner
    cur_y = max(cur_y + 15, height - 190)
    draw.rounded_rectangle([60, cur_y, width - 60, cur_y + 100], radius=24, fill=(30, 41, 59), outline=BRAND_SECONDARY, width=3)
    draw_vector_lightning(draw, 85, cur_y + 36, size=18, fill=BRAND_ACCENT)
    draw.text((105, cur_y + 20), "ACTIONABLE OPERATING PROCEDURE", font=get_bold_font(22), fill=BRAND_ACCENT)
    draw.text((90, cur_y + 52), f"Explore System: {cta}", font=get_bold_font(28), fill=TEXT_PRIMARY)

    # Footer
    draw.text((60, height - 55), "IncuBrix Growth Engine • Verified Submission Kit", font=get_default_font(22), fill=TEXT_MUTED)

    img.save(graphic_path, "PNG")

    # Save editable source JSON
    source_path = os.path.join("output/editable_sources", f"{asset_id}_source.json")
    Path("output/editable_sources").mkdir(parents=True, exist_ok=True)
    source_data = {
        "asset_id": asset_id,
        "format": "square_graphic_1_1",
        "dimensions": "1080x1080",
        "headline": headline,
        "body_text": body_text,
        "cta": cta
    }
    with open(source_path, "w", encoding="utf-8") as f:
        json.dump(source_data, f, indent=2)

    return graphic_path, source_path


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

    font_slide_header = get_bold_font(60)
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
        pill_text = f"INSIGHT #{i} • CORE FRAMEWORK"
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
        draw.text((80, height - 100), f"Swipe >> {cta}", font=font_pill, fill=BRAND_ACCENT)
        draw.text((width - 450, height - 100), "incubrix.com • Turnkey Growth", font=font_small, fill=TEXT_MUTED)

        slide_path = os.path.join(output_dir, f"{asset_id}_slide_{i}.png")
        img.save(slide_path, "PNG")
        rendered_slides_paths.append(slide_path)

    # Save editable source JSON
    source_path = os.path.join("output/editable_sources", f"{asset_id}_source.json")
    Path("output/editable_sources").mkdir(parents=True, exist_ok=True)
    source_data = {
        "asset_id": asset_id,
        "format": "vertical_carousel_4_5",
        "slide_count": len(slides),
        "dimensions": f"{width}x{height}",
        "title": title,
        "slides": slides,
        "cta": cta,
        "rendered_files": rendered_slides_paths
    }
    with open(source_path, "w", encoding="utf-8") as f:
        json.dump(source_data, f, indent=2)

    return primary_cover_path, source_path
