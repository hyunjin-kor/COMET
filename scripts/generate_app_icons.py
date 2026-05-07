"""Resize the master brand asset into the production icon set.

Single source of truth: ``frontend/public/icon-source.png``. Replace
that one file when the brand icon changes; this script downscales it
into every PNG / ICO output the desktop app and the docs reference,
then trims a small uniform inset and applies an iOS-style rounded
mask so the file edges follow the rounded-square frame baked into
the brand asset.

The cream-to-mint gradient in the master extends edge-to-edge, so
auto-detection of the frame outline by colour difference isn't
reliable. Two fixed knobs control the result:

  * ``EDGE_INSET_RATIO`` — how much of each side to trim before
    rounding. Set this to skip whatever soft halo the AI render
    leaves around the frame (drop shadow, glow, anti-aliased gradient).
  * ``CORNER_RADIUS_RATIO`` — final corner curvature, fraction of the
    side after the inset crop. iOS app icons use ~22%.

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

from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "frontend" / "public"
ELECTRON_DIR = ROOT / "electron"
SOURCE = PUBLIC_DIR / "icon-source.png"

PNG_SIZES = (32, 128, 256, 512)
ICO_SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
EDGE_INSET_RATIO = 0.05    # trim 5% off each side before rounding
CORNER_RADIUS_RATIO = 0.22 # iOS-standard squircle approximation


def crop_to_square_with_inset(img: Image.Image, inset_ratio: float = EDGE_INSET_RATIO) -> Image.Image:
    """Center-crop to square and trim ``inset_ratio`` off each side."""
    w, h = img.size
    side = int(min(w, h) * (1.0 - 2 * inset_ratio))
    cx, cy = w // 2, h // 2
    half = side // 2
    return img.crop((cx - half, cy - half, cx + half, cy + half))


def apply_rounded_mask(img: Image.Image, radius_ratio: float = CORNER_RADIUS_RATIO) -> Image.Image:
    """Multiply the icon's alpha by an iOS-style rounded-square mask."""
    w, h = img.size
    radius = int(min(w, h) * radius_ratio)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, w - 1, h - 1), radius=radius, fill=255
    )
    r, g, b, a = img.split()
    return Image.merge("RGBA", (r, g, b, ImageChops.multiply(a, mask)))


def load_source() -> Image.Image:
    if not SOURCE.exists():
        raise FileNotFoundError(
            f"icon source not found: {SOURCE}\n"
            "Place a square (or near-square) PNG at this path before running."
        )
    return crop_to_square_with_inset(Image.open(SOURCE).convert("RGBA"))


def render(cropped: Image.Image, target: int) -> Image.Image:
    return apply_rounded_mask(cropped.resize((target, target), Image.LANCZOS))


def save_pngs(cropped: Image.Image) -> None:
    for size in PNG_SIZES:
        icon = render(cropped, size)
        icon.save(PUBLIC_DIR / f"icon-{size}x{size}.png")
        if size == 512:
            icon.save(PUBLIC_DIR / "icon.png")
            icon.save(ELECTRON_DIR / "icon.png")


def save_ico(cropped: Image.Image) -> None:
    icon = render(cropped, 512)
    icon.save(PUBLIC_DIR / "icon.ico", format="ICO", sizes=ICO_SIZES)


def main() -> None:
    cropped = load_source()
    save_pngs(cropped)
    save_ico(cropped)
    print(
        f"regenerated icons: inset {int(EDGE_INSET_RATIO * 100)}% per side, "
        f"corner radius {int(CORNER_RADIUS_RATIO * 100)}% (cropped source "
        f"{cropped.size[0]}x{cropped.size[1]})"
    )


if __name__ == "__main__":
    main()
