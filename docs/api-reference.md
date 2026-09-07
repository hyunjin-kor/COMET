# API Reference

Base URL:

- Electron/local desktop dev: `http://127.0.0.1:8765/api`
- Standalone backend debug runs: `http://localhost:8000/api`

## Calculator

### POST /api/calculate
Full catalyst cost estimation using the current multi-component request shape.

**Thermocatalyst example:**
```json
{
  "catalyst_domain": "thermal",
  "application_family": "general",
  "components": [
    { "role": "active_metal", "name": "Ni", "wt_pct": 20.0, "price_per_lb": 7.5 },
    { "role": "support", "name": "Al2O3", "wt_pct": 80.0, "price_per_lb": 0.5 }
  ],
  "steps": ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"],
  "order_size_tons": 20.0,
  "include_spent_value": true,
  "reactor_type": "fixed",
  "catalyst_bulk_density": 50.0
}
```

**Electrocatalyst example:**
```json
{
  "catalyst_domain": "electrocatalyst",
  "application_family": "fuel_cell",
  "template_id": "pem_fuel_cell_ccm",
  "components": [
    { "role": "active_catalyst", "material_key": "fcs:ptc-20-vulcan", "wt_pct": 100.0 }
  ],
  "steps": ["membrane_pretreatment", "ionomer_ink_homogenization", "ccm_coating_pass", "electrode_drying_low_temp", "hot_press_lamination", "electrochemical_break_in"],
  "order_size_tons": 20.0,
  "electrode_input": {
    "application_family": "fuel_cell",
    "catalyst_material_key": "fcs:ptc-20-vulcan",
    "ionomer_material_key": "fcs:nafion-d2020",
    "membrane_material_key": "fcs:nafion-117",
    "substrate_material_key": "fcs:carbon-paper-gdl",
    "active_area_cm2": 25.0,
    "catalyst_loading_mg_cm2": 0.5,
    "ionomer_to_catalyst_ratio": 0.8
  }
}
```

**Notable response fields:**

- `summary`: estimated and net cost
- `step_method`: campaign basis and cost split
- `spent_catalyst`: returned when recovery screening is enabled
- `electrode_model`: returned for electrocatalyst area-based runs
- `resolved_materials`: source rows, quote basis, and normalization metadata

Numeric requests reject NaN and Infinity with422. A `template_id` must belong to the selected catalyst domain. When `steps` is omitted (or empty), the selected template supplies its scale-fitted steps; explicit steps remain user edits. Saved calculation input records the steps actually used. The bulk margin correlation also rejects orders that imply a margin of100% or more. These errors do not write a saved estimate or custom material.

### POST /api/calculate/quick
Simplified calculation with minimal inputs.

### POST /api/compare
Compare up to 4 compositions side-by-side.

### POST /api/uncertainty
Monte Carlo simulation (100-10000 iterations). Pass `calculation_input` with the
same body accepted by `/api/calculate`, plus `n_simulations` and optionally `seed`.
`seed` is a nonnegative integer; the same input and seed reproduce the same
summary. Omit it (or pass `null`) for fresh random draws. Both the full calculator
input and legacy flat uncertainty request accept this field.

For `calculation_input`, the response identifies the sampled outcome:

| Field | Thermal | Electrode assembly |
|---|---|---|
| `metric` | `selling_price`, or `selling_price_less_recovery` for a full request with recovery enabled | `electrode_assembly_cost` |
| `unit` | `$/lb` | `$/cm2` |
| `baseline` | Current point estimate for that metric | Current area-based assembly cost |
| `baseline_price_per_lb`, `baseline_price_per_kg` | Compatibility fields retained | Omitted; mass conversion is inapplicable |

The legacy flat response retains its bulk statistics without `baseline` or `metric` fields. `mean`, `median`, quantiles and standard deviation use `unit`. `seed` echoes the requested seed or null. `n_successful`, `n_failed` and `failure_reasons` disclose rejected samples; reported statistics are conditional on successful samples. A thermal scale crossing fits the existing operations to the new scale; a dropped required operation is a failed sample.

`uncertainties` maps supported factor names to positive ordered `[low, high]` pairs. Full inputs accept `active_component_price`, `promoter_price`, `support_price`, `electrode_adjunct_price`, `order_size_tons`; legacy inputs accept `metal_price`, `support_price_per_lb`, `order_size_tons`, `metal_loading_wt_pct`. Unknown keys return422. An empty object fixes all factors at1, while an omitted/null map uses defaults. For an area result, only active-component and adjunct price factors are applied and reported in `uncertainties_applied`; area, loading, bulk order size and the declared manufacturing scenario do not vary.

The offline `scripts/run_all_families.py` analysis accepts `--price-basis <json>`
for a frozen price map and `--basis-type reference` for the academic tier. Frozen
runs omit the wall-clock timestamp (`generated_at: null`) so identical inputs
produce identical JSON; `SOURCE_DATE_EPOCH` can supply a fixed UTC timestamp.

## Prices

### GET /api/templates/costs
`?order_size_tons=20` (and optionally `catalyst_domain`). Processing cost of every process template at that campaign size, materials excluded, with the steps fitted to the campaign's scale (`steps_fitted`, `substitutions`), any steps that could not be priced (`dropped_steps`), and the operations the Step Library has no rate for (`uncosted_operations`).

### GET /api/prices
All metals with latest prices. `?basis=live` (default) returns the daily quotes; `?basis=reference` returns the latest stored monthly averages (IMF PCPS, Johnson Matthey), with `basis_month` on each row. The same parameter applies to `/api/prices/{symbol}`, `/api/prices/{symbol}/history`, `/api/prices/trends` and `/api/decision/benchmarks/{family}`; `POST /api/calculate` takes it as `price_basis` in the body. `GET /api/prices/supports?basis=reference` lists the support-material unit-value series (HS code, material, library keys, latest month and value).

### GET /api/prices/{symbol}
Single metal price (e.g., `/api/prices/Pt`).

### GET /api/prices/{symbol}/history
Price history with `?limit=30` parameter.

### POST /api/prices/refresh
Manually trigger price update from APIs. In non-debug deployments this is limited to local requests by default.

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

## Optional practical costing fields

`POST /api/calculate` and `POST /api/calculate/save` accept the following optional
fields. Existing requests without these fields retain their default calculation.
No field supplies a new equipment rate or a verified market observation.

| Location / field | Meaning and validation |
|---|---|
| `production_rate_ton_per_day` | Positive effective finished-catalyst production rate, in short tons/day; thermal only. Omit or pass `null` for the scale default. |
| `production_rate_note` | Required nonblank source or assumption note when the effective rate is supplied. |
| `components[].recipe_consumption` | Optional thermal purchased-precursor calculation; requires all fields below and `precursor_markup: 1`. |
| `recipe_consumption.precursor_name` | Purchased compound and grade, distinguished from the retained catalyst component. |
| `recipe_consumption.retained_component_fraction` | Mass fraction of the desired retained component in the pure precursor; `(0, 1]`. |
| `recipe_consumption.purity_fraction` | Purchased precursor purity; `(0, 1]`. |
| `recipe_consumption.yield_fraction` | Fraction of that component retained in the finished catalyst; `(0, 1]`. |
| `recipe_consumption.price_per_kg` | Nonnegative explicit purchased-precursor price in USD/kg. |
| `recipe_consumption.source_note` | Required nonblank source or assumption note. |
| `consumables[]` | Up to 30 thermal auxiliary inputs, each with `name`, positive `kg_per_kg_catalyst`, nonnegative `price_per_kg` in USD/kg, and nonblank `source_note`. These quantities are net purchases per kg of finished catalyst. |
| `components[].purchase_evidence` | Optional local fields `supplier`, `quote_date` (`YYYY-MM-DD`), positive `quantity`, `quantity_unit`, `grade`, `cost_boundary`, `reference`, `notes`. No independent verification is implied. |

Recipe cost uses normalized finished-component fraction divided by retained
fraction, purity and yield, multiplied by purchased-precursor USD/kg. The original
component `price_per_lb` stays a reference/recovery price and is not added again.
See [the mass-balance boundary](methodology.md#purchased-precursor-and-auxiliary-consumption).
Electrode requests reject thermal throughput, recipe and auxiliary inputs.

Results add `costing_scope` with `status` (`modeled_steps`, `proxy`, `partial`),
`boundary`, `costed_steps`, `actual_steps`, `declared_steps`, `substitutions`,
`dropped_steps`, `omitted_template_steps`, `added_steps`, `uncosted_operations`,
`route_modified`, `template_name`, and `area_cost_boundary`. Saved results and CSV
exports retain these fields. A complete selected operation list does not establish
complete plant coverage. Recipe cost does not replace the existing LCA inventory.

## Saved complete-estimate comparison

### POST /api/estimates/compare

Compare two to four distinct saved estimates. The IDs below are illustrative;
replace them with IDs returned by `/api/calculate/save` or `/api/estimates`.

```json
{
  "estimate_ids": [12, 19],
  "reference_estimate_id": 12,
  "price_basis": "reference",
  "order_size_tons": 20
}
```

All four fields are required. The reference must be selected. Estimates must share
the same catalyst domain and resolved application family. Electrode comparisons
require electrode assembly inputs in every estimate. Invalid selections return
422; an unknown saved ID returns 404. The endpoint does not overwrite saved data.

The named reference supplies the target/base year, G&A/SARD, recovery assumptions,
effective rate and note. For electrodes it also supplies area, catalyst loading,
ionomer-to-catalyst ratio and manufacturing scenario. Each estimate retains its
complete formulation, precursor yields/consumption, auxiliary amounts, template
and manufacturing steps. Scale-specific equipment is fitted to the common order
quantity, with substitutions and unavailable steps reported.

The response contains:

- `common_conditions`: every shared operating condition and the selected basis.
- `unit`: `USD/lb` for thermal selling price less recovery, or `USD/cm2` for
  electrode assembly cost. The frontend converts thermal mass units for display.
- `price_snapshot`: harmonized values, their source estimate/evidence and
  `overridden_estimate_ids`. Reference prices take priority; missing reference
  materials use the lowest selected estimate ID. Library IDs and manual grades
  remain distinct; unknown product equivalence is reported.
- `estimates[]`: saved result, `repriced_original_conditions`, `common_conditions`,
  `scale_adjustment`, and their three headline `values`.
- `warnings`: scope and comparability limitations. A saved-to-repriced difference
  may include a model-version change, and formulation/route differences are not
  interpreted as pure manufacturing-method effects.

## Local actual-cost evidence

### GET /api/estimates/{estimate_id}/observations

Returns `expected_reference`, preserved `observations`, `eligible_count`,
`mape_pct`, and the explicit user-supplied verification status. `mape_pct` is
`null` when no observation qualifies.

### POST /api/estimates/{estimate_id}/observations

Appends a local observation to the saved result JSON and returns the updated
assessment with status 201. Existing calculation inputs and numeric results
remain unchanged. Required fields are positive `observed_price`,
`observation_date` and nonblank `source`. The optional fields are:

| Field | Accepted values / meaning |
|---|---|
| `currency`, `price_unit` | Three-letter uppercase currency (default `USD`); `lb`, `kg` or `cm2` (default `kg`). No currency conversion is assumed. |
| `price_period` | Observed input-price month `YYYY-MM`; must agree with the observation date and every saved component price month for eligibility. |
| `order_size_tons`, `production_rate_ton_per_day` | Observed short-ton quantity and effective short tons/day; positive when supplied. |
| `components[]` | Independently entered `name`, `wt_pct`, `grade`; observed fractions must total 100 wt% for eligibility. |
| `template_id`, `steps[]` | Observed template ID and exact manufacturing step keys, including repeated operations. |
| `cost_boundary` | `material_purchase` (default), `full_manufacturing_cost`, `full_selling_price`, `full_net_after_recovery`, or `other`. |
| `cost_scope_note`, `production_conditions_note` | Source-documented inclusions/exclusions and operating conditions. |
| `evidence_type` | `supplier_quote` (default), `invoice`, `production_record`, `public_literature`, or `other`. |
| `verified_by_user`, `notes` | User confirmation (default `false`) and optional notes. Confirmation is not independent verification. |

The assessment returns `eligible`, `exclusion_reasons`, the relevant
`predicted_price`, `signed_error_pct`, `absolute_percentage_error` and
`verification`. Error fields remain `null` for missing/mismatched conditions,
unverified records, supplier quotes, partial costing scopes, recipe inputs whose
actual consumption has not been matched, and electrode-area observations. The
first implementation assesses full-cost errors for thermal mass-based cases only.
Ineligible observations remain available as local evidence.

## Optional hosted accounts

The desktop default remains login-free. Opt-in hosted startup requires the commercial data-rights gate and private storage configuration described in [operations](commercial/hosted-operations.ko.md). No real service has been launched.

| Endpoint | Behavior |
|---|---|
| `GET /api/auth/session` | Public bootstrap; `mode`, `authenticated`, and this account's public fields/subscription. Desktop returns `account: null`. |
| `POST /api/auth/login` | `username` and `password`; sets an HttpOnly same-origin session cookie. No client-supplied company/contract fields. |
| `POST /api/auth/logout` | Revokes the current server session and expires its cookie. |
| `POST /api/auth/password` | Authenticated `current_password`, `new_password` (15–128 characters); revokes all account sessions and requires sign-in again. |

Hosted protected APIs require `X-Comet-Account` equal to the account ID returned by session/login. This confirms the current displayed account; only the server cookie resolves the owner. A changed or missing confirmation returns409. All mutations, including login, require the configured exact `Origin` and `X-Comet-Request: 1`. Authentication expiry returns401. The shipped browser adds these headers only in hosted mode; no tokens are stored in browser storage.

Ordinary pending/expired/revoked subscriptions retain saved reads and exports; new calculations and writes return403. Account security disable revokes all access separately. Limits return429 with `Retry-After`: account60/company240 work attempts per minute, uncertainty10 per account per minute, and two concurrent work requests per process. The existing10,000 simulation limit remains. Bodies over2MiB return413. These are initial single-worker guardrails, not a tested capacity or billing promise. No public operator API or client activation endpoint exists. Hosted external price refresh remains disabled.
