"""
IncuBrix Media Renderer - Proportional Social Media Production Engine
Generates verified, platform-native creative files:
1. Full vertical MP4 short videos (1080x1920, 9:16) with fitted card stage,
   extra-bold prominent typography (64-74px), 150px animated audio waveform bars,
   and proportional timeline pacing (hook -> step breakdown -> verified destination).
2. Square executive graphics/quote cards (1080x1080) with bold typography and 3-step value blocks.
3. Multi-slide vertical carousel decks (1080x1350, 4:5 vertical).
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

# Original IncuBrix Design Tokens
BRAND_DARK_BG = (15, 23, 42)       # #0F172A
BRAND_SURFACE = (30, 41, 59)       # #1E293B
BRAND_PRIMARY = (99, 102, 241)     # #6366F1 Electric Indigo
BRAND_SECONDARY = (236, 72, 153)   # #EC4899 Neon Pink
BRAND_ACCENT = (56, 189, 248)      # #38BDF8 Vivid Sky Blue
BRAND_SUCCESS = (16, 185, 129)     # #10B981 Emerald Green
BRAND_YELLOW = (250, 204, 21)      # #FACC15 Accent Yellow
TEXT_PRIMARY = (255, 255, 255)
TEXT_MUTED = (148, 163, 184)


def get_default_font(size: int = 36) -> ImageFont.ImageFont:
    """Loads standard system sans-serif font, fallback to default."""
    candidates = [
        "C:\\Windows\\Fonts\\segoeui.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\calibri.ttf",
        "C:\\Windows\\Fonts\\tahoma.ttf"
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def get_bold_font(size: int = 44) -> ImageFont.ImageFont:
    candidates = [
        "C:\\Windows\\Fonts\\segoeuib.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\calibrib.ttf",
        "C:\\Windows\\Fonts\\trebucbd.ttf"
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return get_default_font(size)


def draw_header_badge(draw: ImageDraw.ImageDraw, text: str = "INCUBRIX SHORTS ENGINE", width: int = 1080):
    badge_w = 640
    badge_h = 84
    x0 = (width - badge_w) // 2
    y0 = 60
    draw.rounded_rectangle([x0, y0, x0 + badge_w, y0 + badge_h], radius=42, fill=BRAND_SURFACE, outline=BRAND_PRIMARY, width=3)
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
    line_spacing: int = 18
) -> int:
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
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
    Renders an actual 1080x1920 vertical MP4 video fitted to the 9:16 aspect ratio.
    Features the beloved original IncuBrix Shorts Engine aesthetic, scaled up with
    prominent extra-bold typography (64-72px), 150px animated audio waveforms,
    and proportional timeline pacing (Hook -> Step Breakdown -> Verified Destination).
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    mp4_path = os.path.join(output_dir, f"{asset_id}.mp4")

    width, height = 1080, 1920
    total_frames = int(duration_seconds * fps)

    # Proportional Timeline Segmentation
    hook_duration = min(6.0, max(2.5, duration_seconds * 0.16))
    cta_duration = min(6.0, max(2.0, duration_seconds * 0.14))
    body_duration = max(1.0, duration_seconds - hook_duration - cta_duration)

    num_steps = len(script_lines) if script_lines else 1
    step_duration = body_duration / num_steps

    # High-Impact Proportional Fonts
    font_hero_hook = get_bold_font(72)
    font_hero_step = get_bold_font(64)
    font_pill = get_bold_font(32)
    font_body = get_default_font(40)
    font_cta = get_bold_font(60)

    # Main Card Bounds (Fitted to 9:16 Canvas, from y=180 to y=1720)
    card_x0, card_x1 = 60, width - 60
    card_y0, card_y1 = 180, 1720

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

        # Base Frame
        img = Image.new("RGB", (width, height), BRAND_DARK_BG)
        draw = ImageDraw.Draw(img)

        # 1. Subtle top gradient
        for y_grad in range(0, 450):
            alpha = int(65 * (1 - y_grad / 450))
            draw.line([(0, y_grad), (width, y_grad)], fill=(BRAND_PRIMARY[0] // 3 + alpha, BRAND_PRIMARY[1] // 4, BRAND_PRIMARY[2] // 2 + alpha))

        # 2. Header Badge (Original IncuBrix Style)
        draw_header_badge(draw, text="INCUBRIX SHORTS ENGINE", width=width)

        # 3. Top Progress Bar
        progress = min(1.0, max(0.0, current_time / duration_seconds))
        bar_w = int(width * progress)
        draw.rectangle([0, 0, width, 14], fill=BRAND_SURFACE)
        draw.rectangle([0, 0, bar_w, 14], fill=BRAND_SECONDARY)

        # 4. Central Content Switching by Timeline
        if current_time < hook_duration:
            # ---------------- HOOK PHASE (0 - 2.5s / 6s) ----------------
            draw.rounded_rectangle([card_x0, card_y0, card_x1, card_y1], radius=36, fill=BRAND_SURFACE, outline=BRAND_PRIMARY, width=4)

            # Eyebrow Pill
            pill_txt = "[ STOP WASTING 18 HOURS/WEEK ]"
            bbox_p = draw.textbbox((0, 0), pill_txt, font=font_pill)
            pw = (bbox_p[2] - bbox_p[0]) + 50
            draw.rounded_rectangle([100, 230, 100 + pw, 300], radius=35, fill=(15, 23, 42), outline=BRAND_ACCENT, width=2)
            draw.text((125, 248), pill_txt, font=font_pill, fill=BRAND_ACCENT)

            # Prominent Hook Headline (fills upper card with 72px bold text)
            next_y = draw_wrapped_text(draw, f'"{hook}"', 100, 340, width - 200, font_hero_hook, TEXT_PRIMARY, line_spacing=24)

            # Animated Concentric Pulse Ring (Original Style, expanded)
            cx, cy = 540, 960
            pulse = int(math.sin(frame_idx * 0.4) * 20)
            draw.ellipse([cx - 160 - pulse, cy - 160 - pulse, cx + 160 + pulse, cy + 160 + pulse], outline=(51, 65, 85), width=3)
            draw.ellipse([cx - 100 - pulse // 2, cy - 100 - pulse // 2, cx + 100 + pulse // 2, cy + 100 + pulse // 2], outline=BRAND_PRIMARY, width=4)
            draw.ellipse([cx - 45, cy - 45, cx + 45, cy + 45], fill=BRAND_SECONDARY)
            draw.text((cx - 170, cy + 160), "VIRAL HOOK INITIALIZED", font=font_pill, fill=BRAND_ACCENT)

            # Bottom Takeaway Callout inside the card
            draw.rounded_rectangle([100, 1480, width - 100, 1640], radius=24, fill=(15, 23, 42), outline=BRAND_PRIMARY, width=2)
            draw.text((130, 1515), ">> CORE OPERATIONAL STRATEGY", font=get_bold_font(28), fill=BRAND_ACCENT)
            draw.text((130, 1565), "Turn 1 Long Video Into a Week of Native Posts", font=get_bold_font(34), fill=TEXT_PRIMARY)

        elif current_time < (duration_seconds - cta_duration):
            # ---------------- STEP BREAKDOWN PHASE ----------------
            step_idx = min(num_steps - 1, max(0, int((current_time - hook_duration) / step_duration)))
            step_text = script_lines[step_idx] if script_lines else "Multiply your content into 30 native assets."

            draw.rounded_rectangle([card_x0, card_y0, card_x1, card_y1], radius=36, fill=BRAND_SURFACE, outline=BRAND_ACCENT, width=4)

            # Step Pill
            pill_txt = f"OPERATIONAL FRAMEWORK #{step_idx + 1}"
            bbox_p = draw.textbbox((0, 0), pill_txt, font=font_pill)
            pw = (bbox_p[2] - bbox_p[0]) + 50
            draw.rounded_rectangle([100, 230, 100 + pw, 300], radius=35, fill=(15, 23, 42), outline=BRAND_SECONDARY, width=2)
            draw.text((125, 248), pill_txt, font=font_pill, fill=BRAND_SECONDARY)

            # Step Headline (64px Bold)
            next_y = draw_wrapped_text(draw, step_text, 100, 340, width - 200, font_hero_step, TEXT_PRIMARY, line_spacing=22)

            # Prominent Animated Sound Waveform Bars (Original Style, now 150px tall across the center!)
            base_x = 120
            wave_y_base = 1000
            for bar_i in range(20):
                wave_h = max(20, int(90 + 70 * math.sin(frame_idx * 0.5 + bar_i * 0.5)))
                bar_col = BRAND_ACCENT if bar_i % 2 == 0 else BRAND_SECONDARY
                draw.rounded_rectangle([base_x + bar_i * 42, wave_y_base - wave_h, base_x + bar_i * 42 + 24, wave_y_base], radius=8, fill=bar_col)

            # Step Progress Bar inside the card
            step_elapsed = current_time - hook_duration - (step_idx * step_duration)
            step_pct = min(1.0, max(0.0, step_elapsed / step_duration))
            draw.rounded_rectangle([100, 1080, width - 100, 1106], radius=13, fill=(15, 23, 42))
            draw.rounded_rectangle([100, 1080, 100 + int((width - 200) * step_pct), 1106], radius=13, fill=BRAND_ACCENT)
            draw.text((100, 1130), f"Step {step_idx + 1} of {num_steps}  •  {int(step_pct * 100)}% Complete", font=font_pill, fill=TEXT_MUTED)

            # Bottom Takeaway Callout inside the card
            draw.rounded_rectangle([100, 1480, width - 100, 1640], radius=24, fill=(15, 23, 42), outline=BRAND_PRIMARY, width=2)
            draw.text((130, 1515), ">> SYSTEMATIC AUTOMATION", font=get_bold_font(28), fill=BRAND_ACCENT)
            draw.text((130, 1565), "Eliminate 18 hours of manual video editing weekly.", font=get_bold_font(34), fill=TEXT_PRIMARY)

        else:
            # ---------------- CTA & FINALE PHASE ----------------
            draw.rounded_rectangle([card_x0, card_y0, card_x1, card_y1], radius=36, fill=BRAND_SURFACE, outline=BRAND_SUCCESS, width=4)

            pill_txt = "OFFICIAL VERIFIED DESTINATION"
            bbox_p = draw.textbbox((0, 0), pill_txt, font=font_pill)
            pw = (bbox_p[2] - bbox_p[0]) + 50
            draw.rounded_rectangle([100, 230, 100 + pw, 300], radius=35, fill=(15, 23, 42), outline=BRAND_SUCCESS, width=2)
            draw.text((125, 248), pill_txt, font=font_pill, fill=BRAND_SUCCESS)

            next_y = draw_wrapped_text(draw, cta, 100, 340, width - 200, font_cta, TEXT_PRIMARY, line_spacing=24)

            # Giant Verified Button
            btn_y0, btn_y1 = 880, 1060
            draw.rounded_rectangle([100, btn_y0, width - 100, btn_y1], radius=36, fill=BRAND_PRIMARY, outline=(129, 140, 248), width=3)
            btn_str = "VISIT: incubrix.com ->"
            bbox_b = draw.textbbox((0, 0), btn_str, font=font_cta)
            bw = bbox_b[2] - bbox_b[0]
            draw.text((100 + (width - 200 - bw) // 2, btn_y0 + 52), btn_str, font=font_cta, fill=TEXT_PRIMARY)

            # Bottom Guarantee Callout inside the card
            draw.rounded_rectangle([100, 1480, width - 100, 1640], radius=24, fill=(15, 23, 42), outline=BRAND_SUCCESS, width=2)
            draw.text((130, 1515), ">> TURNKEY LAUNCH READY", font=get_bold_font(28), fill=BRAND_SUCCESS)
            draw.text((130, 1565), "Start posting with zero extra effort today.", font=get_bold_font(34), fill=TEXT_PRIMARY)

        # 5. Footer Metadata (Original Style)
        draw.text((60, height - 120), "#CreatorOS #ContentRepurposing #GrowthEngine", font=get_bold_font(30), fill=TEXT_MUTED)
        draw.text((60, height - 70), "IncuBrix AI Social Growth Engine | 1080x1920 (9:16 Vertical)", font=get_default_font(26), fill=TEXT_MUTED)

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
    for y_grad in range(0, 360):
        alpha = int(55 * (1 - y_grad / 360))
        draw.line([(0, y_grad), (width, y_grad)], fill=(BRAND_PRIMARY[0] // 3 + alpha, BRAND_PRIMARY[1] // 4, BRAND_PRIMARY[2] // 2 + alpha))

    # Header Badge (Original Style)
    draw_header_badge(draw, text="INCUBRIX STRATEGIC BRIEF", width=width)

    # Main Card (fills 1080x1080 square canvas cleanly)
    card_x0, card_x1 = 60, width - 60
    card_y0, card_y1 = 180, height - 90
    draw.rounded_rectangle([card_x0, card_y0, card_x1, card_y1], radius=32, fill=BRAND_SURFACE, outline=BRAND_PRIMARY, width=3)

    # Eyebrow Pill
    eyebrow_text = "KEY TAKEAWAY  •  PROVEN SYSTEM"
    bbox_e = draw.textbbox((0, 0), eyebrow_text, font=get_bold_font(26))
    ew = (bbox_e[2] - bbox_e[0]) + 50
    draw.rounded_rectangle([100, 220, 100 + ew, 280], radius=30, fill=(15, 23, 42), outline=BRAND_SECONDARY, width=2)
    draw.text((125, 236), eyebrow_text, font=get_bold_font(26), fill=BRAND_SECONDARY)

    # Large Headline (60px Bold, never truncated)
    font_hl = get_bold_font(58)
    cur_y = draw_wrapped_text(draw, headline, 100, 310, width - 200, font_hl, TEXT_PRIMARY, line_spacing=18)

    # 3-Step Systematic Value Blocks
    bullets = [
        ("01", "Turn 1 Long-Form Piece Into 30 Native Assets"),
        ("02", "Native Video, Carousel Decks & Short Posts"),
        ("03", "Full Attribution with Tracked UTMs at incubrix.com")
    ]
    cur_y += 25
    for num, b_txt in bullets:
        draw.rounded_rectangle([100, cur_y, width - 100, cur_y + 80], radius=18, fill=(15, 23, 42), outline=(51, 65, 85), width=2)
        draw.rounded_rectangle([115, cur_y + 16, 165, cur_y + 64], radius=12, fill=BRAND_PRIMARY)
        draw.text((125, cur_y + 24), num, font=get_bold_font(22), fill=TEXT_PRIMARY)
        draw.text((185, cur_y + 26), b_txt, font=get_bold_font(28), fill=(241, 245, 249))
        cur_y += 98

    # Bottom CTA Box
    cur_y = max(cur_y + 15, height - 200)
    draw.rounded_rectangle([100, cur_y, width - 100, cur_y + 85], radius=20, fill=(15, 23, 42), outline=BRAND_ACCENT, width=2)
    draw.text((130, cur_y + 16), ">> CORE OPERATIONAL STRATEGY", font=get_bold_font(20), fill=BRAND_ACCENT)
    draw.text((130, cur_y + 44), f"Strategy: {cta}", font=get_bold_font(26), fill=TEXT_PRIMARY)

    # Footer
    draw.text((60, height - 60), "incubrix.com  •  Verified AI Content Engine  •  #CreatorOS", font=get_default_font(22), fill=TEXT_MUTED)

    img.save(graphic_path, "PNG")

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

    font_slide_header = get_bold_font(58)
    font_body_large = get_bold_font(44)
    font_body_regular = get_default_font(38)
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
        pill_text = f"INSIGHT #{i}  •  CORE FRAMEWORK"
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
