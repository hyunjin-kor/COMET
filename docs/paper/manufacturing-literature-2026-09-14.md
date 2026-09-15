# Supporting information: catalyst preparation evidence

COMET Application Note. Review date: 2026-09-15.

## Scope and source assessment

The audit covers 116 screening candidates in 30 reaction families and 34 generic process templates. Crossref confirmed the bibliographic identity of 401 distinct DOIs. The curated library contains 89 named preparation records from 70 sources; 74 catalog candidates link to at least one record. A link may describe a different specimen and does not verify the catalog formulation.

Thirty reaction-family Europe PMC searches and individual candidate DOI checks were followed by 70 candidate-specific open-access searches. Eighteen initial and fourteen second-pass primary articles were screened, with public supplements where available. Search hits, bibliography, specimen preparation and complete operating costs remain separate assessments.

Read accessible primary Methods or supporting experimental sections for named specimens. Record numeric conditions only when explicit; separate synthesis from characterization, activation, performance tests and electrode fabrication.

This is a catalog-wide evidence audit, not a systematic review of every published synthesis. Failure to retrieve a public text is not proof that no method exists.

Numeric values were transcribed from the stated primary sections. Kelvin values were converted to Celsius by subtracting 273.15; explicit minutes and seconds were converted to hours. Overnight, room temperature, ranges, lower bounds and unspecified ramp rates were not assigned invented numeric values. Nominal loading, measured loading, precursor molar ratio and product mass fraction remain distinct. Input precursor mass is not recovered dry output.

## Use in COMET

Imports create editable records with the specimen, DOI and section locator. They retain the existing cost model. Powder batch costing is enabled only after the user supplies complete operating inputs, actual dry output and explicit costs. It replaces Step Method processing cost and does not add it twice. Electricity is measured kWh or input kW multiplied by time; gas volume and price require matching reference conditions. Temperature alone does not predict furnace consumption, yield or catalytic performance. Electrode preparations remain records and cannot use a dry-powder kg denominator. Published procedures are evidence records, not laboratory operating instructions.

Batch purchases can replace the entire composition-based materials bill. Quantities use kg, g, L, mL, mol, mmol or items, with prices in the same unit; molecular weight and solution density are not inferred. For intermediate batches, all preparation charges are allocated by mass transferred divided by mass recovered on the same material basis; unused recoverable inventory retains its share of cost. Alternatively, explicit whole-batch charging assigns the full expenditure to the receiving batch before any further transfer. Internal transfers are not purchased twice. Unknown masses block proportional allocation. Successive transfers multiply their fractions; each intermediate has one destination, and circular paths are rejected. Branching transfers and co-products require a separately defined boundary. Incurred and allocated costs, input sources and equations are preserved in the calculation trace and exports.

Manufacturing endpoint sensitivity changes one selected numeric cost input at a time. Monte Carlo uses independent uniform distributions within user-specified absolute bounds, with discrete integer draws for repetitions. Unselected inputs remain fixed. Linked gas durations follow the sampled operation time; temperature does not infer power or yield. Invalid combinations are counted and excluded without clamping, so statistics are conditional on successful draws. Bounds describe declared scenarios, not source-validated distributions or industrial confidence intervals. JSON exports retain the baseline request, resolved prices, protocol hash, input evidence, seed, bounds and failures.

Saved batch comparisons harmonize purchase, gas and equipment prices only for explicit specification identifiers. These identifiers declare equivalent chemical forms, grades, concentrations and purchasing or cost boundaries; names alone do not establish equivalence. Matching price units and gas reference conditions are required; no unit or density conversion is inferred. The reference estimate supplies the shared price and its input evidence; absent items use the lowest selected estimate ID. Unkeyed items retain their own prices. Common operating assumptions additionally use the reference electricity tariff, labor rate, overheads and margin. Quantities, yields and sequences remain individual. Original saved cases are preserved, and comparison JSON retains recalculated protocols, evidence and price sources.

The frozen May 2026 screening estimates and rankings use the original composition and process assumptions. The preparation audit does not retrospectively validate these assumptions. No industrial utility use, batch yield or manufacturing cost was inferred from a paper's reaction temperature.

## Candidate coverage

Source/formulation discrepancy flagged: 26; source-specific variant linked without that flag: 56; exact preparation unverified with no curated variant: 34. These are mutually exclusive catalog statuses, not reproducibility grades. No candidate has jointly verified formulation, complete preparation and operational cost inputs.

| Reaction family / candidate | Status | Preparation records | Assessment |
|---|---|---|---|
| aem-electrolyzer-oer / NiFe-LDH scalable anode | variant_available | nife-ldh-rt-2025 | Use the NiFe-LDH source for powder manufacture. The separate flow-engineered electrode paper prepares activated Raney Ni, not NiFe-LDH. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| aem-electrolyzer-oer / Seed-assisted NiFe anode | source_mismatch | Not verified / 확인 못 함 | The accessible 2024 electrode Methods describe Raney Ni coating and alkaline leaching, not seed-assisted NiFe preparation. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| aem-electrolyzer-oer / Cr-doped amorphous NiFe route | source_mismatch | cocr-amorphous-2024 | The cited method prepares binary CoCrOx, NiCrOx and FeCrOx, not ternary Cr-doped NiFe. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| aem-electrolyzer-oer / NiCo2O4 spinel anode | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| ammonia-cracking / Ni/gamma-Al2O3 baseline | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| ammonia-cracking / Ni-MgO/CeO2 interface | source_mismatch | ni-cecnt-2025 | The cited 2025 method uses Ni-CeO2-x/CNTs, with no MgO. The catalog composition is not a reported specimen. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| ammonia-cracking / Ru/MgO premium | variant_available | ru-mgo111-2023 | The 3 wt% nominal literature variant is available; Ru3(CO)12/THF chemistry differs from the catalog RuCl3/MgO price proxies. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| ammonia-cracking / Co/MgO-La2O3 mid-cost route | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| ammonia-synthesis / Promoted fused-iron (magnetite/wustite) baseline | variant_available | fused-wustite-w-12-2022, fused-wustite-w-22-2022 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Additional primary preparation records were read on 2026-09-15; these named laboratory specimens do not jointly validate the original catalog formulation, complete preparation and operating costs. |
| ammonia-synthesis / Cs/Ba-promoted Ru on graphitized carbon (KAAP-type) | variant_available | ba-ru-nmc-2019 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Additional primary preparation records were read on 2026-09-15; these named laboratory specimens do not jointly validate the original catalog formulation, complete preparation and operating costs. |
| ammonia-synthesis / Ru/CaFH low-temperature architecture | variant_available | ru-cafh-method2-2020 | The method includes a Ba-containing modifier and a selected synthesis route. The catalog two-component split is simplified. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| ammonia-synthesis / Cs-promoted Co3Mo3N nitride | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| co2-electroreduction / Cu multicarbon CO2RR cathode | variant_available | od-cu500-2015 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| co2-electroreduction / Au CO-selective CO2RR cathode | variant_available | au-inverse-opal-2015 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| co2-electroreduction / Sn formate CO2RR cathode | source_mismatch | sn-graphene-sheets-2016 | The linked primary titles concern Co-porphyrin frameworks, Cu-to-ethylene and molecule/metal ethanol production; a Sn preparation is not established by these links. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| co2-electroreduction / Ag CO-selective MEA cathode | variant_available | ag-hollow-fiber-redox-2022 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Additional primary preparation records were read on 2026-09-15; these named laboratory specimens do not jointly validate the original catalog formulation, complete preparation and operating costs. |
| co2-methanation / Ni/Al2O3 baseline | source_mismatch | ni-y2o3-2019 | The cited 2019 method prepares 3.9 wt% Ni/Y2O3. It does not establish 20 wt% Ni/Al2O3. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| co2-methanation / Ru/MnOx photothermal route | source_mismatch | ru-mnox-2024 | The default reviewed sample contains 7.3 wt% Ru, not the catalog 5 wt%. Its photodeposition route is not generic oxide calcination. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| co2-methanation / Ru/layered titanate route | source_mismatch | ru-titanate-powder-2025 | Ion exchange produces RuxTiyOz/RuO2; 5 wt% Ru on unchanged Na2Ti3O7 is not established. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| co2-methanation / Ni/CeO2 low-temperature route | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| co2-methanol / Cu/ZnO/Al2O3 baseline | source_mismatch | cza-coprecipitation-2020 | The linked studies use Cu-Zn-Zr, Cu/ZrOx/MgO or ZnO; none establishes the catalog Cu/ZnO/Al2O3 formulation. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| co2-methanol / Cu/ZrOx-MgO interface route | source_mismatch | Not verified / 확인 못 함 | The accessible 2019 method prepares Cu-Zn-Zr oxides, and the 2025 method prepares ZnO nanorods. Neither establishes the catalog Cu/ZrOx-MgO interface specimen. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| co2-methanol / In2O3-ZrO2 low-temperature route | source_mismatch | Not verified / 확인 못 함 | The linked methods involve Ni-promoted indium oxide, Pd-In2O3-ZrO2 or inverse In2O3/Ni, not the unpromoted catalog formulation. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| co2-methanol / Pd/In2O3 promoted oxide | variant_available | pd-in2o3-cp-2019 | The nominal 0.75 wt% Pd variant is supported, but co-precipitation and dry impregnation are distinct preparations. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| co2-to-formate / Ir-pincer (Tanaka / Nozaki anchor) | screening_only | Not verified / 확인 못 함 | The retrieved crystallographic supplement alone does not establish a complete preparative recipe or 30 wt% Ir formulation. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| co2-to-formate / Ru-pincer (Sanford / Beller-style) | screening_only | Not verified / 확인 못 함 | The public supplement refers catalyst 3 synthesis to an earlier paper; the catalytic 120 °C/4 h experiment is not its synthesis. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| co2-to-formate / PdAg / N-doped carbon | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| co2-to-formate / Single-atom Ru on Mg-Al LDH | variant_available | ru-ldh-2017 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| co-prox / Fe-promoted Pt/Al2O3 (fuel-processor standard) | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| co-prox / Au/TiO2 nanogold (low-temperature) | variant_available | au-t100-2020 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Second-pass primary preparation review on 2026-09-15 adds named source specimens; their linkage does not validate exact screening composition or complete manufacturing cost. |
| co-prox / CuO-CeO2 (base-metal option) | variant_available | cu-ceria-nc-2026 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Additional primary preparation records were read on 2026-09-15; these named laboratory specimens do not jointly validate the original catalog formulation, complete preparation and operating costs. |
| dry-reforming / Ni/CeO2 single-site route | source_mismatch | ni-ceria-r-2022, ni-ceria-c-2022, ni-ceria-s-2022 | The cited 2019 preparation uses Ce-substituted hydroxyapatite. Ce-containing HAP is not a CeO2 support. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Additional primary preparation records were read on 2026-09-15; these named laboratory specimens do not jointly validate the original catalog formulation, complete preparation and operating costs. |
| dry-reforming / Ni-zeolite stabilized route | variant_available | ni6-dbeta-d-2024 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| dry-reforming / Ir@CeO2-x premium | variant_available | ir-ceria-2024 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| dry-reforming / Ni-Co/Al-Mg-O bimetallic | variant_available | niht-co-2025 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Second-pass primary preparation review on 2026-09-15 adds named source specimens; their linkage does not validate exact screening composition or complete manufacturing cost. |
| ethylene-epoxidation / Ag / alpha-Al2O3 baseline | variant_available | ag15-alumina-2023 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| ethylene-epoxidation / Ag-Cs / Al2O3 (industrial standard) | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| ethylene-epoxidation / Ag-Cs-Re / Al2O3 (modern HSE) | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| ethylene-epoxidation / Cu-Ag/alpha-Al2O3 (DFT-designed alloy) | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| fischer-tropsch-synthesis / Co / Al2O3 FT (commercial baseline) | variant_available | co6-alumina-2018 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| fischer-tropsch-synthesis / Fe / SiO2 lower-olefin FT | variant_available | fe5c2-silica-l-2022 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Second-pass primary preparation review on 2026-09-15 adds named source specimens; their linkage does not validate exact screening composition or complete manufacturing cost. |
| fischer-tropsch-synthesis / Co / CNT structured FT | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| fischer-tropsch-synthesis / Precipitated Fe-Cu-K (Sasol-class) | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| formic-acid-dehydrogenation / Pd/C baseline | variant_available | pd-carbon-2024 | A nominal 5 wt% Pd/C method is available. Actual batch output and equipment consumption remain user inputs. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| formic-acid-dehydrogenation / Co-SAs/NPs@NC route | variant_available | co-nc950-2024 | The reviewed 950 °C specimen contains 2.69 wt% Co; the catalog rounds this to 3 wt%. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| formic-acid-dehydrogenation / Pt-Mo ensemble route | source_mismatch | ptmo-nc-2023 | The method specifies nominal 0.5 wt% Pt and 5 wt% Mo; the catalog uses 3 wt% Pt and 2 wt% Mo. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| formic-acid-dehydrogenation / Au-Pd in amine-grafted MIL-101 | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| fuel-cell-orr / Pt/C baseline cathode | source_mismatch | pt20-kb-200-2025 | The linked 2025 paper 66813 prepares Pt3Co/carbon, not Pt/C. A separate verified 20 wt% Pt/C method is provided as a named powder variant. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| fuel-cell-orr / Pt-Co intermetallic cathode | source_mismatch | pt20-kb-200-2025 | Some linked preparations are different compositions: the 2025 paper 65122 prepares Pt/C, and 58116 prepares Pt3Fe. They do not verify PtCo manufacture. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| fuel-cell-orr / Fe-N-C PGM-free cathode | variant_available | fe-nc-cvm-2024, fe-nc-brcl-2024 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| fuel-cell-orr / PtNi octahedra (mass-activity ceiling) | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| glycerol-electrooxidation / Pt / C glycerol anode | variant_available | pt-carbon-polyol-2023, ptfe-carbon-polyol-2023 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Additional primary preparation records were read on 2026-09-15; these named laboratory specimens do not jointly validate the original catalog formulation, complete preparation and operating costs. |
| glycerol-electrooxidation / Au / C glycerol anode (selectivity) | variant_available | auin-ni-foam-2025 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Second-pass primary preparation review on 2026-09-15 adds named source specimens; their linkage does not validate exact screening composition or complete manufacturing cost. |
| glycerol-electrooxidation / NiOOH non-noble glycerol anode | variant_available | nioh2-film-2022 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| glycerol-electrooxidation / Pt-Bi DHA-selective anode | variant_available | ptbi-carbon-gas-aggregation-2021 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Second-pass primary preparation review on 2026-09-15 adds named source specimens; their linkage does not validate exact screening composition or complete manufacturing cost. |
| hydrodeoxygenation / Pt / SiO2 HDO | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| hydrodeoxygenation / CoMoS / Al2O3 sulfide HDO | source_mismatch | Not verified / 확인 못 함 | The accessible supplement describes Co-doped MoS2 nanosulfides; it does not establish the catalog 84 wt% alumina-supported preparation. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| hydrodeoxygenation / NiMo / carbon (acid-free) | variant_available | nimos2-2-unsupported-2023, nimos2-2-alumina-2023, nimos2-3-unsupported-2023, nimos2-3-alumina-2023 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Second-pass primary preparation review on 2026-09-15 adds named source specimens; their linkage does not validate exact screening composition or complete manufacturing cost. |
| hydrodeoxygenation / Ru/C noble-metal route | variant_available | ru-nc-melamine-2023 | Commercial Ru/C performance is not disclosure of the supplier manufacturing recipe. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Additional primary preparation records were read on 2026-09-15; these named laboratory specimens do not jointly validate the original catalog formulation, complete preparation and operating costs. |
| hydrogen-evolution-reaction / Pt/C HER cathode (PEM) | variant_available | pt20-kb-200-2025 | The exchange-current trend source is a performance/theory reference, not an exact 20 wt% Pt/C synthesis. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| hydrogen-evolution-reaction / NiMo alkaline HER cathode | variant_available | nimo-powder-2013 | The public method reports precursor Ni:Mo ratio 6:4 molar and composition changes on reduction; catalog 70/30 mass fractions are not interchangeable. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| hydrogen-evolution-reaction / MoS2 acidic HER cathode | variant_available | mos2-m-2016, mos2-s-2016 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Additional primary preparation records were read on 2026-09-15; these named laboratory specimens do not jointly validate the original catalog formulation, complete preparation and operating costs. |
| hydrogen-evolution-reaction / Ru@C2N pH-universal cathode | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| methane-pyrolysis / High-loading Ni/SiO2 | variant_available | nicu-ms-500-2022, nicu-ms-600-2022, nicu-ms-700-2022, nicu-ms-800-2022 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Additional primary preparation records were read on 2026-09-15; these named laboratory specimens do not jointly validate the original catalog formulation, complete preparation and operating costs. |
| methane-pyrolysis / Fe/Al2O3 higher-temperature route | variant_available | fe20-alumina-500-2024 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| methane-pyrolysis / Activated-carbon consumable catalyst | variant_available | coal-ac-1023-2020 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Additional primary preparation records were read on 2026-09-15; these named laboratory specimens do not jointly validate the original catalog formulation, complete preparation and operating costs. |
| methane-pyrolysis / Molten Ni-Bi alloy media | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| methanol-to-olefins / SAPO-34 chabazite (DMTO baseline) | variant_available | sapo34-sp-2025 | The additional 2021 primary study purchased SAPO-34; its 393 K degassing is characterization, not a disclosed catalyst manufacturing recipe. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Additional primary preparation records were read on 2026-09-15; these named laboratory specimens do not jointly validate the original catalog formulation, complete preparation and operating costs. |
| methanol-to-olefins / H-ZSM-5 (MTH baseline) | variant_available | bmp-30-zsm5-2017, tpa-30-zsm5-2017 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Second-pass primary preparation review on 2026-09-15 adds named source specimens; their linkage does not validate exact screening composition or complete manufacturing cost. |
| methanol-to-olefins / Zn / ZSM-5 (aromatics-leaning) | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| methanol-to-olefins / Nanosized SAPO-34 (lifetime play) | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| nh3-scr / V2O5-WO3/TiO2 monolith (stationary standard) | variant_available | v-wti-powder-2021 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| nh3-scr / Cu-SSZ-13 (diesel aftertreatment standard) | variant_available | cu-ssz13-exchange-2021 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| nh3-scr / Fe-ZSM-5 high-temperature variant | variant_available | fezsm5-dr-minerals-2015 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Additional primary preparation records were read on 2026-09-15; these named laboratory specimens do not jointly validate the original catalog formulation, complete preparation and operating costs. |
| nitrogen-reduction-reaction / Lithium-mediated NRR cathode | variant_available | porous-cu-nrr-2022 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| nitrogen-reduction-reaction / Plasma-NRR ammonia route | variant_available | wo3-h2n2-1h-electrode-2025, wo3-h2n2-2h-electrode-2025 | A plasma nitrogen-fixation process is not a conventional catalyst-powder synthesis; the hardware boundary requires separate treatment. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Second-pass primary preparation review on 2026-09-15 adds named source specimens; their linkage does not validate exact screening composition or complete manufacturing cost. |
| nitrogen-reduction-reaction / Aqueous NRR research anchor (Cu) | variant_available | cu-pi300-powder-2019 | Rigorous analytical controls and false-positive studies do not establish a verified productive Cu catalyst or manufacturing recipe. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Second-pass primary preparation review on 2026-09-15 adds named source specimens; their linkage does not validate exact screening composition or complete manufacturing cost. |
| nitrogen-reduction-reaction / Li-mediated flow cell with proton shuttle | variant_available | porous-cu-nrr-2022 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| olefin-metathesis / Re2O7 / Al2O3 mild-condition | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| olefin-metathesis / WO3 / SiO2 (Lummus OCT) | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| olefin-metathesis / MoO3 / SiO2-Al2O3 emerging | variant_available | mo6-silica-2022 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Second-pass primary preparation review on 2026-09-15 adds named source specimens; their linkage does not validate exact screening composition or complete manufacturing cost. |
| olefin-metathesis / W-H/Al2O3 single-site hydride | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| pem-electrolyzer-oer / IrO2 PEM anode baseline | variant_available | iro2-adams-2023 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| pem-electrolyzer-oer / Low-Ir interface-engineered PEM route | variant_available | iro2-adams-2023, ir-mnox-carbon-300-2024 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| pem-electrolyzer-oer / Ru-rich acidic OER route | variant_available | ba-w-ru-sulfate-2023 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| pem-electrolyzer-oer / IrO2/TiO2 supported anode | variant_available | iro2-white-p25-photo-2024 | The retrieved supplement contains characterization and XAS electrode methods; these do not verify bulk catalyst manufacture. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Additional primary preparation records were read on 2026-09-15; these named laboratory specimens do not jointly validate the original catalog formulation, complete preparation and operating costs. |
| photocatalytic-co2-reduction / TiO2 photocatalyst (UV anchor) | variant_available | pt2-p25-2018 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| photocatalytic-co2-reduction / g-C3N4 / SnS2 Z-scheme | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| photocatalytic-co2-reduction / Cu2O / MOF heterojunction | source_mismatch | Not verified / 확인 못 함 | The linked primary title concerns nitrogen-doped In2O3; it does not establish a Cu2O/MOF preparation. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| photocatalytic-co2-reduction / Monoclinic BiVO4 (visible-light oxide) | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| photocatalytic-water-splitting / TiO2 (anatase) baseline | variant_available | meso-tio2-25-2019 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Second-pass primary preparation review on 2026-09-15 adds named source specimens; their linkage does not validate exact screening composition or complete manufacturing cost. |
| photocatalytic-water-splitting / g-C3N4 metal-free photocatalyst | variant_available | gcn-urea-550-2016 | A urea-derived powder method is available. The source water-splitting experiments add cocatalysts, so preparation coverage does not establish activity of metal-free powder. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| photocatalytic-water-splitting / Pt / TiO2 cocatalyst | variant_available | pt2-p25-2018 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| photocatalytic-water-splitting / SrTiO3:Al with Rh/Cr2O3 + CoOOH | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| propane-dehydrogenation / Pt-Sn / Al2O3 (Oleflex-style) | source_mismatch | ptsn-alumina-base-2024, ptsn-alumina-04ca-2024, ptsn-alumina-08ca-2024, ptsn-alumina-12ca-2024 | The linked PtSn preparations include SBA-15 and silica; the catalog alumina/Oleflex-style formulation is not an exact reproduction. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Additional primary preparation records were read on 2026-09-15; these named laboratory specimens do not jointly validate the original catalog formulation, complete preparation and operating costs. |
| propane-dehydrogenation / PtZn intermetallic / zeolite | screening_only | Not verified / 확인 못 함 | The accessible supplement labels 1Pt1Zn and 4Pt4Zn samples; it does not provide the full preparation for catalog 0.5 Pt/1.0 Zn wt%. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| propane-dehydrogenation / h-BN ODHP route | variant_available | fe-bn-milled-2024, fe-bn-iwi-2024 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Second-pass primary preparation review on 2026-09-15 adds named source specimens; their linkage does not validate exact screening composition or complete manufacturing cost. |
| propane-dehydrogenation / CrOx/Al2O3 (Catofin-type) | source_mismatch | cr20-alumina-commercialsupport-2017 | The reviewed primary comparator is 20 wt% Cr2O3 without the catalog K2O promoter; it is not an exact Catofin formulation. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| rwgs / Cu/CeO2 baseline | source_mismatch | cu-ceria-dp-2022 | The source 15CuCe label is Cu/CeO2 mass ratio 0.15, not 15 wt% Cu in the total catalyst. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| rwgs / Pt/TiO2 premium | source_mismatch | Not verified / 확인 못 함 | The 2022 source prepares Pt–MoO3/Mo2N, while the 2023 source studies multicomponent-promoted Pt/TiO2. These do not jointly establish the exact unpromoted catalog specimen. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| rwgs / Mo2N high-temperature route | source_mismatch | beta-mo2n-2024 | The reviewed 2024 preparation is unsupported Mo2N, not the catalog Mo/Al2O3 mass formulation. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| rwgs / Cs-Fe-Cu/Al2O3 high-temperature route | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| selective-acetylene-hydrogenation / Pd / Al2O3 baseline | source_mismatch | Not verified / 확인 못 함 | The first primary citation uses K-beta zeolite; its method cannot be transferred to alumina without a separate source. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| selective-acetylene-hydrogenation / Pd-Ag bimetallic (front-end style) | source_mismatch | Not verified / 확인 못 함 | The PdAg primary citation uses K-beta zeolite. The catalog alumina-supported composition is a screening assumption. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| selective-acetylene-hydrogenation / Pd-Cu single-atom alloy | source_mismatch | pdcu-silicalite-2022 | The cited 2015 primary Methods synthesize Pt/Cu, not Pd/Cu. The added PdCu@S-1 method is a separate zeolite-encapsulated specimen, not validation of the catalog alloy. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| selective-acetylene-hydrogenation / NiZn intermetallic (non-Pd) | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| steam-methane-reforming / Ni on calcium aluminate (industrial baseline) | screening_only | Not verified / 확인 못 함 | Commercial catalyst use and operating conditions do not disclose a complete factory manufacturing recipe. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| steam-methane-reforming / Rh/Al2O3 compact-reformer route | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| steam-methane-reforming / Sn/Ni surface alloy (coking-resistant) | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| syngas-methanol / Cu/ZnO/Al2O3 (industrial workhorse) | variant_available | cza-coprecipitation-2020 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| syngas-methanol / Pd/ZnO intermetallic alternative | variant_available | pd-zno-i-2021 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Second-pass primary preparation review on 2026-09-15 adds named source specimens; their linkage does not validate exact screening composition or complete manufacturing cost. |
| syngas-methanol / Ga-promoted Cu/ZnO (Zn-coverage engineering) | screening_only | Not verified / 확인 못 함 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| water-gas-shift / Cu/ZnO/Al2O3 baseline | variant_available | cza-coprecipitation-2020 | The primary study purchased its commercial Cu/ZnO/Al2O3 comparator; its Cu-nanocrystal synthesis is a different product. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| water-gas-shift / Co-CeO2 interface route | source_mismatch | ceco-spray-2023 | The reviewed source uses Ce:Co molar ratios 1:9 or 9:1; neither establishes the catalog 18 wt% Co formulation. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| water-gas-shift / Pt/CeO2 premium | source_mismatch | pt-ceria-2021 | The reviewed 2021 specimen is measured 1.85 wt% Pt/CeO2; another linked work uses Pt/MoC. Neither verifies the catalog 2.5 wt% formulation. Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. |
| water-gas-shift / Fe2O3-Cr2O3(-CuO) high-temperature shift | variant_available | cr-hm-wgs-2022 | Exact formulation, complete preparation and operational cost inputs are not jointly verified. Generic route steps and reaction-temperature windows must not be used as synthesis conditions. Additional primary preparation records were read on 2026-09-15; these named laboratory specimens do not jointly validate the original catalog formulation, complete preparation and operating costs. |

## Additional primary-source assessment

These targeted Europe PMC searches prioritize public full text and are not an exhaustive systematic review. Zero indexed hits are not evidence that no recipe exists. Selection decisions and unverified access are retained; the remaining candidates require further primary-source review.

| Selected DOI | Preparation records | Assessment |
|---|---|---|
| [10.1021/acsami.2c05221](https://pmc.ncbi.nlm.nih.gov/articles/PMC9305712/) | ni-ceria-r-2022, ni-ceria-c-2022, ni-ceria-s-2022 | Named preparation variants were transcribed. This does not validate the original screening formulation or provide complete operating costs. |
| [10.1021/acscatal.2c03871](https://pmc.ncbi.nlm.nih.gov/articles/PMC9679995/) | cr-hm-wgs-2022 | Named preparation variants were transcribed. This does not validate the original screening formulation or provide complete operating costs. |
| [10.1021/acscatal.5c06552](https://pmc.ncbi.nlm.nih.gov/articles/PMC12724332/) | cu-ceria-nc-2026 | Named preparation variants were transcribed. This does not validate the original screening formulation or provide complete operating costs. |
| [10.1021/acsomega.2c01016](https://pmc.ncbi.nlm.nih.gov/articles/PMC9089693/) | nicu-ms-500-2022, nicu-ms-600-2022, nicu-ms-700-2022, nicu-ms-800-2022 | Named preparation variants were transcribed. This does not validate the original screening formulation or provide complete operating costs. |
| [10.1021/acsomega.9b04044](https://pmc.ncbi.nlm.nih.gov/articles/PMC7017400/) | coal-ac-1023-2020 | Named preparation variants were transcribed. This does not validate the original screening formulation or provide complete operating costs. |
| [10.1038/ncomms10672](https://pmc.ncbi.nlm.nih.gov/articles/PMC4749985/) | mos2-m-2016, mos2-s-2016 | Named preparation variants were transcribed. This does not validate the original screening formulation or provide complete operating costs. |
| [10.1038/ncomms8261](https://pmc.ncbi.nlm.nih.gov/articles/PMC4557299/) | Not curated | Not curated for this candidate: Ni-Fe oxide/carbon and Co oxide specimens differ from the catalog NiCo2O4 spinel. A title or related element does not establish formulation identity. |
| [10.1038/s41467-022-30733-6](https://pmc.ncbi.nlm.nih.gov/articles/PMC9163090/) | ag-hollow-fiber-redox-2022 | Named preparation variants were transcribed. This does not validate the original screening formulation or provide complete operating costs. |
| [10.1038/s41467-024-52518-9](https://pmc.ncbi.nlm.nih.gov/articles/PMC11408692/) | Not curated | Not curated: the main text was read, but gas-migration setup details require the supplement. The public supplement could not be retrieved (Europe PMC response HTTP 503); its contents are not verified. |
| [10.1038/s41467-025-63061-6](https://pmc.ncbi.nlm.nih.gov/articles/PMC12370944/) | Not curated | Not curated: the available Methods describe reduction of analytical specimens and refer to earlier industrial fusion preparation. These conditions do not establish a complete catalyst manufacturing recipe. |
| [10.1038/s41598-025-14220-8](https://pmc.ncbi.nlm.nih.gov/articles/PMC12343829/) | sapo34-sp-2025 | Named preparation variants were transcribed. This does not validate the original screening formulation or provide complete operating costs. |
| [10.1038/srep09270](https://pmc.ncbi.nlm.nih.gov/articles/PMC4366855/) | fezsm5-dr-minerals-2015 | Named preparation variants were transcribed. This does not validate the original screening formulation or provide complete operating costs. |
| [10.1039/c9ra03097b](https://pmc.ncbi.nlm.nih.gov/articles/PMC9066922/) | ba-ru-nmc-2019 | Named preparation variants were transcribed. This does not validate the original screening formulation or provide complete operating costs. |
| [10.1039/d3ra01866k](https://pmc.ncbi.nlm.nih.gov/articles/PMC10336651/) | ru-nc-melamine-2023 | Named preparation variants were transcribed. This does not validate the original screening formulation or provide complete operating costs. |
| [10.3390/ma15238309](https://pmc.ncbi.nlm.nih.gov/articles/PMC9739429/) | fused-wustite-w-12-2022, fused-wustite-w-22-2022 | Named preparation variants were transcribed. This does not validate the original screening formulation or provide complete operating costs. |
| [10.3390/molecules29102392](https://pmc.ncbi.nlm.nih.gov/articles/PMC11124129/) | iro2-white-p25-photo-2024 | Named preparation variants were transcribed. This does not validate the original screening formulation or provide complete operating costs. |
| [10.3390/molecules29132959](https://pmc.ncbi.nlm.nih.gov/articles/PMC11243666/) | ptsn-alumina-base-2024, ptsn-alumina-04ca-2024, ptsn-alumina-08ca-2024, ptsn-alumina-12ca-2024 | Named preparation variants were transcribed. This does not validate the original screening formulation or provide complete operating costs. |
| [10.3390/nano13071173](https://pmc.ncbi.nlm.nih.gov/articles/PMC10096876/) | pt-carbon-polyol-2023, ptfe-carbon-polyol-2023 | Named preparation variants were transcribed. This does not validate the original screening formulation or provide complete operating costs. |
| [10.1002/anie.202103087](https://pmc.ncbi.nlm.nih.gov/articles/PMC8361960/) | pd-zno-i-2021 | Primary preparation section read; explicit quantities and source-specific boundaries transcribed. Missing yields, operation inputs and prices remain unverified. |
| [10.1002/cssc.202402378](https://pmc.ncbi.nlm.nih.gov/articles/PMC12175034/) | auin-ni-foam-2025 | Primary preparation section read; explicit quantities and source-specific boundaries transcribed. Missing yields, operation inputs and prices remain unverified. |
| [10.1021/acsami.0c08258](https://pmc.ncbi.nlm.nih.gov/articles/PMC7458359/) | au-t100-2020 | Primary preparation section read; explicit quantities and source-specific boundaries transcribed. Missing yields, operation inputs and prices remain unverified. |
| [10.1021/acsenergylett.5c01034](https://pmc.ncbi.nlm.nih.gov/articles/PMC12333582/) | wo3-h2n2-1h-electrode-2025, wo3-h2n2-2h-electrode-2025 | Primary preparation section read; explicit quantities and source-specific boundaries transcribed. Missing yields, operation inputs and prices remain unverified. |
| [10.1021/acsomega.3c06188](https://pmc.ncbi.nlm.nih.gov/articles/PMC10620879/) | nimos2-2-unsupported-2023, nimos2-2-alumina-2023, nimos2-3-unsupported-2023, nimos2-3-alumina-2023 | Primary preparation section read; explicit quantities and source-specific boundaries transcribed. Missing yields, operation inputs and prices remain unverified. |
| [10.1021/acsomega.5c08293](https://pmc.ncbi.nlm.nih.gov/articles/PMC12547782/) | niht-co-2025 | Primary preparation section read; explicit quantities and source-specific boundaries transcribed. Missing yields, operation inputs and prices remain unverified. |
| [10.1038/s41467-019-12312-4](https://pmc.ncbi.nlm.nih.gov/articles/PMC6763479/) | cu-pi300-powder-2019 | Primary preparation section read; explicit quantities and source-specific boundaries transcribed. Missing yields, operation inputs and prices remain unverified. |
| [10.1039/c7sc02858j](https://pmc.ncbi.nlm.nih.gov/articles/PMC5855293/) | bmp-30-zsm5-2017, tpa-30-zsm5-2017 | Primary preparation section read; explicit quantities and source-specific boundaries transcribed. Missing yields, operation inputs and prices remain unverified. |
| [10.1039/c8sc04155e](https://pmc.ncbi.nlm.nih.gov/articles/PMC6368211/) | meso-tio2-25-2019 | Primary preparation section read; explicit quantities and source-specific boundaries transcribed. Missing yields, operation inputs and prices remain unverified. |
| [10.1039/c9ra08967e](https://pmc.ncbi.nlm.nih.gov/articles/PMC9048714/) | Not curated | Not curated: the preparation paragraph reports a Ni(NO3)3 hydrate and mutually inconsistent nitrate masses/moles; it also changes CeO2 to ZrO2 in sample naming. These inconsistencies were not silently corrected or used to establish an exact Ni/CeO2 recipe. |
| [10.1039/d0na01009j](https://pmc.ncbi.nlm.nih.gov/articles/PMC9418899/) | ptbi-carbon-gas-aggregation-2021 | Primary preparation section read; explicit quantities and source-specific boundaries transcribed. Missing yields, operation inputs and prices remain unverified. |
| [10.1039/d2sc03321f](https://pmc.ncbi.nlm.nih.gov/articles/PMC9337747/) | mo6-silica-2022 | Primary preparation section read; explicit quantities and source-specific boundaries transcribed. Missing yields, operation inputs and prices remain unverified. |
| [10.1039/d4ey00123k](https://pmc.ncbi.nlm.nih.gov/articles/PMC11320177/) | fe-bn-milled-2024, fe-bn-iwi-2024 | Primary preparation section read; explicit quantities and source-specific boundaries transcribed. Missing yields, operation inputs and prices remain unverified. |
| [10.3390/nano12203704](https://pmc.ncbi.nlm.nih.gov/articles/PMC9610965/) | fe5c2-silica-l-2022 | Primary preparation section read; explicit quantities and source-specific boundaries transcribed. Missing yields, operation inputs and prices remain unverified. |

The accompanying JSON retains each targeted query, database endpoint, search date and hit count. Search retrieval and the existence of a preparation record are separate outcomes.


## Source-specific preparations

### S1. Ru/MgO(111), nominal 3 wt% Ru

Record: `ru-mgo111-2023`. Boundary: catalyst_powder.

Source: [Dispersed surface Ru ensembles on MgO(111) for catalytic ammonia decomposition](https://pmc.ncbi.nlm.nih.gov/articles/PMC9902439/). [DOI 10.1038/s41467-023-36339-w](https://doi.org/10.1038/s41467-023-36339-w). Locator: Methods: Preparation of different MgO supports; Preparation of supported Ru catalysts; Catalytic evaluation. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Support precipitation | Not quantified | 2.0 g MgCl2, 0.12 g benzoic acid, 60 mL water; sonicate, stir 10 min, add 20 mL 2 M NaOH dropwise. |
| Hydrothermal treatment | 180 °C; hold 24 h; ramp unreported °C/min |  |
| Wash and vacuum dry | 80 °C; hold unreported h; ramp unreported °C/min; vacuum | Water wash/filter; overnight duration not quantified. |
| Support calcination | 500 °C; hold 6 h; ramp unreported °C/min; compressed air |  |
| Ru impregnation | 2 h | Ru3(CO)12 in THF; room temperature. |
| Solvent removal and vacuum drying | 90 °C; hold unreported h; ramp unreported °C/min; vacuum | Overnight duration not quantified. |
| Precursor decomposition | 300 °C; hold 3 h; ramp 2 °C/min; Ar |  |
| Pre-reaction activation | 350 °C; hold 4 h; ramp unreported °C/min; 5% H2/He | Separate activation boundary; include only if delivered product is activated. |

Measured representative Ru loading is 3.1 wt%. The catalog RuCl3 price proxy is not the Ru3(CO)12 precursor used here.

### S2. Ni-CeO2-x/CNTs; CeO2:CNT support ratio 0.5

Record: `ni-cecnt-2025`. Boundary: catalyst_powder.

Source: [Breakthrough photothermal ammonia decomposition via low-barrier Ni-CeO2-x interfaces on carbon nanotubes](https://pmc.ncbi.nlm.nih.gov/articles/PMC12749141/). [DOI 10.1038/s41467-025-66325-3](https://doi.org/10.1038/s41467-025-66325-3). Locator: Methods: Preparation of CeO2-x/CNTs support; Preparation of Ni-supported catalysts. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Support mixing | 12 h | 190 mg Ce nitrate hexahydrate, 150 mg CNTs in 100 mL water. |
| Precipitation | 0.5 h | Ammonia solution to pH 9. |
| Wash and dry | vacuum | Water and ethanol, each three washes; room-temperature vacuum drying overnight. |
| Support calcination | 599.85 °C; hold 2 h; ramp 5 °C/min; N2 | Reported 873 K; N2 60 mL/min; flow reference conditions unspecified. |
| Ni impregnation | Not quantified | 100 mg support, 50 mg Ni nitrate hexahydrate in 100 mL water; stir overnight in darkness. |
| Chemical reduction | 0.5 h | Add 50 mg NaBH4; vigorous stirring. |
| Wash and vacuum dry | vacuum | Water and ethanol, each three washes; room-temperature drying duration unreported. |

This source contains no MgO. It cannot verify the catalog Ni-MgO/CeO2 formulation. Final Ni loading and dry output are not inferred from precursor masses.

### S3. NiFe-LDH, room-temperature epoxide route, Ni:Fe = 2:1 molar

Record: `nife-ldh-rt-2025`. Boundary: catalyst_powder.

Source: [Scalable synthesis of NiFe-layered double hydroxide for efficient anion exchange membrane electrolysis](https://pmc.ncbi.nlm.nih.gov/articles/PMC12229561/). [DOI 10.1038/s41467-025-61356-2](https://doi.org/10.1038/s41467-025-61356-2). Locator: Methods: Synthesis. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare precursor solution | Not quantified | Ni:Fe 2:1 molar; pH approximately 2 with HCl. Cations 15–750 mM; chloride and glycidol each 40–2000 mM are experimental ranges, not fixed defaults. |
| Epoxide-driven precipitation and aging | Not quantified | Continuous magnetic stirring at room temperature for 24–72 h; select the reported variant before entering a numeric duration. |
| Recover and wash | Not quantified | Filter or centrifuge; three water washes, each half the original volume; ethanol wash. |
| Dry and store | Not quantified | Dry at room temperature, store in desiccator; duration not reported. |

Powder preparation only. The paper separately fabricates electrodes; neither its ink nor an industrial batch yield is implied here.

### S4. CoCrOx, approximately 1:1 metal:Cr

Record: `cocr-amorphous-2024`. Boundary: catalyst_powder.

Source: [Highly efficient anion exchange membrane water electrolyzers via chromium-doped amorphous electrocatalysts](https://pmc.ncbi.nlm.nih.gov/articles/PMC11035637/). [DOI 10.1038/s41467-024-47736-0](https://doi.org/10.1038/s41467-024-47736-0). Locator: Methods: Synthesis of catalysts. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Mix metal salts | Not quantified | 2 mL each of 2 M CoCl2 and CrCl3 solutions; hydrate forms in original Methods. |
| Borohydride reduction | 0.25 h | Fresh 3 g NaBH4 in 20 mL water added dropwise; mechanical stirring. |
| Age and freeze-dry | Not quantified | Cool, leave overnight, then freeze-dry; exact durations not reported. |
| Wash and vacuum dry | Not quantified | Water/ethanol wash after freeze-drying; vacuum drying temperature and duration not reported. |

Source also prepares binary NiCrOx and FeCrOx. It does not establish the catalog ternary Cr-doped NiFe formulation.

### S5. 12 wt% Ru/CaFH, Method 2, Ba-modified support

Record: `ru-cafh-method2-2020`. Boundary: catalyst_powder.

Source: [Solid solution for catalytic ammonia synthesis from nitrogen and hydrogen gases at 50 °C](https://pmc.ncbi.nlm.nih.gov/articles/PMC7181780/). [DOI 10.1038/s41467-020-15868-8](https://doi.org/10.1038/s41467-020-15868-8). Locator: Methods: Preparation of CaH2-BaF2 mixture and Ru/CaFH. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare Ba modifier | 400 °C; hold 10 h; ramp unreported °C/min; Ar | 87 mol% BaF2 / 13 mol% BaH2; Ar 15 mL/min. |
| Mix support and Ru precursor | Not quantified | 98 mol% CaH2 + 2 mol% modified BaF2; Ru(acac)3 for nominal 12 wt% Ru. |
| Heat under hydrogen | 260 °C; hold 2 h; ramp unreported °C/min; H2 | H2 2.5 mL/min; first hold. |
| Second hydrogen hold | 340 °C; hold 10 h; ramp unreported °C/min; H2 |  |

Ramps not reported. Method 1 is a separate synthesis; its additional support treatment is not added to Method 2. Catalog support proxy omits the Ba modifier.

### S6. Single-atom Ni/Y2O3, measured 3.9 wt% Ni

Record: `ni-y2o3-2019`. Boundary: catalyst_powder.

Source: [Selective light absorber-assisted single nickel atom catalysts for ambient sunlight-driven CO2 methanation](https://pmc.ncbi.nlm.nih.gov/articles/PMC6541650/). [DOI 10.1038/s41467-019-10304-y](https://doi.org/10.1038/s41467-019-10304-y). Locator: Methods: Synthesis of SA Ni/Y2O3. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Mix with graphene oxide | Not quantified | 0.8 g Ni nitrate, 3 g Y nitrate in 100 mL water plus 100 mL GO (2 mg/mL). |
| Recover, redisperse and freeze | Not quantified | Centrifuge/wash; sonicate in water; freeze with liquid nitrogen. |
| Freeze-dry | 72 h | Reported three days. |
| Remove GO template | 400 °C; hold 24 h; ramp unreported °C/min; air |  |
| Reduction | 400 °C; hold 2.5 h; ramp unreported °C/min; 10% H2/Ar |  |

This is not a 20 wt% Ni/Al2O3 recipe. The study distinguishes Ni nanoparticles from single-atom samples.

### S7. Ru/MnOx, default photodeposition sample, measured 7.3 wt% Ru

Record: `ru-mnox-2024`. Boundary: catalyst_powder.

Source: [Photo-thermal coupling to enhance CO2 hydrogenation toward CH4 over Ru/MnO/Mn3O4](https://pmc.ncbi.nlm.nih.gov/articles/PMC10847166/). [DOI 10.1038/s41467-024-45389-7](https://doi.org/10.1038/s41467-024-45389-7). Locator: Methods: Materials synthesis. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Mn precursor mixing | 0.5 h | 1 mmol MnSO4 hydrate and 120 mmol NaOH in 30 mL water. |
| Hydrothermal treatment | 119.85 °C; hold 12 h; ramp unreported °C/min | Reported 393 K. |
| Wash and vacuum dry | 59.85 °C; hold unreported h; ramp unreported °C/min; vacuum | Wash to pH 7; dry at 333 K overnight (unquantified). |
| Photodeposition | 1 h; Ar | 0.1 g MnOx, 10 mL methanol, 0.1 mmol RuCl3 hydrate in 50 mL water; evacuate then Ar at 1 atm. 300 W UV-Xe lamp, 3 W/cm2 irradiance; neither value is measured wall input. |
| Wash and vacuum dry | 59.85 °C; hold unreported h; ramp unreported °C/min; vacuum | 333 K overnight; duration not quantified. |

The catalog 5 wt% Ru differs from the default 7.3 wt% sample. No generic high-temperature calcination is added.

### S8. RuxTiyOz powder from layered Na2Ti3O7 ion exchange

Record: `ru-titanate-powder-2025`. Boundary: catalyst_powder.

Source: [Layered Na2Ti3O7-supported Ru catalyst for ambient CO2 methanation](https://pmc.ncbi.nlm.nih.gov/articles/PMC11965424/). [DOI 10.1038/s41467-025-57954-9](https://doi.org/10.1038/s41467-025-57954-9). Locator: Methods: Synthesis of RuxTiyOz. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Bicarbonate solution | 0.5 h | 0.10501 g NaHCO3 in 25 mL water; room temperature. |
| Ru and titanate addition | Not quantified | 0.11554 g RuCl3 hydrate; wait until bubbles stop, then add 0.1 g Na2Ti3O7. |
| Hydrothermal ion exchange | 160 °C; hold 24 h; ramp unreported °C/min | Vigorous stirring. |
| Filter and wash | Not quantified | Cool to room temperature; filter and wash. |
| Drying | 100 °C; hold 6 h; ramp unreported °C/min |  |

Final product includes reconstructed RuxTiyOz/RuO2. A 5 wt% Ru/intact titanate formulation is not verified. The structured Ti reactor route is separate.

### S9. 5 wt% Pd/C on Vulcan XC72

Record: `pd-carbon-2024`. Boundary: catalyst_powder.

Source: [Disentangling heterogeneous thermocatalytic formic acid dehydrogenation from an electrochemical perspective](https://pmc.ncbi.nlm.nih.gov/articles/PMC11362458/). [DOI 10.1038/s41467-024-51926-1](https://doi.org/10.1038/s41467-024-51926-1). Locator: Methods: Synthesis of Pd/C catalysts. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Precursor dispersion | Not quantified | 0.1575 mmol H2PdCl4, 370.6 mg sodium citrate dihydrate in 40 mL water; add 318 mg carbon; sonicate 20 min. |
| Stir precursor | 1 h |  |
| Reduce Pd | Not quantified | 10 mL solution containing 60 mg Na2CO3 and 40 mg NaBH4 at 0.5 mL/min; 750 rpm. Addition duration is not entered as a reported measurement. |
| Post-addition stirring | 4 h |  |
| Wash and dry | 69.85 °C; hold unreported h; ramp unreported °C/min; vacuum | Filter, wash five times; vacuum dry at 343 K overnight. |

Electrochemical characterization ink is excluded from this thermal powder recipe.

### S10. Co-SAs/NPs@NC-950, measured 2.69 wt% Co

Record: `co-nc950-2024`. Boundary: catalyst_powder.

Source: [Combination of nanoparticles with single-metal sites synergistically boosts co-catalyzed formic acid dehydrogenation](https://pmc.ncbi.nlm.nih.gov/articles/PMC11410817/). [DOI 10.1038/s41467-024-52517-w](https://doi.org/10.1038/s41467-024-52517-w). Locator: Methods: Preparation of CoZn-ZIF and Co-SAs/NPs@NC. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| ZIF precursor mixing | 24 h | 30 mmol Zn nitrate, 3.5 mmol Co nitrate in 300 mL methanol; 120 mmol 2-methylimidazole in 100 mL methanol; room temperature. |
| Recover and wash | Not quantified | Centrifuge 6429 g for 10 min; three methanol washes. |
| Vacuum drying | 60 °C; hold unreported h; ramp unreported °C/min; vacuum | Overnight duration unquantified. |
| Pyrolysis | 950 °C; hold 1 h; ramp 5 °C/min; 6% H2 / 94% Ar | Cool under synthesis atmosphere; no acid etch reported. |

The 750, 850 and 950 °C samples are distinct. Catalog 3 wt% Co is rounded rather than the measured 2.69 wt%.

### S11. Pt-Mo/NC, nominal 0.5 wt% Pt and 5 wt% Mo

Record: `ptmo-nc-2023`. Boundary: catalyst_powder.

Source: [Defect-driven nanostructuring of low-nuclearity Pt-Mo ensembles for continuous gas-phase formic acid dehydrogenation](https://pmc.ncbi.nlm.nih.gov/articles/PMC10657381/). [DOI 10.1038/s41467-023-42759-5](https://doi.org/10.1038/s41467-023-42759-5). Locator: Methods: Catalyst preparation. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Polyaniline precursor | Not quantified | Chill aniline/HCl and ammonium persulfate solutions at 277 K for 1 h; mix 5 min at room temperature, stand overnight. |
| Wash and dry polymer | 99.85 °C; hold unreported h; ramp unreported °C/min | Wash with 4 L water; 373 K overnight. |
| Carbonize support | 1 h | 1073–1673 K, 5 K/min, 1 h depending on sample; no single target selected. |
| Mo impregnation and drying | 79.85 °C; hold 12 h; ramp unreported °C/min | Ammonium molybdate incipient wetness; 353 K. |
| Mo heat treatment | 499.85 °C; hold 5 h; ramp 10 °C/min; Ar | 773 K. |
| Pt impregnation and drying | 79.85 °C; hold 12 h; ramp unreported °C/min | H2PtCl6 hydrate; 353 K. |
| Pt heat treatment | 499.85 °C; hold 4 h; ramp 5 °C/min; Ar | 773 K. |
| Carburization first hold | 299.85 °C; hold 1 h; ramp 5 °C/min; 20% CH4 / 80% H2 | 573 K. |
| Carburization second hold | 699.85 °C; hold 2 h; ramp 1 °C/min; 20% CH4 / 80% H2 | 973 K. |

Catalog 3 wt% Pt/2 wt% Mo does not match this paper. Support carbonization variant must be resolved before costing.

### S12. Pd/In2O3 co-precipitated, nominal 0.75 wt% Pd

Record: `pd-in2o3-cp-2019`. Boundary: catalyst_powder.

Source: [Atomic-scale engineering of indium oxide promotion by palladium for methanol production via CO2 hydrogenation](https://pmc.ncbi.nlm.nih.gov/articles/PMC6662860/). [DOI 10.1038/s41467-019-11349-9](https://doi.org/10.1038/s41467-019-11349-9). Locator: Methods: Catalyst preparation. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Co-precipitation | Not quantified | In and Pd nitrate hydrates in 50 mL water; add Na2CO3 at 3 mL/min to pH 9.2; room temperature. |
| Aging | 1 h |  |
| Recover and wash | Not quantified | Add 50 mL water; pressure filtration; three 500 mL water washes. |
| Vacuum drying | 49.85 °C; hold 1.5 h; ramp unreported °C/min; vacuum | 323 K at 1.5 kPa. |
| Calcination | 299.85 °C; hold 3 h; ramp 2 °C/min; static air | 573 K. |

Precursor quantities must correspond to the selected Pd loading; the paper reports a loading series. Dry impregnation is a separate route.

### S13. Ir/CeO2-x nanorods, loading series

Record: `ir-ceria-2024`. Boundary: catalyst_powder.

Source: [Facilitating the dry reforming of methane with interfacial synergistic catalysis in an Ir@CeO2−x catalyst](https://pmc.ncbi.nlm.nih.gov/articles/PMC11069590/). [DOI 10.1038/s41467-024-48122-6](https://doi.org/10.1038/s41467-024-48122-6). Locator: Methods: Preparation of catalysts. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Support precipitation | 0.5 h | 20 mL 0.4 M cerium nitrate + 140 mL 6.8 M NaOH; room-temperature stirring. |
| Hydrothermal support synthesis | 100 °C; hold 24 h; ramp unreported °C/min |  |
| Filter, wash and dry | 65 °C; hold 18 h; ramp unreported °C/min |  |
| Support calcination | 500 °C; hold 4 h; ramp 10 °C/min; air |  |
| Ir deposition | 8 h | 0.5 g support, 20 mL water; variable H2IrCl6 hydrate solution volume for the selected loading. |
| Recover, water/ethanol wash and dry | 60 °C; hold 12 h; ramp unreported °C/min |  |
| Pre-reaction activation | 750 °C; hold 3 h; ramp unreported °C/min; CH4/CO2 1:1 | Separate activation boundary; CH4:CO2 1:1, total 50 mL/min. |

Exact catalog 0.6 wt% sample requires the loading-specific measured composition; no yield inferred.

### S14. 15CuCe deposited/precipitated, Cu mass relative to CeO2 = 15%

Record: `cu-ceria-dp-2022`. Boundary: catalyst_powder.

Source: [Partially sintered copper‒ceria as excellent catalyst for the high-temperature reverse water gas shift reaction](https://pmc.ncbi.nlm.nih.gov/articles/PMC8844362/). [DOI 10.1038/s41467-022-28476-5](https://doi.org/10.1038/s41467-022-28476-5). Locator: Methods: Preparation of copper–ceria catalysts. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Deposition precipitation | Not quantified | 0.50 g CeO2 in 30 mL water; Cu nitrate in 12.5 mL water; 0.50 M Na2CO3 to approximately pH 9. |
| Age slurry | 1 h | Room temperature. |
| Filter and wash | Not quantified | Wash with 1 L water at room temperature. |
| Drying | 75 °C; hold unreported h; ramp unreported °C/min; air | Overnight duration unquantified. |
| Calcination | 600 °C; hold 4 h; ramp 2 °C/min; static air |  |

15CuCe means Cu/CeO2 mass ratio 0.15, not 15 wt% of total catalyst. Do not apply the catalog 15/85 mass fractions as a source measurement.

### S15. Unsupported beta-Mo2N

Record: `beta-mo2n-2024`. Boundary: catalyst_powder.

Source: [Reverse water gas-shift reaction product driven dynamic activation of molybdenum nitride catalyst surface](https://pmc.ncbi.nlm.nih.gov/articles/PMC11271606/). [DOI 10.1038/s41467-024-47550-8](https://doi.org/10.1038/s41467-024-47550-8). Locator: Methods: Catalyst synthesis. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare MoO3 | 500 °C; hold 4 h; ramp unreported °C/min | Calcine ammonium heptamolybdate; cool before nitridation. |
| Nitridation | 300 °C; hold 0 h; ramp 5 °C/min; 700 °C; hold 2 h; ramp 1 °C/min; H2/N2 | 0.5 g MoO3; H2 100 mL/min and N2 45 mL/min. No hold is specified at the 300 °C breakpoint. |
| Cool and passivate | 12 h; 1% O2/Ar | Cool to room temperature; 1% O2/Ar for 12 h. |

No alumina is present. Gamma-Mo2N uses NH3 and is a separate sample; carbide production is excluded.

### S16. Single-atom Ru/LDH; Mg:Al = 5:1

Record: `ru-ldh-2017`. Boundary: catalyst_powder.

Source: [Isolated Single-Atomic Ru Catalyst Bound on a Layered Double Hydroxide for Hydrogenation of CO2 to Formic Acid](https://acs.figshare.com/articles/journal_contribution/Isolated_Single-Atomic_Ru_Catalyst_Bound_on_a_Layered_Double_Hydroxide_for_Hydrogenation_of_CO_sub_2_sub_to_Formic_Acid/4807219). [DOI 10.1021/acscatal.7b00312](https://doi.org/10.1021/acscatal.7b00312). Locator: Supporting Information, PDF page 2: General procedure for preparation of LDHs; Synthesis of catalyst. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| LDH precipitation | Not quantified | 0.01 mol Al nitrate and 0.05 mol Mg nitrate in 100 mL water added to 60 mL Na2CO3/NaOH solution. |
| LDH aging | 65 °C; hold 18 h; ramp unreported °C/min | Vigorous stirring. |
| Recover, wash and dry support | 110 °C; hold unreported h; ramp unreported °C/min | Overnight duration unquantified. |
| Ru deposition | 50 °C; hold 8 h; ramp unreported °C/min | 6.80 mg RuCl3 hydrate, 85 mL water, 10 mL 0.2 M NaOH; 0.5 g LDH. |
| Centrifuge, wash and vacuum dry | vacuum | Overnight; drying temperature not reported. |

80 °C/24 h degassing is BET characterization, not catalyst manufacture; 100 °C/24 h is catalytic testing.

### S17. Ni-Mo nanopowder, nominal precursor Ni:Mo = 6:4 molar

Record: `nimo-powder-2013`. Boundary: catalyst_powder.

Source: [Ni–Mo Nanopowders for Efficient Electrochemical Hydrogen Evolution](https://acs.figshare.com/articles/journal_contribution/Ni_Mo_Nanopowders_for_Efficient_Electrochemical_Hydrogen_Evolution/2447356). [DOI 10.1021/cs300691m](https://doi.org/10.1021/cs300691m). Locator: Supporting Information, S1–S3: Preparation of powders. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Mix precursor | Not quantified | 1.5 g Ni nitrate hexahydrate, 0.6 g ammonium heptamolybdate, 5 mL water, 2 mL 30% NH4OH; add to 45 mL diethylene glycol. |
| Precipitate with heating | Not quantified | Stir 500 rpm; hotplate setpoint 350 °C, solution removed at approximately 110 °C. Setpoint is not sample temperature. |
| Recover and wash | Not quantified | Centrifuge hot suspension approximately 10 min; water and acetone washes; disperse in methanol. |
| Solvent evaporation | 60 °C; hold unreported h; ramp unreported °C/min | Hotplate at 60 °C for several hours; exact duration not reported. |
| First reduction hold | 200 °C; hold 0.5 h; ramp unreported °C/min; 5% H2 / 95% N2 | Forming gas 500 sccm. |
| Second reduction hold | 450 °C; hold 1 h; ramp unreported °C/min; 5% H2 / 95% N2 | Cool under forming gas; wet with isopropanol before air exposure as specified by the source. |

Nominal precursor ratio is not measured product composition. Subsequent coating/annealing on Ti foil is electrode fabrication and is excluded from powder costs.

### S18. Thin alpha-Ni(OH)2 film on FTO for glycerol electrooxidation

Record: `nioh2-film-2022`. Boundary: electrode.

Source: [Predictive control of selective secondary alcohol oxidation of glycerol on NiOOH](https://pmc.ncbi.nlm.nih.gov/articles/PMC9532427/). [DOI 10.1038/s41467-022-33637-7](https://doi.org/10.1038/s41467-022-33637-7). Locator: Methods: Ni(OH)2 electrode preparation. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Clean and mask FTO | Not quantified | Soap, water, acetone, isopropanol, high-purity water; 0.5 cm2 exposed area. |
| Electrodeposition | 0.0125 h | 10 mM Ni nitrate and 30 mM KNO3; -0.25 mA/cm2 for 45 s; three-electrode cell. |
| Rinse and air dry | Not quantified | High-purity water rinse; air stream; duration not reported. |

Electrode fabrication, not powder synthesis. NiOOH develops during electrochemical operation. The thick-film variant uses different deposition conditions.

### S19. Pt/CeO2, measured 1.85 wt% Pt

Record: `pt-ceria-2021`. Boundary: catalyst_powder.

Source: [Dynamic structure of active sites in ceria-supported Pt catalysts for the water gas shift reaction](https://pmc.ncbi.nlm.nih.gov/articles/PMC7876036/). [DOI 10.1038/s41467-021-21132-4](https://doi.org/10.1038/s41467-021-21132-4). Locator: Methods: Sample preparation. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Deposition | 95 °C; hold 24 h; ramp unreported °C/min | 0.5 g ceria, 2.0 g urea, 8 mL water; add 3.3 g aqueous chloroplatinic acid solution (approximately 1 wt% Pt). |
| Wash | Not quantified | Three centrifugation/redispersion cycles in water. |
| Drying | 60 °C; hold unreported h; ramp unreported °C/min | Overnight duration unquantified. |
| Crush and calcine | 500 °C; hold unreported h; ramp 10 °C/min | Hold time not reported in this section. |

Catalog 2.5 wt% Pt is different. The 300 °C/2 h CO treatment in the paper is an in situ microscopy experiment, not a general manufacturing step.

### S20. Cr20/Al2O3-c, nominal 20 wt% Cr2O3

Record: `cr20-alumina-commercialsupport-2017`. Boundary: catalyst_powder.

Source: [Catalytic Behavior of Chromium Oxide Supported on Nanocasting-Prepared Mesoporous Alumina in Dehydrogenation of Propane](https://pmc.ncbi.nlm.nih.gov/articles/PMC5618360/). [DOI 10.3390/nano7090249](https://doi.org/10.3390/nano7090249). Locator: Section 3.1: Catalyst Preparation. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Support calcination | 700 °C; hold 6 h; ramp unreported °C/min; air flow | Commercial gamma-alumina. |
| Chromium impregnation | Not quantified | 1 g support, 3 mL chromium nitrate nonahydrate solution; target 20 wt% Cr2O3. |
| Room-temperature drying | Not quantified | Overnight duration unquantified. |
| Heated drying | 60 °C; hold 6 h; ramp unreported °C/min |  |
| Final calcination | 600 °C; hold 6 h; ramp unreported °C/min; air flow |  |

This reference sample is not the K-promoted catalog 19 wt% Cr2O3 / 1.5 wt% K2O formulation. Nanocast alumina samples require additional support manufacture.

### S21. Au inverse-opal electrode

Record: `au-inverse-opal-2015`. Boundary: electrode.

Source: [Mesostructure-Induced Selectivity in CO2 Reduction Catalysis](https://acs.figshare.com/articles/journal_contribution/Mesostructure_Induced_Selectivity_in_CO_sub_2_sub_Reduction_Catalysis/2104099). [DOI 10.1021/jacs.5b08259](https://doi.org/10.1021/jacs.5b08259). Locator: Supporting Information S3–S4: Synthesis of Gold Inverse Opals. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Clean Au-coated glass | 1 h | Piranha immersion 1 h, no external heating; follow the source safety procedure. |
| Surface treatment | Not quantified | 10 mM sodium mercaptopropanesulfonate overnight; rinse, N2 dry. |
| Template deposition | 55 °C; hold unreported h; ramp unreported °C/min | 0.008 wt% polystyrene spheres and 0.003 wt% IGEPAL; evaporate until dry. |
| Template sintering | 95 °C; hold 2 h; ramp unreported °C/min |  |
| Gold electrodeposition | Not quantified | Ethanol and 0.1 M HClO4 pre-wetting; 50 mM KAuCl4 in 0.1 M HClO4, 0.5 mA/cm2; charge 0.5, 1.5 or 2.5 C/cm2 specifies different thicknesses. |
| Remove template | Not quantified | Toluene overnight; ethanol/water wash; final piranha treatment 10 min. |

Electrode area, charge and substrate are required; this is not a bulk Au powder price model.

### S22. Oxide-derived Cu-500 electrode

Record: `od-cu500-2015`. Boundary: electrode.

Source: [Probing the Active Surface Sites for CO Reduction on Oxide-Derived Copper Electrocatalysts](https://acs.figshare.com/articles/journal_contribution/Probing_the_Active_Surface_Sites_for_CO_Reduction_on_Oxide_Derived_Copper_Electrocatalysts/2202244). [DOI 10.1021/jacs.5b06227](https://doi.org/10.1021/jacs.5b06227). Locator: Supporting Information S2: Materials and Electrode Preparation. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Electropolishing | 0.0833333 h | 85% phosphoric acid, 5 V against Ti counter electrode. |
| Rinse and nitrogen dry | Not quantified |  |
| Oxidation | 500 °C; hold 1 h; ramp unreported °C/min; air |  |
| Slow cooling | Not quantified | Several hours to room temperature; exact duration not reported. |
| Reduction | 130 °C; hold 2 h; ramp unreported °C/min; H2 | H2 200 sccm. |
| Cool under hydrogen | Not quantified | Exact duration not reported. |

The source studies CO reduction, not a complete CO2-to-multicarbon electrode process. Subsequent 200/350 °C annealing variants are not merged.

### S23. 1Ce9CoOx spray-pyrolyzed precursor

Record: `ceco-spray-2023`. Boundary: catalyst_powder.

Source: [Boosting reactivity of water-gas shift reaction by synergistic function over CeO2-x/CoO1-x/Co dual interfacial structures](https://pmc.ncbi.nlm.nih.gov/articles/PMC10611738/). [DOI 10.1038/s41467-023-42577-9](https://doi.org/10.1038/s41467-023-42577-9). Locator: Methods: Catalyst preparations. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Precursor solution | 0.166667 h | 8 mmol total Co/Ce nitrates, Ce:Co 1:9 molar, 60 mL ethanol. |
| Spray pyrolysis | 400 °C; hold unreported h; ramp unreported °C/min; N2 | Ultrasonic aerosol, pure N2 carrier, 90 cm glass tube; feed rate and collection duration unreported. |
| Drying | 70 °C; hold unreported h; ramp unreported °C/min | Overnight duration unquantified. |

Ce:Co 9:1 is a separate sample. Neither ratio establishes the catalog 18 wt% Co composition. Reduction to the active dual-interface material requires its separate activation conditions.

### S24. Ba0.3(SO4)deltaW0.2Ru0.5O2-delta powder

Record: `ba-w-ru-sulfate-2023`. Boundary: catalyst_powder.

Source: [Stabilizing ruthenium dioxide with cation-anchored sulfate for durable oxygen evolution in proton-exchange membrane water electrolyzers](https://pmc.ncbi.nlm.nih.gov/articles/PMC10703920/). [DOI 10.1038/s41467-023-43977-7](https://doi.org/10.1038/s41467-023-43977-7). Locator: Methods: Catalyst synthesis. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Precursor dispersion | Not quantified | 0.1 mmol Ru(acac)3, 0.02 mmol BaWO4, 0.6 mmol thiourea in 10 mL oleylamine; sonicate 30 min. |
| Stir under nitrogen | 0.5 h; N2 |  |
| Sulfide synthesis | 250 °C; hold 2.5 h; ramp unreported °C/min; N2 |  |
| Recover and wash | Not quantified | Cool; centrifuge and ethanol-wash at least five times. |
| Disperse on carbon | 10 h | 50 mL cyclohexane, 23 mg Vulcan XC72; stir and sonicate. |
| Filter and dry | 80 °C; hold 5 h; ramp unreported °C/min |  |
| Oxidize | 400 °C; hold 5 h; ramp unreported °C/min; air |  |
| Acid wash and filter | 12 h | 0.5 M H2SO4. |

Ba, W and sulfate are part of this material; the catalog pure RuO2 proxy is not its composition. PEMWE testing uses material without carbon support; final carbon removal/output must be reconciled.

### S25. Unsupported IrO2 comparator

Record: `iro2-adams-2023`. Boundary: catalyst_powder.

Source: [Nano-metal diborides-supported anode catalyst with strongly coupled TaOx/IrO2 catalytic layer for low-iridium-loading proton exchange membrane electrolyzer](https://pmc.ncbi.nlm.nih.gov/articles/PMC10447464/). [DOI 10.1038/s41467-023-40912-8](https://doi.org/10.1038/s41467-023-40912-8). Locator: Methods: Materials synthesis, unsupported IrO2 comparator prepared without TaB2. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Precursor dispersion | Not quantified | K2IrCl6 in isopropanol with NaNO3; omit TaB2 for the unsupported comparator; sonicate 30 min. |
| Drying | 90 °C; hold 5 h; ramp unreported °C/min |  |
| Grind and heat | 350 °C; hold 1 h; ramp 5 °C/min |  |
| Cool and wash | Not quantified | Natural cooling; ethanol and water wash to remove residual salts. |
| Final drying | 90 °C; hold 12 h; ramp unreported °C/min |  |

Precursor quantities and finished mass must be specified for a costed batch. Supported IrO2@TaB2 requires a separate diboride synthesis and is not interchangeable with this comparator.

### S26. Fe-N-C with chemical vapor modification (CVM)

Record: `fe-nc-cvm-2024`. Boundary: catalyst_powder.

Source: [Monosymmetric Fe-N4 sites enabling durable proton exchange membrane fuel cell cathode by chemical vapor modification](https://pmc.ncbi.nlm.nih.gov/articles/PMC11101623/). [DOI 10.1038/s41467-024-47817-0](https://doi.org/10.1038/s41467-024-47817-0). Locator: Methods: Synthesis of FeZn-ZIFs; Synthesis of Fe-N-C; Synthesis of Fe-N-CCVM. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| ZIF synthesis | 24 h | 3.0 g Zn nitrate, 440 mg Fe(acac)3 in 40 mL methanol + 6.5 g 2-methylimidazole in 80 mL methanol; room temperature. |
| Recover, wash and vacuum dry | 55 °C; hold 12 h; ramp unreported °C/min; vacuum | Three ethanol washes. |
| Pyrolysis | 950 °C; hold 2 h; ramp 5 °C/min; 10% H2 / 90% Ar |  |
| Acid etching | 12 h | Cool; 1 M HCl. |
| Wash and dry | 55 °C; hold unreported h; ramp unreported °C/min | High-purity water wash; dry thoroughly; exact drying duration unreported. |
| Chemical vapor modification | 900 °C; hold 2 h; ramp 5 °C/min; Ar | 60 mg Fe-N-C downstream at 900 °C/2 h, 5 °C/min; separate upstream 2.0 g cyanamide zone heated to 700 °C at 10 °C/min. Two-zone energy consumption must be measured separately. |

Powder manufacture, not complete PEMFC electrode fabrication. The two heated zones are simultaneous, not two serial catalyst treatments.

### S27. Fe-NCBrCl, measured 2.50 wt% Fe

Record: `fe-nc-brcl-2024`. Boundary: catalyst_powder.

Source: [A Fe-NC electrocatalyst boosted by trace bromide ions with high performance in proton exchange membrane fuel cells](https://pmc.ncbi.nlm.nih.gov/articles/PMC11362171/). [DOI 10.1038/s41467-024-51858-w](https://doi.org/10.1038/s41467-024-51858-w). Locator: Methods: Catalyst synthesis. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| ZIF-8 synthesis | 16 h | 10 mmol Zn nitrate and 80 mmol 2-methylimidazole, each in 100 mL methanol; sonicate separately 5 min, combine and stir at room temperature. |
| Recover, wash and vacuum dry | 60 °C; hold unreported h; ramp unreported °C/min; vacuum | Methanol washes; overnight drying duration unquantified. |
| Phenanthroline incorporation | 12 h | 1.0 g ZIF-8 + 0.3 g phenanthroline in ethanol/water 2:1; room temperature. |
| Evaporation | 80 °C; hold unreported h; ramp unreported °C/min | Exact duration unreported. |
| Grind and pyrolyze | 1000 °C; hold 1 h; ramp 5 °C/min; Ar |  |
| Salt and Fe incorporation | Not quantified | 100 mg NC + 150 mg NH4Cl + 150 mg NH4Br + 6 mg FeCl2 tetrahydrate; grind after natural cooling. |
| Second pyrolysis | 900 °C; hold 1 h; ramp 10 °C/min; Ar |  |

The unmodified Fe-NC comparator contains 2.25 wt% Fe. Br/Cl treatments and electrode ink/assembly must not be treated as interchangeable variants.

### S28. 15 wt% Ag/alpha-Al2O3

Record: `ag15-alumina-2023`. Boundary: catalyst_powder.

Source: [Revealing the Nature of Active Oxygen Species and Reaction Mechanism of Ethylene Epoxidation by Supported Ag/α-Al
                    2
                    O
                    3
                    Catalysts](https://pmc.ncbi.nlm.nih.gov/articles/PMC10775145/). [DOI 10.1021/acscatal.3c04361](https://doi.org/10.1021/acscatal.3c04361). Locator: Methods: Catalyst Synthesis. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare Ag complex | Not quantified | Silver oxalate prepared from silver nitrate and oxalic acid; mix oxalate, ethylenediamine and water in mass ratio 1:0.5:0.5. Oxalate preparation time unreported. |
| Incipient-wetness impregnation | 0.5 h | Target 15 wt% Ag on alpha-Al2O3; stir. |
| Dry | 90 °C; hold unreported h; ramp unreported °C/min | Overnight; exact duration unreported. |
| Calcine | 450 °C; hold 0.75 h; ramp unreported °C/min; N2 |  |

Nominal composition matches the unpromoted Ag screening case. This does not supply actual yield, utility use or Cs/Re-promoted manufacturing. Test-bed sieving to 40–60 mesh is separate.

### S29. VWTi powder on commercial W-containing TiO2

Record: `v-wti-powder-2021`. Boundary: catalyst_powder.

Source: [Simple physical mixing of zeolite prevents sulfur deactivation of vanadia catalysts for NOx removal](https://pmc.ncbi.nlm.nih.gov/articles/PMC7876025/). [DOI 10.1038/s41467-021-21228-x](https://doi.org/10.1038/s41467-021-21228-x). Locator: Methods: Synthesis of catalyst and physical mixing with zeolite. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare vanadium solution | 0.5 h | Dissolve ammonium metavanadate in oxalic acid solution. Add DT-52 support reported as 7.7 wt% tungsten; this is not a WO3 mass fraction. |
| Evaporate | Not quantified | Rotary evaporator; temperature and duration unreported. |
| Dry | 105 °C; hold unreported h; ramp unreported °C/min | Forced-convection oven; overnight duration unreported. |
| Calcine | 500 °C; hold 4 h; ramp unreported °C/min | Atmosphere and ramp not stated in this Methods paragraph. |

Powder only: monolith washcoating and its binder are not disclosed here. The separate VWTi/zeolite mixture uses 2:1 mass ratio; it is not the baseline powder. Exact V loading requires the specimen-specific analysis.

### S30. Cu-SSZ-13 from supplied NH4-SSZ-13 (Si/Al2 = 23)

Record: `cu-ssz13-exchange-2021`. Boundary: catalyst_powder.

Source: [Simple physical mixing of zeolite prevents sulfur deactivation of vanadia catalysts for NOx removal](https://pmc.ncbi.nlm.nih.gov/articles/PMC7876025/). [DOI 10.1038/s41467-021-21228-x](https://doi.org/10.1038/s41467-021-21228-x). Locator: Methods: Synthesis of catalyst and physical mixing with zeolite. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Cu ion exchange | 65 °C; hold 24 h; ramp unreported °C/min | 1 g supplied NH4-SSZ-13 in 0.1 M copper nitrate solution; solution volume unreported. |
| Filter and dry | 105 °C; hold unreported h; ramp unreported °C/min | Forced-convection oven; drying duration unreported. |
| Calcine | 550 °C; hold 4 h; ramp unreported °C/min | Ramp and atmosphere not specified. |

Parent zeolite is supplied, not synthesized by this sequence. The separate Si/Al2 = 9 synthesis is a different specimen. Cu loading and monolith manufacturing are not inferred.

### S31. CZA, Cu:Zn:Al = 7:2:1 molar, ex situ reduction

Record: `cza-coprecipitation-2020`. Boundary: catalyst_powder.

Source: [Synergistic ultraviolet and visible light photo-activation enables intensified low-temperature methanol synthesis over copper/zinc oxide/alumina](https://pmc.ncbi.nlm.nih.gov/articles/PMC7109065/). [DOI 10.1038/s41467-020-15445-z](https://doi.org/10.1038/s41467-020-15445-z). Locator: Methods: Catalyst synthesis. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Mix nitrates | 65 °C; hold 0.3333333333333333 h; ramp unreported °C/min | 14, 4 and 2 mL of 0.5 M Cu, Zn and Al nitrates, respectively. |
| Precipitate | 65 °C; hold 0.16666666666666666 h; ramp unreported °C/min | Add 10 mL 1.2 M sodium carbonate dropwise; stir another 10 min. |
| Age, wash and filter | Not quantified | Aging exceeds 60 min; exact time unspecified. |
| Dry | Not quantified | Overnight above 80 °C; neither exact temperature nor duration is reported. |
| Grind and calcine | 250 °C; hold 3 h; ramp 5 °C/min; air | Air flow 30 mL/min; reference state unreported. |
| Ex situ reduction | 250 °C; hold 3 h; ramp unreported °C/min; 10% H2/N2 | Selected preparation variant. The separate in situ 350 °C/1 h route must not be appended. |

Molar precursor ratio is not a final oxide mass fraction or an industrial CZA formulation. The source tests photothermal CO2 hydrogenation, not the catalog syngas process.

### S32. 20% Fe/Al2O3, 500 °C calcination variant

Record: `fe20-alumina-500-2024`. Boundary: catalyst_powder.

Source: [Hydrogen Production via Methane Decomposition over Alumina Doped with Titanium Oxide‐Supported Iron Catalyst for Various Calcination Temperatures](https://pmc.ncbi.nlm.nih.gov/articles/PMC11004458/). [DOI 10.1002/open.202300173](https://doi.org/10.1002/open.202300173). Locator: Experimental Section: Catalyst Preparation. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Dissolve iron precursor | 0.25 h | Stir in water at room temperature. The source prints Fe(NO3)2·9H2O; precursor identity requires clarification rather than silent chemical correction. |
| Add alumina and impregnate | 80 °C; hold 3 h; ramp unreported °C/min |  |
| Dry | 120 °C; hold unreported h; ramp unreported °C/min | Overnight duration unreported. |
| Calcine | 500 °C; hold 5 h; ramp unreported °C/min | Selected 500 °C specimen; 300 and 800 °C are alternative preparations. |

The mixed alumina–titania support is a different specimen. Source precursor formula is unresolved; do not use it to calculate stoichiometric purchases. Activation and actual batch output remain separate inputs.

### S33. 6 wt% Co/alpha-Al2O3, calcined precursor

Record: `co6-alumina-2018`. Boundary: catalyst_powder.

Source: [Activity enhancement of cobalt catalysts by tuning metal-support interactions](https://pmc.ncbi.nlm.nih.gov/articles/PMC6203836/). [DOI 10.1038/s41467-018-06903-w](https://doi.org/10.1038/s41467-018-06903-w). Locator: Methods: Synthesis. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Sieve support | Not quantified | 75–150 micrometre alpha-Al2O3 grains. |
| Pre-dry support | 80 °C; hold 1 h; ramp unreported °C/min; vacuum | 2 g support. |
| Impregnate | Not quantified | Pore-filling aqueous Co nitrate hexahydrate for 6 wt% Co; magnetic/manual mixing. |
| Dry | 60 °C; hold 12 h; ramp unreported °C/min; stagnant air |  |
| Calcine | 350 °C; hold 2 h; ramp 3 °C/min; N2 | N2 flow 1 L/min; reference state not specified. |
| Combine, press and sieve | Not quantified | Multiple 2 g batches combined; 75–150 micrometre fraction. No yield is inferred. |

This 6 wt% Co, alpha-alumina specimen differs from the catalog commercial Co/alumina formulation. Reduction–oxidation and subsequent activation are separate experimental treatments, not appended here.

### S34. Sn quantum sheets confined in graphene

Record: `sn-graphene-sheets-2016`. Boundary: catalyst_powder.

Source: [Metallic tin quantum sheets confined in graphene toward high-efficiency carbon dioxide electroreduction](https://pmc.ncbi.nlm.nih.gov/articles/PMC5025773/). [DOI 10.1038/ncomms12697](https://doi.org/10.1038/ncomms12697). Locator: Methods: Synthesis of Sn quantum sheets confined in grapheme. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Disperse SnO2 sheets | 0.5 h | 10 mg preformed ultrathin SnO2 in 40 mL 0.03 M glucose solution; upstream sheet synthesis is referred to an earlier paper. |
| Hydrothermal treatment | 180 °C; hold 10 h; ramp unreported °C/min |  |
| First anneal | 500 °C; hold 2 h; ramp unreported °C/min; Ar |  |
| Second anneal | 1000 °C; hold 0.08333333333333333 h; ramp unreported °C/min; Ar | Immediately follows first anneal; ramps unreported. |
| Rapid cooling | Not quantified | Room temperature within 1 min under Ar; exact time not assigned. |

Composite powder, not bulk Sn and not a finished electrode. Upstream ultrathin SnO2 synthesis, Sn mass fraction and coating operations are incomplete.

### S35. 2 wt% Pt/P25 prepared by the 1.8 nm Pt route

Record: `pt2-p25-2018`. Boundary: catalyst_powder.

Source: [Size-dependent activity and selectivity of carbon dioxide photocatalytic reduction over platinum nanoparticles](https://pmc.ncbi.nlm.nih.gov/articles/PMC5871894/). [DOI 10.1038/s41467-018-03666-2](https://doi.org/10.1038/s41467-018-03666-2). Locator: Methods: Preparation of catalysts; explicit P25 support substitution. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Disperse support | 0.25 h | 0.2 g P25 in 50 mL ethylene glycol. |
| Add Pt precursor | 0.5 h | 2.1 mL H2PtCl6·6H2O solution in ethylene glycol (5 mg/mL); stir. |
| Purge and reduce | 159.85 °C; hold 2 h; ramp unreported °C/min; N2 | Evacuate/fill N2; add 1.25 mL 0.25 M NaOH in ethylene glycol. Reported 433 K. |
| Cool and acidify | 2 h | After room-temperature cooling add 2 mL 0.25 M HCl in ethylene glycol; stir. |
| Wash and vacuum dry | 60 °C; hold unreported h; ramp unreported °C/min; vacuum | Ethanol and water wash; overnight duration unreported. |

P25 is a supplied mixed-phase support, not pure anatase. This is the named P25 comparator; the main HTSO support and other Pt size variants require different preparation.

### S36. Porous Cu on stainless-steel mesh for Li-mediated NRR

Record: `porous-cu-nrr-2022`. Boundary: electrode.

Source: [Electrosynthesis of ammonia with high selectivity and high rates via engineering of the solid-electrolyte interphase](https://pmc.ncbi.nlm.nih.gov/articles/PMC9511958/). [DOI 10.1016/j.joule.2022.07.009](https://doi.org/10.1016/j.joule.2022.07.009). Locator: Experimental procedures: Preparation of porous Cu electrode. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare mesh | Not quantified | 0.2–1 cm2 SS316 mesh, spot-weld Cu wire; geometry is an experimental range. |
| Clean substrate | Not quantified | Dip in 0.06 M HCl; rinse with water and ethanol. |
| Electrodeposit Cu | Not quantified | 0.4 M CuSO4 in 1.5 M H2SO4; total current −2 A; 15 s–7 min are variants, not a fixed duration. |
| Wash and vacuum dry | Not quantified | Repeated water/ethanol cleaning; drying temperature and time unreported. |
| Trim and store | Not quantified | Remove excess Cu outside geometric area; Ar glovebox storage. |

Substrate preparation only: Li deposition/SEI formation occurs separately during electrochemical operation. Do not describe this as an aqueous Cu catalyst proving ammonia production.

### S37. 20 wt% Pt/Ketjenblack, 200 °C variant

Record: `pt20-kb-200-2025`. Boundary: catalyst_powder.

Source: [Self-modulated hydrogen electrocatalysis on sub-2-nm platinum nanoparticles by in situ generated surface hydrides](https://pmc.ncbi.nlm.nih.gov/articles/PMC12638883/). [DOI 10.1038/s41467-025-65122-2](https://doi.org/10.1038/s41467-025-65122-2). Locator: Methods: Catalyst preparation. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Impregnate and stir | 3 h | 160 mg Ketjenblack EC300J; 1.062 mL H2PtCl6 solution (38 mg Pt/mL) and 1.5 mL 0.816 M NaOH. |
| Sonicate | 0.5 h |  |
| Freeze-dry | 24 h |  |
| Reduce | 200 °C; hold 2 h; ramp unreported °C/min; 4% H2/Ar | Selected 200 °C variant; 400 and 600 °C are separate specimens. |
| Wash and freeze-dry | Not quantified | Three ultrapure-water washes; final freeze-drying time unreported. |

Powder only; ionomer ink and electrode assembly are separate. This source prepares Pt/C, not the PtCo formulation to which the catalog links it.

### S38. 6 wt% Ni/dBeta D, flowing-air powder variant

Record: `ni6-dbeta-d-2024`. Boundary: catalyst_powder.

Source: [Tuning metal-support interactions in nickel–zeolite catalysts leads to enhanced stability during dry reforming of methane](https://pmc.ncbi.nlm.nih.gov/articles/PMC11452210/). [DOI 10.1038/s41467-024-50729-8](https://doi.org/10.1038/s41467-024-50729-8). Locator: Methods: Materials and catalysts. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Convert NH4-Beta to H-Beta | 550 °C; hold 12 h; ramp unreported °C/min; air | Air 600 mL/min; flow reference unspecified. |
| Dealuminate | 80 °C; hold 16 h; ramp unreported °C/min | 1 g H-Beta and 25 mL concentrated nitric acid. |
| Recover, wash and dry | 90 °C; hold unreported h; ramp unreported °C/min | Centrifuge and wash; dry overnight. |
| Grind with Ni precursor | 0.333333 h | Nickel nitrate hexahydrate for nominal 6 wt% Ni. |
| Staged calcination | 100 °C; hold 3 h; ramp 1 °C/min; 600 °C; hold 6 h; ramp 1 °C/min; air | Approximately 1 g precursor in ceramic boat; air 1200 mL/min. Starting temperature and flow reference unreported. |

Static-air NP and packed-bed D/HD samples are distinct. Pre-test calcination and optional 750 °C H2 reduction are excluded from this as-prepared powder record. Nominal loading differs from other screening formulations.

### S39. Ir/MnOx on carbon, 300 °C variant

Record: `ir-mnox-carbon-300-2024`. Boundary: catalyst_powder.

Source: [Ir-O-Mn embedded in porous nanosheets enhances charge transfer in low-iridium PEM electrolyzers](https://pmc.ncbi.nlm.nih.gov/articles/PMC11696821/). [DOI 10.1038/s41467-024-54646-8](https://doi.org/10.1038/s41467-024-54646-8). Locator: Methods: Synthesis of Ir-Mn bimetallic oxide precursor; Synthesis of Ir/MnOx catalyst. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Hydrolyze Ir precursor | 80 °C; hold unreported h; ramp unreported °C/min | 200 microlitre H2IrCl6·H2O solution (0.1 g/mL) in 10 mL 0.1 M KOH; wait until near-colorless, then heat until light blue. Durations unreported. |
| Add Mn and react | 80 °C; hold 2 h; ramp unreported °C/min | 1 mL MnCl2 solution (10 mg/mL), added dropwise. |
| Wash and disperse | Not quantified | Three water washes and one ethanol wash; disperse in ethanol. |
| Mix with carbon | 1 h | Add 10 mg carbon black; ambient sonication. |
| Recover and dry | 60 °C; hold 3 h; ramp unreported °C/min | Centrifuge before drying. |
| Heat-treat | 300 °C; hold 1 h; ramp unreported °C/min; H2/Ar | Gas fraction, flow and ramp unreported. |

Carbon-supported powder only; separate anode and PEMWE fabrication are not included. Catalog oxide/metal fractions cannot be inferred from precursor quantities alone.

### S40. Urea-derived g-C3N4, 550 °C variant without cocatalyst

Record: `gcn-urea-550-2016`. Boundary: catalyst_powder.

Source: [Overall water splitting by Pt/g-C
                    3
                    N
                    4
                    photocatalysts without using sacrificial agents](https://pmc.ncbi.nlm.nih.gov/articles/PMC6005136/). [DOI 10.1039/c5sc04572j](https://doi.org/10.1039/c5sc04572j). Locator: Supporting Information p 1: Methods, Catalysts preparation. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Load urea | Not quantified | 10 g urea in a covered crucible. This is input mass, not recovered catalyst output. |
| Polymerize | 550 °C; hold 2 h; ramp 5 °C/min; air flow | Selected 550 °C specimen; 500, 525, 575 and 600 °C are alternatives. |
| Cool and recover | Not quantified | Natural cooling to room temperature; duration and final dry output unreported. |

Metal-free support preparation only. The source adds Pt/other cocatalysts in separate experiments; overall water splitting must not be attributed to this unmodified powder alone.

### S41. PdCu encapsulated in silicalite-1 (PdCu@S-1)

Record: `pdcu-silicalite-2022`. Boundary: catalyst_powder.

Source: [Alloyed PdCu Nanoparticles within Siliceous Zeolite Crystals for Catalytic Semihydrogenation](https://pmc.ncbi.nlm.nih.gov/articles/PMC9888633/). [DOI 10.1021/acsmaterialsau.1c00080](https://doi.org/10.1021/acsmaterialsau.1c00080). Locator: Materials and Methods: Synthesis of PdCu@S-1. Crossref checked: 2026-09-14.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare zeolite solution | Not quantified | 14.88 g 40 wt% TPAOH and 90.24 g water; stir 10 min. Add 26.16 g TEOS and stir 6 h at room temperature. |
| Prepare metal solution | Not quantified | 0.75 mL Na2PdCl4 (20 mg/mL) and 0.285 g Cu nitrate trihydrate in 5 mL water; stir 30 min. Add 0.606 g ethylenediamine; stir 30 min. |
| Combine solutions | 0.166667 h | Room-temperature stirring. |
| Hydrothermal synthesis | 180 °C; hold 96 h; ramp unreported °C/min |  |
| Remove organic template | 550 °C; hold 4 h; ramp unreported °C/min; air |  |

Encapsulated PdCu/zeolite is not the catalog single-atom-alloy composition or alumina support. Recovery, washing, yield and precursor conversion are not fully specified by this subsection.

### S42. Ni/SiO2, Gen 1, nominal 5 wt% Ni

Record: `ni-silica-gen1-2024`. Boundary: catalyst_powder.

Source: [Cost‐Responsive Optimization of Nickel Nanoparticle Synthesis](https://doi.org/10.1002/adsu.202300030). [DOI 10.1002/adsu.202300030](https://doi.org/10.1002/adsu.202300030). Locator: Experimental Section: solution-phase synthesis Gen 1; synthesis of silica-supported Ni NPs (published PDF p. 6). Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Charge nickel precursor and solvents | Not quantified | Three-neck flask with condenser; nitrogen handling. |
| Evacuate and backfill | N2/vacuum | Three cycles; cycle duration and gas flow not reported. |
| Degas | 100 °C; hold 1 h; ramp unreported °C/min; vacuum | Rapid heating; ramp rate not reported. |
| Cool | Not quantified | Natural cooling to ambient temperature; duration not reported. |
| Add phosphine | N2 | At room temperature under nitrogen. |
| Evacuate and backfill | N2/vacuum | Three cycles; cycle duration and gas flow not reported. |
| Nanoparticle synthesis | 220 °C; hold 2 h; ramp unreported °C/min; N2 | Rapid heating; ramp rate not reported. |
| Cool | Not quantified | Natural cooling to ambient temperature; duration not reported. |
| Precipitate and centrifuge | 0.166667 h | Centrifugation for 10 min at 8000 rpm. Precipitation and transfer time are additional and unreported. |
| Deposit on silica | Not quantified | Redisperse recovered nanoparticles in 10 mL chloroform; add to a 1 g/mL silica suspension targeting 5 wt% Ni. Silica and suspension quantities require recovered Ni amount. |
| Sonicate | 0.0833333 h |  |
| Stir | Not quantified | Overnight; duration not quantified. |
| Separate | Not quantified | Centrifugation; speed and duration of this second separation not reported. |
| Dry | vacuum | Vacuum drying; temperature and time not reported. Store dried catalyst under nitrogen. |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Charge nickel precursor and solvents | Ni(acac)2 | 2 g |  |
| Charge nickel precursor and solvents | Oleylamine, 70% | 25.6 mL |  |
| Charge nickel precursor and solvents | 1-Octadecene, 90% | 2 mL |  |
| Add phosphine | Trioctylphosphine | 1.74 mL | The source volume is explicit; its stated equivalents conflict with its mmol values. |
| Precipitate and centrifuge | Acetone | 40 mL |  |
| Deposit on silica | Chloroform for redispersion | 10 mL |  |
| Deposit on silica | Silica support | Not verified / 확인 못 함 |  |
| Deposit on silica | Chloroform for silica suspension | Not verified / 확인 못 함 |  |

The supported product is nominally 5 wt% Ni/SiO2; nanoparticle yield is not the recovered dry mass of this supported batch. No complete purchasing bill, supplier prices, mean equipment power, gas flow, attended labor or dry batch output is established by these Methods. The published material-cost comparison excludes complete capital and operating costs. Its published 2016-dollar prices are not live quotes and are not imported. Precipitation/transfer and cooling times remain additional unknowns. Ambient temperature and overnight duration have not been assigned numeric values. Gen 1 reports TOP as 1.74 mL, 3.9 mmol and 2 equivalents against 7.8 mmol Ni; the equivalence statement conflicts with the stated amounts. Only the explicit volume is transcribed.

### S43. Ni/SiO2, Gen 4, nominal 5 wt% Ni

Record: `ni-silica-gen4-2024`. Boundary: catalyst_powder.

Source: [Cost‐Responsive Optimization of Nickel Nanoparticle Synthesis](https://doi.org/10.1002/adsu.202300030). [DOI 10.1002/adsu.202300030](https://doi.org/10.1002/adsu.202300030). Locator: Experimental Section: solution-phase synthesis Gen 4; synthesis of silica-supported Ni NPs (published PDF p. 6). Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Charge nickel precursor and solvents | Not quantified | Three-neck flask with condenser; nitrogen handling. |
| Evacuate and backfill | N2/vacuum | Three cycles; cycle duration and gas flow not reported. |
| Degas | 100 °C; hold 1 h; ramp unreported °C/min; vacuum | Rapid heating; ramp rate not reported. |
| Cool | Not quantified | Natural cooling to ambient temperature; duration not reported. |
| Add phosphine | N2 | At room temperature under nitrogen. |
| Evacuate and backfill | N2/vacuum | Three cycles; cycle duration and gas flow not reported. |
| Nanoparticle synthesis | 220 °C; hold 1 h; ramp unreported °C/min; N2 | Rapid heating; ramp rate not reported. |
| Cool | Not quantified | Natural cooling to ambient temperature; duration not reported. |
| Precipitate and centrifuge | 0.166667 h | Centrifugation for 10 min at 8000 rpm. Precipitation and transfer time are additional and unreported. |
| Deposit on silica | Not quantified | Redisperse recovered nanoparticles in 10 mL chloroform; add to a 1 g/mL silica suspension targeting 5 wt% Ni. Silica and suspension quantities require recovered Ni amount. |
| Sonicate | 0.0833333 h |  |
| Stir | Not quantified | Overnight; duration not quantified. |
| Separate | Not quantified | Centrifugation; speed and duration of this second separation not reported. |
| Dry | vacuum | Vacuum drying; temperature and time not reported. Store dried catalyst under nitrogen. |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Charge nickel precursor and solvents | Ni(OAc)2·4H2O | 0.97 g |  |
| Charge nickel precursor and solvents | Oleylamine, 70% | 12.8 mL |  |
| Add phosphine | Triphenylphosphine | 4.08 g |  |
| Precipitate and centrifuge | Chloroform | Not verified / 확인 못 함 | Approximately 5 mL in the source; not entered as an exact quantity. |
| Precipitate and centrifuge | Isopropanol | 20 mL |  |
| Deposit on silica | Chloroform for redispersion | 10 mL |  |
| Deposit on silica | Silica support | Not verified / 확인 못 함 |  |
| Deposit on silica | Chloroform for silica suspension | Not verified / 확인 못 함 |  |

The supported product is nominally 5 wt% Ni/SiO2; nanoparticle yield is not the recovered dry mass of this supported batch. No complete purchasing bill, supplier prices, mean equipment power, gas flow, attended labor or dry batch output is established by these Methods. The published material-cost comparison excludes complete capital and operating costs. Its published 2016-dollar prices are not live quotes and are not imported. Precipitation/transfer and cooling times remain additional unknowns. Ambient temperature and overnight duration have not been assigned numeric values.

### S44. Pt/SrTiO3 by solution-phase metalation, nominal 1 wt% Pt

Record: `pt-sto-somc-2025`. Boundary: catalyst_powder.

Source: [Techno-economic and life cycle analyses of the synthesis of a platinum–strontium titanate catalyst](https://doi.org/10.1039/d5cy00189g). [DOI 10.1039/d5cy00189g](https://doi.org/10.1039/d5cy00189g). Locator: Materials and methods: Synthesis of Pt/STO at laboratory scale (published PDF pp. 2–3). Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare strontium solution | 2 h |  |
| Prepare titanium solution | 0.166667 h |  |
| Mix solutions | 0.166667 h |  |
| Add base | 0.466667 h | 10 M solution; source reports 276.9 g and 10 mL/min for 28 min. No density is inferred to reconcile these quantities. |
| Settle | 0.166667 h |  |
| Hydrothermal treatment | 240 °C; hold unreported h; ramp 2 °C/min | Source says heated to 240 °C at 2 °C/min over the next 2 h. The division between ramp and hold is ambiguous; hold time is not assigned. |
| Cool and wash | Not quantified | Cooling rate 2 °C/min; end temperature and washing quantities unspecified. Final solution pH 13.2. Vacuum filtration. |
| Dry support | 110 °C; hold 12 h; ramp unreported °C/min; air |  |
| Calcine support | 550 °C; hold 4 h; ramp unreported °C/min |  |
| Vacuum pretreatment | 200 °C; hold unreported h; ramp unreported °C/min; vacuum | Duration not specified for this initial treatment. |
| Ozone treatment | 200 °C; hold 2 h; ramp unreported °C/min; 8% O3 in O2 | 400 sccm; standard reference temperature and pressure not specified. |
| Hydroxylation | 200 °C; hold 2 h; ramp unreported °C/min; humidified N2 | N2 bubbled through water at ambient temperature; powder remains at 200 °C. Flow not reported. |
| Support pretreatment before metalation | 200 °C; hold 12 h; ramp unreported °C/min | The source specifies 200 °C, 12 h for the support added to the precursor solution. |
| Metalation | 120 °C; hold 72 h; ramp unreported °C/min; N2 | N2 glovebox; precursor solution targets 1 wt% Pt. Solution and support quantities unspecified. |
| Cool | Not quantified | Room temperature; time unspecified. |
| Wash with toluene | Not quantified | Wash/filter three times; volume and time per wash unreported. |
| Exchange solvent | Not quantified | One final wash with pentane; volume and time unreported. |
| Vacuum dry | 60 °C; hold unreported h; ramp unreported °C/min; vacuum | Overnight; duration not quantified. |
| Reduce | 300 °C; hold 4 h; ramp unreported °C/min; 10% H2 | 10% H2; carrier identity and flow not specified in this Methods paragraph. |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Prepare strontium solution | Sr(OH)2·8H2O | 38.7 g |  |
| Prepare strontium solution | Acetic acid | 48 g |  |
| Prepare strontium solution | Water | 640 g |  |
| Prepare titanium solution | TiCl4 | 27.6 g |  |
| Prepare titanium solution | Ethanol | 505 g |  |
| Add base | NaOH solution, 10 M | 276.9 g |  |
| Metalation | MeCpPtMe3, 98% | Not verified / 확인 못 함 |  |
| Metalation | Dodecane | Not verified / 확인 못 함 |  |
| Wash with toluene | Toluene | Not verified / 확인 못 함 |  |
| Exchange solvent | Pentane | Not verified / 확인 못 함 |  |

The laboratory procedure is summarized in the TEA paper from earlier experimental studies; the original experimental references remain necessary for full replication. The 240 °C hydrothermal ramp/hold wording is unresolved. The 2 °C/min heating rate is transcribed; no separate 2 h hold is assumed. The published 285 kg batch and industrial utility estimates belong to a scale-up model, not measurements of this laboratory batch. Actual recovered dry mass, mean equipment powers, gas-reference conditions and complete precursor/solvent quantities remain unknown.

### S45. PtSn/Al2O3 pellets

Record: `ptsn-alumina-base-2024`. Boundary: catalyst_powder.

Source: [The Acid Roles of PtSn@Al2O3 in the Synthesis and Performance of Propane Dehydrogenation](https://doi.org/10.3390/molecules29132959). [DOI 10.3390/molecules29132959](https://doi.org/10.3390/molecules29132959). Locator: Section4.1 Synthesis of Catalysts: Sn/Al2O3 pellets and PtSn/Al2O3(-CA). Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare Sn-containing powder blend | Intermediate batch: blend | 20.000 g boehmite plus 0.3297 g SnC2O4. Input total is not measured recovered blend mass. |
| Prepare pellet bath | Intermediate batch: pellets | Add HCl until pH 2. |
| Prepare pellet slurry | 2 h; Intermediate batch: pellets | Use 3.750 g of the preceding blend; internally transferred, not repurchased. |
| Form and react pellets | 0.5 h; Intermediate batch: pellets | Drip slurry from a syringe into the bath; dripping time is additional and unreported. |
| Wash pellets | Intermediate batch: pellets | Three water washes; per-wash duration and volume unreported. |
| Dry pellets | air; Intermediate batch: pellets | Ambient air until dry; temperature and duration unreported. |
| Calcine pellets | 110 °C; hold 0.5 h; ramp unreported °C/min; 350 °C; hold 0.5 h; ramp 4 °C/min; 560 °C; hold 4 h; ramp 1.75 °C/min; Intermediate batch: pellets | Source ramp durations: room temperature to 110 °C in 30 min; 110 to 350 °C in 60 min; 350 to 560 °C in 120 min. First ramp rate cannot be inferred without starting temperature. Later rates are exact endpoint/time conversions. |
| Impregnate Pt | 3 h | Use 3.0000 g recovered pellets. Precursor solution is 30 mmol/L; no independent solution-density conversion. |
| Dry impregnated pellets | 110 °C; hold unreported h; ramp unreported °C/min | Overnight duration unreported. |
| Calcine Pt-containing pellets | 400 °C; hold 2 h; ramp unreported °C/min |  |

Intermediate transfers (recovery is not inferred from precursor inputs):

| Intermediate / destination | Recovered kg | Used kg | Source details |
|---|---|---|---|
| Sn-containing powder blend / pellets | Not verified / 확인 못 함 | 0.00375 | Source uses 3.750 g of a blend prepared from 20.000 g SB and 0.3297 g tin oxalate; recovered blend mass unreported. |
| Sn/Al2O3 pellets / final batch | Not verified / 확인 못 함 | 0.003 | Source impregnates3.0000 g recovered pellets; total pellet recovery is unreported. |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Prepare Sn-containing powder blend | Boehmite SB powder | 20 g |  |
| Prepare Sn-containing powder blend | Tin(II) oxalate | 0.3297 g |  |
| Prepare pellet bath | CaCl2 | 4 g |  |
| Prepare pellet bath | Water for bath | 400 mL |  |
| Prepare pellet bath | HCl for pH adjustment | Not verified / 확인 못 함 |  |
| Prepare pellet slurry | Water for slurry | 10 mL |  |
| Prepare pellet slurry | Sodium alginate | 0.09 g |  |
| Wash pellets | Wash water | Not verified / 확인 못 함 |  |
| Impregnate Pt | H2PtCl6 solution,30mmol/L | 3.3 mL |  |

These are laboratory pellets; the preparation does not validate an Oleflex industrial formulation. Two sequential aliquots require recovered blend and pellet masses. The summed precursor input is not used as a measured yield. Water/KOH post-treatment variants and reaction testing are outside this selected specimen boundary. Recovered dry output, operating power, attended labor and prices are not established by these preparation sections; this is not a cost-complete protocol.

### S46. PtSn/Al2O3 pellets-0.4CA

Record: `ptsn-alumina-04ca-2024`. Boundary: catalyst_powder.

Source: [The Acid Roles of PtSn@Al2O3 in the Synthesis and Performance of Propane Dehydrogenation](https://doi.org/10.3390/molecules29132959). [DOI 10.3390/molecules29132959](https://doi.org/10.3390/molecules29132959). Locator: Section4.1 Synthesis of Catalysts: Sn/Al2O3 pellets and PtSn/Al2O3(-CA). Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare Sn-containing powder blend | Intermediate batch: blend | 20.000 g boehmite plus 0.3297 g SnC2O4. Input total is not measured recovered blend mass. |
| Prepare pellet bath | Intermediate batch: pellets | Add HCl until pH 2. |
| Prepare pellet slurry | 2 h; Intermediate batch: pellets | Use 3.750 g of the preceding blend; internally transferred, not repurchased. |
| Form and react pellets | 0.5 h; Intermediate batch: pellets | Drip slurry from a syringe into the bath; dripping time is additional and unreported. |
| Wash pellets | Intermediate batch: pellets | Three water washes; per-wash duration and volume unreported. |
| Dry pellets | air; Intermediate batch: pellets | Ambient air until dry; temperature and duration unreported. |
| Calcine pellets | 110 °C; hold 0.5 h; ramp unreported °C/min; 350 °C; hold 0.5 h; ramp 4 °C/min; 560 °C; hold 4 h; ramp 1.75 °C/min; Intermediate batch: pellets | Source ramp durations: room temperature to 110 °C in 30 min; 110 to 350 °C in 60 min; 350 to 560 °C in 120 min. First ramp rate cannot be inferred without starting temperature. Later rates are exact endpoint/time conversions. |
| Impregnate Pt | 3 h | Use 3.0000 g recovered pellets. Precursor solution is 30 mmol/L; no independent solution-density conversion. |
| Dry impregnated pellets | 110 °C; hold unreported h; ramp unreported °C/min | Overnight duration unreported. |
| Calcine Pt-containing pellets | 400 °C; hold 2 h; ramp unreported °C/min |  |

Intermediate transfers (recovery is not inferred from precursor inputs):

| Intermediate / destination | Recovered kg | Used kg | Source details |
|---|---|---|---|
| Sn-containing powder blend / pellets | Not verified / 확인 못 함 | 0.00375 | Source uses 3.750 g of a blend prepared from 20.000 g SB and 0.3297 g tin oxalate; recovered blend mass unreported. |
| Sn/Al2O3 pellets / final batch | Not verified / 확인 못 함 | 0.003 | Source impregnates3.0000 g recovered pellets; total pellet recovery is unreported. |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Prepare Sn-containing powder blend | Boehmite SB powder | 20 g |  |
| Prepare Sn-containing powder blend | Tin(II) oxalate | 0.3297 g |  |
| Prepare pellet bath | CaCl2 | 4 g |  |
| Prepare pellet bath | Water for bath | 400 mL |  |
| Prepare pellet bath | HCl for pH adjustment | Not verified / 확인 못 함 |  |
| Prepare pellet slurry | Water for slurry | 10 mL |  |
| Prepare pellet slurry | Sodium alginate | 0.09 g |  |
| Wash pellets | Wash water | Not verified / 확인 못 함 |  |
| Impregnate Pt | H2PtCl6 solution,30mmol/L | 3.3 mL |  |
| Impregnate Pt | Citric acid monohydrate | 0.168 g |  |

These are laboratory pellets; the preparation does not validate an Oleflex industrial formulation. Two sequential aliquots require recovered blend and pellet masses. The summed precursor input is not used as a measured yield. Water/KOH post-treatment variants and reaction testing are outside this selected specimen boundary. Recovered dry output, operating power, attended labor and prices are not established by these preparation sections; this is not a cost-complete protocol.

### S47. PtSn/Al2O3 pellets-0.8CA

Record: `ptsn-alumina-08ca-2024`. Boundary: catalyst_powder.

Source: [The Acid Roles of PtSn@Al2O3 in the Synthesis and Performance of Propane Dehydrogenation](https://doi.org/10.3390/molecules29132959). [DOI 10.3390/molecules29132959](https://doi.org/10.3390/molecules29132959). Locator: Section4.1 Synthesis of Catalysts: Sn/Al2O3 pellets and PtSn/Al2O3(-CA). Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare Sn-containing powder blend | Intermediate batch: blend | 20.000 g boehmite plus 0.3297 g SnC2O4. Input total is not measured recovered blend mass. |
| Prepare pellet bath | Intermediate batch: pellets | Add HCl until pH 2. |
| Prepare pellet slurry | 2 h; Intermediate batch: pellets | Use 3.750 g of the preceding blend; internally transferred, not repurchased. |
| Form and react pellets | 0.5 h; Intermediate batch: pellets | Drip slurry from a syringe into the bath; dripping time is additional and unreported. |
| Wash pellets | Intermediate batch: pellets | Three water washes; per-wash duration and volume unreported. |
| Dry pellets | air; Intermediate batch: pellets | Ambient air until dry; temperature and duration unreported. |
| Calcine pellets | 110 °C; hold 0.5 h; ramp unreported °C/min; 350 °C; hold 0.5 h; ramp 4 °C/min; 560 °C; hold 4 h; ramp 1.75 °C/min; Intermediate batch: pellets | Source ramp durations: room temperature to 110 °C in 30 min; 110 to 350 °C in 60 min; 350 to 560 °C in 120 min. First ramp rate cannot be inferred without starting temperature. Later rates are exact endpoint/time conversions. |
| Impregnate Pt | 3 h | Use 3.0000 g recovered pellets. Precursor solution is 30 mmol/L; no independent solution-density conversion. |
| Dry impregnated pellets | 110 °C; hold unreported h; ramp unreported °C/min | Overnight duration unreported. |
| Calcine Pt-containing pellets | 400 °C; hold 2 h; ramp unreported °C/min |  |

Intermediate transfers (recovery is not inferred from precursor inputs):

| Intermediate / destination | Recovered kg | Used kg | Source details |
|---|---|---|---|
| Sn-containing powder blend / pellets | Not verified / 확인 못 함 | 0.00375 | Source uses 3.750 g of a blend prepared from 20.000 g SB and 0.3297 g tin oxalate; recovered blend mass unreported. |
| Sn/Al2O3 pellets / final batch | Not verified / 확인 못 함 | 0.003 | Source impregnates3.0000 g recovered pellets; total pellet recovery is unreported. |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Prepare Sn-containing powder blend | Boehmite SB powder | 20 g |  |
| Prepare Sn-containing powder blend | Tin(II) oxalate | 0.3297 g |  |
| Prepare pellet bath | CaCl2 | 4 g |  |
| Prepare pellet bath | Water for bath | 400 mL |  |
| Prepare pellet bath | HCl for pH adjustment | Not verified / 확인 못 함 |  |
| Prepare pellet slurry | Water for slurry | 10 mL |  |
| Prepare pellet slurry | Sodium alginate | 0.09 g |  |
| Wash pellets | Wash water | Not verified / 확인 못 함 |  |
| Impregnate Pt | H2PtCl6 solution,30mmol/L | 3.3 mL |  |
| Impregnate Pt | Citric acid monohydrate | 0.336 g |  |

These are laboratory pellets; the preparation does not validate an Oleflex industrial formulation. Two sequential aliquots require recovered blend and pellet masses. The summed precursor input is not used as a measured yield. Water/KOH post-treatment variants and reaction testing are outside this selected specimen boundary. Recovered dry output, operating power, attended labor and prices are not established by these preparation sections; this is not a cost-complete protocol.

### S48. PtSn/Al2O3 pellets-1.2CA

Record: `ptsn-alumina-12ca-2024`. Boundary: catalyst_powder.

Source: [The Acid Roles of PtSn@Al2O3 in the Synthesis and Performance of Propane Dehydrogenation](https://doi.org/10.3390/molecules29132959). [DOI 10.3390/molecules29132959](https://doi.org/10.3390/molecules29132959). Locator: Section4.1 Synthesis of Catalysts: Sn/Al2O3 pellets and PtSn/Al2O3(-CA). Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare Sn-containing powder blend | Intermediate batch: blend | 20.000 g boehmite plus 0.3297 g SnC2O4. Input total is not measured recovered blend mass. |
| Prepare pellet bath | Intermediate batch: pellets | Add HCl until pH 2. |
| Prepare pellet slurry | 2 h; Intermediate batch: pellets | Use 3.750 g of the preceding blend; internally transferred, not repurchased. |
| Form and react pellets | 0.5 h; Intermediate batch: pellets | Drip slurry from a syringe into the bath; dripping time is additional and unreported. |
| Wash pellets | Intermediate batch: pellets | Three water washes; per-wash duration and volume unreported. |
| Dry pellets | air; Intermediate batch: pellets | Ambient air until dry; temperature and duration unreported. |
| Calcine pellets | 110 °C; hold 0.5 h; ramp unreported °C/min; 350 °C; hold 0.5 h; ramp 4 °C/min; 560 °C; hold 4 h; ramp 1.75 °C/min; Intermediate batch: pellets | Source ramp durations: room temperature to 110 °C in 30 min; 110 to 350 °C in 60 min; 350 to 560 °C in 120 min. First ramp rate cannot be inferred without starting temperature. Later rates are exact endpoint/time conversions. |
| Impregnate Pt | 3 h | Use 3.0000 g recovered pellets. Precursor solution is 30 mmol/L; no independent solution-density conversion. |
| Dry impregnated pellets | 110 °C; hold unreported h; ramp unreported °C/min | Overnight duration unreported. |
| Calcine Pt-containing pellets | 400 °C; hold 2 h; ramp unreported °C/min |  |

Intermediate transfers (recovery is not inferred from precursor inputs):

| Intermediate / destination | Recovered kg | Used kg | Source details |
|---|---|---|---|
| Sn-containing powder blend / pellets | Not verified / 확인 못 함 | 0.00375 | Source uses 3.750 g of a blend prepared from 20.000 g SB and 0.3297 g tin oxalate; recovered blend mass unreported. |
| Sn/Al2O3 pellets / final batch | Not verified / 확인 못 함 | 0.003 | Source impregnates3.0000 g recovered pellets; total pellet recovery is unreported. |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Prepare Sn-containing powder blend | Boehmite SB powder | 20 g |  |
| Prepare Sn-containing powder blend | Tin(II) oxalate | 0.3297 g |  |
| Prepare pellet bath | CaCl2 | 4 g |  |
| Prepare pellet bath | Water for bath | 400 mL |  |
| Prepare pellet bath | HCl for pH adjustment | Not verified / 확인 못 함 |  |
| Prepare pellet slurry | Water for slurry | 10 mL |  |
| Prepare pellet slurry | Sodium alginate | 0.09 g |  |
| Wash pellets | Wash water | Not verified / 확인 못 함 |  |
| Impregnate Pt | H2PtCl6 solution,30mmol/L | 3.3 mL |  |
| Impregnate Pt | Citric acid monohydrate | 0.504 g |  |

These are laboratory pellets; the preparation does not validate an Oleflex industrial formulation. Two sequential aliquots require recovered blend and pellet masses. The summed precursor input is not used as a measured yield. Water/KOH post-treatment variants and reaction testing are outside this selected specimen boundary. Recovered dry output, operating power, attended labor and prices are not established by these preparation sections; this is not a cost-complete protocol.

### S49. Ba/Ru-N-MC; nitrogen-doped mesoporous carbon

Record: `ba-ru-nmc-2019`. Boundary: catalyst_powder.

Source: [Effect of nitrogen co-doping with ruthenium on the catalytic performance of Ba/Ru–N-MC catalysts for ammonia synthesis](https://doi.org/10.1039/c9ra03097b). [DOI 10.1039/c9ra03097b](https://doi.org/10.1039/c9ra03097b). Locator: Experimental: catalyst preparation (Ru-N-MC and Ba/Ru-N-MC). Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Load Ru into silica template | 100 °C; hold 3 h; ramp unreported °C/min; Intermediate batch: ru-nmc |  |
| Introduce carbon and nitrogen precursors | Intermediate batch: ru-nmc |  |
| First carbon precursor treatment | 100 °C; hold 6 h; ramp unreported °C/min; Intermediate batch: ru-nmc |  |
| Second carbon precursor treatment | 160 °C; hold 6 h; ramp unreported °C/min; Intermediate batch: ru-nmc |  |
| Carbonize | 850 °C; hold 3 h; ramp 3 °C/min; N2; Intermediate batch: ru-nmc |  |
| Remove silica template | 70 °C; hold unreported h; ramp unreported °C/min; Intermediate batch: ru-nmc | NaOH wash at 70 °C; concentration, duration and complete rinse/recovery details not quantified here. |
| Ba impregnation | 12 h | Use 1 g Ru-N-MC; nominal Ba 4 wt% on carbon basis. |
| Dry after Ba impregnation | 110 °C; hold 12 h; ramp unreported °C/min |  |
| Reduce | 400 °C; hold 4 h; ramp unreported °C/min; H2 |  |

Intermediate transfers (recovery is not inferred from precursor inputs):

| Intermediate / destination | Recovered kg | Used kg | Source details |
|---|---|---|---|
| Ru-N-MC intermediate / final batch | Not verified / 확인 못 함 | 0.001 |  |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Load Ru into silica template | RuCl3 hydrate | 0.6 g |  |
| Load Ru into silica template | Water | 17 mL |  |
| Load Ru into silica template | SiO2 template | 6 g |  |
| Introduce carbon and nitrogen precursors | Sucrose | 7.5 g |  |
| Introduce carbon and nitrogen precursors | Urea | 0.66 g |  |
| Introduce carbon and nitrogen precursors | Oxalic acid | 0.6 g |  |
| Introduce carbon and nitrogen precursors | Water | 8 mL |  |
| Remove silica template | NaOH solution | Not verified / 확인 못 함 |  |
| Ba impregnation | Ba(NO3)2 | 0.076 g |  |
| Ba impregnation | Water | 5 mL |  |

Ru-N-MC synthesis and subsequent 1 g aliquot have separate batch boundaries. The mesoporous nitrogen-doped support is not the graphite used in the catalog KAAP-style proxy. High-pressure catalytic activation tests are not included in manufacture. The source reports different Ru contents for distinct loading sequences; Ba-Ru/N-MC is not the same preparation. Recovered dry output, operating power, attended labor and prices are not established by these preparation sections; this is not a cost-complete protocol.

### S50. W-12 fused wustite precursor

Record: `fused-wustite-w-12-2022`. Boundary: catalyst_powder.

Source: [Influence of Magnesium Oxide on the Structure and Catalytic Activity of the Wustite Catalyst for Ammonia Synthesis](https://doi.org/10.3390/ma15238309). [DOI 10.3390/ma15238309](https://doi.org/10.3390/ma15238309). Locator: Section2.1 Preparation of Catalyst Precursors; Table1. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Mix oxide promoters and iron sources | Not quantified | Magnetite, aluminum/calcium/magnesium oxides, KNO3 and metallic Fe. Exact charge masses not reported. Product analysis: Al2O3 2.25%, CaO 1.74%, K2O 0.43%, MgO 0%; Fe2+/Fe3+=5.21 |
| Fuse precursor | 0.833333 h | Source specifies 2000 A for 50 min; voltage, power factor and actual electrical input are unreported. |
| Cast and cool | Not quantified | Pour into a water-cooled mold; cooling duration and utility demand unreported. |
| Crush and sieve | Not quantified | Retain 1–1.2 mm granules; recovered amount and energy unreported. |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Mix oxide promoters and iron sources | Magnetite | Not verified / 확인 못 함 |  |
| Mix oxide promoters and iron sources | Al2O3 | Not verified / 확인 못 함 |  |
| Mix oxide promoters and iron sources | CaO | Not verified / 확인 못 함 |  |
| Mix oxide promoters and iron sources | KNO3 | Not verified / 확인 못 함 |  |
| Mix oxide promoters and iron sources | Metallic Fe | Not verified / 확인 못 함 |  |

This record ends at oxidic precursor granules. Catalytic reduction/activation and reactor testing require a separately declared product boundary. Reported current cannot be substituted for kW or kWh. Table 1 oxide analysis is not a precursor purchasing recipe. Recovered dry output, operating power, attended labor and prices are not established by these preparation sections; this is not a cost-complete protocol.

### S51. W-22 fused wustite precursor

Record: `fused-wustite-w-22-2022`. Boundary: catalyst_powder.

Source: [Influence of Magnesium Oxide on the Structure and Catalytic Activity of the Wustite Catalyst for Ammonia Synthesis](https://doi.org/10.3390/ma15238309). [DOI 10.3390/ma15238309](https://doi.org/10.3390/ma15238309). Locator: Section2.1 Preparation of Catalyst Precursors; Table1. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Mix oxide promoters and iron sources | Not quantified | Magnetite, aluminum/calcium/magnesium oxides, KNO3 and metallic Fe. Exact charge masses not reported. Product analysis: Al2O3 1.80%, CaO 1.75%, K2O 0.37%, MgO 1.15%; Fe2+/Fe3+=9.46 |
| Fuse precursor | 0.833333 h | Source specifies 2000 A for 50 min; voltage, power factor and actual electrical input are unreported. |
| Cast and cool | Not quantified | Pour into a water-cooled mold; cooling duration and utility demand unreported. |
| Crush and sieve | Not quantified | Retain 1–1.2 mm granules; recovered amount and energy unreported. |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Mix oxide promoters and iron sources | Magnetite | Not verified / 확인 못 함 |  |
| Mix oxide promoters and iron sources | Al2O3 | Not verified / 확인 못 함 |  |
| Mix oxide promoters and iron sources | CaO | Not verified / 확인 못 함 |  |
| Mix oxide promoters and iron sources | KNO3 | Not verified / 확인 못 함 |  |
| Mix oxide promoters and iron sources | Metallic Fe | Not verified / 확인 못 함 |  |
| Mix oxide promoters and iron sources | MgO | Not verified / 확인 못 함 |  |

This record ends at oxidic precursor granules. Catalytic reduction/activation and reactor testing require a separately declared product boundary. Reported current cannot be substituted for kW or kWh. Table 1 oxide analysis is not a precursor purchasing recipe. Recovered dry output, operating power, attended labor and prices are not established by these preparation sections; this is not a cost-complete protocol.

### S52. Pt/C by polyol method; nominal20wt%metal

Record: `pt-carbon-polyol-2023`. Boundary: catalyst_powder.

Source: [Glycerol Electro-Oxidation in Alkaline Medium with Pt-Fe/C Electrocatalysts Synthesized by the Polyol Method: Increased Selectivity and Activity Provided by Less Expensive Catalysts](https://doi.org/10.3390/nano13071173). [DOI 10.3390/nano13071173](https://doi.org/10.3390/nano13071173). Locator: Section2.1 Electrocatalyst Synthesis. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Activate carbon support | 400 °C; hold unreported h; ramp unreported °C/min; N2; Intermediate batch: carbon | 400 °C under N2; duration unreported. Source subsequently uses 160 mg activated carbon; original carbon charge/recovery unreported. |
| Dissolve base in ethylene glycol | 0.5 h | Ultrasound 30 min; pH 13. |
| Dissolve metal precursors | Not quantified | Ultrasound for over 30 min, a lower bound; exact duration remains unknown. |
| Reflux under nitrogen | 130 °C; hold 4.5 h; ramp unreported °C/min; N2 |  |
| Cool and add carbon | Not quantified | Cool to room temperature; use 160 mg activated carbon as an internal transfer. |
| Sonicate carbon suspension | 0.5 h |  |
| Adsorb particles on carbon | 24 h |  |
| Filter and wash | Not quantified | 0.2 micrometre PTFE membrane; water 1 L and two 10 mL ethanol portions. |
| Dry on membrane | 80 °C; hold 4 h; ramp unreported °C/min |  |
| Recover catalyst | Not quantified | Remove catalyst from membrane; recovered dry mass not reported. |

Intermediate transfers (recovery is not inferred from precursor inputs):

| Intermediate / destination | Recovered kg | Used kg | Source details |
|---|---|---|---|
| Activated Vulcan carbon / final batch | Not verified / 확인 못 함 | 0.00016 |  |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Activate carbon support | Vulcan carbon | Not verified / 확인 못 함 |  |
| Dissolve base in ethylene glycol | Ethylene glycol | 100 mL |  |
| Dissolve base in ethylene glycol | NaOH | 0.4 g |  |
| Dissolve metal precursors | H2PtCl6·6H2O | 0.1063 g |  |
| Filter and wash | Water for washing | 1 L |  |
| Filter and wash | Ethanol for washing | 20 mL |  |
| Filter and wash | PTFE filter membrane | Not verified / 확인 못 함 |  |

The stated 200 mg synthesis target is not measured recovered catalyst mass. The hydrazine variant is excluded. Particle preparation is distinct from electrode ink and assembly. Recovered dry output, operating power, attended labor and prices are not established by these preparation sections; this is not a cost-complete protocol.

### S53. Pt50Fe50/C by polyol method

Record: `ptfe-carbon-polyol-2023`. Boundary: catalyst_powder.

Source: [Glycerol Electro-Oxidation in Alkaline Medium with Pt-Fe/C Electrocatalysts Synthesized by the Polyol Method: Increased Selectivity and Activity Provided by Less Expensive Catalysts](https://doi.org/10.3390/nano13071173). [DOI 10.3390/nano13071173](https://doi.org/10.3390/nano13071173). Locator: Section2.1 Electrocatalyst Synthesis. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Activate carbon support | 400 °C; hold unreported h; ramp unreported °C/min; N2; Intermediate batch: carbon | 400 °C under N2; duration unreported. Source subsequently uses 160 mg activated carbon; original carbon charge/recovery unreported. |
| Dissolve base in ethylene glycol | 0.5 h | Ultrasound 30 min; pH 13. |
| Dissolve metal precursors | Not quantified | Ultrasound for over 30 min, a lower bound; exact duration remains unknown. |
| Reflux under nitrogen | 130 °C; hold 4.5 h; ramp unreported °C/min; N2 |  |
| Cool and add carbon | Not quantified | Cool to room temperature; use 160 mg activated carbon as an internal transfer. |
| Sonicate carbon suspension | 0.5 h |  |
| Adsorb particles on carbon | 24 h |  |
| Filter and wash | Not quantified | 0.2 micrometre PTFE membrane; water 1 L and two 10 mL ethanol portions. |
| Dry on membrane | 80 °C; hold 4 h; ramp unreported °C/min |  |
| Recover catalyst | Not quantified | Remove catalyst from membrane; recovered dry mass not reported. |

Intermediate transfers (recovery is not inferred from precursor inputs):

| Intermediate / destination | Recovered kg | Used kg | Source details |
|---|---|---|---|
| Activated Vulcan carbon / final batch | Not verified / 확인 못 함 | 0.00016 |  |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Activate carbon support | Vulcan carbon | Not verified / 확인 못 함 |  |
| Dissolve base in ethylene glycol | Ethylene glycol | 100 mL |  |
| Dissolve base in ethylene glycol | NaOH | 0.4 g |  |
| Dissolve metal precursors | H2PtCl6·6H2O | 0.08 g |  |
| Dissolve metal precursors | FeCl2·4H2O | 0.0319 g |  |
| Filter and wash | Water for washing | 1 L |  |
| Filter and wash | Ethanol for washing | 20 mL |  |
| Filter and wash | PTFE filter membrane | Not verified / 확인 못 함 |  |

The stated 200 mg synthesis target is not measured recovered catalyst mass. The hydrazine variant is excluded. Particle preparation is distinct from electrode ink and assembly. Recovered dry output, operating power, attended labor and prices are not established by these preparation sections; this is not a cost-complete protocol.

### S54. Ru/NC-M from melamine

Record: `ru-nc-melamine-2023`. Boundary: catalyst_powder.

Source: [Preparation of Ru/N-doped carbon catalysts by induction of different nitrogen source precursors for the hydroprocessing of lignin oil](https://doi.org/10.1039/d3ra01866k). [DOI 10.1039/d3ra01866k](https://doi.org/10.1039/d3ra01866k). Locator: Experimental: Preparation of catalysts. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Grind Ru and nitrogen source | Not quantified | Use the melamine variant. |
| Thermal preparation of nitrogen-rich carbon | 2 h | Source lists 500, 600 and 650 °C for the preparation series without an unambiguous single specimen temperature in this paragraph; select the specimen before assigning a temperature. |
| Hydrogen treatment | 300 °C; hold 2 h; ramp 5 °C/min; H2 |  |
| Cool | Not quantified | Room-temperature endpoint; duration unreported. |
| Passivate | 2 h; 1% O2/N2 |  |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Grind Ru and nitrogen source | RuCl3 hydrate | 0.05 g |  |
| Grind Ru and nitrogen source | Melamine | 5 g |  |

Melamine-derived nitrogen-rich carbon is not equivalent to a generic Ru/activated-carbon formulation. The first treatment temperature remains unresolved for this selected named specimen; the three temperatures are not a sequential heating program. Recovered dry output, operating power, attended labor and prices are not established by these preparation sections; this is not a cost-complete protocol.

### S55. AC-1023 from untreated Datong coal

Record: `coal-ac-1023-2020`. Boundary: catalyst_powder.

Source: [Effect of Thermal Extraction on Coal-Based Activated Carbon for Methane Decomposition to Hydrogen](https://doi.org/10.1021/acsomega.9b04044). [DOI 10.1021/acsomega.9b04044](https://doi.org/10.1021/acsomega.9b04044). Locator: Sections2.1 Preparation and Thermal Solution of Coal Samples;2.2 Preparation of AC. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Crush and sieve coal | Not quantified | Datong coal; particle size below 0.5 mm. |
| Vacuum dry coal | 109.85 °C; hold 2 h; ramp unreported °C/min; vacuum |  |
| Mix with activator | 24 h | DT/KOH mixture described with 4:1 mass ratio; order of numerator/denominator is not resolved here. Water and ethanol amounts unreported. |
| Carbonize and activate | 199.85 °C; hold 1 h; ramp 5 °C/min; 749.85 °C; hold 2 h; ramp 5 °C/min; N2 | 298 K to 473 K in 35 min corresponds to 5 K/min; then 1023 K at 5 K/min. Nitrogen 200 mL/min, reference state unreported. |
| Cool | N2 | To room temperature under 50 mL/min N2; duration unreported. |
| Acid wash | Not quantified | Source gives 24 h soaking in 3 M HCl and 6 h magnetic mixing; whether mixing is included in the 24 h is unresolved, so these are not added as 30 h. |
| Rinse and filter | Not quantified | Water until neutral; volume and time unreported. |
| Dry activated carbon | 149.85 °C; hold 2 h; ramp unreported °C/min |  |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Crush and sieve coal | Datong coal | Not verified / 확인 못 함 |  |
| Mix with activator | KOH | Not verified / 확인 못 함 |  |
| Mix with activator | Water | Not verified / 확인 못 함 |  |
| Mix with activator | Ethanol | Not verified / 확인 못 함 |  |
| Acid wash | HCl solution,3M | Not verified / 확인 못 함 |  |
| Rinse and filter | Rinse water | Not verified / 확인 못 함 |  |

AC-1023 uses raw DT; the benzene-extracted RR route designated AC-1023-1 is excluded. KOH ratio orientation and acid-treatment elapsed time remain unresolved. Celsius values are exact conversions from source Kelvin values. Recovered dry output, operating power, attended labor and prices are not established by these preparation sections; this is not a cost-complete protocol.

### S56. NiCu/MS(500); nominal50wt%Ni and5wt%Cu

Record: `nicu-ms-500-2022`. Boundary: catalyst_powder.

Source: [Effect of Calcination Temperature on Cu-Modified Ni Catalysts Supported on Mesocellular Silica for Methane Decomposition](https://doi.org/10.1021/acsomega.2c01016). [DOI 10.1021/acsomega.2c01016](https://doi.org/10.1021/acsomega.2c01016). Locator: Section4.1 Catalyst Preparation. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare silica sol | Intermediate batch: ms | P123 in water; add 37 wt% HCl and TMB at 40 °C. TMB:P123 mass ratio 2:1. Quantities unreported. |
| Age silica sol | 40 °C; hold 24 h; ramp unreported °C/min; Intermediate batch: ms |  |
| Hydrothermal synthesis | 100 °C; hold 24 h; ramp unreported °C/min; Intermediate batch: ms |  |
| Filter and wash support | Intermediate batch: ms | Water wash; volume unreported. |
| Dry support | 100 °C; hold unreported h; ramp unreported °C/min; Intermediate batch: ms | Overnight duration unreported. |
| Calcine support | 550 °C; hold 6 h; ramp unreported °C/min; air; Intermediate batch: ms |  |
| Co-impregnate Ni and Cu | 1 h | Metal solution added to MS at room temperature; exact support portion and precursor charges unreported. |
| Microwave dry | 0.0166667 h | 800 W oven setting for 1 min; this is not measured electrical input power. |
| Calcine impregnated catalyst | 500 °C; hold 4 h; ramp unreported °C/min |  |

Intermediate transfers (recovery is not inferred from precursor inputs):

| Intermediate / destination | Recovered kg | Used kg | Source details |
|---|---|---|---|
| Mesocellular silica support / final batch | Not verified / 확인 못 함 | Not verified / 확인 못 함 |  |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Prepare silica sol | P123 | Not verified / 확인 못 함 |  |
| Prepare silica sol | Water | Not verified / 확인 못 함 |  |
| Prepare silica sol | HCl solution,37wt% | Not verified / 확인 못 함 |  |
| Prepare silica sol | 1,3,5-Trimethylbenzene | Not verified / 확인 못 함 |  |
| Prepare silica sol | Sodium silicate solution,29.45%SiO2 | Not verified / 확인 못 함 |  |
| Filter and wash support | Wash water | Not verified / 확인 못 함 |  |
| Co-impregnate Ni and Cu | Ni(NO3)2·6H2O | Not verified / 확인 못 함 |  |
| Co-impregnate Ni and Cu | Cu(NO3)2·3H2O | Not verified / 확인 못 함 |  |
| Co-impregnate Ni and Cu | Water for impregnation | Not verified / 확인 못 함 |  |

The Cu-promoted mesocellular silica specimen is distinct from the catalog Ni/SiO2 baseline. A portion of a separate MS preparation is used; recovered support output and transferred mass are unreported. The microwave setting is retained as equipment information and is not imported as average_power_kw. Recovered dry output, operating power, attended labor and prices are not established by these preparation sections; this is not a cost-complete protocol.

### S57. NiCu/MS(600); nominal50wt%Ni and5wt%Cu

Record: `nicu-ms-600-2022`. Boundary: catalyst_powder.

Source: [Effect of Calcination Temperature on Cu-Modified Ni Catalysts Supported on Mesocellular Silica for Methane Decomposition](https://doi.org/10.1021/acsomega.2c01016). [DOI 10.1021/acsomega.2c01016](https://doi.org/10.1021/acsomega.2c01016). Locator: Section4.1 Catalyst Preparation. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare silica sol | Intermediate batch: ms | P123 in water; add 37 wt% HCl and TMB at 40 °C. TMB:P123 mass ratio 2:1. Quantities unreported. |
| Age silica sol | 40 °C; hold 24 h; ramp unreported °C/min; Intermediate batch: ms |  |
| Hydrothermal synthesis | 100 °C; hold 24 h; ramp unreported °C/min; Intermediate batch: ms |  |
| Filter and wash support | Intermediate batch: ms | Water wash; volume unreported. |
| Dry support | 100 °C; hold unreported h; ramp unreported °C/min; Intermediate batch: ms | Overnight duration unreported. |
| Calcine support | 550 °C; hold 6 h; ramp unreported °C/min; air; Intermediate batch: ms |  |
| Co-impregnate Ni and Cu | 1 h | Metal solution added to MS at room temperature; exact support portion and precursor charges unreported. |
| Microwave dry | 0.0166667 h | 800 W oven setting for 1 min; this is not measured electrical input power. |
| Calcine impregnated catalyst | 600 °C; hold 4 h; ramp unreported °C/min |  |

Intermediate transfers (recovery is not inferred from precursor inputs):

| Intermediate / destination | Recovered kg | Used kg | Source details |
|---|---|---|---|
| Mesocellular silica support / final batch | Not verified / 확인 못 함 | Not verified / 확인 못 함 |  |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Prepare silica sol | P123 | Not verified / 확인 못 함 |  |
| Prepare silica sol | Water | Not verified / 확인 못 함 |  |
| Prepare silica sol | HCl solution,37wt% | Not verified / 확인 못 함 |  |
| Prepare silica sol | 1,3,5-Trimethylbenzene | Not verified / 확인 못 함 |  |
| Prepare silica sol | Sodium silicate solution,29.45%SiO2 | Not verified / 확인 못 함 |  |
| Filter and wash support | Wash water | Not verified / 확인 못 함 |  |
| Co-impregnate Ni and Cu | Ni(NO3)2·6H2O | Not verified / 확인 못 함 |  |
| Co-impregnate Ni and Cu | Cu(NO3)2·3H2O | Not verified / 확인 못 함 |  |
| Co-impregnate Ni and Cu | Water for impregnation | Not verified / 확인 못 함 |  |

The Cu-promoted mesocellular silica specimen is distinct from the catalog Ni/SiO2 baseline. A portion of a separate MS preparation is used; recovered support output and transferred mass are unreported. The microwave setting is retained as equipment information and is not imported as average_power_kw. Recovered dry output, operating power, attended labor and prices are not established by these preparation sections; this is not a cost-complete protocol.

### S58. NiCu/MS(700); nominal50wt%Ni and5wt%Cu

Record: `nicu-ms-700-2022`. Boundary: catalyst_powder.

Source: [Effect of Calcination Temperature on Cu-Modified Ni Catalysts Supported on Mesocellular Silica for Methane Decomposition](https://doi.org/10.1021/acsomega.2c01016). [DOI 10.1021/acsomega.2c01016](https://doi.org/10.1021/acsomega.2c01016). Locator: Section4.1 Catalyst Preparation. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare silica sol | Intermediate batch: ms | P123 in water; add 37 wt% HCl and TMB at 40 °C. TMB:P123 mass ratio 2:1. Quantities unreported. |
| Age silica sol | 40 °C; hold 24 h; ramp unreported °C/min; Intermediate batch: ms |  |
| Hydrothermal synthesis | 100 °C; hold 24 h; ramp unreported °C/min; Intermediate batch: ms |  |
| Filter and wash support | Intermediate batch: ms | Water wash; volume unreported. |
| Dry support | 100 °C; hold unreported h; ramp unreported °C/min; Intermediate batch: ms | Overnight duration unreported. |
| Calcine support | 550 °C; hold 6 h; ramp unreported °C/min; air; Intermediate batch: ms |  |
| Co-impregnate Ni and Cu | 1 h | Metal solution added to MS at room temperature; exact support portion and precursor charges unreported. |
| Microwave dry | 0.0166667 h | 800 W oven setting for 1 min; this is not measured electrical input power. |
| Calcine impregnated catalyst | 700 °C; hold 4 h; ramp unreported °C/min |  |

Intermediate transfers (recovery is not inferred from precursor inputs):

| Intermediate / destination | Recovered kg | Used kg | Source details |
|---|---|---|---|
| Mesocellular silica support / final batch | Not verified / 확인 못 함 | Not verified / 확인 못 함 |  |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Prepare silica sol | P123 | Not verified / 확인 못 함 |  |
| Prepare silica sol | Water | Not verified / 확인 못 함 |  |
| Prepare silica sol | HCl solution,37wt% | Not verified / 확인 못 함 |  |
| Prepare silica sol | 1,3,5-Trimethylbenzene | Not verified / 확인 못 함 |  |
| Prepare silica sol | Sodium silicate solution,29.45%SiO2 | Not verified / 확인 못 함 |  |
| Filter and wash support | Wash water | Not verified / 확인 못 함 |  |
| Co-impregnate Ni and Cu | Ni(NO3)2·6H2O | Not verified / 확인 못 함 |  |
| Co-impregnate Ni and Cu | Cu(NO3)2·3H2O | Not verified / 확인 못 함 |  |
| Co-impregnate Ni and Cu | Water for impregnation | Not verified / 확인 못 함 |  |

The Cu-promoted mesocellular silica specimen is distinct from the catalog Ni/SiO2 baseline. A portion of a separate MS preparation is used; recovered support output and transferred mass are unreported. The microwave setting is retained as equipment information and is not imported as average_power_kw. Recovered dry output, operating power, attended labor and prices are not established by these preparation sections; this is not a cost-complete protocol.

### S59. NiCu/MS(800); nominal50wt%Ni and5wt%Cu

Record: `nicu-ms-800-2022`. Boundary: catalyst_powder.

Source: [Effect of Calcination Temperature on Cu-Modified Ni Catalysts Supported on Mesocellular Silica for Methane Decomposition](https://doi.org/10.1021/acsomega.2c01016). [DOI 10.1021/acsomega.2c01016](https://doi.org/10.1021/acsomega.2c01016). Locator: Section4.1 Catalyst Preparation. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare silica sol | Intermediate batch: ms | P123 in water; add 37 wt% HCl and TMB at 40 °C. TMB:P123 mass ratio 2:1. Quantities unreported. |
| Age silica sol | 40 °C; hold 24 h; ramp unreported °C/min; Intermediate batch: ms |  |
| Hydrothermal synthesis | 100 °C; hold 24 h; ramp unreported °C/min; Intermediate batch: ms |  |
| Filter and wash support | Intermediate batch: ms | Water wash; volume unreported. |
| Dry support | 100 °C; hold unreported h; ramp unreported °C/min; Intermediate batch: ms | Overnight duration unreported. |
| Calcine support | 550 °C; hold 6 h; ramp unreported °C/min; air; Intermediate batch: ms |  |
| Co-impregnate Ni and Cu | 1 h | Metal solution added to MS at room temperature; exact support portion and precursor charges unreported. |
| Microwave dry | 0.0166667 h | 800 W oven setting for 1 min; this is not measured electrical input power. |
| Calcine impregnated catalyst | 800 °C; hold 4 h; ramp unreported °C/min |  |

Intermediate transfers (recovery is not inferred from precursor inputs):

| Intermediate / destination | Recovered kg | Used kg | Source details |
|---|---|---|---|
| Mesocellular silica support / final batch | Not verified / 확인 못 함 | Not verified / 확인 못 함 |  |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Prepare silica sol | P123 | Not verified / 확인 못 함 |  |
| Prepare silica sol | Water | Not verified / 확인 못 함 |  |
| Prepare silica sol | HCl solution,37wt% | Not verified / 확인 못 함 |  |
| Prepare silica sol | 1,3,5-Trimethylbenzene | Not verified / 확인 못 함 |  |
| Prepare silica sol | Sodium silicate solution,29.45%SiO2 | Not verified / 확인 못 함 |  |
| Filter and wash support | Wash water | Not verified / 확인 못 함 |  |
| Co-impregnate Ni and Cu | Ni(NO3)2·6H2O | Not verified / 확인 못 함 |  |
| Co-impregnate Ni and Cu | Cu(NO3)2·3H2O | Not verified / 확인 못 함 |  |
| Co-impregnate Ni and Cu | Water for impregnation | Not verified / 확인 못 함 |  |

The Cu-promoted mesocellular silica specimen is distinct from the catalog Ni/SiO2 baseline. A portion of a separate MS preparation is used; recovered support output and transferred mass are unreported. The microwave setting is retained as equipment information and is not imported as average_power_kw. Recovered dry output, operating power, attended labor and prices are not established by these preparation sections; this is not a cost-complete protocol.

### S60. SAPO-34-P (SP), conventional-template reference

Record: `sapo34-sp-2025`. Boundary: catalyst_powder.

Source: [Green synthesis of SAPO-34 via dual bio-templates for enhanced catalytic performance in MTO reaction](https://doi.org/10.1038/s41598-025-14220-8). [DOI 10.1038/s41598-025-14220-8](https://doi.org/10.1038/s41598-025-14220-8). Locator: Experimental and theoretical approach: Materials; Catalyst fabrication. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare Al/template solution | 1 h | AIP, TEAOH, morpholine and water. Molar gel composition 1Al2O3:1P2O5:0.6SiO2:1.25TEAOH:1.25Mor:70H2O; absolute charges unreported. SP excludes okra/coffee templates. |
| Add silicon source | 60 °C; hold 3 h; ramp unreported °C/min |  |
| Add phosphorus source | 60 °C; hold 2 h; ramp unreported °C/min |  |
| Age gel | 24 h | Room temperature not quantified. |
| Hydrothermal crystallization | 180 °C; hold 18 h; ramp unreported °C/min |  |
| Separate crystals | Not quantified | Initial centrifugation; time and rotation speed unreported. |
| Wash crystals | Not quantified | Four water washes; per-wash time and water volume unreported. |
| Dry crystals | 100 °C; hold 12 h; ramp unreported °C/min |  |
| Remove templates by calcination | 550 °C; hold 5 h; ramp unreported °C/min |  |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Prepare Al/template solution | Aluminum isopropoxide,99% | Not verified / 확인 못 함 |  |
| Prepare Al/template solution | TEAOH solution,20wt% | Not verified / 확인 못 함 |  |
| Prepare Al/template solution | Morpholine,99% | Not verified / 확인 못 함 |  |
| Prepare Al/template solution | Water | Not verified / 확인 못 함 |  |
| Add silicon source | Tetraethyl orthosilicate | Not verified / 확인 못 함 |  |
| Add phosphorus source | H3PO4 solution,85wt% | Not verified / 확인 못 함 |  |
| Wash crystals | Wash water | Not verified / 확인 못 함 |  |

SP is the conventional-template reference; the enhanced dual-template SPG specimen has additional okra and coffee preparation steps and is not represented by this record. Gel stoichiometry is not an industrial precursor bill or a measured final composition. Pre-reaction nitrogen pretreatment is outside this as-calcined boundary. Recovered dry output, operating power, attended labor and prices are not established by these preparation sections; this is not a cost-complete protocol.

### S61. FeZ-DR from diatomite and rectorite

Record: `fezsm5-dr-minerals-2015`. Boundary: catalyst_powder.

Source: [One-pot synthesis of hierarchical FeZSM-5 zeolites from natural aluminosilicates for selective catalytic reduction of NO by NH3](https://doi.org/10.1038/srep09270). [DOI 10.1038/srep09270](https://doi.org/10.1038/srep09270). Locator: Methods: Depolymerization of the natural minerals; Synthesis of FeZSM-5 zeolites. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Activate diatomite | 600 °C; hold 4 h; ramp unreported °C/min; air; Intermediate batch: diatomite |  |
| Depolymerize rectorite | 250 °C; hold 2 h; ramp unreported °C/min; air; Intermediate batch: rectorite | Mix rectorite, NaOH and water; open Teflon drum in an air-exposed oven. |
| Mix crystallization gel | Not quantified | Molar composition Al2O3:Fe2O3:SiO2:Na2O:TPABr:H2O=1.1:0.26:40:6:4:1600. Use treated minerals; absolute quantities and portions unreported. |
| Crystallize zeolite | 170 °C; hold 48 h; ramp unreported °C/min | Autogenous pressure; no numeric pressure specified. |
| Filter and wash | Not quantified | Water volume and elapsed time unreported. |
| Dry zeolite | 120 °C; hold unreported h; ramp unreported °C/min | Overnight duration unreported. |
| Remove template | 550 °C; hold 6 h; ramp unreported °C/min; air |  |
| Ammonium exchange | Not quantified | Successive exchanges with 1 M NH4Cl; exchange duration and number of passes unreported. |
| Convert to H form | 520 °C; hold 4 h; ramp unreported °C/min | Source gives 520 °C 4 h calcinations following exchanges; number of repeated exchange/calcination passes unresolved. |

Intermediate transfers (recovery is not inferred from precursor inputs):

| Intermediate / destination | Recovered kg | Used kg | Source details |
|---|---|---|---|
| Activated diatomite / final batch | Not verified / 확인 못 함 | Not verified / 확인 못 함 |  |
| Depolymerized rectorite / final batch | Not verified / 확인 못 함 | Not verified / 확인 못 함 |  |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Activate diatomite | Natural diatomite | Not verified / 확인 못 함 |  |
| Depolymerize rectorite | Natural rectorite | Not verified / 확인 못 함 |  |
| Depolymerize rectorite | NaOH | Not verified / 확인 못 함 |  |
| Depolymerize rectorite | Water | Not verified / 확인 못 함 |  |
| Mix crystallization gel | TPABr | Not verified / 확인 못 함 |  |
| Mix crystallization gel | NaOH for gel | Not verified / 확인 못 함 |  |
| Mix crystallization gel | Water for gel | Not verified / 확인 못 함 |  |
| Filter and wash | Wash water | Not verified / 확인 못 함 |  |
| Ammonium exchange | NH4Cl solution,1M | Not verified / 확인 못 함 |  |

Mineral compositions vary by grade; their Si, Al and Fe contents cannot be replaced by a generic pure oxide formulation. The number and duration of ion-exchange cycles and treated-mineral aliquots must be resolved before complete costing. The He pretreatment for catalytic tests is not included. Recovered dry output, operating power, attended labor and prices are not established by these preparation sections; this is not a cost-complete protocol.

### S62. IrO2 on white-P25 TiO2 by photodeposition

Record: `iro2-white-p25-photo-2024`. Boundary: catalyst_powder.

Source: [IrO2 Oxygen Evolution Catalysts Prepared by an Optimized Photodeposition Process on TiO2 Substrates](https://doi.org/10.3390/molecules29102392). [DOI 10.3390/molecules29102392](https://doi.org/10.3390/molecules29102392). Locator: Section4.1 Synthesis of IrO2 on Various TiO2 Powders: Photodeposition. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare and de-aerate iridium solution | 0.25 h; N2 | 120 mL of 0.002 M K3IrCl6; adjust pH 11 with 1 M KOH. Nitrogen purge 15 min; flow unreported. |
| Add white-P25 and homogenize | 0.333333 h | TiO2 concentration 0.008 M; no independently reported solid charge is inferred from solution concentration. |
| Photodeposit iridium | 8 h | Ambient temperature; UVA 350–400 nm, peak 369 nm. 9 W lamp rating is not measured system electrical input. |
| Vacuum filter and wash | Not quantified | Use distilled water; volume/time unreported. |
| Dry powder | Not quantified | Overnight at room temperature; neither value numerically specified. |
| Grind powder | Not quantified | Agate mortar; time unreported. |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Prepare and de-aerate iridium solution | K3IrCl6 aqueous solution,0.002M | 120 mL |  |
| Prepare and de-aerate iridium solution | KOH solution,1M | Not verified / 확인 못 함 |  |
| Add white-P25 and homogenize | White-P25 TiO2 | Not verified / 확인 못 함 |  |
| Vacuum filter and wash | Distilled wash water | Not verified / 확인 못 함 |  |

This record uses purchased white-P25; black/oxysulfate support fabrication is a different boundary. Approximately 25 wt% Ir is a reported deposition outcome, not exact retained mass or recovered dry output. Electrode assembly is not included. Recovered dry output, operating power, attended labor and prices are not established by these preparation sections; this is not a cost-complete protocol.

### S63. Cr-HM, Cr-doped hematite precursor for high-temperature WGS

Record: `cr-hm-wgs-2022`. Boundary: catalyst_powder.

Source: [Substituting Chromium in Iron-Based Catalysts for the High-Temperature Water–Gas Shift Reaction](https://doi.org/10.1021/acscatal.2c03871). [DOI 10.1021/acscatal.2c03871](https://doi.org/10.1021/acscatal.2c03871). Locator: Catalyst Preparation. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Dissolve metal nitrates | 60 °C; hold unreported h; ramp unreported °C/min | Target Cr/Fe atomic ratio 8.4%; stated equivalence to 8 wt% Cr2O3/alpha-Fe2O3. Precursor charges unreported. |
| Precipitate and age | 60 °C; hold 1 h; ramp unreported °C/min | Add NaOH to pH 10 under vigorous stirring; age at 60 °C 1 h. Addition time is additional and unreported. |
| Filter and wash | Not quantified | Wash volume and time unreported. |
| Dry precursor | 150 °C; hold 3 h; ramp unreported °C/min |  |
| Calcine hematite precursor | 400 °C; hold 4 h; ramp unreported °C/min; static air |  |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Dissolve metal nitrates | Fe(III) nitrate | Not verified / 확인 못 함 |  |
| Dissolve metal nitrates | Cr(III) nitrate | Not verified / 확인 못 함 |  |
| Dissolve metal nitrates | Water | Not verified / 확인 못 함 |  |
| Precipitate and age | NaOH solution | Not verified / 확인 못 함 |  |
| Filter and wash | Wash water | Not verified / 확인 못 함 |  |

The record ends at as-calcined hematite; magnetite activation under WGS conditions is separate. Cu-containing CrCu-HM and alternative dopants are distinct specimens; generic commercial Fe-Cr formulation is not independently validated. Recovered dry output, operating power, attended labor and prices are not established by these preparation sections; this is not a cost-complete protocol.

### S64. 2Ni-R; nominal2wt%Ni on ceria nanorods

Record: `ni-ceria-r-2022`. Boundary: catalyst_powder.

Source: [CO <sub>2</sub> Activation over Nanoshaped CeO <sub>2</sub> Decorated with Nickel for Low-Temperature Methane Dry Reforming](https://doi.org/10.1021/acsami.2c05221). [DOI 10.1021/acsami.2c05221](https://doi.org/10.1021/acsami.2c05221). Locator: Section2.1 Synthesis of Catalysts. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare and mix support solutions | 0.5 h; Intermediate batch: ceria |  |
| Hydrothermal ceria synthesis | 100 °C; hold 24 h; ramp unreported °C/min; Intermediate batch: ceria | Approximately 35 mL is the autoclave capacity, not a reported aliquot volume. Number of vessels and distribution of the combined solution are unreported. |
| Wash and centrifuge | Intermediate batch: ceria | 7500 rpm90 s per centrifugation; repeat with water and finally ethanol until sodium removal. Total wash/cycle count and elapsed time unreported. |
| Freeze-dry ceria | Intermediate batch: ceria | Duration and temperature unreported. |
| Calcine ceria | 500 °C; hold 4 h; ramp 5 °C/min; static air; Intermediate batch: ceria |  |
| Dissolve nickel precursor | 0.25 h |  |
| Add prepared ceria | 0.25 h | Use 1 g of the separately prepared ceria; internal transfer. |
| First pH adjustment and aging | 2 h | Add 2.5 wt% ammonia dropwise to pH 7.5, then stir 2 h; addition time unreported. |
| Second pH adjustment | 0.25 h | Adjust pH 9 with 25 wt% ammonia, then stir 15 min; addition time unreported. |
| Filter and dry | 70 °C; hold unreported h; ramp unreported °C/min | Filtration time and overnight drying duration unreported. |
| Calcine Ni/ceria | 500 °C; hold 4 h; ramp 5 °C/min |  |

Intermediate transfers (recovery is not inferred from precursor inputs):

| Intermediate / destination | Recovered kg | Used kg | Source details |
|---|---|---|---|
| Prepared CeO2 support / final batch | Not verified / 확인 못 함 | 0.001 |  |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Prepare and mix support solutions | NaOH,99% | 58.8 g |  |
| Prepare and mix support solutions | Water for NaOH | 140 mL |  |
| Prepare and mix support solutions | Ce(NO3)3·6H2O,99% | 4.9 g |  |
| Prepare and mix support solutions | Water for cerium salt | 84 mL |  |
| Wash and centrifuge | Wash water | Not verified / 확인 못 함 |  |
| Wash and centrifuge | Absolute ethanol | Not verified / 확인 못 함 |  |
| Dissolve nickel precursor | Ni(NO3)2·6H2O,99% | 0.1 g |  |
| Dissolve nickel precursor | Water | 40 mL |  |
| First pH adjustment and aging | Ammonia solution,2.5wt% | Not verified / 확인 못 함 |  |
| Second pH adjustment | Ammonia solution,25wt% | Not verified / 확인 못 함 |  |

Actual Ni contents are 1.95, 1.80 and 1.85 wt% for 2Ni-R, 2Ni-C and 2Ni-S respectively; nominal loading is not substituted for measured loading. These Ni/ceria specimens do not establish the catalog single-atom structure. Support preparation and 1 g transfer have distinct mass boundaries. P330 identifies a controller in the reported equipment description, not a calibrated mean-power curve. Multiple-vessel use and the full washing duration remain unreported. Recovered dry output, operating power, attended labor and prices are not established by these preparation sections; this is not a cost-complete protocol.

### S65. 2Ni-C; nominal2wt%Ni on ceria nanocubes

Record: `ni-ceria-c-2022`. Boundary: catalyst_powder.

Source: [CO <sub>2</sub> Activation over Nanoshaped CeO <sub>2</sub> Decorated with Nickel for Low-Temperature Methane Dry Reforming](https://doi.org/10.1021/acsami.2c05221). [DOI 10.1021/acsami.2c05221](https://doi.org/10.1021/acsami.2c05221). Locator: Section2.1 Synthesis of Catalysts. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare and mix support solutions | 0.5 h; Intermediate batch: ceria |  |
| Hydrothermal ceria synthesis | 180 °C; hold 24 h; ramp unreported °C/min; Intermediate batch: ceria | Approximately 35 mL is the autoclave capacity, not a reported aliquot volume. Number of vessels and distribution of the combined solution are unreported. |
| Wash and centrifuge | Intermediate batch: ceria | 7500 rpm90 s per centrifugation; repeat with water and finally ethanol until sodium removal. Total wash/cycle count and elapsed time unreported. |
| Dry ceria | 70 °C; hold unreported h; ramp unreported °C/min; air; Intermediate batch: ceria | Overnight duration unreported. |
| Calcine ceria | 500 °C; hold 4 h; ramp 5 °C/min; static air; Intermediate batch: ceria |  |
| Dissolve nickel precursor | 0.25 h |  |
| Add prepared ceria | 0.25 h | Use 1 g of the separately prepared ceria; internal transfer. |
| First pH adjustment and aging | 2 h | Add 2.5 wt% ammonia dropwise to pH 7.5, then stir 2 h; addition time unreported. |
| Second pH adjustment | 0.25 h | Adjust pH 9 with 25 wt% ammonia, then stir 15 min; addition time unreported. |
| Filter and dry | 70 °C; hold unreported h; ramp unreported °C/min | Filtration time and overnight drying duration unreported. |
| Calcine Ni/ceria | 500 °C; hold 4 h; ramp 5 °C/min |  |

Intermediate transfers (recovery is not inferred from precursor inputs):

| Intermediate / destination | Recovered kg | Used kg | Source details |
|---|---|---|---|
| Prepared CeO2 support / final batch | Not verified / 확인 못 함 | 0.001 |  |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Prepare and mix support solutions | NaOH,99% | 58.8 g |  |
| Prepare and mix support solutions | Water for NaOH | 140 mL |  |
| Prepare and mix support solutions | Ce(NO3)3·6H2O,99% | 4.9 g |  |
| Prepare and mix support solutions | Water for cerium salt | 84 mL |  |
| Wash and centrifuge | Wash water | Not verified / 확인 못 함 |  |
| Wash and centrifuge | Absolute ethanol | Not verified / 확인 못 함 |  |
| Dissolve nickel precursor | Ni(NO3)2·6H2O,99% | 0.1 g |  |
| Dissolve nickel precursor | Water | 40 mL |  |
| First pH adjustment and aging | Ammonia solution,2.5wt% | Not verified / 확인 못 함 |  |
| Second pH adjustment | Ammonia solution,25wt% | Not verified / 확인 못 함 |  |

Actual Ni contents are 1.95, 1.80 and 1.85 wt% for 2Ni-R, 2Ni-C and 2Ni-S respectively; nominal loading is not substituted for measured loading. These Ni/ceria specimens do not establish the catalog single-atom structure. Support preparation and 1 g transfer have distinct mass boundaries. P330 identifies a controller in the reported equipment description, not a calibrated mean-power curve. Multiple-vessel use and the full washing duration remain unreported. Recovered dry output, operating power, attended labor and prices are not established by these preparation sections; this is not a cost-complete protocol.

### S66. 2Ni-S; nominal2wt%Ni on ceria nanospheres

Record: `ni-ceria-s-2022`. Boundary: catalyst_powder.

Source: [CO <sub>2</sub> Activation over Nanoshaped CeO <sub>2</sub> Decorated with Nickel for Low-Temperature Methane Dry Reforming](https://doi.org/10.1021/acsami.2c05221). [DOI 10.1021/acsami.2c05221](https://doi.org/10.1021/acsami.2c05221). Locator: Section2.1 Synthesis of Catalysts. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare ceria sol | 1 h; Intermediate batch: ceria |  |
| Age under controlled humidity | 40 °C; hold 48 h; ramp unreported °C/min; Intermediate batch: ceria | 25% relative humidity; 50 mL covered glass beaker. |
| Second aging | 100 °C; hold 48 h; ramp unreported °C/min; Intermediate batch: ceria | Humidity not constrained in this step. |
| Extract template | 45 °C; hold 24 h; ramp unreported °C/min; Intermediate batch: ceria |  |
| Calcine ceria spheres | 500 °C; hold 4 h; ramp 1 °C/min; static air; Intermediate batch: ceria |  |
| Dissolve nickel precursor | 0.25 h |  |
| Add prepared ceria | 0.25 h | Use 1 g of the separately prepared ceria; internal transfer. |
| First pH adjustment and aging | 2 h | Add 2.5 wt% ammonia dropwise to pH 7.5, then stir 2 h; addition time unreported. |
| Second pH adjustment | 0.25 h | Adjust pH 9 with 25 wt% ammonia, then stir 15 min; addition time unreported. |
| Filter and dry | 70 °C; hold unreported h; ramp unreported °C/min | Filtration time and overnight drying duration unreported. |
| Calcine Ni/ceria | 500 °C; hold 4 h; ramp 5 °C/min |  |

Intermediate transfers (recovery is not inferred from precursor inputs):

| Intermediate / destination | Recovered kg | Used kg | Source details |
|---|---|---|---|
| Prepared CeO2 support / final batch | Not verified / 확인 못 함 | 0.001 |  |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Prepare ceria sol | CTAB,98% | 0.91 g |  |
| Prepare ceria sol | Ce(NO3)3·6H2O,99% | 2.18 g |  |
| Prepare ceria sol | Absolute ethanol | 10 mL |  |
| Extract template | Absolute ethanol for extraction | Not verified / 확인 못 함 |  |
| Dissolve nickel precursor | Ni(NO3)2·6H2O,99% | 0.1 g |  |
| Dissolve nickel precursor | Water | 40 mL |  |
| First pH adjustment and aging | Ammonia solution,2.5wt% | Not verified / 확인 못 함 |  |
| Second pH adjustment | Ammonia solution,25wt% | Not verified / 확인 못 함 |  |

Actual Ni contents are 1.95, 1.80 and 1.85 wt% for 2Ni-R, 2Ni-C and 2Ni-S respectively; nominal loading is not substituted for measured loading. These Ni/ceria specimens do not establish the catalog single-atom structure. Support preparation and 1 g transfer have distinct mass boundaries. P330 identifies a controller in the reported equipment description, not a calibrated mean-power curve. Multiple-vessel use and the full washing duration remain unreported. Recovered dry output, operating power, attended labor and prices are not established by these preparation sections; this is not a cost-complete protocol.

### S67. 1Cu/CeO2-NC; nominal1wt%Cu on ceria nanocubes

Record: `cu-ceria-nc-2026`. Boundary: catalyst_powder.

Source: [Fine-Tuning Catalysts: The Role of Support Nanomorphology in Shaping Cu/CeO <sub>2</sub> CO-PROX Properties](https://doi.org/10.1021/acscatal.5c06552). [DOI 10.1021/acscatal.5c06552](https://doi.org/10.1021/acscatal.5c06552). Locator: Experimental and Theoretical Details: opening catalyst-preparation paragraph. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Supply ceria nanocubes | Not quantified | Ceria support synthesis is referred to earlier work; this selected boundary begins with preformed nanocubes. |
| Impregnate copper | Not quantified | Incipient wetness with aqueous copper nitrate; exact masses, concentration, volume and drying details are not given in this paragraph. |
| Calcine Cu/ceria | 500 °C; hold 2 h; ramp unreported °C/min; air |  |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Supply ceria nanocubes | Preformed ceria nanocubes | Not verified / 확인 못 함 |  |
| Impregnate copper | Copper nitrate solution | Not verified / 확인 못 함 |  |

This is a partial final-catalyst preparation record starting from preformed support. Earlier support references and unspecified impregnation/drying details remain necessary for full replication. The 0.16 wt% Cu nanocube and 1 wt% Cu nanosphere variants are different specimens. This preparation does not verify the catalog CuO phase/loading. Recovered dry output, operating power, attended labor and prices are not established by these preparation sections; this is not a cost-complete protocol.

### S68. M-MoS2 nanosheets stored in water

Record: `mos2-m-2016`. Boundary: catalyst_powder.

Source: [Pure and stable metallic phase molybdenum disulfide nanosheets for hydrogen evolution reaction](https://doi.org/10.1038/ncomms10672). [DOI 10.1038/ncomms10672](https://doi.org/10.1038/ncomms10672). Locator: Methods: Preparation of M-MoS2 and S-MoS2. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare precursor solution | 2 h |  |
| Hydrothermal reaction | 200 °C; hold 12 h; ramp unreported °C/min | Place autoclave into preheated oven; sample ramp history not reported. |
| Cool | Not quantified | Remove autoclave and cool rapidly to room temperature; duration unreported. |
| Collect and wash | Not quantified | Several water washes; exact count and amounts unreported. |
| Store suspension | Not quantified | Store in deionized water; no drying or weighed dry product reported. |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Prepare precursor solution | MoO3 | 0.012 g |  |
| Prepare precursor solution | Thioacetamide | 0.014 g |  |
| Prepare precursor solution | Urea | 0.12 g |  |
| Prepare precursor solution | Water | 10 mL |  |
| Collect and wash | Wash water | Not verified / 확인 못 함 |  |
| Store suspension | Storage water | Not verified / 확인 못 함 |  |

The stored product is a water suspension. A hypothetical dry recovery or drying step is not added; costing a delivered dry catalyst requires a separately defined boundary. The two phases are different source specimens. A generic acidic-HER MoS2 catalog entry does not fix phase or synthesis. Recovered dry output, operating power, attended labor and prices are not established by these preparation sections; this is not a cost-complete protocol.

### S69. S-MoS2 nanosheets stored in water

Record: `mos2-s-2016`. Boundary: catalyst_powder.

Source: [Pure and stable metallic phase molybdenum disulfide nanosheets for hydrogen evolution reaction](https://doi.org/10.1038/ncomms10672). [DOI 10.1038/ncomms10672](https://doi.org/10.1038/ncomms10672). Locator: Methods: Preparation of M-MoS2 and S-MoS2. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare precursor solution | 2 h |  |
| Hydrothermal reaction | 240 °C; hold 12 h; ramp unreported °C/min | Place autoclave into preheated oven; sample ramp history not reported. |
| Cool | Not quantified | Remove autoclave and cool rapidly to room temperature; duration unreported. |
| Collect and wash | Not quantified | Several water washes; exact count and amounts unreported. |
| Store suspension | Not quantified | Store in deionized water; no drying or weighed dry product reported. |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Prepare precursor solution | MoO3 | 0.012 g |  |
| Prepare precursor solution | Thioacetamide | 0.014 g |  |
| Prepare precursor solution | Urea | 0.12 g |  |
| Prepare precursor solution | Water | 10 mL |  |
| Collect and wash | Wash water | Not verified / 확인 못 함 |  |
| Store suspension | Storage water | Not verified / 확인 못 함 |  |

The stored product is a water suspension. A hypothetical dry recovery or drying step is not added; costing a delivered dry catalyst requires a separately defined boundary. The two phases are different source specimens. A generic acidic-HER MoS2 catalog entry does not fix phase or synthesis. Recovered dry output, operating power, attended labor and prices are not established by these preparation sections; this is not a cost-complete protocol.

### S70. Activated Ag hollow-fiber electrode;240s oxidation

Record: `ag-hollow-fiber-redox-2022`. Boundary: electrode.

Source: [Hierarchical micro/nanostructured silver hollow fiber boosts electroreduction of carbon dioxide](https://doi.org/10.1038/s41467-022-30733-6). [DOI 10.1038/s41467-022-30733-6](https://doi.org/10.1038/s41467-022-30733-6). Locator: Supplementary Information,Preparations,pp.S2–S3; Ag HF synthesis and electrochemical redox activation. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Dissolve polymer | 1 h; Intermediate batch: fiber |  |
| Disperse silver by ball milling | 24 h; Intermediate batch: fiber | 250 mL zirconia jar; 5 mm zirconia balls. Electrode fabrication uses a portion of this much larger batch. |
| Cool and degas | 5 h; Intermediate batch: fiber | Cool to room temperature, then vacuumize 1 mbar for 5 h; cooling time is additional and unreported. |
| Spin and phase-invert | Intermediate batch: fiber | Extrude into water; extrusion time and water demand unreported. |
| Extract solvent | 24 h; Intermediate batch: fiber | Keep in water 24 h. |
| Stretch and dry green fibers | 48 h; Intermediate batch: fiber | Ambient conditions, approximately 28% relative humidity; stretching time additional and unreported. |
| Cut and remove polymer | 600 °C; hold 6 h; ramp 1 °C/min; air; Intermediate batch: fiber | Cut into lengths; cutting time unreported. Air 100 mL/min; flow reference state unspecified. |
| Cool | Intermediate batch: fiber | Natural cooling to room temperature; duration unreported. |
| Reduce silver fibers | 300 °C; hold 3 h; ramp 1 °C/min; 5% H2/Ar; Intermediate batch: fiber |  |
| Assemble fiber electrode | Not quantified | Ten tubes with 3 cm exposed length each; conductive silver adhesive to copper tube, gas-tight epoxy at ends/joints. Exposed area 4 cm2; silver loading 29±1 mg/cm2. No exact mass transfer inferred. |
| Cure electrode assembly | 12 h | Room temperature unspecified. |
| Prepare activation cell and purge | 0.5 h | 0.5 M KHCO3, CO2-saturated; CO2 10 mL/min after evacuation. Nafion 117 separator, Ag/AgCl reference and Pt mesh counterelectrode are setup elements, not assumed consumables. |
| Electrooxidize | 0.0666667 h | 2.0 V versus KCl-saturated Ag/AgCl, 240 s. Reference potential is not cell voltage or electrical input power. |
| Electroreduce | 0.166667 h | -0.50 V versus KCl-saturated Ag/AgCl, 600 s; no current-time integral or system input energy reported. |

Intermediate transfers (recovery is not inferred from precursor inputs):

| Intermediate / destination | Recovered kg | Used kg | Source details |
|---|---|---|---|
| Silver hollow fibers / final batch | Not verified / 확인 못 함 | Not verified / 확인 못 함 | Only ten selected tubes enter the final electrode; no exact total recovery or used mass reported. |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Dissolve polymer | Polyetherimide | 24 g |  |
| Dissolve polymer | N-methyl-2-pyrrolidone | 96 g |  |
| Disperse silver by ball milling | Silver powder,99.9%,50nm | 80 g |  |
| Spin and phase-invert | Spinning-bath water | Not verified / 확인 못 함 |  |
| Extract solvent | Extraction water | Not verified / 확인 못 함 |  |
| Assemble fiber electrode | Copper tube | Not verified / 확인 못 함 |  |
| Assemble fiber electrode | Conductive silver adhesive | Not verified / 확인 못 함 |  |
| Assemble fiber electrode | Nonconductive epoxy | Not verified / 확인 못 함 |  |
| Prepare activation cell and purge | KHCO3 electrolyte,0.5M | Not verified / 확인 못 함 |  |

This is an area-defined hollow-fiber electrode, not the generic Ag membrane-electrode assembly in the catalog. It cannot use powder batch costing. The 80 g silver synthesis is not the silver used in one 4 cm2 electrode. Whole fiber output and exact transfer mass remain unknown. Potentiostat potentials and geometric loading are retained as source conditions; electrical energy and manufacturing yield are not inferred. Recovered dry output, operating power, attended labor and prices are not established by these preparation sections; this is not a cost-complete protocol.

### S71. NiHT-Co; Co-modified Ni hydrotalcite-derived catalyst

Record: `niht-co-2025`. Boundary: catalyst_powder.

Source: [Synergistic Effect of Group 9 Metals on the Performance of Hydrotalcite-Derived Ni Catalysts for Methane Dry Reforming](https://doi.org/10.1021/acsomega.5c08293). [DOI 10.1021/acsomega.5c08293](https://doi.org/10.1021/acsomega.5c08293). Locator: Methodology: Catalyst Preparation. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Dissolve metal precursors | Not quantified | Mg/Al/Ni molar ratio 2.5:1:0.212. Source adds CoCl2 at 20% of the weight of Ni; no elemental loading or absolute salt masses inferred. |
| Precipitate and stir | 2 h | Add a small aliquot of 1 M Na2CO3 preheated to 60 °C, then 2 M NaOH to pH 9.5. The 60 °C value describes the carbonate solution, not a verified vessel temperature. |
| Hydrothermal aging | 80 °C; hold unreported h; ramp unreported °C/min | Overnight duration is unreported. |
| Wash and separate | Not quantified | Centrifugal filtration until neutral pH; counts and times unreported. |
| Dry precursor | 100 °C; hold 8 h; ramp unreported °C/min |  |
| Calcine precursor | 800 °C; hold 6 h; ramp unreported °C/min |  |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Dissolve metal precursors | Mg nitrate | Not verified / 확인 못 함 |  |
| Dissolve metal precursors | Al nitrate | Not verified / 확인 못 함 |  |
| Dissolve metal precursors | Ni nitrate | Not verified / 확인 못 함 |  |
| Dissolve metal precursors | CoCl2 | Not verified / 확인 못 함 |  |
| Dissolve metal precursors | Deionized water | 75 mL |  |
| Precipitate and stir | Na2CO3 solution, 1 M | Not verified / 확인 못 함 |  |
| Precipitate and stir | NaOH solution, 2 M | Not verified / 확인 못 함 |  |
| Wash and separate | Wash water | Not verified / 확인 못 함 |  |

Selected boundary ends at calcined powder; reduction and catalytic evaluation are separate. This source specimen does not establish the catalog Ni/Co loadings. Unless explicitly reported, recovered dry output remains unknown. Mean electrical demand, attended labor and procurement prices are not established; this is not a cost-complete protocol.

### S72. 0.2-NiMoS2 unsupported

Record: `nimos2-2-unsupported-2023`. Boundary: catalyst_powder.

Source: [Selective Deoxygenation of Waste Cooking Oil to Diesel-Like Hydrocarbons Using Supported and Unsupported NiMoS2 Catalysts](https://doi.org/10.1021/acsomega.3c06188). [DOI 10.1021/acsomega.3c06188](https://doi.org/10.1021/acsomega.3c06188). Locator: Experimental Section: Catalyst Synthesis. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare sulfide precursors | Not quantified | Nickel salt mass and additional dissolving water are not specified. |
| Hydrothermal synthesis | 360 °C; hold 1 h; ramp unreported °C/min; H2 | Initial H2 pressure 28 bar; gauge/absolute basis is unstated. 250 mL is reactor capacity, not solution charge. |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Prepare sulfide precursors | Ammonium tetrathiomolybdate | 0.3 g |  |
| Prepare sulfide precursors | Deionized water | 50 g |  |
| Prepare sulfide precursors | Ni(NO3)2·6H2O | Not verified / 확인 못 함 |  |
| Prepare sulfide precursors | Additional water | Not verified / 확인 못 함 |  |
| Prepare sulfide precursors | Decalin | 5 g |  |

Ni/(Ni + Mo) atomic ratio 0.2 is not a catalyst mass fraction. Recovery, rinsing and drying are not described in this selected synthesis paragraph. Waste-cooking-oil deoxygenation and this alumina/unsupported formulation do not establish a carbon-supported catalog formulation or a general bio-oil result. Unless explicitly reported, recovered dry output remains unknown. Mean electrical demand, attended labor and procurement prices are not established; this is not a cost-complete protocol.

### S73. 0.2-NiMoS2/gamma-Al2O3

Record: `nimos2-2-alumina-2023`. Boundary: catalyst_powder.

Source: [Selective Deoxygenation of Waste Cooking Oil to Diesel-Like Hydrocarbons Using Supported and Unsupported NiMoS2 Catalysts](https://doi.org/10.1021/acsomega.3c06188). [DOI 10.1021/acsomega.3c06188](https://doi.org/10.1021/acsomega.3c06188). Locator: Experimental Section: Catalyst Synthesis. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare sulfide precursors | Not quantified | The supported route does not restate absolute precursor quantities; the unsupported quantities are not transferred automatically. |
| Warm precursor solution | 80 °C; hold 0.5 h; ramp unreported °C/min |  |
| Add support | Not quantified | The source states 20 wt% gamma-Al2O3 based on catalyst weight; actual support mass and recovered catalyst mass are unreported. |
| Hydrothermal synthesis | 350 °C; hold unreported h; ramp unreported °C/min; H2 | Initial H2 pressure 28 bar; gauge/absolute basis and supported-route hold time are not stated. |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Prepare sulfide precursors | Ammonium tetrathiomolybdate | Not verified / 확인 못 함 |  |
| Prepare sulfide precursors | Ni(NO3)2·6H2O | Not verified / 확인 못 함 |  |
| Prepare sulfide precursors | Deionized water | Not verified / 확인 못 함 |  |
| Prepare sulfide precursors | Decalin | Not verified / 확인 못 함 |  |
| Add support | gamma-Al2O3 | Not verified / 확인 못 함 |  |

Ni/(Ni + Mo) atomic ratio 0.2 is not a catalyst mass fraction. Recovery, rinsing and drying are not described in this selected synthesis paragraph. Waste-cooking-oil deoxygenation and this alumina/unsupported formulation do not establish a carbon-supported catalog formulation or a general bio-oil result. Unless explicitly reported, recovered dry output remains unknown. Mean electrical demand, attended labor and procurement prices are not established; this is not a cost-complete protocol.

### S74. 0.3-NiMoS2 unsupported

Record: `nimos2-3-unsupported-2023`. Boundary: catalyst_powder.

Source: [Selective Deoxygenation of Waste Cooking Oil to Diesel-Like Hydrocarbons Using Supported and Unsupported NiMoS2 Catalysts](https://doi.org/10.1021/acsomega.3c06188). [DOI 10.1021/acsomega.3c06188](https://doi.org/10.1021/acsomega.3c06188). Locator: Experimental Section: Catalyst Synthesis. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare sulfide precursors | Not quantified | Nickel salt mass and additional dissolving water are not specified. |
| Hydrothermal synthesis | 360 °C; hold 1 h; ramp unreported °C/min; H2 | Initial H2 pressure 28 bar; gauge/absolute basis is unstated. 250 mL is reactor capacity, not solution charge. |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Prepare sulfide precursors | Ammonium tetrathiomolybdate | 0.3 g |  |
| Prepare sulfide precursors | Deionized water | 50 g |  |
| Prepare sulfide precursors | Ni(NO3)2·6H2O | Not verified / 확인 못 함 |  |
| Prepare sulfide precursors | Additional water | Not verified / 확인 못 함 |  |
| Prepare sulfide precursors | Decalin | 5 g |  |

Ni/(Ni + Mo) atomic ratio 0.3 is not a catalyst mass fraction. Recovery, rinsing and drying are not described in this selected synthesis paragraph. Waste-cooking-oil deoxygenation and this alumina/unsupported formulation do not establish a carbon-supported catalog formulation or a general bio-oil result. Unless explicitly reported, recovered dry output remains unknown. Mean electrical demand, attended labor and procurement prices are not established; this is not a cost-complete protocol.

### S75. 0.3-NiMoS2/gamma-Al2O3

Record: `nimos2-3-alumina-2023`. Boundary: catalyst_powder.

Source: [Selective Deoxygenation of Waste Cooking Oil to Diesel-Like Hydrocarbons Using Supported and Unsupported NiMoS2 Catalysts](https://doi.org/10.1021/acsomega.3c06188). [DOI 10.1021/acsomega.3c06188](https://doi.org/10.1021/acsomega.3c06188). Locator: Experimental Section: Catalyst Synthesis. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare sulfide precursors | Not quantified | The supported route does not restate absolute precursor quantities; the unsupported quantities are not transferred automatically. |
| Warm precursor solution | 80 °C; hold 0.5 h; ramp unreported °C/min |  |
| Add support | Not quantified | The source states 20 wt% gamma-Al2O3 based on catalyst weight; actual support mass and recovered catalyst mass are unreported. |
| Hydrothermal synthesis | 350 °C; hold unreported h; ramp unreported °C/min; H2 | Initial H2 pressure 28 bar; gauge/absolute basis and supported-route hold time are not stated. |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Prepare sulfide precursors | Ammonium tetrathiomolybdate | Not verified / 확인 못 함 |  |
| Prepare sulfide precursors | Ni(NO3)2·6H2O | Not verified / 확인 못 함 |  |
| Prepare sulfide precursors | Deionized water | Not verified / 확인 못 함 |  |
| Prepare sulfide precursors | Decalin | Not verified / 확인 못 함 |  |
| Add support | gamma-Al2O3 | Not verified / 확인 못 함 |  |

Ni/(Ni + Mo) atomic ratio 0.3 is not a catalyst mass fraction. Recovery, rinsing and drying are not described in this selected synthesis paragraph. Waste-cooking-oil deoxygenation and this alumina/unsupported formulation do not establish a carbon-supported catalog formulation or a general bio-oil result. Unless explicitly reported, recovered dry output remains unknown. Mean electrical demand, attended labor and procurement prices are not established; this is not a cost-complete protocol.

### S76. chi-Fe5C2@SiO2_L

Record: `fe5c2-silica-l-2022`. Boundary: catalyst_powder.

Source: [Effects of Silica Shell Encapsulated Nanocrystals on Active χ-Fe5C2 Phase and Fischer–Tropsch Synthesis](https://doi.org/10.3390/nano12203704). [DOI 10.3390/nano12203704](https://doi.org/10.3390/nano12203704). Locator: Sections 2.2.1 and 2.2.2; selected low-loading silica-shell specimen. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Mix and degas | N2; Intermediate batch: carbide | Room-temperature N2 degassing; duration unreported. |
| Heat amine mixture | 120 °C; hold unreported h; ramp unreported °C/min; N2; Intermediate batch: carbide | Mix fully before carbonyl addition; hold and ramp unreported. |
| Introduce Fe carbonyl and react | 180 °C; hold 0.5 h; ramp unreported °C/min; N2; Intermediate batch: carbide |  |
| Complete carbide synthesis | 350 °C; hold 0.08333333333333333 h; ramp unreported °C/min; N2; Intermediate batch: carbide |  |
| Cool and passivate | 0.25 h; 5% O2/N2; Intermediate batch: carbide | Cooling to ambient is additional and unreported; passivation lasts 15 min. |
| Magnetically separate and wash | Intermediate batch: carbide | Approximately 20 washes of about 1 min and about 250 mL total hexane. Approximate values are retained here, not set as exact repetition, duration or purchase quantity. |
| Prepare solution A | Not quantified | Disperse 0.070 g recovered carbide with PVP in ethanol; sonication time unreported. |
| Mix CTAB and water | 60 °C; hold 0.5 h; ramp unreported °C/min |  |
| Prepare solution B | 60 °C; hold unreported h; ramp unreported °C/min | Add solution A and mix at 60 °C for at least 30 min. Exact elapsed time is unreported. |
| Prepare solution C | 90 °C; hold 0.3333333333333333 h; ramp unreported °C/min |  |
| Cool solutions | Not quantified | Cool B and C to room temperature before mixing; duration unreported. |
| Encapsulate carbide | 48 h |  |
| Wash encapsulated particles | Not quantified |  |
| Dry silica-shell particles | 60 °C; hold unreported h; ramp unreported °C/min; vacuum | Drying duration is unreported. No additional calcination or pre-reaction reduction is added. |

Intermediate transfers (recovery is not inferred from precursor inputs):

| Intermediate / destination | Recovered kg | Used kg | Source details |
|---|---|---|---|
| Preformed chi-Fe5C2 nanoparticles / final batch | Not verified / 확인 못 함 | 7e-05 |  |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Mix and degas | Octadecylamine, 85% | 30 g |  |
| Mix and degas | CTAB | 0.226 g |  |
| Introduce Fe carbonyl and react | Fe(CO)5, 99.99% | 1 mL |  |
| Magnetically separate and wash | Hexane | Not verified / 확인 못 함 |  |
| Prepare solution A | PVP, average molecular weight 40000 | 3 g |  |
| Prepare solution A | Ethanol | 50 mL |  |
| Mix CTAB and water | CTAB | 8.4 g |  |
| Mix CTAB and water | Deionized water | 72 g |  |
| Prepare solution C | TEOS, 98% | 6 g |  |
| Prepare solution C | Triethanolamine, 98% | 45 g |  |
| Wash encapsulated particles | Wash water | Not verified / 확인 못 함 |  |
| Wash encapsulated particles | Wash ethanol | Not verified / 확인 못 함 |  |

The source reports 3.5 wt% Fe for the L specimen. The H variant changes aliquots and aqueous contact; its quantities are not inferred by copying L. Measured nanoparticle and final dry recovery remain unknown. Some formulation stages can occur concurrently; operation-hour sums are not a production schedule. Unless explicitly reported, recovered dry output remains unknown. Mean electrical demand, attended labor and procurement prices are not established; this is not a cost-complete protocol.

### S77. BMP-30 calcined ZSM-5

Record: `bmp-30-zsm5-2017`. Boundary: catalyst_powder.

Source: [Simple organic structure directing agents for synthesizing nanocrystalline zeolites](https://doi.org/10.1039/c7sc02858j). [DOI 10.1039/c7sc02858j](https://doi.org/10.1039/c7sc02858j). Locator: Experimental: Synthesis of zeolites; Results: Synthesis and characterization of nanosized ZSM-5. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare zeolite gel | Not quantified | Nominal Si/Al = 30, OSDA/Si = 0.4, H2O/Si = 15. Boundary begins with prepared OSDA hydroxide solution; upstream OSDA synthesis is not included. |
| Concentrate gel | Not quantified | Stir and evaporate excess water until desired gel composition; time and temperature unreported. |
| Crystallize zeolite | 150 °C; hold 336 h; ramp unreported °C/min | 14 days converted to 336 h. |
| Filter and wash | Not quantified |  |
| Dry zeolite | 100 °C; hold unreported h; ramp unreported °C/min | Drying duration unreported. |
| Remove organic template | 580 °C; hold 6 h; ramp unreported °C/min; air |  |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Prepare zeolite gel | N-butyl-N-methylpyrrolidinium hydroxide solution | Not verified / 확인 못 함 |  |
| Prepare zeolite gel | Ludox AS-40, 40 wt% silica | Not verified / 확인 못 함 |  |
| Prepare zeolite gel | Al(OH)3 source, source specification 58% | Not verified / 확인 못 함 |  |
| Filter and wash | Wash water | Not verified / 확인 못 함 |  |

Reported solid yields are inequalities (>90% for BMP-30 and <70% for TPA-30) on inorganic input basis; no exact recovered mass or uncertainty distribution is inferred. Boundary ends at calcined powder. Pelletization, sieving and 540 °C air activation of a 50 mg reactor specimen belong to subsequent testing, not to this whole-batch preparation. Unless explicitly reported, recovered dry output remains unknown. Mean electrical demand, attended labor and procurement prices are not established; this is not a cost-complete protocol.

### S78. TPA-30 calcined ZSM-5

Record: `tpa-30-zsm5-2017`. Boundary: catalyst_powder.

Source: [Simple organic structure directing agents for synthesizing nanocrystalline zeolites](https://doi.org/10.1039/c7sc02858j). [DOI 10.1039/c7sc02858j](https://doi.org/10.1039/c7sc02858j). Locator: Experimental: Synthesis of zeolites; Results: Synthesis and characterization of nanosized ZSM-5. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare zeolite gel | Not quantified | Nominal Si/Al = 30, OSDA/Si = 0.4, H2O/Si = 15. Boundary begins with prepared OSDA hydroxide solution; upstream OSDA synthesis is not included. |
| Concentrate gel | Not quantified | Stir and evaporate excess water until desired gel composition; time and temperature unreported. |
| Crystallize zeolite | 150 °C; hold 336 h; ramp unreported °C/min | 14 days converted to 336 h. |
| Filter and wash | Not quantified |  |
| Dry zeolite | 100 °C; hold unreported h; ramp unreported °C/min | Drying duration unreported. |
| Remove organic template | 580 °C; hold 6 h; ramp unreported °C/min; air |  |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Prepare zeolite gel | Tetrapropylammonium hydroxide solution | Not verified / 확인 못 함 |  |
| Prepare zeolite gel | Ludox AS-40, 40 wt% silica | Not verified / 확인 못 함 |  |
| Prepare zeolite gel | Al(OH)3 source, source specification 58% | Not verified / 확인 못 함 |  |
| Filter and wash | Wash water | Not verified / 확인 못 함 |  |

Reported solid yields are inequalities (>90% for BMP-30 and <70% for TPA-30) on inorganic input basis; no exact recovered mass or uncertainty distribution is inferred. Boundary ends at calcined powder. Pelletization, sieving and 540 °C air activation of a 50 mg reactor specimen belong to subsequent testing, not to this whole-batch preparation. Unless explicitly reported, recovered dry output remains unknown. Mean electrical demand, attended labor and procurement prices are not established; this is not a cost-complete protocol.

### S79. Au-In electrodeposited on Ni foam

Record: `auin-ni-foam-2025`. Boundary: electrode.

Source: [Gold–Indium Electrocatalysts for the Selective Oxidation of Glycerol Coupled with CO 2 Reduction](https://doi.org/10.1002/cssc.202402378). [DOI 10.1002/cssc.202402378](https://doi.org/10.1002/cssc.202402378). Locator: Experimental Section: Electrode Synthesis. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare indium stock | Not quantified | 0.25 M In3+ stock adjusted to pH 2 with diluted H2SO4; quantities unreported. |
| Prepare deposition bath | Not quantified | Final concentrations: KCN 1 M, glucose 0.1 M, In3+ 0.05 M, KOH 1.3 M, K[Au(CN)2] 0.025 M. 400 mL denotes cell capacity, not an established bath volume. |
| Clean Ni foam | Not quantified | Ni-4753 foam, 16 cm2, 1.6 mm thick; acetone cleaning followed by water rinse. |
| Deposit Au-In | 70 °C; hold 0.03333333333333333 h; ramp unreported °C/min | Apply -80 mA/cm2 for 120 s. Current density is not cell input power. Thermostat and cell preparation time are not included in the deposition hold. |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Prepare indium stock | Indium(III) sulfate, at least 98% | Not verified / 확인 못 함 |  |
| Prepare indium stock | Diluted H2SO4 | Not verified / 확인 못 함 |  |
| Prepare indium stock | Stock water | Not verified / 확인 못 함 |  |
| Prepare deposition bath | KCN | Not verified / 확인 못 함 |  |
| Prepare deposition bath | D-glucose | Not verified / 확인 못 함 |  |
| Prepare deposition bath | KOH | Not verified / 확인 못 함 |  |
| Prepare deposition bath | K[Au(CN)2] | Not verified / 확인 못 함 |  |
| Prepare deposition bath | Bath water | Not verified / 확인 못 함 |  |
| Clean Ni foam | Ni foam, 16 cm2 piece | 1 item |  |
| Clean Ni foam | Acetone | Not verified / 확인 못 함 |  |
| Clean Ni foam | Rinse water | Not verified / 확인 못 함 |  |

Au-only comparator uses a different bath and -70 mA/cm2; it is not substituted for the Au-In specimen. This Ni-foam-supported alloy is a glycerol-oxidation preparation variant, not the catalog Au/carbon formulation. Deposited mass and bath reuse/lifetime are not established. Unless explicitly reported, recovered dry output remains unknown. Mean electrical demand, attended labor and procurement prices are not established; this is not a cost-complete protocol.

### S80. PtBi/C from gas-aggregated clusters; powder before ink preparation

Record: `ptbi-carbon-gas-aggregation-2021`. Boundary: catalyst_powder.

Source: [Binary and ternary Pt-based clusters grown in a plasma multimagnetron-based gas aggregation source: electrocatalytic evaluation towards glycerol oxidation](https://doi.org/10.1039/d0na01009j). [DOI 10.1039/d0na01009j](https://doi.org/10.1039/d0na01009j). Locator: Experimental setup: cluster collection and carbon-supported electrode preparation. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Condition sputtering targets | Not quantified | Pt and Bi targets 99.99%; presputtering at least 5 min until stable voltage. Exact duration and target consumption unreported. |
| Collect bimetallic clusters | 0.166667 h | Collect in a glass vial for 10 min. Ar flow 80 sccm; reference temperature and pressure unstated. Target powers vary across experiments (Pt 20-30 W, Bi 8-13 W) and do not measure whole-system electricity. |
| Disperse collected clusters | Not quantified | Weigh collected material by vial mass difference; no specimen-specific recovered mass reported here. Sonication time unreported. |
| Treat carbon support | 400 °C; hold unreported h; ramp unreported °C/min; N2 | Vulcan XC72 at 400 °C under N2; treatment time and mass unreported. |
| Mix and disperse on carbon | Not quantified | 40 wt% total metal target; at least 20 min sonication. Exact duration and ethanol quantity unreported. |
| Filter and dry | Not quantified | Alumina membrane: 0.2 micrometre pores, 0.1 mm thickness, 13 mm diameter. Drying temperature/duration unreported. |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Condition sputtering targets | Pt sputtering target consumption | Not verified / 확인 못 함 |  |
| Condition sputtering targets | Bi sputtering target consumption | Not verified / 확인 못 함 |  |
| Disperse collected clusters | Ethanol | Not verified / 확인 못 함 |  |
| Treat carbon support | Vulcan XC72 | Not verified / 확인 못 함 |  |
| Mix and disperse on carbon | Mixing ethanol | Not verified / 확인 못 함 |  |
| Filter and dry | Alumina filter membrane, 13 mm diameter | Not verified / 확인 못 함 |  |

Selected boundary is supported powder before an ink aliquot is deposited on glassy carbon. Three-minute Si and three-second TEM-grid depositions are characterization specimens and are not powder collection times. The 40 wt% figure is a target for total metal; composition-specific Pt/Bi fractions and complete utility use remain unstated. No DHA selectivity or catalog exact composition is established by this import. Unless explicitly reported, recovered dry output remains unknown. Mean electrical demand, attended labor and procurement prices are not established; this is not a cost-complete protocol.

### S81. Meso-TiO2-25; mixed anatase/rutile microspheres before Pt loading

Record: `meso-tio2-25-2019`. Boundary: catalyst_powder.

Source: [Synthesis of uniform ordered mesoporous TiO 2 microspheres with controllable phase junctions for efficient solar water splitting](https://doi.org/10.1039/c8sc04155e). [DOI 10.1039/c8sc04155e](https://doi.org/10.1039/c8sc04155e). Locator: Supporting Information p. 1: Synthesis of Meso-TiO2-25; p. 2 defines subsequent Pt-loaded tests. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare self-assembly solution | Not quantified |  |
| First solvent evaporation | 40 °C; hold 20 h; ramp unreported °C/min |  |
| Second solvent evaporation | 80 °C; hold 8 h; ramp unreported °C/min |  |
| Nitrogen thermal treatment | 400 °C; hold 3 h; ramp unreported °C/min; N2 |  |
| Air thermal treatment | 400 °C; hold 3 h; ramp unreported °C/min; air |  |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Prepare self-assembly solution | Pluronic F127 | 1.5 g |  |
| Prepare self-assembly solution | Concentrated HCl | 2 g |  |
| Prepare self-assembly solution | Acetic acid | 2 g |  |
| Prepare self-assembly solution | Tetrabutyl titanate | 3.4 g |  |
| Prepare self-assembly solution | Tetrahydrofuran | 30 mL |  |

The source specifies separate 3 h nitrogen and air treatments. Gas flow, ramp and cooling durations remain unreported. This is a mixed-phase powder rather than the catalog pure-anatase baseline. The hydrogen-evolution tests use 1 wt% Pt and sacrificial methanol; Pt loading and reaction conditions are outside this unmodified powder boundary. Unless explicitly reported, recovered dry output remains unknown. Mean electrical demand, attended labor and procurement prices are not established; this is not a cost-complete protocol.

### S82. 2Pd-ZnO-i; as-calcined impregnation precursor

Record: `pd-zno-i-2021`. Boundary: catalyst_powder.

Source: [Mechanistic Study of Carbon Dioxide Hydrogenation over Pd/ZnO‐Based Catalysts: The Role of Palladium–Zinc Alloy in Selective Methanol Synthesis](https://doi.org/10.1002/anie.202103087). [DOI 10.1002/anie.202103087](https://doi.org/10.1002/anie.202103087). Locator: Supporting Information pp. 1-2 (PDF pp. 2-3): ZnO support and Synthesis of 2Pd-ZnO-i. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Supply ZnO support | Not quantified | Boundary starts with 300 mg of prepared ZnO. The upstream source paragraph gives 170 mL water and a 150 mL autoclave; loading/portioning is unresolved and is not entered as a cost-ready support recipe. |
| Impregnate palladium | Not quantified | 2 mL aqueous solution containing 15.3 mg palladium nitrate hydrate (source spelling: dehydrate). Solution volume is not independently treated as 2 mL pure water. |
| Dry impregnated support | Not quantified | Overnight at room temperature; duration and temperature unspecified. |
| Calcine impregnated support | 350 °C; hold 4 h; ramp 2 °C/min; air |  |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Supply ZnO support | Prepared ZnO support | 0.3 g |  |
| Impregnate palladium | Palladium nitrate hydrate, 99.9% | 0.0153 g |  |
| Impregnate palladium | Water for 2 mL impregnation solution | Not verified / 확인 못 함 |  |

Reported Pd content is 1.95 wt% by AAS; recovered final mass is not reported. The prepared-nanoparticle route is a different specimen. As-calcined precursor is not automatically the reduced Pd-Zn intermetallic phase. Subsequent reduction and reaction testing require their own boundary. Unresolved support synthesis charge/vessel discrepancy is preserved rather than silently corrected. Unless explicitly reported, recovered dry output remains unknown. Mean electrical demand, attended labor and procurement prices are not established; this is not a cost-complete protocol.

### S83. Cu/PI-300 powder from prepared polyimide support

Record: `cu-pi300-powder-2019`. Boundary: catalyst_powder.

Source: [Boosting selective nitrogen reduction to ammonia on electron-deficient copper nanoparticles](https://doi.org/10.1038/s41467-019-12312-4). [DOI 10.1038/s41467-019-12312-4](https://doi.org/10.1038/s41467-019-12312-4). Locator: Methods: Preparation of PI nanoflower; Preparation of Cu/PI catalyst and Cu/C catalyst. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Supply PI-300 support | Not quantified | Boundary starts with prepared PI-300. Upstream synthesis lists 1.08 g and 2.18 g monomers as 100 mmol each and takes a 30 mL solution aliquot; mass/mole consistency and recovered support yield are unresolved. |
| Disperse copper salt and support | 2 h | Combined sonication and vigorous stirring interval 2 h; not counted twice. |
| Add base and stir | 2 h |  |
| Reduce copper | Not quantified | Add NaBH4 solution dropwise; addition and subsequent reaction duration unreported. |
| Recover and wash | Not quantified | Centrifuge and wash thoroughly; times/counts unreported. |
| Dry powder | 60 °C; hold unreported h; ramp unreported °C/min; vacuum | Overnight duration unreported. |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Supply PI-300 support | Prepared PI-300 support | 0.1 g |  |
| Disperse copper salt and support | Cu(NO3)2·3H2O | 0.019 g |  |
| Disperse copper salt and support | Water | 8 mL |  |
| Add base and stir | NaOH solution, 1 M | 0.2 mL |  |
| Reduce copper | NaBH4 solution, 1 M | 0.5 mL |  |
| Recover and wash | Wash water | Not verified / 확인 못 함 |  |
| Recover and wash | Wash ethanol | Not verified / 확인 못 함 |  |

This is the powder before carbon-cloth ink deposition. PI-400, PI-600, Cu/C and CuOx/PI-300 are different specimens. The upstream support procedure has inconsistent mass/mole annotations and no total recovered mass; it is not silently interpreted as an exact manufacturing input. Unless explicitly reported, recovered dry output remains unknown. Mean electrical demand, attended labor and procurement prices are not established; this is not a cost-complete protocol.

### S84. WO3-H2/N2-1h on carbon cloth

Record: `wo3-h2n2-1h-electrode-2025`. Boundary: electrode.

Source: [Plasma-Assisted Surface Nitridation of Proton Intercalatable WO3 for Efficient Electrocatalytic Ammonia Synthesis](https://doi.org/10.1021/acsenergylett.5c01034). [DOI 10.1021/acsenergylett.5c01034](https://doi.org/10.1021/acsenergylett.5c01034). Locator: Supporting Information S1-S2 (PDF pp. 2-3); main text paragraph defining plasma-treated specimen names. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Dissolve tungsten precursor | 0.333333 h; Intermediate batch: stock | Source amount retained in mmol without an inferred molecular weight. |
| Acidify and dilute stock | Intermediate batch: stock | Add 3 M HCl to pH 1.2 and 3.5 mmol oxalic acid, then dilute to 25 mL. This is final solution volume, not an additional 25 mL water charge. |
| Prepare substrate | Not quantified | Carbon cloth with MPL, Hydro-LAT 1400, 0.75 by 0.75 cm. Sequential water and alcohol ultrasonic cleaning; exact times unreported. |
| Charge growth solution | Not quantified | Use 4 mL of the preceding 25 mL stock and add Na2SO4; no density or dry-mass allocation inferred. |
| Microwave hydrothermal growth | 180 °C; hold 0.25 h; ramp unreported °C/min |  |
| Cool and wash electrode | Not quantified | Cool to ambient and rinse several times; elapsed time and water amount unreported. |
| Dry electrode | 70 °C; hold unreported h; ramp unreported °C/min; ambient | Drying duration unreported. |
| Plasma surface nitridation | 1 h; H2/N2 (1:4) | H2/N2 = 1:4; 1 h treatment. Source states 16 torr, 20 kHz and 13 kV AC. Frequency and voltage do not establish electrical energy; ambient temperature has no numeric value. |

Intermediate transfers (recovery is not inferred from precursor inputs):

| Intermediate / destination | Recovered kg | Used kg | Source details |
|---|---|---|---|
| Tungsten precursor stock solution / final batch | Not verified / 확인 못 함 | Not verified / 확인 못 함 | Diluted to 25 mL; 4 mL is used. These are solution volumes, not recovered or transferred dry masses. |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Dissolve tungsten precursor | Na2WO4·2H2O | 1.25 mmol |  |
| Dissolve tungsten precursor | Deionized water | 10 mL |  |
| Acidify and dilute stock | HCl solution, 3 M | Not verified / 확인 못 함 |  |
| Acidify and dilute stock | Oxalic acid | 3.5 mmol |  |
| Acidify and dilute stock | Dilution water | Not verified / 확인 못 함 |  |
| Prepare substrate | Carbon cloth, 0.75 by 0.75 cm piece | 1 item |  |
| Prepare substrate | Cleaning water | Not verified / 확인 못 함 |  |
| Prepare substrate | Cleaning alcohol | Not verified / 확인 못 함 |  |
| Charge growth solution | Na2SO4 | 0.1 g |  |
| Cool and wash electrode | Rinse water | Not verified / 확인 못 함 |  |

This is surface nitridation to prepare an electrocatalyst, not an ammonia-producing plasma reactor. The catalog plasma-NRR route remains a distinct boundary. The precursor stock transfer is 4/25 on a volume basis. It is retained explicitly; stock mass and final electrode active mass are not inferred. Unless explicitly reported, recovered dry output remains unknown. Mean electrical demand, attended labor and procurement prices are not established; this is not a cost-complete protocol.

### S85. WO3-H2/N2-2h on carbon cloth

Record: `wo3-h2n2-2h-electrode-2025`. Boundary: electrode.

Source: [Plasma-Assisted Surface Nitridation of Proton Intercalatable WO3 for Efficient Electrocatalytic Ammonia Synthesis](https://doi.org/10.1021/acsenergylett.5c01034). [DOI 10.1021/acsenergylett.5c01034](https://doi.org/10.1021/acsenergylett.5c01034). Locator: Supporting Information S1-S2 (PDF pp. 2-3); main text paragraph defining plasma-treated specimen names. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Dissolve tungsten precursor | 0.333333 h; Intermediate batch: stock | Source amount retained in mmol without an inferred molecular weight. |
| Acidify and dilute stock | Intermediate batch: stock | Add 3 M HCl to pH 1.2 and 3.5 mmol oxalic acid, then dilute to 25 mL. This is final solution volume, not an additional 25 mL water charge. |
| Prepare substrate | Not quantified | Carbon cloth with MPL, Hydro-LAT 1400, 0.75 by 0.75 cm. Sequential water and alcohol ultrasonic cleaning; exact times unreported. |
| Charge growth solution | Not quantified | Use 4 mL of the preceding 25 mL stock and add Na2SO4; no density or dry-mass allocation inferred. |
| Microwave hydrothermal growth | 180 °C; hold 0.25 h; ramp unreported °C/min |  |
| Cool and wash electrode | Not quantified | Cool to ambient and rinse several times; elapsed time and water amount unreported. |
| Dry electrode | 70 °C; hold unreported h; ramp unreported °C/min; ambient | Drying duration unreported. |
| Plasma surface nitridation | 2 h; H2/N2 (1:4) | H2/N2 = 1:4; 2 h treatment. Source states 16 torr, 20 kHz and 13 kV AC. Frequency and voltage do not establish electrical energy; ambient temperature has no numeric value. |

Intermediate transfers (recovery is not inferred from precursor inputs):

| Intermediate / destination | Recovered kg | Used kg | Source details |
|---|---|---|---|
| Tungsten precursor stock solution / final batch | Not verified / 확인 못 함 | Not verified / 확인 못 함 | Diluted to 25 mL; 4 mL is used. These are solution volumes, not recovered or transferred dry masses. |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Dissolve tungsten precursor | Na2WO4·2H2O | 1.25 mmol |  |
| Dissolve tungsten precursor | Deionized water | 10 mL |  |
| Acidify and dilute stock | HCl solution, 3 M | Not verified / 확인 못 함 |  |
| Acidify and dilute stock | Oxalic acid | 3.5 mmol |  |
| Acidify and dilute stock | Dilution water | Not verified / 확인 못 함 |  |
| Prepare substrate | Carbon cloth, 0.75 by 0.75 cm piece | 1 item |  |
| Prepare substrate | Cleaning water | Not verified / 확인 못 함 |  |
| Prepare substrate | Cleaning alcohol | Not verified / 확인 못 함 |  |
| Charge growth solution | Na2SO4 | 0.1 g |  |
| Cool and wash electrode | Rinse water | Not verified / 확인 못 함 |  |

This is surface nitridation to prepare an electrocatalyst, not an ammonia-producing plasma reactor. The catalog plasma-NRR route remains a distinct boundary. The precursor stock transfer is 4/25 on a volume basis. It is retained explicitly; stock mass and final electrode active mass are not inferred. Unless explicitly reported, recovered dry output remains unknown. Mean electrical demand, attended labor and procurement prices are not established; this is not a cost-complete protocol.

### S86. Mo-6@SiO2; cationic molybdenum oxo alkylidene NHC complex

Record: `mo6-silica-2022`. Boundary: catalyst_powder.

Source: [Cationic molybdenum oxo alkylidenes stabilized by N-heterocyclic carbenes: from molecular systems to efficient supported metathesis catalysts](https://doi.org/10.1039/d2sc03321f). [DOI 10.1039/d2sc03321f](https://doi.org/10.1039/d2sc03321f). Locator: Experimental: Silica; [MoO(CHCMe3)(OHMT)(IMes)][B(ArF)4] (Mo-6); Synthesis of silica-supported complex Mo-6@SiO2. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Ligand substitution | 0.0833333 h; Intermediate batch: mo6 | Start from the named preformed Mo reagent and IMes; their prior syntheses are outside this boundary. |
| Remove and exchange solvents | Intermediate batch: mo6 | Remove benzene under vacuum; co-evaporate with 2 x 1 mL ether and 2 x 1 mL pentane. Durations unreported. |
| Prepare anion-exchange solutions | Intermediate batch: mo6 | Dissolve residue in 3 mL CH2Cl2 and add to NaB(ArF)4 suspended in 2 mL CH2Cl2. |
| Anion exchange | 2 h; Intermediate batch: mo6 |  |
| Isolate and wash molecular precursor | Intermediate batch: mo6 | Remove solvent, stir with 10 mL pentane, decant, wash with 4 mL pentane and dry under vacuum. Times unreported. |
| Filter molecular precursor | Intermediate batch: mo6 | Dissolve in 2 mL CH2Cl2, filter through Celite and add pentane to filtrate. Celite and final pentane amounts unreported. |
| Crystallize Mo-6 | -35 °C; hold unreported h; ramp unreported °C/min; Intermediate batch: mo6 | Storage time unreported; source yield 296.0 mg (80%). |
| Compact and sieve silica | Intermediate batch: silica | Aerosil Degussa, 200 m2/g; compact with water and sieve. Initial mass and dimensions are unreported. |
| Calcine silica | 500 °C; hold 12 h; ramp unreported °C/min; air; Intermediate batch: silica |  |
| First vacuum treatment | 500 °C; hold 8 h; ramp unreported °C/min; Intermediate batch: silica | Vacuum 10^-5 mbar = 10^-8 bar. |
| Second vacuum treatment | 700 °C; hold 14 h; ramp unreported °C/min; Intermediate batch: silica |  |
| Graft Mo-6 | 25 °C; hold 3 h; ramp unreported °C/min; N2 glovebox | Use 78.8 mg Mo-6 and 160.1 mg SiO2-700; additional solvent of the separately mentioned yellow Mo-6 solution is unspecified. |
| Decant and wash with dichlorobenzene | Not quantified | Three suspension/decantation cycles, 1 mL each; times unreported. |
| Wash with toluene | Not quantified | Three suspension/decantation cycles, 1 mL each; times unreported. |
| Wash with pentane | Not quantified | Three suspension/decantation cycles, 2 mL each; times unreported. |
| Dry supported complex | 2 h; high vacuum | Room temperature is unspecified. Reported isolated supported product: 180 mg. |

Reported dry output of this source specimen: 0.00018 kg. This is not a measurement of a new user batch.


Intermediate transfers (recovery is not inferred from precursor inputs):

| Intermediate / destination | Recovered kg | Used kg | Source details |
|---|---|---|---|
| Isolated Mo-6 molecular precursor / final batch | 0.000296 | 7.88e-05 | Source isolates 296.0 mg Mo-6 and uses 78.8 mg for grafting. |
| Prepared SiO2-700 / final batch | Not verified / 확인 못 함 | 0.0001601 |  |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Ligand substitution | IMes | 0.0669 g |  |
| Ligand substitution | [MoO(CHCMe3)(OHMT)(Cl)(3-BrPy)] | 0.155 g |  |
| Ligand substitution | Benzene | 4 mL |  |
| Remove and exchange solvents | Diethyl ether | 2 mL |  |
| Remove and exchange solvents | n-Pentane | 2 mL |  |
| Prepare anion-exchange solutions | NaB(ArF)4 | 0.1948 g |  |
| Prepare anion-exchange solutions | Dichloromethane | 5 mL |  |
| Isolate and wash molecular precursor | n-Pentane | 14 mL |  |
| Filter molecular precursor | Dichloromethane | 2 mL |  |
| Filter molecular precursor | Celite | Not verified / 확인 못 함 |  |
| Filter molecular precursor | Crystallization n-pentane | Not verified / 확인 못 함 |  |
| Compact and sieve silica | Aerosil silica, 200 m2/g | Not verified / 확인 못 함 |  |
| Compact and sieve silica | Compaction water | Not verified / 확인 못 함 |  |
| Graft Mo-6 | o-Dichlorobenzene for silica suspension | 5 mL |  |
| Graft Mo-6 | Additional Mo-6 solution solvent | Not verified / 확인 못 함 |  |
| Decant and wash with dichlorobenzene | o-Dichlorobenzene | 1 mL |  |
| Wash with toluene | Toluene | 1 mL |  |
| Wash with pentane | n-Pentane | 2 mL |  |

This is a molecular supported metathesis catalyst, not the catalog MoO3/SiO2-Al2O3 oxide formulation. Its reported dry mass is source-specific, not a measured yield of a new user batch. The known Mo-6 aliquot is 78.8/296.0 on a mass basis. The separately prepared silica batch recovery is unreported and still blocks complete proportional allocation. Precursor synthesis starts with named prepared reagents. Unknown solvent additions, setup, washing times and silica quantities prevent a complete manufacturing-cost claim. Unless explicitly reported, recovered dry output remains unknown. Mean electrical demand, attended labor and procurement prices are not established; this is not a cost-complete protocol.

### S87. 0.5Fe/BN1; nominal one-hour mechanochemical specimen

Record: `fe-bn-milled-2024`. Boundary: catalyst_powder.

Source: [Mechanochemically-derived iron atoms on defective boron nitride for stable propylene production](https://doi.org/10.1039/d4ey00123k). [DOI 10.1039/d4ey00123k](https://doi.org/10.1039/d4ey00123k). Locator: Supporting Information p. 1 (PDF p. 2), Catalyst Synthesis. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Charge milling jar | Not quantified | Nominal Fe loading 0.5 wt%; actual precursor masses unreported. 50 cm3 zirconia jar and sixteen 10 mm zirconia balls. |
| Programmed dry milling | Not quantified | Each programmed cycle begins with 30 s at 5 Hz then 10 min at 30 Hz. The specimen label denotes 1 h milling, but the cycle count and inclusion of initial phases in total elapsed time are not specified; no exact elapsed duration or count inferred. |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Charge milling jar | h-BN, 99.5% metal basis | Not verified / 확인 못 함 |  |
| Charge milling jar | Fe(NO3)3·9H2O, >98% | Not verified / 확인 못 함 |  |

No post-synthesis calcination is added to this dry-milled specimen. Frequency is not electrical power. The Fe-decorated material is a source-specific N2O-ODHP variant, not the catalog unmodified h-BN formulation. Cycle setup and nominal treatment labels do not establish measured production time. Unless explicitly reported, recovered dry output remains unknown. Mean electrical demand, attended labor and procurement prices are not established; this is not a cost-complete protocol.

### S88. 0.5Fe/BN-IWI; impregnation comparator

Record: `fe-bn-iwi-2024`. Boundary: catalyst_powder.

Source: [Mechanochemically-derived iron atoms on defective boron nitride for stable propylene production](https://doi.org/10.1039/d4ey00123k). [DOI 10.1039/d4ey00123k](https://doi.org/10.1039/d4ey00123k). Locator: Supporting Information p. 1 (PDF p. 2), Catalyst Synthesis. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare impregnation solution | Not quantified | Nominal Fe loading 0.5 wt%; absolute nitrate and water quantities unreported. |
| Impregnate h-BN | Not quantified | Add solution dropwise to unmodified h-BN. Premilled BN1-IWI is a different preparation. |
| Dry impregnated powder | 79.85 °C; hold unreported h; ramp unreported °C/min; vacuum | 353 K converted to 79.85 °C. Overnight duration is unreported. |
| Calcine impregnated powder | 599.85 °C; hold 5 h; ramp 5 °C/min; static air | 873 K converted to 599.85 °C; 5 K/min temperature increment equals 5 °C/min. |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Prepare impregnation solution | Fe(NO3)3·9H2O, >98% | Not verified / 확인 못 함 |  |
| Prepare impregnation solution | Deionized water | Not verified / 확인 못 함 |  |
| Impregnate h-BN | h-BN, 99.5% metal basis | Not verified / 확인 못 함 |  |

This uses unmodified h-BN, not the separately milled BN1 support or the nitrogen-annealed comparator. Characterization digestion at 533 K and sorption pretreatment at 473 K are excluded from manufacture. Unless explicitly reported, recovered dry output remains unknown. Mean electrical demand, attended labor and procurement prices are not established; this is not a cost-complete protocol.

### S89. AuT100; Au on pure TiO2

Record: `au-t100-2020`. Boundary: catalyst_powder.

Source: [Au-Decorated Ce–Ti Mixed Oxides for Efficient CO Preferential Photooxidation](https://doi.org/10.1021/acsami.0c08258). [DOI 10.1021/acsami.0c08258](https://doi.org/10.1021/acsami.0c08258). Locator: Supporting Information S2-S3: Synthesis of CeO2-TiO2 mixed oxides; Synthesis of Au-NPs/CeO2-TiO2 photocatalysts. Crossref checked: 2026-09-15.

| Operation | Explicit conditions | Source details |
|---|---|---|
| Prepare titania precursor | Intermediate batch: titania | For pure titania, no ceria is added. Reported TTIP 1.9 mmol and acetic acid 19 mmol; no unverified mass conversion. Ice bath has no stated numeric temperature. |
| Basify titania precursor | Intermediate batch: titania | Add 0.3 M K2CO3 at 0.4 mL/min until pH 8.2. Total volume/time unreported; pump flow is not a gas input. |
| Age titania precursor | 20 h; Intermediate batch: titania |  |
| Centrifuge and wash support | Intermediate batch: titania | Durations and wash amounts unreported. |
| Dry titania support | 80 °C; hold unreported h; ramp unreported °C/min; Intermediate batch: titania | Overnight duration unreported. |
| Calcine titania support | 450 °C; hold 5 h; ramp 3 °C/min; Intermediate batch: titania |  |
| Pretreat support aliquot | 100 °C; hold unreported h; ramp unreported °C/min | Use 0.5 g prepared support, pretreated overnight at 100 °C. This duration is not assigned a numeric value. |
| Prepare gold deposition solution | Not quantified | HAuCl4·3H2O amount selected for nominal 1 wt% Au; raise pH to 9 with 0.1 M NaOH at 1 mL/h. Exact salt amount, water and addition time are unreported. |
| Deposit gold | 70 °C; hold 2 h; ramp unreported °C/min | Add pretreated support to alkaline solution under stirring; maintain approximately pH 9 during 2 h at 70 °C. |
| Wash supported gold | Not quantified | Rinse until chloride disappearance by AgNO3 test; no fixed wash count. Test reagent is tracked separately with unknown amount. |
| Dry Au/TiO2 | 100 °C; hold unreported h; ramp unreported °C/min | Overnight duration unreported. |
| Calcine Au/TiO2 | 200 °C; hold 4 h; ramp 2 °C/min; flowing air |  |

Intermediate transfers (recovery is not inferred from precursor inputs):

| Intermediate / destination | Recovered kg | Used kg | Source details |
|---|---|---|---|
| Prepared pure titania support / final batch | Not verified / 확인 못 함 | 0.0005 |  |

Explicit purchases/inputs (unpriced; missing amounts remain unknown):

| Operation | Material | Amount | Note |
|---|---|---|---|
| Prepare titania precursor | Titanium isopropoxide, 97% | 1.9 mmol |  |
| Prepare titania precursor | Glacial acetic acid | 19 mmol |  |
| Basify titania precursor | K2CO3 solution, 0.3 M | Not verified / 확인 못 함 |  |
| Centrifuge and wash support | Deionized wash water | Not verified / 확인 못 함 |  |
| Prepare gold deposition solution | HAuCl4·3H2O, 99.9% | Not verified / 확인 못 함 |  |
| Prepare gold deposition solution | Milli-Q water | Not verified / 확인 못 함 |  |
| Prepare gold deposition solution | NaOH solution, 0.1 M | Not verified / 확인 못 함 |  |
| Wash supported gold | Milli-Q wash water | Not verified / 확인 못 함 |  |
| Wash supported gold | AgNO3 chloride test reagent | Not verified / 확인 못 함 |  |

Selected T100 is explicitly pure titania. Mixed CT labels conflict with stated Ce/Ti loading descriptions, so no mixed-oxide composition or amount is inferred. The source does not establish how the initial support synthesis was scaled or repeated to supply the 0.5 g support aliquot. A single stated precursor charge is not assumed to produce that mass. 1 wt% Au is a nominal target. This photo-PROX specimen does not establish an industrial low-temperature PROX formulation or matched performance. Unless explicitly reported, recovered dry output remains unknown. Mean electrical demand, attended labor and procurement prices are not established; this is not a cost-complete protocol.

## Operating references

These public references retain geography, period, quantity basis and source locator. Only electricity averages can be applied directly as explicit scenarios. Wage-only statistics and equipment connected loads remain reference information. No reference substitutes for measured batch electricity, actual gas conditions, staffing or a supplier quotation. The source texts and manuals are not redistributed.

| Reference | Value | Scope | Source |
|---|---|---|---|
| US industrial electricity, 2025 (preliminary) | 0.0862 USD/kWh | National retail average, not a facility tariff or live quote. Source 8.62 US cents/kWh divided by 100. Review demand charges, customer class and location against the actual bill. | [U.S. EIA, Electricity explained: Prices and factors affecting prices](https://www.eia.gov/energyexplained/electricity/prices-and-factors-affecting-prices.php); 2025 annual average retail prices by customer type; footnote 1, Electric Power Monthly Table 5.3, February 2026 (preliminary); accessed 2026-09-15 |
| US commercial electricity, 2025 (preliminary) | 0.1341 USD/kWh | National commercial retail average. Laboratory electricity contracts may use different customer classes and charges. Source 13.41 US cents/kWh divided by 100. | [U.S. EIA, Electricity explained: Prices and factors affecting prices](https://www.eia.gov/energyexplained/electricity/prices-and-factors-affecting-prices.php); 2025 annual average retail prices by customer type; footnote 1, Electric Power Monthly Table 5.3, February 2026 (preliminary); accessed 2026-09-15 |
| US chemical technicians, May 2023 mean wage | 29.29 USD/person-hour | Occupation 19-4031, national mean wage. This is a historical wage, not a current fully loaded labor rate. Employer nonwage benefits are excluded by OEWS; staffing, benefits and price-year adjustments require a separate basis. | [U.S. BLS, Occupational Employment and Wages, May 2023: 19-4031 Chemical Technicians](https://www.bls.gov/oes/2023/may/oes194031.htm); National estimates, mean hourly wage; OEWS FAQ, wage definitions; accessed 2026-09-15 |
| Nabertherm L 9/11/SKM, connected load (web specification) | 3.7 kW rated connected load | 9 L, Tmax 1100 °C; recommended long holds up to 1000 °C. Connected load is not measured average input power. Options and supply voltage affect the rating. The 2024 operating manual lists 3.4 kW for the same model name; confirm the actual unit's version and nameplate. | [Nabertherm, muffle furnaces with embedded heating elements in the ceramic muffle up to 1100 °C](https://nabertherm.com/es/productos/labor/hornos-de-mufla/hornos-de-mufla-con-elementos-calefactores-integrados-en-la-mufla); Especificaciones técnicas, L 9/11/SKM row and footnotes 1, 5; accessed 2026-09-15 |
| Nabertherm L 9/11/SKM, connected load (2024 manual) | 3.4 kW rated connected load | Manual p. 25, L 9/11/SKM: 9 L, Tmax 1100 °C, connected load 3.4 kW. This differs from the current web table's 3.7 kW. Neither value is measured average consumption for a catalyst recipe. | [Nabertherm Operating Instructions, M01.1060 English, 2024-07](https://nabertherm.com/sites/default/files/noindex/2025-03/M01.1060_English_2024-07.pdf); p. 25, muffle furnace L 9/11/SKM technical table; accessed 2026-09-15 |

## Input provenance

Explicit numeric preparation values carry per-field source snapshots in the JSON library. The stored value, DOI, locator and review date survive import, editing, saving and export. An edit preserves the source value and is flagged as modified; it does not become a published value. Publication metadata verification, source transcription and actual operating measurements are separate evidence levels. Library imports do not populate unknown prices or dry output mass.

## Generic templates

All templates remain generic cost sequences, not source-verified experimental preparations.

- `aem_fuel_cell_ccm`: AEM Fuel Cell CCM / GDE Route
- `alkaline_electrolyzer_gde`: Alkaline Electrolyzer Electrode Route
- `colloidal_nanoparticle_deposition`: Colloidal / Polyol Nanoparticle Synthesis with Deposition
- `combustion_synthesis_mixed_oxide`: Solution Combustion Synthesis - Mixed Oxide
- `coprecipitation_metal_oxide`: Co-precipitation - Metal on Oxide Support
- `custom_step_process`: Custom Step Process
- `deposition_precipitation_metal_oxide`: Deposition-Precipitation - Metal on Oxide Support
- `dmfc_gde_route`: DMFC Anode GDE / CCM Route
- `excess_solution_impregnation_metal_oxide`: Excess-Solution (Wet) Impregnation - Metal on Oxide Support
- `fcc_catalyst_usy_w_re`: FCC Catalyst (USY w/ RE)
- `fusion_promoted_magnetite`: Oxide-Melt Fusion - Promoted Magnetite
- `hydrothermal_oxide_nanostructure`: Hydrothermal / Solvothermal Synthesis - Bulk Oxide
- `ion_exchange_zeolite_metal`: Ion Exchange - Metal into Zeolite
- `magnesia_alumina`: Magnesia/Alumina
- `metal_carbide_bulk`: Metal Carbide (Bulk)
- `metal_carbide_on_metal_oxide`: Metal Carbide on Metal Oxide
- `metal_earth_abundant_on_metal_oxide`: Metal (Earth Abundant) on Metal Oxide
- `metal_pgm_carbon`: PGM on Carbon Support
- `metal_pgm_on_carbon`: Metal (PGM) on Carbon
- `metal_pgm_on_metal_oxide`: Metal (PGM) on Metal Oxide
- `pem_electrolyzer_ccm`: PEM Electrolyzer CCM Route
- `pem_fuel_cell_ccm`: PEM Fuel Cell CCM / MEA Route
- `reduction_activation_addon`: Activation - Gas-Phase Reduction (H2)
- `shaping_extrusion_pelletizing`: Shaping - Extrudates, Pellets and Spheres
- `sol_gel_metal_oxide`: Sol-Gel - Metal on Oxide Support
- `solid_state_mechanochemical`: Solid-State / Mechanochemical Synthesis - Bulk Oxide or Nitride
- `sulfidation_hydrotreating`: Impregnation with Sulfidation - Hydrotreating Catalysts
- `washcoat_monolith`: Washcoating - Catalyst on Monolith / Honeycomb
- `wet_impregnation_metal_oxide`: Incipient Wetness Impregnation - Metal on Oxide Support
- `zeolite_beta_bulk`: Zeolite Beta (Bulk)
- `zeolite_beta_with_metal_active_site`: Zeolite Beta with Metal Active Site
- `zeolite_fcc`: FCC Catalyst (Zeolite-based)
- `zeolite_zsm_5_2025_pct`: Zeolite ZSM-5 (20–25%)
- `zeolite_zsm_5_bulk`: Zeolite ZSM-5 (Bulk)

## Bibliographic and access inventory

Access flags indicate a retrieved public full text or PDF supplement; they do not indicate that its Methods were curated. No source article, supporting PDF or private author attachment is redistributed. All source materials retain their own terms.

| DOI and title | Public full text | Public supplement | Method record |
|---|---|---|---|
| [Ammonia, 2. Production Processes](https://doi.org/10.1002/14356007.o02_o11) — 10.1002/14356007.o02_o11 | Not verified | Not verified | Not verified |
| [Methanol Synthesis](https://doi.org/10.1002/9783527610044.hetcat0148) — 10.1002/9783527610044.hetcat0148 | Not verified | Not verified | Not verified |
| [Silica‐Alumina‐Supported, Tungsten‐Based Heterogeneous Alkane Metathesis Catalyst: Is it Closer to a Silica‐ or an Alumina‐Supported System?](https://doi.org/10.1002/adsc.200600436) — 10.1002/adsc.200600436 | Not verified | Not verified | Not verified |
| [Cost‐Responsive Optimization of Nickel Nanoparticle Synthesis](https://doi.org/10.1002/adsu.202300030) — 10.1002/adsu.202300030 | Yes | Not verified | Yes |
| [Development and Recent Progress on Ammonia Synthesis Catalysts for Haber–Bosch Process](https://doi.org/10.1002/aesr.202000043) — 10.1002/aesr.202000043 | Not verified | Not verified | Not verified |
| [PtZn intermetallic nanoalloy encapsulated in silicalite‐1 for propane dehydrogenation](https://doi.org/10.1002/aic.17295) — 10.1002/aic.17295 | Not verified | Not verified | Not verified |
| [Methane steam reforming, methanation and water‐gas shift: I. Intrinsic kinetics](https://doi.org/10.1002/aic.690350109) — 10.1002/aic.690350109 | Not verified | Not verified | Not verified |
| [Understanding the Failure of Direct CC Coupling in the Zeolite‐Catalyzed Methanol‐to‐Olefin Process](https://doi.org/10.1002/anie.200503824) — 10.1002/anie.200503824 | Not verified | Not verified | Not verified |
| [Direct Transformation of Ethylene into Propylene Catalyzed by a Tungsten Hydride Supported on Alumina: Trifunctional Single‐Site Catalysis](https://doi.org/10.1002/anie.200701199) — 10.1002/anie.200701199 | Not verified | Not verified | Not verified |
| [Controlled Generation of Hydrogen from Formic Acid Amine Adducts at Room Temperature and Application in H2/O2 Fuel Cells](https://doi.org/10.1002/anie.200705972) — 10.1002/anie.200705972 | Not verified | Not verified | Not verified |
| [The Haber–Bosch Process Revisited: On the Real Structure and Stability of “Ammonia Iron” under Working Conditions](https://doi.org/10.1002/anie.201305812) — 10.1002/anie.201305812 | Not verified | Not verified | Not verified |
| [Highly Efficient Photocatalytic H2 Evolution from Water using Visible Light and Structure‐Controlled Graphitic Carbon Nitride](https://doi.org/10.1002/anie.201403375) — 10.1002/anie.201403375 | Yes | Yes | Not verified |
| [Hierarchical NiCo                     2                     O                     4                     Hollow Microcuboids as Bifunctional Electrocatalysts for Overall Water‐Splitting](https://doi.org/10.1002/anie.201600525) — 10.1002/anie.201600525 | Not verified | Not verified | Not verified |
| [Self‐organized Ruthenium–Barium Core–Shell Nanoparticles on a Mesoporous Calcium Amide Matrix for Efficient Low‐Temperature Ammonia Synthesis](https://doi.org/10.1002/anie.201712398) — 10.1002/anie.201712398 | Not verified | Not verified | Not verified |
| [Selective Hydrogenation and Hydrodeoxygenation of Aromatic Ketones to Cyclohexane Derivatives Using a Rh@SILP Catalyst](https://doi.org/10.1002/anie.201916385) — 10.1002/anie.201916385 | Yes | Yes | Not verified |
| [Why Boron Nitride is such a Selective Catalyst for the Oxidative Dehydrogenation of Propane](https://doi.org/10.1002/anie.202003695) — 10.1002/anie.202003695 | Not verified | Not verified | Not verified |
| [Mechanistic Study of Carbon Dioxide Hydrogenation over Pd/ZnO‐Based Catalysts: The Role of Palladium–Zinc Alloy in Selective Methanol Synthesis](https://doi.org/10.1002/anie.202103087) — 10.1002/anie.202103087 | Yes | Yes | Yes |
| [Shape‐Selective Conversion of Methanol to Hydrocarbons Over 10‐Ring Unidirectional‐Channel Acidic H‐ZSM‐22](https://doi.org/10.1002/cctc.200900057) — 10.1002/cctc.200900057 | Not verified | Not verified | Not verified |
| [Shape‐ and Size‐Specific Chemistry of Ag Nanostructures in Catalytic Ethylene Epoxidation](https://doi.org/10.1002/cctc.200900231) — 10.1002/cctc.200900231 | Not verified | Not verified | Not verified |
| [Ethylene Epoxidation Catalyzed by Silver Oxide](https://doi.org/10.1002/cctc.201000249) — 10.1002/cctc.201000249 | Not verified | Not verified | Not verified |
| [Mechanism of the Catalytic Oxidation of Glycerol on Polycrystalline Gold and Platinum Electrodes](https://doi.org/10.1002/cctc.201100023) — 10.1002/cctc.201100023 | Not verified | Not verified | Not verified |
| [Dehydrogenation of Propane over Silica‐Supported Platinum–Tin Catalysts Prepared by Direct Reduction: Effects of Tin/Platinum Ratio and Reduction Temperature](https://doi.org/10.1002/cctc.201402306) — 10.1002/cctc.201402306 | Not verified | Not verified | Not verified |
| [Ordered Mesoporous Materials as Supports for Stable Iron Catalysts in the Fischer–Tropsch Synthesis of Lower Olefins](https://doi.org/10.1002/cctc.201600492) — 10.1002/cctc.201600492 | Not verified | Not verified | Not verified |
| [Tailoring Single‐Atom Platinum for Selective and Stable Catalysts in Propane Dehydrogenation](https://doi.org/10.1002/cplu.202100560) — 10.1002/cplu.202100560 | Not verified | Not verified | Not verified |
| [An Overview of Glycerol Electrooxidation Mechanisms on Pt, Pd and Au](https://doi.org/10.1002/cssc.202002669) — 10.1002/cssc.202002669 | Not verified | Not verified | Not verified |
| [Gold–Indium Electrocatalysts for the Selective Oxidation of Glycerol Coupled with CO 2 Reduction](https://doi.org/10.1002/cssc.202402378) — 10.1002/cssc.202402378 | Yes | Not verified | Yes |
| [Sustainion Imidazolium‐Functionalized Polymers for Carbon Dioxide Electrolysis](https://doi.org/10.1002/ente.201600636) — 10.1002/ente.201600636 | Not verified | Not verified | Not verified |
| [Influence of Support Type and Metal Loading in Methane Decomposition over Iron Catalyst for Hydrogen Production](https://doi.org/10.1002/jccs.201500052) — 10.1002/jccs.201500052 | Not verified | Not verified | Not verified |
| [Hydrogen Production via Methane Decomposition over Alumina Doped with Titanium Oxide‐Supported Iron Catalyst for Various Calcination Temperatures](https://doi.org/10.1002/open.202300173) — 10.1002/open.202300173 | Yes | Yes | Yes |
| [Carbon Monoxide Removal from Hydrogen-Rich Fuel Cell Feedstreams by Selective Catalytic Oxidation](https://doi.org/10.1006/jcat.1993.1205) — 10.1006/jcat.1993.1205 | Not verified | Not verified | Not verified |
| [Low-Temperature Oxidation of CO over Gold Supported on TiO2, α-Fe2O3, and Co3O4](https://doi.org/10.1006/jcat.1993.1322) — 10.1006/jcat.1993.1322 | Not verified | Not verified | Not verified |
| [Kinetics of the Selective CO Oxidation in H2-Rich Gas on Pt/Al2O3](https://doi.org/10.1006/jcat.1997.1781) — 10.1006/jcat.1997.1781 | Not verified | Not verified | Not verified |
| [Kinetics of the Selective Low-Temperature Oxidation of CO in H2-Rich Gas over Au/α-Fe2O3](https://doi.org/10.1006/jcat.1998.2333) — 10.1006/jcat.1998.2333 | Not verified | Not verified | Not verified |
| [Catalytic Performance of Fe–ZSM-5 Catalysts for Selective Catalytic Reduction of Nitric Oxide by Ammonia](https://doi.org/10.1006/jcat.1999.2674) — 10.1006/jcat.1999.2674 | Not verified | Not verified | Not verified |
| [The Genesis and Development of the Commercial BP Doubly Promoted Catalyst for Ammonia Synthesis](https://doi.org/10.1007/s10562-014-1226-4) — 10.1007/s10562-014-1226-4 | Not verified | Not verified | Not verified |
| [Current Understanding of Cu-Exchanged Chabazite Molecular Sieves for Use as Commercial Diesel Engine DeNOx Catalysts](https://doi.org/10.1007/s11244-013-0145-8) — 10.1007/s11244-013-0145-8 | Not verified | Not verified | Not verified |
| [Cobalt Particle Size Effects in the Fischer–Tropsch Synthesis and in the Hydrogenation of CO2 Studied with Nanoparticle Model Catalysts on Silica](https://doi.org/10.1007/s11244-013-0206-z) — 10.1007/s11244-013-0206-z | Not verified | Not verified | Not verified |
| [Water effect on the new catalyst of high temperature shift conversion during first reduction](https://doi.org/10.1007/s13203-018-0222-9) — 10.1007/s13203-018-0222-9 | Not verified | Not verified | Not verified |
| [Carbon dioxide reforming of methane over nickel/alkaline earth metal oxide catalysts](https://doi.org/10.1016/0926-860x(95)00201-4) — 10.1016/0926-860x(95)00201-4 | Not verified | Not verified | Not verified |
| [Development of copper/zinc oxide-based multicomponent catalysts for methanol synthesis from carbon dioxide and hydrogen](https://doi.org/10.1016/0926-860x(95)00305-3) — 10.1016/0926-860x(95)00305-3 | Not verified | Not verified | Not verified |
| [Kinetics of steam reforming of methane on Ru/Al2O3 catalyst promoted with Mn oxides](https://doi.org/10.1016/j.apcata.2004.12.003) — 10.1016/j.apcata.2004.12.003 | Not verified | Not verified | Not verified |
| [Properties and metathesis activity of molybdena-alumina, molybdena-silica-alumina and molybdena-silica catalysts—a comparative study](https://doi.org/10.1016/j.apcata.2006.07.002) — 10.1016/j.apcata.2006.07.002 | Not verified | Not verified | Not verified |
| [Promoters state and catalyst activation during ammonia synthesis over Ru/C](https://doi.org/10.1016/j.apcata.2007.02.022) — 10.1016/j.apcata.2007.02.022 | Not verified | Not verified | Not verified |
| [Selective hydrogenation of acetylene in the presence of ethylene on K+-β-zeolite supported Pd and PdAg catalysts](https://doi.org/10.1016/j.apcata.2007.09.017) — 10.1016/j.apcata.2007.09.017 | Not verified | Not verified | Not verified |
| [Synthesis of CNT-supported cobalt nanoparticle catalysts using a microemulsion technique: Role of nanoparticle size on reducibility, activity and selectivity in Fischer–Tropsch reactions](https://doi.org/10.1016/j.apcata.2009.11.029) — 10.1016/j.apcata.2009.11.029 | Not verified | Not verified | Not verified |
| [Hydrodeoxygenation of guaiacol as a model compound of bio-oil in methanol over mesoporous noble metal catalysts](https://doi.org/10.1016/j.apcata.2018.01.008) — 10.1016/j.apcata.2018.01.008 | Not verified | Not verified | Not verified |
| [Enhancement of catalytic properties for glycerol electrooxidation on Pt and Pd nanoparticles induced by Bi surface modification](https://doi.org/10.1016/j.apcatb.2011.08.020) — 10.1016/j.apcatb.2011.08.020 | Not verified | Not verified | Not verified |
| [Fe catalysts for methane decomposition to produce hydrogen and carbon nano materials](https://doi.org/10.1016/j.apcatb.2017.02.052) — 10.1016/j.apcatb.2017.02.052 | Not verified | Not verified | Not verified |
| [CO2 hydrogenation to methanol over Pd/In2O3: effects of Pd and oxygen vacancy](https://doi.org/10.1016/j.apcatb.2017.06.069) — 10.1016/j.apcatb.2017.06.069 | Not verified | Not verified | Not verified |
| [PdAg alloy nanoparticles encapsulated in N-doped microporous hollow carbon spheres for hydrogenation of CO2 to formate](https://doi.org/10.1016/j.apcatb.2020.119628) — 10.1016/j.apcatb.2020.119628 | Not verified | Not verified | Not verified |
| [Cu+–Ti3+ interface interaction mediated CO2 coordination model for controlling the selectivity of photocatalytic reduction CO2](https://doi.org/10.1016/j.apcatb.2021.120803) — 10.1016/j.apcatb.2021.120803 | Not verified | Not verified | Not verified |
| [Surface modification and enhanced photocatalytic CO2 reduction performance of TiO2: a review](https://doi.org/10.1016/j.apsusc.2016.09.093) — 10.1016/j.apsusc.2016.09.093 | Not verified | Not verified | Not verified |
| [Selective ethanol formation from photocatalytic reduction of carbon dioxide in water with BiVO4 photocatalyst](https://doi.org/10.1016/j.catcom.2009.10.010) — 10.1016/j.catcom.2009.10.010 | Not verified | Not verified | Not verified |
| [Selective methanol production from photocatalytic reduction of CO2 on BiVO4 under visible light irradiation](https://doi.org/10.1016/j.catcom.2012.08.008) — 10.1016/j.catcom.2012.08.008 | Not verified | Not verified | Not verified |
| [Catalytic activity of carbons for methane decomposition reaction](https://doi.org/10.1016/j.cattod.2005.02.018) — 10.1016/j.cattod.2005.02.018 | Not verified | Not verified | Not verified |
| [Four challenges for nickel steam-reforming catalysts](https://doi.org/10.1016/j.cattod.2005.10.002) — 10.1016/j.cattod.2005.10.002 | Not verified | Not verified | Not verified |
| [Recent progress in selective CO removal in a H2-rich stream](https://doi.org/10.1016/j.cattod.2008.06.027) — 10.1016/j.cattod.2008.06.027 | Not verified | Not verified | Not verified |
| [Fischer-Tropsch synthesis: Relations between structure of cobalt catalysts and their catalytic performance](https://doi.org/10.1016/j.cattod.2008.10.036) — 10.1016/j.cattod.2008.10.036 | Not verified | Not verified | Not verified |
| [Hydrodeoxygenation of guaiacol on noble metal catalysts](https://doi.org/10.1016/j.cattod.2008.10.037) — 10.1016/j.cattod.2008.10.037 | Not verified | Not verified | Not verified |
| [Dehydrogenation of propane over Pt-SBA-15 and Pt-Sn-SBA-15: Effect of Sn on the dispersion of Pt and catalytic behavior](https://doi.org/10.1016/j.cattod.2009.01.002) — 10.1016/j.cattod.2009.01.002 | Not verified | Not verified | Not verified |
| [Catalytic CO2 valorization into CH4 on Ni-based ceria-zirconia. Reaction mechanism by operando IR spectroscopy](https://doi.org/10.1016/j.cattod.2013.02.019) — 10.1016/j.cattod.2013.02.019 | Not verified | Not verified | Not verified |
| [CO-insertion mechanism based kinetic model of the Fischer–Tropsch synthesis reaction over Re-promoted Co catalyst](https://doi.org/10.1016/j.cattod.2013.08.008) — 10.1016/j.cattod.2013.08.008 | Not verified | Not verified | Not verified |
| [Development and application of wüstite-based ammonia synthesis catalysts](https://doi.org/10.1016/j.cattod.2019.10.031) — 10.1016/j.cattod.2019.10.031 | Not verified | Not verified | Not verified |
| [Recent progress for reversible homogeneous catalytic hydrogen storage in formic acid and in methanol](https://doi.org/10.1016/j.ccr.2017.11.021) — 10.1016/j.ccr.2017.11.021 | Not verified | Not verified | Not verified |
| [Electrochemical reduction of CO2 to formate in aqueous solution using electro-deposited Sn catalysts](https://doi.org/10.1016/j.cej.2016.02.084) — 10.1016/j.cej.2016.02.084 | Not verified | Not verified | Not verified |
| [Fischer-Tropsch Synthesis Steps into the Solar Era: Lower Olefins from Syngas](https://doi.org/10.1016/j.chempr.2018.11.020) — 10.1016/j.chempr.2018.11.020 | Not verified | Not verified | Not verified |
| [Iridium Single-Atom Catalyst Performing a Quasi-homogeneous Hydrogenation Transformation of CO2 to Formate](https://doi.org/10.1016/j.chempr.2018.12.014) — 10.1016/j.chempr.2018.12.014 | Not verified | Not verified | Not verified |
| [Bi-modified palladium nanocubes for glycerol electrooxidation](https://doi.org/10.1016/j.elecom.2013.07.022) — 10.1016/j.elecom.2013.07.022 | Not verified | Not verified | Not verified |
| [Review on methanation – From fundamentals to current projects](https://doi.org/10.1016/j.fuel.2015.10.111) — 10.1016/j.fuel.2015.10.111 | Not verified | Not verified | Not verified |
| [Hydrogen production by catalytic decomposition of methane over Ni/SiO2Ni/SiO2☆](https://doi.org/10.1016/j.ijhydene.2007.01.007) — 10.1016/j.ijhydene.2007.01.007 | Not verified | Not verified | Not verified |
| [Study of the deactivation mechanism of carbon blacks used in methane decomposition](https://doi.org/10.1016/j.ijhydene.2008.05.072) — 10.1016/j.ijhydene.2008.05.072 | Not verified | Not verified | Not verified |
| [Ni/CeO2 catalysts with high CO2 methanation activity and high CH4 selectivity at low temperatures](https://doi.org/10.1016/j.ijhydene.2011.12.122) — 10.1016/j.ijhydene.2011.12.122 | Not verified | Not verified | Not verified |
| [Glycerol electrooxidation on Pd, Pt and Au nanoparticles supported on carbon ceramic electrode in alkaline media](https://doi.org/10.1016/j.ijhydene.2012.08.127) — 10.1016/j.ijhydene.2012.08.127 | Not verified | Not verified | Not verified |
| [Methane decomposition over iron catalyst for hydrogen production](https://doi.org/10.1016/j.ijhydene.2014.10.058) — 10.1016/j.ijhydene.2014.10.058 | Not verified | Not verified | Not verified |
| [Hydrogen production by ammonia decomposition using Co catalyst supported on Mg mixed oxide systems](https://doi.org/10.1016/j.ijhydene.2015.09.057) — 10.1016/j.ijhydene.2015.09.057 | Not verified | Not verified | Not verified |
| [Hydrogen production from ammonia decomposition using Co/γ-Al2O3 catalysts – Insights into the effect of synthetic method](https://doi.org/10.1016/j.ijhydene.2020.07.090) — 10.1016/j.ijhydene.2020.07.090 | Not verified | Not verified | Not verified |
| [Ethylene epoxidation over silver and copper–silver bimetallic catalysts: II. Cs and Cl promotion](https://doi.org/10.1016/j.jcat.2005.10.017) — 10.1016/j.jcat.2005.10.017 | Not verified | Not verified | Not verified |
| [Ethylene epoxidation over silver and copper–silver bimetallic catalysts: I. Kinetics and selectivity](https://doi.org/10.1016/j.jcat.2005.10.018) — 10.1016/j.jcat.2005.10.018 | Not verified | Not verified | Not verified |
| [Pulse-response TAP studies of the reverse water–gas shift reaction over a Pt/CeO2 catalyst](https://doi.org/10.1016/j.jcat.2005.10.020) — 10.1016/j.jcat.2005.10.020 | Not verified | Not verified | Not verified |
| [Promotion of the long-term stability of reforming Ni catalysts by surface alloying](https://doi.org/10.1016/j.jcat.2007.04.020) — 10.1016/j.jcat.2007.04.020 | Not verified | Not verified | Not verified |
| [Development of stable bimetallic catalysts for carbon dioxide reforming of methane](https://doi.org/10.1016/j.jcat.2007.05.004) — 10.1016/j.jcat.2007.05.004 | Not verified | Not verified | Not verified |
| [Cobalt species in promoted cobalt alumina-supported Fischer–Tropsch catalysts](https://doi.org/10.1016/j.jcat.2007.09.018) — 10.1016/j.jcat.2007.09.018 | Not verified | Not verified | Not verified |
| [Correlations between synthesis, precursor, and catalyst structure and activity of a large set of CuO/ZnO/Al2O3 catalysts for methanol synthesis](https://doi.org/10.1016/j.jcat.2008.07.004) — 10.1016/j.jcat.2008.07.004 | Not verified | Not verified | Not verified |
| [First principles calculations and experimental insight into methane steam reforming over transition metal catalysts](https://doi.org/10.1016/j.jcat.2008.08.003) — 10.1016/j.jcat.2008.08.003 | Not verified | Not verified | Not verified |
| [Excellent activity and selectivity of Cu-SSZ-13 in the selective catalytic reduction of NOx with NH3](https://doi.org/10.1016/j.jcat.2010.07.031) — 10.1016/j.jcat.2010.07.031 | Not verified | Not verified | Not verified |
| [Influence of particle size on the activity and stability in steam methane reforming of supported Rh nanoparticles](https://doi.org/10.1016/j.jcat.2011.03.015) — 10.1016/j.jcat.2011.03.015 | Not verified | Not verified | Not verified |
| [Comparative study of hydrotalcite-derived supported Pd2Ga and PdZn intermetallic nanoparticles as methanol synthesis and methanol steam reforming catalysts](https://doi.org/10.1016/j.jcat.2012.05.020) — 10.1016/j.jcat.2012.05.020 | Not verified | Not verified | Not verified |
| [Zinc inclusion to heterogeneous nickel catalysts reduces oligomerization during the semi-hydrogenation of acetylene](https://doi.org/10.1016/j.jcat.2014.05.007) — 10.1016/j.jcat.2014.05.007 | Not verified | Not verified | Not verified |
| [Kinetics and mechanism of m-cresol hydrodeoxygenation on a Pt/SiO2 catalyst](https://doi.org/10.1016/j.jcat.2014.05.024) — 10.1016/j.jcat.2014.05.024 | Not verified | Not verified | Not verified |
| [An investigation on the role of Re as a promoter in Ag Cs Re/α-Al 2 O 3 high-selectivity, ethylene epoxidation catalysts](https://doi.org/10.1016/j.jcat.2014.11.007) — 10.1016/j.jcat.2014.11.007 | Not verified | Not verified | Not verified |
| [Methanation of CO2: Structural response of a Ni-based catalyst under fluctuating reaction conditions unraveled by operando spectroscopy](https://doi.org/10.1016/j.jcat.2015.04.006) — 10.1016/j.jcat.2015.04.006 | Not verified | Not verified | Not verified |
| [Methylbenzene hydrocarbon pool in methanol-to-olefins conversion over zeolite H-ZSM-5](https://doi.org/10.1016/j.jcat.2015.10.001) — 10.1016/j.jcat.2015.10.001 | Not verified | Not verified | Not verified |
| [Pd/ZnO catalysts for direct CO2 hydrogenation to methanol](https://doi.org/10.1016/j.jcat.2016.03.017) — 10.1016/j.jcat.2016.03.017 | Not verified | Not verified | Not verified |
| [A direct Z-scheme g-C3N4/SnS2 photocatalyst with superior visible-light CO2 reduction performance](https://doi.org/10.1016/j.jcat.2017.06.006) — 10.1016/j.jcat.2017.06.006 | Not verified | Not verified | Not verified |
| [Propane dehydrogenation over supported Pt-Sn nanoparticles](https://doi.org/10.1016/j.jcat.2018.09.006) — 10.1016/j.jcat.2018.09.006 | Not verified | Not verified | Not verified |
| [Industrial and scientific directions of methanol catalyst development](https://doi.org/10.1016/j.jcat.2019.02.002) — 10.1016/j.jcat.2019.02.002 | Not verified | Not verified | Not verified |
| [Photocatalytic reduction of CO2 over a hybrid photocatalyst composed of WO3 and graphitic carbon nitride (g-C3N4) under visible light](https://doi.org/10.1016/j.jcou.2014.02.002) — 10.1016/j.jcou.2014.02.002 | Not verified | Not verified | Not verified |
| [CO2 valorisation via Reverse Water-Gas Shift reaction using advanced Cs doped Fe-Cu/Al2O3 catalysts](https://doi.org/10.1016/j.jcou.2017.08.009) — 10.1016/j.jcou.2017.08.009 | Not verified | Not verified | Not verified |
| [Compact hollow fibre reactors for efficient methane conversion](https://doi.org/10.1016/j.jeurceramsoc.2017.04.011) — 10.1016/j.jeurceramsoc.2017.04.011 | Not verified | Not verified | Not verified |
| [Natural gas to synthesis gas – Catalysts and catalytic processes](https://doi.org/10.1016/j.jngse.2011.03.004) — 10.1016/j.jngse.2011.03.004 | Not verified | Not verified | Not verified |
| [A Particulate Photocatalyst Water-Splitting Panel for Large-Scale Solar Hydrogen Generation](https://doi.org/10.1016/j.joule.2017.12.009) — 10.1016/j.joule.2017.12.009 | Not verified | Not verified | Not verified |
| [Understanding Continuous Lithium-Mediated Electrochemical Nitrogen Reduction](https://doi.org/10.1016/j.joule.2019.02.003) — 10.1016/j.joule.2019.02.003 | Not verified | Not verified | Not verified |
| [Electrosynthesis of ammonia with high selectivity and high rates via engineering of the solid-electrolyte interphase](https://doi.org/10.1016/j.joule.2022.07.009) — 10.1016/j.joule.2022.07.009 | Yes | Yes | Yes |
| [Membrane electrode assembly: Another technical roadmap for lithium-mediated nitrogen reduction?](https://doi.org/10.1016/j.joule.2023.07.019) — 10.1016/j.joule.2023.07.019 | Not verified | Not verified | Not verified |
| [Review of material design and reactor engineering on TiO2 photocatalysis for CO2 reduction](https://doi.org/10.1016/j.jphotochemrev.2015.06.001) — 10.1016/j.jphotochemrev.2015.06.001 | Not verified | Not verified | Not verified |
| [Accelerated optochemical engineering solutions to CO2 photocatalysis for a sustainable future](https://doi.org/10.1016/j.matt.2022.07.033) — 10.1016/j.matt.2022.07.033 | Not verified | Not verified | Not verified |
| [Origin of enhanced ethylene oxide selectivity by Cs-promoted silver catalyst](https://doi.org/10.1016/j.mcat.2017.08.007) — 10.1016/j.mcat.2017.08.007 | Not verified | Not verified | Not verified |
| [Zirconia phase effect in Pd/ZrO2 catalyzed CO2 hydrogenation into formate](https://doi.org/10.1016/j.mcat.2019.110461) — 10.1016/j.mcat.2019.110461 | Not verified | Not verified | Not verified |
| [Selectivity control through fundamental mechanistic insight in the conversion of methanol to hydrocarbons over zeolites](https://doi.org/10.1016/j.micromeso.2010.07.013) — 10.1016/j.micromeso.2010.07.013 | Not verified | Not verified | Not verified |
| [Industrial applications of olefin metathesis](https://doi.org/10.1016/j.molcata.2003.10.049) — 10.1016/j.molcata.2003.10.049 | Not verified | Not verified | Not verified |
| [Nitrogen doping of indium oxide for enhanced photocatalytic reduction of CO2 to methanol](https://doi.org/10.1016/j.nanoen.2022.107613) — 10.1016/j.nanoen.2022.107613 | Not verified | Not verified | Not verified |
| [Efficient methanol synthesis: Perspectives, technologies and optimization strategies](https://doi.org/10.1016/j.pecs.2016.06.001) — 10.1016/j.pecs.2016.06.001 | Not verified | Not verified | Not verified |
| [Construction of a reaction coordinate and a microkinetic model for ethylene epoxidation on silver from DFT calculations and surface science experiments](https://doi.org/10.1016/s0021-9517(02)00156-2) — 10.1016/s0021-9517(02)00156-2 | Not verified | Not verified | Not verified |
| [Synthesis of Methanol](https://doi.org/10.1016/s0166-9834(00)80103-7) — 10.1016/s0166-9834(00)80103-7 | Not verified | Not verified | Not verified |
| [Hydrogen and synthesis gas by steam- and C02 reforming](https://doi.org/10.1016/s0360-0564(02)47006-x) — 10.1016/s0360-0564(02)47006-x | Not verified | Not verified | Not verified |
| [Hydrogen production by catalytic decomposition of methane over activated carbons: kinetic study](https://doi.org/10.1016/s0360-3199(03)00111-3) — 10.1016/s0360-3199(03)00111-3 | Not verified | Not verified | Not verified |
| [Selective catalytic oxidation of CO in H2: fuel cell applications](https://doi.org/10.1016/s0920-5861(00)00426-0) — 10.1016/s0920-5861(00)00426-0 | Not verified | Not verified | Not verified |
| [The Fischer–Tropsch process: 1950–2000](https://doi.org/10.1016/s0920-5861(01)00453-9) — 10.1016/s0920-5861(01)00453-9 | Not verified | Not verified | Not verified |
| [A comparative study of Pt/γ-Al2O3, Au/α-Fe2O3 and CuO–CeO2 catalysts for the selective oxidation of carbon monoxide in excess hydrogen](https://doi.org/10.1016/s0920-5861(02)00058-5) — 10.1016/s0920-5861(02)00058-5 | Not verified | Not verified | Not verified |
| [Ni/SiO2 and Fe/SiO2 catalysts for production of hydrogen and filamentous carbon via methane decomposition](https://doi.org/10.1016/s0920-5861(02)00248-1) — 10.1016/s0920-5861(02)00248-1 | Not verified | Not verified | Not verified |
| [Highly effective conversion of CO2 to methanol over supported and promoted copper-based catalysts: influence of support and promoter](https://doi.org/10.1016/s0926-3373(00)00205-8) — 10.1016/s0926-3373(00)00205-8 | Not verified | Not verified | Not verified |
| [Chemical and mechanistic aspects of the selective catalytic reduction of NO  by ammonia over oxide catalysts: A review](https://doi.org/10.1016/s0926-3373(98)00040-x) — 10.1016/s0926-3373(98)00040-x | Not verified | Not verified | Not verified |
| [Cobalt molybdenum bimetallic nitride catalysts for ammonia synthesis](https://doi.org/10.1016/s0926-860x(01)00529-4) — 10.1016/s0926-860x(01)00529-4 | Not verified | Not verified | Not verified |
| [Cobalt molybdenum bimetallic nitride catalysts for ammonia synthesis](https://doi.org/10.1016/s0926-860x(01)00626-3) — 10.1016/s0926-860x(01)00626-3 | Not verified | Not verified | Not verified |
| [Present status and perspectives in de-NOx SCR catalysis](https://doi.org/10.1016/s0926-860x(01)00832-8) — 10.1016/s0926-860x(01)00832-8 | Not verified | Not verified | Not verified |
| [Selective catalytic oxidation of CO in H2: structural study of Fe oxide-promoted Pt/alumina catalyst](https://doi.org/10.1016/s0926-860x(01)00915-2) — 10.1016/s0926-860x(01)00915-2 | Not verified | Not verified | Not verified |
| [Study of reverse water gas shift reaction by TPD, TPR and CO2 hydrogenation over potassium-promoted Cu/SiO2 catalyst](https://doi.org/10.1016/s0926-860x(02)00221-1) — 10.1016/s0926-860x(02)00221-1 | Not verified | Not verified | Not verified |
| [Selective CO oxidation over CuO-CeO2 catalysts prepared via the urea–nitrate combustion method](https://doi.org/10.1016/s0926-860x(02)00558-6) — 10.1016/s0926-860x(02)00558-6 | Not verified | Not verified | Not verified |
| [Epoxidation of ethylene over silver catalysts supported on α-alumina crystal carriers](https://doi.org/10.1016/s0926-860x(02)00595-1) — 10.1016/s0926-860x(02)00595-1 | Not verified | Not verified | Not verified |
| [Wustite as a new precursor of industrial ammonia synthesis catalysts](https://doi.org/10.1016/s0926-860x(03)00313-2) — 10.1016/s0926-860x(03)00313-2 | Not verified | Not verified | Not verified |
| [Methane-reforming reactions over Ni/Ce-ZrO2/θ-Al2O3 catalysts](https://doi.org/10.1016/s0926-860x(03)00359-4) — 10.1016/s0926-860x(03)00359-4 | Not verified | Not verified | Not verified |
| [Carbon-supported promoted Ru catalyst for ammonia synthesis](https://doi.org/10.1016/s0926-860x(99)00144-1) — 10.1016/s0926-860x(99)00144-1 | Not verified | Not verified | Not verified |
| [Comparative studies of low-temperature water–gas shift reaction over Pt/CeO2, Au/CeO2, and Au/Fe2O3 catalysts](https://doi.org/10.1016/s1566-7367(03)00036-0) — 10.1016/s1566-7367(03)00036-0 | Not verified | Not verified | Not verified |
| [Ammonia synthesis catalyst 100 years: Practice, enlightenment and challenge](https://doi.org/10.1016/s1872-2067(14)60118-2) — 10.1016/s1872-2067(14)60118-2 | Not verified | Not verified | Not verified |
| [Anion-Exchange Membrane Water Electrolyzers](https://doi.org/10.1021/acs.chemrev.1c00854) — 10.1021/acs.chemrev.1c00854 | Yes | Yes | Not verified |
| [CO2 Hydrogenation to Formate and Methanol as an Alternative to Photo- and Electrochemical CO2 Reduction](https://doi.org/10.1021/acs.chemrev.5b00197) — 10.1021/acs.chemrev.5b00197 | Not verified | Not verified | Not verified |
| [Progress and Perspectives of Electrochemical CO2 Reduction on Copper in Aqueous Electrolyte](https://doi.org/10.1021/acs.chemrev.8b00705) — 10.1021/acs.chemrev.8b00705 | Not verified | Yes | Not verified |
| [Review of the Decomposition of Ammonia to Generate Hydrogen](https://doi.org/10.1021/acs.iecr.1c00843) — 10.1021/acs.iecr.1c00843 | Not verified | Not verified | Not verified |
| [Methane Pyrolysis for Zero-Emission Hydrogen Production: A Potential Bridge Technology from Fossil Fuels to a Renewable and Sustainable Hydrogen Economy](https://doi.org/10.1021/acs.iecr.1c01679) — 10.1021/acs.iecr.1c01679 | Not verified | Not verified | Not verified |
| [Carbon Nanofiber Growth Rates on NiCu Catalysts: Quantitative Coupling of Macroscopic and Nanoscale In Situ Studies](https://doi.org/10.1021/acs.jpcc.3c02657) — 10.1021/acs.jpcc.3c02657 | Yes | Yes | Not verified |
| [Au-Decorated Ce–Ti Mixed Oxides for Efficient CO Preferential Photooxidation](https://doi.org/10.1021/acsami.0c08258) — 10.1021/acsami.0c08258 | Yes | Yes | Yes |
| [CO <sub>2</sub> Activation over Nanoshaped CeO <sub>2</sub> Decorated with Nickel for Low-Temperature Methane Dry Reforming](https://doi.org/10.1021/acsami.2c05221) — 10.1021/acsami.2c05221 | Yes | Not verified | Yes |
| [PtZn Intermetallic Compound Nanoparticles in Mesoporous Zeolite Exhibiting High Catalyst Durability for Propane Dehydrogenation](https://doi.org/10.1021/acscatal.1c01808) — 10.1021/acscatal.1c01808 | Not verified | Yes | Not verified |
| [Substituting Chromium in Iron-Based Catalysts for the High-Temperature Water–Gas Shift Reaction](https://doi.org/10.1021/acscatal.2c03871) — 10.1021/acscatal.2c03871 | Yes | Not verified | Yes |
| [Revealing the Nature of Active Oxygen Species and Reaction Mechanism of Ethylene Epoxidation by Supported Ag/α-Al                     2                     O                     3                     Catalysts](https://doi.org/10.1021/acscatal.3c04361) — 10.1021/acscatal.3c04361 | Yes | Yes | Yes |
| [Unveiling the Structure–Property Relationship of MgO-Supported Ni Ammonia Decomposition Catalysts from Bulk to Atomic Structure by In Situ/Operando Studies](https://doi.org/10.1021/acscatal.3c05629) — 10.1021/acscatal.3c05629 | Yes | Yes | Not verified |
| [Methanol to Olefins (MTO): From Fundamentals to Commercialization](https://doi.org/10.1021/acscatal.5b00007) — 10.1021/acscatal.5b00007 | Not verified | Yes | Not verified |
| [Iron-Based Catalysts for the High-Temperature Water–Gas Shift (HT-WGS) Reaction: A Review](https://doi.org/10.1021/acscatal.5b02594) — 10.1021/acscatal.5b02594 | Not verified | Not verified | Not verified |
| [Fine-Tuning Catalysts: The Role of Support Nanomorphology in Shaping Cu/CeO <sub>2</sub> CO-PROX Properties](https://doi.org/10.1021/acscatal.5c06552) — 10.1021/acscatal.5c06552 | Yes | Not verified | Yes |
| [Promotion Mechanisms of Iron Oxide-Based High Temperature Water–Gas Shift Catalysts by Chromium and Copper](https://doi.org/10.1021/acscatal.6b00698) — 10.1021/acscatal.6b00698 | Not verified | Yes | Not verified |
| [IrO                     2                     -TiO                     2                     : A High-Surface-Area, Active, and Stable Electrocatalyst for the Oxygen Evolution Reaction](https://doi.org/10.1021/acscatal.6b03246) — 10.1021/acscatal.6b03246 | Not verified | Yes | Not verified |
| [Isolated Single-Atomic Ru Catalyst Bound on a Layered Double Hydroxide for Hydrogenation of CO2 to Formic Acid](https://doi.org/10.1021/acscatal.7b00312) — 10.1021/acscatal.7b00312 | Not verified | Yes | Yes |
| [Potential of an Alumina-Supported Ni3Fe Catalyst in the Methanation of CO2: Impact of Alloy Formation on Activity and Stability](https://doi.org/10.1021/acscatal.7b01896) — 10.1021/acscatal.7b01896 | Not verified | Yes | Not verified |
| [Selective Hydrogenation of Acetylene to Ethylene in the Presence of a Carbonaceous Surface Layer on a Pd/Cu(111) Single-Atom Alloy](https://doi.org/10.1021/acscatal.7b02862) — 10.1021/acscatal.7b02862 | Not verified | Not verified | Not verified |
| [Low-Temperature CO                     2                     Methanation over CeO                     2                     -Supported Ru Single Atoms, Nanoclusters, and Nanoparticles Competitively Tuned by Strong Metal–Support Interactions and H-Spillover Effect](https://doi.org/10.1021/acscatal.7b04469) — 10.1021/acscatal.7b04469 | Not verified | Yes | Not verified |
| [Surface Engineering of CoMoS Nanosulfide for Hydrodeoxygenation of Lignin-Derived Phenols to Arenes](https://doi.org/10.1021/acscatal.8b03402) — 10.1021/acscatal.8b03402 | Not verified | Yes | Not verified |
| [Relationship between Atomic Scale Structure and Reactivity of Pt Catalysts: Hydrodeoxygenation of m-Cresol over Isolated Pt Cations and Clusters](https://doi.org/10.1021/acscatal.9b04330) — 10.1021/acscatal.9b04330 | Not verified | Yes | Not verified |
| [Plasma-Assisted Surface Nitridation of Proton Intercalatable WO3 for Efficient Electrocatalytic Ammonia Synthesis](https://doi.org/10.1021/acsenergylett.5c01034) — 10.1021/acsenergylett.5c01034 | Yes | Yes | Yes |
| [Alloyed PdCu Nanoparticles within Siliceous Zeolite Crystals for Catalytic Semihydrogenation](https://doi.org/10.1021/acsmaterialsau.1c00080) — 10.1021/acsmaterialsau.1c00080 | Yes | Yes | Yes |
| [Effect of Calcination Temperature on Cu-Modified Ni Catalysts Supported on Mesocellular Silica for Methane Decomposition](https://doi.org/10.1021/acsomega.2c01016) — 10.1021/acsomega.2c01016 | Yes | Not verified | Yes |
| [Selective Deoxygenation of Waste Cooking Oil to Diesel-Like Hydrocarbons Using Supported and Unsupported NiMoS2 Catalysts](https://doi.org/10.1021/acsomega.3c06188) — 10.1021/acsomega.3c06188 | Yes | Not verified | Yes |
| [Synergistic Effect of Group 9 Metals on the Performance of Hydrotalcite-Derived Ni Catalysts for Methane Dry Reforming](https://doi.org/10.1021/acsomega.5c08293) — 10.1021/acsomega.5c08293 | Yes | Not verified | Yes |
| [Compact Steam-Methane Reforming for the Production of Hydrogen in Continuous Flow Microreactor Systems](https://doi.org/10.1021/acsomega.9b02063) — 10.1021/acsomega.9b02063 | Yes | Not verified | Not verified |
| [Effect of Thermal Extraction on Coal-Based Activated Carbon for Methane Decomposition to Hydrogen](https://doi.org/10.1021/acsomega.9b04044) — 10.1021/acsomega.9b04044 | Yes | Not verified | Yes |
| [Nitrogen Fixation with Water Vapor by Nonequilibrium Plasma: toward Sustainable Ammonia Production](https://doi.org/10.1021/acssuschemeng.9b07849) — 10.1021/acssuschemeng.9b07849 | Not verified | Yes | Not verified |
| [Semiconductor-based Photocatalytic Hydrogen Generation](https://doi.org/10.1021/cr1001645) — 10.1021/cr1001645 | Not verified | Not verified | Not verified |
| [Solar Water Splitting Cells](https://doi.org/10.1021/cr1002326) — 10.1021/cr1002326 | Not verified | Not verified | Not verified |
| [Catalytic Dehydrogenation of Light Alkanes on Metals and Metal Oxides](https://doi.org/10.1021/cr5002436) — 10.1021/cr5002436 | Not verified | Not verified | Not verified |
| [Recent Advances in Preferential Oxidation of CO Reaction over Platinum Group Metal Catalysts](https://doi.org/10.1021/cs200418w) — 10.1021/cs200418w | Not verified | Not verified | Not verified |
| [Highly Selective Electro-Oxidation of Glycerol to Dihydroxyacetone on Platinum in the Presence of Bismuth](https://doi.org/10.1021/cs200599g) — 10.1021/cs200599g | Not verified | Yes | Not verified |
| [Ni–Mo Nanopowders for Efficient Electrochemical Hydrogen Evolution](https://doi.org/10.1021/cs300691m) — 10.1021/cs300691m | Not verified | Yes | Yes |
| [Catalytic CO                     2                     Hydrogenation to Formate by a Ruthenium Pincer Complex](https://doi.org/10.1021/cs400609u) — 10.1021/cs400609u | Not verified | Yes | Not verified |
| [Olefin Metathesis by Supported Metal Oxide Catalysts](https://doi.org/10.1021/cs500528h) — 10.1021/cs500528h | Not verified | Not verified | Not verified |
| [Historical Developments in Hydroprocessing Bio-oils](https://doi.org/10.1021/ef070044u) — 10.1021/ef070044u | Not verified | Not verified | Not verified |
| [Anisole and Guaiacol Hydrodeoxygenation over Monolithic Pt–Sn Catalysts](https://doi.org/10.1021/ef200728r) — 10.1021/ef200728r | Not verified | Not verified | Not verified |
| [Promoter effects on precipitated iron catalysts for Fischer-Tropsch synthesis](https://doi.org/10.1021/ie00098a008) — 10.1021/ie00098a008 | Not verified | Not verified | Not verified |
| [Kinetic Studies of Carbon Dioxide Reforming of Methane over Ni−Co/Al−Mg−O Bimetallic Catalyst](https://doi.org/10.1021/ie801078p) — 10.1021/ie801078p | Not verified | Not verified | Not verified |
| [Hydrotreatment of Fast Pyrolysis Oil Using Heterogeneous Noble-Metal Catalysts](https://doi.org/10.1021/ie9006003) — 10.1021/ie9006003 | Not verified | Not verified | Not verified |
| [Catalyst Design by Interpolation in the Periodic Table:  Bimetallic Ammonia Synthesis Catalysts](https://doi.org/10.1021/ja010963d) — 10.1021/ja010963d | Not verified | Not verified | Not verified |
| [Control of Ethylene Epoxidation Selectivity by Surface Oxametallacycles](https://doi.org/10.1021/ja029076g) — 10.1021/ja029076g | Not verified | Yes | Not verified |
| [On the Mechanism of Cs Promotion in Ethylene Epoxidation on Ag](https://doi.org/10.1021/ja048462q) — 10.1021/ja048462q | Not verified | Yes | Not verified |
| [Biomimetic Hydrogen Evolution:  MoS                     2                     Nanoparticles as Catalyst for Hydrogen Evolution](https://doi.org/10.1021/ja0504690) — 10.1021/ja0504690 | Not verified | Yes | Not verified |
| [Synergistic Catalysis of Metal–Organic Framework-Immobilized Au–Pd Nanoparticles in Dehydrogenation of Formic Acid for Chemical Hydrogen Storage](https://doi.org/10.1021/ja200122f) — 10.1021/ja200122f | Not verified | Yes | Not verified |
| [MoS                     2                     Nanoparticles Grown on Graphene: An Advanced Catalyst for the Hydrogen Evolution Reaction](https://doi.org/10.1021/ja201269b) — 10.1021/ja201269b | Not verified | Yes | Not verified |
| [Benchmarking Heterogeneous Electrocatalysts for the Oxygen Evolution Reaction](https://doi.org/10.1021/ja407115p) — 10.1021/ja407115p | Not verified | Yes | Not verified |
| [Nickel–Iron Oxyhydroxide Oxygen-Evolution Electrocatalysts: The Role of Intentional and Incidental Iron Incorporation](https://doi.org/10.1021/ja502379c) — 10.1021/ja502379c | Not verified | Yes | Not verified |
| [Catalytic Hydrogenation of Carbon Dioxide Using Ir(III)−Pincer Complexes](https://doi.org/10.1021/ja903574e) — 10.1021/ja903574e | Not verified | Yes | Not verified |
| [A Novel Aqueous Process for Preparation of Crystal Form-Controlled and Highly Crystalline BiVO                     4                     Powder from Layered Vanadates at Room Temperature and Its Photocatalytic and Photophysical Properties](https://doi.org/10.1021/ja992541y) — 10.1021/ja992541y | Not verified | Not verified | Not verified |
| [Structure and Reactivity of Oxygen-Bridged Diamino Dicopper(II) Complexes in Cu-Ion-Exchanged Chabazite Catalyst for NH3-Mediated Selective Catalytic Reduction](https://doi.org/10.1021/jacs.0c06270) — 10.1021/jacs.0c06270 | Yes | Yes | Not verified |
| [Probing the Active Surface Sites for CO Reduction on Oxide-Derived Copper Electrocatalysts](https://doi.org/10.1021/jacs.5b06227) — 10.1021/jacs.5b06227 | Not verified | Yes | Yes |
| [Mesostructure-Induced Selectivity in CO2 Reduction Catalysis](https://doi.org/10.1021/jacs.5b08259) — 10.1021/jacs.5b08259 | Not verified | Yes | Yes |
| [Optimizing Binding Energies of Key Intermediates for CO                     2                     Hydrogenation to Methanol over Oxide-Supported Copper](https://doi.org/10.1021/jacs.6b05791) — 10.1021/jacs.6b05791 | Not verified | Yes | Not verified |
| [High Electrocatalytic Hydrogen Evolution Activity of an Anomalous Ruthenium Catalyst](https://doi.org/10.1021/jacs.6b11291) — 10.1021/jacs.6b11291 | Not verified | Yes | Not verified |
| [The Central Role of Bicarbonate in the Electrochemical Reduction of Carbon Dioxide on Gold](https://doi.org/10.1021/jacs.6b13287) — 10.1021/jacs.6b13287 | Not verified | Yes | Not verified |
| [Selective Acetylene Hydrogenation over Single-Atom Alloy Nanoparticles by Kinetic Monte Carlo](https://doi.org/10.1021/jacs.9b02132) — 10.1021/jacs.9b02132 | Not verified | Yes | Not verified |
| [Nanosize-Enhanced Lifetime of SAPO-34 Catalysts in Methanol-to-Olefin Reactions](https://doi.org/10.1021/jp312857p) — 10.1021/jp312857p | Not verified | Yes | Not verified |
| [Size-Dependent Activity of Co3O4 Nanoparticle Anodes for Alkaline Water Electrolysis](https://doi.org/10.1021/jp904022e) — 10.1021/jp904022e | Not verified | Yes | Not verified |
| [Synthesis and Characterization of 9 nm Pt–Ni Octahedra with a Record High Activity of 3.3 A/mg                     Pt                     for the Oxygen Reduction Reaction](https://doi.org/10.1021/nl401881z) — 10.1021/nl401881z | Not verified | Yes | Not verified |
| [CuO–CeO2 mixed oxide catalysts for the selective oxidation of carbon monoxide in excess hydrogen](https://doi.org/10.1023/a:1009013029842) — 10.1023/a:1009013029842 | Not verified | Not verified | Not verified |
| [Activity, Selectivity, and Long-Term Stability of Different Metal Oxide Supported Gold Catalysts for the Preferential CO Oxidation in H2-Rich Gas](https://doi.org/10.1023/a:1012365710979) — 10.1023/a:1012365710979 | Not verified | Not verified | Not verified |
| [The role of zinc oxide in Cu/ZnO catalysts for methanol synthesis and the water–gas shift reaction](https://doi.org/10.1023/a:1019181715731) — 10.1023/a:1019181715731 | Not verified | Not verified | Not verified |
| [Rhenium Oxide Supported on Mesoporous Organised Alumina as a Catalyst for Metathesis of 1-Alkenes](https://doi.org/10.1023/b:catl.0000034280.35570.26) — 10.1023/b:catl.0000034280.35570.26 | Not verified | Not verified | Not verified |
| [Electrochemical Photolysis of Water at a Semiconductor Electrode](https://doi.org/10.1038/238037a0) — 10.1038/238037a0 | Not verified | Not verified | Not verified |
| [Electrocatalyst approaches and challenges for automotive fuel cells](https://doi.org/10.1038/nature11115) — 10.1038/nature11115 | Not verified | Not verified | Not verified |
| [Enhanced electrocatalytic CO2 reduction via field-induced reagent concentration](https://doi.org/10.1038/nature19060) — 10.1038/nature19060 | Not verified | Not verified | Not verified |
| [Ammonia synthesis using a stable electride as an electron donor and reversible hydrogen store](https://doi.org/10.1038/nchem.1476) — 10.1038/nchem.1476 | Not verified | Not verified | Not verified |
| [Pure and stable metallic phase molybdenum disulfide nanosheets for hydrogen evolution reaction](https://doi.org/10.1038/ncomms10672) — 10.1038/ncomms10672 | Yes | Not verified | Yes |
| [Metallic tin quantum sheets confined in graphene toward high-efficiency carbon dioxide electroreduction](https://doi.org/10.1038/ncomms12697) — 10.1038/ncomms12697 | Yes | Yes | Yes |
| [Nanoscale nickel oxide/nickel heterostructures for active hydrogen evolution electrocatalysis](https://doi.org/10.1038/ncomms5695) — 10.1038/ncomms5695 | Not verified | Not verified | Not verified |
| [Electride support boosts nitrogen dissociation over ruthenium catalyst and shifts the bottleneck in ammonia synthesis](https://doi.org/10.1038/ncomms7731) — 10.1038/ncomms7731 | Yes | Yes | Not verified |
| [Bifunctional non-noble metal oxide nanoparticle electrocatalysts through lithium-induced conversion for overall water splitting](https://doi.org/10.1038/ncomms8261) — 10.1038/ncomms8261 | Yes | Not verified | Not verified |
| [Selective hydrogenation of 1,3-butadiene on platinum–copper alloys at the single-atom limit](https://doi.org/10.1038/ncomms9550) — 10.1038/ncomms9550 | Yes | Yes | Not verified |
| [Patched bimetallic surfaces are active catalysts for ammonia decomposition](https://doi.org/10.1038/ncomms9619) — 10.1038/ncomms9619 | Yes | Yes | Not verified |
| [Activity origin and catalyst design principles for electrocatalytic hydrogen evolution on heteroatom-doped graphene](https://doi.org/10.1038/nenergy.2016.130) — 10.1038/nenergy.2016.130 | Not verified | Not verified | Not verified |
| [Trends in electrocatalysis on extended and nanoscale Pt-bimetallic alloy surfaces](https://doi.org/10.1038/nmat1840) — 10.1038/nmat1840 | Not verified | Not verified | Not verified |
| [A metal-free polymeric photocatalyst for hydrogen production from water under visible light](https://doi.org/10.1038/nmat2317) — 10.1038/nmat2317 | Not verified | Not verified | Not verified |
| [Band alignment of rutile and anatase TiO2](https://doi.org/10.1038/nmat3697) — 10.1038/nmat3697 | Not verified | Not verified | Not verified |
| [Enhanced catalytic activity in strained chemically exfoliated WS2 nanosheets for hydrogen evolution](https://doi.org/10.1038/nmat3700) — 10.1038/nmat3700 | Not verified | Not verified | Not verified |
| [Activating and optimizing MoS2 basal planes for hydrogen evolution through the formation of strained sulphur vacancies](https://doi.org/10.1038/nmat4465) — 10.1038/nmat4465 | Not verified | Not verified | Not verified |
| [The role of electronic coupling between substrate and 2D MoS2 nanosheets in electrocatalytic production of hydrogen](https://doi.org/10.1038/nmat4660) — 10.1038/nmat4660 | Not verified | Not verified | Not verified |
| [Hydrogen production from formic acid decomposition at room temperature using a Ag–Pd core–shell nanocatalyst](https://doi.org/10.1038/nnano.2011.42) — 10.1038/nnano.2011.42 | Not verified | Not verified | Not verified |
| [An efficient and pH-universal ruthenium-based catalyst for the hydrogen evolution reaction](https://doi.org/10.1038/nnano.2016.304) — 10.1038/nnano.2016.304 | Not verified | Not verified | Not verified |
| [The most active Cu facet for low-temperature water gas shift reaction](https://doi.org/10.1038/s41467-017-00620-6) — 10.1038/s41467-017-00620-6 | Yes | Yes | Not verified |
| [Manufacture of highly loaded silica-supported cobalt Fischer–Tropsch catalysts from a metal organic framework](https://doi.org/10.1038/s41467-017-01910-9) — 10.1038/s41467-017-01910-9 | Yes | Yes | Not verified |
| [Size-dependent activity and selectivity of carbon dioxide photocatalytic reduction over platinum nanoparticles](https://doi.org/10.1038/s41467-018-03666-2) — 10.1038/s41467-018-03666-2 | Yes | Yes | Yes |
| [Activity enhancement of cobalt catalysts by tuning metal-support interactions](https://doi.org/10.1038/s41467-018-06903-w) — 10.1038/s41467-018-06903-w | Yes | Yes | Yes |
| [Exploring the ternary interactions in Cu–ZnO–ZrO2 catalysts for efficient CO2 hydrogenation to methanol](https://doi.org/10.1038/s41467-019-09072-6) — 10.1038/s41467-019-09072-6 | Yes | Yes | Not verified |
| [Selective light absorber-assisted single nickel atom catalysts for ambient sunlight-driven CO2 methanation](https://doi.org/10.1038/s41467-019-10304-y) — 10.1038/s41467-019-10304-y | Yes | Not verified | Yes |
| [Atomic-scale engineering of indium oxide promotion by palladium for methanol production via CO2 hydrogenation](https://doi.org/10.1038/s41467-019-11349-9) — 10.1038/s41467-019-11349-9 | Yes | Yes | Yes |
| [Highly efficient decomposition of ammonia using high-entropy alloy catalysts](https://doi.org/10.1038/s41467-019-11848-9) — 10.1038/s41467-019-11848-9 | Yes | Yes | Not verified |
| [Boosting selective nitrogen reduction to ammonia on electron-deficient copper nanoparticles](https://doi.org/10.1038/s41467-019-12312-4) — 10.1038/s41467-019-12312-4 | Yes | Not verified | Yes |
| [Atomically dispersed nickel as coke-resistant active sites for methane dry reforming](https://doi.org/10.1038/s41467-019-12843-w) — 10.1038/s41467-019-12843-w | Yes | Yes | Not verified |
| [Synergistic ultraviolet and visible light photo-activation enables intensified low-temperature methanol synthesis over copper/zinc oxide/alumina](https://doi.org/10.1038/s41467-020-15445-z) — 10.1038/s41467-020-15445-z | Yes | Yes | Yes |
| [Solid solution for catalytic ammonia synthesis from nitrogen and hydrogen gases at 50 °C](https://doi.org/10.1038/s41467-020-15868-8) — 10.1038/s41467-020-15868-8 | Yes | Yes | Yes |
| [Single-atom Pt in intermetallics as an ultrastable and selective catalyst for propane dehydrogenation](https://doi.org/10.1038/s41467-020-16693-9) — 10.1038/s41467-020-16693-9 | Yes | Yes | Not verified |
| [Identifying the nature of the active sites in methanol synthesis over Cu/ZnO/Al2O3 catalysts](https://doi.org/10.1038/s41467-020-17631-5) — 10.1038/s41467-020-17631-5 | Yes | Yes | Not verified |
| [Identification and elimination of false positives in electrochemical nitrogen reduction studies](https://doi.org/10.1038/s41467-020-19130-z) — 10.1038/s41467-020-19130-z | Yes | Yes | Not verified |
| [Dynamic structure of active sites in ceria-supported Pt catalysts for the water gas shift reaction](https://doi.org/10.1038/s41467-021-21132-4) — 10.1038/s41467-021-21132-4 | Yes | Yes | Yes |
| [Simple physical mixing of zeolite prevents sulfur deactivation of vanadia catalysts for NOx removal](https://doi.org/10.1038/s41467-021-21228-x) — 10.1038/s41467-021-21228-x | Yes | Yes | Yes |
| [Nanostructure of nickel-promoted indium oxide catalysts drives selectivity in CO2 hydrogenation](https://doi.org/10.1038/s41467-021-22224-x) — 10.1038/s41467-021-22224-x | Yes | Yes | Not verified |
| [Stabilizing the framework of SAPO-34 zeolite toward long-term methanol-to-olefins conversion](https://doi.org/10.1038/s41467-021-24403-2) — 10.1038/s41467-021-24403-2 | Yes | Yes | Not verified |
| [The role of oxygen-permeable ionomer for polymer electrolyte fuel cells](https://doi.org/10.1038/s41467-021-25301-3) — 10.1038/s41467-021-25301-3 | Yes | Yes | Not verified |
| [Advancements in cathode catalyst and cathode layer design for proton exchange membrane fuel cells](https://doi.org/10.1038/s41467-021-25911-x) — 10.1038/s41467-021-25911-x | Yes | Yes | Not verified |
| [Partially sintered copper‒ceria as excellent catalyst for the high-temperature reverse water gas shift reaction](https://doi.org/10.1038/s41467-022-28476-5) — 10.1038/s41467-022-28476-5 | Yes | Yes | Yes |
| [Iron atom–cluster interactions increase activity and improve durability in Fe–N–C fuel cells](https://doi.org/10.1038/s41467-022-30702-z) — 10.1038/s41467-022-30702-z | Yes | Yes | Not verified |
| [Hierarchical micro/nanostructured silver hollow fiber boosts electroreduction of carbon dioxide](https://doi.org/10.1038/s41467-022-30733-6) — 10.1038/s41467-022-30733-6 | Yes | Yes | Yes |
| [Subsurface oxygen defects electronically interacting with active sites on In2O3 for enhanced photothermocatalytic CO2 reduction](https://doi.org/10.1038/s41467-022-30958-5) — 10.1038/s41467-022-30958-5 | Yes | Yes | Not verified |
| [Ptn–Ov synergistic sites on MoOx/γ-Mo2N heterostructure for low-temperature reverse water–gas shift reaction](https://doi.org/10.1038/s41467-022-33308-7) — 10.1038/s41467-022-33308-7 | Yes | Yes | Not verified |
| [Flame-made ternary Pd-In2O3-ZrO2 catalyst with enhanced oxygen vacancy generation for CO2 hydrogenation to methanol](https://doi.org/10.1038/s41467-022-33391-w) — 10.1038/s41467-022-33391-w | Yes | Yes | Not verified |
| [Predictive control of selective secondary alcohol oxidation of glycerol on NiOOH](https://doi.org/10.1038/s41467-022-33637-7) — 10.1038/s41467-022-33637-7 | Yes | Yes | Yes |
| [Fully-exposed Pt-Fe cluster for efficient preferential oxidation of CO towards hydrogen purification](https://doi.org/10.1038/s41467-022-34674-y) — 10.1038/s41467-022-34674-y | Yes | Yes | Not verified |
| [Dispersed surface Ru ensembles on MgO(111) for catalytic ammonia decomposition](https://doi.org/10.1038/s41467-023-36339-w) — 10.1038/s41467-023-36339-w | Yes | Not verified | Yes |
| [Ionomer-free and recyclable porous-transport electrode for high-performing proton-exchange-membrane water electrolysis](https://doi.org/10.1038/s41467-023-40375-x) — 10.1038/s41467-023-40375-x | Not verified | Not verified | Not verified |
| [Nano-metal diborides-supported anode catalyst with strongly coupled TaOx/IrO2 catalytic layer for low-iridium-loading proton exchange membrane electrolyzer](https://doi.org/10.1038/s41467-023-40912-8) — 10.1038/s41467-023-40912-8 | Yes | Yes | Yes |
| [Accelerated discovery of multi-elemental reverse water-gas shift catalysts using extrapolative machine learning approach](https://doi.org/10.1038/s41467-023-41341-3) — 10.1038/s41467-023-41341-3 | Yes | Yes | Not verified |
| [Boosting reactivity of water-gas shift reaction by synergistic function over CeO2-x/CoO1-x/Co dual interfacial structures](https://doi.org/10.1038/s41467-023-42577-9) — 10.1038/s41467-023-42577-9 | Yes | Yes | Yes |
| [Defect-driven nanostructuring of low-nuclearity Pt-Mo ensembles for continuous gas-phase formic acid dehydrogenation](https://doi.org/10.1038/s41467-023-42759-5) — 10.1038/s41467-023-42759-5 | Yes | Yes | Yes |
| [Balancing elementary steps enables coke-free dry reforming of methane](https://doi.org/10.1038/s41467-023-43277-0) — 10.1038/s41467-023-43277-0 | Yes | Yes | Not verified |
| [Stabilizing ruthenium dioxide with cation-anchored sulfate for durable oxygen evolution in proton-exchange membrane water electrolyzers](https://doi.org/10.1038/s41467-023-43977-7) — 10.1038/s41467-023-43977-7 | Yes | Yes | Yes |
| [Photo-thermal coupling to enhance CO2 hydrogenation toward CH4 over Ru/MnO/Mn3O4](https://doi.org/10.1038/s41467-024-45389-7) — 10.1038/s41467-024-45389-7 | Yes | Yes | Yes |
| [Reverse water gas-shift reaction product driven dynamic activation of molybdenum nitride catalyst surface](https://doi.org/10.1038/s41467-024-47550-8) — 10.1038/s41467-024-47550-8 | Yes | Yes | Yes |
| [Highly efficient anion exchange membrane water electrolyzers via chromium-doped amorphous electrocatalysts](https://doi.org/10.1038/s41467-024-47736-0) — 10.1038/s41467-024-47736-0 | Yes | Yes | Yes |
| [Monosymmetric Fe-N4 sites enabling durable proton exchange membrane fuel cell cathode by chemical vapor modification](https://doi.org/10.1038/s41467-024-47817-0) — 10.1038/s41467-024-47817-0 | Yes | Yes | Yes |
| [Facilitating the dry reforming of methane with interfacial synergistic catalysis in an Ir@CeO2−x catalyst](https://doi.org/10.1038/s41467-024-48122-6) — 10.1038/s41467-024-48122-6 | Yes | Yes | Yes |
| [Tuning metal-support interactions in nickel–zeolite catalysts leads to enhanced stability during dry reforming of methane](https://doi.org/10.1038/s41467-024-50729-8) — 10.1038/s41467-024-50729-8 | Yes | Yes | Yes |
| [Proton exchange membrane-like alkaline water electrolysis using flow-engineered three-dimensional electrodes](https://doi.org/10.1038/s41467-024-51704-z) — 10.1038/s41467-024-51704-z | Yes | Yes | Not verified |
| [Utilizing full-spectrum sunlight for ammonia decomposition to hydrogen over GaN nanowires-supported Ru nanoparticles on silicon](https://doi.org/10.1038/s41467-024-51810-y) — 10.1038/s41467-024-51810-y | Yes | Yes | Not verified |
| [A Fe-NC electrocatalyst boosted by trace bromide ions with high performance in proton exchange membrane fuel cells](https://doi.org/10.1038/s41467-024-51858-w) — 10.1038/s41467-024-51858-w | Yes | Yes | Yes |
| [Disentangling heterogeneous thermocatalytic formic acid dehydrogenation from an electrochemical perspective](https://doi.org/10.1038/s41467-024-51926-1) — 10.1038/s41467-024-51926-1 | Yes | Yes | Yes |
| [Combination of nanoparticles with single-metal sites synergistically boosts co-catalyzed formic acid dehydrogenation](https://doi.org/10.1038/s41467-024-52517-w) — 10.1038/s41467-024-52517-w | Yes | Yes | Yes |
| [Stable and homogeneous intermetallic alloys by atomic gas-migration for propane dehydrogenation](https://doi.org/10.1038/s41467-024-52518-9) — 10.1038/s41467-024-52518-9 | Yes | Not verified | Not verified |
| [Ir-O-Mn embedded in porous nanosheets enhances charge transfer in low-iridium PEM electrolyzers](https://doi.org/10.1038/s41467-024-54646-8) — 10.1038/s41467-024-54646-8 | Yes | Yes | Yes |
| [Boosting the durability of RuO2 via confinement effect for proton exchange membrane water electrolyzer](https://doi.org/10.1038/s41467-024-55747-0) — 10.1038/s41467-024-55747-0 | Yes | Yes | Not verified |
| [Layered Na2Ti3O7-supported Ru catalyst for ambient CO2 methanation](https://doi.org/10.1038/s41467-025-57954-9) — 10.1038/s41467-025-57954-9 | Yes | Yes | Yes |
| [Support-free iridium hydroxide for high-efficiency proton-exchange membrane water electrolysis](https://doi.org/10.1038/s41467-025-58019-7) — 10.1038/s41467-025-58019-7 | Yes | Yes | Not verified |
| [Sandwiching intermetallic Pt3Fe and ionomer with porous N-doped carbon layers for oxygen reduction reaction](https://doi.org/10.1038/s41467-025-58116-7) — 10.1038/s41467-025-58116-7 | Yes | Yes | Not verified |
| [Synergistic niobium and manganese co-doping into RuO2 nanocrystal enables PEM water splitting under high current](https://doi.org/10.1038/s41467-025-59710-5) — 10.1038/s41467-025-59710-5 | Yes | Yes | Not verified |
| [Regulating orbital interaction to construct quasi-covalent bond networks in Pt intermetallic alloys for high-performance fuel cells](https://doi.org/10.1038/s41467-025-60171-z) — 10.1038/s41467-025-60171-z | Yes | Yes | Not verified |
| [Scalable synthesis of NiFe-layered double hydroxide for efficient anion exchange membrane electrolysis](https://doi.org/10.1038/s41467-025-61356-2) — 10.1038/s41467-025-61356-2 | Yes | Yes | Yes |
| [High-entropy RuO2 catalyst with dual-site oxide path for durable acidic oxygen evolution reaction](https://doi.org/10.1038/s41467-025-61763-5) — 10.1038/s41467-025-61763-5 | Yes | Yes | Not verified |
| [Quantifying electronic and geometric effects on the activity of platinum catalysts for water-gas shift](https://doi.org/10.1038/s41467-025-61895-8) — 10.1038/s41467-025-61895-8 | Yes | Yes | Not verified |
| [Tunnel-structured IrOx unlocks catalytic efficiency in proton exchange membrane water electrolyzers](https://doi.org/10.1038/s41467-025-62861-0) — 10.1038/s41467-025-62861-0 | Yes | Yes | Not verified |
| [Decoding technical multi-promoted ammonia synthesis catalysts](https://doi.org/10.1038/s41467-025-63061-6) — 10.1038/s41467-025-63061-6 | Yes | Not verified | Not verified |
| [Support-tuned iridium reconstruction with crystalline phase dominating acidic oxygen evolution](https://doi.org/10.1038/s41467-025-63541-9) — 10.1038/s41467-025-63541-9 | Yes | Yes | Not verified |
| [Self-modulated hydrogen electrocatalysis on sub-2-nm platinum nanoparticles by in situ generated surface hydrides](https://doi.org/10.1038/s41467-025-65122-2) — 10.1038/s41467-025-65122-2 | Yes | Yes | Yes |
| [Ce-induced synergistic effect in exsolved perovskite catalyst for highly efficient and robust methane dry reforming](https://doi.org/10.1038/s41467-025-65619-w) — 10.1038/s41467-025-65619-w | Yes | Yes | Not verified |
| [Inverse In2O3-x/Ni interfaces via Ni3InC0.5 surface reconstruction for efficient CO2 hydrogenation to methanol](https://doi.org/10.1038/s41467-025-65929-z) — 10.1038/s41467-025-65929-z | Yes | Yes | Not verified |
| [Breakthrough photothermal ammonia decomposition via low-barrier Ni-CeO2-x interfaces on carbon nanotubes](https://doi.org/10.1038/s41467-025-66325-3) — 10.1038/s41467-025-66325-3 | Yes | Yes | Yes |
| [Durable acidic water oxidation ruthenium based electrocatalyst by fluorination induced symmetry breaking](https://doi.org/10.1038/s41467-025-66475-4) — 10.1038/s41467-025-66475-4 | Yes | Yes | Not verified |
| [Ionomer distribution control via thiophene S-modification of carbon support for high-power proton exchange membrane fuel cells](https://doi.org/10.1038/s41467-025-66813-6) — 10.1038/s41467-025-66813-6 | Yes | Yes | Not verified |
| [Active bridging hydride species in ZnO nanorods originated from hydroxyl and oxygen vacancy](https://doi.org/10.1038/s41467-025-67625-4) — 10.1038/s41467-025-67625-4 | Yes | Yes | Not verified |
| [Breaking activity-selectivity-stability trade-offs in reverse water-gas shift reaction via high-energy micro-faceted Mo2N nanocrystals](https://doi.org/10.1038/s41467-026-68756-y) — 10.1038/s41467-026-68756-y | Yes | Yes | Not verified |
| [Mesoporous ruthenium titanium oxide solid solution with efficient three phase reaction interface for water electrolysis](https://doi.org/10.1038/s41467-026-70502-3) — 10.1038/s41467-026-70502-3 | Yes | Yes | Not verified |
| [Advances and challenges in understanding the electrocatalytic conversion of carbon dioxide to fuels](https://doi.org/10.1038/s41560-019-0450-y) — 10.1038/s41560-019-0450-y | Not verified | Not verified | Not verified |
| [Atomically dispersed iron sites with a nitrogen–carbon coating as highly active and durable oxygen reduction catalysts for fuel cells](https://doi.org/10.1038/s41560-022-01062-1) — 10.1038/s41560-022-01062-1 | Not verified | Not verified | Not verified |
| [A rigorous electrochemical ammonia synthesis protocol with quantitative isotope measurements](https://doi.org/10.1038/s41586-019-1260-x) — 10.1038/s41586-019-1260-x | Not verified | Not verified | Not verified |
| [Molecular tuning of CO2-to-ethylene conversion](https://doi.org/10.1038/s41586-019-1782-2) — 10.1038/s41586-019-1782-2 | Not verified | Not verified | Not verified |
| [A stable low-temperature H2-production catalyst by crowding Pt on α-MoC](https://doi.org/10.1038/s41586-020-03130-6) — 10.1038/s41586-020-03130-6 | Not verified | Not verified | Not verified |
| [Photocatalytic water splitting with a quantum efficiency of almost unity](https://doi.org/10.1038/s41586-020-2278-9) — 10.1038/s41586-020-2278-9 | Not verified | Not verified | Not verified |
| [Green synthesis of SAPO-34 via dual bio-templates for enhanced catalytic performance in MTO reaction](https://doi.org/10.1038/s41598-025-14220-8) — 10.1038/s41598-025-14220-8 | Yes | Not verified | Yes |
| [Alkaline-earth-promoted Pd–Ag/Al2O3 for selective acetylene hydrogenation: green-oil mitigation, ethylene selectivity, and implications for hydrogen spillover](https://doi.org/10.1038/s41598-026-46044-5) — 10.1038/s41598-026-46044-5 | Yes | Not verified | Not verified |
| [Lifetime improvement in methanol-to-olefins catalysis over chabazite materials by high-pressure H2 co-feeds](https://doi.org/10.1038/s41929-018-0125-2) — 10.1038/s41929-018-0125-2 | Not verified | Not verified | Not verified |
| [Single platinum atoms immobilized on an MXene as an efficient catalyst for the hydrogen evolution reaction](https://doi.org/10.1038/s41929-018-0195-1) — 10.1038/s41929-018-0195-1 | Not verified | Not verified | Not verified |
| [Fe–N–C electrocatalyst with dense active sites and efficient mass transport for high-performance proton exchange membrane fuel cells](https://doi.org/10.1038/s41929-019-0237-3) — 10.1038/s41929-019-0237-3 | Not verified | Not verified | Not verified |
| [Reaction systems for solar hydrogen production via water splitting with particulate semiconductor photocatalysts](https://doi.org/10.1038/s41929-019-0242-6) — 10.1038/s41929-019-0242-6 | Not verified | Not verified | Not verified |
| [Challenges and prospects in the catalysis of electroreduction of nitrogen to ammonia](https://doi.org/10.1038/s41929-019-0252-4) — 10.1038/s41929-019-0252-4 | Not verified | Not verified | Not verified |
| [Cooperative CO2-to-ethanol conversion via enriched intermediates at molecule–metal catalyst interfaces](https://doi.org/10.1038/s41929-019-0383-7) — 10.1038/s41929-019-0383-7 | Not verified | Not verified | Not verified |
| [Light-driven CO2 methanation over Au-grafted Ce0.95Ru0.05O2 solid-solution catalysts with activities approaching the thermodynamic limit](https://doi.org/10.1038/s41929-023-00970-z) — 10.1038/s41929-023-00970-z | Not verified | Not verified | Not verified |
| [Seed-assisted formation of NiFe anode catalysts for anion exchange membrane water electrolysis at industrial-scale current density](https://doi.org/10.1038/s41929-024-01209-1) — 10.1038/s41929-024-01209-1 | Not verified | Not verified | Not verified |
| [Atom-by-atom design of Cu/ZrOx clusters on MgO for CO2 hydrogenation using liquid-phase atomic layer deposition](https://doi.org/10.1038/s41929-024-01236-y) — 10.1038/s41929-024-01236-y | Not verified | Not verified | Not verified |
| [Cost-efficient and stable electrolysis of reverse osmosis water using a Co-RuO2-enabled PEM electrolyser](https://doi.org/10.1038/s41929-025-01456-w) — 10.1038/s41929-025-01456-w | Not verified | Not verified | Not verified |
| [One-pot synthesis of hierarchical FeZSM-5 zeolites from natural aluminosilicates for selective catalytic reduction of NO by NH3](https://doi.org/10.1038/srep09270) — 10.1038/srep09270 | Yes | Not verified | Yes |
| [Application of olefin metathesis in oleochemistry: an example of green chemistry](https://doi.org/10.1039/b109896a) — 10.1039/b109896a | Not verified | Not verified | Not verified |
| [Heterogeneous photocatalyst materials for water splitting](https://doi.org/10.1039/b800489g) — 10.1039/b800489g | Not verified | Not verified | Not verified |
| [High-quality hydrogen from the catalyzed decomposition of formic acid by Pd–Au/C and Pd–Ag/C](https://doi.org/10.1039/b803661f) — 10.1039/b803661f | Not verified | Not verified | Not verified |
| [The renaissance of iron-based Fischer–Tropsch synthesis: on the multifaceted catalyst deactivation behaviour](https://doi.org/10.1039/b805427d) — 10.1039/b805427d | Not verified | Not verified | Not verified |
| [Insights in the hydrotreatment of fast pyrolysis oil using a ruthenium on carbon catalyst](https://doi.org/10.1039/b923170f) — 10.1039/b923170f | Not verified | Not verified | Not verified |
| [Artificial photosynthesis: semiconductor photocatalytic fixation of CO2 to afford higher organic compounds](https://doi.org/10.1039/c0dt01777a) — 10.1039/c0dt01777a | Not verified | Not verified | Not verified |
| [Recent advances in catalytic hydrogenation of carbon dioxide](https://doi.org/10.1039/c1cs15008a) — 10.1039/c1cs15008a | Not verified | Not verified | Not verified |
| [Methanol-to-hydrocarbon chemistry: The carbon pool (r)evolution](https://doi.org/10.1039/c1cy00197c) — 10.1039/c1cy00197c | Not verified | Not verified | Not verified |
| [New insights into the electrochemical reduction of carbon dioxide on metallic copper surfaces](https://doi.org/10.1039/c2ee21234j) — 10.1039/c2ee21234j | Not verified | Not verified | Not verified |
| [Single atom alloy surface analogs in Pd0.18Cu15 nanoparticles for selective hydrogenation reactions](https://doi.org/10.1039/c3cp51538a) — 10.1039/c3cp51538a | Not verified | Not verified | Not verified |
| [Methanol to olefins: activity and stability of nanosized SAPO-34 molecular sieves and control of selectivity by silicon distribution](https://doi.org/10.1039/c3cp52247d) — 10.1039/c3cp52247d | Not verified | Not verified | Not verified |
| [A review of dry (CO                     2                     ) reforming of methane over noble metal catalysts](https://doi.org/10.1039/c3cs60395d) — 10.1039/c3cs60395d | Not verified | Not verified | Not verified |
| [Selective electrocatalytic reduction of carbon dioxide to formate by a water-soluble iridium pincer catalyst](https://doi.org/10.1039/c3sc51339d) — 10.1039/c3sc51339d | Not verified | Not verified | Not verified |
| [Insights into the electrocatalytic reduction of CO                     2                     on metallic silver surfaces](https://doi.org/10.1039/c4cp00692e) — 10.1039/c4cp00692e | Not verified | Not verified | Not verified |
| [Semiconductor heterojunction photocatalysts: design, construction, and photocatalytic performances](https://doi.org/10.1039/c4cs00126e) — 10.1039/c4cs00126e | Not verified | Not verified | Not verified |
| [Noble metal-free hydrogen evolution catalysts for water splitting](https://doi.org/10.1039/c4cs00448e) — 10.1039/c4cs00448e | Not verified | Not verified | Not verified |
| [Recent advances in automotive catalysis for NO                     x                     emission control by small-pore microporous materials](https://doi.org/10.1039/c5cs00108k) — 10.1039/c5cs00108k | Not verified | Not verified | Not verified |
| [Formic acid as a hydrogen storage material – development of homogeneous catalysts for selective hydrogen release](https://doi.org/10.1039/c5cs00618j) — 10.1039/c5cs00618j | Not verified | Not verified | Not verified |
| [Overall water splitting by Pt/g-C                     3                     N                     4                     photocatalysts without using sacrificial agents](https://doi.org/10.1039/c5sc04572j) — 10.1039/c5sc04572j | Yes | Yes | Yes |
| [Flux-mediated doping of SrTiO                     3                     photocatalysts for efficient overall water splitting](https://doi.org/10.1039/c5ta04843e) — 10.1039/c5ta04843e | Not verified | Not verified | Not verified |
| [Electrocatalysis for the oxygen evolution reaction: recent development and future perspectives](https://doi.org/10.1039/c6cs00328a) — 10.1039/c6cs00328a | Not verified | Not verified | Not verified |
| [CO                     2                     conversion by reverse water gas shift catalysis: comparison of catalysts, mechanisms and their consequences for CO                     2                     conversion to liquid fuels](https://doi.org/10.1039/c6ra05414e) — 10.1039/c6ra05414e | Not verified | Not verified | Not verified |
| [Hydrogen production by methane decomposition over Ni–Cu–SiO                     2                     catalysts: effect of temperature on catalyst deactivation](https://doi.org/10.1039/c6ra05782a) — 10.1039/c6ra05782a | Not verified | Not verified | Not verified |
| [Well-defined silica supported bipodal molybdenum oxo alkyl complexes: a model of the active sites of industrial olefin metathesis catalysts](https://doi.org/10.1039/c7cc06041f) — 10.1039/c7cc06041f | Not verified | Not verified | Not verified |
| [Palladium–gold single atom alloy catalysts for liquid phase selective hydrogenation of 1-hexyne](https://doi.org/10.1039/c7cy00794a) — 10.1039/c7cy00794a | Not verified | Not verified | Not verified |
| [Simple organic structure directing agents for synthesizing nanocrystalline zeolites](https://doi.org/10.1039/c7sc02858j) — 10.1039/c7sc02858j | Yes | Not verified | Yes |
| [Cu-CHA – a model system for applied selective redox catalysis](https://doi.org/10.1039/c8cs00373d) — 10.1039/c8cs00373d | Not verified | Not verified | Not verified |
| [Synthesis of uniform ordered mesoporous TiO 2 microspheres with controllable phase junctions for efficient solar water splitting](https://doi.org/10.1039/c8sc04155e) — 10.1039/c8sc04155e | Yes | Yes | Yes |
| [Effect of nitrogen co-doping with ruthenium on the catalytic performance of Ba/Ru–N-MC catalysts for ammonia synthesis](https://doi.org/10.1039/c9ra03097b) — 10.1039/c9ra03097b | Yes | Not verified | Yes |
| [Ni nanocatalysts supported on mesoporous Al 2 O 3 –CeO 2 for CO 2 methanation at low temperature](https://doi.org/10.1039/c9ra08967e) — 10.1039/c9ra08967e | Yes | Not verified | Not verified |
| [Current status and perspectives in oxidative, non-oxidative and CO                     2                     -mediated dehydrogenation of propane and isobutane over metal oxide catalysts](https://doi.org/10.1039/d0cs01140a) — 10.1039/d0cs01140a | Not verified | Not verified | Not verified |
| [Binary and ternary Pt-based clusters grown in a plasma multimagnetron-based gas aggregation source: electrocatalytic evaluation towards glycerol oxidation](https://doi.org/10.1039/d0na01009j) — 10.1039/d0na01009j | Yes | Not verified | Yes |
| [Anion-exchange membrane water electrolyzers and fuel cells](https://doi.org/10.1039/d2cs00038e) — 10.1039/d2cs00038e | Not verified | Not verified | Not verified |
| [Cationic molybdenum oxo alkylidenes stabilized by N-heterocyclic carbenes: from molecular systems to efficient supported metathesis catalysts](https://doi.org/10.1039/d2sc03321f) — 10.1039/d2sc03321f | Yes | Yes | Yes |
| [Preparation of Ru/N-doped carbon catalysts by induction of different nitrogen source precursors for the hydroprocessing of lignin oil](https://doi.org/10.1039/d3ra01866k) — 10.1039/d3ra01866k | Yes | Not verified | Yes |
| [Insight into the influence of Re and Cl on Ag catalysts in ethylene epoxidation](https://doi.org/10.1039/d4cy00858h) — 10.1039/d4cy00858h | Yes | Yes | Not verified |
| [Mechanochemically-derived iron atoms on defective boron nitride for stable propylene production](https://doi.org/10.1039/d4ey00123k) — 10.1039/d4ey00123k | Yes | Yes | Yes |
| [Efficient hydrodeoxygenation of lignin-derived phenolic compounds under acid-free conditions over carbon-supported NiMo catalysts](https://doi.org/10.1039/d4gc02298j) — 10.1039/d4gc02298j | Not verified | Not verified | Not verified |
| [Techno-economic and life cycle analyses of the synthesis of a platinum–strontium titanate catalyst](https://doi.org/10.1039/d5cy00189g) — 10.1039/d5cy00189g | Yes | Not verified | Yes |
| [The State of the Art in Selective Catalytic Reduction of NOxby Ammonia Using Metal‐Exchanged Zeolite Catalysts](https://doi.org/10.1080/01614940802480122) — 10.1080/01614940802480122 | Not verified | Not verified | Not verified |
| [Water Gas Shift Catalysis](https://doi.org/10.1080/01614940903048661) — 10.1080/01614940903048661 | Not verified | Not verified | Not verified |
| [Overview: State-of-the Art Commercial Membranes for Anion Exchange Membrane Water Electrolysis](https://doi.org/10.1115/1.4047963) — 10.1115/1.4047963 | Not verified | Not verified | Not verified |
| [Active Nonmetallic Au and Pt Species on Ceria-Based Water-Gas Shift Catalysts](https://doi.org/10.1126/science.1085721) — 10.1126/science.1085721 | Not verified | Not verified | Not verified |
| [Improved Oxygen Reduction Activity on Pt                     3                     Ni(111) via Increased Surface Site Availability](https://doi.org/10.1126/science.1135941) — 10.1126/science.1135941 | Not verified | Not verified | Not verified |
| [Identification of Active Edge Sites for Electrochemical H                     2                     Evolution from MoS                     2                     Nanocatalysts](https://doi.org/10.1126/science.1141483) — 10.1126/science.1141483 | Not verified | Not verified | Not verified |
| [Identification of Non-Precious Metal Alloy Catalysts for Selective Hydrogenation of Acetylene](https://doi.org/10.1126/science.1156660) — 10.1126/science.1156660 | Not verified | Not verified | Not verified |
| [Alkali-Stabilized Pt-OH                            x                          Species Catalyze Low-Temperature Water-Gas Shift Reactions](https://doi.org/10.1126/science.1192449) — 10.1126/science.1192449 | Not verified | Not verified | Not verified |
| [Efficient Dehydrogenation of Formic Acid Using an Iron Catalyst](https://doi.org/10.1126/science.1206613) — 10.1126/science.1206613 | Not verified | Not verified | Not verified |
| [A Perovskite Oxide Optimized for Oxygen Evolution Catalysis from Molecular Orbital Principles](https://doi.org/10.1126/science.1212858) — 10.1126/science.1212858 | Not verified | Not verified | Not verified |
| [The Active Site of Methanol Synthesis over Cu/ZnO/Al                     2                     O                     3                     Industrial Catalysts](https://doi.org/10.1126/science.1219831) — 10.1126/science.1219831 | Not verified | Not verified | Not verified |
| [Highly Crystalline Multimetallic Nanoframes with Three-Dimensional Electrocatalytic Surfaces](https://doi.org/10.1126/science.1249061) — 10.1126/science.1249061 | Not verified | Not verified | Not verified |
| [Design of a Surface Alloy Catalyst for Steam Reforming](https://doi.org/10.1126/science.279.5358.1913) — 10.1126/science.279.5358.1913 | Not verified | Not verified | Not verified |
| [Covalent organic frameworks comprising cobalt porphyrins for catalytic CO             2             reduction in water](https://doi.org/10.1126/science.aac8343) — 10.1126/science.aac8343 | Not verified | Not verified | Not verified |
| [Combining theory and experiment in electrocatalysis: Insights into materials design](https://doi.org/10.1126/science.aad4998) — 10.1126/science.aad4998 | Not verified | Not verified | Not verified |
| [Quantifying the promotion of Cu catalysts by ZnO for methanol synthesis](https://doi.org/10.1126/science.aaf0718) — 10.1126/science.aaf0718 | Not verified | Not verified | Not verified |
| [Selective oxidative dehydrogenation of propane to propene using boron nitride catalysts](https://doi.org/10.1126/science.aaf7885) — 10.1126/science.aaf7885 | Not verified | Not verified | Not verified |
| [Super-dry reforming of methane intensifies CO             2             utilization via Le Chatelier’s principle](https://doi.org/10.1126/science.aah7161) — 10.1126/science.aah7161 | Not verified | Not verified | Not verified |
| [Dynamic multinuclear sites formed by mobilized copper ions in NO                                            x                                          selective catalytic reduction](https://doi.org/10.1126/science.aan5630) — 10.1126/science.aan5630 | Not verified | Not verified | Not verified |
| [Catalytic molten metals for the direct conversion of methane to hydrogen and separable carbon](https://doi.org/10.1126/science.aao5023) — 10.1126/science.aao5023 | Not verified | Not verified | Not verified |
| [CO                     2                     electroreduction to ethylene via hydroxide-mediated copper catalysis at an abrupt interface](https://doi.org/10.1126/science.aas9100) — 10.1126/science.aas9100 | Not verified | Not verified | Not verified |
| [What would it take for renewably powered electrosynthesis to displace petrochemical processes?](https://doi.org/10.1126/science.aav3506) — 10.1126/science.aav3506 | Not verified | Not verified | Not verified |
| [CO                     2                     electrolysis to multicarbon products at activities greater than 1 A cm                     −2](https://doi.org/10.1126/science.aay4217) — 10.1126/science.aay4217 | Not verified | Not verified | Not verified |
| [Nitrogen reduction to ammonia at high efficiency and rates based on a phosphonium proton shuttle](https://doi.org/10.1126/science.abg2371) — 10.1126/science.abg2371 | Not verified | Not verified | Not verified |
| [Stable and selective catalysts for propane dehydrogenation operating at thermodynamic limit](https://doi.org/10.1126/science.abg7894) — 10.1126/science.abg7894 | Not verified | Not verified | Not verified |
| [Continuous-flow electrosynthesis of ammonia by nitrogen reduction and hydrogen oxidation](https://doi.org/10.1126/science.adf4403) — 10.1126/science.adf4403 | Not verified | Not verified | Not verified |
| [Ammonia Synthesis Catalysts](https://doi.org/10.1142/8199) — 10.1142/8199 | Not verified | Not verified | Not verified |
| [Trends in the Exchange Current for Hydrogen Evolution](https://doi.org/10.1149/1.1856988) — 10.1149/1.1856988 | Not verified | Not verified | Not verified |
| [Influence of Ionomer Content in IrO                     2                     /TiO                     2                     Electrodes on PEM Water Electrolyzer Performance](https://doi.org/10.1149/2.0231611jes) — 10.1149/2.0231611jes | Not verified | Not verified | Not verified |
| [Analysis of Voltage Losses in PEM Water Electrolyzers with Low Platinum Group Metal Loadings](https://doi.org/10.1149/2.0641805jes) — 10.1149/2.0641805jes | Not verified | Not verified | Not verified |
| [Novel Gold Catalysts for the Oxidation of Carbon Monoxide at a Temperature far Below 0 °C](https://doi.org/10.1246/cl.1987.405) — 10.1246/cl.1987.405 | Not verified | Not verified | Not verified |
| [Olefin Metathesis over Mesoporous Alumina-supported Rhenium Oxide Catalyst](https://doi.org/10.1246/cl.2002.850) — 10.1246/cl.2002.850 | Not verified | Not verified | Not verified |
| [Selective Electrooxidation of Glycerol Into Value-Added Chemicals: A Short Overview](https://doi.org/10.3389/fchem.2019.00100) — 10.3389/fchem.2019.00100 | Yes | Not verified | Not verified |
| [Recent Advances in Supported Metal Catalysts and Oxide Catalysts for the Reverse Water-Gas Shift Reaction](https://doi.org/10.3389/fchem.2020.00709) — 10.3389/fchem.2020.00709 | Yes | Not verified | Not verified |
| [Structured Alumina Substrates for Environmental Catalysis Produced by Stereolithography](https://doi.org/10.3390/app11178239) — 10.3390/app11178239 | Not verified | Not verified | Not verified |
| [A Short Review on Ni Based Catalysts and Related Engineering Issues for Methane Steam Reforming](https://doi.org/10.3390/catal10030352) — 10.3390/catal10030352 | Not verified | Not verified | Not verified |
| [Fe-Exchanged Small-Pore Zeolites as Ammonia Selective Catalytic Reduction (NH3-SCR) Catalysts](https://doi.org/10.3390/catal10111324) — 10.3390/catal10111324 | Not verified | Not verified | Not verified |
| [VOx Surface Coverage Optimization of V2O5/WO3-TiO2 SCR Catalysts by Variation of the V Loading and by Aging](https://doi.org/10.3390/catal5041704) — 10.3390/catal5041704 | Not verified | Not verified | Not verified |
| [A Case Study for the Deactivation and Regeneration of a V2O5-WO3/TiO2 Catalyst in a Tail-End SCR Unit of a Municipal Waste Incineration Plant](https://doi.org/10.3390/catal9050464) — 10.3390/catal9050464 | Not verified | Not verified | Not verified |
| [Glycerol Electro-Oxidation in Alkaline Media and Alkaline Direct Glycerol Fuel Cells](https://doi.org/10.3390/catal9120980) — 10.3390/catal9120980 | Not verified | Not verified | Not verified |
| [A Study on CO2 Methanation and Steam Methane Reforming over Commercial Ni/Calcium Aluminate Catalysts](https://doi.org/10.3390/en13112792) — 10.3390/en13112792 | Not verified | Not verified | Not verified |
| [Methane Cracking for Hydrogen Production: A Review of Catalytic and Molten Media Pyrolysis](https://doi.org/10.3390/en14113107) — 10.3390/en14113107 | Not verified | Not verified | Not verified |
| [Influence of Magnesium Oxide on the Structure and Catalytic Activity of the Wustite Catalyst for Ammonia Synthesis](https://doi.org/10.3390/ma15238309) — 10.3390/ma15238309 | Yes | Not verified | Yes |
| [Cobalt-based Catalysts for Ammonia Decomposition](https://doi.org/10.3390/ma6062400) — 10.3390/ma6062400 | Yes | Not verified | Not verified |
| [IrO2 Oxygen Evolution Catalysts Prepared by an Optimized Photodeposition Process on TiO2 Substrates](https://doi.org/10.3390/molecules29102392) — 10.3390/molecules29102392 | Yes | Not verified | Yes |
| [The Acid Roles of PtSn@Al2O3 in the Synthesis and Performance of Propane Dehydrogenation](https://doi.org/10.3390/molecules29132959) — 10.3390/molecules29132959 | Yes | Not verified | Yes |
| [Effects of Silica Shell Encapsulated Nanocrystals on Active χ-Fe5C2 Phase and Fischer–Tropsch Synthesis](https://doi.org/10.3390/nano12203704) — 10.3390/nano12203704 | Yes | Not verified | Yes |
| [Glycerol Electro-Oxidation in Alkaline Medium with Pt-Fe/C Electrocatalysts Synthesized by the Polyol Method: Increased Selectivity and Activity Provided by Less Expensive Catalysts](https://doi.org/10.3390/nano13071173) — 10.3390/nano13071173 | Yes | Not verified | Yes |
| [A Conceptual Approach for the Design of New Catalysts for Ammonia Synthesis: A Metal—Support Interactions Review](https://doi.org/10.3390/nano13222914) — 10.3390/nano13222914 | Yes | Not verified | Not verified |
| [Catalytic Behavior of Chromium Oxide Supported on Nanocasting-Prepared Mesoporous Alumina in Dehydrogenation of Propane](https://doi.org/10.3390/nano7090249) — 10.3390/nano7090249 | Yes | Yes | Yes |
