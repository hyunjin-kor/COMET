"""Synchronize derived CatCost data files from the workbook."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catcost_excel import (
    CatCostWorkbook,
    DATA_DIR,
    extract_capex_factors,
    extract_cepci,
    extract_chemppi,
    extract_equipment_library,
    extract_opex_factors,
    extract_step_library,
    sync_process_templates,
    sync_spent_catalyst_json,
)


def _write_json(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def main() -> int:
    workbook = CatCostWorkbook()
    try:
        step_path = _write_json(DATA_DIR / "step_library.json", extract_step_library(workbook))
        equipment_path = _write_json(DATA_DIR / "equipment_library.json", extract_equipment_library(workbook))
        chemppi_path = _write_json(DATA_DIR / "chemppi.json", extract_chemppi(workbook))
        cepci_path = _write_json(DATA_DIR / "cepci.json", extract_cepci(workbook))
        capex_path = _write_json(DATA_DIR / "capex_factors.json", extract_capex_factors(workbook))
        opex_path = _write_json(DATA_DIR / "opex_factors.json", extract_opex_factors(workbook))
        spent_path = sync_spent_catalyst_json(workbook)
        template_paths = sync_process_templates(workbook)
    finally:
        workbook.close()

    print(f"synced: {step_path}")
    print(f"synced: {equipment_path}")
    print(f"synced: {chemppi_path}")
    print(f"synced: {cepci_path}")
    print(f"synced: {capex_path}")
    print(f"synced: {opex_path}")
    print(f"synced: {spent_path}")
    for path in template_paths:
        print(f"synced: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
