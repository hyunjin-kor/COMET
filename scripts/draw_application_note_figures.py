"""Draw Application Note Figures 2 and 3 from repository assets and frozen runs.

Figure 1 is an AI-assisted illustration kept as a committed PNG with its raw file, provenance
note and the connector-line script (scripts/straighten_note_fig1_leaders.py), so it is not
drawn here. Figure 2 annotates the committed Ni/Al2O3 result-screen capture
(scripts/capture_note_result_screen.py). Figure 3 reads the frozen joint robustness study
and the methods supplement. Run:

    python scripts/draw_application_note_figures.py --out-dir docs/paper/figures-note-2026-09-09
"""

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle  # noqa: E402
from PIL import Image  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "docs/paper/robustness-2026-09-08/decision_robustness.json"
METHODS = ROOT / "docs/paper/methods-2026-09-09/methods_study.json"
SCREEN = ROOT / "docs/paper/figures-note-2026-09-09/screen_result_ni_al2o3.png"
CALLOUTS = [(1, 298, 217), (2, 576, 217), (3, 856, 217), (4, 1134, 217), (5, 150, 706), (6, 968, 36)]
INK, MUTED, RULE, GREY = "#1F2A30", "#5B6870", "#C3CBCE", "#9AA6AB"
FILL, ACC, ACC_DEEP, WARN = "#F4F6F7", "#1B6F78", "#124C52", "#B8702F"
LW = 0.9
plt.rcParams.update({"font.family": "Arial", "font.size": 7.5, "text.color": INK, "svg.fonttype": "none",
                     "svg.hashsalt": "comet-note-figures-2026-09-09", "axes.edgecolor": INK, "axes.linewidth": 0.6,
                     "xtick.color": INK, "ytick.color": INK, "mathtext.fontset": "custom", "mathtext.rm": "Arial",
                     "mathtext.it": "Arial:italic", "mathtext.bf": "Arial:bold"})


def figure2_result_screen():
    img = Image.open(SCREEN)
    scale = img.width / 1180  # 1180-px result container captured at device scale 2
    crop_h = int(800 * scale)
    img = img.crop((0, 0, img.width, min(img.height, crop_h)))
    fig = plt.figure(figsize=(178 / 25.4, 130 / 25.4))
    ax = fig.add_axes([0.005, 0.075, 0.99, 0.915])
    ax.imshow(img)
    ax.axis("off")
    for n, x, y in CALLOUTS:
        ax.add_patch(Circle((x * scale, y * scale), 20 * scale, fc=ACC, ec="white", lw=1.2, zorder=5))
        ax.text(x * scale, y * scale, str(n), ha="center", va="center", fontsize=7, fontweight="bold", color="white",
                zorder=6)
    legend = [("1", "Headline price"), ("2", "Cost build-up"), ("3", "Price evidence"), ("4", "Preparation basis"),
              ("5", "Costing scope"), ("6", "CSV export")]
    lax = fig.add_axes([0.02, 0.01, 0.96, 0.05])
    lax.axis("off")
    for (n, text), xx in zip(legend, (0.01, 0.17, 0.32, 0.48, 0.66, 0.82), strict=True):
        lax.text(xx, 0.5, n, transform=lax.transAxes, ha="center", va="center", fontsize=6, color="white",
                 fontweight="bold", bbox=dict(boxstyle="circle,pad=0.25", fc=ACC, ec="none"))
        lax.text(xx + 0.022, 0.5, text, transform=lax.transAxes, ha="left", va="center", fontsize=6.8)
    return fig


FAMILY_NAMES = {
    "aem-electrolyzer-oer": "AEM electrolyzer OER",
    "ammonia-cracking": "Ammonia cracking",
    "ammonia-synthesis": "Ammonia synthesis",
    "co2-electroreduction": "CO$_2$ electroreduction",
    "co2-methanation": "CO$_2$ methanation",
    "co2-methanol": "CO$_2$ to methanol",
    "co2-to-formate": "CO$_2$ to formate",
    "co-prox": "Preferential CO oxidation",
    "dry-reforming": "Methane dry reforming",
    "ethylene-epoxidation": "Ethylene epoxidation",
    "fischer-tropsch-synthesis": "Fischer–Tropsch synthesis",
    "formic-acid-dehydrogenation": "Formic acid dehydrogenation",
    "fuel-cell-orr": "Fuel-cell ORR",
    "glycerol-electrooxidation": "Glycerol electro-oxidation",
    "hydrodeoxygenation": "Bio-oil hydrodeoxygenation",
    "hydrogen-evolution-reaction": "Hydrogen evolution reaction",
    "methane-pyrolysis": "Methane pyrolysis",
    "methanol-to-olefins": "Methanol to olefins",
    "nh3-scr": "NH$_3$-SCR",
    "nitrogen-reduction-reaction": "Electrochemical N$_2$ reduction",
    "olefin-metathesis": "Olefin metathesis",
    "pem-electrolyzer-oer": "PEM electrolyzer OER",
    "photocatalytic-co2-reduction": "Photocatalytic CO$_2$ reduction",
    "photocatalytic-water-splitting": "Photocatalytic water splitting",
    "propane-dehydrogenation": "Propane dehydrogenation",
    "rwgs": "Reverse water-gas shift",
    "selective-acetylene-hydrogenation": "Selective acetylene hydrogenation",
    "steam-methane-reforming": "Steam methane reforming",
    "syngas-methanol": "Syngas to methanol",
    "water-gas-shift": "Water-gas shift",
}


def _clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_linewidth(0.5)
    ax.tick_params(width=0.5)


def figure3_diagnostics():
    study = json.loads(STUDY.read_text(encoding="utf-8"))
    methods = json.loads(METHODS.read_text(encoding="utf-8"))
    fams = sorted(((f["family"], f["joint_grids"]["0.05"]["candidates"][f["reference_winner"]]["first_rank_share_pct"])
                   for f in study["families"]), key=lambda t: t[1])
    fig = plt.figure(figsize=(178 / 25.4, 100 / 25.4))
    ax = fig.add_axes([0.225, 0.095, 0.26, 0.845])
    ys = list(range(len(fams)))
    ax.hlines(ys, 0, [s for _, s in fams], color=RULE, lw=0.7)
    ax.plot([s for _, s in fams], ys, "o", ms=3, color=ACC, mec=ACC)
    ax.axvline(50, color=GREY, ls=(0, (1.5, 1.5)), lw=0.6)
    ax.set_yticks(ys)
    ax.set_yticklabels([FAMILY_NAMES.get(f, f) for f, _ in fams], fontsize=5.8)
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.7, len(fams) - 0.3)
    ax.set_xlabel("Scenarios in which the reference winner keeps first rank (%)", fontsize=6.6)
    ax.tick_params(axis="x", labelsize=6.2, length=2)
    ax.tick_params(axis="y", length=0)
    _clean(ax)
    fig.text(0.01, 0.955, "a", fontsize=8, fontweight="bold")
    bx = fig.add_axes([0.70, 0.625, 0.285, 0.30])
    labels = ["Removal changes winner", "Stable within ±2 points", "Stable within ±5 points", "Stable within ±10 points"]
    counts = [study["summary"]["candidate_removal_families_changed"],
              *[study["summary"]["rubric_robust_family_counts"][k] for k in ("2", "5", "10")]]
    bx.barh(range(4), counts, color=[WARN, ACC, ACC, ACC], height=0.62)
    bx.set_yticks(range(4))
    bx.set_yticklabels(labels, fontsize=6)
    bx.invert_yaxis()
    bx.set_xlim(0, 30)
    bx.set_xlabel("Reaction families (of 30)", fontsize=6.6)
    bx.tick_params(axis="x", labelsize=6.2, length=2)
    bx.tick_params(axis="y", length=0)
    for i, c in enumerate(counts):
        bx.text(c + 0.6, i, str(c), va="center", fontsize=6.2)
    _clean(bx)
    fig.text(0.53, 0.955, "b", fontsize=8, fontweight="bold")
    cx = fig.add_axes([0.70, 0.095, 0.285, 0.40])
    rows = methods["normalization"]["example"]["rows"]
    names = ["Co/MgO–La$_2$O$_3$", "Ni–MgO/CeO$_2$", "Ni/Al$_2$O$_3$"]
    xs = range(3)
    cx.bar([x - 0.19 for x in xs], [r["total_before"] for r in rows], 0.36, color=ACC, label="Full candidate set")
    cx.bar([x + 0.19 for x in xs], [r["total_after"] for r in rows], 0.36, color=WARN, label="Ru candidate removed")
    for x, r in zip(xs, rows, strict=True):
        cx.text(x - 0.19, r["total_before"] + 1.5, f"{r['total_before']:.1f}", ha="center", fontsize=5.6)
        cx.text(x + 0.19, r["total_after"] + 1.5, f"{r['total_after']:.1f}", ha="center", fontsize=5.6)
    cx.set_xticks(list(xs))
    cx.set_xticklabels([f"{n}\n{r['cost']:.4f} USD/lb" for n, r in zip(names, rows, strict=True)], fontsize=5.8)
    cx.set_ylim(0, 128)
    cx.set_ylabel("Composite score", fontsize=6.6)
    cx.tick_params(axis="y", labelsize=6.2, length=2)
    cx.tick_params(axis="x", length=0)
    cx.legend(fontsize=5.6, frameon=False, loc="upper left", handlelength=1.2, borderaxespad=0.2)
    _clean(cx)
    fig.text(0.53, 0.515, "c", fontsize=8, fontweight="bold")
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "docs/paper/figures-note-2026-09-09")
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for name, fn in (("fig2_result_screen", figure2_result_screen), ("fig3_decision_diagnostics", figure3_diagnostics)):
        fig = fn()
        fig.savefig(args.out_dir / f"{name}.png", dpi=400, facecolor="white", metadata={"Software": "COMET"})
        fig.savefig(args.out_dir / f"{name}.svg", facecolor="white", metadata={"Date": None})
        plt.close(fig)
        print("wrote", args.out_dir / name)


if __name__ == "__main__":
    main()
