"""Draw the Table of Contents graphic for the Application Note.

ACS asks for a graphic that fits 3.25 x 1.75 inches, so this is drawn at that size and saved
as SVG and a 300 dpi LZW TIFF, matching scripts/build_submission_manuscript.py. Nothing here
is AI-generated: ACS does not allow an AI image in a TOC graphic, and the numbers shown are
read from the same frozen files as Figure 2. The pitted sphere is the software's own motif,
a comet nucleus being the same irregular porous geometry as a catalyst pellet. Run:

    python scripts/draw_note_toc_graphic.py --out-dir docs/paper/figures-note-2026-09-09
    python scripts/draw_note_toc_graphic.py --lang ko
"""

import argparse
import io
import json
import math
import random
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, FancyBboxPatch  # noqa: E402
from PIL import Image  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = ROOT / "docs/paper/submission-2026-09-08/all_families_2026-09-08.json"
MARKET = ROOT / "docs/paper/catalyst_market_2026-09-10.json"
INK, MUTED, RULE = "#1F2A30", "#5B6870", "#C3CBCE"
ACC, ACC_MID, ACC_PALE, WARN = "#1B6F78", "#6FA8AE", "#D9E5E7", "#B8702F"
LB_PER_KG = 2.20462

TEXT = {
    "en": {"font": "Arial",
           "title": "Traceable catalyst manufacturing cost",
           "left": "Composition\nroute, scale",
           "mid": "Itemised cost",
           "mid_unit": "USD/lb",
           "seg": ["Materials", "Processing", "Overhead"],
           "right": "Traded range",
           "right_note": "US imports, HS 3815",
           "foot": "Every price carries its source, date and basis"},
    "ko": {"font": "Malgun Gothic",
           "title": "출처를 추적하는 촉매 제조 원가",
           "left": "조성\n경로, 규모",
           "mid": "항목별 원가",
           "mid_unit": "USD/lb",
           "seg": ["재료비", "가공비", "간접비"],
           "right": "거래 범위",
           "right_note": "미국 수입, HS 3815",
           "foot": "모든 가격에 출처·일자·기준이 붙는다"},
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
    families = json.loads(FAMILIES.read_text(encoding="utf-8"))["families"]
    thermal = [f for f in families if f["catalyst_domain"] == "thermal"]
    best = min((min(f["candidates"], key=lambda c: c["landed_cost_per_lb"]) for f in thermal),
               key=lambda c: abs(c["landed_cost_per_lb"] - 5.0))
    total = best["landed_cost_per_lb"]
    shares = [best["materials_cost_per_lb"] / total, best["processing_cost_per_lb"] / total]
    shares.append(max(0.0, 1 - sum(shares)))
    traded = json.loads(MARKET.read_text(encoding="utf-8"))["series"]["HS381519"]["points"]
    values = sorted(p["price"] / LB_PER_KG for p in traded)
    low, high = values[len(values) // 10], values[-len(values) // 10]

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
        y = by + bh - 0.11 - i * 0.155
        ax.add_patch(Circle((bx + bw + 0.115, y + 0.022), 0.028, fc=colour, ec="none"))
        ax.text(bx + bw + 0.165, y + 0.022, name, ha="left", va="center", fontsize=5.6, color=INK)
    ax.text(bx + bw / 2, by + bh + 0.11, label["mid"], ha="center", va="bottom", fontsize=6.6, fontweight="bold")
    ax.text(bx + bw / 2, by - 0.135, label["mid_unit"], ha="center", va="center", fontsize=5.8, color=MUTED)

    rx, rw, ry = 2.40, 0.76, 0.88
    ax.add_patch(FancyBboxPatch((rx, ry - 0.135), rw, 0.27, boxstyle="round,pad=0,rounding_size=0.135",
                                fc="#F7EFE6", ec=WARN, lw=0.8))
    ax.text(rx + rw / 2, ry + 0.215, label["right"], ha="center", va="bottom", fontsize=6.6, fontweight="bold")
    ax.text(rx, ry - 0.215, f"{low:.0f}", ha="left", va="center", fontsize=6.0, color=WARN)
    ax.text(rx + rw, ry - 0.215, f"{high:.0f}", ha="right", va="center", fontsize=6.0, color=WARN)
    position = rx + rw * min(max((total - low) / (high - low), 0.13), 0.55)
    ax.add_patch(Circle((position, ry), 0.055, fc=ACC, ec="white", lw=0.9, zorder=5))
    ax.text(position + 0.075, ry, f"{total:.2f}", ha="left", va="center", fontsize=6.2, color=ACC,
            fontweight="bold")
    ax.text(rx + rw / 2, ry - 0.365, label["right_note"], ha="center", va="center", fontsize=5.6, color=MUTED)

    for x0, x1 in ((0.75, 0.97), (2.03, 2.35)):
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
    png = io.BytesIO()
    fig.savefig(png, format="png", dpi=300, facecolor="white")
    plt.close(fig)
    image = Image.open(png).convert("RGB")
    image.save(stem + ".png", dpi=(300, 300))
    image.save(stem + ".tif", format="TIFF", dpi=(300, 300), compression="tiff_lzw")
    print("wrote", stem + ".svg/.png/.tif", image.size)


if __name__ == "__main__":
    main()
