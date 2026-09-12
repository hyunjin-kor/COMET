"""Draw Application Note Figures 2, 3 and 4 from repository assets and frozen runs.

Figure 1 is an AI-assisted illustration kept as a committed PNG with its raw file, provenance
note and the connector-line script (scripts/straighten_note_fig1_leaders.py), so it is not
drawn here. Figure 2 draws the cost model, the cost structure of the cheapest candidate in
every thermal reaction family, the three published CatCost validation cases against their
published market prices, and the estimates against the traded unit value of the matching
catalyst category. Figure 3 is the monthly price record of every metal the library prices, in
one column. Figure 4 reads the frozen combined robustness study and the methods supplement.
All three render in English or Korean. Run:

    python scripts/draw_application_note_figures.py --out-dir docs/paper/figures-note-2026-09-09
    python scripts/draw_application_note_figures.py --lang ko
"""

import argparse
import json
import math
import re
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402
from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "docs/paper/robustness-2026-09-08/decision_robustness.json"
METHODS = ROOT / "docs/paper/methods-2026-09-09/methods_study.json"
EXAMPLE = ROOT / "docs/paper/figures-note-2026-09-09/screen_result_ni_al2o3.json"
MARKET = ROOT / "docs/paper/catalyst_market_2026-09-10.json"
FAMILIES = ROOT / "docs/paper/submission-2026-09-08/all_families_2026-09-08.json"
VALIDATION = ROOT / "docs/paper/submission-2026-09-08/table62_reproduction_2026-09-08.json"
HISTORY = ROOT / "docs/paper/submission-2026-09-08/monthly_history_2026-09-08.json"
REFERENCE_MONTH = "2026-05"
INK, MUTED, RULE, GREY = "#1F2A30", "#5B6870", "#C3CBCE", "#9AA6AB"
FILL, ACC, ACC_MID, WARN = "#F4F6F7", "#1B6F78", "#6FA8AE", "#B8702F"


TEXT = {
    "en": {
        "font": "Arial",
        "formulation": "Formulation", "route": "Preparation route",
        "basis": "Price basis", "order_size": "Order size",
        "materials": "Materials",
        "processing": "Processing (Step Method)",
        "selling_price": "Selling price",
        "share_x": "Share of the selling price (%)",
        "seg_materials": "Materials", "seg_processing": "Processing", "seg_overhead": "Overhead and margin",
        "total_head": "USD/lb",
        "c_x": "Selling price (USD per lb, log scale)",
        "c_comet": "COMET", "c_published": "Published method", "c_market": "Published market price",
        "c_y": "Deviation from market price (%)",
        "market_ratio_y": "Estimate ÷ traded unit value",
        "market_titles": {"nickel": "Nickel catalysts", "precious": "Precious-metal catalysts", "other": "Other active substances"},
        "market_traded": "Import unit value (= 1)",
        "market_estimate": "Reference-leading candidates",
        "unit_lb": "USD/lb",
        "metals_base": "Base metals", "metals_precious": "Precious metals", "metal_price": "Price",
        "f3_first": "Reference leader", "f3_second": "Leading alternative",
        "f3_other": "Other candidates", "f3_x": "First-rank frequency (%)",
        "f3_tests": ["Joint share\n≥50%", "Candidate\nremoval", "Score bounds\n±2 points",
                     "Score bounds\n±5 points", "Score bounds\n±10 points"],
        "f3_b_x": "Leader retained (families)",
        "f3_c_x": "Cost (USD/lb)",
        "f3_before": "Reference leader", "f3_after": "Leader after removal",
        "usd_lb": "USD/lb",
    },
    "ko": {
        "font": "Malgun Gothic",
        "formulation": "조성", "route": "제조 경로",
        "basis": "가격 기준", "order_size": "주문량",
        "materials": "재료비",
        "processing": "가공비 (Step Method)",
        "selling_price": "판매 단가",
        "share_x": "판매 단가 대비 비율 (%)",
        "seg_materials": "재료비", "seg_processing": "가공비", "seg_overhead": "간접비와 마진",
        "total_head": "USD/lb",
        "c_x": "판매 단가 (USD/lb, 로그 축)",
        "c_comet": "COMET", "c_published": "발표된 방법", "c_market": "발표된 시장 가격",
        "c_y": "시장 가격 대비 편차 (%)",
        "market_ratio_y": "추정값 ÷ 거래 단가",
        "market_titles": {"nickel": "니켈계 촉매", "precious": "귀금속계 촉매", "other": "그 밖의 활성 물질"},
        "market_traded": "수입 단가 (= 1)",
        "market_estimate": "기준 조건의 1위 후보",
        "unit_lb": "USD/lb",
        "metals_base": "일반 금속", "metals_precious": "귀금속", "metal_price": "가격",
        "f3_first": "기준 조건의 1위", "f3_second": "주요 대안 후보",
        "f3_other": "그 밖의 후보", "f3_x": "1위 빈도 (%)",
        "f3_tests": ["결합 시나리오\n빈도 ≥50%", "후보 제거", "점수 범위\n±2점",
                     "점수 범위\n±5점", "점수 범위\n±10점"],
        "f3_b_x": "1위 유지 반응군 수",
        "f3_c_x": "원가 (USD/lb)",
        "f3_before": "기준 조건의 1위", "f3_after": "제거 후 1위",
        "usd_lb": "USD/lb",
    },
}

FAMILY_NAMES = {
    "en": {
        "aem-electrolyzer-oer": "AEM electrolyzer OER", "ammonia-cracking": "Ammonia cracking",
        "ammonia-synthesis": "Ammonia synthesis", "co2-electroreduction": "CO$_2$ electroreduction",
        "co2-methanation": "CO$_2$ methanation", "co2-methanol": "CO$_2$ to methanol",
        "co2-to-formate": "CO$_2$ to formate", "co-prox": "Preferential CO oxidation",
        "dry-reforming": "Methane dry reforming", "ethylene-epoxidation": "Ethylene epoxidation",
        "fischer-tropsch-synthesis": "Fischer–Tropsch synthesis",
        "formic-acid-dehydrogenation": "Formic acid dehydrogenation", "fuel-cell-orr": "Fuel-cell ORR",
        "glycerol-electrooxidation": "Glycerol electro-oxidation",
        "hydrodeoxygenation": "Bio-oil hydrodeoxygenation",
        "hydrogen-evolution-reaction": "Hydrogen evolution reaction", "methane-pyrolysis": "Methane pyrolysis",
        "methanol-to-olefins": "Methanol to olefins", "nh3-scr": "NH$_3$-SCR",
        "nitrogen-reduction-reaction": "Electrochemical N$_2$ reduction", "olefin-metathesis": "Olefin metathesis",
        "pem-electrolyzer-oer": "PEM electrolyzer OER",
        "photocatalytic-co2-reduction": "Photocatalytic CO$_2$ reduction",
        "photocatalytic-water-splitting": "Photocatalytic water splitting",
        "propane-dehydrogenation": "Propane dehydrogenation", "rwgs": "Reverse water-gas shift",
        "selective-acetylene-hydrogenation": "Selective acetylene hydrogenation",
        "steam-methane-reforming": "Steam methane reforming", "syngas-methanol": "Syngas to methanol",
        "water-gas-shift": "Water-gas shift",
    },
    "ko": {
        "aem-electrolyzer-oer": "AEM 수전해 OER", "ammonia-cracking": "암모니아 분해",
        "ammonia-synthesis": "암모니아 합성", "co2-electroreduction": "CO$_2$ 전기환원",
        "co2-methanation": "CO$_2$ 메탄화", "co2-methanol": "CO$_2$ 메탄올 전환",
        "co2-to-formate": "CO$_2$ 포름산염 전환", "co-prox": "CO 선택 산화",
        "dry-reforming": "메탄 건식 개질", "ethylene-epoxidation": "에틸렌 에폭시화",
        "fischer-tropsch-synthesis": "피셔–트롭슈 합성",
        "formic-acid-dehydrogenation": "포름산 탈수소", "fuel-cell-orr": "연료전지 ORR",
        "glycerol-electrooxidation": "글리세롤 전기산화", "hydrodeoxygenation": "바이오오일 수첨탈산소",
        "hydrogen-evolution-reaction": "수소 발생 반응", "methane-pyrolysis": "메탄 열분해",
        "methanol-to-olefins": "메탄올 올레핀 전환", "nh3-scr": "NH$_3$-SCR",
        "nitrogen-reduction-reaction": "전기화학적 N$_2$ 환원", "olefin-metathesis": "올레핀 복분해",
        "pem-electrolyzer-oer": "PEM 수전해 OER", "photocatalytic-co2-reduction": "광촉매 CO$_2$ 환원",
        "photocatalytic-water-splitting": "광촉매 물분해", "propane-dehydrogenation": "프로판 탈수소",
        "rwgs": "역 수성가스 전이", "selective-acetylene-hydrogenation": "아세틸렌 선택 수소화",
        "steam-methane-reforming": "메탄 수증기 개질", "syngas-methanol": "합성가스 메탄올 전환",
        "water-gas-shift": "수성가스 전이",
    },
}

VALIDATION_NAMES = {
    "en": {"2 wt% Pt/C": "2 wt%\nPt/C", "21 wt% Ni/Al2O3": "21 wt%\nNi/Al$_2$O$_3$",
           "USY-based FCC (with RE)": "USY\nFCC"},
    "ko": {"2 wt% Pt/C": "2 wt%\nPt/C", "21 wt% Ni/Al2O3": "21 wt%\nNi/Al$_2$O$_3$",
           "USY-based FCC (with RE)": "USY\nFCC"},
}

L = TEXT["en"]
FAM = FAMILY_NAMES["en"]
VAL = VALIDATION_NAMES["en"]


def set_language(lang):
    global L, FAM, VAL
    L, FAM, VAL = TEXT[lang], FAMILY_NAMES[lang], VALIDATION_NAMES[lang]
    plt.rcParams.update({
        "font.family": L["font"], "font.size": 7.5, "text.color": INK, "svg.fonttype": "none",
        "svg.hashsalt": "comet-note-figures-2026-09-09", "axes.edgecolor": INK, "axes.linewidth": 0.6,
        "xtick.color": INK, "ytick.color": INK, "axes.unicode_minus": False,
        "mathtext.fontset": "custom", "mathtext.rm": "Arial", "mathtext.it": "Arial:italic",
        "mathtext.bf": "Arial:bold", "mathtext.sf": "Arial", "mathtext.fallback": "stixsans",
    })


def _clean(ax, left=True):
    """A closed box on all four sides, which is what the author asked for in review."""
    for side in ("top", "right", "bottom", "left"):
        ax.spines[side].set_visible(True)
        ax.spines[side].set_linewidth(0.5)
    ax.tick_params(width=0.5, length=2, labelsize=7.5)


def _box(ax, x, y, w, h, fill=FILL, edge=RULE, lw=0.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.8", fc=fill, ec=edge, lw=lw))


def _arrow(ax, x1, y1, x2, y2, color=INK):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=6, color=color, lw=0.7,
                                 shrinkA=0, shrinkB=0, zorder=4))


def _cost_model_panel(fig):
    ax = fig.add_axes([0, 0.8044, 1, 0.1956])
    ax.set_xlim(0, 178)
    ax.set_ylim(0, 47)
    ax.axis("off")
    for key, y in (("formulation", 36), ("basis", 26), ("route", 16), ("order_size", 6)):
        _box(ax, 4, y, 34, 8)
        ax.text(21, y + 4, L[key], ha="center", va="center", fontsize=8.5, fontweight="bold")
        _arrow(ax, 38.4, y + 4, 49.6, y + 4)

    mx, mw = 50, 46
    _box(ax, mx, 26, mw, 18, fill="white", edge=INK, lw=0.6)
    ax.text(73, 40, L["materials"], ha="center", va="center", fontsize=9.0, fontweight="bold")
    ax.text(73, 32, r"$C_\mathrm{m}=\sum_i w_i\,c_i$", ha="center", va="center", fontsize=11.0)
    _box(ax, mx, 6, mw, 18, fill="white", edge=INK, lw=0.6)
    ax.text(73, 20, L["processing"], ha="center", va="center", fontsize=8.5, fontweight="bold")
    ax.text(73, 12, r"$C_\mathrm{p}=\dfrac{24\,T\,I\,H}{M}$", ha="center", va="center", fontsize=11.0)

    px, pw = 112, 62
    _box(ax, px, 15, pw, 22, fill="#EAF1F2", edge=ACC, lw=0.6)
    ax.text(143, 32.5, L["selling_price"], ha="center", va="center", fontsize=9.0, fontweight="bold")
    ax.text(143, 23.5, r"$P=\dfrac{(C_\mathrm{m}+C_\mathrm{p})(1+g)(1+s)}{1-m}$", ha="center",
            va="center", fontsize=11.0)

    # Independent orthogonal paths preserve the two cost contributions.
    for start_y, end_y, label_y, label, va in (
        (35, 30, 36.5, r"$C_\mathrm{m}$", "bottom"),
        (15, 22, 13.5, r"$C_\mathrm{p}$", "top"),
    ):
        ax.plot([96.4, 103, 103], [start_y, start_y, end_y], color=INK, lw=0.7, zorder=3)
        _arrow(ax, 103, end_y, px - 0.4, end_y)
        ax.text(100, label_y, label, ha="center", va=va, fontsize=8.5)

    # Order size also sets the selling-margin fraction, independently of processing cost.
    ax.plot([44, 44, 143], [10, 2, 2], color=INK, lw=0.7, zorder=3)
    _arrow(ax, 143, 2, 143, 14.6)
    ax.text(145, 8, r"$m$", ha="left", va="center", fontsize=9.0)


def _structure_panel(fig):
    """Cost composition of the lowest-cost candidate in every thermal reaction family."""
    data = json.loads(FAMILIES.read_text(encoding="utf-8"))
    rows = []
    for family in data["families"]:
        if family["catalyst_domain"] != "thermal":
            continue
        best = min(family["candidates"], key=lambda c: c["landed_cost_per_lb"])
        total = best["landed_cost_per_lb"]
        materials, processing = best["materials_cost_per_lb"], best["processing_cost_per_lb"]
        rows.append((family["family"], total, 100 * materials / total, 100 * processing / total,
                     100 * (total - materials - processing) / total))
    rows.sort(key=lambda r: r[2])
    ax = fig.add_axes([0.205, 0.4222, 0.295, 0.3200])
    ys = range(len(rows))
    ax.barh(ys, [r[2] for r in rows], color=ACC, height=0.74, label=L["seg_materials"])
    ax.barh(ys, [r[3] for r in rows], left=[r[2] for r in rows], color=ACC_MID, height=0.74,
            label=L["seg_processing"])
    ax.barh(ys, [r[4] for r in rows], left=[r[2] + r[3] for r in rows], color="#D9DEE1", height=0.74,
            label=L["seg_overhead"])
    for i, row in enumerate(rows):
        ax.text(104, i, f"{row[1]:,.2f}" if row[1] < 100 else f"{row[1]:,.0f}", va="center", ha="left",
                fontsize=6.2)
    ax.text(104, len(rows) - 0.1, L["total_head"], va="bottom", ha="left", fontsize=6.2, color=MUTED)
    ax.set_yticks(list(ys))
    ax.set_yticklabels([FAM.get(r[0], r[0]) for r in rows], fontsize=6.5)
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.7, len(rows) - 0.3)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel(L["share_x"], fontsize=7.8)
    ax.legend(fontsize=6.8, frameon=False, loc="lower left", bbox_to_anchor=(-0.66, 1.015), ncol=3,
              handlelength=1.0, columnspacing=0.8, handletextpad=0.4, borderaxespad=0.0)
    _clean(ax)
    ax.tick_params(axis="y", length=0, labelsize=6.5)


def _validation_panel(fig):
    """The three published CatCost cases against the market prices printed beside them."""
    cases = json.loads(VALIDATION.read_text(encoding="utf-8"))
    ax = fig.add_axes([0.735, 0.4844, 0.245, 0.2400])
    xs = range(len(cases))
    comet, published, labels = [], [], []
    for case in cases:
        market = case["market"]["market_price_per_lb"]
        estimate = next(r for r in case["rows"] if r["key"] == "estimated_price_per_lb")
        ours = case.get("with_published_rate", {}).get("estimated_price_per_lb", estimate["comet"])
        comet.append(100 * (ours - market) / market)
        published.append(100 * (estimate["published"] - market) / market)
        labels.append(VAL.get(case["name"], case["name"]))
    ax.bar([x - 0.2 for x in xs], comet, 0.38, color=ACC, label=L["c_comet"])
    ax.bar([x + 0.2 for x in xs], published, 0.38, color=GREY, label=L["c_published"])
    for x, (a, b) in enumerate(zip(comet, published, strict=True)):
        ax.text(x - 0.2, a - 0.9, f"{a:.1f}", ha="center", va="top", fontsize=7.0, color=ACC)
        offset = 3.0 if abs(a - b) < 2.0 else 0.9
        ax.text(x + 0.2, b - offset, f"{b:.1f}", ha="center", va="top", fontsize=7.0, color=MUTED)
    ax.axhline(0, color=INK, lw=0.6)
    ax.set_xticks(list(xs))
    ax.set_xticklabels(labels, fontsize=6.8)
    ax.set_ylim(-26, 3)
    ax.set_ylabel(L["c_y"], fontsize=7.8)
    ax.legend(fontsize=6.8, frameon=False, loc="lower left", bbox_to_anchor=(-0.24, 1.01), ncol=2,
              handlelength=1.0, columnspacing=0.8, handletextpad=0.4, borderaxespad=0.0)
    _clean(ax)
    ax.tick_params(axis="x", length=0)


PRECIOUS = ("Pt", "Pd", "Rh", "Ru", "Ir", "Au", "Ag", "Os")
MARKET_GROUPS = [("HS381511", "nickel"), ("HS381512", "precious"), ("HS381519", "other")]
LB_PER_KG = 2.20462


def _active_group(names):
    """Classify by the active substance, following the wording of the HS subheadings."""
    joined = " ".join(names)
    if re.search(r"(?<![A-Za-z])Ni(?![a-z])", joined):
        return "nickel"
    if any(re.search(rf"(?<![A-Za-z]){symbol}(?![a-z])", joined) for symbol in PRECIOUS):
        return "precious"
    return "other"


def _family_groups():
    """Map every mass-basis family to an HS subheading through its leading candidate."""
    study = json.loads(STUDY.read_text(encoding="utf-8"))
    winners = {f["family"]: f["reference_winner"] for f in study["families"]
               if f.get("unit") == "$/lb" and f.get("domain") == "thermal"}
    mapping = {}
    for path in sorted((ROOT / "backend/data").glob("*_benchmark.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        family = record.get("family")
        if family not in winners:
            continue
        candidate = next((c for c in record["candidates"] if c["slug"] == winners[family]), None)
        if candidate is None:
            continue
        actives = [c["name"] for c in candidate.get("components", [])
                   if c["role"] in ("active_metal", "active_catalyst")]
        if actives:
            mapping[family] = _active_group(actives)
    return mapping


def _market_panel(fig):
    """How far each estimate sits from the unit value of the matching traded category."""
    market = json.loads(MARKET.read_text(encoding="utf-8"))["series"]
    study = json.loads(STUDY.read_text(encoding="utf-8"))
    mapping = _family_groups()
    estimates = {}
    for family in study["families"]:
        group = mapping.get(family["family"])
        if group is None:
            continue
        slug = family["reference_winner"]
        points = []
        for ledger in family["monthly_ledgers"]:
            entry = next((c for c in ledger["candidates"] if c["slug"] == slug), None)
            if entry is not None:
                points.append((datetime.strptime(ledger["month"], "%Y-%m"),
                               entry["summary"]["landed_cost_per_lb"]))
        if len(points) > 1:
            estimates.setdefault(group, []).append(points)

    left, right, bottom, height = 0.075, 0.985, 0.0400, 0.2311
    gap = 0.055
    width = (right - left - 2 * gap) / 3
    for index, (code, group) in enumerate(MARKET_GROUPS):
        ax = fig.add_axes([left + index * (width + gap), bottom, width, height])
        series = market[code]
        traded = {pt["date"][:7]: pt["price"] / LB_PER_KG for pt in series["points"] if pt["price"] > 0}
        for points in estimates.get(group, []):
            ratios = [(date, value / traded[date.strftime("%Y-%m")]
                       if date.strftime("%Y-%m") in traded else math.nan) for date, value in points]
            if len(ratios) > 1:
                ax.plot([d for d, _ in ratios], [r for _, r in ratios], color=ACC, lw=0.8, alpha=0.85, zorder=3)
        ax.axhline(1.0, color=WARN, lw=1.4, zorder=4)
        ax.set_yscale("log")
        ax.set_xlim(datetime(2019, 1, 1), datetime(2026, 6, 1))
        ax.xaxis.set_major_locator(mdates.YearLocator(2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.yaxis.set_major_locator(LogLocator(base=10.0, subs=(1.0, 2.0, 5.0), numticks=12))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"{v:g}"))
        ax.yaxis.set_minor_formatter(NullFormatter())
        ax.set_title(f"{L['market_titles'][group]}  ({series['hs'][:4]}.{series['hs'][4:]})",
                     fontsize=7.5, fontweight="bold", pad=3)
        if index == 0:
            ax.set_ylabel(L["market_ratio_y"], fontsize=7.8)
        _clean(ax)
    handles = [plt.Line2D([], [], color=WARN, lw=1.4), plt.Line2D([], [], color=ACC, lw=0.9)]
    fig.legend(handles, [L["market_traded"], L["market_estimate"]], fontsize=7.0, frameon=False, ncol=2,
               loc="lower left", bbox_to_anchor=(left, bottom + height + 0.025), handlelength=1.6,
               columnspacing=1.4, handletextpad=0.5)


BASE_METALS = ("Ni", "Cu", "Co", "Mo", "Sn", "Al", "Zn")
PRECIOUS_METALS = ("Rh", "Ir", "Au", "Pt", "Pd", "Ru", "Ag")


METAL_COLOURS = ("#0072B2", "#D55E00", "#009E73", "#CC79A7", "#9C6B00", "#508DA8", "#555555")


def _label_ends(ax, ends, fontsize=6.4):
    """The element symbol at the end of each line, pushed apart where lines converge."""
    low, high = ax.get_ylim()
    step = (math.log10(high) - math.log10(low)) / 13
    placed = None
    for value, symbol, colour, date in sorted(ends, key=lambda end: end[0], reverse=True):
        position = math.log10(value)
        if placed is not None and placed - position < step:
            position = placed - step
        placed = position
        ax.annotate("", xy=(date, value), xycoords="data", xytext=(1.025, 10 ** position),
                    textcoords=ax.get_yaxis_transform(), annotation_clip=False,
                    arrowprops={"arrowstyle": "-", "color": colour, "lw": 0.5, "shrinkA": 0, "shrinkB": 0})
        ax.text(1.045, 10 ** position, symbol, transform=ax.get_yaxis_transform(),
                ha="left", va="center", fontsize=fontsize, color=colour)


def figure2_cost_model():
    fig = plt.figure(figsize=(178 / 25.4, 225 / 25.4))
    _cost_model_panel(fig)
    _structure_panel(fig)
    _validation_panel(fig)
    _market_panel(fig)
    for label, x, y in (("a", 0.012, 0.9822), ("b", 0.012, 0.7644), ("c", 0.60, 0.7644),
                        ("d", 0.012, 0.3022)):
        fig.text(x, y, label, fontsize=10.0, fontweight="bold")
    return fig


def figure3_metal_prices():
    """The monthly price record of every metal the library prices, in one column.

    Each metal uses a distinct colour; endpoint leaders connect displaced labels to the data.
    """
    series = json.loads(HISTORY.read_text(encoding="utf-8"))["series"]
    fig = plt.figure(figsize=(86 / 25.4, 122 / 25.4))
    for index, (symbols, title) in enumerate(((PRECIOUS_METALS, L["metals_precious"]),
                                              (BASE_METALS, L["metals_base"]))):
        ax = fig.add_axes([0.20, 0.575 - index * 0.47, 0.58, 0.345])
        ends = []
        for order, symbol in enumerate(symbols):
            points = series[symbol]["points"]
            prices = [point["price"] for point in points]
            colour = METAL_COLOURS[order]
            ax.plot([datetime.strptime(point["date"], "%Y-%m-%d") for point in points], prices,
                    color=colour, lw=1.0)
            ends.append((prices[-1], symbol, colour, datetime.strptime(points[-1]["date"], "%Y-%m-%d")))
        ax.set_yscale("log")
        ax.set_xlim(datetime(2019, 1, 1), datetime(2026, 6, 1))
        ax.xaxis.set_major_locator(mdates.YearLocator(2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.yaxis.set_major_locator(LogLocator(base=10.0, subs=(1.0, 3.0), numticks=10))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _p: f"{value:g}"))
        ax.yaxis.set_minor_formatter(NullFormatter())
        ax.set_title(title, fontsize=7.6, fontweight="bold", pad=4)
        unit = "USD/troy oz" if index == 0 else "USD/lb"
        ax.set_ylabel(f"{L['metal_price']} ({unit})", fontsize=7.0)
        _clean(ax)
        _label_ends(ax, ends)
        fig.text(0.015, 0.955 - index * 0.47, "ab"[index], fontsize=10.0, fontweight="bold")
    return fig


def figure4_diagnostics():
    study = json.loads(STUDY.read_text(encoding="utf-8"))
    summary = study["summary"]
    rows = []
    for family in study["families"]:
        candidates = family["joint_grids"]["0.05"]["candidates"]
        winner = family["reference_winner"]
        first = candidates[winner]["first_rank_share_pct"]
        others = sorted((v["first_rank_share_pct"] for k, v in candidates.items() if k != winner), reverse=True)
        second = others[0] if others else 0.0
        rows.append((family["family"], first, second, max(0.0, 100.0 - first - second)))
    rows.sort(key=lambda r: r[1])
    fig = plt.figure(figsize=(178 / 25.4, 150 / 25.4))

    ax = fig.add_axes([0.265, 0.070, 0.265, 0.860])
    ys = list(range(len(rows)))
    ax.barh(ys, [r[1] for r in rows], color=ACC, height=0.72, label=L["f3_first"])
    ax.barh(ys, [r[2] for r in rows], left=[r[1] for r in rows], color=WARN, height=0.72, label=L["f3_second"])
    ax.barh(ys, [r[3] for r in rows], left=[r[1] + r[2] for r in rows], color="#D9DEE1", height=0.72,
            label=L["f3_other"])
    ax.axvline(50, color="white", lw=0.6)
    ax.axvline(50, color=GREY, lw=0.5, ls=(0, (1.5, 1.5)))
    ax.set_yticks(ys)
    ax.set_yticklabels([FAM.get(r[0], r[0]) for r in rows], fontsize=7.0)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_xlabel(L["f3_x"], fontsize=8.0)
    ax.legend(fontsize=7.0, frameon=False, loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=3, handlelength=1.0,
              columnspacing=0.9, handletextpad=0.5, borderaxespad=0.0)
    _clean(ax)
    ax.tick_params(axis="y", length=0)
    fig.text(0.01, 0.975, "a", fontsize=10.0, fontweight="bold")

    bx = fig.add_axes([0.79, 0.700, 0.185, 0.230])
    n = summary["families"]
    counts = [n - summary["families_reference_winner_below_half_joint"],
              n - summary["candidate_removal_families_changed"],
              *[summary["rubric_robust_family_counts"][k] for k in ("2", "5", "10")]]
    yb = list(range(len(counts)))
    bx.barh(yb, [n] * len(counts), color="#EEF1F2", height=0.64)
    bx.barh(yb, counts, color=ACC, height=0.64)
    for i, count in enumerate(counts):
        bx.text(count + 0.6, i, str(count), va="center", fontsize=7.5)
    bx.set_yticks(yb)
    bx.set_yticklabels(L["f3_tests"], fontsize=7.5)
    bx.invert_yaxis()
    bx.set_xlim(0, n)
    bx.set_xticks([0, 10, 20, 30])
    bx.set_xlabel(L["f3_b_x"], fontsize=8.0)
    _clean(bx, left=False)
    bx.tick_params(axis="y", length=0)
    fig.text(0.635, 0.975, "b", fontsize=10.0, fontweight="bold")

    flips = []
    for family in study["families"]:
        for removal in family.get("candidate_removal", []):
            if not removal.get("winner_changed"):
                continue
            costs = {row["slug"]: row["summary"]["landed_cost_per_lb"] for row in removal["before"]}
            before, after = family["reference_winner"], removal["renormalized_winner"]
            if before in costs and after in costs:
                flips.append((family["family"], costs[before], costs[after]))
    flips.sort(key=lambda row: row[1] / row[2])

    cx = fig.add_axes([0.80, 0.085, 0.175, 0.415])
    for index, (_family, before, after) in enumerate(flips):
        cx.plot([after, before], [index, index], color=RULE, lw=1.0, zorder=2)
        cx.plot(before, index, "o", color=ACC, mfc="none", ms=5.0, zorder=3)
        cx.plot(after, index, "o", color=WARN, ms=3.0, zorder=4)
    cx.set_yticks(range(len(flips)))
    cx.set_yticklabels([FAM.get(family, family) for family, _b, _a in flips], fontsize=6.8)
    cx.set_ylim(-0.7, len(flips) - 0.3)
    cx.set_xscale("log")
    cx.xaxis.set_major_locator(LogLocator(base=10.0, subs=(1.0,), numticks=8))
    cx.xaxis.set_major_formatter(FuncFormatter(lambda value, _p: f"{value:g}"))
    cx.xaxis.set_minor_formatter(NullFormatter())
    cx.set_xlabel(L["f3_c_x"], fontsize=8.0)
    cx.plot([], [], "o", color=ACC, mfc="none", ms=5, label=L["f3_before"])
    cx.plot([], [], "o", color=WARN, ms=3, label=L["f3_after"])
    cx.legend(fontsize=6.8, frameon=False, loc="lower left", bbox_to_anchor=(0.0, 1.01), ncol=1,
              handlelength=1.0, handletextpad=0.5, borderaxespad=0.0)
    _clean(cx)
    cx.tick_params(axis="y", length=0)
    fig.text(0.635, 0.545, "c", fontsize=10.0, fontweight="bold")
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "docs/paper/figures-note-2026-09-09")
    parser.add_argument("--lang", choices=sorted(TEXT), default="en")
    args = parser.parse_args()
    set_language(args.lang)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    suffix = "" if args.lang == "en" else f".{args.lang}"
    for name, function in (("fig2_cost_model", figure2_cost_model),
                           ("fig3_metal_prices", figure3_metal_prices),
                           ("fig4_decision_diagnostics", figure4_diagnostics)):
        figure = function()
        figure.savefig(args.out_dir / f"{name}{suffix}.png", dpi=400, facecolor="white",
                       metadata={"Software": "COMET"})
        figure.savefig(args.out_dir / f"{name}{suffix}.svg", facecolor="white", metadata={"Date": None})
        plt.close(figure)
        print("wrote", args.out_dir / f"{name}{suffix}")


if __name__ == "__main__":
    main()
