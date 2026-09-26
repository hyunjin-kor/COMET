"""Draw the Table of Contents graphic for the Application Note.

ACS asks for a graphic that fits 3.25 x 1.75 inches, so this is drawn at that size and saved
as SVG and a 300 dpi LZW TIFF. Shapes are drawn in code without generative image-model
outputs, and every plotted quantity comes from the frozen records of the article: the itemized
selling price and the production-scale curve of the Ni/Al2O3 base case (what-if study) and the monthly
costs of the two ammonia-cracking candidates that attain the lowest cost (price-crossover study). Run:

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
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle, Wedge  # noqa: E402
from PIL import Image  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
WHATIF = ROOT / "docs/paper/whatif-2026-09-21/whatif_study.json"
CROSSOVERS = ROOT / "docs/paper/price-crossovers-2026-09-21/price_crossovers.json"
INK, MUTED, RULE = "#1F2A30", "#5B6870", "#C3CBCE"
ACC, ACC_MID, GREY, TILE, WARN = "#1B6F78", "#6FA8AE", "#9AA6AB", "#E4EEEF", "#B8702F"
KG_PER_SHORT_TON = 907.18474
PER_LB_TO_PER_KG = 1 / 0.45359237

NAME = "Catalyst Overall Manufacturing Estimation Tool"

TEXT = {
    "en": {"font": "Arial",
           "inputs_head": "Inputs", "inputs": ["Composition", "Preparation\nmethod", "Production\nscale", "Material\nprices"],
           "price": "Estimated price", "items": ["Materials", "Processing", "G&A, SARD", "Margin"],
           "drivers_head": "What moves the price", "scale": "Production scale", "metals": "Metal prices",
           "reaction": "NH$_3$ cracking", "co": "Co", "ni": "Ni"},
    "ko": {"font": "Malgun Gothic",
           "inputs_head": "입력", "inputs": ["조성", "제조법", "생산 규모", "원료 가격"],
           "price": "추정 판매 단가", "items": ["재료비", "가공비", "G&A, SARD", "마진"],
           "drivers_head": "단가를 움직이는 요인", "scale": "생산 규모", "metals": "금속 가격",
           "reaction": "NH$_3$ 분해", "co": "Co", "ni": "Ni"},
}


def _icon(ax, kind, x, y, size):
    """One input pictogram inside a pale tile whose lower-left corner is (x, y)."""
    ax.add_patch(FancyBboxPatch((x, y), size, size, boxstyle="round,pad=0,rounding_size=0.03", fc=TILE, ec="none"))
    cx, cy, u = x + size / 2, y + size / 2, size / 10
    if kind == "composition":  # a loading on a support
        ax.add_patch(Wedge((cx, cy), 3.3 * u, 90 - 72, 90, width=1.5 * u, fc=WARN, ec="none"))
        ax.add_patch(Wedge((cx, cy), 3.3 * u, 90, 360 + 90 - 72, width=1.5 * u, fc=ACC, ec="none"))
    elif kind == "procedure":  # a sequence of processing steps
        for index in range(3):
            ax.add_patch(Rectangle((x + (1.3 + index * 2.9) * u, cy - 0.9 * u), 1.8 * u, 1.8 * u, fc=ACC, ec="none"))
        for index in range(2):
            ax.plot([x + (3.2 + index * 2.9) * u, x + (4.1 + index * 2.9) * u], [cy, cy], color=ACC, lw=0.7, solid_capstyle="butt")
    elif kind == "order":  # stacked drums of product
        for dx, dy in ((-1.7, -2.6), (1.7, -2.6), (0, 0.5)):
            ax.add_patch(FancyBboxPatch((cx + (dx - 1.4) * u, cy + dy * u), 2.8 * u, 2.6 * u,
                                        boxstyle="round,pad=0,rounding_size=0.008", fc=ACC_MID if dy < 0 else ACC, ec="none"))
    else:  # a calendar sheet carrying a price line
        ax.add_patch(FancyBboxPatch((x + 2.2 * u, y + 2.2 * u), 5.6 * u, 5.6 * u, boxstyle="round,pad=0,rounding_size=0.012",
                                    fc="white", ec=ACC, lw=0.7))
        ax.add_patch(Rectangle((x + 2.2 * u, y + 6.4 * u), 5.6 * u, 1.4 * u, fc=ACC, ec="none"))
        ax.plot([x + 3.0 * u, x + 4.3 * u, x + 5.4 * u, x + 7.0 * u], [y + 3.3 * u, y + 4.8 * u, y + 3.9 * u, y + 5.5 * u],
                color=WARN, lw=0.8, solid_capstyle="round", solid_joinstyle="round")


def _mini_axes(fig, box):
    axes = fig.add_axes([box[0] / 3.25, box[1] / 1.75, box[2] / 3.25, box[3] / 1.75])
    axes.set_xticks([])
    axes.set_yticks([])
    axes.minorticks_off()
    for side in ("top", "right"):
        axes.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        axes.spines[side].set_linewidth(0.6)
        axes.spines[side].set_color(MUTED)
    return axes


def graphic(lang):
    label = TEXT[lang]
    whatif = json.loads(WHATIF.read_text(encoding="utf-8"))
    crossovers = json.loads(CROSSOVERS.read_text(encoding="utf-8"))
    plt.rcParams.update({"font.family": label["font"], "text.color": INK, "svg.fonttype": "none",
                         "svg.hashsalt": "comet-note-toc-2026-09-21", "axes.unicode_minus": False})
    fig = plt.figure(figsize=(3.25, 1.75), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, 3.25), ylim=(0, 1.75))
    ax.axis("off")
    renderer = fig.canvas.get_renderer()
    cursor = 0.07
    pieces = [("COMET:", 9.0, "bold", INK)]
    for word in NAME.split():
        pieces += [(" ", 6.9, "normal", INK), (word[0], 6.9, "bold", INK), (word[1:], 6.9, "normal", MUTED)]
    for string, size, weight, colour in pieces:
        if string == " ":
            cursor += 0.035
            continue
        piece = ax.text(cursor, 1.585, string, ha="left", va="baseline", fontsize=size, fontweight=weight, color=colour)
        cursor = piece.get_window_extent(renderer).transformed(ax.transData.inverted()).x1
    if cursor > 3.18:
        raise ValueError("The software name does not fit the width of the graphic")

    # inputs
    ax.text(0.07, 1.41, label["inputs_head"], ha="left", va="center", fontsize=6.4, fontweight="bold")
    for index, (kind, name) in enumerate(zip(("composition", "procedure", "order", "prices"), label["inputs"], strict=True)):
        y = 1.07 - index * 0.275
        _icon(ax, kind, 0.07, y, 0.21)
        ax.text(0.33, y + 0.105, name, ha="left", va="center", fontsize=6.2, linespacing=1.05)

    # itemized selling price of the Ni/Al2O3 base case
    base = whatif["catalysts"]["ni"]["baseline"]
    parts = [base["materials_per_lb"], base["processing_per_lb"], base["ga_per_lb"] + base["sard_per_lb"], base["margin_per_lb"]]
    if abs(sum(parts) - base["selling_price_per_lb"]) > 5e-4:
        raise ValueError("The items of the selling price do not add up")
    x0, width, y0, height = 1.07, 0.23, 0.25, 1.03
    bottom = y0
    for share, colour, name in zip([p / sum(parts) for p in parts], (ACC, ACC_MID, GREY, WARN), label["items"], strict=True):
        ax.add_patch(Rectangle((x0, bottom), width, share * height, fc=colour, ec="white", lw=0.5))
        ax.text(x0 + width + 0.04, bottom + share * height / 2, name, ha="left", va="center", fontsize=6.0)
        bottom += share * height
    ax.text(x0, 1.41, label["price"], ha="left", va="center", fontsize=6.4, fontweight="bold")
    ax.text(x0 + width / 2, 0.165, "USD/kg", ha="center", va="center", fontsize=6.0, color=MUTED)
    for start in (0.885, 1.83):
        y, shaft, head, neck, tip = 0.78, 0.028, 0.075, start + 0.075, start + 0.15
        ax.add_patch(Polygon([(start, y - shaft), (neck, y - shaft), (neck, y - head), (tip, y), (neck, y + head), (neck, y + shaft),
                              (start, y + shaft)], closed=True, fc=ACC_MID, ec="none"))

    # selling price of the base case against production scale, with both ends written out
    left, right = 2.04, 3.18
    rows = whatif["order_size"]["ni"]
    tonnes = [row["order_size_tons"] * KG_PER_SHORT_TON / 1000 for row in rows]
    prices = [row["selling_price_per_lb"] * PER_LB_TO_PER_KG for row in rows]
    ax.text(left, 1.41, label["drivers_head"], ha="left", va="center", fontsize=6.4, fontweight="bold")
    ax.text(left, 1.265, label["scale"], ha="left", va="center", fontsize=6.2)
    curve = _mini_axes(fig, (left + 0.03, 0.915, right - left - 0.03, 0.27))
    curve.plot(tonnes, prices, color=WARN, lw=1.2)
    curve.plot([tonnes[0], tonnes[-1]], [prices[0], prices[-1]], ls="none", marker="o", ms=2.6, color=WARN)
    curve.set_xscale("log")
    curve.set_yscale("log")
    curve.set_xlim(tonnes[0] * 0.75, tonnes[-1] * 1.3)
    curve.set_ylim(prices[-1] * 0.65, prices[0] * 5)
    curve.minorticks_off()
    curve.set_xticks([])
    curve.set_yticks([])
    curve.annotate(f"{prices[0]:.0f} USD/kg", (tonnes[0], prices[0]), xytext=(5, 1.5), textcoords="offset points", ha="left", va="bottom",
                   fontsize=6.0, color=WARN)
    curve.annotate(f"{prices[-1]:.0f} USD/kg", (tonnes[-1], prices[-1]), xytext=(0, 4), textcoords="offset points", ha="right", va="bottom",
                   fontsize=6.0, color=WARN)
    ax.text(right, 1.265, "Ni/Al$_2$O$_3$", ha="right", va="center", fontsize=6.0, color=MUTED)
    ax.text(left + 0.03, 0.85, f"{tonnes[0]:.1f} t", ha="left", va="center", fontsize=6.0, color=MUTED)
    ax.text(right, 0.85, f"{tonnes[-1]:,.0f} t", ha="right", va="center", fontsize=6.0, color=MUTED)

    # monthly costs of the two ammonia-cracking candidates; the gap between them takes the color of the cheaper one
    family = next(row for row in crossovers["families"] if row["family"] == "ammonia-cracking")
    records = family["periods"]["monthly"]["records"]
    if {row["cost_winner"] for row in records} != {"co-mgo-la2o3", "ni-alumina-baseline"}:
        raise ValueError("The graphic names a cobalt and a nickel catalyst")
    ax.text(left, 0.71, label["metals"], ha="left", va="center", fontsize=6.2)
    ax.text(right, 0.71, label["reaction"], ha="right", va="center", fontsize=6.0, color=MUTED)
    plot_left, plot_right = left + 0.03, right - 0.16
    lines = _mini_axes(fig, (plot_left, 0.19, plot_right - plot_left, 0.44))
    months = list(range(len(records)))
    cobalt = [row["costs"]["co-mgo-la2o3"] for row in records]
    nickel = [row["costs"]["ni-alumina-baseline"] for row in records]
    lines.fill_between(months, cobalt, nickel, where=[c <= n for c, n in zip(cobalt, nickel, strict=True)], interpolate=True,
                       color=ACC, alpha=0.25, linewidth=0)
    lines.fill_between(months, cobalt, nickel, where=[c >= n for c, n in zip(cobalt, nickel, strict=True)], interpolate=True,
                       color=WARN, alpha=0.25, linewidth=0)
    lines.plot(months, cobalt, color=ACC, lw=1.0)
    lines.plot(months, nickel, color=WARN, lw=1.0)
    lines.set_xlim(0, len(records) - 1)
    lines.margins(y=0.08)
    for values, name, colour, align in ((cobalt, label["co"], ACC, "bottom"), (nickel, label["ni"], WARN, "top")):
        lines.annotate(name, (months[-1], values[-1]), xytext=(2.5, 1 if align == "bottom" else -1), textcoords="offset points",
                       ha="left", va=align, fontsize=6.0, color=colour, annotation_clip=False)
    first, last = (records[i]["date"][:4] for i in (0, -1))
    ax.text(plot_left, 0.125, first, ha="left", va="center", fontsize=6.0, color=MUTED)
    ax.text(plot_right, 0.125, last, ha="right", va="center", fontsize=6.0, color=MUTED)
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
