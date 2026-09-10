"""Draw Application Note Figures 2 and 3 from repository assets and frozen runs.

Figure 1 is an AI-assisted illustration kept as a committed PNG with its raw file, provenance
note and the connector-line script (scripts/straighten_note_fig1_leaders.py), so it is not
drawn here. Figure 2 draws the cost model, the price build-up of the Ni/Al2O3 example recorded by
scripts/capture_note_result_screen.py and the nickel price basis from the frozen 2026-09-08 series. Figure 3 reads the frozen joint robustness study
and the methods supplement. Run:

    python scripts/draw_application_note_figures.py --out-dir docs/paper/figures-note-2026-09-09
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "docs/paper/robustness-2026-09-08/decision_robustness.json"
METHODS = ROOT / "docs/paper/methods-2026-09-09/methods_study.json"
EXAMPLE = ROOT / "docs/paper/figures-note-2026-09-09/screen_result_ni_al2o3.json"
HISTORY = ROOT / "docs/paper/submission-2026-09-08/price_history_2026-09-08.json"
REFERENCE_MONTH = "2026-05"
INK, MUTED, RULE, GREY = "#1F2A30", "#5B6870", "#C3CBCE", "#9AA6AB"
FILL, ACC, ACC_DEEP, WARN = "#F4F6F7", "#1B6F78", "#124C52", "#B8702F"
LW = 0.9
plt.rcParams.update({"font.family": "Arial", "font.size": 7.5, "text.color": INK, "svg.fonttype": "none",
                     "svg.hashsalt": "comet-note-figures-2026-09-09", "axes.edgecolor": INK, "axes.linewidth": 0.6,
                     "xtick.color": INK, "ytick.color": INK, "mathtext.fontset": "custom", "mathtext.rm": "Arial",
                     "mathtext.it": "Arial:italic", "mathtext.bf": "Arial:bold"})


def _clean(ax, left=True):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    if not left:
        ax.spines["left"].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_linewidth(0.5)
    ax.tick_params(width=0.5, length=2, labelsize=6)


def _box(ax, x, y, w, h, fill=FILL, edge=RULE, lw=0.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.8", fc=fill, ec=edge, lw=lw))


def _arrow(ax, x1, y1, x2, y2, color=INK):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=6, color=color, lw=0.7,
                                 shrinkA=0, shrinkB=0, zorder=4))


def figure2_cost_model():
    example = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    history = json.loads(HISTORY.read_text(encoding="utf-8"))["series"]["Ni"]
    fig = plt.figure(figsize=(178 / 25.4, 128 / 25.4))

    # ---- a: cost model schematic (millimetre coordinates)
    ax = fig.add_axes([0, 0.585, 1, 0.415])
    ax.set_xlim(0, 178)
    ax.set_ylim(0, 53)
    ax.axis("off")
    fig.text(0.012, 0.975, "a", fontsize=8, fontweight="bold")
    inputs = [("Formulation", "components, wt%"), ("Preparation route", "operations, order size"),
              ("Price basis", "live or reference tier")]
    for i, (title, sub) in enumerate(inputs):
        y = 40 - i * 13.5
        _box(ax, 4, y, 26, 11)
        ax.text(17, y + 7.4, title, ha="center", va="center", fontsize=6.4, fontweight="bold")
        ax.text(17, y + 3.4, sub, ha="center", va="center", fontsize=5.6, color=MUTED)
    stages = [
        ("Materials", r"$C_\mathrm{m}=\sum_i w_i\,c_i$", ["unit price × mass fraction, or a", "purchased input a = w/(f·p·y)"]),
        ("Processing (Step Method)", r"$C_\mathrm{p}=\dfrac{24\,T\,I\,\sum_j H_j}{M}$",
         ["hourly rates by scale class,", "campaign time, index, mass"]),
        ("Overhead and margin", r"$P=\dfrac{(C_\mathrm{m}+C_\mathrm{p})(1+g)(1+s)}{1-m}$",
         ["G&A and S&ARD uplift,", "margin set by order size"]),
    ]
    x0, sw, gap = 36, 31, 3.5
    for i, (title, eq, notes) in enumerate(stages):
        x = x0 + i * (sw + gap)
        _box(ax, x, 12, sw, 39, fill="white", edge=INK, lw=0.6)
        ax.text(x + sw / 2, 47, title, ha="center", va="center", fontsize=6.4, fontweight="bold")
        ax.text(x + sw / 2, 36.5, eq, ha="center", va="center", fontsize=7.2)
        for k, note in enumerate(notes):
            ax.text(x + sw / 2, 22.5 - k * 4.0, note, ha="center", va="center", fontsize=5.4, color=MUTED)
        if i < len(stages) - 1:
            _arrow(ax, x + sw + 0.3, 31.5, x + sw + gap - 0.3, 31.5)
    _arrow(ax, 30.3, 45.5, 35.7, 40)
    _arrow(ax, 30.3, 32, 35.7, 32)
    _arrow(ax, 30.3, 18.5, 35.7, 24)
    xo = x0 + 3 * sw + 2 * gap + 4
    _box(ax, xo, 12, 178 - xo - 3, 39, fill="#EAF1F2", edge=ACC, lw=0.6)
    ax.text(xo + (178 - xo - 3) / 2, 47, "Ledger", ha="center", va="center", fontsize=6.4, fontweight="bold")
    for k, line_text in enumerate(["selling price per lb", "price, source, quote date", "reliability grade, tier",
                                   "operations priced,", "substituted or uncosted"]):
        ax.text(xo + 2.5, 40.5 - k * 5.4, line_text, ha="left", va="center", fontsize=5.6)
    _arrow(ax, x0 + 3 * sw + 2 * gap + 0.3, 31.5, xo - 0.3, 31.5)

    # ---- b: price build-up for the worked example
    bx = fig.add_axes([0.075, 0.075, 0.40, 0.44])
    sm = example["step_method"]
    comps = example["materials"]["components"]
    items = [(c["name"].replace("2", "$_2$").replace("3", "$_3$"), c["cost_per_lb_cat"]) for c in comps]
    items += [("Processing", sm["processing_cost_per_lb"]), ("G&A", sm["ga_per_lb"]), ("S&ARD", sm["sard_per_lb"]),
              ("Margin", sm["margin_per_lb"])]
    colors = [ACC] * len(comps) + ["#6FA8AE", GREY, GREY, WARN]
    base = 0.0
    for i, ((label, value), color) in enumerate(zip(items, colors, strict=True)):
        bx.bar(i, value, bottom=base, color=color, width=0.66)
        bx.text(i, base + value + 0.08, f"{value:.2f}", ha="center", va="bottom", fontsize=5.8)
        base += value
        if i < len(items) - 1:
            bx.plot([i + 0.33, i + 1 - 0.33], [base, base], color=GREY, lw=0.5, ls=(0, (1.5, 1.5)))
    total = sm["estimated_price_per_lb"]
    bx.bar(len(items), total, color=INK, width=0.66)
    bx.text(len(items), total + 0.08, f"{total:.2f}", ha="center", va="bottom", fontsize=5.8, fontweight="bold")
    bx.set_xticks(range(len(items) + 1))
    bx.set_xticklabels([label for label, _ in items] + ["Selling\nprice"], fontsize=5.8)
    bx.set_ylim(0, total * 1.18)
    bx.set_ylabel("USD per lb of catalyst", fontsize=6.4)
    bx.text(0.02, 0.97, "20 wt% Ni/Al$_2$O$_3$ · incipient wetness · 20 t · live tier", transform=bx.transAxes,
            ha="left", va="top", fontsize=5.6, color=MUTED)
    _clean(bx)
    bx.tick_params(axis="x", length=0)
    fig.text(0.012, 0.535, "b", fontsize=8, fontweight="bold")

    # ---- c: price basis for nickel
    cx = fig.add_axes([0.585, 0.075, 0.40, 0.44])
    dates = [datetime.strptime(p["date"], "%Y-%m-%d") for p in history["points"]]
    prices = [p["price"] for p in history["points"]]
    replay_end = next(d for d in dates if d.strftime("%Y-%m") == REFERENCE_MONTH)
    cx.axvspan(dates[0], replay_end, color=FILL, zorder=0)
    cx.plot(dates, prices, color=GREY, lw=0.8, zorder=2)
    ref_price = prices[dates.index(replay_end)]
    cx.plot(replay_end, ref_price, "o", color=ACC, ms=4.2, zorder=4)
    cx.annotate(f"Reference tier\n{REFERENCE_MONTH} average, {ref_price:.2f}", (replay_end, ref_price),
                xytext=(-8, 14), textcoords="offset points", ha="right", va="bottom", fontsize=5.6, color=ACC,
                arrowprops=dict(arrowstyle="-", color=ACC, lw=0.5))
    live_date = datetime.strptime(example["captured_at"][:10], "%Y-%m-%d")
    live_price = example["nickel_quote"]["price"]
    cx.plot(live_date, live_price, "o", mfc=WARN, mec=WARN, ms=4.2, zorder=4)
    cx.annotate(f"Live tier\n{example['captured_at'][:10]} quote, {live_price:.2f}", (live_date, live_price),
                xytext=(-6, -18), textcoords="offset points", ha="right", va="top", fontsize=5.6, color=WARN,
                arrowprops=dict(arrowstyle="-", color=WARN, lw=0.5))
    cx.text(dates[0] + (replay_end - dates[0]) / 2, max(prices) * 1.02, f"{len([d for d in dates if d <= replay_end])}-month replay window",
            ha="center", va="bottom", fontsize=5.6, color=MUTED)
    cx.set_ylabel("Nickel price (USD/lb)", fontsize=6.4)
    cx.set_ylim(0, max(prices) * 1.15)
    cx.xaxis.set_major_locator(mdates.YearLocator(2))
    cx.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    _clean(cx)
    fig.text(0.53, 0.535, "c", fontsize=8, fontweight="bold")
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
    for name, fn in (("fig2_cost_model", figure2_cost_model), ("fig3_decision_diagnostics", figure3_diagnostics)):
        fig = fn()
        fig.savefig(args.out_dir / f"{name}.png", dpi=400, facecolor="white", metadata={"Software": "COMET"})
        fig.savefig(args.out_dir / f"{name}.svg", facecolor="white", metadata={"Date": None})
        plt.close(fig)
        print("wrote", args.out_dir / name)


if __name__ == "__main__":
    main()
