import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import test from 'node:test';

const require = createRequire(new URL('../frontend/package.json', import.meta.url));
const ts = require('typescript');
async function loadHelper(name) {
  const source = readFileSync(new URL(`../frontend/src/lib/${name}.ts`, import.meta.url), 'utf8');
  const { outputText } = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 },
  });
  return import(`data:text/javascript;base64,${Buffer.from(outputText).toString('base64')}`);
}

const { sameSteps, matchThermalTemplate, isThermalTemplateReady, togglePreparationStep, fitPreparationSelection } = await loadHelper('preparation-selection');
const { compareElectroPreference } = await loadHelper('electrode-defaults');
const { electrodeCostRows } = await loadHelper('electrode-result');
const { blankRecipe, validRecipe, validConsumables } = await loadHelper('recipe-inputs');
const { buildResultCsv } = await loadHelper('export-csv');

test('optional recipes reject incomplete values, zero yield and double interpretation of percentages', () => {
  assert.equal(validRecipe(undefined), true);
  assert.equal(validRecipe(blankRecipe()), false);
  const recipe = { precursor_name: 'Synthetic precursor', source_note: 'Arithmetic fixture', retained_component_fraction: 0.25, purity_fraction: 0.8, yield_fraction: 0.5, price_per_kg: 5 };
  assert.equal(validRecipe(recipe), true);
  assert.equal(validRecipe({ ...recipe, yield_fraction: 0 }), false);
  assert.equal(validRecipe({ ...recipe, purity_fraction: 80 }), false);
  assert.equal(validRecipe({ ...recipe, price_per_kg: '' }), false);
  assert.equal(validConsumables([]), true);
  assert.equal(validConsumables([{ name: 'Wash', source_note: 'Synthetic', kg_per_kg_catalyst: 3, price_per_kg: .5 }]), true);
  assert.equal(validConsumables([{ name: 'Wash', source_note: '', kg_per_kg_catalyst: 3, price_per_kg: .5 }]), false);
});

test('CSV preserves calculation scope, production assumptions and purchased-input evidence', () => {
  const result = {
    input_summary: { composition: 'Synthetic fixture', production_rate_ton_per_day: 5, production_rate_note: 'Measured-rate fixture' },
    summary: { estimated_price_per_lb: 20, estimated_price_per_kg: 44, net_cost_per_lb: 19, net_cost_per_kg: 42 },
    step_method: { scale: 'medium', campaign_days: 5, margin_pct: 20, processing_cost_per_lb: 2 },
    materials: { total_materials_cost_per_lb: 10, components: [{ name: 'Ni', role: 'active_metal', wt_pct: 20, price_per_lb: 8, precursor_markup: 1, cost_per_lb_cat: 5, cost_pct: 50,
      recipe_consumption: { precursor_name: 'Synthetic precursor', retained_component_fraction: .25, purity_fraction: .8, yield_fraction: .5, price_per_kg: 5, purchased_kg_per_kg_catalyst: 2, cost_per_kg_catalyst: 10, source_note: 'Synthetic recipe' } }],
      consumables: [{ name: 'Synthetic wash', kg_per_kg_catalyst: 3, price_per_kg: .5, cost_per_lb_cat: .68, source_note: 'Net purchase fixture' }] },
    purchase_evidence: [{ name: 'Ni', price_per_lb: 8, evidence: { supplier: 'Supplier, synthetic', quote_date: '2026-05-07', grade: 'Test only' } }],
    costing_scope: { status: 'partial', boundary: 'Selected operations only', actual_steps: ['mix'], costed_steps: [], substitutions: [], dropped_steps: ['centrifuge'], omitted_template_steps: [], added_steps: [], uncosted_operations: ['Pressure vessel uncosted'], route_modified: false },
  };
  const csv = buildResultCsv({ result, generatedAt: '2026-09-07', orderSize: 20, stepLabels: ['Mix'], steps: ['mix'] });
  for (const text of ['Measured-rate fixture', 'Synthetic precursor', 'Synthetic wash', '"Supplier, synthetic"', 'Pressure vessel uncosted', 'centrifuge', '2026-05-07']) assert.ok(csv.includes(text), text);
});

test('repeated operations remain distinct while order-only changes match', () => {
  assert.equal(sameSteps(['mix', 'mix', 'dry'], ['mix', 'dry', 'dry']), false);
  assert.equal(sameSteps(['mix', 'mix', 'dry'], ['dry', 'mix', 'mix']), true);
});

test('unchecking and rechecking a repeated operation restores its count and original sequence', () => {
  const basis = ['mix', 'react', 'filter', 'react', 'dry', 'react'];
  const before = { steps: [...basis], basis: [...basis] };
  const off = togglePreparationStep(before, 'react');
  assert.deepEqual(off.steps, ['mix', 'filter', 'dry']);
  assert.deepEqual(togglePreparationStep(off, 'react'), before);
  assert.deepEqual(before.steps, basis);
});

test('interleaved step toggles preserve other edits and restore repeated operations after draft reload', () => {
  const initial = { steps: ['mix', 'react', 'dry', 'react'], basis: ['mix', 'react', 'dry', 'react'] };
  let state = togglePreparationStep(initial, 'react');
  state = togglePreparationStep(state, 'dry');
  state = togglePreparationStep(state, 'mill');
  state = togglePreparationStep(JSON.parse(JSON.stringify(state)), 'react');
  assert.deepEqual(state.steps, ['mix', 'react', 'react', 'mill']);
  state = togglePreparationStep(state, 'dry');
  assert.deepEqual(state.steps, ['mix', 'react', 'dry', 'react', 'mill']);
});

test('scale fitting keeps deliberate omissions and additions including an in-flight manual edit', () => {
  const cost = { steps_fitted: ['mix', 'kiln_continuous', 'filter', 'filter'], substitutions: [{from:'kiln_batch',to:'kiln_continuous'}] };
  const selection = { basis: ['mix', 'kiln_batch', 'filter', 'filter'], steps: ['mix', 'filter', 'filter', 'mill'] };
  const fitted = fitPreparationSelection(selection, cost, ['mix','kiln_continuous','filter','mill']);
  assert.deepEqual(fitted.steps, ['mix','filter','filter','mill']);
  assert.deepEqual(togglePreparationStep(fitted, 'kiln_continuous').steps, ['mix','kiln_continuous','filter','filter','mill']);
  assert.equal(isThermalTemplateReady('selected', {selected:cost}, fitted.steps, 20, 20, true), true);
  assert.equal(isThermalTemplateReady('selected', {selected:cost}, fitted.steps, 200, 20, true), false);
});

test('editing a chosen method never silently adopts another method with matching steps', () => {
  const templates = [{id:'chosen',steps:['mix','dry']},{id:'other',steps:['mix']}];
  assert.equal(matchThermalTemplate(templates, {}, ['mix'], 'chosen'), null);
  assert.equal(matchThermalTemplate(templates, {}, ['mix'], null), null);
  assert.equal(matchThermalTemplate(templates, {}, ['mix','dry'], 'chosen').id, 'chosen');
});

test('returning to a smaller scale does not reinsert a deliberately removed substituted kiln', () => {
  const selection = {steps:['mix'],basis:['mix','kiln_continuous'],substitutions:[{from:'kiln_batch',to:'kiln_continuous'}]};
  const small = fitPreparationSelection(selection, {steps_fitted:['mix','kiln_batch'],substitutions:[]}, ['mix','kiln_batch']);
  assert.deepEqual(small.steps, ['mix']);
  assert.deepEqual(togglePreparationStep(small, 'kiln_batch').steps, ['mix','kiln_batch']);
});

test('selected card identity survives identical routes and scale fitting', () => {
  const templates = ['first', 'selected'].map((id) => ({ id, name: id, steps: ['mix', 'kiln_batch'] }));
  assert.equal(matchThermalTemplate(templates, {}, templates[0].steps, 'selected').id, 'selected');
  assert.equal(matchThermalTemplate(templates, {}, templates[0].steps, null), null);
  const fitted = Object.fromEntries(templates.map(({ id }) => [id, { steps_fitted: ['mix', 'kiln_continuous_indirect'] }]));
  assert.equal(matchThermalTemplate(templates, fitted, fitted.selected.steps_fitted, 'selected').id, 'selected');
  assert.equal(matchThermalTemplate(templates, fitted, ['mix'], 'selected'), null);
});

test('selected method waits for current-scale steps, while manual routes stay usable', () => {
  const costs = { selected: { steps_fitted: ['mix', 'kiln_batch'] } };
  assert.equal(isThermalTemplateReady('selected', {}, ['mix'], 2, null), false);
  assert.equal(isThermalTemplateReady('selected', costs, ['mix', 'kiln_batch'], 2, 20), false);
  assert.equal(isThermalTemplateReady('selected', costs, ['mix', 'kiln_continuous'], 2, 2), false);
  assert.equal(isThermalTemplateReady('selected', costs, ['mix', 'kiln_batch'], 2, 2), true);
  assert.equal(isThermalTemplateReady(null, {}, ['mix'], 2, null), true);
});

const categories = ['Electrocatalyst Powder', 'Ionomer', 'Membrane', 'Gas Diffusion Layer'];
const candidates = {
  'Electrocatalyst Powder': ['Pt', 'PtRu', 'Ir', 'Ru', 'Ni', 'Ag'].map((symbol) => ({ name: symbol, symbol })),
  Ionomer: [{ name: 'PFSA dispersion' }, { name: 'AEM dispersion' }],
  Membrane: [{ name: 'PFSA membrane' }, { name: 'AEM membrane' }],
  'Gas Diffusion Layer': [{ name: 'Carbon paper' }, { name: 'Titanium PTL' }, { name: 'Nickel foam' }],
};
for (const [family, template, expected] of [
  ['fuel_cell', 'pem_fuel_cell_ccm', ['Pt', 'PFSA dispersion', 'PFSA membrane', 'Carbon paper']],
  ['direct_methanol_fuel_cell', 'dmfc_gde_route', ['PtRu', 'PFSA dispersion', 'PFSA membrane', 'Carbon paper']],
  ['electrolyzer', 'pem_electrolyzer_ccm', ['Ir', 'PFSA dispersion', 'PFSA membrane', 'Titanium PTL']],
  ['electrolyzer', 'alkaline_electrolyzer_gde', ['Ni', 'AEM dispersion', 'AEM membrane', 'Nickel foam']],
]) {
  test(`${family} × ${template} defaults`, () => {
    const chosen = categories.map((category) => [...candidates[category]].reverse().sort((left, right) =>
      compareElectroPreference(left, right, category, family, template))[0].name);
    assert.deepEqual(chosen, expected);
  });
}

test('AEM fuel-cell route retains existing application-family preference', () => {
  const exact = { name: 'Exact family', application_family: 'fuel_cell', price: 100 };
  const general = { name: 'General', application_family: 'general', price: 1 };
  assert.ok(compareElectroPreference(exact, general, 'Electrocatalyst Powder', 'fuel_cell', 'aem_fuel_cell_ccm') < 0);
});

test('equal chemistry ranks prefer source scope, then quoted price, then name', () => {
  const compare = (left, right) => compareElectroPreference(left, right, 'Ionomer', 'fuel_cell', 'pem_fuel_cell_ccm');
  const base = { name: 'PFSA A', price_scope: 'vendor_lab', price: 10 };
  assert.ok(compare({ ...base, price_scope: 'literature_high_volume', price: 100 }, base) < 0);
  assert.ok(compare({ ...base, price: 5 }, base) < 0);
  assert.ok(compare(base, { ...base, name: 'PFSA B' }) < 0);
});

test('electrode displayed ledger uses area costs without thermal cost fields', () => {
  const result = {
    electrode_model: { active_area_cm2: 25, total_cost_usd: 5, breakdown: [
      { label: 'Catalyst powder', cost_usd: 2 }, { label: 'Membrane', cost_usd: 3 },
    ] },
    materials: { total_materials_cost_per_lb: 999999 },
    step_method: { processing_cost_per_lb: 888888, ga_per_lb: 777777, margin_pct: 66 },
    spent_catalyst: { V_reclaimed_per_lb: 555555 },
  };
  const rows = electrodeCostRows(result);
  assert.deepEqual(rows.map((row) => row.label), ['Catalyst powder', 'Membrane']);
  assert.equal(rows.reduce((sum, row) => sum + row.costPerCm2, 0), 0.2);
  assert.equal(rows.reduce((sum, row) => sum + row.share, 0), 100);
  assert.deepEqual(electrodeCostRows({ electrode_model: result.electrode_model }), rows);
  assert.equal(electrodeCostRows({ electrode_model: null }), null);
});
