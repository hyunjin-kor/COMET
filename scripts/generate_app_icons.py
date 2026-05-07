"""Resize the master brand asset into the production icon set.

Single source of truth: ``frontend/public/icon-source.png``. Replace
that one file when the brand icon changes; this script downscales it
into every PNG / ICO output the desktop app and the docs reference.

Outputs:
  frontend/public/icon-32x32.png
  frontend/public/icon-128x128.png
  frontend/public/icon-256x256.png
  frontend/public/icon-512x512.png
  frontend/public/icon.png            (mirror of 512x512)
  frontend/public/icon.ico            (multi-size: 16/24/32/48/64/128/256)
  electron/icon.png                   (mirror of 512x512)

If the source isn't square (typical for an AI-generated render), the
image is center-cropped to the smaller dimension before resizing, so
the frame and subject stay in proportion.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "frontend" / "public"
ELECTRON_DIR = ROOT / "electron"
SOURCE = PUBLIC_DIR / "icon-source.png"

PNG_SIZES = (32, 128, 256, 512)
ICO_SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def to_square(img: Image.Image) -> Image.Image:
    """Center-crop to the smaller side so resizes don't distort."""
    w, h = img.size
    if w == h:
        return img
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    return img.crop((left, top, left + side, top + side))


def load_source() -> Image.Image:
    if not SOURCE.exists():
        raise FileNotFoundError(
            f"icon source not found: {SOURCE}\n"
            "Place a square (or near-square) PNG at this path before running."
        )
    return to_square(Image.open(SOURCE).convert("RGBA"))


def resized(source: Image.Image, size: int) -> Image.Image:
    return source.resize((size, size), Image.LANCZOS)


def save_pngs(source: Image.Image) -> None:
    for size in PNG_SIZES:
        icon = resized(source, size)
        icon.save(PUBLIC_DIR / f"icon-{size}x{size}.png")
        if size == 512:
            icon.save(PUBLIC_DIR / "icon.png")
            icon.save(ELECTRON_DIR / "icon.png")


def save_ico(source: Image.Image) -> None:
    icon = resized(source, 512)
    icon.save(PUBLIC_DIR / "icon.ico", format="ICO", sizes=ICO_SIZES)


def main() -> None:
    source = load_source()
    save_pngs(source)
    save_ico(source)
    print(f"regenerated icons from {SOURCE.name} ({source.size[0]}×{source.size[1]} after square crop)")


if __name__ == "__main__":
    main()
