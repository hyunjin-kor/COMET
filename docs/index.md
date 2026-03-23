# CatPrice

**Real-time metal price based catalyst manufacturing cost estimation tool.**

CatPrice is an open-source tool that estimates catalyst manufacturing costs using the Step Method and CapEx/OpEx Factors methodology, with real-time metal spot price integration.

## Features

- **Step Method Calculator** - Estimate catalyst selling price based on processing steps, production scale, and materials cost
- **Real-time Metal Prices** - Automatic daily price updates from Metals.Dev and MetalpriceAPI
- **Composition Comparison** - Compare up to 4 catalyst compositions side-by-side
- **Monte Carlo Uncertainty** - Probabilistic cost ranges via simulation
- **Materials Library** - Comprehensive database of metals, supports, and precursors
- **Process Templates** - Pre-configured templates for common catalyst types
- **Price Escalation** - ChemPPI/CEPCI-based cost adjustment between years
- **Spent Catalyst Recovery** - Estimate reclaimed value of spent PGM catalysts

## Academic Citation

This tool implements methodologies from:

- Baddour, F.G., et al. (2018). "An Exceptionally Mild and Scalable Solution-Phase Synthesis of Molybdenum Carbide Nanoparticles for Thermocatalytic CO2 Hydrogenation." *Journal of the American Chemical Society*.
- Van Allsburg, K.M., et al. (2022). "Early-stage evaluation of catalyst manufacturing cost and environmental impact using CatCost." *Nature Catalysis*.

## Quick Start

```bash
# Backend
pip install -e .
uvicorn backend.main:app --reload

# Frontend
cd frontend && npm install && npm run dev
```

Visit `http://localhost:5173` to use the application.
