# Supporting Information

COMET: Catalyst Overall Manufacturing Estimation Tool

## S1. Scope and calculation boundaries

This supplement documents the September 2026 COMET Application Note. The May 2026 screening results retain their original frozen formulations and assumptions. The later preparation review does not retrospectively validate those formulations. The new manufacturing example is a hypothetical software demonstration, not an experimental catalyst cost or a comparison of matched catalytic performance.

Batch purchases replace composition-based materials costs; batch operation costs replace Step Method processing costs. For each operation, electricity is measured kWh or the sum of mean power multiplied by ramp, hold and additional durations. A ramp takes absolute temperature change divided by the entered ramp rate. Equipment occupancy is charged for the full entered operation duration; attended labor is a separate input. Gas volume is flow multiplied by its selected duration, using matching reference conditions for flow and price. Temperature, stirring speed and pressure are retained as preparation conditions; they do not infer equipment power, staffing, chemical yield or performance.

Intermediate charges are allocated by used/recovered mass or used/prepared volume of a homogeneous solution, with successive fractions multiplied along a chain. An explicit whole-batch option assigns the full incurred expenditure to its destination before subsequent transfers. Actual operation times and incurred expenditures remain distinct from their allocated shares. Unknown recovery prevents proportional allocation. Branching transfers, co-products and density-based conversions are not inferred.

For final dry mass M, manufacturing cost is (purchases + electricity + equipment + labor + gas + explicit additional charges)/M. Selling price applies sequential G&A and SARD factors, then divides by (1 − margin). The example excludes disposal, analytical testing, waste credits, catalyst use, tax, freight and any equipment cost not represented in the stated occupancy rate. Occupancy rates are assumed aggregate charges, not measured depreciation or purchase prices. Unknown required inputs are not treated as zero. Dry powder mass is not an electrode-area denominator.

## S2. Declared manufacturing inputs

Every numerical input below is an assumption chosen for arithmetic verification. The example does not identify a specific active phase or precursor chemistry. Dry output is independently specified; precursor stoichiometry and material yield are not inferred. The composition fields retained by the application are inactive for the purchase-based materials calculation.

Final dry output: 0.030 kg. Electricity: 0.10 USD/kWh. Labor: 10.00 USD/person-hour. G&A and SARD: 0.05 and 0.05; selling margin: 0.10. One batch is evaluated. The 2025 price-basis fields do not apply an index escalation to this direct batch calculation.

All thermal operations start at 20 °C and ramp at 5 °C/min. Each includes one additional hour of passive cooling/handling with explicitly zero additional electricity but continued equipment occupancy. Cooling is a declared duration, not a heat-transfer calculation. Reduction gas flows throughout ramp, hold and additional time at 0.1 L/min and costs 10 USD/m3; both flow and price refer to 0 °C and 1 atm. Its chemical composition is unspecified because this is an arithmetic scenario.

| Operation | Hold target (°C) | Hold or mixing (h) | Ramp / hold power (kW) | Equipment (USD/h) | Attendance (person-h) |
|---|---:|---:|---|---:|---:|
| Impregnation | Not assigned | 2 | Constant 0.05 | 1 | 0.25 |
| Drying | 120 | 4 | 0.4 / 0.25 | 0.8 | 0.1 |
| Calcination | 500 | 3 | 2 / 1.2 | 3 | 0.1 |
| Reduction | 400 | 2 | 1.5 / 0.6 | 2 | 0.25 |

| Purchase at impregnation | Quantity | Unit price | Batch expenditure (USD) |
|---|---:|---:|---:|
| Specified precursor solution (illustrative) | 5 mL | 2 USD/mL | 10.0000 |
| Support (illustrative) | 24 g | 0.05 USD/g | 1.2000 |
| Solvent (illustrative) | 100 mL | 0.01 USD/mL | 1.0000 |

## S3. Independent arithmetic verification

An independent balance uses explicit scalar arithmetic, without reading engine result fields. Thermal durations include ramp, hold and the additional hour. The full application API produces the same baseline and endpoint results. The regression also checks the application's seeded Monte Carlo summary and histogram counts.

| Operation | Occupancy (h) | Electricity (kWh) |
|---|---:|---:|
| Impregnation | 2.000000 | 0.100000 |
| Drying | 5.333333 | 1.133333 |
| Calcination | 5.600000 | 6.800000 |
| Reduction | 4.266667 | 3.100000 |

| Cost component | Incurred per batch (USD) | Per dry product (USD/kg) |
|---|---:|---:|
| Purchases | 12.200000 | 406.666667 |
| Electricity | 1.113333 | 37.111111 |
| Equipment occupancy | 31.600000 | 1053.333333 |
| Attended labor | 7.000000 | 233.333333 |
| Gas | 0.256000 | 8.533333 |
| G&A | 2.608467 | 86.948889 |
| SARD | 2.738890 | 91.296333 |
| Margin | 6.390743 | 213.024778 |

Manufacturing cost before overheads and margin is 1738.977778 USD/kg; selling price is 2130.247778 USD/kg. One extra calcination hour costs (1.2 kW × 0.1 USD/kWh + 3 USD/h)/0.030 kg × 1.05 × 1.05/0.90 = 127.40 USD/kg. Attendance does not change in this scenario.

## S4. Manufacturing sensitivity and uncertainty

Each endpoint changes only its named input; all other batch inputs remain fixed. Temperature does not determine an assumed power change. The dry-output endpoints therefore assess cost allocation, not predicted chemical yields or scale economies.

| Varied input | Low | High | Selling price at low (USD/kg) | Selling price at high (USD/kg) |
|---|---:|---:|---:|---:|
| Dry output | 0.015 kg/batch | 0.045 kg/batch | 4260.4956 | 1420.1653 |
| Precursor price | 1.0 USD/mL | 3.0 USD/mL | 1926.0810 | 2334.4144 |
| Impregnation time | 1.0 h | 4.0 h | 2089.2103 | 2212.3227 |
| Drying hold | 2.0 h | 8.0 h | 2062.8729 | 2264.9977 |
| Calcination hold | 1.0 h | 6.0 h | 1875.4477 | 2512.4478 |
| Calcination power | 0.6 kW | 2.4 kW | 2122.8978 | 2144.9478 |
| Reduction hold | 1.0 h | 4.0 h | 2043.6812 | 2303.3810 |
| Electricity tariff | 0.05 USD/kWh | 0.2 USD/kWh | 2107.5173 | 2175.7088 |

Figure 3(c) evaluates 21 calcination-hold values from 1 to 6 h at each of three dry masses (0.015, 0.030 and 0.045 kg), giving 63 scenarios. The complete grid is stored under `sweep` in manufacturing_study.json.

Monte Carlo uses seed 20260915 and 1000 trials. Independent uniform bounds are 0.024–0.036 kg dry output, 2–4 h calcination hold, 0.9–1.5 kW hold power and 0.06–0.12 USD/kWh. All other inputs are fixed. Successful/failed trials: 1000/0. Mean selling price is 2164.6042 USD/kg; the 5th and 95th percentiles are 1778.9261 and 2629.8509 USD/kg. These are scenario percentiles, not statistical confidence bounds. Individual sampled inputs and results are retained in the JSON. The application ordinarily excludes and counts invalid combinations without clamping; this example has none. Its random stream includes five fixed price/order multiplier columns before manufacturing draws, matching the API.

## S5. Frozen price and screening basis

The following May 2026 costs use the original screening formulations and route assumptions, not the subsequently curated preparation records. Powder values are converted from the stored legacy USD/lb fields using 1 lb = 0.45359237 kg. An electrode candidate's powder cost is distinct from assembly cost per area. These observations do not establish equivalent activity or commercial quotation validity.

![Figure S1. Metal price history. Monthly averages from January 2019 to May 2026: (a) precious metals; (b) base metals. Prices are USD/kg and both axes are logarithmic. Histories are unsmoothed observations, not forecasts.](figures-note-2026-09-09/fig3_metal_prices.png)

| Family | Candidate | Powder cost (USD/kg) | Environmental mass coverage (%) |
|---|---|---:|---:|
| aem-electrolyzer-oer | Cr-doped amorphous NiFe route | 88.7608 | 100.00 |
| aem-electrolyzer-oer | Seed-assisted NiFe anode | 79.5137 | 100.00 |
| aem-electrolyzer-oer | NiCo2O4 spinel anode | 75.9109 | 100.00 |
| aem-electrolyzer-oer | NiFe-LDH scalable anode | 70.0902 | 100.00 |
| ammonia-cracking | Co/MgO-La2O3 mid-cost route | 10.4523 | 100.00 |
| ammonia-cracking | Ni-MgO/CeO2 interface | 12.8157 | 100.00 |
| ammonia-cracking | Ni/gamma-Al2O3 baseline | 9.6062 | 100.00 |
| ammonia-cracking | Ru/MgO premium | 2790.9583 | 100.00 |
| ammonia-synthesis | Cs-promoted Co3Mo3N nitride | 118.7672 | 97.98 |
| ammonia-synthesis | Promoted fused-iron (magnetite/wustite) baseline | 11.1847 | 96.47 |
| ammonia-synthesis | Cs/Ba-promoted Ru on graphitized carbon (KAAP-type) | 6530.4608 | 8.00 |
| ammonia-synthesis | Ru/CaFH low-temperature architecture | 10564.7251 | 12.00 |
| co2-electroreduction | Ag CO-selective MEA cathode | 4101.4184 | 100.00 |
| co2-electroreduction | Cu multicarbon CO2RR cathode | 61.8511 | 100.00 |
| co2-electroreduction | Sn formate CO2RR cathode | 95.1356 | 100.00 |
| co2-electroreduction | Au CO-selective CO2RR cathode | 281017.0718 | 100.00 |
| co2-methanation | Ni/CeO2 low-temperature route | 10.6186 | 100.00 |
| co2-methanation | Ni/Al2O3 baseline | 11.9757 | 100.00 |
| co2-methanation | Ru/layered titanate route | 3877.2098 | 5.00 |
| co2-methanation | Ru/MnOx photothermal route | 3878.5315 | 5.00 |
| co2-methanol | Cu/ZnO/Al2O3 baseline | 18.1024 | 100.00 |
| co2-methanol | Cu/ZrOx-MgO interface route | 12.8794 | 79.00 |
| co2-methanol | In2O3-ZrO2 low-temperature route | 303.3056 | 100.00 |
| co2-methanol | Pd/In2O3 promoted oxide | 1020.7473 | 100.00 |
| co2-to-formate | PdAg / N-doped carbon | 4416.2301 | 10.00 |
| co2-to-formate | Single-atom Ru on Mg-Al LDH | 579.7370 | 0.50 |
| co2-to-formate | Ru-pincer (Sanford / Beller-style) | 37236.9820 | 30.00 |
| co2-to-formate | Ir-pincer (Tanaka / Nozaki anchor) | 164689.0396 | 30.00 |
| co-prox | CuO-CeO2 (base-metal option) | 26.7652 | 100.00 |
| co-prox | Fe-promoted Pt/Al2O3 (fuel-processor standard) | 639.0068 | 100.00 |
| co-prox | Au/TiO2 nanogold (low-temperature) | 5893.9647 | 100.00 |
| dry-reforming | Ni-Co/Al-Mg-O bimetallic | 13.1709 | 9.50 |
| dry-reforming | Ni/CeO2 single-site route | 12.1927 | 100.00 |
| dry-reforming | Ni-zeolite stabilized route | 12.0646 | 12.00 |
| dry-reforming | Ir@CeO2-x premium | 2179.5878 | 100.00 |
| ethylene-epoxidation | Ag-Cs / Al2O3 (industrial standard) | 522.9759 | 99.95 |
| ethylene-epoxidation | Ag / alpha-Al2O3 baseline | 522.3891 | 100.00 |
| ethylene-epoxidation | Cu-Ag/alpha-Al2O3 (DFT-designed alloy) | 539.3653 | 99.70 |
| ethylene-epoxidation | Ag-Cs-Re / Al2O3 (modern HSE) | 558.0821 | 99.95 |
| fischer-tropsch-synthesis | Fe / SiO2 lower-olefin FT | 11.4116 | 30.00 |
| fischer-tropsch-synthesis | Precipitated Fe-Cu-K (Sasol-class) | 14.6014 | 91.00 |
| fischer-tropsch-synthesis | Co / Al2O3 FT (commercial baseline) | 32.4728 | 100.00 |
| fischer-tropsch-synthesis | Co / CNT structured FT | 89.1113 | 15.00 |
| formic-acid-dehydrogenation | Co-SAs/NPs@NC route | 22.5899 | 3.00 |
| formic-acid-dehydrogenation | Pt-Mo ensemble route | 3081.2293 | 5.00 |
| formic-acid-dehydrogenation | Pd/C baseline | 3807.3101 | 5.00 |
| formic-acid-dehydrogenation | Au-Pd in amine-grafted MIL-101 | 7853.1905 | 4.00 |
| fuel-cell-orr | Fe-N-C PGM-free cathode | 16.0913 | 2.00 |
| fuel-cell-orr | Pt-Co intermetallic cathode | 18886.2868 | 30.00 |
| fuel-cell-orr | Pt/C baseline cathode | 18522.1982 | 20.00 |
| fuel-cell-orr | PtNi octahedra (mass-activity ceiling) | 83318.5611 | 80.00 |
| glycerol-electrooxidation | NiOOH non-noble glycerol anode | 47.2971 | 100.00 |
| glycerol-electrooxidation | Pt / C glycerol anode | 22406.7422 | 20.00 |
| glycerol-electrooxidation | Pt-Bi DHA-selective anode | 50258.8582 | 47.50 |
| glycerol-electrooxidation | Au / C glycerol anode (selectivity) | 56250.1089 | 20.00 |
| hydrodeoxygenation | CoMoS / Al2O3 sulfide HDO | 23.9371 | 100.00 |
| hydrodeoxygenation | NiMo / carbon (acid-free) | 29.1162 | 15.00 |
| hydrodeoxygenation | Pt / SiO2 HDO | 1039.2192 | 1.00 |
| hydrodeoxygenation | Ru/C noble-metal route | 4229.4993 | 5.00 |
| hydrogen-evolution-reaction | NiMo alkaline HER cathode | 69.2432 | 100.00 |
| hydrogen-evolution-reaction | MoS2 acidic HER cathode | 81.1098 | 100.00 |
| hydrogen-evolution-reaction | Pt/C HER cathode (PEM) | 20415.5978 | 20.00 |
| hydrogen-evolution-reaction | Ru@C2N pH-universal cathode | 27439.4750 | 30.00 |
| methane-pyrolysis | Activated-carbon consumable catalyst | 5.3619 | 0.00 |
| methane-pyrolysis | Fe/Al2O3 higher-temperature route | 10.0685 | 100.00 |
| methane-pyrolysis | High-loading Ni/SiO2 | 27.3622 | 75.00 |
| methane-pyrolysis | Molten Ni-Bi alloy media | 52.4974 | 27.00 |
| methanol-to-olefins | H-ZSM-5 (MTH baseline) | 12.8155 | 0.00 |
| methanol-to-olefins | Zn / ZSM-5 (aromatics-leaning) | 13.1541 | 3.00 |
| methanol-to-olefins | SAPO-34 chabazite (DMTO baseline) | 31.8927 | 0.00 |
| methanol-to-olefins | Nanosized SAPO-34 (lifetime play) | 34.7792 | 0.00 |
| nh3-scr | V2O5-WO3/TiO2 monolith (stationary standard) | 13.4658 | 100.00 |
| nh3-scr | Fe-ZSM-5 high-temperature variant | 11.3778 | 2.00 |
| nh3-scr | Cu-SSZ-13 (diesel aftertreatment standard) | 43.4765 | 2.50 |
| nitrogen-reduction-reaction | Lithium-mediated NRR cathode | 75.7325 | 100.00 |
| nitrogen-reduction-reaction | Plasma-NRR ammonia route | 73.7277 | 0.00 |
| nitrogen-reduction-reaction | Aqueous NRR research anchor (Cu) | 75.2034 | 100.00 |
| nitrogen-reduction-reaction | Li-mediated flow cell with proton shuttle | 128.6827 | 0.00 |
| olefin-metathesis | WO3 / SiO2 (Lummus OCT) | 14.0428 | 7.00 |
| olefin-metathesis | MoO3 / SiO2-Al2O3 emerging | 24.2224 | 8.00 |
| olefin-metathesis | W-H/Al2O3 single-site hydride | 20.8809 | 100.00 |
| olefin-metathesis | Re2O7 / Al2O3 mild-condition | 250.0110 | 100.00 |
| pem-electrolyzer-oer | Low-Ir interface-engineered PEM route | 568137.6982 | 100.00 |
| pem-electrolyzer-oer | Ru-rich acidic OER route | 403860.4635 | 100.00 |
| pem-electrolyzer-oer | IrO2/TiO2 supported anode | 164456.7105 | 100.00 |
| pem-electrolyzer-oer | IrO2 PEM anode baseline | 568136.8646 | 100.00 |
| photocatalytic-co2-reduction | TiO2 photocatalyst (UV anchor) | 22.4838 | 100.00 |
| photocatalytic-co2-reduction | g-C3N4 / SnS2 Z-scheme | 57.0411 | 0.00 |
| photocatalytic-co2-reduction | Monoclinic BiVO4 (visible-light oxide) | 75.2019 | 0.00 |
| photocatalytic-co2-reduction | Cu2O / MOF heterojunction | 142.5976 | 40.00 |
| photocatalytic-water-splitting | Pt / TiO2 cocatalyst | 1161.1655 | 100.00 |
| photocatalytic-water-splitting | TiO2 (anatase) baseline | 22.4838 | 100.00 |
| photocatalytic-water-splitting | g-C3N4 metal-free photocatalyst | 43.4066 | 0.00 |
| photocatalytic-water-splitting | SrTiO3:Al with Rh/Cr2O3 + CoOOH | 6744.6335 | 2.00 |
| propane-dehydrogenation | CrOx/Al2O3 (Catofin-type) | 7.9962 | 79.50 |
| propane-dehydrogenation | h-BN ODHP route | 59.0120 | 0.00 |
| propane-dehydrogenation | Pt-Sn / Al2O3 (Oleflex-style) | 450.1581 | 100.00 |
| propane-dehydrogenation | PtZn intermetallic / zeolite | 515.6427 | 1.50 |
| rwgs | Cu/CeO2 baseline | 12.3734 | 100.00 |
| rwgs | Mo2N high-temperature route | 73.9741 | 100.00 |
| rwgs | Cs-Fe-Cu/Al2O3 high-temperature route | 18.1509 | 99.00 |
| rwgs | Pt/TiO2 premium | 1914.8446 | 100.00 |
| selective-acetylene-hydrogenation | NiZn intermetallic (non-Pd) | 13.0930 | 100.00 |
| selective-acetylene-hydrogenation | Pd-Cu single-atom alloy | 22.5652 | 100.00 |
| selective-acetylene-hydrogenation | Pd / Al2O3 baseline | 33.5268 | 100.00 |
| selective-acetylene-hydrogenation | Pd-Ag bimetallic (front-end style) | 40.5472 | 100.00 |
| steam-methane-reforming | Ni on calcium aluminate (industrial baseline) | 12.4299 | 14.50 |
| steam-methane-reforming | Sn/Ni surface alloy (coking-resistant) | 10.7092 | 100.00 |
| steam-methane-reforming | Rh/Al2O3 compact-reformer route | 5961.2564 | 100.00 |
| syngas-methanol | Cu/ZnO/Al2O3 (industrial workhorse) | 20.0202 | 100.00 |
| syngas-methanol | Ga-promoted Cu/ZnO (Zn-coverage engineering) | 36.1395 | 97.00 |
| syngas-methanol | Pd/ZnO intermetallic alternative | 1919.3189 | 100.00 |
| water-gas-shift | Cu/ZnO/Al2O3 baseline | 17.1054 | 100.00 |
| water-gas-shift | Co-CeO2 interface route | 24.6225 | 100.00 |
| water-gas-shift | Fe2O3-Cr2O3(-CuO) high-temperature shift | 15.0009 | 87.62 |
| water-gas-shift | Pt/CeO2 premium | 2388.8929 | 100.00 |

Ranking calculations use the original four criterion weights and assigned route/performance scores retained in the frozen methods and robustness files. The complete 0.05 weight grid contains 1,771 nonnegative combinations summing to one. With 89 months and 30 families, it defines 4,728,570 scenarios. Support prices remain at baseline in monthly metal-price tests. Candidate removal is tested both with recomputed and retained cost normalization ranges. Score tests lower the baseline candidate and raise alternatives by 2, 5 or 10 points, bounded by 0 and 100. Frequencies are conditional on these enumerated scenarios. No probability distribution for future market prices or catalyst performance is inferred.

## S6. Preparation evidence and unresolved inputs

The library has 92 source-specific preparations from 71 primary sources. Of 116 screening candidates, 75 link to at least one preparation; 41 have no curated preparation. Bibliographic verification covers 401 DOIs. Links may describe variants. No candidate has jointly verified catalog composition, complete preparation, utilities, recovered output and prices. A source_mismatch flag is retained for discrepancies even where a related preparation is available.

| Reaction family | Candidates | With preparation | Source mismatch flagged |
|---|---:|---:|---:|
| aem-electrolyzer-oer | 4 | 2 | 2 |
| ammonia-cracking | 4 | 2 | 1 |
| ammonia-synthesis | 4 | 3 | 0 |
| co-prox | 3 | 2 | 0 |
| co2-electroreduction | 4 | 4 | 1 |
| co2-methanation | 4 | 3 | 3 |
| co2-methanol | 4 | 3 | 3 |
| co2-to-formate | 4 | 1 | 0 |
| dry-reforming | 4 | 4 | 1 |
| ethylene-epoxidation | 4 | 1 | 0 |
| fischer-tropsch-synthesis | 4 | 2 | 0 |
| formic-acid-dehydrogenation | 4 | 3 | 1 |
| fuel-cell-orr | 4 | 3 | 2 |
| glycerol-electrooxidation | 4 | 4 | 0 |
| hydrodeoxygenation | 4 | 2 | 1 |
| hydrogen-evolution-reaction | 4 | 3 | 0 |
| methane-pyrolysis | 4 | 3 | 0 |
| methanol-to-olefins | 4 | 2 | 0 |
| nh3-scr | 3 | 3 | 0 |
| nitrogen-reduction-reaction | 4 | 4 | 0 |
| olefin-metathesis | 4 | 1 | 0 |
| pem-electrolyzer-oer | 4 | 4 | 0 |
| photocatalytic-co2-reduction | 4 | 1 | 1 |
| photocatalytic-water-splitting | 4 | 3 | 0 |
| propane-dehydrogenation | 4 | 3 | 2 |
| rwgs | 4 | 2 | 3 |
| selective-acetylene-hydrogenation | 4 | 1 | 3 |
| steam-methane-reforming | 3 | 0 | 0 |
| syngas-methanol | 3 | 2 | 0 |
| water-gas-shift | 4 | 4 | 2 |

Mutually exclusive catalog assessment counts: screening_only: 34; source_mismatch: 26; variant_available: 56.

The companion preparation-evidence document and JSON contain all candidate assessments, source titles and DOIs, section locators, reported operation inputs, per-field evidence, transfer boundaries and unresolved values. The final targeted lookup rechecked 101 existing citations for 42 then-unlinked candidates; nine accessible texts were assessed. A failed public-copy lookup does not establish that no free source exists elsewhere. Kelvin-to-Celsius and time conversions are explicit. Overnight, room temperature, approximate values and unspecified recovery remain unquantified. Primary articles, third-party SI files and private author attachments are not redistributed.

Operating references preserve geography, period and basis. EIA electricity averages can be selected as explicit scenarios; BLS wage statistics and manufacturer connected-load ratings remain references, not measured batch costs or average operating power. Actual staffing, utility consumption and supplier prices require separate evidence.

## S7. Reproduction and data files

Run from the supplied COMET source root with its declared project dependencies. No paid data access is needed to regenerate the frozen analyses. Regeneration reads stored inputs; refreshing an external source is a separate operation. The software version label alone does not identify these local changes; the per-file checksums in the accompanying package identify the supplied source snapshot.

```text
python scripts/reproduce_manufacturing_study.py --check
python scripts/build_manufacturing_literature_review.py --check
python -m scripts.build_note_si --check
python scripts/draw_application_note_figures.py
python scripts/draw_application_note_figures.py --lang ko
python scripts/build_application_note.py --check
python -m pytest backend/tests/test_application_note.py -q
python -m ruff check scripts/
```

The manufacturing regression is `backend/tests/test_manufacturing_study.py`. It compares independent arithmetic with the calculation, sensitivity and Monte Carlo APIs. Source fidelity, missing-input handling, persistence, transfers and comparisons have separate regression tests. Native PowerPoint source decks and export manifests identify conceptual-artwork labels; numerical panels come from frozen JSON. The TOC uses programmatically drawn artwork without generative images.

| Input record | SHA-256 of supplied file |
|---|---|
| docs/paper/manufacturing-study-2026-09-15/manufacturing_study.json | 81ecbddedf8a70f71490fe87ed113aff5f8928739112f170ffd0a32b1f9341f8 |
| backend/data/manufacturing_literature.json | 11baf75cf1b2d175083b3e53703a5ebe93e54978bc0631e4356f062e6e4b29c6 |
| backend/data/manufacturing_operating_references.json | cce47f24732a494453eef41c0df1b4d0034ef2309039ce49253a304cd21690c3 |
| docs/paper/submission-2026-09-08/all_families_2026-09-08.json | c29a4228daffdad0fce84a1371a8407c80e78796c046438f414fd04697e5fd27 |
| docs/paper/robustness-2026-09-08/decision_robustness.json | 1b3cf44a148cf2b95435d6148b75d4f12f915c1c58c8743ef106821c9bd28059 |
| docs/paper/methods-2026-09-09/methods_study.json | 3e0334cae853187259e65d147375c1e2b68361b42b8cd9a75dd6682bbf9725ca |

Companion documents: `manufacturing-literature-2026-09-14.md` (complete preparation evidence) and `application-note-2026-09-09.md` (main article and reference list). Machine-readable JSON retains additional rows and original units; publication tables and plots use kg-based powder costs. Software is under PolyForm Noncommercial 1.0.0; third-party source terms remain applicable.
