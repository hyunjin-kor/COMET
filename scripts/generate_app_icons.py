"""Resize the master brand asset into the production icon set.

Single source of truth: ``frontend/public/icon-source.png``. Replace
that one file when the brand icon changes; this script:

1. detects the rounded-square frame already baked into the source
   image (typical for an AI-generated app icon render),
2. crops to that frame's exact bounding box,
3. resizes to each output size,
4. applies a rounded-corner alpha mask whose radius matches the
   detected frame curvature, scaled down to the target size.

This way the file edges follow the frame the brand asset already
shows — we never invent a new corner radius and never crop into
the frame contents.

Outputs:
  frontend/public/icon-32x32.png
  frontend/public/icon-128x128.png
  frontend/public/icon-256x256.png
  frontend/public/icon-512x512.png
  frontend/public/icon.png            (mirror of 512x512)
  frontend/public/icon.ico            (multi-size: 16/24/32/48/64/128/256)
  electron/icon.png                   (mirror of 512x512)
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "frontend" / "public"
ELECTRON_DIR = ROOT / "electron"
SOURCE = PUBLIC_DIR / "icon-source.png"

PNG_SIZES = (32, 128, 256, 512)
ICO_SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
CONTENT_THRESHOLD = 18  # sum-of-RGB-channel diff vs corner background; tuned empirically


def _content_mask(img: Image.Image, threshold: int = CONTENT_THRESHOLD) -> np.ndarray:
    """True wherever a pixel differs from the corner background by ``threshold`` RGB sum."""
    arr = np.array(img.convert("RGB"))
    bg = arr[0:30, 0:30].astype(float).mean(axis=(0, 1))
    diff = np.abs(arr.astype(float) - bg).sum(axis=2)
    return diff > threshold


def detect_frame(img: Image.Image) -> tuple[Image.Image, int]:
    """Detect the baked-in rounded frame and return ``(cropped_square, radius_px)``.

    The returned image is the source cropped tightly to the frame's outer
    bounding box, then center-cropped to square if the bbox isn't already.
    The radius is the corner curvature in pixels at that crop's resolution.
    """
    mask = _content_mask(img)
    h, w = mask.shape
    ys_any = np.any(mask, axis=1)
    xs_any = np.any(mask, axis=0)
    if not ys_any.any():
        # No detectable frame — treat the whole image as content with no rounding.
        return img, 0

    top = int(np.argmax(ys_any))
    bottom = int(h - 1 - np.argmax(ys_any[::-1]))
    left = int(np.argmax(xs_any))
    right = int(w - 1 - np.argmax(xs_any[::-1]))

    # Radius: at the topmost content row (ignoring AA), the first content x sits
    # at ``left + radius``; symmetric on the right side. Average for stability.
    sample_y = min(top + 3, bottom - 1)
    row = np.where(mask[sample_y])[0]
    if len(row) == 0:
        radius = 0
    else:
        radius_left = int(row.min()) - left
        radius_right = right - int(row.max())
        radius = max(0, (radius_left + radius_right) // 2)

    cropped = img.crop((left, top, right + 1, bottom + 1))
    cw, ch = cropped.size
    if cw != ch:
        side = min(cw, ch)
        cl = (cw - side) // 2
        ct = (ch - side) // 2
        cropped = cropped.crop((cl, ct, cl + side, ct + side))
    return cropped, radius


def render(cropped: Image.Image, source_radius: int, target: int) -> Image.Image:
    """Resize the framed source to ``target`` square and apply a matching rounded mask."""
    source_size = cropped.size[0]
    scaled_radius = int(round(source_radius * target / source_size))
    img = cropped.resize((target, target), Image.LANCZOS)
    mask = Image.new("L", (target, target), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, target - 1, target - 1), radius=scaled_radius, fill=255
    )
    r, g, b, a = img.split()
    return Image.merge("RGBA", (r, g, b, ImageChops.multiply(a, mask)))


def load_source() -> tuple[Image.Image, int]:
    if not SOURCE.exists():
        raise FileNotFoundError(
            f"icon source not found: {SOURCE}\n"
            "Place a square (or near-square) PNG at this path before running."
        )
    return detect_frame(Image.open(SOURCE).convert("RGBA"))


def save_pngs(cropped: Image.Image, radius: int) -> None:
    for size in PNG_SIZES:
        icon = render(cropped, radius, size)
        icon.save(PUBLIC_DIR / f"icon-{size}x{size}.png")
        if size == 512:
            icon.save(PUBLIC_DIR / "icon.png")
            icon.save(ELECTRON_DIR / "icon.png")


def save_ico(cropped: Image.Image, radius: int) -> None:
    icon = render(cropped, radius, 512)
    icon.save(PUBLIC_DIR / "icon.ico", format="ICO", sizes=ICO_SIZES)


def main() -> None:
    cropped, radius = load_source()
    save_pngs(cropped, radius)
    save_ico(cropped, radius)
    print(
        f"detected frame: cropped to {cropped.size[0]}x{cropped.size[1]} "
        f"with corner radius {radius}px (~{radius / cropped.size[0] * 100:.1f}% of side)"
    )


if __name__ == "__main__":
    main()
