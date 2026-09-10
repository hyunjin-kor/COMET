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
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch  # noqa: E402
from PIL import Image  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "docs/paper/robustness-2026-09-08/decision_robustness.json"
METHODS = ROOT / "docs/paper/methods-2026-09-09/methods_study.json"
SCREEN = ROOT / "docs/paper/figures-note-2026-09-09/screen_result_ni_al2o3.png"
CALLOUTS = [(1, 298, 217), (2, 576, 217), (3, 856, 217), (4, 1134, 217), (5, 150, 706)]
INK, MUTED, RULE, GREY = "#1F2A30", "#5B6870", "#C3CBCE", "#9AA6AB"
FILL, ACC, ACC_DEEP, WARN = "#F4F6F7", "#1B6F78", "#124C52", "#B8702F"
LW = 0.9
plt.rcParams.update({"font.family": "Arial", "font.size": 7.5, "text.color": INK, "svg.fonttype": "none",
                     "svg.hashsalt": "comet-note-figures-2026-09-09", "axes.edgecolor": INK, "axes.linewidth": 0.6,
                     "xtick.color": INK, "ytick.color": INK, "mathtext.fontset": "custom", "mathtext.rm": "Arial",
                     "mathtext.it": "Arial:italic", "mathtext.bf": "Arial:bold"})


def _card(ax, x, y, w, h, label, value, details):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.8", fc=FILL, ec=RULE, lw=0.5))
    ax.text(x + 2.2, y + h - 3.0, label, ha="left", va="center", fontsize=5.8, color=MUTED)
    ax.text(x + 2.2, y + h - 7.4, value, ha="left", va="center", fontsize=6.8, fontweight="bold", color=INK)
    for i, line_text in enumerate(details):
        ax.text(x + 2.2, y + h - 11.0 - i * 3.2, line_text, ha="left", va="center", fontsize=5.6, color=INK)


def figure2_result_screen():
    meta = json.loads(SCREEN.with_suffix(".json").read_text(encoding="utf-8"))
    img = Image.open(SCREEN)
    scale = img.width / 1180  # 1180-px result container captured at device scale 2
    crop_top, crop_bottom = 150, 800
    img = img.crop((0, int(crop_top * scale), img.width, min(img.height, int(crop_bottom * scale))))
    fig = plt.figure(figsize=(178 / 25.4, 130 / 25.4))

    strip = fig.add_axes([0, 0.815, 1, 0.185])
    strip.set_xlim(0, 178)
    strip.set_ylim(0, 24)
    strip.axis("off")
    components = {c["role"]: c for c in meta["request"]["components"]}
    ni, al = components["active_metal"], components["support"]
    quote = meta["nickel_quote"]
    captured = meta["captured_at"][:10]
    cards = [
        ("Formulation", f"{ni['wt_pct']:g} wt% Ni / Al$_2$O$_3$",
         [f"Ni: live quote, {ni['price_per_lb']:.2f} USD/lb", f"Al$_2$O$_3$: indexed, {al['price_per_lb']:.3f} USD/lb"]),
        ("Preparation", "Incipient wetness impregnation",
         [f"{len(meta['step_labels'])} steps from the method catalog", f"{meta['route_summary']['manufacturing_mode']} mode"]),
        ("Scale", f"{meta['request']['order_size_tons']:g} t order", ["Step Method equipment fitted", "to the order size"]),
        ("Price basis", "Live tier", [f"quotes retrieved {captured}", quote["source"]]),
    ]
    x, w, gap, y0, h = 6, 39.5, 3.2, 5.5, 17
    for label, value, details in cards:
        _card(strip, x, y0, w, h, label, value, details)
        x += w + gap
    strip.add_patch(FancyArrowPatch((89, y0 - 0.3), (89, 0.6), arrowstyle="-|>", mutation_scale=6, color=INK, lw=0.7,
                                    shrinkA=0, shrinkB=0))
    fig.text(0.012, 0.975, "a", fontsize=8, fontweight="bold")

    ax = fig.add_axes([0.005, 0.075, 0.99, 0.735])
    ax.imshow(img)
    ax.axis("off")
    for n, cx, cy in CALLOUTS:
        cy -= crop_top
        ax.add_patch(Circle((cx * scale, cy * scale), 20 * scale, fc=ACC, ec="white", lw=1.2, zorder=5))
        ax.text(cx * scale, cy * scale, str(n), ha="center", va="center", fontsize=7, fontweight="bold", color="white",
                zorder=6)
    fig.text(0.012, 0.80, "b", fontsize=8, fontweight="bold")
    legend = [("1", "Headline price"), ("2", "Cost build-up"), ("3", "Price evidence"), ("4", "Preparation basis"),
              ("5", "Costing scope")]
    lax = fig.add_axes([0.02, 0.01, 0.96, 0.05])
    lax.axis("off")
    for (n, text), xx in zip(legend, (0.01, 0.20, 0.39, 0.58, 0.80), strict=True):
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


def _clean(ax, left=True):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    if not left:
        ax.spines["left"].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_linewidth(0.5)
    ax.tick_params(width=0.5, length=2, labelsize=6)


def figure3_diagnostics():
    study = json.loads(STUDY.read_text(encoding="utf-8"))
    methods = json.loads(METHODS.read_text(encoding="utf-8"))
    summary = study["summary"]
    rows = []
    for fam in study["families"]:
        cands = fam["joint_grids"]["0.05"]["candidates"]
        winner = fam["reference_winner"]
        win = cands[winner]["first_rank_share_pct"]
        others = sorted((v["first_rank_share_pct"] for k, v in cands.items() if k != winner), reverse=True)
        rows.append((fam["family"], win, others[0] if others else 0.0, max(0.0, 100.0 - win - (others[0] if others else 0.0))))
    rows.sort(key=lambda r: r[1])
    fig = plt.figure(figsize=(178 / 25.4, 108 / 25.4))

    ax = fig.add_axes([0.215, 0.085, 0.33, 0.83])
    ys = list(range(len(rows)))
    ax.barh(ys, [r[1] for r in rows], color=ACC, height=0.72, label="Reference winner")
    ax.barh(ys, [r[2] for r in rows], left=[r[1] for r in rows], color=WARN, height=0.72, label="Strongest challenger")
    ax.barh(ys, [r[3] for r in rows], left=[r[1] + r[2] for r in rows], color="#D9DEE1", height=0.72, label="Other candidates")
    ax.axvline(50, color="white", lw=0.6)
    ax.axvline(50, color=GREY, lw=0.5, ls=(0, (1.5, 1.5)))
    ax.set_yticks(ys)
    ax.set_yticklabels([FAMILY_NAMES.get(r[0], r[0]) for r in rows], fontsize=5.6)
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_xlabel("Scenarios in which the candidate ranks first (%)", fontsize=6.4)
    ax.legend(fontsize=5.6, frameon=False, loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=3, handlelength=1.0,
              columnspacing=0.9, handletextpad=0.5, borderaxespad=0.0)
    _clean(ax)
    ax.tick_params(axis="y", length=0)
    fig.text(0.01, 0.965, "a", fontsize=8, fontweight="bold")

    bx = fig.add_axes([0.745, 0.60, 0.235, 0.29])
    n = summary["families"]
    tests = [
        ("Majority of scenarios", n - summary["families_reference_winner_below_half_joint"]),
        ("Any one candidate removed", n - summary["candidate_removal_families_changed"]),
        ("Scores moved ±2 points", summary["rubric_robust_family_counts"]["2"]),
        ("Scores moved ±5 points", summary["rubric_robust_family_counts"]["5"]),
        ("Scores moved ±10 points", summary["rubric_robust_family_counts"]["10"]),
    ]
    yb = list(range(len(tests)))
    bx.barh(yb, [n] * len(tests), color="#EEF1F2", height=0.64)
    bx.barh(yb, [t[1] for t in tests], color=ACC, height=0.64)
    for i, (_, c) in enumerate(tests):
        bx.text(c + 0.6, i, f"{c}", va="center", fontsize=6, color=INK)
    bx.set_yticks(yb)
    bx.set_yticklabels([t[0] for t in tests], fontsize=6)
    bx.invert_yaxis()
    bx.set_xlim(0, n)
    bx.set_xticks([0, 10, 20, 30])
    bx.set_xlabel("Families whose reference winner survives (of 30)", fontsize=6.4)
    _clean(bx, left=False)
    bx.tick_params(axis="y", length=0)
    fig.text(0.565, 0.965, "b", fontsize=8, fontweight="bold")

    cx = fig.add_axes([0.745, 0.085, 0.235, 0.40])
    ex = methods["normalization"]["example"]["rows"]
    names = ["Co/MgO–La$_2$O$_3$", "Ni–MgO/CeO$_2$", "Ni/Al$_2$O$_3$"]
    before = [r["total_before"] for r in ex]
    after = [r["total_after"] for r in ex]
    win_b, win_a = before.index(max(before)), after.index(max(after))
    ys = [2, 1, 0]
    for i, y in enumerate(ys):
        cx.plot([after[i], before[i]], [y, y], color=RULE, lw=1.0, zorder=2)
        cx.plot(before[i], y, "o", color=ACC, ms=4.2, zorder=3)
        cx.plot(after[i], y, "o", mfc="white" if after[i] == before[i] else WARN, mec=WARN, mew=0.9, ms=4.2, zorder=4)
        cx.text(before[i], y + 0.22, f"{before[i]:.1f}" + (" (1st)" if i == win_b else ""), ha="center", va="bottom",
                fontsize=5.6, color=ACC)
        cx.text(after[i], y - 0.22, f"{after[i]:.1f}" + (" (1st)" if i == win_a else ""), ha="center", va="top",
                fontsize=5.6, color=WARN)
    cx.set_yticks(ys)
    cx.set_yticklabels([f"{n}\n{r['cost']:.2f} USD/lb" for n, r in zip(names, ex, strict=True)], fontsize=5.8)
    cx.set_ylim(-0.8, 2.8)
    cx.set_xlim(35, 100)
    cx.set_xlabel("Composite score", fontsize=6.4)
    cx.plot([], [], "o", color=ACC, ms=4, label="Full candidate set")
    cx.plot([], [], "o", mfc=WARN, mec=WARN, ms=4, label="Ru candidate removed")
    cx.legend(fontsize=5.6, frameon=False, loc="lower left", handlelength=1.0, handletextpad=0.5, borderaxespad=0.2)
    _clean(cx)
    cx.tick_params(axis="y", length=0)
    fig.text(0.565, 0.505, "c", fontsize=8, fontweight="bold")
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
