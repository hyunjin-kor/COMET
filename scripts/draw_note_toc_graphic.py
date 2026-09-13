"""Draw the Table of Contents graphic for the Application Note.

ACS asks for a graphic that fits 3.25 x 1.75 inches, so this is drawn at that size and saved
as SVG and a 300 dpi LZW TIFF. Shapes are drawn in code without generative image-model
outputs. The equal cost bands illustrate categories, not numerical results; the TOC
summarizes inputs, cost estimation, and ranking without a market-price comparison. Run:

    python scripts/draw_note_toc_graphic.py --out-dir docs/paper/figures-note-2026-09-09
    python scripts/draw_note_toc_graphic.py --lang ko
"""

import argparse
import io
import math
import random
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, FancyBboxPatch  # noqa: E402
from PIL import Image  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
INK, MUTED, RULE = "#1F2A30", "#5B6870", "#C3CBCE"
ACC, ACC_MID, ACC_PALE, WARN = "#1B6F78", "#6FA8AE", "#D9E5E7", "#B8702F"

TEXT = {
    "en": {"font": "Arial",
           "title": "COMET",
           "left": "Composition\nPrices, route",
           "mid": "Cost",
           "mid_unit": "USD/kg",
           "seg": ["Materials", "Processing", "Overheads\n+ margin"],
           "right": "Ranking",
           "criteria": ["Cost", "Data quality", "Route", "Performance"],
           "foot": "Sources · Assumptions · Reproducibility"},
    "ko": {"font": "Malgun Gothic",
           "title": "COMET",
           "left": "조성\n가격, 경로",
           "mid": "원가",
           "mid_unit": "USD/kg",
           "seg": ["재료비", "가공비", "간접비·마진"],
           "right": "순위 산정",
           "criteria": ["원가", "자료 신뢰도", "제조 경로", "성능"],
           "foot": "출처 · 가정 · 재현 정보"},
}


def _pellet(ax, cx, cy, r, seed=20260910):
    """A pitted porous sphere: the comet nucleus that gives the software its name.

    Pit centres are drawn from a fixed seed so the figure is reproducible, rejected when they
    would cross the rim, and sized from a small set so the surface reads as porous rather than
    speckled.
    """
    rng = random.Random(seed)
    ax.add_patch(Circle((cx, cy), r, fc=ACC_PALE, ec=ACC, lw=1.0, zorder=2))
    placed = []
    while len(placed) < 26:
        angle = rng.uniform(0, 2 * math.pi)
        radius = r * math.sqrt(rng.uniform(0, 1)) * 0.84
        size = rng.choice((0.055, 0.075, 0.075, 0.10, 0.10, 0.135, 0.17)) * r
        x, y = cx + radius * math.cos(angle), cy + radius * math.sin(angle)
        if math.hypot(x - cx, y - cy) + size > r * 0.93:
            continue
        if any(math.hypot(x - px, y - py) < (size + ps) * 1.25 for px, py, ps in placed):
            continue
        placed.append((x, y, size))
    for x, y, size in placed:
        shade = ACC if size > 0.09 * r else ACC_MID
        ax.add_patch(Ellipse((x, y), 2 * size, 1.75 * size, fc=shade, ec="none",
                             alpha=0.9 if shade == ACC_MID else 0.8, zorder=3))


def graphic(lang):
    label = TEXT[lang]
    plt.rcParams.update({"font.family": label["font"], "text.color": INK, "svg.fonttype": "none",
                         "svg.hashsalt": "comet-note-toc-2026-09-10", "axes.unicode_minus": False})
    shares = [1 / 3] * 3

    fig, ax = plt.subplots(figsize=(3.25, 1.75), dpi=300)
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set(xlim=(0, 3.25), ylim=(0, 1.75))
    ax.axis("off")
    ax.text(1.625, 1.575, label["title"], ha="center", va="center", fontsize=9.0, fontweight="bold")

    _pellet(ax, 0.42, 0.88, 0.275)
    ax.text(0.42, 0.42, label["left"], ha="center", va="top", fontsize=6.0, color=MUTED, linespacing=1.55)

    bx, bw, by, bh = 1.13, 0.33, 0.47, 0.78
    ax.add_patch(FancyBboxPatch((bx - 0.13, by - 0.05), bw + 0.26, bh + 0.10,
                                boxstyle="round,pad=0,rounding_size=0.05", fc="white", ec=RULE, lw=0.6))
    bottom = by
    for share, colour in zip(shares, (ACC, ACC_MID, "#DCE2E4"), strict=True):
        ax.add_patch(FancyBboxPatch((bx, bottom), bw, share * bh, boxstyle="round,pad=0,rounding_size=0.008",
                                    fc=colour, ec="none"))
        bottom += share * bh
    legend = list(zip(label["seg"], (ACC, ACC_MID, "#B9C2C6"), strict=True))[::-1]
    for i, (name, colour) in enumerate(legend):
        y = by + bh - (i + 0.5) * bh / 3
        ax.add_patch(Circle((bx + bw + 0.115, y + 0.022), 0.028, fc=colour, ec="none"))
        ax.text(bx + bw + 0.165, y + 0.022, name, ha="left", va="center", fontsize=6.0, color=INK)
    ax.text(bx + bw / 2, by + bh + 0.11, label["mid"], ha="center", va="bottom", fontsize=6.6, fontweight="bold")
    ax.text(bx + bw / 2, by - 0.135, label["mid_unit"], ha="center", va="center", fontsize=6.0, color=MUTED)

    rx, rw = 2.40, 0.76
    ax.add_patch(FancyBboxPatch((rx, 0.49), rw, 0.72, boxstyle="round,pad=0,rounding_size=0.05",
                                fc="#F7EFE6", ec=WARN, lw=0.8))
    ax.text(rx + rw / 2, by + bh + 0.11, label["right"], ha="center", va="bottom", fontsize=6.6, fontweight="bold")
    for i, criterion in enumerate(label["criteria"]):
        ax.text(rx + rw / 2, 1.08 - i * 0.15, criterion, ha="center", va="center", fontsize=6.0)

    for x0, x1 in ((0.75, 0.97), (2.16, 2.35)):
        ax.add_patch(FancyArrowPatch((x0, 0.88), (x1, 0.88), arrowstyle="-|>", mutation_scale=7,
                                     color=MUTED, lw=0.9, shrinkA=0, shrinkB=0))
    ax.text(1.625, 0.135, label["foot"], ha="center", va="center", fontsize=6.0, color=MUTED)
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "docs/paper/figures-note-2026-09-09")
    parser.add_argument("--lang", choices=sorted(TEXT), default="en")
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    suffix = "" if args.lang == "en" else f".{args.lang}"
    fig = graphic(args.lang)
    stem = str(args.out_dir / f"toc_graphic{suffix}")
    fig.savefig(stem + ".svg", format="svg", metadata={"Date": None}, facecolor="white")
    svg_path = Path(stem + ".svg")
    svg_path.write_text("\n".join(line.rstrip() for line in svg_path.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    png = io.BytesIO()
    fig.savefig(png, format="png", dpi=300, facecolor="white")
    plt.close(fig)
    image = Image.open(png).convert("RGB")
    image.save(stem + ".png", dpi=(300, 300))
    image.save(stem + ".tif", format="TIFF", dpi=(300, 300), compression="tiff_lzw")
    print("wrote", stem + ".svg/.png/.tif", image.size)


if __name__ == "__main__":
    main()
