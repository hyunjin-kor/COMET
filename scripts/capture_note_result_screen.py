"""Record the worked example of Figure 2 in the Application Note and capture its result screen.

Builds a 20 wt% Ni/Al2O3 estimate through the running COMET backend (incipient-wetness
template, 20 t order, live price tier), writes the request, the quotes and the full cost
result to a JSON sidecar next to the output (the figure script reads it), seeds the browser
session the same way the README capture does, and saves the top of the result page for
reference. Requires the backend serving the built
frontend at http://127.0.0.1:8765 and Python Playwright with Chrome. Run:

    python scripts/capture_note_result_screen.py --out docs/paper/figures-note-2026-09-09/screen_result_ni_al2o3.png
"""

import argparse
import json
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8765"
API = BASE + "/api"
TEMPLATE = "wet_impregnation_metal_oxide"
ORDER_TONS = 20
NI_WT, AL2O3_WT = 20, 80


def get(path):
    with urllib.request.urlopen(API + path, timeout=60) as response:
        return json.load(response)


def post(path, body):
    request = urllib.request.Request(API + path, data=json.dumps(body).encode("utf-8"),
                                     headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response)


def per_lb(price, unit):
    if unit == "$/troy_oz":
        return price * 14.5833
    if unit == "$/kg":
        return price / 2.20462
    return price


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    prices = get("/prices")
    options = get("/materials/composition-options?catalyst_domain=thermal")
    step_names = {row["key"]: row["name"] for row in get("/materials/steps")}
    template = get(f"/materials/templates/{TEMPLATE}")
    nickel = next(row for row in prices if row["symbol"] == "Ni" and row["source_type"] == "live")
    alumina = next(row for row in options["support_options"] if row["display_name"] == "Al2O3")
    steps = template["steps"]
    ni_price = per_lb(nickel["price"], nickel["unit"])

    request = {
        "catalyst_domain": "thermal",
        "application_family": "general",
        "template_id": TEMPLATE,
        "order_size_tons": ORDER_TONS,
        "steps": steps,
        "components": [
            {"role": "active_metal", "name": "Ni", "wt_pct": NI_WT, "price_per_lb": ni_price},
            {"role": "support", "name": alumina["display_name"], "wt_pct": AL2O3_WT,
             "price_per_lb": alumina["price_per_lb"]},
        ],
    }
    result = post("/calculate", request)
    now = datetime.now(UTC).isoformat()
    draft = {
        "rows": [
            {"id": "draft-active-ni", "role": "active_metal", "name": "Ni", "material_key": None, "symbol": "Ni",
             "selection_key": "live:Ni", "wt_pct": NI_WT, "price_per_lb": ni_price, "source_type": "live",
             "source": nickel["source"]},
            {"id": "draft-support-al2o3", "role": "support", "name": alumina["display_name"],
             "material_key": alumina.get("material_key"), "symbol": alumina.get("symbol"),
             "selection_key": alumina["selection_key"], "wt_pct": AL2O3_WT, "price_per_lb": alumina["price_per_lb"],
             "source_type": alumina["source_type"], "source": alumina.get("quote_source") or "Library"},
        ],
        "steps": steps,
        "preparationStepBasis": steps,
        "thermalTemplateId": TEMPLATE,
        "catalystDomain": "thermal",
        "applicationFamily": "general",
        "orderSize": ORDER_TONS,
        "pricesUpdatedAt": now,
        "includeSpentValue": False,
        "reactorType": "fixed",
        "catalystBulkDensity": 50,
        "electrocatalystConfig": None,
        "benchmarkCandidate": None,
    }
    snapshot = {
        "result": result,
        "orderSize": ORDER_TONS,
        "steps": steps,
        "stepLabels": [step_names.get(key, key) for key in steps],
        "selectedSupportName": alumina["display_name"],
        "activeMetalCount": 1,
        "liveFeedCount": sum(row["source_type"] == "live" for row in prices),
        "indexedFeedCount": sum(row["source_type"] == "indexed" for row in prices),
        "nonSupportWt": NI_WT,
        "supportWtPct": AL2O3_WT,
        "generatedAt": now,
        "benchmarkCandidate": None,
        "costInput": request,
    }
    summary = result.get("summary", {})
    sidecar = {
        "captured_at": now,
        "request": request,
        "nickel_quote": nickel,
        "alumina_row": alumina,
        "template_name": template["name"],
        "step_labels": snapshot["stepLabels"],
        "route_summary": result.get("route_summary"),
        "summary": summary,
        "materials": result.get("materials"),
        "step_method": result.get("step_method"),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.with_suffix(".json").write_text(json.dumps(sidecar, indent=2, ensure_ascii=False) + chr(10), encoding="utf-8")
    print("estimate:", {k: summary.get(k) for k in ("estimated_price_per_lb", "net_cost_per_lb")},
          "route:", (result.get("route_summary") or {}).get("name"))

    init = """
    ({draft, snapshot}) => {
      localStorage.setItem('comet_unit', 'lb');
      const apply = () => {
        window.sessionStorage.setItem('comet_calculator_draft', JSON.stringify(draft));
        window.sessionStorage.setItem('comet_calculator_result', JSON.stringify(snapshot));
      };
      apply();
      const startedAt = Date.now();
      const timer = window.setInterval(() => { apply(); if (Date.now() - startedAt > 4000) window.clearInterval(timer); }, 50);
    }
    """
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1500, "height": 1120}, device_scale_factor=2)
        page = context.new_page()
        page.set_default_timeout(45000)
        page.add_init_script(f"(() => {{ const fn = {init.strip()}; fn({json.dumps({'draft': draft, 'snapshot': snapshot})}); }})();")
        page.goto(BASE, wait_until="domcontentloaded")
        page.evaluate("(route) => { window.history.pushState({}, '', route); window.dispatchEvent(new PopStateEvent('popstate')); }",
                      "/calculator/result?result=summary")
        page.wait_for_load_state("domcontentloaded")
        try:
            page.wait_for_load_state("networkidle", timeout=3000)
        except Exception:
            pass
        page.wait_for_timeout(1200)
        page.wait_for_selector("text=Preparation basis")
        clip = page.evaluate("""() => {
          const node = document.querySelector('main > div > div:last-child');
          if (!node) return null;
          const rect = node.getBoundingClientRect();
          return { x: rect.left + window.scrollX, y: rect.top + window.scrollY, width: rect.width, height: Math.min(rect.height, 860) };
        }""")
        if clip is None:
            raise SystemExit("result container not found")
        page.screenshot(path=str(args.out), type="png", full_page=True,
                        clip={"x": max(0, int(clip["x"])), "y": max(0, int(clip["y"])),
                              "width": int(clip["width"] + 0.5), "height": int(clip["height"] + 0.5)})
        browser.close()
    print("wrote", args.out)


if __name__ == "__main__":
    main()
