# Supporting Information

COMET: Catalyst Overall Manufacturing Estimation Tool

## S1. Calculation methods and boundaries

This Supporting Information describes the manufacturing calculation, the stated batch conditions, numerical verification, screening results with library loadings and production scales, calculator parametric analyses, observed-price and preparation-method cost crossovers, ranking sensitivity, first-ranked candidates under current quotations, the documentation of literature preparations, the screened published prices and application views. The August 2026 screening results retain their original formulations and assumptions. The later preparation review does not retrospectively validate those formulations. The new manufacturing example is a hypothetical software demonstration, not an experimental catalyst cost or a comparison of matched catalytic performance.

The screening calculations use the published Step Method and its cost-accounting framework.<sup>1,2</sup> A component with mass fraction w in the catalyst, mass fraction f in the pure precursor, precursor purity p and retention y requires w/(f p y) kg of precursor per kg of catalyst. Table S1 compares every line of the three demonstration cases of the method with the COMET calculation from the published conditions and prices.<sup>1</sup> The lines before the margin agree within the rounding of the published table. For Ni/Al₂O₃ the published table applies a margin of 33% of the pre-margin cost, whereas COMET applies the production-scale correlation of the same source, which gives 24.17% at this production scale. For the fluid catalytic cracking (FCC) catalyst the source states an effective production rate of 60,781.4 kg/day in place of the nominal rate, and Table S1 uses that rate. Its margin differs in the same way (11% of the pre-margin cost in the table, 12.83% from the correlation). Prices are converted from the published values per pound.

Table S1. Line-by-line reproduction of the published Step Method examples (published value / COMET).

| Line | 2 wt% Pt/C | 21 wt% Ni/Al₂O₃ | FCC catalyst |
|---|---:|---:|---:|
| Hourly step cost (USD/h) | 390 / 390 | 1,200 / 1,200 | 6,725 / 6,725 |
| Campaign duration (d) | 2.50 / 2.50 | 3.00 / 3.00 | 4.00 / 3.99 |
| Campaign cost (USD) | 23,400 / 23,400 | 86,400 / 86,400 | 645,600 / 643,191 |
| Processing cost (USD/kg) | 12.90 / 12.90 | 4.76 / 4.76 | 3.55 / 3.55 |
| Materials and processing (USD/kg) | 36.49 / 36.49 | 30.95 / 30.95 | 4.34 / 4.32 |
| G&A (USD/kg) | 1.83 / 1.82 | 1.54 / 1.55 | 0.22 / 0.22 |
| SARD (USD/kg) | 1.92 / 1.92 | 1.63 / 1.63 | 0.22 / 0.23 |
| Margin (USD/kg) | 20.11 / 20.11 | 11.27 / 8.25 | 0.53 / 0.61 |
| Selling price (USD/kg) | 60.34 / 60.34 | 45.39 / 42.37 | 5.31 / 5.37 |

G&A, general and administrative; SARD, sales, administrative, research and distribution. The Pt/C prices exclude platinum value.

In the batch calculation, purchases replace composition-based materials costs and operation costs replace Step Method processing costs. For each operation, electricity is measured kWh or the sum of mean power multiplied by ramp, hold and additional durations. For temperatures in °C and a ramp rate in °C/min, eq S1 gives the ramp duration in hours. Equipment occupancy is charged for the full entered operation duration; operator labor is entered separately. Gas volume is flow multiplied by its selected duration, using matching reference conditions for flow and price. Temperature, stirring speed and pressure are retained as preparation conditions; they do not infer equipment power, staffing, chemical yield or performance.

Intermediate charges are allocated by used/recovered mass or used/prepared volume of a homogeneous solution, with successive fractions multiplied along a chain. An explicit whole-batch option assigns the full incurred expenditure to its destination before subsequent transfers. Actual operation times and incurred expenditures remain distinct from their allocated shares. Unknown recovery prevents proportional allocation. Branching transfers, co-products and density-based conversions are not inferred. Figure S1 illustrates the allocation chain: a solution aliquot charged by volume fraction, an intermediate solid transferred by mass fraction, and the final dry batch that carries the allocated shares.

![Figure S1. Intermediate transfers. Conceptual sequence of a solution aliquot (volume fraction), an intermediate solid transfer (mass fraction) and the final dry batch used in eq S5. The drawing is conceptual and contains no numerical result.](figures-si-2026-09-16/figS1_allocation.png)

Equations S1–S6 define the calculation. General and administrative (G&A) and sales, administrative, research and distribution (SARD) overheads are applied sequentially before the selling margin. The example excludes disposal, analytical testing, waste credits, catalyst use, tax, freight and any equipment cost not represented in the stated occupancy rate. Occupancy rates are assumed aggregate charges, not measured depreciation or purchase prices. Unknown required conditions are not treated as zero. Dry powder mass is not an electrode-area denominator.

tᵣ = |T₁ − T₀|/(60r)    (S1)

Eᵢ = Σⱼ Pᵢⱼtᵢⱼ    (S2)

Vᵢ = 60Fᵢtᵍᵢ/1000    (S3)

Bᵢ = Bᵖᵢ + pₑEᵢ + qᵢtᵢ + pₗℓᵢ + pᵍᵢVᵢ + Aᵢ    (S4)

C = (Σᵢ aᵢBᵢ)/M    (S5)

P = C(1 + g)(1 + s)/(1 − m)    (S6)

In eq S1, T₀ and T₁ are the initial and target temperatures and r is the ramp rate. In eq S2, Eᵢ is operation electricity (kWh), Pᵢⱼ is mean power (kW), and tᵢⱼ is the duration (h) of phase j, including any explicitly powered additional period. Measured electricity can replace eq S2. In eq S3, Fᵢ is gas flow (L/min), tᵍᵢ is its selected duration (h), and Vᵢ is volume (m³); flow and price must refer to the same temperature and pressure.

In eq S4, Bᵢ is incurred expenditure (USD), Bᵖᵢ is purchases assigned to the operation (USD), pₑ is electricity price (USD/kWh), qᵢ is equipment occupancy rate (USD/h), tᵢ is full occupancy (h), pₗ is labor rate (USD/person-hour), ℓᵢ is attendance (person-hour), pᵍᵢ is gas price (USD/m³), and Aᵢ is an explicit additional charge (USD). Sums over multiple gases or purchases are implicit. Repeated operations contribute their incurred expenditure for each repetition. In eq S5, aᵢ is the dimensionless share allocated to the final batch and M is its recovered dry mass (kg); direct final-batch operations have aᵢ = 1. For proportional transfers, aᵢ is the product of used/recovered mass fractions or used/prepared solution-volume fractions along the transfer chain. Whole-batch charging contributes a factor of one at that transfer. In eq S6, C is manufacturing cost (USD/kg), P is selling price (USD/kg), and g, s and m are dimensionless G&A, SARD and selling-margin fractions.

## S2. Stated batch conditions

Every numerical value below is an assumption chosen for arithmetic verification. The example does not identify a specific active phase or precursor chemistry. The dry product mass is specified independently; precursor stoichiometry and material yield are not inferred. The composition entries of the application are inactive for the purchase-based materials calculation.

Tables S2 and S3 specify the operating conditions and purchases used in eqs S1–S6. Final dry product mass: 0.030 kg. Electricity: 0.10 USD/kWh. Labor: 10.00 USD/person-hour. G&A and SARD: 0.05 and 0.05; selling margin: 0.10. One batch is evaluated. The 2025 price-basis fields do not apply an index escalation to this direct batch calculation.

All thermal operations start at 20 °C and ramp at 5 °C/min. Each includes one additional hour of passive cooling/handling with explicitly zero additional electricity but continued equipment occupancy. Cooling is a stated duration, not a heat-transfer calculation. Reduction gas flows throughout ramp, hold and additional time at 0.1 L/min and costs 10 USD/m³; both flow and price refer to 0 °C and 1 atm. Its chemical composition is unspecified because this is an arithmetic scenario.

Table S2. Assumed operating conditions for the 0.030 kg manufacturing example.

| Operation | Hold target (°C) | Hold or mixing (h) | Ramp / hold power (kW) | Equipment (USD/h) | Attendance (person-h) |
|---|---:|---:|---|---:|---:|
| Impregnation | Not assigned | 2 | Constant 0.05 | 1 | 0.25 |
| Drying | 120 | 4 | 0.4 / 0.25 | 0.8 | 0.1 |
| Calcination | 500 | 3 | 2 / 1.2 | 3 | 0.1 |
| Reduction | 400 | 2 | 1.5 / 0.6 | 2 | 0.25 |

Table S3. Assumed purchases charged at impregnation.

| Purchase at impregnation | Quantity | Unit price | Batch expenditure (USD) |
|---|---:|---:|---:|
| Specified precursor solution (illustrative) | 5 mL | 2 USD/mL | 10.0000 |
| Support (illustrative) | 24 g | 0.05 USD/g | 1.2000 |
| Solvent (illustrative) | 100 mL | 0.01 USD/mL | 1.0000 |

## S3. Independent arithmetic verification

Tables S4 and S5 report an independent scalar evaluation of eqs S1–S6. Thermal durations include ramp, hold and the additional hour. The application programming interface (API) produces the same baseline and endpoint results. The regression also checks the application's Monte Carlo summary (fixed random seed) and histogram counts.

Table S4. Calculated operation durations and electricity consumption.

| Operation | Occupancy (h) | Electricity (kWh) |
|---|---:|---:|
| Impregnation | 2.000000 | 0.100000 |
| Drying | 5.333333 | 1.133333 |
| Calcination | 5.600000 | 6.800000 |
| Reduction | 4.266667 | 3.100000 |

Table S5. Manufacturing-cost contributions, overheads and selling margin.

| Cost component | Contribution per batch (USD) | Per dry product (USD/kg) |
|---|---:|---:|
| Purchases | 12.200000 | 406.666667 |
| Electricity | 1.113333 | 37.111111 |
| Equipment occupancy | 31.600000 | 1053.333333 |
| Attended labor | 7.000000 | 233.333333 |
| Gas | 0.256000 | 8.533333 |
| Manufacturing cost | 52.169333 | 1738.977778 |
| G&A | 2.608467 | 86.948889 |
| SARD | 2.738890 | 91.296333 |
| Margin | 6.390743 | 213.024778 |
| Selling price | 63.907433 | 2130.247778 |

Manufacturing cost before overheads and margin is 1738.977778 USD/kg; selling price is 2130.247778 USD/kg. One extra calcination hour costs (1.2 kW × 0.1 USD/kWh + 3 USD/h)/0.030 kg × 1.05 × 1.05/0.90 = 127.40 USD/kg. Attendance does not change in this scenario.

## S4. Manufacturing sensitivity and uncertainty

Table S6 changes only the named condition at each endpoint; all other batch conditions remain fixed. Temperature does not determine an assumed power change. The dry-product-mass endpoints therefore assess cost allocation, not predicted chemical yields or scale economies.

Table S6. One-at-a-time sensitivity endpoints for the manufacturing example.

| Varied condition | Low | High | Selling price at low (USD/kg) | Selling price at high (USD/kg) |
|---|---:|---:|---:|---:|
| Dry output | 0.015 kg/batch | 0.045 kg/batch | 4260.4956 | 1420.1653 |
| Precursor price | 1.0 USD/mL | 3.0 USD/mL | 1926.0810 | 2334.4144 |
| Impregnation time | 1.0 h | 4.0 h | 2089.2103 | 2212.3227 |
| Drying hold | 2.0 h | 8.0 h | 2062.8729 | 2264.9977 |
| Calcination hold | 1.0 h | 6.0 h | 1875.4477 | 2512.4478 |
| Calcination power | 0.6 kW | 2.4 kW | 2122.8978 | 2144.9478 |
| Reduction hold | 1.0 h | 4.0 h | 2043.6812 | 2303.3810 |
| Electricity tariff | 0.05 USD/kWh | 0.2 USD/kWh | 2107.5173 | 2175.7088 |

Figure S2 plots the same endpoints as departures from the baseline selling price. Dry product mass dominates because the fixed batch expenditure is divided by the recovered mass; calcination power changes the price little because electricity is a small part of the assumed operating cost compared with equipment occupancy (Table S5).

![Figure S2. Sensitivity endpoints. Selling price at the low and high value of each condition in Table S6; the vertical line marks the baseline of 2130.25 USD/kg. Each bar changes one condition while all other batch conditions remain fixed.](figures-si-2026-09-16/figS2_sensitivity.png)

Figure 3(c) evaluates 21 calcination-hold values from 1 to 6 h at each of three dry masses (0.015, 0.030 and 0.045 kg), giving 63 scenarios. The machine-readable manufacturing data retain all 63 input–output pairs.

Monte Carlo uses seed 20260915 and 1000 trials. Independent uniform bounds are 0.024–0.036 kg dry product mass, 2–4 h calcination hold, 0.9–1.5 kW hold power and 0.06–0.12 USD/kWh. All other conditions are fixed. Successful/failed trials: 1000/0. Mean selling price is 2164.6042 USD/kg; the 5th and 95th percentiles are 1778.9261 and 2629.8509 USD/kg. These are scenario percentiles, not statistical confidence bounds. Individual sampled values and results are retained in the accompanying data file (JSON). The application ordinarily excludes and counts invalid combinations without truncation; this example has none. The accompanying reproduction instructions specify the random-number generator and the sampling order. Figure S3 shows the distribution of the trial results and the sampled dry product mass against the resulting selling price; the sampled dry product mass accounts for most of the spread.

![Figure S3. Monte Carlo samples. (a) Selling-price histogram of the 1000 trials (fixed random seed) with the mean (solid line) and the 5th and 95th percentiles (dashed lines). (b) Sampled dry product mass against selling price for the same trials. Bounds are scenario assumptions, not measured variability.](figures-si-2026-09-16/figS3_monte_carlo.png)

## S5. Price basis and screening results

The following August 2026 costs use the original screening formulations and route assumptions, not the subsequently documented preparation records. Table S7 reports estimated selling prices for 116 screening candidates with the active-metal loading (or, for bulk formulations, the active phase) and the production scale recorded in the library for each candidate; it does not report measured manufacturing costs. Each candidate is priced at its own library loading, which follows the cited source where it reports one and is otherwise an engineering assumption noted in the library; loadings are not normalized across candidates. Powder values are converted from the original USD/lb values using 1 lb = 0.45359237 kg, and production scales from short tons. An electrode candidate's powder price is distinct from assembly cost per area. These observations do not establish equivalent activity or commercial quotation validity.

Johnson Matthey<sup>3</sup> and Westmetall<sup>4</sup> supply current metal quotations. Figure S4 summarizes the monthly price histories from Johnson Matthey and the International Monetary Fund (IMF).<sup>5</sup> Environmental mass coverage is the fraction assigned a screening inventory factor, including compound proxies; it is not a measure of inventory accuracy.<sup>6</sup>

Reference metal prices are the August 2026 monthly averages. U.S. import unit values of support materials are published several months later, so each support uses its latest verified monthly value at or before that month (May 2026 to July 2026); the observation month is recorded with the price and no month is interpolated. Metals without a published monthly series keep their annual reference values.

![Figure S4. Metal price history. Monthly averages from January 2019 to August 2026: (a) precious metals; (b) base metals. Prices are USD/kg; both price axes use logarithmic scales. Histories are unsmoothed observations, not forecasts.](figures-si-2026-09-16/figS4_metal_prices.png)

Table S7. Library loadings, production scales, estimated powder selling prices and environmental mass coverage at August 2026 prices.

| Reaction family | Candidate model | Active metal or phase (wt%) | Production scale (kg) | Selling price (USD/kg) | Mass coverage (%) |
|---|---|---|---:|---:|---:|
| AEM OER (anion-exchange-membrane oxygen evolution reaction) | Cr-doped amorphous NiFe | Cr-doped amorphous NiFe 100 | 1,814.4 | 88.7608 | 100.00 |
| AEM OER (anion-exchange-membrane oxygen evolution reaction) | Seed-assisted NiFe | Seed-assisted NiFe 100 | 1,814.4 | 79.5137 | 100.00 |
| AEM OER (anion-exchange-membrane oxygen evolution reaction) | NiCo₂O₄ spinel | Ni 24.4; Co 49.1 | 18,143.7 | 74.8436 | 100.00 |
| AEM OER (anion-exchange-membrane oxygen evolution reaction) | NiFe layered double hydroxide | NiFe-LDH 100 | 1,814.4 | 70.0902 | 100.00 |
| Ammonia cracking | Co/MgO–La₂O₃ | Co 5 | 18,143.7 | 10.2438 | 100.00 |
| Ammonia cracking | Ni–MgO/CeO₂ interface | Ni 15 | 18,143.7 | 12.1490 | 100.00 |
| Ammonia cracking | Ni/γ-Al₂O₃ | Ni 12 | 18,143.7 | 9.0694 | 100.00 |
| Ammonia cracking | Ru/MgO | Ru 3 | 18,143.7 | 2925.7988 | 100.00 |
| Ammonia synthesis | Cs-promoted Co₃Mo₃N | Co 37 | 18,143.7 | 124.0850 | 97.98 |
| Ammonia synthesis | Promoted fused iron (magnetite/wüstite) | Fe 68.6 | 18,143.7 | 11.1794 | 96.47 |
| Ammonia synthesis | Cs/Ba-promoted Ru on graphitized carbon | Ru 8 | 18,143.7 | 6844.2796 | 8.00 |
| Ammonia synthesis | Ru/CaFH | Ru 12 | 18,143.7 | 11076.3861 | 12.00 |
| CO₂ electroreduction | Ag cathode for CO production | Ag 100 | 18,143.7 | 3448.6420 | 100.00 |
| CO₂ electroreduction | Cu cathode for multicarbon products | Cu 100 | 1,814.4 | 63.3415 | 100.00 |
| CO₂ electroreduction | Sn cathode for formate production | Sn 100 | 4,535.9 | 98.3738 | 100.00 |
| CO₂ electroreduction | Au cathode for CO production | Au 100 | 907.2 | 270492.0215 | 100.00 |
| CO₂ methanation | Ni/CeO₂ | Ni 10 | 18,143.7 | 10.3110 | 100.00 |
| CO₂ methanation | Ni/Al₂O₃ | Ni 20 | 18,143.7 | 11.2436 | 100.00 |
| CO₂ methanation | Ru/layered titanate | Ru 5 | 18,143.7 | 4064.8188 | 5.00 |
| CO₂ methanation | Ru/MnOₓ | Ru 5 | 18,143.7 | 4066.1405 | 5.00 |
| CO₂ hydrogenation to methanol | Cu/ZnO/Al₂O₃ | Cu 45 | 18,143.7 | 18.5993 | 100.00 |
| CO₂ hydrogenation to methanol | Cu/ZrOₓ–MgO interface | Cu 14 | 18,143.7 | 12.8926 | 79.00 |
| CO₂ hydrogenation to methanol | In₂O₃–ZrO₂ | In 55 | 18,143.7 | 303.3056 | 100.00 |
| CO₂ hydrogenation to methanol | Pd/In₂O₃ | Pd 0.75 | 18,143.7 | 986.8909 | 100.00 |
| CO₂ hydrogenation to formate | PdAg on N-doped carbon | Pd 5 | 1,814.4 | 4136.3381 | 10.00 |
| CO₂ hydrogenation to formate | Single-atom Ru on Mg–Al layered double hydroxide | Ru 0.5 | 1,814.4 | 606.5210 | 0.50 |
| CO₂ hydrogenation to formate | Ru pincer complex | Ru 30 | 453.6 | 38918.2585 | 30.00 |
| CO₂ hydrogenation to formate | Ir pincer complex | Ir 30 | 453.6 | 172878.4838 | 30.00 |
| CO-PROX (preferential CO oxidation) | CuO–CeO₂ | Cu 5.6 | 1,814.4 | 26.8499 | 100.00 |
| CO-PROX (preferential CO oxidation) | Fe-promoted Pt/Al₂O₃ | Pt 0.5 | 1,814.4 | 575.5767 | 100.00 |
| CO-PROX (preferential CO oxidation) | Au/TiO₂ nanoparticles | Au 2 | 1,814.4 | 5674.6684 | 100.00 |
| DRM (dry reforming of methane) | Ni–Co/Al–Mg–O | Ni 4; Co 5.5 | 18,143.7 | 13.0478 | 9.50 |
| DRM (dry reforming of methane) | Ni/CeO₂ single sites | Ni 8 | 18,143.7 | 11.9332 | 100.00 |
| DRM (dry reforming of methane) | Ni/zeolite | Ni 12 | 18,143.7 | 11.6755 | 12.00 |
| DRM (dry reforming of methane) | Ir@CeO₂₋ₓ | Ir 0.6 | 18,143.7 | 2289.2484 | 100.00 |
| Ethylene epoxidation | Ag–Cs/Al₂O₃ | Ag 15 | 45,359.2 | 441.1119 | 99.95 |
| Ethylene epoxidation | Ag/α-Al₂O₃ | Ag 15 | 45,359.2 | 440.5250 | 100.00 |
| Ethylene epoxidation | Cu–Ag/α-Al₂O₃ | Ag 14 | 18,143.7 | 455.6011 | 99.70 |
| Ethylene epoxidation | Ag–Cs–Re/Al₂O₃ | Ag 15 | 18,143.7 | 472.4052 | 99.95 |
| FTS (Fischer–Tropsch synthesis) | Fe/SiO₂ | Fe 30 | 45,359.2 | 11.4116 | 30.00 |
| FTS (Fischer–Tropsch synthesis) | Precipitated Fe–Cu–K | Fe 88 | 18,143.7 | 14.6266 | 91.00 |
| FTS (Fischer–Tropsch synthesis) | Co/Al₂O₃ | Co 20 | 45,359.2 | 32.3511 | 100.00 |
| FTS (Fischer–Tropsch synthesis) | Co on carbon nanotubes | Co 15 | 4,535.9 | 89.1113 | 15.00 |
| Formic acid dehydrogenation | Co single atoms/nanoparticles on N-doped carbon | Co 3 | 4,535.9 | 22.5899 | 3.00 |
| Formic acid dehydrogenation | Pt–Mo ensembles | Pt 3 | 4,535.9 | 2765.4290 | 5.00 |
| Formic acid dehydrogenation | Pd/C | Pd 5 | 4,535.9 | 3583.4818 | 5.00 |
| Formic acid dehydrogenation | Au–Pd in amine-grafted MIL-101 | Au 2; Pd 2 | 1,814.4 | 7524.6967 | 4.00 |
| ORR (oxygen reduction reaction) in fuel cells | Fe–N–C cathode | Fe 2 | 18,143.7 | 16.0913 | 2.00 |
| ORR (oxygen reduction reaction) in fuel cells | Pt–Co intermetallic cathode | Pt 20 | 18,143.7 | 16937.9738 | 30.00 |
| ORR (oxygen reduction reaction) in fuel cells | Pt/C cathode | Pt 20 | 18,143.7 | 16610.3025 | 20.00 |
| ORR (oxygen reduction reaction) in fuel cells | PtNi octahedra | Pt 70; Ni 10 | 18,143.7 | 74714.6942 | 80.00 |
| Glycerol electrooxidation | NiOOH anode | NiOOH 100 | 4,535.9 | 43.7543 | 100.00 |
| Glycerol electrooxidation | Pt/C anode | Pt 20 | 1,814.4 | 20097.1582 | 20.00 |
| Glycerol electrooxidation | Pt–Bi anode for dihydroxyacetone production | Pt 47.5 | 18,143.7 | 45069.4263 | 47.50 |
| Glycerol electrooxidation | Au/C anode | Au 20 | 907.2 | 54145.0988 | 20.00 |
| HDO (hydrodeoxygenation) | CoMoS/Al₂O₃ | Mo 12 | 18,143.7 | 24.8556 | 100.00 |
| HDO (hydrodeoxygenation) | NiMo/carbon | Mo 10 | 4,535.9 | 30.2851 | 15.00 |
| HDO (hydrodeoxygenation) | Pt/SiO₂ | Pt 1 | 4,535.9 | 933.6314 | 1.00 |
| HDO (hydrodeoxygenation) | Ru/C | Ru 5 | 18,143.7 | 4434.5406 | 5.00 |
| HER (hydrogen evolution reaction) | NiMo cathode (alkaline) | Ni 70 | 4,535.9 | 69.7715 | 100.00 |
| HER (hydrogen evolution reaction) | MoS₂ cathode (acidic) | MoS₂ 100 | 1,814.4 | 81.1098 | 100.00 |
| HER (hydrogen evolution reaction) | Pt/C cathode | Pt 20 | 4,535.9 | 18308.9733 | 20.00 |
| HER (hydrogen evolution reaction) | Ru@C₂N cathode | Ru 30 | 18,143.7 | 28769.7939 | 30.00 |
| Methane pyrolysis | Activated carbon | Activated carbon 100 | 18,143.7 | 5.3619 | 0.00 |
| Methane pyrolysis | Fe/Al₂O₃ | Fe 62 | 18,143.7 | 10.0077 | 100.00 |
| Methane pyrolysis | Ni/SiO₂ | Ni 75 | 18,143.7 | 24.9967 | 75.00 |
| Methane pyrolysis | Molten Ni–Bi alloy | Ni 27 | 18,143.7 | 51.7425 | 27.00 |
| MTO (methanol-to-olefins conversion) | H-ZSM-5 | H-ZSM-5 100 | 45,359.2 | 12.8155 | 0.00 |
| MTO (methanol-to-olefins conversion) | Zn/ZSM-5 | H-ZSM-5 97 | 18,143.7 | 13.1722 | 3.00 |
| MTO (methanol-to-olefins conversion) | SAPO-34 (chabazite) | SAPO-34 chabazite 100 | 45,359.2 | 31.8927 | 0.00 |
| MTO (methanol-to-olefins conversion) | Nanosized SAPO-34 | SAPO-34 chabazite (nano) 100 | 18,143.7 | 34.7792 | 0.00 |
| NH₃-SCR (selective catalytic reduction with ammonia) | V₂O₅–WO₃/TiO₂ monolith | V₂O₅ 2.5 | 18,143.7 | 13.5686 | 100.00 |
| NH₃-SCR (selective catalytic reduction with ammonia) | Fe-ZSM-5 | Fe 2 | 18,143.7 | 11.3778 | 2.00 |
| NH₃-SCR (selective catalytic reduction with ammonia) | Cu-SSZ-13 | Cu 2.5 | 18,143.7 | 43.5071 | 2.50 |
| NRR (nitrogen reduction reaction) | Plasma-assisted ammonia synthesis | Ni / steel (plasma-tolerant cathode) 100 | 1,814.4 | 70.0124 | 0.00 |
| NRR (nitrogen reduction reaction) | Li-mediated cathode | Cu (Li-cycle current collector) 100 | 907.2 | 77.3664 | 100.00 |
| NRR (nitrogen reduction reaction) | Cu in aqueous electrolyte | Cu 100 | 907.2 | 76.8373 | 100.00 |
| NRR (nitrogen reduction reaction) | Li-mediated flow cell with proton shuttle | Li-mediated GDE assembly (Li salt + phosphonium shuttle) 100 | 1,814.4 | 128.6827 | 0.00 |
| Olefin metathesis | WO₃/SiO₂ | W 7 | 45,359.2 | 13.8338 | 7.00 |
| Olefin metathesis | MoO₃/SiO₂–Al₂O₃ | Mo 8 | 4,535.9 | 24.9958 | 8.00 |
| Olefin metathesis | W–H/Al₂O₃ single-site hydride | W 4 | 1,814.4 | 20.6950 | 100.00 |
| Olefin metathesis | Re₂O₇/Al₂O₃ | Re 8 | 907.2 | 249.8159 | 100.00 |
| PEM OER (proton-exchange-membrane oxygen evolution reaction) | Low-Ir interface architecture | IrO₂ 100 | 18,143.7 | 568137.6982 | 100.00 |
| PEM OER (proton-exchange-membrane oxygen evolution reaction) | Ru-rich anode | RuO₂ 100 | 18,143.7 | 403860.4635 | 100.00 |
| PEM OER (proton-exchange-membrane oxygen evolution reaction) | IrO₂/TiO₂ anode | Ir 40 | 18,143.7 | 172764.3939 | 100.00 |
| PEM OER (proton-exchange-membrane oxygen evolution reaction) | IrO₂ anode | IrO₂ 100 | 18,143.7 | 568136.8646 | 100.00 |
| Photocatalytic CO₂ reduction | TiO₂ | TiO₂ (anatase) 100 | 4,535.9 | 22.4838 | 100.00 |
| Photocatalytic CO₂ reduction | g-C₃N₄/SnS₂ Z-scheme | g-C₃N₄ 60; SnS₂ 40 | 1,814.4 | 57.0411 | 0.00 |
| Photocatalytic CO₂ reduction | Monoclinic BiVO₄ | BiVO₄ 100 | 1,814.4 | 75.2019 | 0.00 |
| Photocatalytic CO₂ reduction | Cu₂O/metal–organic framework heterojunction | Cu (from Cu₂O) 40 | 907.2 | 143.2513 | 40.00 |
| Photocatalytic water splitting | Pt/TiO₂ | Pt 1 | 1,814.4 | 1045.6865 | 100.00 |
| Photocatalytic water splitting | TiO₂ (anatase) | TiO₂ (anatase) 100 | 4,535.9 | 22.4838 | 100.00 |
| Photocatalytic water splitting | g-C₃N₄ | g-C₃N₄ 100 | 1,814.4 | 43.4066 | 0.00 |
| Photocatalytic water splitting | SrTiO₃:Al with Rh/Cr₂O₃ and CoOOH | SrTiO₃:Al 98 | 1,814.4 | 6045.0016 | 2.00 |
| PDH (propane dehydrogenation) | CrOₓ/Al₂O₃ | Cr₂O₃ 19 | 45,359.2 | 7.8745 | 79.50 |
| PDH (propane dehydrogenation) | h-BN (oxidative dehydrogenation) | h-BN 100 | 18,143.7 | 59.0120 | 0.00 |
| PDH (propane dehydrogenation) | Pt–Sn/Al₂O₃ | Pt 0.5 | 45,359.2 | 404.3516 | 100.00 |
| PDH (propane dehydrogenation) | PtZn intermetallic/zeolite | Pt 0.5 | 9,071.8 | 465.7309 | 1.50 |
| RWGS (reverse water–gas shift) | Cu/CeO₂ | Cu 15 | 18,143.7 | 12.5551 | 100.00 |
| RWGS (reverse water–gas shift) | Mo₂N | Mo 65 | 18,143.7 | 79.7249 | 100.00 |
| RWGS (reverse water–gas shift) | Cs–Fe–Cu/Al₂O₃ | Fe 15 | 18,143.7 | 18.0583 | 99.00 |
| RWGS (reverse water–gas shift) | Pt/TiO₂ | Pt 2 | 18,143.7 | 1718.3038 | 100.00 |
| Selective acetylene hydrogenation | NiZn intermetallic | Ni 15 | 18,143.7 | 12.5335 | 100.00 |
| Selective acetylene hydrogenation | Pd–Cu single-atom alloy | Pd (single-atom) 0.01 | 4,535.9 | 22.0094 | 100.00 |
| Selective acetylene hydrogenation | Pd/Al₂O₃ | Pd 0.04 | 45,359.2 | 31.8211 | 100.00 |
| Selective acetylene hydrogenation | Pd–Ag bimetallic | Pd 0.04 | 45,359.2 | 37.7502 | 100.00 |
| SMR (steam methane reforming) | Ni on calcium aluminate | Ni 14.5 | 18,143.7 | 11.9839 | 14.50 |
| SMR (steam methane reforming) | Sn/Ni surface alloy | Ni 15 | 18,143.7 | 10.1285 | 100.00 |
| SMR (steam methane reforming) | Rh/Al₂O₃ | Rh 1 | 1,814.4 | 5342.1595 | 100.00 |
| Methanol synthesis from syngas | Cu/ZnO/Al₂O₃ | Cu 48 | 18,143.7 | 20.6626 | 100.00 |
| Methanol synthesis from syngas | Ga-promoted Cu/ZnO | Cu 47 | 18,143.7 | 36.6688 | 97.00 |
| Methanol synthesis from syngas | Pd/ZnO intermetallic | Pd 2.5 | 18,143.7 | 1806.4642 | 100.00 |
| WGS (water–gas shift) | Cu/ZnO/Al₂O₃ | Cu 40 | 18,143.7 | 17.5338 | 100.00 |
| WGS (water–gas shift) | Co–CeO₂ interface | Co 18 | 18,143.7 | 24.6228 | 100.00 |
| WGS (water–gas shift) | Fe₂O₃–Cr₂O₃(–CuO) | Fe 61.6 | 18,143.7 | 14.9844 | 87.62 |
| WGS (water–gas shift) | Pt/CeO₂ | Pt 2.5 | 18,143.7 | 2143.0777 | 100.00 |

Names identify the original screening models, not experimentally verified compositions or performance-equivalent catalysts. Loadings are the library values; a bulk formulation lists its active phase at 100 wt% or the stated split. Family membership follows the original screening library, including related reactions; it does not imply identical reaction conditions. g-C₃N₄ denotes graphitic carbon nitride; h-BN, hexagonal boron nitride; SAPO, silicoaluminophosphate. MIL-101, ZSM-5 and SSZ-13 retain their established material identifiers.

Figure 4(a)–(c) of the main article varies one calculator variable at a time for two alumina-supported catalysts prepared by incipient wetness impregnation. Table S8 lists the variables and the resulting selling prices at August 2026 prices. Production scales (the catalyst mass of one order) are entered in short tons and shown in kilograms; operations that are unavailable at the production scale of an order are replaced by the application's scale equivalents (a batch kiln for the continuous kiln at the small scale). Precious-metal value is part of the materials cost and carries overheads and margin; no spent-catalyst credit is applied. The selling price is linear in the metal price, so the ruthenium price at which the two catalysts cost the same per kilogram follows from two evaluations and was confirmed by a third. These analyses compare manufacturing cost only; they do not compare catalytic performance.

Table S8. Calculator parametric analyses at August 2026 prices.

| Catalyst | Varied quantity | Range | Selling price (USD/kg) |
|---|---|---|---|
| 20 wt% Ni/Al₂O₃ | Baseline (18,143.7 kg order) | — | 10.33 |
| Ni/Al₂O₃ | Metal loading | 5–30 wt% | 7.02–12.54 |
| 20 wt% Ni/Al₂O₃ | Production scale | 907.2–907,184.7 kg | 46.21–5.06 |
| 2 wt% Ru/Al₂O₃ | Baseline (18,143.7 kg order) | — | 1,480.36 |
| Ru/Al₂O₃ | Metal loading | 0.5–5 wt% | 374.52–3,692.03 |
| 2 wt% Ru/Al₂O₃ | Production scale | 907.2–907,184.7 kg | 1,993.12–1,289.17 |
| 20 wt% Ni/Al₂O₃ | Preparation method | 5 methods | 10.33–11.59 |

Nickel is priced at 16.75 USD/kg and ruthenium at 53,852 USD/kg. The preparation methods are: Incipient Wetness Impregnation; Excess-Solution (Wet) Impregnation; Deposition-Precipitation; Co-precipitation; Sol-Gel. The two baseline catalysts would cost the same per kilogram at a ruthenium price of 162 USD/kg, 0.30% of the August 2026 price; the lowest monthly ruthenium price of the 92-month record is 8,038 USD/kg.

Table S9 prices every supported-metal candidate of the powder-catalyst families (a candidate with an active metal and a support) with its library composition under each of the 5 preparation methods at 18,143.7 kg, on the August 2026 reference basis and without the route allowances of the screening library. Processing cost depends on the operation sequence and the production scale only, so the five methods span 1.26 USD/kg of selling price for every candidate, and a candidate can be the least expensive of its family under some assignment of methods exactly when its lowest price lies below the highest price of every other candidate; with the same method applied to every candidate, the cost order never changes. Candidates with a component role the calculator request does not accept are excluded: Pd–Cu single-atom alloy (host metal). Figure 4(f) of the main article shows the ammonia-cracking pair for every pair of methods. These are cost orders at equal catalyst mass; catalytic performance is not compared.

Table S9. Cost order under the five preparation methods at 18,143.7 kg.

| Reaction family | Candidates | Least expensive by materials | Materials difference to the next candidate (USD/kg) | Candidates that can be least expensive |
|---|---:|---|---:|---|
| Ammonia cracking | 4 | Ni/γ-Al₂O₃ | 0.81 | Co/MgO–La₂O₃; Ni–MgO/CeO₂ interface; Ni/γ-Al₂O₃ |
| Ammonia synthesis | 3 | Promoted fused iron (magnetite/wüstite) | 4,990.69 | Promoted fused iron (magnetite/wüstite) |
| CO₂ methanation | 4 | Ni/CeO₂ | 0.68 | Ni/CeO₂; Ni/Al₂O₃ |
| CO₂ hydrogenation to methanol | 4 | Cu/ZrOₓ–MgO interface | 4.59 | Cu/ZrOₓ–MgO interface |
| CO₂ hydrogenation to formate | 2 | Single-atom Ru on Mg–Al layered double hydroxide | 2,127.03 | Single-atom Ru on Mg–Al layered double hydroxide |
| CO-PROX (preferential CO oxidation) | 3 | CuO–CeO₂ | 330.09 | CuO–CeO₂ |
| DRM (dry reforming of methane) | 4 | Ni/CeO₂ single sites | 0.47 | Ni/CeO₂ single sites; Ni/zeolite |
| Ethylene epoxidation | 4 | Cu–Ag/α-Al₂O₃ | 4.93 | Cu–Ag/α-Al₂O₃ |
| FTS (Fischer–Tropsch synthesis) | 4 | Fe/SiO₂ | 2.02 | Fe/SiO₂ |
| Formic acid dehydrogenation | 4 | Co single atoms/nanoparticles on N-doped carbon | 1,818.09 | Co single atoms/nanoparticles on N-doped carbon |
| HDO (hydrodeoxygenation) | 4 | NiMo/carbon | 0.42 | CoMoS/Al₂O₃; NiMo/carbon |
| Methane pyrolysis | 3 | Fe/Al₂O₃ | 10.82 | Fe/Al₂O₃ |
| NH₃-SCR (selective catalytic reduction with ammonia) | 3 | Fe-ZSM-5 | 1.02 | Fe-ZSM-5 |
| Olefin metathesis | 4 | W–H/Al₂O₃ single-site hydride | 2.51 | W–H/Al₂O₃ single-site hydride |
| PDH (propane dehydrogenation) | 3 | CrOₓ/Al₂O₃ | 302.48 | CrOₓ/Al₂O₃ |
| RWGS (reverse water–gas shift) | 4 | Cu/CeO₂ | 5.60 | Cu/CeO₂ |
| Selective acetylene hydrogenation | 3 | NiZn intermetallic | 16.06 | NiZn intermetallic |
| SMR (steam methane reforming) | 3 | Ni on calcium aluminate | 0.21 | Ni on calcium aluminate; Sn/Ni surface alloy |
| Methanol synthesis from syngas | 3 | Cu/ZnO/Al₂O₃ | 11.61 | Cu/ZnO/Al₂O₃ |
| WGS (water–gas shift) | 4 | Fe₂O₃–Cr₂O₃(–CuO) | 1.47 | Fe₂O₃–Cr₂O₃(–CuO) |

Materials costs are per kilogram of catalyst. In 5 of the 20 families more than one candidate can be the least expensive.

Ranking calculations use the original four criterion weights and assigned route/performance scores retained in the archived methods and robustness files. The complete 0.05 weight grid contains 1,771 nonnegative combinations summing to one. With 92 months and 30 families, it defines 4,887,960 scenarios. Support prices remain at baseline in monthly metal-price tests. Candidate removal is tested both with recomputed and retained cost normalization ranges. Score tests lower the baseline candidate and raise alternatives by 2, 5 or 10 points, bounded by 0 and 100. Frequencies are conditional on these enumerated scenarios. No probability distribution for future market prices or catalyst performance is inferred. Route and performance scores are screening judgments assigned from the literature, not measured or predicted activity.

Figure 4(d) of the main article repeats the screening calculation for ammonia cracking under the 92 monthly metal-price states with formulations, production scales, route assumptions, support prices, price-source grades and route and performance scores fixed.<sup>3,5</sup> Figure 4(e) marks the lowest-cost candidate of every month in the 6 families where it changes. The numbers of months as the lowest-cost candidate are ammonia cracking: Co/MgO–La₂O₃ 53, Ni/γ-Al₂O₃ 39 (8 changes); dry reforming of methane: Ni–Co/Al–Mg–O 55, Ni/zeolite 26, Ni/CeO₂ single sites 11 (9 changes); water–gas shift: Cu/ZnO/Al₂O₃ 69, Fe₂O₃–Cr₂O₃(–CuO) 23 (13 changes); CO₂ electroreduction: Cu cathode for multicarbon products 60, Sn cathode for formate production 32 (7 changes); hydrogen evolution reaction: NiMo cathode (alkaline) 91, MoS₂ cathode (acidic) 1 (2 changes); nitrogen reduction reaction: Cu in aqueous electrolyte 77, Plasma-assisted ammonia synthesis 15 (1 change). Figure S5 shows the same recalculation for methane dry reforming and water–gas shift, where the lowest-cost candidate changes 9 and 13 times (8 times for ammonia cracking) while the balanced-weight recommendation of these families does not change. Panel (c) places the monthly states of ammonia cracking in the nickel–cobalt price plane: they cluster near the conditional equal-cost boundary, so modest cobalt moves change the lowest-cost candidate. The September–October 2025 cobalt price increase from 33.48 to 43.15 USD/kg also reverses the lowest-cost candidate in methane dry reforming while nickel is nearly unchanged. These are conditional model comparisons between screening candidates, not contemporaneous supplier quotations or performance comparisons.

![Figure S5. Observed-price cost crossovers. Costs (modeled selling prices) under the 92 monthly price states for the candidates that attain the lowest cost at any state in (a) methane dry reforming and (b) water–gas shift; lines connect observed states and do not locate a crossover date. (c) Conditional equal-cost boundary between Co/MgO–La₂O₃ (Co/Mg–La) and Ni/γ-Al₂O₃ (Ni/Al₂O₃) in the nickel–cobalt price plane; points are monthly states colored by the cheaper candidate, and the enlarged view names September and October 2025. Ni–Co/Al–Mg denotes Ni–Co/Al–Mg–O; Ni/CeO₂, Ni/CeO₂ single sites; Cu–ZnO, Cu/ZnO/Al₂O₃; Fe–Cr, Fe₂O₃–Cr₂O₃(–CuO) (Table S7). Other prices and engineering assumptions remain at reference values.](figures-si-2026-09-16/figS5_crossovers.png)

![Figure S6. Ranking sensitivity. (a) First-rank frequencies over the joint price and weight scenarios; dashed line, 50%. (b) Number of the 30 reaction families retaining the baseline candidate under each test. (c) Cost differences between the first-ranked candidates before and after candidate removal; negative values indicate less expensive replacements. PEM, proton exchange membrane; AEM, anion exchange membrane; OER, oxygen evolution reaction; ORR, oxygen reduction reaction; SCR, selective catalytic reduction; RWGS, reverse water–gas shift.](figures-si-2026-09-16/figS6_ranking_tests.png)

Figure S6 summarizes the ranking sensitivity. Panel (a) separates, for every family, how often the baseline candidate, its most frequent alternative and the other candidates rank first over the joint scenarios; the median baseline frequency is 58.95%. Panel (b) counts the families whose baseline candidate ranks first in at least half of the joint scenarios or is retained under candidate removal and under route/performance-score changes of 2, 5 and 10 points; passing one test does not establish robustness to the others. Removing one candidate that does not rank first changes the first-ranked candidate in 8 of 86 tests. In ammonia cracking, removing Ru/MgO (2,925.80 USD/kg) leaves the other costs unchanged but contracts their range, so renormalization changes the scores of Co/MgO–La₂O₃ and Ni/γ-Al₂O₃ from 89.4 and 87.4 to 72.2 and 87.4 and reverses their order; retaining the original range prevents every such reversal. Panel (c) gives 100 × (C₁ − C₀)/C₀ for the affected families, where C₀ and C₁ are the costs of the first-ranked candidates before and after removal.

The monthly recalculations hold price-source grades fixed. Replacing the August 2026 reference with the current quotations collected on 2026-09-21 also changes these grades: a metal without a current quotation falls back to a reference price, and each candidate's price-reliability score weights its sources by materials-cost share. With all other conditions unchanged, the first-ranked candidate changes in 4 families with balanced weights, 4 with cost-first weights, 10 with evidence-first weights and 4 with the performance weight set to zero. Table S10 lists the balanced-weight changes with the price-reliability and cost scores of the former first-ranked candidate. The current quotations are a single snapshot taken on that date, not a price history.

Table S10. First-ranked candidates under balanced weighting with the August 2026 reference prices and with the current quotations.

| Reaction family | First-ranked, August 2026 reference | First-ranked, current quotations | Former first-ranked: price reliability | Former first-ranked: cost score |
|---|---|---|---:|---:|
| Ammonia cracking | Co/MgO–La₂O₃ | Ni–MgO/CeO₂ interface | 85.2 → 56.7 | 100.0 → 100.0 |
| Ammonia synthesis | Cs-promoted Co₃Mo₃N | Promoted fused iron (magnetite/wüstite) | 83.5 → 56.8 | 99.0 → 99.2 |
| CO-PROX (preferential CO oxidation) | CuO–CeO₂ | Fe-promoted Pt/Al₂O₃ | 79.0 → 78.3 | 100.0 → 100.0 |
| DRM (dry reforming of methane) | Ni–Co/Al–Mg–O | Ni/CeO₂ single sites | 84.4 → 59.5 | 99.9 → 100.0 |

Scores are on a 0–100 scale; route and performance scores are unchanged between the two bases.

## S6. Literature preparation procedures and missing conditions

The library has 92 source-specific preparations from 71 primary sources. Of 116 screening candidates, 75 link to at least one preparation; 41 have no documented preparation. Bibliographic verification covers 401 digital object identifiers (DOIs). A linked preparation may be a related variant of the library formulation. No candidate has jointly verified library composition, complete preparation, utilities, recovered mass and prices. Table S11 counts source/formulation discrepancies even where a related preparation is available.

Table S11. Documented preparations and unresolved source/formulation discrepancies.

| Reaction family | Candidates | With documented preparation | Source mismatch noted |
|---|---:|---:|---:|
| AEM OER (anion-exchange-membrane oxygen evolution reaction) | 4 | 2 | 2 |
| Ammonia cracking | 4 | 2 | 1 |
| Ammonia synthesis | 4 | 3 | 0 |
| CO-PROX (preferential CO oxidation) | 3 | 2 | 0 |
| CO₂ electroreduction | 4 | 4 | 1 |
| CO₂ methanation | 4 | 3 | 3 |
| CO₂ hydrogenation to methanol | 4 | 3 | 3 |
| CO₂ hydrogenation to formate | 4 | 1 | 0 |
| DRM (dry reforming of methane) | 4 | 4 | 1 |
| Ethylene epoxidation | 4 | 1 | 0 |
| FTS (Fischer–Tropsch synthesis) | 4 | 2 | 0 |
| Formic acid dehydrogenation | 4 | 3 | 1 |
| ORR (oxygen reduction reaction) in fuel cells | 4 | 3 | 2 |
| Glycerol electrooxidation | 4 | 4 | 0 |
| HDO (hydrodeoxygenation) | 4 | 2 | 1 |
| HER (hydrogen evolution reaction) | 4 | 3 | 0 |
| Methane pyrolysis | 4 | 3 | 0 |
| MTO (methanol-to-olefins conversion) | 4 | 2 | 0 |
| NH₃-SCR (selective catalytic reduction with ammonia) | 3 | 3 | 0 |
| NRR (nitrogen reduction reaction) | 4 | 4 | 0 |
| Olefin metathesis | 4 | 1 | 0 |
| PEM OER (proton-exchange-membrane oxygen evolution reaction) | 4 | 4 | 0 |
| Photocatalytic CO₂ reduction | 4 | 1 | 1 |
| Photocatalytic water splitting | 4 | 3 | 0 |
| PDH (propane dehydrogenation) | 4 | 3 | 2 |
| RWGS (reverse water–gas shift) | 4 | 2 | 3 |
| Selective acetylene hydrogenation | 4 | 1 | 3 |
| SMR (steam methane reforming) | 3 | 0 | 0 |
| Methanol synthesis from syngas | 3 | 2 | 0 |
| WGS (water–gas shift) | 4 | 4 | 2 |

Mutually exclusive library assessment counts: No documented preparation: 34; Source/formulation discrepancy noted: 26; Source-specific preparation available: 56. The 75 candidates linked to a preparation comprise the 56 with a source-specific preparation and 19 of the noted discrepancies; the 41 without a documented preparation comprise the 34 unverified candidates and the remaining 7 noted discrepancies. Figure S7 shows these assessments by reaction family.

![Figure S7. Documentation status of the preparations. Number of screening candidates in each reaction family with a source-specific preparation, with a noted source/formulation discrepancy, or without a documented preparation. Families are ordered by the number of candidates with a source-specific preparation.](figures-si-2026-09-16/figS7_evidence.png)

The companion preparation document and data file contain all candidate assessments, source titles and DOIs, section references, reported operating conditions, the evidence for each value, transfer boundaries and unresolved values. The final targeted lookup rechecked 101 existing citations for 42 then-unlinked candidates; nine accessible texts were assessed. A failed public-copy lookup does not establish that no free source exists elsewhere. Kelvin-to-Celsius and time conversions are explicit. Overnight, room temperature, approximate values and unspecified recovery remain unquantified. Primary articles, third-party SI files and private author attachments are not redistributed.

Operating references preserve geography, period and basis. U.S. Energy Information Administration (EIA) electricity averages can be selected as explicit scenarios; U.S. Bureau of Labor Statistics (BLS) wage statistics and manufacturer connected-load ratings remain references, not measured batch costs or average operating power. Actual staffing, utility consumption and supplier prices require separate evidence.

Figure S8 illustrates the record structure preserved for each imported preparation: the located source passage, the structured record in which reported values and later user modifications are distinguished, and the resulting cost contribution with its checksum.

![Figure S8. Source-linked record. Conceptual sequence from a located passage in a source, through a structured record that distinguishes reported values from user modifications, to the cost contribution and its checksum. The drawing is conceptual.](figures-si-2026-09-16/figS8_provenance.png)

## S7. Published catalyst prices

The main article states that accuracy against industrial prices is not established. Table S12 lists the 10 cases screened on 2026-09-07 in a bounded search of free public sources (government cost reports, supplier product pages, filed commercial contracts, public procurement and open papers); a case is matched only when composition and grade, quantity and production scale, price date and currency, manufacturing route and yield, and cost boundary all agree with a library formulation, and an unknown dimension is not matched. None of the cases is matched. Retail pack prices are arithmetic normalizations, not bulk quotations; a market price is not a manufacturing cost; and the three demonstration cases of Table S1 are not independent validation. The search is bounded, so a failed match does not establish that no usable price exists elsewhere.

Table S12. Published price cases screened on 2026-09-07.

| Case | Type of source | Observation | Matched dimensions |
|---|---|---|---|
| Axens STR111 commercial catalyst base-price schedule (filed technology-transfer agreement) | signed contract price schedule | 16.5 EUR/kg, 2007-06 | price date and currency; cost boundary |
| 5 wt% Pt on Vulcan XC-72, 1 g public catalog offer | public catalog offer | 129 USD/pack (1 g pack), 2026-09-07 | price date and currency |
| 10 wt% Pt on Vulcan XC-72, 1 g public catalog offer | public catalog offer | 140 USD/pack (1 g pack), 2026-09-07 | price date and currency |
| 20 wt% Ni on Vulcan XC-72R Grade S, 1 g public catalog offer | public catalog offer | 145 USD/pack (1 g pack), 2026-09-07 | price date and currency |
| Chloroplatinic-acid preparation quote within a DOE catalyst-ink cost model | reported supplier quote | no usable price | none |
| Battelle reported bulk XC-72 carbon quote | reported supplier quote | 0.9 USD/kg, 2014-02 | price date and currency |
| Hog et al. 2026 mixed supplier/literature consumable-price regression | quoted and modeled data mixture | no usable price | price date and currency |
| BPCL 2013 VGO hydrodesulfurization catalyst procurement price form | unpriced tender | no usable price | none |
| ESTCP PCB demonstration-informed treatment-cost model | field cost informed model | no usable price | none |
| Mendoza Suarez and Tatarchuk 2025 catalyst-price sensitivity assumptions | assumed scenario price | 100 and 1500 USD/kg (assumed scenarios) | none |

Cases are identified by the screening record E01–E10; the five dimensions are composition and grade, quantity and production scale, price date and currency, manufacturing route and yield, and cost boundary.

## S8. Application interface

Figure S9 shows two views of COMET 1.4.0 recorded with a separate test database and without connection to price services. Panel (a) shows the source attached to one imported value: the purchased quantity of a reagent in the first operation of the PtSn/Al₂O₃ pellet preparation record imported from its Methods section,<sup>7</sup> with the citation, section, DOI, access date and recorded value. Unreported conditions of imported records remain blank. Panel (b) shows the evidence section of the result page for the illustrative batch of Tables S2–S5, with the time, electricity and the electricity, equipment, labor and gas costs of each operation.

![Figure S9. Application views. (a) Source record of one imported value in the preparation editor. (b) Operation-level time, electricity and cost contributions of the illustrative batch on the result page. Interface text is English; the Korean interface presents the same content.](figures-si-2026-09-16/figS9_interface.png)

## S9. References

[1] Baddour, F. G.; Snowden-Swan, L.; Super, J. D.; Van Allsburg, K. M. Estimating Precommercial Heterogeneous Catalyst Price: A Simple Step-Based Method. *Organic Process Research & Development* **2018**, *22* (12), 1599–1605. https://doi.org/10.1021/acs.oprd.8b00245.

[2] Van Allsburg, K. M.; Tan, E. C. D.; Super, J. D.; Schaidle, J. A.; Baddour, F. G. Early-stage evaluation of catalyst manufacturing cost and environmental impact using CatCost. *Nature Catalysis* **2022**, *5* (4), 342–353. https://doi.org/10.1038/s41929-022-00759-6.

[3] Johnson Matthey. PGM Prices and Trading. https://matthey.com/products-and-markets/pgms-and-circularity/pgm-management (accessed September 21, 2026).

[4] Westmetall. Market Data: Prices and LME Stocks. https://www.westmetall.com/en/markdaten.php (accessed September 21, 2026).

[5] International Monetary Fund. Primary Commodity Price System (PCPS), SDMX 2.1 data service. https://api.imf.org/external/sdmx/2.1/dataflow/IMF.RES/PCPS (accessed September 21, 2026).

[6] Nuss, P.; Eckelman, M. J. Life Cycle Assessment of Metals: A Scientific Synthesis. *PLoS ONE* **2014**, *9* (7), e101298. https://doi.org/10.1371/journal.pone.0101298.

[7] Niu, H.; Ma, J.; Gan, L.; Li, K. The Acid Roles of PtSn@Al₂O₃ in the Synthesis and Performance of Propane Dehydrogenation. *Molecules* **2024**, *29* (13), 2959. https://doi.org/10.3390/molecules29132959.
