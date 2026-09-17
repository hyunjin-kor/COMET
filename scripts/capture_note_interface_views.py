"""Capture the two Supporting Information interface views from a running COMET review server.

View A shows the Preparation Method step after a literature preparation record has been
imported in record-only mode, so the per-input sources are visible. View B shows the result
page of the illustrative 2026-09-15 manufacturing batch in batch-cost mode with the detailed
protocol and its per-operation cost contributions. Both views are captured in English and
Korean at a 900 px wide viewport with a device scale factor of 2.

Requires a backend serving the built frontend on --base with an isolated database and no
API keys (for example _local/software-review-2026-09-14/serve_review.py 8877) and Python
Playwright with Chrome. The screenshots are Figure S6 artwork; rebuild the deck afterwards:

    python scripts/capture_note_interface_views.py --base http://127.0.0.1:8877
    python scripts/build_note_figure_decks.py figS9_interface
"""

import argparse
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ARTWORK = ROOT / "docs/paper/diagram-sources-2026-09-16/artwork"
STUDY = ROOT / "docs/paper/manufacturing-study-2026-09-15/manufacturing_study.json"
PROFILE = "ptsn-alumina-base-2024"
TEXT = {
    "en": {"literature": "Choose a literature preparation", "specimen": "Published specimen",
           "import": "Use as editable preparation record", "protocol": "Detailed manufacturing protocol",
           "run": "Run estimate", "evidence": "Batch input evidence", "sources": "Sources for individual inputs"},
    "ko": {"literature": "문헌 제조법에서 가져오기", "specimen": "문헌 시료",
           "import": "편집 가능한 제조 기록으로 가져오기", "protocol": "상세 제조 조건", "run": "계산 실행", "evidence": "배치 입력 근거", "sources": "입력 항목별 출처"},
}
RECORD_HEIGHT = 900
COSTS_HEIGHT = 800


def draft_from_request(request):
    rows = [{"id": f"row-{index}", "role": component["role"], "name": component["name"], "wt_pct": component["wt_pct"],
             "price_per_lb": component["price_per_lb"], "source_type": "manual", "source": "Illustrative scenario"}
            for index, component in enumerate(request["components"])]
    return {"rows": rows, "steps": request["steps"], "catalystDomain": "thermal", "orderSize": request["order_size_tons"],
            "pricesUpdatedAt": None, "manufacturingProtocol": request["manufacturing_protocol"]}


def record_draft():
    rows = [{"id": "row-0", "role": "active_metal", "name": "Ni", "symbol": "Ni", "wt_pct": 2, "price_per_lb": 7.5,
             "source_type": "manual", "source": "Illustrative entry"},
            {"id": "row-1", "role": "support", "name": "CeO2", "wt_pct": 98, "price_per_lb": 3.0,
             "source_type": "manual", "source": "Illustrative entry"}]
    return {"rows": rows, "steps": [], "catalystDomain": "thermal", "orderSize": 1, "pricesUpdatedAt": None}


def open_all_details(page):
    page.evaluate("() => document.querySelectorAll('details').forEach((node) => { node.open = true; })")


def capture_section(page, section, path, max_height):
    section.scroll_into_view_if_needed()
    page.wait_for_timeout(300)
    section.screenshot(path=str(path))
    with Image.open(path) as image:
        limit = max_height * 2
        if image.height > limit:
            image.crop((0, 0, image.width, limit)).save(path)


def capture_range(page, first, last, path, max_height):
    """Screenshot the page region spanning two elements, in page coordinates."""
    first.scroll_into_view_if_needed()
    page.wait_for_timeout(300)
    scroll = page.evaluate("() => [window.scrollX, window.scrollY]")
    top, bottom = first.bounding_box(), last.bounding_box()
    height = min(bottom["y"] + bottom["height"] - top["y"], max_height)
    page.screenshot(path=str(path), full_page=True,
                    clip={"x": top["x"] + scroll[0], "y": top["y"] + scroll[1], "width": top["width"], "height": height})


def seed(page, base, lang, draft, query):
    page.goto(base + "/")
    page.evaluate("([key, value]) => window.localStorage.setItem(key, value)", ["comet_lang", lang])
    page.evaluate("([key, value]) => window.sessionStorage.setItem(key, value)", ["comet_calculator_draft", json.dumps(draft)])
    page.evaluate("() => window.sessionStorage.removeItem('comet_calculator_result')")
    page.goto(f"{base}/?estimate={query}")
    page.wait_for_load_state("networkidle")


def capture_record_view(page, base, lang, profile_sample, path):
    text = TEXT[lang]
    seed(page, base, lang, record_draft(), "manufacturing")
    page.get_by_text(text["literature"], exact=True).first.click()
    page.get_by_label(text["specimen"]).select_option(label=profile_sample)
    page.get_by_role("button", name=text["import"]).click()
    page.wait_for_timeout(500)
    section = page.locator(f'section[aria-label="{text["protocol"]}"]').first
    open_all_details(page)
    # Collapse the literature chooser again so the imported, editable record is what the figure shows.
    page.evaluate("(label) => document.querySelectorAll('details').forEach((node) => { "
                  "if (node.querySelector('summary')?.textContent?.trim() === label) node.open = false; })", text["literature"])
    page.wait_for_timeout(300)
    # The figure shows the per-field literature sources of the first imported operation.
    first_operation = section.locator("details").filter(has=page.locator("summary", has_text=re.compile("^1[.] "))).first
    sources = first_operation.locator("details", has_text=text["sources"]).first
    sources.locator("select").first.select_option(value="quantity")
    page.wait_for_timeout(300)
    capture_section(page, sources, path, RECORD_HEIGHT)


def capture_costs_view(page, base, lang, request, path):
    text = TEXT[lang]
    seed(page, base, lang, draft_from_request(request), "result")
    page.get_by_role("button", name=text["run"]).click()
    page.wait_for_url("**/calculator/result**", timeout=120000)
    page.goto(f"{base}/calculator/result?result=sources")
    page.wait_for_load_state("networkidle")
    section = page.locator("section", has_text=text["evidence"]).first
    open_all_details(page)
    page.wait_for_timeout(300)
    operations = section.locator("details", has=page.locator("summary"))
    names = [operation["name"] for operation in request["manufacturing_protocol"]["operations"]]
    first = section.locator("details", has_text=f"1. {names[0]}").first
    last = section.locator("details", has_text=f"{len(names)}. {names[-1]}").first
    capture_range(page, first, last, path, COSTS_HEIGHT)
    del operations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="http://127.0.0.1:8877")
    parser.add_argument("--profile", default=PROFILE)
    args = parser.parse_args()
    study = json.loads(STUDY.read_text(encoding="utf-8"))
    ARTWORK.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 900, "height": 900}, device_scale_factor=2)
        page = context.new_page()
        page.goto(args.base + "/api/decision/manufacturing-literature")
        profiles = json.loads(page.locator("pre").inner_text())["profiles"]
        profile = next(row for row in profiles if row["id"] == args.profile)
        outputs = []
        for lang in ("en", "ko"):
            record = ARTWORK / f"figS9_interface.record.{lang}.png"
            costs = ARTWORK / f"figS9_interface.costs.{lang}.png"
            capture_record_view(page, args.base, lang, profile["sample"], record)
            capture_costs_view(page, args.base, lang, study["request"], costs)
            outputs.extend([record, costs])
        browser.close()
    manifest = {"captured_at": datetime.now(UTC).isoformat(timespec="seconds"), "server": args.base,
                "viewport": [900, 900], "device_scale_factor": 2, "profile": {"id": profile["id"], "sample": profile["sample"], "doi": profile["doi"]},
                "batch_scenario": "docs/paper/manufacturing-study-2026-09-15/manufacturing_study.json:request",
                "database": "isolated review database; no user data", "files": {}}
    for path in outputs:
        manifest["files"][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (ARTWORK / "figS9_interface.capture.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest["files"], indent=2))


if __name__ == "__main__":
    main()
