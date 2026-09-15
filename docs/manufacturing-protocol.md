# Detailed catalyst manufacturing protocols

The calculator's **Preparation Method → Detailed manufacturing protocol**
records an ordered laboratory or production protocol. Operations can be repeated,
duplicated, reordered and named independently, including successive impregnation,
evaporation, drying, calcination, reduction and washing treatments. No synthesis
conditions are inferred from a catalyst name or a literature-template label.

## Literature preparations

**Choose a literature preparation** opens the named-specimen library. Each record
includes its primary source, verified DOI, section locator, ordered operations and
unresolved inputs. Selecting it creates an editable `record_only` protocol; it does
not replace composition, precursor purchases or headline costs. The source record ID
and citation travel with saved inputs and CSV exports. Edits are user adaptations,
not new source-verified conditions.

The [preparation evidence supplement](paper/manufacturing-literature-2026-09-14.md)
documents the audit of all 116 candidates and 34 generic templates. It separates
source/formulation discrepancies, available source-specific variants, and unverified
preparations. A DOI check establishes bibliographic identity; it does not verify a
recipe or its manufacturing cost. Reaction-temperature windows in candidate cards
are labeled as reaction conditions and must not be copied into synthesis fields.

Unreported values remain blank. A reported range or “overnight” stays in source
notes; nominal loading and precursor molar ratios do not become measured mass
fractions. Supplied catalysts and characterization treatments do not disclose
manufacturing. Powder manufacture, activation and electrode assembly must be
reviewed separately before defining the delivered-product boundary.

Both thermal and electrochemical cases can retain preparation records. Only thermal
powder cases support the optional detailed batch-cost model. Electrode records cannot
use a powder kg denominator, even when all numerical fields have been filled.
The existing electrode area-cost model remains separate.

Curated facts are maintained in `backend/data/manufacturing_literature.json`.
After updating that source, run `python scripts/build_manufacturing_literature_review.py`
to regenerate the supplement and its count/hash record; `--check` detects drift.
Source article PDFs and private author attachments are not redistributed.

Each operation can record equipment, atmosphere, absolute pressure, stirring speed,
pH, solvent volume, addition details and source notes. A temperature program stores
successive target temperatures, ramp rates and hold times. Cooling can be a downward
temperature segment or explicitly entered additional time. Reduction and purge gases
have their own flow, use duration, purchase price and volume reference conditions.

## Recording conditions and calculating costs

**Record conditions** preserves incomplete protocols alongside the empirical Step
Method estimate. The headline cost remains unchanged. Unknown fields stay blank,
and incomplete detailed operating costs are returned as unavailable, never zero.

**Batch operating inputs** replaces Step Method processing costs. It requires the
finished dry batch output, electricity and labor rates, a source/assumption note,
and complete operating cost inputs for every operation. Enter zero explicitly for
excluded costs. The model does not add Step Method equipment rates or automatically
escalate the entered rates. Equipment-only rates must exclude the separately entered
electricity, gas and labor charges. Attended labor is person-hours, not the entire
duration of an unattended overnight treatment.

The calculation uses:

- Ramp hours = absolute temperature change / ramp rate / 60.
- Operation hours = ramp hours + hold hours + additional setup/cleaning/cooling hours.
- Electricity = measured input kWh **or** the sum of mean input kW × hours.
- Gas volume (m³) = flow (L/min) × use hours × 60 / 1,000.
- Operation cost = electricity + equipment hours × equipment-only rate + attended
  person-hours × labor rate + gas purchases + other explicit charges.
- Processing USD/kg = total allocated repeated operation cost / finished dry batch mass.

Gas flow and price must refer to the same temperature and pressure. The model does
not convert actual flow to standard flow automatically. Premixed gas is priced as
the purchased mixture. Every operation's time, electricity, gas and cost are
multiplied by its repetition count.

The composition basis retains explicit precursor-content, purity, retention-yield
and kg/kg purchased-consumable inputs. Alternatively, batch purchases replace that
entire materials bill: quantity × matching-unit price × repetitions × allocation
fraction / final dry kg. A solvent purchase can follow the operation's mL volume.
Prices, density, purity corrections and solvent recovery are not inferred. Flowing
gas purchases remain processing charges. Final dry mass is a measured or explicitly
assumed denominator, not an automatic reaction-yield calculation.

### Intermediate batches and aliquots

An intermediate batch can feed another intermediate or the final batch.
Assign all operations preparing that intermediate to its named batch. Record the
mass recovered from the entire declared batch (including repeated operations) and
the mass transferred to its receiving batch on the same material and mass basis.
Purchases, electricity, gas, equipment, labor and additional charges receive the
same **used mass / recovered mass** allocation. Successive transfers multiply the
fractions along the path to the final batch. Missing masses prevent proportional
costing; the schema rejects mass used above recovered mass and undefined batches.

This allocation assumes unused recoverable material retains its share of cost.
It does not reduce cash expenditure for the complete intermediate batch. To charge
all that expenditure to the final product (for example, a one-off preparation with
no inventory credit), explicitly select **whole batch**. Unknown intermediate
recovery remains a record in that mode and is not needed to invent a cost fraction.
Final dry output is required in both modes. Internally transferred intermediates
must not be entered again as purchased materials. Each intermediate has one receiving
batch, and circular transfers are rejected. Branching one intermediate into multiple
destinations, co-product allocation, inventory scheduling and automatic loss balances
are not modeled. Record such boundaries separately before costing.

The report preserves whole-batch purchase quantities, operation time, electricity,
incurred charges, allocation fractions and allocated final-product costs. CSV/JSON
exports retain both incurred and allocated charges. Input sources retain original
values when recovery or transfer assumptions are edited. The trace links each
allocation through materials and processing contributions to the selling price.

The result separates **materials + processing** from the subsequent G&A/SARD
adjustments and user-entered selling margin. Batch mode defaults to zero selling
margin, rather than applying an industrial order-size margin correlation to a
gram-scale experiment. The existing G&A/SARD inputs remain applicable.

## Interpretation and boundaries

Measured kWh or mean input power should represent the actual operating conditions,
including equipment losses. A temperature setpoint alone does not determine energy.
Holding time affects power-based electricity and equipment occupancy; changing a
target temperature also changes the ramp duration at a fixed ramp rate. Measured
kWh stays fixed until the user updates it. Temperature, pressure, pH, atmosphere
and stirring speed do not automatically predict conversion, yield or catalyst
performance. These variables can be compared through separately saved cases.

Power-times-duration follows dimensional energy accounting. Electricity consumption
is expressed in kWh; see the US Department of Energy's [Electricity 101](https://www.energy.gov/oe/electricity-101).
Industrial furnace duty also depends on stored heat and heat-loss pathways; see
DOE's [process-heating sourcebook](https://www.energy.gov/sites/default/files/2014/05/f15/process_heating_sourcebook2.pdf).
COMET therefore does not substitute solid sensible heat for measured furnace input.
No equipment power, gas price or laboratory-to-industrial scaling factor is supplied
as if it were measured evidence.

Order totals repeat the reference batch costs linearly, including fractional batch
equivalents. There is no economy of scale, integer-batch scheduling or automatic
equipment resizing. Time is the sum of operation-hours; parallel work, equipment
sharing and unattended overlap are not scheduled. The legacy `campaign_days`
response field in batch mode is allocated operation-hours × batch equivalents / 24, not
observed plant lead time. Batch-mode environmental results cover materials only;
the detailed utility inputs are not yet mapped to process LCA.

## Saved cases, export and comparisons

The complete protocol travels with calculator drafts, saved inputs/results and CSV
exports (including a lossless protocol JSON field). Existing saved cases remain
compatible and keep Step Method behavior. Batch/Step Method mixed comparisons are
rejected. Batch comparisons preserve each protocol, dry batch output, equipment
rates and gas prices; the common-conditions column additionally shares the reference
electricity tariff, labor rate and margin. This is not complete procurement-price
harmonization across all operating inputs.

Monte Carlo uses the chosen manufacturing model but keeps protocol conditions,
batch yield and operating rates fixed. Its current intervals sample the existing
material-price/order inputs, not temperature/time/utility uncertainty. Neither this
extension nor its synthetic regression tests establish industrial cost accuracy.
