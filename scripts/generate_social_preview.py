"""Generate the GitHub social-preview image (1280x640) for the repository.

The output goes to ``docs/assets/social-preview.png`` and is meant to be
uploaded once at GitHub Settings -> General -> Social preview. The image
keeps the same icon language as the desktop app (re-uses ``draw_icon``
from generate_app_icons.py) on a clean Toss-style white surface.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from generate_app_icons import draw_icon  # noqa: E402

OUTPUT = ROOT / "docs" / "assets" / "social-preview.png"

CANVAS_W = 1280
CANVAS_H = 640
ICON_SIZE = 360
PADDING_LEFT = 96


def _load_font(size: int, *, bold: bool) -> ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/seguivar.ttf" if bold else "C:/Windows/Fonts/seguivb.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (255, 255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    # Soft Toss-blue accent stripe behind the icon.
    accent = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    accent_draw = ImageDraw.Draw(accent)
    accent_draw.rounded_rectangle(
        (PADDING_LEFT - 32, (CANVAS_H - ICON_SIZE) // 2 - 32,
         PADDING_LEFT + ICON_SIZE + 32,
         (CANVAS_H + ICON_SIZE) // 2 + 32),
        radius=64,
        fill=(232, 242, 255, 255),  # #e8f2ff (Toss brand-soft)
    )
    canvas.alpha_composite(accent)

    # Render the existing app icon at 360 px and paste it.
    icon = draw_icon(ICON_SIZE)
    icon_x = PADDING_LEFT
    icon_y = (CANVAS_H - ICON_SIZE) // 2
    canvas.alpha_composite(icon, (icon_x, icon_y))

    # Wordmark + tagline (right column).
    text_x = PADDING_LEFT + ICON_SIZE + 80
    title_font = _load_font(96, bold=True)
    sub_font = _load_font(34, bold=False)
    accent_font = _load_font(22, bold=True)

    # Eyebrow label.
    draw.text(
        (text_x, 168),
        "DESKTOP WORKSPACE",
        font=accent_font,
        fill=(49, 130, 246, 255),  # #3182f6
        spacing=4,
    )
    # Title.
    draw.text((text_x, 200), "CatPrice", font=title_font, fill=(25, 31, 40, 255))
    # Tagline.
    tagline_lines = [
        "Real-time metal prices,",
        "catalyst cost intelligence,",
        "and source-linked benchmarks.",
    ]
    y = 320
    for line in tagline_lines:
        draw.text((text_x, y), line, font=sub_font, fill=(78, 89, 104, 255))
        y += 44

    # Bottom-right footer chip.
    chip_text = "github.com/hyunjin-kor/CatPrice"
    chip_font = _load_font(22, bold=True)
    bbox = draw.textbbox((0, 0), chip_text, font=chip_font)
    chip_w = bbox[2] - bbox[0]
    chip_h = bbox[3] - bbox[1]
    chip_pad_x = 18
    chip_pad_y = 10
    chip_x = CANVAS_W - chip_w - chip_pad_x * 2 - 48
    chip_y = CANVAS_H - chip_h - chip_pad_y * 2 - 48
    draw.rounded_rectangle(
        (chip_x, chip_y,
         chip_x + chip_w + chip_pad_x * 2,
         chip_y + chip_h + chip_pad_y * 2),
        radius=24,
        fill=(25, 31, 40, 255),
    )
    draw.text(
        (chip_x + chip_pad_x, chip_y + chip_pad_y - 2),
        chip_text,
        font=chip_font,
        fill=(255, 255, 255, 255),
    )

    # Hairline border so the white canvas has a visible edge in dark Slack/etc.
    draw.rectangle((0, 0, CANVAS_W - 1, CANVAS_H - 1), outline=(229, 232, 235, 255), width=2)

    canvas.convert("RGB").save(OUTPUT, format="PNG", optimize=True)
    print(f"wrote {OUTPUT.relative_to(ROOT)} ({OUTPUT.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
