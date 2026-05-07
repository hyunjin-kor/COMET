"""Resize the master brand asset into the production icon set.

Single source of truth: ``frontend/public/icon-source.png``. Replace
that one file when the brand icon changes; this script downscales it
into every PNG / ICO output the desktop app and the docs reference,
applying an iOS-style rounded-corner alpha mask so the file edges
look clean inside avatar / repo-card UIs.

Outputs:
  frontend/public/icon-32x32.png
  frontend/public/icon-128x128.png
  frontend/public/icon-256x256.png
  frontend/public/icon-512x512.png
  frontend/public/icon.png            (mirror of 512x512)
  frontend/public/icon.ico            (multi-size: 16/24/32/48/64/128/256)
  electron/icon.png                   (mirror of 512x512)

If the source isn't square (typical for an AI-generated render), the
image is center-cropped to the smaller dimension before resizing.
The rounded mask is applied per output size so edge anti-aliasing
stays crisp at every resolution.
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
CORNER_RADIUS_RATIO = 0.22  # iOS app-icon standard squircle approximation
CONTENT_ZOOM = 0.07         # crop this fraction off each side so the dome content
                            # fills more of the visible icon (the rounded mask later
                            # trims any leftover cream halo near the corners)


def to_square(img: Image.Image, zoom: float = CONTENT_ZOOM) -> Image.Image:
    """Center-crop to a square, optionally zooming in by ``zoom`` on each side."""
    w, h = img.size
    side = int(min(w, h) * (1.0 - 2 * zoom))
    cx, cy = w // 2, h // 2
    half = side // 2
    return img.crop((cx - half, cy - half, cx + half, cy + half))


def apply_rounded_mask(img: Image.Image, radius_ratio: float = CORNER_RADIUS_RATIO) -> Image.Image:
    """Multiply the icon's alpha by an iOS-style rounded-square mask.

    Existing transparency in the source is preserved (we multiply alphas
    rather than replace), so any sprite cut-outs inside the brand frame
    keep working.
    """
    w, h = img.size
    radius = int(min(w, h) * radius_ratio)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=255)
    r, g, b, a = img.split()
    return Image.merge("RGBA", (r, g, b, ImageChops.multiply(a, mask)))


def load_source() -> Image.Image:
    if not SOURCE.exists():
        raise FileNotFoundError(
            f"icon source not found: {SOURCE}\n"
            "Place a square (or near-square) PNG at this path before running."
        )
    return to_square(Image.open(SOURCE).convert("RGBA"))


def render(source: Image.Image, size: int) -> Image.Image:
    return apply_rounded_mask(source.resize((size, size), Image.LANCZOS))


def save_pngs(source: Image.Image) -> None:
    for size in PNG_SIZES:
        icon = render(source, size)
        icon.save(PUBLIC_DIR / f"icon-{size}x{size}.png")
        if size == 512:
            icon.save(PUBLIC_DIR / "icon.png")
            icon.save(ELECTRON_DIR / "icon.png")


def save_ico(source: Image.Image) -> None:
    icon = render(source, 512)
    icon.save(PUBLIC_DIR / "icon.ico", format="ICO", sizes=ICO_SIZES)


def main() -> None:
    source = load_source()
    save_pngs(source)
    save_ico(source)
    print(f"regenerated icons with {int(CORNER_RADIUS_RATIO * 100)}% rounded mask "
          f"(source {source.size[0]}×{source.size[1]} after square crop)")


if __name__ == "__main__":
    main()
