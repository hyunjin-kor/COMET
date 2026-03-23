"""Monte Carlo uncertainty analysis for catalyst cost estimation.

Inspired by BioSTEAM's uncertainty analysis approach.
Provides probabilistic cost ranges instead of single-point estimates.
"""

from __future__ import annotations

import numpy as np

from backend.core.cost_engine import estimate_catalyst_cost


def run_monte_carlo(
    base_params: dict,
    uncertainties: dict[str, tuple[float, float]] | None = None,
    n_simulations: int = 1000,
    seed: int | None = None,
) -> dict:
    """Run Monte Carlo simulation on catalyst cost estimation.

    Args:
        base_params: Base parameters for estimate_catalyst_cost().
        uncertainties: Dict mapping parameter name to (low_factor, high_factor)
                       relative to base value. E.g. {"metal_price": (0.8, 1.2)}
                       means metal price varies from 80% to 120% of base.
        n_simulations: Number of Monte Carlo iterations.
        seed: Random seed for reproducibility.

    Returns:
        Dict with statistical summary and raw results.
    """
    rng = np.random.default_rng(seed)

    if uncertainties is None:
        uncertainties = {
            "metal_price": (0.8, 1.2),
            "support_price_per_lb": (0.9, 1.1),
            "order_size_tons": (0.8, 1.2),
        }

    results = []
    for _ in range(n_simulations):
        params = dict(base_params)
        for param, (lo, hi) in uncertainties.items():
            if param in params:
                base_val = base_params[param]
                factor = rng.uniform(lo, hi)
                params[param] = base_val * factor

        try:
            result = estimate_catalyst_cost(**params)
            results.append(result["summary"]["estimated_price_per_lb"])
        except (ValueError, KeyError):
            continue

    if not results:
        raise ValueError("All simulations failed")

    arr = np.array(results)

    return {
        "n_simulations": n_simulations,
        "n_successful": len(results),
        "mean": round(float(np.mean(arr)), 4),
        "median": round(float(np.median(arr)), 4),
        "std": round(float(np.std(arr)), 4),
        "min": round(float(np.min(arr)), 4),
        "max": round(float(np.max(arr)), 4),
        "p5": round(float(np.percentile(arr, 5)), 4),
        "p25": round(float(np.percentile(arr, 25)), 4),
        "p75": round(float(np.percentile(arr, 75)), 4),
        "p95": round(float(np.percentile(arr, 95)), 4),
        "unit": "$/lb",
        "uncertainties_applied": uncertainties,
    }
