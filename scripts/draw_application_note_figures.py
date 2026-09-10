"""Draw Application Note Figures 2 and 3 from repository assets and frozen runs.

Figure 1 is an AI-assisted illustration kept as a committed PNG with its raw file, provenance
note and the connector-line script (scripts/straighten_note_fig1_leaders.py), so it is not
drawn here. Figure 2 draws the cost model, the price build-up of the Ni/Al2O3 example recorded by
scripts/capture_note_result_screen.py and the price basis of eight metals from the frozen
2026-09-08 price package. Figure 3 reads the frozen joint robustness study
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
from matplotlib.ticker import FuncFormatter, MaxNLocator  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "docs/paper/robustness-2026-09-08/decision_robustness.json"
METHODS = ROOT / "docs/paper/methods-2026-09-09/methods_study.json"
EXAMPLE = ROOT / "docs/paper/figures-note-2026-09-09/screen_result_ni_al2o3.json"
HISTORY = ROOT / "docs/paper/submission-2026-09-08/price_history_2026-09-08.json"
LIVE = ROOT / "docs/paper/submission-2026-09-08/live_basis_2026-09-08.json"
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


def _arrow(ax, x1, y1, x2, y2, color=INK, label=None, dy=1.6):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=6, color=color, lw=0.7,
                                 shrinkA=0, shrinkB=0, zorder=4))
    if label:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + dy, label, ha="center", va="bottom", fontsize=6.4, color=INK)


METALS = [("Pt", "Platinum"), ("Pd", "Palladium"), ("Rh", "Rhodium"), ("Ru", "Ruthenium"),
          ("Ir", "Iridium"), ("Au", "Gold"), ("Ag", "Silver"), ("Ni", "Nickel")]


def _price_unit(unit):
    return {"$/troy_oz": "USD/troy oz", "$/lb": "USD/lb"}.get(unit, unit)


def figure2_cost_model():
    example = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    history = json.loads(HISTORY.read_text(encoding="utf-8"))["series"]
    live = json.loads(LIVE.read_text(encoding="utf-8"))["price_basis"]
    fig = plt.figure(figsize=(178 / 25.4, 150 / 25.4))

    # ---- a: cost model schematic (millimetre coordinates)
    ax = fig.add_axes([0, 0.715, 1, 0.285])
    ax.set_xlim(0, 178)
    ax.set_ylim(0, 47)
    ax.axis("off")
    fig.text(0.012, 0.978, "a", fontsize=8, fontweight="bold")
    inputs = [("Formulation", "components, wt%", 35.5), ("Preparation route", "operations, order size", 20),
              ("Price basis", "live or reference tier", 4.5)]
    for title, sub, y in inputs:
        _box(ax, 6, y, 26, 9.6)
        ax.text(19, y + 6.4, title, ha="center", va="center", fontsize=6.6, fontweight="bold")
        ax.text(19, y + 2.7, sub, ha="center", va="center", fontsize=5.6, color=MUTED)
    mx, mw = 38, 57
    _box(ax, mx, 24.5, mw, 21, fill="white", edge=INK, lw=0.6)
    ax.text(mx + mw / 2, 42.2, "Materials", ha="center", va="center", fontsize=6.8, fontweight="bold")
    ax.text(mx + mw / 2, 35.0, r"$C_\mathrm{m}=\sum_i w_i\,c_i$", ha="center", va="center", fontsize=8.6)
    ax.text(mx + mw / 2, 29.6, "unit price × mass fraction", ha="center", va="center", fontsize=5.6)
    ax.text(mx + mw / 2, 26.6, "purchased input: a = w/(f·p·y)", ha="center", va="center", fontsize=5.6)
    _box(ax, mx, 1.0, mw, 21, fill="white", edge=INK, lw=0.6)
    ax.text(mx + mw / 2, 18.7, "Processing (Step Method)", ha="center", va="center", fontsize=6.8, fontweight="bold")
    ax.text(mx + mw / 2, 11.5, r"$C_\mathrm{p}=24\,T\,I\,\sum_j H_j\,/\,M$", ha="center", va="center", fontsize=8.6)
    ax.text(mx + mw / 2, 6.1, "hourly rates at the fitted scale class", ha="center", va="center", fontsize=5.6)
    ax.text(mx + mw / 2, 3.1, "campaign time, index escalation, mass produced", ha="center", va="center", fontsize=5.6)
    _arrow(ax, 32.3, 40.3, mx - 0.3, 38.5)
    _arrow(ax, 32.3, 9.3, mx - 0.3, 11.5)
    _arrow(ax, 32.3, 24.8, mx - 0.3, 31.5)
    _arrow(ax, 32.3, 24.8, mx - 0.3, 15.5)
    px, pw = 101, 40
    _box(ax, px, 11, pw, 24, fill="white", edge=INK, lw=0.6)
    ax.text(px + pw / 2, 31.7, "Overhead and margin", ha="center", va="center", fontsize=6.8, fontweight="bold")
    ax.text(px + pw / 2, 22.5, r"$P=\dfrac{(C_\mathrm{m}+C_\mathrm{p})(1+g)(1+s)}{1-m}$", ha="center", va="center",
            fontsize=8.6)
    ax.text(px + pw / 2, 14.1, "G&A, S&ARD, margin set by order size", ha="center", va="center", fontsize=5.6)
    _arrow(ax, mx + mw + 0.3, 35.0, px - 0.3, 27.0, label=r"$C_\mathrm{m}$")
    _arrow(ax, mx + mw + 0.3, 11.5, px - 0.3, 19.0, label=r"$C_\mathrm{p}$", dy=-4.6)
    lx, lw_ = 147, 28
    _box(ax, lx, 11, lw_, 24, fill="#EAF1F2", edge=ACC, lw=0.6)
    ax.text(lx + lw_ / 2, 31.7, "Ledger", ha="center", va="center", fontsize=6.8, fontweight="bold")
    for k, line_text in enumerate(["selling price per lb", "price, source, date", "grade, price tier",
                                   "operations priced,", "substituted, uncosted"]):
        ax.text(lx + 2.2, 27.3 - k * 3.6, line_text, ha="left", va="center", fontsize=5.5)
    _arrow(ax, px + pw + 0.3, 23.0, lx - 0.3, 23.0, label=r"$P$")

    # ---- b: price build-up for the worked example
    bx = fig.add_axes([0.07, 0.115, 0.255, 0.50])
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
    bx.set_xticklabels([label for label, _ in items] + ["Selling price"], fontsize=5.6, rotation=45, ha="right",
                       rotation_mode="anchor")
    bx.set_ylim(0, total * 1.18)
    bx.set_ylabel("USD per lb of catalyst", fontsize=6.4)
    bx.text(0.02, 0.97, "20 wt% Ni/Al$_2$O$_3$\nincipient wetness, 20 t, live tier", transform=bx.transAxes,
            ha="left", va="top", fontsize=5.6, color=MUTED)
    _clean(bx)
    bx.tick_params(axis="x", length=0)
    fig.text(0.012, 0.64, "b", fontsize=8, fontweight="bold")

    # ---- c: price basis of the metals that dominate catalyst cost
    fig.text(0.365, 0.64, "c", fontsize=8, fontweight="bold")
    x_left, x_right, y_bottom, y_top = 0.425, 0.985, 0.115, 0.585
    cols, rows_n = 4, 2
    pw_ = (x_right - x_left - (cols - 1) * 0.02) / cols
    ph_ = (y_top - y_bottom - 0.10) / rows_n
    replay_end = None
    for k, (sym, name) in enumerate(METALS):
        r_, c_ = divmod(k, cols)
        cx = fig.add_axes([x_left + c_ * (pw_ + 0.02), y_top - (r_ + 1) * ph_ - r_ * 0.10, pw_, ph_])
        series = history[sym]
        dates = [datetime.strptime(p["date"], "%Y-%m-%d") for p in series["points"]]
        prices = [p["price"] for p in series["points"]]
        replay_end = next(d for d in dates if d.strftime("%Y-%m") == REFERENCE_MONTH)
        cx.axvspan(dates[0], replay_end, color=FILL, zorder=0)
        cx.plot(dates, prices, color=GREY, lw=0.7, zorder=2)
        cx.plot(replay_end, prices[dates.index(replay_end)], "o", color=ACC, ms=3.4, zorder=4)
        quote = live[sym]
        cx.plot(datetime.strptime(quote["fetched_at"][:10], "%Y-%m-%d"), quote["price"], "o", mfc=WARN, mec=WARN,
                ms=3.4, zorder=4)
        top = max(max(prices), quote["price"])
        cx.set_ylim(0, top * 1.25)
        cx.set_xlim(dates[0], datetime(2026, 11, 1))
        cx.text(0.03, 0.96, f"{name}  ({_price_unit(series['unit'])})", transform=cx.transAxes, ha="left", va="top",
                fontsize=5.6, fontweight="bold")
        cx.yaxis.set_major_locator(MaxNLocator(3))
        cx.yaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"{v / 1000:g}k" if v >= 1000 else f"{v:g}"))
        cx.set_xticks([datetime(y, 1, 1) for y in (2020, 2023, 2026)])
        cx.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        _clean(cx)
        cx.tick_params(labelsize=5.2, length=1.5, pad=1.5)
    fig.text(0.705, 0.625, "Monthly averages 2019-01 to 2026-07; shaded: 89-month replay window\n"
             f"teal: reference tier ({REFERENCE_MONTH} average); orange: live quote held in the frozen package",
             ha="center", va="center", fontsize=5.4, color=MUTED, linespacing=1.4)
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
