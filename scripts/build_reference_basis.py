"""Write the paper's --price-basis file from a frozen history.

Takes the latest month every series in the history covers (or --month), pairs
each metal's monthly average with the USGS / CatCost anchors for metals that
have no published series, and writes the map the analysis scripts accept
through --price-basis. No network access: the basis is a function of the
committed history file alone, so it reproduces on any machine.

Run:  python scripts/build_reference_basis.py --history docs/paper/price_history_<date>.json --out docs/paper/reference_basis_<date>.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.core.price_fetcher import get_reference_prices  # noqa: E402
from backend.core.reference_basis import build_price_basis, latest_common_month  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--history", type=Path, required=True, help="frozen history from fetch_price_history.py")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--month", help="YYYY-MM; default is the latest month every series covers")
    args = ap.parse_args()

    series = json.loads(args.history.read_text(encoding="utf-8"))["series"]
    month = args.month or latest_common_month(series)
    basis = build_price_basis(series, month, get_reference_prices())

    out = {
        "generated_at": datetime.now(UTC).isoformat(),
        "history_file": str(args.history),
        "basis_month": month,
        "from_series": sorted(series),
        "from_anchors": sorted(s for s in basis if s not in series),
        "price_basis": basis,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=1), encoding="utf-8")

    print(f"basis month {month}")
    print(f"{'symbol':<8}{'price':>12}  {'unit':<11}source")
    for symbol in sorted(basis):
        entry = basis[symbol]
        print(f"{symbol:<8}{entry['price']:>12.4f}  {entry['unit']:<11}{entry['source']}")
    print(f"wrote {args.out}  (series={len(series)}, anchors={len(basis) - len(series)})")


if __name__ == "__main__":
    main()
