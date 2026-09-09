"""Draw the three Application Note figures as vector graphics from repository assets and frozen runs.

Figure 1 is a static workflow schematic with pictograms drawn from primitives (no third-party
icon files). Figure 2 annotates the committed result-screen capture. Figure 3 reads the frozen
joint robustness study and the methods supplement. Run:

    python scripts/draw_application_note_figures.py --out-dir docs/paper/figures-note-2026-09-09
"""

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import (  # noqa: E402
    Arc,
    Circle,
    Ellipse,
    FancyArrowPatch,
    FancyBboxPatch,
    Polygon,
    Rectangle,
)
from PIL import Image  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "docs/paper/robustness-2026-09-08/decision_robustness.json"
METHODS = ROOT / "docs/paper/methods-2026-09-09/methods_study.json"
SCREEN = ROOT / "docs/assets/screen-cost-estimate-result.png"
INK, MUTED, RULE, GREY = "#1F2A30", "#5B6870", "#C3CBCE", "#9AA6AB"
FILL, ACC, ACC_DEEP, WARN = "#F4F6F7", "#1B6F78", "#124C52", "#B8702F"
LW = 0.9
plt.rcParams.update({"font.family": "Arial", "font.size": 7.5, "text.color": INK, "svg.fonttype": "none",
                     "svg.hashsalt": "comet-note-figures-2026-09-09", "axes.edgecolor": INK, "axes.linewidth": 0.6,
                     "xtick.color": INK, "ytick.color": INK})


def line(ax, xs, ys, lw=LW, color=ACC, **kw):
    ax.add_line(Line2D(xs, ys, lw=lw, color=color, solid_capstyle="round", solid_joinstyle="round", **kw))


# ---------------------------------------------------------------- pictograms, each inside a 10 x 8 mm cell
def icon_sources(ax, x, y):
    ax.add_patch(Ellipse((x + 2.6, y + 6.4), 4.2, 1.5, fc="none", ec=ACC, lw=LW))
    line(ax, [x + 0.5, x + 0.5], [y + 6.4, y + 2.2])
    line(ax, [x + 4.7, x + 4.7], [y + 6.4, y + 2.2])
    ax.add_patch(Arc((x + 2.6, y + 2.2), 4.2, 1.5, theta1=180, theta2=360, ec=ACC, lw=LW))
    ax.add_patch(Arc((x + 2.6, y + 4.3), 4.2, 1.5, theta1=180, theta2=360, ec=ACC, lw=LW))
    line(ax, [x + 6.2, x + 6.2, x + 10.2], [y + 7.2, y + 1.6, y + 1.6], color=MUTED, lw=0.7)
    line(ax, [x + 6.8, x + 7.8, x + 8.6, x + 9.8], [y + 3.0, y + 4.6, y + 3.8, y + 6.6])
    for px, py in ((x + 6.8, y + 3.0), (x + 7.8, y + 4.6), (x + 8.6, y + 3.8), (x + 9.8, y + 6.6)):
        ax.add_patch(Circle((px, py), 0.38, fc="white", ec=ACC, lw=LW))


def icon_tiers(ax, x, y):
    ax.add_patch(FancyBboxPatch((x + 0.4, y + 1.0), 5.2, 5.4, boxstyle="round,pad=0,rounding_size=0.5", fc="none", ec=ACC, lw=LW))
    line(ax, [x + 0.4, x + 5.6], [y + 5.0, y + 5.0])
    for i in range(2):
        line(ax, [x + 1.7 + i * 2.6, x + 1.7 + i * 2.6], [y + 5.6, y + 7.0])
    for r in range(2):
        for c in range(3):
            ax.add_patch(Rectangle((x + 1.2 + c * 1.45, y + 1.8 + r * 1.35), 0.75, 0.75,
                                   fc=ACC if (r, c) == (1, 1) else "none", ec=ACC, lw=0.6))
    line(ax, [x + 6.3, x + 7.3, x + 7.9, x + 8.6, x + 9.2, x + 10.3], [y + 3.8, y + 3.8, y + 6.6, y + 1.2, y + 3.8, y + 3.8])


def icon_costing(ax, x, y):
    ax.add_patch(FancyBboxPatch((x + 0.4, y + 1.0), 5.4, 4.2, boxstyle="round,pad=0,rounding_size=0.4", fc="none", ec=ACC, lw=LW))
    line(ax, [x + 4.2, x + 4.2, x + 5.4, x + 5.4], [y + 5.2, y + 7.2, y + 7.2, y + 5.2])
    ax.add_patch(Rectangle((x + 1.3, y + 2.0), 2.2, 1.6, fc="none", ec=ACC, lw=0.7))
    ax.add_patch(Polygon([(x + 2.4, y + 2.2), (x + 3.1, y + 2.9), (x + 2.8, y + 3.35), (x + 2.4, y + 3.0),
                          (x + 2.0, y + 3.35), (x + 1.7, y + 2.9)], closed=True, fc=WARN, ec="none"))
    line(ax, [x + 7.2, x + 7.2, x + 6.3, x + 9.9, x + 9.0, x + 9.0], [y + 7.0, y + 4.6, y + 1.2, y + 1.2, y + 4.6, y + 7.0])
    line(ax, [x + 6.7, x + 9.5], [y + 2.6, y + 2.6], lw=0.7)
    line(ax, [x + 6.6, x + 9.6], [y + 7.0, y + 7.0])


def icon_results(ax, x, y):
    ax.add_patch(Polygon([(x + 1.0, y + 0.8), (x + 1.0, y + 7.4), (x + 6.2, y + 7.4), (x + 7.8, y + 5.8), (x + 7.8, y + 0.8)],
                         closed=True, fc="none", ec=ACC, lw=LW))
    line(ax, [x + 6.2, x + 6.2, x + 7.8], [y + 7.4, y + 5.8, y + 5.8])
    for i, w in enumerate((4.2, 4.2, 2.6)):
        line(ax, [x + 2.0, x + 2.0 + w], [y + 5.4 - i * 1.25, y + 5.4 - i * 1.25], lw=0.7)
    line(ax, [x + 5.6, x + 6.3, x + 7.5], [y + 2.2, y + 1.5, y + 3.2], lw=1.1)
    ax.add_patch(Circle((x + 9.4, y + 2.2), 0.9, fc="none", ec=ACC, lw=0.7))
    ax.add_patch(Circle((x + 9.4, y + 4.4), 0.9, fc=ACC, ec="none"))
    ax.add_patch(Circle((x + 9.4, y + 6.6), 0.9, fc="none", ec=ACC, lw=0.7))


def icon_decision(ax, x, y):
    cx = x + 5.2
    line(ax, [cx, cx], [y + 0.9, y + 7.2])
    line(ax, [cx - 2.4, cx + 2.4], [y + 0.9, y + 0.9])
    line(ax, [cx - 3.9, cx + 3.9], [y + 6.2, y + 6.2])
    for dx, dy in ((-3.9, 0), (3.9, 0.6)):
        px, py = cx + dx, y + 6.2 + dy
        line(ax, [px - 1.6, px, px + 1.6], [py - 2.6, py, py - 2.6], lw=0.7)
        ax.add_patch(Arc((px, py - 2.6), 3.4, 1.6, theta1=180, theta2=360, ec=ACC, lw=LW))
    ax.add_patch(Circle((cx, y + 6.2), 0.45, fc=ACC, ec="none"))


def pill(ax, x, y, text, size=6.4, fill="white", edge=RULE, color=INK, weight="normal", pad=2.2):
    """Rounded keyword chip anchored at its left edge; returns its width in mm."""
    width = len(text) * size * 0.52 / 72 * 25.4 + 2 * pad
    ax.add_patch(FancyBboxPatch((x, y - 2.4), width, 4.8, boxstyle="round,pad=0,rounding_size=2.4",
                                fc=fill, ec=edge, lw=0.5))
    ax.text(x + width / 2, y, text, ha="center", va="center", fontsize=size, color=color, fontweight=weight)
    return width


def pill_row(ax, x, y, items, max_w, gap=1.8, dy=6.2, **kw):
    """Lay chips left to right, wrapping to a new row when the line is full."""
    cx, cy = x, y
    for text in items:
        w = len(text) * kw.get("size", 6.4) * 0.52 / 72 * 25.4 + 2 * kw.get("pad", 2.2)
        if cx + w > x + max_w and cx > x:
            cx, cy = x, cy - dy
        pill(ax, cx, cy, text, **kw)
        cx += w + gap
    return cy


def figure1_workflow():
    w_mm, h_mm = 180, 92
    fig = plt.figure(figsize=(w_mm / 25.4, h_mm / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w_mm)
    ax.set_ylim(0, h_mm)
    ax.axis("off")
    layers = [
        ("Sources", icon_sources,
         ["IMF PCPS", "Johnson Matthey", "UN Comtrade HS", "USGS anchors", "Live feeds", "116 candidates · 30 families"]),
        ("Price tiers", icon_tiers, ["Live quotes", "Frozen monthly reference", "One switch"]),
        ("Costing", icon_costing, ["Step Method", "Recipe w/(f·p·y)", "Electrode per cm²", "Partial LCA"]),
        ("Results", icon_results, ["Ledger with evidence", "Priced / substituted / uncosted", "Monte Carlo", "Comparison"]),
        ("Decision", icon_decision, ["Composite score", "Weight sweep", "Price replay", "Removal control", "Score boxes"]),
    ]
    spine_x, x0, w = 8, 14, 124
    rail_x, rail_w = 143, 33
    top = h_mm - 3
    heights = [16, 14, 15, 15, 16]
    bands = []
    for i, ((title, icon, chips), h) in enumerate(zip(layers, heights, strict=True)):
        y = top - h
        ax.add_patch(FancyBboxPatch((x0, y), w, h, boxstyle="round,pad=0,rounding_size=1.2", fc=FILL, ec=RULE, lw=0.5))
        ax.add_patch(Circle((spine_x, y + h / 2), 3.1, fc=ACC, ec="white", lw=0.8, zorder=4))
        ax.text(spine_x, y + h / 2, f"{i + 1:02d}", ha="center", va="center", fontsize=6.4, color="white",
                fontweight="bold", zorder=5)
        icon(ax, x0 + 3.5, y + h / 2 - 3.8)
        ax.text(x0 + 16.5, y + h / 2, title, ha="left", va="center", fontsize=8.4, fontweight="bold")
        pill_row(ax, x0 + 40, y + h - 5.2, chips, max_w=w - 43)
        bands.append((y, y + h))
        top = y - 2.6
    line(ax, [spine_x, spine_x], [bands[0][1] - 2, bands[-1][0] + 2], color=ACC, lw=0.9)
    for (upper_bottom, _), (_, lower_top) in zip(bands[:-1], bands[1:], strict=True):
        ax.add_patch(FancyArrowPatch((spine_x, upper_bottom - 3.4), (spine_x, lower_top + 3.3), arrowstyle="-|>",
                                     mutation_scale=6, color=ACC, lw=0.9, shrinkA=0, shrinkB=0, zorder=3))
    rail_bottom, rail_top = bands[-1][0], bands[0][1]
    ax.add_patch(FancyBboxPatch((rail_x, rail_bottom), rail_w, rail_top - rail_bottom,
                                boxstyle="round,pad=0,rounding_size=1.2", fc=ACC_DEEP, ec="none"))
    ax.text(rail_x + rail_w / 2, rail_top - 5, "Carried with\nevery number", ha="center", va="center",
            fontsize=7.6, fontweight="bold", color="white")
    tags = ["source · date", "reliability grade", "price tier", "manufacturing scope", "functional unit",
            "LCA coverage", "SHA-256 hashes", "seed"]
    for i, tag in enumerate(tags):
        yy = rail_top - 15 - i * 8.3
        width = len(tag) * 6.4 * 0.52 / 72 * 25.4 + 4.4
        ax.add_patch(FancyBboxPatch((rail_x + (rail_w - width) / 2, yy - 2.4), width, 4.8,
                                    boxstyle="round,pad=0,rounding_size=2.4", fc="white", ec="none", alpha=0.14))
        ax.text(rail_x + rail_w / 2, yy, tag, ha="center", va="center", fontsize=6.4, color="white")
    for bottom, top_ in bands:
        line(ax, [x0 + w, rail_x], [(bottom + top_) / 2, (bottom + top_) / 2], color=RULE, lw=0.5, ls=(0, (2, 2)))
    return fig


def figure2_result_screen():
    img = Image.open(SCREEN).crop((0, 0, 1180, 705))
    fig = plt.figure(figsize=(180 / 25.4, 118 / 25.4))
    ax = fig.add_axes([0.01, 0.08, 0.98, 0.91])
    ax.imshow(img)
    ax.axis("off")
    for n, x, y in [(1, 300, 195), (2, 585, 195), (3, 865, 195), (4, 1145, 195), (5, 970, 42)]:
        ax.add_patch(Circle((x, y), 22, fc=ACC, ec="white", lw=1.5, zorder=5))
        ax.text(x, y, str(n), ha="center", va="center", fontsize=8, fontweight="bold", color="white", zorder=6)
    legend = [("1", "Headline price and basis"), ("2", "Cost build-up"), ("3", "Evidence and coverage"),
              ("4", "Preparation basis"), ("5", "CSV export")]
    lax = fig.add_axes([0.02, 0.01, 0.96, 0.06])
    lax.axis("off")
    for (n, text), xx in zip(legend, (0.01, 0.245, 0.395, 0.615, 0.80), strict=True):
        lax.text(xx, 0.5, n, transform=lax.transAxes, ha="center", va="center", fontsize=6.2, color="white",
                 fontweight="bold", bbox=dict(boxstyle="circle,pad=0.25", fc=ACC, ec="none"))
        lax.text(xx + 0.022, 0.5, text, transform=lax.transAxes, ha="left", va="center", fontsize=7)
    return fig


def figure3_diagnostics():
    study = json.loads(STUDY.read_text(encoding="utf-8"))
    methods = json.loads(METHODS.read_text(encoding="utf-8"))
    fams = sorted(((f["family"], f["joint_grids"]["0.05"]["candidates"][f["reference_winner"]]["first_rank_share_pct"])
                   for f in study["families"]), key=lambda t: t[1])
    fig = plt.figure(figsize=(180 / 25.4, 95 / 25.4))
    ax = fig.add_axes([0.20, 0.10, 0.36, 0.82])
    ys = list(range(len(fams)))
    ax.hlines(ys, 0, [s for _, s in fams], color=RULE, lw=0.8)
    ax.plot([s for _, s in fams], ys, "o", ms=3.2, color=ACC, mec=ACC)
    ax.axvline(50, color=GREY, ls=":", lw=0.8)
    ax.set_yticks(ys)
    ax.set_yticklabels([f for f, _ in fams], fontsize=5.6)
    ax.set_xlim(0, 100)
    ax.set_xlabel("First-rank share of joint scenarios (%)", fontsize=6.8)
    ax.tick_params(axis="x", labelsize=6.5, length=2)
    ax.tick_params(axis="y", length=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.text(0.015, 0.95, "a", fontsize=9, fontweight="bold")
    bx = fig.add_axes([0.66, 0.60, 0.32, 0.32])
    labels = ["Removal changes winner", "Robust to ±2 points", "Robust to ±5 points", "Robust to ±10 points"]
    counts = [study["summary"]["candidate_removal_families_changed"],
              *[study["summary"]["rubric_robust_family_counts"][k] for k in ("2", "5", "10")]]
    bx.barh(range(4), counts, color=[WARN, ACC, ACC, ACC], height=0.62)
    bx.set_yticks(range(4))
    bx.set_yticklabels(labels, fontsize=6.2)
    bx.invert_yaxis()
    bx.set_xlim(0, 30)
    bx.set_xlabel("Families (of 30)", fontsize=6.8)
    bx.tick_params(axis="x", labelsize=6.5, length=2)
    bx.tick_params(axis="y", length=0)
    for i, c in enumerate(counts):
        bx.text(c + 0.5, i, str(c), va="center", fontsize=6.5)
    for s in ("top", "right"):
        bx.spines[s].set_visible(False)
    fig.text(0.585, 0.95, "b", fontsize=9, fontweight="bold")
    cx = fig.add_axes([0.66, 0.10, 0.32, 0.37])
    rows = methods["normalization"]["example"]["rows"]
    names = ["Co/MgO-La$_2$O$_3$", "Ni-MgO/CeO$_2$", "Ni/Al$_2$O$_3$"]
    xs = range(3)
    cx.bar([x - 0.19 for x in xs], [r["total_before"] for r in rows], 0.36, color=ACC, label="Full set")
    cx.bar([x + 0.19 for x in xs], [r["total_after"] for r in rows], 0.36, color=WARN, label="Ru removed")
    for x, r in zip(xs, rows, strict=True):
        cx.text(x - 0.19, r["total_before"] + 1.5, f"{r['total_before']:.1f}", ha="center", fontsize=5.8)
        cx.text(x + 0.19, r["total_after"] + 1.5, f"{r['total_after']:.1f}", ha="center", fontsize=5.8)
    cx.set_xticks(list(xs))
    cx.set_xticklabels([f"{n}\n${r['cost']:.4f}/lb" for n, r in zip(names, rows, strict=True)], fontsize=6)
    cx.set_ylim(0, 128)
    cx.set_ylabel("Composite score", fontsize=6.8)
    cx.tick_params(axis="y", labelsize=6.5, length=2)
    cx.tick_params(axis="x", length=0)
    cx.legend(fontsize=5.6, frameon=False, loc="upper left", handlelength=1.2)
    for s in ("top", "right"):
        cx.spines[s].set_visible(False)
    fig.text(0.585, 0.50, "c", fontsize=9, fontweight="bold")
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "docs/paper/figures-note-2026-09-09")
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for name, fn in (("fig1_workflow_stack", figure1_workflow), ("fig2_result_screen", figure2_result_screen),
                     ("fig3_decision_diagnostics", figure3_diagnostics)):
        fig = fn()
        fig.savefig(args.out_dir / f"{name}.png", dpi=400, facecolor="white", metadata={"Software": "COMET"})
        fig.savefig(args.out_dir / f"{name}.svg", facecolor="white", metadata={"Date": None})
        plt.close(fig)
        print("wrote", args.out_dir / name)


if __name__ == "__main__":
    main()
