#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "media" / "reels"
REELS = json.loads((ROOT / "content" / "reels.json").read_text(encoding="utf-8"))
WIDTH, HEIGHT, FPS = 1080, 1920, 24
BG = (23, 27, 28)
PAPER = (243, 239, 229)
MUTED = (166, 170, 163)
ACCENT = (227, 131, 102)
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def wrap(text, font, max_width, draw):
    words = text.split()
    lines, line = [], ""
    for word in words:
        candidate = word if not line else f"{line} {word}"
        if draw.textlength(candidate, font=font) <= max_width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def slide_image(reel, index, text):
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    serif = ImageFont.truetype(SERIF, 83)
    small = ImageFont.truetype(SANS_BOLD, 27)
    footer = ImageFont.truetype(SANS, 25)
    label = ImageFont.truetype(SANS_BOLD, 24)

    draw.text((94, 100), "DISONANCIA COGNITIVA", font=small, fill=PAPER)
    draw.text((94, 158), "IDEAS EN TENSIÓN", font=label, fill=ACCENT)
    draw.text((WIDTH - 190, 100), f"{index + 1:02d} / 03", font=small, fill=MUTED)
    draw.line((94, 220, WIDTH - 94, 220), fill=(65, 70, 68), width=2)
    draw.line((94, HEIGHT - 232, WIDTH - 94, HEIGHT - 232), fill=(65, 70, 68), width=2)

    lines = wrap(text, serif, WIDTH - 210, draw)
    line_height = 112
    total_height = len(lines) * line_height
    y = (HEIGHT - total_height) // 2 - 15
    for line in lines:
        draw.text((94, y), line, font=serif, fill=PAPER)
        y += line_height

    draw.rounded_rectangle((94, HEIGHT - 174, 176, HEIGHT - 166), radius=4, fill=ACCENT)
    draw.text((198, HEIGHT - 192), reel["title"], font=footer, fill=MUTED)
    return image


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    blank = Image.new("RGB", (WIDTH, HEIGHT), BG)
    fade_frames = 9
    frames_per_slide = FPS * 4

    for reel in REELS:
        slides = [slide_image(reel, idx, text) for idx, text in enumerate(reel["slides"])]
        slides[0].save(OUTPUT / f"{reel['id']}.jpg", "JPEG", quality=88, optimize=True)

        target = OUTPUT / f"{reel['id']}.mp4"
        command = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "rawvideo", "-pixel_format", "rgb24", "-video_size", f"{WIDTH}x{HEIGHT}",
            "-framerate", str(FPS), "-i", "-", "-an",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "25",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(target),
        ]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            for slide in slides:
                for frame_number in range(frames_per_slide):
                    if frame_number < fade_frames:
                        alpha = frame_number / fade_frames
                    elif frame_number >= frames_per_slide - fade_frames:
                        alpha = (frames_per_slide - 1 - frame_number) / fade_frames
                    else:
                        alpha = 1.0
                    frame = Image.blend(blank, slide, max(0.0, min(1.0, alpha)))
                    process.stdin.write(frame.tobytes())
            process.stdin.close()
            error = process.stderr.read().decode("utf-8", errors="replace")
            result = process.wait()
            if result:
                raise RuntimeError(error or f"ffmpeg terminó con código {result}")
        except Exception:
            process.kill()
            process.wait()
            raise
        print(f"{target.relative_to(ROOT)} ({target.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
