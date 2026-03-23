# API Reference

Base URL: `http://localhost:8000/api`

## Calculator

### POST /api/calculate
Full catalyst cost estimation using Step Method.

**Request Body:**
```json
{
  "metal_symbol": "Ni",
  "metal_price": 7.50,
  "metal_price_unit": "$/lb",
  "metal_loading_wt_pct": 15.0,
  "support_name": "Al2O3",
  "support_price_per_lb": 0.50,
  "steps": ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"],
  "order_size_tons": 20.0
}
```

### POST /api/calculate/quick
Simplified calculation with minimal inputs.

### POST /api/compare
Compare up to 4 compositions side-by-side.

### POST /api/uncertainty
Monte Carlo simulation (100-10000 iterations).

## Prices

### GET /api/prices
All metals with latest prices.

### GET /api/prices/{symbol}
Single metal price (e.g., `/api/prices/Pt`).

### GET /api/prices/{symbol}/history
Price history with `?limit=30` parameter.

### POST /api/prices/refresh
Manually trigger price update from APIs.

## Materials

### GET /api/materials
List all materials. Filter with `?category=metal` or `?q=plat`.

### POST /api/materials
Add a custom material.

### GET /api/materials/templates
List process templates.

### GET /api/materials/templates/{id}
Get specific template details.

### GET /api/materials/steps
List all processing steps with hourly costs.

## Import/Export

### POST /api/import/catcost
Import CatCost-compatible JSON file.

### GET /api/export/{estimate_id}
Export saved estimate (`?format=json` or `?format=csv`).

## System

### GET /api/health
Server health check with scheduler status.
