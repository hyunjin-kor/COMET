"""Draw Application Note Figures 2 and 3 from repository assets and frozen runs.

Figure 1 is an AI-assisted illustration kept as a committed PNG with its raw file, provenance
note and the connector-line script (scripts/straighten_note_fig1_leaders.py), so it is not
drawn here. Figure 2 draws the cost model, the cost structure of the lowest-cost candidate in
every thermal reaction family, the three published CatCost validation cases against their
published market prices, and the price basis of eight metals. Figure 3 reads the frozen
combined robustness study and the methods supplement. Both figures render in English or
Korean. Run:

    python scripts/draw_application_note_figures.py --out-dir docs/paper/figures-note-2026-09-09
    python scripts/draw_application_note_figures.py --lang ko
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
FAMILIES = ROOT / "docs/paper/submission-2026-09-08/all_families_2026-09-08.json"
VALIDATION = ROOT / "docs/paper/submission-2026-09-08/table62_reproduction_2026-09-08.json"
REFERENCE_MONTH = "2026-05"
INK, MUTED, RULE, GREY = "#1F2A30", "#5B6870", "#C3CBCE", "#9AA6AB"
FILL, ACC, ACC_MID, WARN = "#F4F6F7", "#1B6F78", "#6FA8AE", "#B8702F"

METALS = ["Pt", "Pd", "Rh", "Ru", "Ir", "Au", "Ag", "Ni"]

TEXT = {
    "en": {
        "font": "Arial",
        "formulation": "Formulation", "formulation_sub": "components, wt%",
        "route": "Preparation route", "route_sub": "operations, order size",
        "basis": "Price basis", "basis_sub": "spot or reference month",
        "materials": "Materials", "materials_1": "unit price × mass fraction",
        "materials_2": "purchased input: a = w/(f·p·y)",
        "processing": "Processing (Step Method)", "processing_1": "hourly rates at the fitted scale class",
        "processing_2": "campaign time, index escalation, mass produced",
        "overhead": "Overhead and margin", "overhead_1": "G&A, S&ARD, margin set by order size",
        "breakdown": "Cost breakdown",
        "breakdown_lines": ["selling price per lb", "price, source, date", "grade, price basis",
                            "operations priced,", "substituted, uncosted"],
        "share_x": "Share of the selling price (%)",
        "seg_materials": "Materials", "seg_processing": "Processing", "seg_overhead": "Overhead and margin",
        "total_head": "USD/lb",
        "b_note": "Lowest-cost candidate in each thermal reaction family, reference month 2026-05",
        "c_x": "Selling price (USD per lb, log scale)",
        "c_comet": "COMET", "c_published": "Published estimate", "c_market": "Published market price",
        "c_note": "CatCost User Guide Table 6.2; the FCC case uses\nthe footnote rate of 67 short tons per day",
        "d_note": ("Monthly averages 2019-01 to 2026-07; shaded: 89-month repricing window\n"
                   "teal: reference basis (2026-05 monthly average); orange: spot quote in the fixed price package"),
        "metal_names": {"Pt": "Platinum", "Pd": "Palladium", "Rh": "Rhodium", "Ru": "Ruthenium",
                        "Ir": "Iridium", "Au": "Gold", "Ag": "Silver", "Ni": "Nickel"},
        "unit_oz": "USD/troy oz", "unit_lb": "USD/lb",
        "f3_first": "Ranked first at reference conditions", "f3_second": "Closest competitor",
        "f3_other": "Other candidates", "f3_x": "Cases in which the candidate ranks first (%)",
        "f3_tests": ["Majority of cases", "Any one candidate removed", "Scores moved ±2 points",
                     "Scores moved ±5 points", "Scores moved ±10 points"],
        "f3_b_x": "Families keeping the same leader (of 30)",
        "f3_c_x": "Composite score", "f3_full": "Full candidate set", "f3_removed": "Ru candidate removed",
        "f3_first_tag": " (1st)", "usd_lb": "USD/lb",
    },
    "ko": {
        "font": "Malgun Gothic",
        "formulation": "조성", "formulation_sub": "성분, wt%",
        "route": "제조 경로", "route_sub": "공정, 주문 규모",
        "basis": "가격 기준", "basis_sub": "현물 또는 기준월",
        "materials": "재료비", "materials_1": "단가 × 질량 분율",
        "materials_2": "구매 원료: a = w/(f·p·y)",
        "processing": "가공비 (Step Method)", "processing_1": "맞춰진 규모 등급의 시간당 단가",
        "processing_2": "캠페인 시간, 지수 보정, 생산 질량",
        "overhead": "간접비와 마진", "overhead_1": "일반관리비, 판매·연구개발, 주문 규모별 마진",
        "breakdown": "원가 내역",
        "breakdown_lines": ["파운드당 판매 단가", "가격, 출처, 일자", "등급, 가격 기준",
                            "산정·대체·", "미산정 공정"],
        "share_x": "판매 단가 대비 비율 (%)",
        "seg_materials": "재료비", "seg_processing": "가공비", "seg_overhead": "간접비와 마진",
        "total_head": "USD/lb",
        "b_note": "각 열촉매 반응군의 최저 원가 후보, 기준월 2026-05",
        "c_x": "판매 단가 (USD/lb, 로그 축)",
        "c_comet": "COMET", "c_published": "발표된 추정값", "c_market": "발표된 시장 가격",
        "c_note": "CatCost 사용자 안내 표 6.2\nFCC 사례는 각주의 일 67 short ton 처리량 기준",
        "d_note": ("2019-01~2026-07 월평균, 음영은 89개월 재산정 구간\n"
                   "청록: 기준월(2026-05) 평균, 주황: 고정 가격 묶음의 현물 시세"),
        "metal_names": {"Pt": "백금", "Pd": "팔라듐", "Rh": "로듐", "Ru": "루테늄",
                        "Ir": "이리듐", "Au": "금", "Ag": "은", "Ni": "니켈"},
        "unit_oz": "USD/트로이온스", "unit_lb": "USD/lb",
        "f3_first": "기준 조건 1위 후보", "f3_second": "가장 가까운 경쟁 후보",
        "f3_other": "나머지 후보", "f3_x": "후보가 1위를 차지한 경우의 비율 (%)",
        "f3_tests": ["과반 경우에서 유지", "후보 하나 제외", "점수 ±2점 이동",
                     "점수 ±5점 이동", "점수 ±10점 이동"],
        "f3_b_x": "1위가 유지되는 반응군 수 (30개 중)",
        "f3_c_x": "종합 점수", "f3_full": "전체 후보 집합", "f3_removed": "Ru 후보 제외",
        "f3_first_tag": " (1위)", "usd_lb": "USD/lb",
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
    "en": {"2 wt% Pt/C": "2 wt% Pt/C", "21 wt% Ni/Al2O3": "21 wt% Ni/Al$_2$O$_3$",
           "USY-based FCC (with RE)": "USY FCC"},
    "ko": {"2 wt% Pt/C": "2 wt% Pt/C", "21 wt% Ni/Al2O3": "21 wt% Ni/Al$_2$O$_3$",
           "USY-based FCC (with RE)": "USY FCC"},
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
        "mathtext.fontset": "custom", "mathtext.rm": L["font"], "mathtext.it": f"{L['font']}:italic",
        "mathtext.bf": f"{L['font']}:bold",
    })


def _clean(ax, left=True):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    if not left:
        ax.spines["left"].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_linewidth(0.5)
    ax.tick_params(width=0.5, length=2, labelsize=6)


def _box(ax, x, y, w, h, fill=FILL, edge=RULE, lw=0.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.8", fc=fill, ec=edge, lw=lw))


def _arrow(ax, x1, y1, x2, y2, color=INK, label=None, dy=1.6):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=6, color=color, lw=0.7,
                                 shrinkA=0, shrinkB=0, zorder=4))
    if label:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + dy, label, ha="center", va="bottom", fontsize=6.4, color=INK)


def _cost_model_panel(fig):
    ax = fig.add_axes([0, 0.795, 1, 0.205])
    ax.set_xlim(0, 178)
    ax.set_ylim(0, 47)
    ax.axis("off")
    for title, sub, y in ((L["formulation"], L["formulation_sub"], 35.5),
                          (L["route"], L["route_sub"], 20),
                          (L["basis"], L["basis_sub"], 4.5)):
        _box(ax, 6, y, 26, 9.6)
        ax.text(19, y + 6.4, title, ha="center", va="center", fontsize=6.6, fontweight="bold")
        ax.text(19, y + 2.7, sub, ha="center", va="center", fontsize=5.6, color=MUTED)
    mx, mw = 38, 57
    _box(ax, mx, 24.5, mw, 21, fill="white", edge=INK, lw=0.6)
    ax.text(mx + mw / 2, 42.2, L["materials"], ha="center", va="center", fontsize=6.8, fontweight="bold")
    ax.text(mx + mw / 2, 35.0, r"$C_\mathrm{m}=\sum_i w_i\,c_i$", ha="center", va="center", fontsize=8.6)
    ax.text(mx + mw / 2, 29.6, L["materials_1"], ha="center", va="center", fontsize=5.6)
    ax.text(mx + mw / 2, 26.6, L["materials_2"], ha="center", va="center", fontsize=5.6)
    _box(ax, mx, 1.0, mw, 21, fill="white", edge=INK, lw=0.6)
    ax.text(mx + mw / 2, 18.7, L["processing"], ha="center", va="center", fontsize=6.8, fontweight="bold")
    ax.text(mx + mw / 2, 11.5, r"$C_\mathrm{p}=24\,T\,I\,\sum_j H_j\,/\,M$", ha="center", va="center", fontsize=8.6)
    ax.text(mx + mw / 2, 6.1, L["processing_1"], ha="center", va="center", fontsize=5.6)
    ax.text(mx + mw / 2, 3.1, L["processing_2"], ha="center", va="center", fontsize=5.6)
    _arrow(ax, 32.3, 40.3, mx - 0.3, 38.5)
    _arrow(ax, 32.3, 9.3, mx - 0.3, 11.5)
    _arrow(ax, 32.3, 24.8, mx - 0.3, 31.5)
    _arrow(ax, 32.3, 24.8, mx - 0.3, 15.5)
    px, pw = 101, 40
    _box(ax, px, 11, pw, 24, fill="white", edge=INK, lw=0.6)
    ax.text(px + pw / 2, 31.7, L["overhead"], ha="center", va="center", fontsize=6.8, fontweight="bold")
    ax.text(px + pw / 2, 22.5, r"$P=\dfrac{(C_\mathrm{m}+C_\mathrm{p})(1+g)(1+s)}{1-m}$", ha="center", va="center",
            fontsize=8.6)
    ax.text(px + pw / 2, 14.1, L["overhead_1"], ha="center", va="center", fontsize=5.6)
    _arrow(ax, mx + mw + 0.3, 35.0, px - 0.3, 27.0, label=r"$C_\mathrm{m}$")
    _arrow(ax, mx + mw + 0.3, 11.5, px - 0.3, 19.0, label=r"$C_\mathrm{p}$", dy=-4.6)
    lx, lw_ = 147, 28
    _box(ax, lx, 11, lw_, 24, fill="#EAF1F2", edge=ACC, lw=0.6)
    ax.text(lx + lw_ / 2, 31.7, L["breakdown"], ha="center", va="center", fontsize=6.8, fontweight="bold")
    for k, line_text in enumerate(L["breakdown_lines"]):
        ax.text(lx + 2.2, 27.3 - k * 3.6, line_text, ha="left", va="center", fontsize=5.5)
    _arrow(ax, px + pw + 0.3, 23.0, lx - 0.3, 23.0, label=r"$P$")


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
    ax = fig.add_axes([0.205, 0.415, 0.295, 0.325])
    ys = range(len(rows))
    ax.barh(ys, [r[2] for r in rows], color=ACC, height=0.74, label=L["seg_materials"])
    ax.barh(ys, [r[3] for r in rows], left=[r[2] for r in rows], color=ACC_MID, height=0.74,
            label=L["seg_processing"])
    ax.barh(ys, [r[4] for r in rows], left=[r[2] + r[3] for r in rows], color="#D9DEE1", height=0.74,
            label=L["seg_overhead"])
    for i, row in enumerate(rows):
        ax.text(104, i, f"{row[1]:,.2f}" if row[1] < 100 else f"{row[1]:,.0f}", va="center", ha="left",
                fontsize=5.0)
    ax.text(104, len(rows) - 0.1, L["total_head"], va="bottom", ha="left", fontsize=5.0, color=MUTED)
    ax.set_yticks(list(ys))
    ax.set_yticklabels([FAM.get(r[0], r[0]) for r in rows], fontsize=5.2)
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.7, len(rows) - 0.3)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel(L["share_x"], fontsize=6.2)
    ax.legend(fontsize=5.4, frameon=False, loc="lower left", bbox_to_anchor=(-0.66, 1.015), ncol=3,
              handlelength=1.0, columnspacing=0.8, handletextpad=0.4, borderaxespad=0.0)
    _clean(ax)
    ax.tick_params(axis="y", length=0, labelsize=5.2)
    fig.text(0.04, 0.366, L["b_note"], fontsize=5.2, color=MUTED)


def _validation_panel(fig):
    """The three published CatCost cases against the market prices published beside them."""
    cases = json.loads(VALIDATION.read_text(encoding="utf-8"))
    ax = fig.add_axes([0.735, 0.50, 0.245, 0.215])
    ys = list(range(len(cases)))[::-1]
    for y, case in zip(ys, cases, strict=True):
        published = next(r for r in case["rows"] if r["key"] == "estimated_price_per_lb")["published"]
        comet = case.get("with_published_rate", {}).get("estimated_price_per_lb")
        comet = comet if comet is not None else next(
            r for r in case["rows"] if r["key"] == "estimated_price_per_lb")["comet"]
        market = case["market"]["market_price_per_lb"]
        ax.plot([min(comet, market), max(comet, market)], [y, y], color=RULE, lw=1.0, zorder=2)
        ax.plot(published, y, "o", mfc="white", mec=GREY, mew=1.0, ms=7.0, zorder=3)
        ax.plot(comet, y, "o", color=ACC, ms=3.6, zorder=4)
        ax.plot(market, y, "o", color=WARN, ms=4.2, zorder=4)
        ax.text(market * 1.12, y, f"{100 * (comet - market) / market:+.1f}%", va="center", ha="left",
                fontsize=5.6, color=ACC)
    ax.set_yticks(ys)
    ax.set_yticklabels([VAL.get(c["name"], c["name"]) for c in cases], fontsize=5.6)
    ax.set_xscale("log")
    ax.set_xlim(1.5, 90)
    ax.set_ylim(-0.7, len(cases) - 0.3)
    ax.set_xticks([2, 5, 10, 20, 50])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"{v:g}"))
    ax.set_xlabel(L["c_x"], fontsize=6.2)
    ax.plot([], [], "o", color=ACC, ms=3.6, label=L["c_comet"])
    ax.plot([], [], "o", mfc="white", mec=GREY, mew=1.0, ms=5.5, label=L["c_published"])
    ax.plot([], [], "o", color=WARN, ms=4, label=L["c_market"])
    ax.legend(fontsize=5.4, frameon=False, loc="lower left", bbox_to_anchor=(-0.30, 1.02), ncol=1,
              handlelength=1.0, columnspacing=0.8, handletextpad=0.4, borderaxespad=0.0, labelspacing=0.35)
    _clean(ax)
    ax.tick_params(axis="y", length=0)
    fig.text(0.615, 0.425, L["c_note"], fontsize=5.2, color=MUTED, linespacing=1.5)


def _price_basis_panel(fig):
    history = json.loads(HISTORY.read_text(encoding="utf-8"))["series"]
    live = json.loads(LIVE.read_text(encoding="utf-8"))["price_basis"]
    x_left, x_right, y_top = 0.055, 0.985, 0.30
    cols, panel_gap, row_gap = 4, 0.018, 0.085
    width = (x_right - x_left - (cols - 1) * panel_gap) / cols
    height = (y_top - 0.045 - row_gap) / 2
    for k, symbol in enumerate(METALS):
        row, col = divmod(k, cols)
        ax = fig.add_axes([x_left + col * (width + panel_gap), y_top - (row + 1) * height - row * row_gap,
                           width, height])
        series = history[symbol]
        dates = [datetime.strptime(p["date"], "%Y-%m-%d") for p in series["points"]]
        prices = [p["price"] for p in series["points"]]
        cut = next(d for d in dates if d.strftime("%Y-%m") == REFERENCE_MONTH)
        ax.axvspan(dates[0], cut, color=FILL, zorder=0)
        ax.plot(dates, prices, color=GREY, lw=0.7, zorder=2)
        ax.plot(cut, prices[dates.index(cut)], "o", color=ACC, ms=3.4, zorder=4)
        quote = live[symbol]
        ax.plot(datetime.strptime(quote["fetched_at"][:10], "%Y-%m-%d"), quote["price"], "o", color=WARN, ms=3.4,
                zorder=4)
        unit = L["unit_oz"] if series["unit"] == "$/troy_oz" else L["unit_lb"]
        ax.set_ylim(0, max(max(prices), quote["price"]) * 1.25)
        ax.set_xlim(dates[0], datetime(2026, 11, 1))
        ax.text(0.03, 0.96, f"{L['metal_names'][symbol]}  ({unit})", transform=ax.transAxes, ha="left", va="top",
                fontsize=5.6, fontweight="bold")
        ax.yaxis.set_major_locator(MaxNLocator(3))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"{v / 1000:g}k" if v >= 1000 else f"{v:g}"))
        ax.set_xticks([datetime(y, 1, 1) for y in (2020, 2023, 2026)])
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        _clean(ax)
        ax.tick_params(labelsize=5.2, length=1.5, pad=1.5)
    fig.text(0.52, 0.325, L["d_note"], ha="center", va="center", fontsize=5.4, color=MUTED, linespacing=1.4)


def figure2_cost_model():
    fig = plt.figure(figsize=(178 / 25.4, 205 / 25.4))
    _cost_model_panel(fig)
    _structure_panel(fig)
    _validation_panel(fig)
    _price_basis_panel(fig)
    for label, x, y in (("a", 0.012, 0.982), ("b", 0.012, 0.762), ("c", 0.60, 0.762), ("d", 0.012, 0.335)):
        fig.text(x, y, label, fontsize=8, fontweight="bold")
    return fig


def figure3_diagnostics():
    study = json.loads(STUDY.read_text(encoding="utf-8"))
    methods = json.loads(METHODS.read_text(encoding="utf-8"))
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
    fig = plt.figure(figsize=(178 / 25.4, 108 / 25.4))

    ax = fig.add_axes([0.215, 0.085, 0.33, 0.83])
    ys = list(range(len(rows)))
    ax.barh(ys, [r[1] for r in rows], color=ACC, height=0.72, label=L["f3_first"])
    ax.barh(ys, [r[2] for r in rows], left=[r[1] for r in rows], color=WARN, height=0.72, label=L["f3_second"])
    ax.barh(ys, [r[3] for r in rows], left=[r[1] + r[2] for r in rows], color="#D9DEE1", height=0.72,
            label=L["f3_other"])
    ax.axvline(50, color="white", lw=0.6)
    ax.axvline(50, color=GREY, lw=0.5, ls=(0, (1.5, 1.5)))
    ax.set_yticks(ys)
    ax.set_yticklabels([FAM.get(r[0], r[0]) for r in rows], fontsize=5.6)
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_xlabel(L["f3_x"], fontsize=6.4)
    ax.legend(fontsize=5.6, frameon=False, loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=3, handlelength=1.0,
              columnspacing=0.9, handletextpad=0.5, borderaxespad=0.0)
    _clean(ax)
    ax.tick_params(axis="y", length=0)
    fig.text(0.01, 0.965, "a", fontsize=8, fontweight="bold")

    bx = fig.add_axes([0.70, 0.625, 0.285, 0.29])
    n = summary["families"]
    counts = [n - summary["families_reference_winner_below_half_joint"],
              n - summary["candidate_removal_families_changed"],
              *[summary["rubric_robust_family_counts"][k] for k in ("2", "5", "10")]]
    yb = list(range(len(counts)))
    bx.barh(yb, [n] * len(counts), color="#EEF1F2", height=0.64)
    bx.barh(yb, counts, color=ACC, height=0.64)
    for i, count in enumerate(counts):
        bx.text(count + 0.6, i, str(count), va="center", fontsize=6)
    bx.set_yticks(yb)
    bx.set_yticklabels(L["f3_tests"], fontsize=6)
    bx.invert_yaxis()
    bx.set_xlim(0, n)
    bx.set_xticks([0, 10, 20, 30])
    bx.set_xlabel(L["f3_b_x"], fontsize=6.4)
    _clean(bx, left=False)
    bx.tick_params(axis="y", length=0)
    fig.text(0.635, 0.965, "b", fontsize=8, fontweight="bold")

    cx = fig.add_axes([0.70, 0.095, 0.285, 0.40])
    example = methods["normalization"]["example"]["rows"]
    names = ["Co/MgO–La$_2$O$_3$", "Ni–MgO/CeO$_2$", "Ni/Al$_2$O$_3$"]
    before = [r["total_before"] for r in example]
    after = [r["total_after"] for r in example]
    win_b, win_a = before.index(max(before)), after.index(max(after))
    ys = [2, 1, 0]
    for i, y in enumerate(ys):
        cx.plot([after[i], before[i]], [y, y], color=RULE, lw=1.0, zorder=2)
        cx.plot(before[i], y, "o", color=ACC, ms=4.2, zorder=3)
        cx.plot(after[i], y, "o", mfc="white" if after[i] == before[i] else WARN, mec=WARN, mew=0.9, ms=4.2, zorder=4)
        cx.text(before[i], y + 0.22, f"{before[i]:.1f}" + (L["f3_first_tag"] if i == win_b else ""), ha="center",
                va="bottom", fontsize=5.6, color=ACC)
        cx.text(after[i], y - 0.22, f"{after[i]:.1f}" + (L["f3_first_tag"] if i == win_a else ""), ha="center",
                va="top", fontsize=5.6, color=WARN)
    cx.set_yticks(ys)
    cx.set_yticklabels([f"{n}\n{r['cost']:.2f} {L['usd_lb']}" for n, r in zip(names, example, strict=True)],
                       fontsize=5.8)
    cx.set_ylim(-0.8, 2.8)
    cx.set_xlim(35, 100)
    cx.set_xlabel(L["f3_c_x"], fontsize=6.4)
    cx.plot([], [], "o", color=ACC, ms=4, label=L["f3_full"])
    cx.plot([], [], "o", mfc=WARN, mec=WARN, ms=4, label=L["f3_removed"])
    cx.legend(fontsize=5.6, frameon=False, loc="lower left", handlelength=1.0, handletextpad=0.5, borderaxespad=0.2)
    _clean(cx)
    cx.tick_params(axis="y", length=0)
    fig.text(0.635, 0.505, "c", fontsize=8, fontweight="bold")
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
                           ("fig3_decision_diagnostics", figure3_diagnostics)):
        figure = function()
        figure.savefig(args.out_dir / f"{name}{suffix}.png", dpi=400, facecolor="white",
                       metadata={"Software": "COMET"})
        figure.savefig(args.out_dir / f"{name}{suffix}.svg", facecolor="white", metadata={"Date": None})
        plt.close(figure)
        print("wrote", args.out_dir / f"{name}{suffix}")


if __name__ == "__main__":
    main()
