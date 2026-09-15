"""Draw the four Application Note figures from labels and frozen runs.

Figure 1 and the Figure 2(a) schematic use checked PowerPoint exports of the
selected generated artwork. Data panels remain bound to the frozen JSON. Run
scripts/export_note_diagram_slides.ps1 after editing the source decks.
Figure 2 draws the cost model, the cost structure of the cheapest candidate in
every thermal reaction family, and the three published CatCost validation cases against their
published market prices. The trade comparison helper is retained for the audit record.
Figure 3 is the monthly price record of every metal the library prices, in
one column. Figure 4 reads the frozen combined robustness study and the methods supplement.
All four render in English or Korean. Run:

    python scripts/draw_application_note_figures.py --out-dir docs/paper/figures-note-2026-09-09
    python scripts/draw_application_note_figures.py --lang ko
"""

import argparse
import hashlib
import json
import math
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import (  # noqa: E402
    FuncFormatter,
    LogFormatterMathtext,
    LogLocator,
    NullFormatter,
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.paper_units import PER_LB_TO_PER_KG, publication_cost, publication_unit  # noqa: E402

DIAGRAMS = ROOT / "docs/paper/diagram-sources-2026-09-13-h26"
STUDY = ROOT / "docs/paper/robustness-2026-09-08/decision_robustness.json"
METHODS = ROOT / "docs/paper/methods-2026-09-09/methods_study.json"
EXAMPLE = ROOT / "docs/paper/figures-note-2026-09-09/screen_result_ni_al2o3.json"
MARKET = ROOT / "docs/paper/catalyst_market_2026-09-10.json"
FAMILIES = ROOT / "docs/paper/submission-2026-09-08/all_families_2026-09-08.json"
VALIDATION = ROOT / "docs/paper/submission-2026-09-08/table62_reproduction_2026-09-08.json"
HISTORY = ROOT / "docs/paper/submission-2026-09-08/monthly_history_2026-09-08.json"
REFERENCE_MONTH = "2026-05"
INK, MUTED, GREY = "#1F2A30", "#5B6870", "#9AA6AB"
ACC, ACC_MID, WARN = "#1B6F78", "#6FA8AE", "#B8702F"


TEXT = {
    "en": {
        "font": "Arial",
        "share_x": "Share of the selling price (%)",
        "seg_materials": "Materials", "seg_processing": "Processing", "seg_overhead": "Overheads + profit margin + route allowances",
        "total_head": "USD/kg",
        "c_x": "Selling price (USD per kg, log scale)",
        "c_comet": "COMET", "c_published": "Baddour et al. [1]", "c_market": "Published market price",
        "c_y": "Deviation from market price (%)",
        "market_ratio_y": "Estimated price / import unit value",
        "market_titles": {"nickel": "Nickel catalysts", "precious": "Precious-metal catalysts", "other": "Other active substances"},
        "market_traded": "Import unit value (= 1)",
        "market_estimate": "Top-ranked candidates at baseline",
        "unit_lb": "USD/kg",
        "metals_base": "Base metals", "metals_precious": "Precious metals", "metal_price": "Price",
        "f3_first": "Baseline candidate", "f3_second": "Alternative candidate",
        "f3_other": "Other candidates", "f3_x": "Frequency of ranking first (%)",
        "f3_tests": ["First in ≥50%\nof scenarios", "Candidate\nremoval", "Scores ±2",
                     "Scores ±5", "Scores ±10"],
        "f3_b_x": "Reaction families",
        "f3_c_x": "Cost difference (%)",
        "usd_lb": "USD/kg",
    },
    "ko": {
        "font": "Malgun Gothic",
        "share_x": "판매 단가 대비 비율 (%)",
        "seg_materials": "재료비", "seg_processing": "가공비", "seg_overhead": "간접비·판매 마진·경로별 추가 비용",
        "total_head": "USD/kg",
        "c_x": "판매 단가 (USD/kg, 로그 축)",
        "c_comet": "COMET", "c_published": "Baddour 등 [1]", "c_market": "발표된 시장 가격",
        "c_y": "시장 가격 대비 편차 (%)",
        "market_ratio_y": "추정 가격 / 수입 단가",
        "market_titles": {"nickel": "니켈계 촉매", "precious": "귀금속계 촉매", "other": "그 밖의 활성 물질"},
        "market_traded": "수입 단가 (= 1)",
        "market_estimate": "기준 조건의 1위 후보",
        "unit_lb": "USD/kg",
        "metals_base": "비귀금속", "metals_precious": "귀금속", "metal_price": "가격",
        "f3_first": "기준 조건의 1위", "f3_second": "대안 후보",
        "f3_other": "그 밖의 후보", "f3_x": "1위 빈도 (%)",
        "f3_tests": ["시나리오 ≥50%에서\n1위", "후보 제거", "점수 ±2",
                     "점수 ±5", "점수 ±10"],
        "f3_b_x": "반응군 수",
        "f3_c_x": "원가 차이 (%)",
        "usd_lb": "USD/kg",
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

LANG = "en"
L = TEXT["en"]
FAM = FAMILY_NAMES["en"]
VAL = VALIDATION_NAMES["en"]


def set_language(lang):
    global LANG, L, FAM, VAL
    LANG = lang
    L, FAM, VAL = TEXT[lang], FAMILY_NAMES[lang], VALIDATION_NAMES[lang]
    plt.rcParams.update({
        "font.family": L["font"], "font.size": 8.5, "text.color": INK, "svg.fonttype": "none",
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
    ax.tick_params(width=0.5, length=2, labelsize=8.5)


def _diagram_asset(name, kind):
    """Refuse stale exports after a source slide or exported image has changed."""
    manifest = json.loads((DIAGRAMS / "exports.json").read_text(encoding="utf-8"))
    record = next(row for row in manifest["diagrams"] if row["source"] == f"{name}.pptx")
    exported = next(row for row in record["exports"] if row["language"] == LANG)
    for relative, expected in ((record["source"], record["source_sha256"]),
                               (exported[kind], exported[f"{kind}_sha256"])):
        asset = DIAGRAMS / relative
        if hashlib.sha256(asset.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Stale PowerPoint export: {relative}; run scripts/export_note_diagram_slides.ps1")
    return DIAGRAMS / exported[kind]


def _cost_model_panel(fig):
    ax = fig.add_axes([0, 1 - (4 + 178 / 3) / 207, 1, (178 / 3) / 207])
    ax.imshow(plt.imread(_diagram_asset("fig2a_cost_model", "png")), aspect="auto")
    ax.axis("off")


def _save_cost_model_svg(fig, destination):
    """Preserve vector data panels and embed the image-based PowerPoint schematic."""
    panel = fig.axes[0]
    panel.images[0].set_visible(False)
    try:
        fig.savefig(destination, facecolor="white", metadata={"Date": None})
    finally:
        panel.images[0].set_visible(True)
    tree = ET.parse(destination)
    diagram = ET.parse(_diagram_asset("fig2a_cost_model", "svg")).getroot()
    diagram.set("viewBox", f"0 0 {diagram.attrib['width']} {diagram.attrib['height']}")
    position = panel.get_position()
    width, height = fig.get_size_inches() * 72
    for key, value in (("x", position.x0 * width), ("y", (1 - position.y1) * height),
                       ("width", position.width * width), ("height", position.height * height)):
        diagram.set(key, str(value))
    tree.getroot().append(diagram)
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
    svg = ET.tostring(tree.getroot(), encoding="utf-8", xml_declaration=True).decode("utf-8")
    destination.write_text("\n".join(line.rstrip() for line in svg.splitlines()) + "\n", encoding="utf-8")


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
    ax = fig.add_axes([59 / 178, 52 / 207, 104 / 178, 79 / 207])
    ys = range(len(rows))
    ax.barh(ys, [r[2] for r in rows], color=ACC, height=0.74, label=L["seg_materials"])
    ax.barh(ys, [r[3] for r in rows], left=[r[2] for r in rows], color=ACC_MID, height=0.74, edgecolor="white", lw=0.5,
            label=L["seg_processing"])
    ax.barh(ys, [r[4] for r in rows], left=[r[2] + r[3] for r in rows], color="#D9DEE1", height=0.74, edgecolor="white", lw=0.5,
            label=L["seg_overhead"])
    for i, row in enumerate(rows):
        cost = publication_cost(row[1], "$/lb")
        ax.text(104, i, f"{cost:,.2f}" if cost < 100 else f"{cost:,.0f}", va="center", ha="left",
                fontsize=8.5)
    ax.text(104, len(rows) + 0.35, L["total_head"], va="bottom", ha="left", fontsize=8.5, color=MUTED)
    ax.set_yticks(list(ys))
    ax.set_yticklabels([FAM.get(r[0], r[0]) for r in rows], fontsize=8.5)
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.7, len(rows) - 0.3)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_axisbelow(True)
    ax.grid(axis="x", color="#E6EAEC", lw=0.5)
    ax.set_xlabel(L["share_x"], fontsize=9)
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, fontsize=8.5, frameon=False, loc="upper left", bbox_to_anchor=(59 / 178, 139 / 207), ncol=3,
              handlelength=1.0, columnspacing=0.8, handletextpad=0.4, borderaxespad=0.0)
    _clean(ax)
    ax.tick_params(axis="y", length=0, labelsize=8.5)


def _validation_panel(fig):
    """Three aligned paired comparisons on the same market-deviation scale."""
    cases = json.loads(VALIDATION.read_text(encoding="utf-8"))
    comparison_colors = ("#7762A7", "#D99545")
    for index, case in enumerate(cases):
        ax = fig.add_axes([(14 + index * 59) / 178, 13 / 207, 43 / 178, 21 / 207])
        market = case["market"]["market_price_per_lb"]
        estimate = next(r for r in case["rows"] if r["key"] == "estimated_price_per_lb")
        ours = case.get("with_published_rate", {}).get("estimated_price_per_lb", estimate["comet"])
        values = [100 * (ours - market) / market, 100 * (estimate["published"] - market) / market]
        for y, value, color, label in zip((1, 0), values, comparison_colors,
                                          (L["c_comet"], L["c_published"]), strict=True):
            ax.barh(y, value, height=0.52, color=color, label=label)
            ax.text(value - 0.65, y, f"{value:.1f}", ha="right", va="center", fontsize=8.5)
        ax.set_xlim(-30, 0)
        ax.set_ylim(-0.65, 1.65)
        ax.set_xticks([-20, -10, 0])
        ax.set_yticks([])
        title = VAL.get(case["name"], case["name"]).replace("\n", " ")
        ax.set_title(title, fontsize=9, pad=5)
        _clean(ax)
        if index == 0:
            handles, labels = ax.get_legend_handles_labels()
            fig.legend(handles, labels, frameon=False, fontsize=8.5, ncol=2,
                       loc="upper right", bbox_to_anchor=(0.97, 43 / 207), borderaxespad=0,
                       handlelength=1.0, handletextpad=0.5, columnspacing=1.4)
    fig.text(0.5, 1.8 / 207, L["c_y"], fontsize=9, ha="center", va="bottom")


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
    """Retained audit comparison with trade unit values; excluded from the note figures."""
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


METAL_COLOURS = (ACC, WARN, "#687C38", "#9B6686", "#69747D", "#408FB0", "#303D45")
METAL_STYLES = ("-", "--", "-", "--", "-", "-.", ":")


def _label_ends(ax, ends, fontsize=8.5):
    """The element symbol at the end of each line, pushed apart where lines converge."""
    low, high = ax.get_ylim()
    height_pt = ax.get_position().height * ax.figure.get_size_inches()[1] * 72
    step = (math.log10(high) - math.log10(low)) * fontsize * 1.3 / height_pt
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
                ha="left", va="center", fontsize=fontsize, color=INK)


def figure2_cost_model():
    fig = plt.figure(figsize=(178 / 25.4, 207 / 25.4))
    _cost_model_panel(fig)
    _structure_panel(fig)
    _validation_panel(fig)
    for label, top in (("(b)", 67), ("(c)", 164)):
        fig.text(0.012, 1 - top / 207, label, fontsize=10, fontweight="bold", va="top")
    return fig


def figure3_metal_prices():
    """The monthly price record of every metal the library prices, in one column.

    Colours, line styles and endpoint labels distinguish the unsmoothed observations.
    """
    series = json.loads(HISTORY.read_text(encoding="utf-8"))["series"]
    fig = plt.figure(figsize=(84 / 25.4, 122 / 25.4))
    for index, (symbols, title) in enumerate(((PRECIOUS_METALS, L["metals_precious"]),
                                              (BASE_METALS, L["metals_base"]))):
        ax = fig.add_axes([0.23, 0.565 - index * 0.475, 0.59, 0.35])
        ends = []
        for order, symbol in enumerate(symbols):
            points = series[symbol]["points"]
            prices = [publication_cost(point["price"], series[symbol]["unit"]) for point in points]
            colour = METAL_COLOURS[order]
            ax.plot([datetime.strptime(point["date"], "%Y-%m-%d") for point in points], prices,
                    color=colour, lw=1.05, ls=METAL_STYLES[order], solid_capstyle="round")
            ends.append((prices[-1], symbol, colour, datetime.strptime(points[-1]["date"], "%Y-%m-%d")))
        ax.set_yscale("log")
        ax.set_xlim(datetime(2019, 1, 1), datetime(2026, 6, 1))
        ax.xaxis.set_major_locator(mdates.YearLocator(2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.yaxis.set_major_locator(LogLocator(base=10.0, subs=(1.0, 3.0), numticks=10))
        ax.yaxis.set_major_formatter(LogFormatterMathtext(labelOnlyBase=True) if index == 0
                                    else FuncFormatter(lambda value, _p: f"{value:g}"))
        ax.yaxis.set_minor_formatter(NullFormatter())
        ax.set_title(title, loc="left", fontsize=9, fontweight="bold", pad=6)
        ax.set_axisbelow(True)
        ax.grid(axis="y", which="major", color="#E6EAEC", lw=0.5)
        unit = "USD/kg"
        ax.set_ylabel(f"{L['metal_price']} ({unit})", fontsize=8.5)
        _clean(ax)
        _label_ends(ax, ends)
        fig.text(0.015, 0.935 - index * 0.475, f"({'ab'[index]})", fontsize=10, fontweight="bold")
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
    fig = plt.figure(figsize=(178 / 25.4, 203 / 25.4))

    ax = fig.add_axes([59 / 178, 83 / 203, 112 / 178, 105 / 203])
    ys = list(range(len(rows)))
    ax.barh(ys, [r[1] for r in rows], color=ACC, height=0.72, label=L["f3_first"])
    ax.barh(ys, [r[2] for r in rows], left=[r[1] for r in rows], color=WARN, height=0.72, edgecolor="white", lw=0.5, label=L["f3_second"])
    ax.barh(ys, [r[3] for r in rows], left=[r[1] + r[2] for r in rows], color="#D9DEE1", height=0.72, edgecolor="white", lw=0.5,
            label=L["f3_other"])
    ax.axvline(50, color="white", lw=0.6)
    ax.axvline(50, color=GREY, lw=0.5, ls=(0, (1.5, 1.5)))
    ax.set_yticks(ys)
    ax.set_yticklabels([FAM.get(r[0], r[0]) for r in rows], fontsize=8.5)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_xlabel(L["f3_x"], fontsize=9)
    ax.legend(fontsize=8.5, frameon=False, loc="lower left", bbox_to_anchor=(0.0, 1.035), ncol=3, handlelength=1.0,
              columnspacing=0.9, handletextpad=0.5, borderaxespad=0.0)
    _clean(ax)
    ax.tick_params(axis="y", length=0)
    fig.text(0.012, 0.985, "(a)", fontsize=10, fontweight="bold", va="top")

    bx = fig.add_axes([37 / 178, 13 / 203, 38 / 178, 47 / 203])
    n = summary["families"]
    counts = [n - summary["families_reference_winner_below_half_joint"],
              n - summary["candidate_removal_families_changed"],
              *[summary["rubric_robust_family_counts"][k] for k in ("2", "5", "10")]]
    yb = list(range(len(counts)))
    bx.barh(yb, [n] * len(counts), color="#EEF1F2", height=0.64)
    bx.barh(yb, counts, color=ACC, height=0.64)
    for i, count in enumerate(counts):
        bx.text(count + 0.6, i, str(count), va="center", fontsize=8.5)
    bx.set_yticks(yb)
    bx.set_yticklabels(L["f3_tests"], fontsize=8.5)
    bx.invert_yaxis()
    bx.set_xlim(0, n)
    bx.set_xticks([0, 10, 20, 30])
    bx.set_xlabel(L["f3_b_x"], fontsize=9)
    _clean(bx, left=False)
    bx.tick_params(axis="y", length=0)
    fig.text(0.012, 69 / 203, "(b)", fontsize=10, fontweight="bold", va="top")

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

    cx = fig.add_axes([134 / 178, 13 / 203, 40 / 178, 47 / 203])
    for index, (_family, before, after) in enumerate(flips):
        difference = 100 * (after - before) / before
        cx.barh(index, difference, height=0.58, color=ACC, edgecolor=ACC, lw=0.5)
        cx.text(difference - 2, index, f"{difference:.1f}", ha="right", va="center", fontsize=8.5)
    cx.set_yticks(range(len(flips)))
    cx.set_yticklabels([FAM.get(family, family) for family, _b, _a in flips], fontsize=8.5)
    cx.set_ylim(-0.7, len(flips) - 0.3)
    cx.set_xlim(-130, 0)
    cx.set_xticks([-100, -50, 0])
    cx.set_xlabel(L["f3_c_x"], fontsize=9)
    _clean(cx)
    cx.tick_params(axis="y", length=0)
    fig.text(0.51, 69 / 203, "(c)", fontsize=10, fontweight="bold", va="top")
    return fig


def _crossover_axis(ax):
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.65)
        spine.set_color(INK)
    ax.tick_params(labelsize=9, direction="out", length=3, width=0.65)
    ax.grid(axis="y", color="#E6EAEC", lw=0.45)
    ax.set_axisbelow(True)


def _crossover_dates(records):
    return [datetime.fromisoformat(row["date"] + ("-15" if len(row["date"]) == 7 else "")) for row in records]


def figure_price_crossovers(study, mechanisms, lang="en"):
    """Three thermal cost histories and the conditional Ni–Co boundary."""
    families = {f["family"]: f for f in study["families"]}
    fig, axes = plt.subplots(2, 2, figsize=(178 / 25.4, 171 / 25.4))
    fig.subplots_adjust(left=0.105, right=0.985, bottom=0.085, top=0.95, wspace=0.31, hspace=0.56)
    colors = (ACC, WARN, "#7A6A8B")
    cases = [
        ("ammonia-cracking", [("co-mgo-la2o3", "Co/Mg–La"), ("ni-alumina-baseline", "Ni/Al$_2$O$_3$")]),
        ("dry-reforming", [("ni-co-almgo", "Ni–Co/Al–Mg"), ("ni-zeolite-stable", "Ni/zeolite"),
                           ("ni-single-atom-ceria", "Ni/CeO$_2$")]),
        ("water-gas-shift", [("cu-zno-baseline", "Cu–ZnO"), ("fe-cr-hts", "Fe–Cr")]),
    ]
    for index, (family, series) in enumerate(cases):
        ax = axes.flat[index]
        records = families[family]["periods"]["monthly"]["records"]
        values = []
        for i, (slug, label) in enumerate(series):
            costs = [publication_cost(r["costs"][slug], families[family]["unit"]) for r in records]
            values.extend(costs)
            ax.plot(_crossover_dates(records), costs, color=colors[i], lw=1.45,
                    ls=("-", "--", "-.")[i], label=label)
        low, high = min(values), max(values)
        ax.set_ylim(low - (high - low) * 0.12, high + (high - low) * 0.4)
        ax.set_xlim(datetime(2019, 1, 1), datetime(2026, 7, 1))
        ax.xaxis.set_major_locator(mdates.YearLocator(2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.set_ylabel("Cost (USD/kg)" if lang == "en" else "원가 (USD/kg)", fontsize=10)
        ax.set_title(f"({chr(97 + index)}) {FAMILY_NAMES[lang][family]}", loc="left", fontsize=10.5, pad=10)
        ax.legend(loc="upper left", frameon=False, fontsize=9, handlelength=1.6, labelspacing=0.28,
                  borderpad=0.2)
        _crossover_axis(ax)
    ax = axes.flat[3]
    boundary = mechanisms["ammonia_boundary"]
    factor = PER_LB_TO_PER_KG
    x = [p["Ni"] * factor for p in boundary["points"]]
    y = [p["Co_threshold"] * factor for p in boundary["points"]]
    ax.fill_between(x, 5 * factor, y, color=ACC, alpha=0.07)
    ax.fill_between(x, y, 42 * factor, color=WARN, alpha=0.07)
    ax.plot(x, y, color=INK, lw=1.1)
    monthly = families["ammonia-cracking"]["periods"]["monthly"]["records"]
    for point, row in zip(boundary["observations"], monthly, strict=True):
        color = ACC if row["cost_winner"] == "co-mgo-la2o3" else WARN
        ax.scatter(point["Ni"] * factor, point["Co"] * factor, s=12, c=color, alpha=0.65, linewidths=0.25, edgecolors="white")
    selected = {p["date"]: {"Ni": p["Ni"] * factor, "Co": p["Co"] * factor}
                for p in boundary["observations"] if p["date"] in ("2025-09", "2025-10")}
    for day, point in selected.items():
        ax.scatter(point["Ni"], point["Co"], s=38, marker="D", facecolor="white", edgecolor=INK, lw=0.8, zorder=5)
        ax.annotate(day, (point["Ni"], point["Co"]), xytext=(9, -17 if day == "2025-09" else 8),
                    textcoords="offset points", fontsize=8.8, color=INK)
    ax.annotate("", xy=(selected["2025-10"]["Ni"], selected["2025-10"]["Co"]),
                xytext=(selected["2025-09"]["Ni"], selected["2025-09"]["Co"]),
                arrowprops={"arrowstyle": "->", "lw": 0.9, "color": INK})
    ax.text(0.04, 0.90, "Ni/Al$_2$O$_3$", color=WARN, fontsize=10, transform=ax.transAxes)
    ax.text(0.55, 0.08, "Co/Mg–La", color=ACC, fontsize=10, transform=ax.transAxes)
    ax.set_xlim(4 * factor, 16 * factor)
    ax.set_ylim(5 * factor, 42 * factor)
    ax.set_xlabel("Ni (USD/kg)", fontsize=10)
    ax.set_ylabel("Co (USD/kg)", fontsize=10)
    ax.set_title("(d) Ammonia cost boundary" if lang == "en" else "(d) 암모니아 분해 원가 경계",
                 loc="left", fontsize=10.5, pad=10)
    _crossover_axis(ax)
    return fig


def figure_daily_crossovers(study, lang="en"):
    families = {f["family"]: f for f in study["families"]}
    fig, axes = plt.subplots(2, 1, figsize=(178 / 25.4, 145 / 25.4))
    fig.subplots_adjust(left=0.11, right=0.98, bottom=0.08, top=0.89, hspace=0.55)
    cases = [("photocatalytic-water-splitting", "pt-tio2-cocatalyst", "tio2-anatase-baseline", "Pt/TiO$_2$ $-$ TiO$_2$"),
             ("co-prox", "pt-fe-alumina", "cuo-ceo2", "Pt–Fe/Al$_2$O$_3$ $-$ CuO/CeO$_2$")]
    for i, (family, a, b, label) in enumerate(cases):
        ax = axes[i]
        rows = families[family]["periods"]["daily"]["records"]
        days = _crossover_dates(rows)
        continuous = [r["continuous_scores"][a] - r["continuous_scores"][b] for r in rows]
        app = [r["scores"][a]["total"] - r["scores"][b]["total"] for r in rows]
        ax.plot(days, continuous, color=ACC, lw=1.7, label="Fixed nonprice scores" if lang == "en" else "비가격 점수 고정")
        ax.plot(days, app, color=WARN, lw=1.1, ls="--", label="Application score" if lang == "en" else "앱 점수")
        ax.axhline(0, color=INK, lw=0.8)
        ax.fill_between(days, continuous, 0, where=[v < 0 for v in continuous], color=WARN, alpha=0.12)
        ax.set_xlim(datetime(2026, 1, 1), datetime(2026, 9, 15))
        ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1, 3, 5, 7, 9)))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        ax.set_ylabel("Score difference" if lang == "en" else "점수 차이", fontsize=10)
        title = FAMILY_NAMES[lang][family].replace("\n", " ")
        ax.set_title(f"({chr(97 + i)}) {title}", fontsize=10.5, loc="left", pad=10)
        ax.text(1, 1.05, label, ha="right", transform=ax.transAxes, fontsize=9.5)
        _crossover_axis(ax)
    fig.legend(*axes[0].get_legend_handles_labels(), loc="upper center", ncol=2, frameon=False,
               fontsize=10, bbox_to_anchor=(0.55, 0.985))
    return fig


def figure_crossover_atlas(study, lang="en"):
    import numpy as np
    from matplotlib.colors import ListedColormap

    families = sorted(study["families"], key=lambda f: (f["domain"] != "thermal", f["family"]))
    fig, axes = plt.subplots(1, 2, figsize=(178 / 25.4, 222 / 25.4), sharey=True)
    fig.subplots_adjust(left=0.44, right=0.98, top=0.93, bottom=0.045, wspace=0.2)
    keys = ("cost_winner", "app_winner", "continuous_winner")
    for ax, period, letter in zip(axes, ("monthly", "daily"), ("a", "b"), strict=True):
        values = np.array([[len(f["periods"][period]["summary"]["transitions"][key]) for key in keys] for f in families])
        ax.imshow(values > 0, cmap=ListedColormap(["#F1F3F4", "#D1E3E5"]), aspect="auto", vmin=0, vmax=1)
        for y in range(len(families)):
            for x in range(3):
                ax.text(x, y, str(values[y, x]), ha="center", va="center", fontsize=9.5,
                        color=INK if values[y, x] else GREY, fontweight="bold" if values[y, x] else "normal")
        ax.set_xticks(range(3), ["Cost", "App", "Fixed"] if lang == "en" else ["원가", "앱", "고정"])
        ax.xaxis.tick_top()
        ax.tick_params(axis="x", labelsize=10, length=0, pad=5)
        ax.set_yticks(range(len(families)))
        ax.tick_params(axis="y", length=0, pad=9)
        ax.set_title(f"({letter}) " + ({"monthly": "Monthly", "daily": "Daily"}[period] if lang == "en"
                                      else {"monthly": "월별", "daily": "일별"}[period]), fontsize=11, pad=28)
        for y in range(1, len(families)):
            ax.axhline(y - 0.5, color="white", lw=0.5)
        ax.axhline(22.5, color=GREY, lw=1)
        for spine in ax.spines.values():
            spine.set_visible(False)
    axes[0].set_yticklabels([FAMILY_NAMES[lang][f["family"]].replace("\n", " ") for f in families], fontsize=9)
    return fig


def draw_crossovers(directory, out, lang):
    """New research figures; preserve the four currently embedded paper figures."""
    from matplotlib.backends.backend_pdf import PdfPages

    study = json.loads((directory / "price_crossovers.json").read_text(encoding="utf-8"))
    mechanisms = json.loads((directory / "crossover_mechanisms.json").read_text(encoding="utf-8"))
    if hashlib.sha256((directory / "price_crossovers.json").read_bytes()).hexdigest() != mechanisms["study_sha256"]:
        raise ValueError("Crossover study and mechanism analysis do not match")
    plt.rcParams.update({"font.size": 10, "svg.fonttype": "none", "svg.hashsalt": "COMET-price-crossovers"})
    suffix = "" if lang == "en" else ".ko"
    figures = [("fig_price_crossovers", figure_price_crossovers(study, mechanisms, lang)),
               ("fig_daily_rank_changes", figure_daily_crossovers(study, lang)),
               ("fig_crossover_atlas", figure_crossover_atlas(study, lang))]
    layout_checks = []

    def check_layout(fig, name):
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        width, height = fig.canvas.get_width_height()
        texts = list(fig.texts)
        for ax in fig.axes:
            texts.extend([ax.title, ax._left_title, ax.xaxis.label, ax.yaxis.label])
        for legend in [*fig.legends, *[ax.get_legend() for ax in fig.axes if ax.get_legend()]]:
            texts.extend(legend.get_texts())
        for text in texts:
            if not text.get_text():
                continue
            box = text.get_window_extent(renderer)
            if box.x0 < -1 or box.y0 < -1 or box.x1 > width + 1 or box.y1 > height + 1:
                raise ValueError(f"{name}: text outside figure: {text.get_text()}")
        layout_checks.append({"figure": name, "checked_titles_labels_legend": len(texts), "within_canvas": True})

    for name, fig in figures:
        check_layout(fig, name)
        for extension in ("png", "svg", "pdf"):
            metadata = {"Software": "COMET"} if extension == "png" else ({"Date": None} if extension == "svg"
                                                                                 else {"Creator": "COMET", "CreationDate": None, "ModDate": None})
            fig.savefig(out / f"{name}{suffix}.{extension}", dpi=400, facecolor="white", metadata=metadata)
            if extension == "svg":
                path = out / f"{name}{suffix}.svg"
                svg = path.read_text(encoding="utf-8")
                path.write_text("\n".join(line.rstrip() for line in svg.splitlines()) + "\n", encoding="utf-8")
        plt.close(fig)
        print("wrote", out / f"{name}{suffix}")
    with PdfPages(out / f"all_candidate_costs{suffix}.pdf", metadata={"Creator": "COMET", "CreationDate": None, "ModDate": None}) as pdf:
        for family in study["families"]:
            fig, axes = plt.subplots(1, 2, figsize=(178 / 25.4, 116 / 25.4))
            fig.subplots_adjust(left=0.15, right=0.98, top=0.82, bottom=0.34, wspace=0.50)
            fig.suptitle(FAMILY_NAMES[lang][family["family"]].replace("\n", " "), fontsize=12, y=0.98)
            for ax, period in zip(axes, ("monthly", "daily"), strict=True):
                rows = family["periods"][period]["records"]
                for i, slug in enumerate(family["candidates"]):
                    ax.plot(_crossover_dates(rows), [publication_cost(r["costs"][slug], family["unit"]) for r in rows], lw=1.25,
                            color=(ACC, WARN, "#7A6A8B", GREY)[i], ls=("-", "--", "-.", ":")[i],
                            label=slug)
                ax.set_yscale("log")
                unit = publication_unit(family["unit"]).replace("$", "USD")
                ax.set_ylabel(("Cost" if lang == "en" else "원가") + " (" + unit + ")", fontsize=9.5)
                ax.set_title(("Monthly" if period == "monthly" else "Daily") if lang == "en" else ("월별" if period == "monthly" else "일별"), fontsize=10)
                ax.xaxis.set_major_locator(mdates.YearLocator(2) if period == "monthly" else mdates.MonthLocator(bymonth=(1, 5, 9)))
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y" if period == "monthly" else "%b %Y"))
                _crossover_axis(ax)
            fig.legend(*axes[0].get_legend_handles_labels(), loc="lower left", bbox_to_anchor=(0.08, 0.015),
                       frameon=False, fontsize=9.2, ncol=1, labelspacing=0.7)
            check_layout(fig, family["family"])
            pdf.savefig(fig, facecolor="white")
            plt.close(fig)
    (out / f"layout_checks{suffix}.json").write_text(json.dumps(layout_checks, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "docs/paper/figures-note-2026-09-09")
    parser.add_argument("--lang", choices=sorted(TEXT), default="en")
    parser.add_argument("--crossovers", type=Path, help="Separate frozen price-crossover study directory")
    args = parser.parse_args()
    set_language(args.lang)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    if args.crossovers:
        draw_crossovers(args.crossovers, args.out_dir, args.lang)
        return
    suffix = "" if args.lang == "en" else f".{args.lang}"
    for kind in ("png", "svg"):
        shutil.copyfile(_diagram_asset("fig1_workflow", kind), args.out_dir / f"fig1_workflow_stack{suffix}.{kind}")
    print("wrote", args.out_dir / f"fig1_workflow_stack{suffix}")
    for name, function in (("fig2_cost_model", figure2_cost_model),
                           ("fig3_metal_prices", figure3_metal_prices),
                           ("fig4_decision_diagnostics", figure4_diagnostics)):
        figure = function()
        figure.savefig(args.out_dir / f"{name}{suffix}.png", dpi=400, facecolor="white",
                       metadata={"Software": "COMET"})
        svg_path = args.out_dir / f"{name}{suffix}.svg"
        if name == "fig2_cost_model":
            _save_cost_model_svg(figure, svg_path)
        else:
            figure.savefig(svg_path, facecolor="white", metadata={"Date": None})
            svg = svg_path.read_text(encoding="utf-8")
            svg_path.write_text("\n".join(line.rstrip() for line in svg.splitlines()) + "\n", encoding="utf-8")
        plt.close(figure)
        print("wrote", args.out_dir / f"{name}{suffix}")


if __name__ == "__main__":
    main()
