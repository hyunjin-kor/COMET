"""Draw the Table of Contents graphic for the Application Note.

ACS asks for a graphic that fits 3.25 x 1.75 inches, so this is drawn at that size and saved
as SVG and a 300 dpi LZW TIFF. Shapes are drawn in code without generative image-model
outputs, and every plotted quantity comes from the frozen records of the article: the itemized
selling price and the order-size curve of the Ni/Al2O3 base case (what-if study) and the
lowest-cost ammonia-cracking candidate of each month (price-crossover study). Run:

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
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle  # noqa: E402
from PIL import Image  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
WHATIF = ROOT / "docs/paper/whatif-2026-09-21/whatif_study.json"
CROSSOVERS = ROOT / "docs/paper/price-crossovers-2026-09-21/price_crossovers.json"
INK, MUTED, RULE = "#1F2A30", "#5B6870", "#C3CBCE"
ACC, ACC_MID, GREY, PALE, WARN = "#1B6F78", "#6FA8AE", "#9AA6AB", "#D9DEE1", "#B8702F"
KG_PER_SHORT_TON = 907.18474

TEXT = {
    "en": {"font": "Arial", "title": "COMET", "subtitle": "catalyst manufacturing cost",
           "inputs": ["Composition", "Procedure", "Order size", "Dated prices"],
           "price": "Estimated price", "items": ["Materials", "Processing", "G&A, SARD", "Margin"],
           "order": "Order size", "fold": "{fold:.1f}× lower", "months": "Cheapest catalyst\nfor NH$_3$ cracking",
           "co": "Co catalyst", "ni": "Ni catalyst"},
    "ko": {"font": "Malgun Gothic", "title": "COMET", "subtitle": "촉매 제조 원가 추정",
           "inputs": ["조성", "제조 절차", "주문량", "날짜별 가격"],
           "price": "추정 판매 단가", "items": ["재료비", "가공비", "G&A, SARD", "마진"],
           "order": "주문량", "fold": "{fold:.1f}배 낮아짐", "months": "NH$_3$ 분해 최저 원가",
           "co": "Co 촉매", "ni": "Ni 촉매"},
}


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
    ax.text(0.09, 1.585, label["title"], ha="left", va="center", fontsize=9.0, fontweight="bold")
    ax.text(0.63, 1.578, label["subtitle"], ha="left", va="center", fontsize=6.2, color=MUTED)

    # inputs
    ax.add_patch(FancyBboxPatch((0.09, 0.30), 0.86, 1.06, boxstyle="round,pad=0,rounding_size=0.05", fc="white", ec=RULE, lw=0.6))
    for index, name in enumerate(label["inputs"]):
        y = 1.215 - index * 0.255
        ax.add_patch(Rectangle((0.16, y - 0.03), 0.06, 0.06, fc=ACC if index < 3 else WARN, ec="none"))
        ax.text(0.27, y, name, ha="left", va="center", fontsize=6.2)

    # itemized selling price of the Ni/Al2O3 base case
    base = whatif["catalysts"]["ni"]["baseline"]
    parts = [base["materials_per_lb"], base["processing_per_lb"], base["ga_per_lb"] + base["sard_per_lb"], base["margin_per_lb"]]
    if abs(sum(parts) - base["selling_price_per_lb"]) > 5e-4:
        raise ValueError("The items of the selling price do not add up")
    x0, width, y0, height = 1.20, 0.25, 0.30, 1.00
    bottom = y0
    for share, colour, name in zip([p / sum(parts) for p in parts], (ACC, ACC_MID, GREY, WARN), label["items"], strict=True):
        ax.add_patch(Rectangle((x0, bottom), width, share * height, fc=colour, ec="white", lw=0.5))
        ax.text(x0 + width + 0.045, bottom + share * height / 2, name, ha="left", va="center", fontsize=6.0)
        bottom += share * height
    ax.text(x0 + 0.37, 1.41, label["price"], ha="center", va="center", fontsize=6.4, fontweight="bold")
    ax.text(x0 + width / 2, 0.215, "USD/kg", ha="center", va="center", fontsize=6.0, color=MUTED)
    for start, stop in ((0.985, 1.14), (2.085, 2.24)):
        ax.add_patch(FancyArrowPatch((start, 0.83), (stop, 0.83), arrowstyle="-|>", mutation_scale=7, color=MUTED, lw=0.9,
                                     shrinkA=0, shrinkB=0))

    # selling price of the base case against order size
    rows = whatif["order_size"]["ni"]
    curve = fig.add_axes([2.40 / 3.25, 0.93 / 1.75, 0.76 / 3.25, 0.44 / 1.75])
    curve.plot([row["order_size_tons"] * KG_PER_SHORT_TON / 1000 for row in rows], [row["selling_price_per_lb"] for row in rows],
               color=WARN, lw=1.2, marker="o", ms=1.8)
    curve.set_xscale("log")
    curve.set_yscale("log")
    curve.set_xticks([])
    curve.set_yticks([])
    curve.minorticks_off()
    for side in ("top", "right"):
        curve.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        curve.spines[side].set_linewidth(0.6)
        curve.spines[side].set_color(MUTED)
    curve.set_xlabel(label["order"], fontsize=6.0, labelpad=1.5, color=INK)
    curve.set_ylabel("USD/kg", fontsize=6.0, labelpad=1.5, color=INK)
    fold = rows[0]["selling_price_per_lb"] / rows[-1]["selling_price_per_lb"]
    curve.text(0.97, 0.86, "Ni/Al$_2$O$_3$", transform=curve.transAxes, ha="right", va="center", fontsize=6.0, color=INK)
    curve.text(0.97, 0.56, label["fold"].format(fold=fold), transform=curve.transAxes, ha="right", va="center", fontsize=6.0, color=WARN)

    # lowest-cost ammonia-cracking candidate of each month
    family = next(row for row in crossovers["families"] if row["family"] == "ammonia-cracking")
    winners = [row["cost_winner"] for row in family["periods"]["monthly"]["records"]]
    if set(winners) != {"co-mgo-la2o3", "ni-alumina-baseline"}:
        raise ValueError("The strip names a cobalt and a nickel catalyst")
    left, right, y, tall = 2.30, 3.16, 0.34, 0.13
    step = (right - left) / len(winners)
    start = 0
    for stop in range(1, len(winners) + 1):
        if stop == len(winners) or winners[stop] != winners[start]:
            ax.add_patch(Rectangle((left + start * step, y), (stop - start) * step, tall, ec="none",
                                   fc=ACC if winners[start] == "co-mgo-la2o3" else WARN))
            start = stop
    ax.text(left, 0.50, label["months"], ha="left", va="bottom", fontsize=6.0, linespacing=1.15)
    first, last = (family["periods"]["monthly"]["records"][i]["date"][:4] for i in (0, -1))
    ax.text(left, 0.265, first, ha="left", va="center", fontsize=6.0, color=MUTED)
    ax.text(right, 0.265, last, ha="right", va="center", fontsize=6.0, color=MUTED)
    ax.text(left, 0.135, label["co"], ha="left", va="center", fontsize=6.0, color=ACC)
    ax.text(right, 0.135, label["ni"], ha="right", va="center", fontsize=6.0, color=WARN)
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
