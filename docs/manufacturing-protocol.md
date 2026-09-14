# Detailed catalyst manufacturing protocols

The thermal calculator's **Preparation Method → Detailed manufacturing protocol**
records an ordered laboratory or production protocol. Operations can be repeated,
duplicated, reordered and named independently, including successive impregnation,
evaporation, drying, calcination, reduction and washing treatments. No synthesis
conditions are inferred from a catalyst name or a literature-template label.

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
- Processing USD/kg = total repeated operation cost / finished dry batch mass.

Gas flow and price must refer to the same temperature and pressure. The model does
not convert actual flow to standard flow automatically. Premixed gas is priced as
the purchased mixture. Every operation's time, electricity, gas and cost are
multiplied by its repetition count.

The materials calculation retains its explicit precursor-content, purity, retention
yield and purchased-consumable inputs. Solvent volumes in the protocol are records;
they do not add another solvent charge. Final dry batch mass is a denominator, not
an automatic reaction-yield or material-balance calculation. Intermediate-product
transfers and losses require documented material inputs and notes.

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
response field in batch mode is this serial sum × batch equivalents / 24, not
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
