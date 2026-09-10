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


def _pellet(ax, cx, cy, r):
    """A pitted porous sphere: the comet nucleus that gives the software its name."""
    ax.add_patch(Circle((cx, cy), r, fc=ACC_PALE, ec=ACC, lw=0.9, zorder=2))
    pits = [(-0.42, 0.34, 0.17), (0.30, 0.44, 0.12), (-0.10, 0.02, 0.21), (0.46, -0.10, 0.15),
            (-0.48, -0.30, 0.13), (0.10, -0.48, 0.16), (-0.16, 0.62, 0.09), (0.60, 0.20, 0.09)]
    for dx, dy, pr in pits:
        ax.add_patch(Ellipse((cx + dx * r, cy + dy * r), 2 * pr * r, 1.6 * pr * r,
                             fc=ACC_MID, ec="none", alpha=0.75, zorder=3))


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
    ax.text(1.625, 1.585, label["title"], ha="center", va="center", fontsize=8.4, fontweight="bold")

    _pellet(ax, 0.40, 0.86, 0.245)
    ax.text(0.40, 0.41, label["left"], ha="center", va="top", fontsize=5.8, color=MUTED, linespacing=1.5)

    bx, bw, by, bh = 1.10, 0.30, 0.44, 0.80
    ax.add_patch(FancyBboxPatch((bx - 0.13, by - 0.05), bw + 0.26, bh + 0.10,
                                boxstyle="round,pad=0,rounding_size=0.05", fc="white", ec=RULE, lw=0.6))
    bottom = by
    for share, colour in zip(shares, (ACC, ACC_MID, "#DCE2E4"), strict=True):
        ax.add_patch(FancyBboxPatch((bx, bottom), bw, share * bh, boxstyle="round,pad=0,rounding_size=0.008",
                                    fc=colour, ec="none"))
        bottom += share * bh
    for i, (name, colour) in enumerate(zip(label["seg"], (ACC, ACC_MID, "#B9C2C6"), strict=True)):
        y = by + bh - 0.11 - i * 0.155
        ax.add_patch(Circle((bx + bw + 0.115, y + 0.022), 0.028, fc=colour, ec="none"))
        ax.text(bx + bw + 0.165, y + 0.022, name, ha="left", va="center", fontsize=5.4, color=INK)
    ax.text(bx + bw / 2, by + bh + 0.10, label["mid"], ha="center", va="bottom", fontsize=6.2, fontweight="bold")
    ax.text(bx - 0.055, by - 0.115, label["mid_unit"], ha="left", va="center", fontsize=5.4, color=MUTED)

    rx, rw, ry = 2.42, 0.72, 0.86
    ax.add_patch(FancyBboxPatch((rx, ry - 0.115), rw, 0.23, boxstyle="round,pad=0,rounding_size=0.03",
                                fc="#F4EAE0", ec=WARN, lw=0.7))
    ax.text(rx + rw / 2, ry + 0.20, label["right"], ha="center", va="bottom", fontsize=6.2, fontweight="bold")
    ax.text(rx, ry - 0.175, f"{low:.0f}", ha="left", va="top", fontsize=5.4, color=WARN)
    ax.text(rx + rw, ry - 0.175, f"{high:.0f}", ha="right", va="top", fontsize=5.4, color=WARN)
    position = rx + rw * min(max((total - low) / (high - low), 0.08), 0.92)
    ax.add_patch(Circle((position, ry), 0.055, fc=ACC, ec="white", lw=0.9, zorder=5))
    ax.text(position, ry + 0.155, f"{total:.2f}", ha="center", va="bottom", fontsize=5.6, color=ACC,
            fontweight="bold")
    ax.text(rx + rw / 2, ry - 0.325, label["right_note"], ha="center", va="center", fontsize=5.2, color=MUTED)

    for x0, x1 in ((0.70, 0.94), (1.98, 2.37)):
        ax.add_patch(FancyArrowPatch((x0, 0.86), (x1, 0.86), arrowstyle="-|>", mutation_scale=6,
                                     color=INK, lw=0.8, shrinkA=0, shrinkB=0))
    ax.text(1.625, 0.14, label["foot"], ha="center", va="center", fontsize=5.8, color=MUTED)
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
