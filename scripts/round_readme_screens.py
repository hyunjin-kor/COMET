"""Round the corners of README screenshot PNGs in docs/assets.

The captured screenshots are rectangular while the in-app cards inside them use
20-24 px rounded corners, which looks inconsistent on the GitHub README. This
script post-processes each `screen-*.png` to give the image itself transparent
rounded corners so the outer frame matches the inner UI language.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DIR = REPO_ROOT / "docs" / "assets"
DEFAULT_GLOB = "screen-*.png"
DEFAULT_RADIUS = 24
DEFAULT_BORDER_WIDTH = 1
DEFAULT_BORDER_COLOR = (15, 23, 42, 28)  # slate-900 @ ~11% alpha — readable on light & dark


def round_corners(
    image: Image.Image,
    radius: int,
    border_width: int = 0,
    border_color: tuple[int, int, int, int] = DEFAULT_BORDER_COLOR,
) -> Image.Image:
    rgba = image.convert("RGBA")
    width, height = rgba.size
    radius = max(0, min(radius, width // 2, height // 2))
    if radius == 0 and border_width <= 0:
        return rgba

    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=radius, fill=255)

    alpha = rgba.split()[3]
    alpha = Image.composite(alpha, Image.new("L", (width, height), 0), mask)
    rgba.putalpha(alpha)

    if border_width > 0:
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rounded_rectangle(
            (0, 0, width - 1, height - 1),
            radius=radius,
            outline=border_color,
            width=border_width,
        )
        rgba = Image.alpha_composite(rgba, overlay)

    return rgba


def process_file(path: Path, radius: int, border_width: int) -> None:
    with Image.open(path) as image:
        rounded = round_corners(image, radius, border_width=border_width)
    rounded.save(path, format="PNG", optimize=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dir",
        type=Path,
        default=DEFAULT_DIR,
        help=f"Directory to scan (default: {DEFAULT_DIR.relative_to(REPO_ROOT)})",
    )
    parser.add_argument(
        "--glob",
        default=DEFAULT_GLOB,
        help=f"Filename pattern to match (default: {DEFAULT_GLOB})",
    )
    parser.add_argument(
        "--radius",
        type=int,
        default=DEFAULT_RADIUS,
        help=f"Corner radius in pixels (default: {DEFAULT_RADIUS})",
    )
    parser.add_argument(
        "--border-width",
        type=int,
        default=DEFAULT_BORDER_WIDTH,
        help=f"Outline width in pixels, 0 to disable (default: {DEFAULT_BORDER_WIDTH})",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Optional explicit PNG paths. Overrides --dir/--glob when provided.",
    )
    args = parser.parse_args()

    if args.paths:
        targets = [p for p in args.paths if p.suffix.lower() == ".png"]
    else:
        targets = sorted(args.dir.glob(args.glob))

    if not targets:
        print("No PNG targets found.", file=sys.stderr)
        return 1

    for target in targets:
        process_file(target, args.radius, args.border_width)
        print(
            f"rounded {target.relative_to(REPO_ROOT)} "
            f"(r={args.radius}px, border={args.border_width}px)"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
