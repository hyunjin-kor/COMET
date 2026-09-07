import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import test from 'node:test';

const require = createRequire(new URL('../frontend/package.json', import.meta.url));
const ts = require('typescript');
const pageSource = readFileSync(new URL('../frontend/src/pages/Uncertainty.tsx', import.meta.url), 'utf8');
const syntax = ts.createSourceFile('Uncertainty.tsx', pageSource, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
const declarations = new Map();
function visit(node) {
  if (ts.isFunctionDeclaration(node) && node.name) declarations.set(node.name.text, node.getText(syntax));
  ts.forEachChild(node, visit);
}
visit(syntax);
function loadFunction(name, dependencies = {}) {
  assert.ok(declarations.has(name), `Missing actual page function ${name}`);
  const { outputText } = ts.transpileModule(declarations.get(name), {
    compilerOptions: { target: ts.ScriptTarget.ES2022 },
  });
  return new Function(...Object.keys(dependencies), `${outputText}\nreturn ${name};`)(...Object.values(dependencies));
}
const { outputText } = ts.transpileModule(readFileSync(new URL('../frontend/src/lib/recipe-inputs.ts', import.meta.url), 'utf8'), {
  compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 },
});
const { validRecipe, validConsumables, blankRecipe } = await import(`data:text/javascript;base64,${Buffer.from(outputText).toString('base64')}`);
const buildRangeInputFromDraft = loadFunction('buildRangeInputFromDraft', { validRecipe, validConsumables });
const recipe = { precursor_name: 'Synthetic Ni precursor', retained_component_fraction: 0.25, purity_fraction: 0.8, yield_fraction: 0.5, price_per_kg: 5, source_note: 'Synthetic arithmetic fixture' };
const purchase = { supplier: 'Synthetic supplier', quote_date: '2026-05-07', quantity: 10, quantity_unit: 'kg', grade: 'Fixture', cost_boundary: 'Retained metal, no transport', reference: 'No actual purchase' };
const draft = () => ({
  catalystDomain: 'thermal', applicationFamily: 'general', orderSize: 20, steps: ['mixer_slurry'], pricesUpdatedAt: null,
  rows: [
    { id: 'active', role: 'active_metal', name: 'Ni', wt_pct: 20, price_per_lb: 7, source_type: 'manual', source: '' },
    { id: 'support', role: 'support', name: 'Al2O3', wt_pct: 75, price_per_lb: 999, material_key: 'lit:support', source_type: 'indexed', source: '' },
  ],
});

test('range preserves precursor consumption, purchase evidence, throughput, consumables and template identity', () => {
  const value = draft();
  Object.assign(value, { thermalTemplateId: 'hydrothermal_oxide_nanostructure', productionRate: 5, productionRateNote: 'Synthetic 5 short ton/day', consumables: [{ name: 'Wash', kg_per_kg_catalyst: 3, price_per_kg: 0.5, source_note: 'Synthetic fixture' }] });
  Object.assign(value.rows[0], { recipe_consumption: recipe, purchase_evidence: purchase });
  const original = structuredClone(value);
  const input = buildRangeInputFromDraft(value);
  assert.equal(input.template_id, value.thermalTemplateId);
  assert.equal(input.production_rate_ton_per_day, 5);
  assert.equal(input.production_rate_note, value.productionRateNote);
  assert.deepEqual(input.consumables, value.consumables);
  assert.deepEqual(input.components[0].recipe_consumption, recipe);
  assert.deepEqual(input.components[0].purchase_evidence, purchase);
  assert.equal(input.components[1].wt_pct, 80);
  assert.equal(input.components[1].price_per_lb, undefined);
  assert.deepEqual(value, original);
});

test('range rejects incomplete recipes, zero retention, missing production evidence and incomplete wash inputs', () => {
  for (const invalidRecipe of [blankRecipe(), { ...recipe, price_per_kg: '' }, { ...recipe, yield_fraction: 0 }]) {
    const value = draft();
    value.rows[0].recipe_consumption = invalidRecipe;
    assert.equal(buildRangeInputFromDraft(value), null);
  }
  assert.equal(buildRangeInputFromDraft({ ...draft(), productionRate: 5, productionRateNote: '' }), null);
  assert.equal(buildRangeInputFromDraft({ ...draft(), productionRate: Infinity, productionRateNote: 'Fixture' }), null);
  assert.equal(buildRangeInputFromDraft({ ...draft(), consumables: [{ name: 'Wash', kg_per_kg_catalyst: '', price_per_kg: 0.5, source_note: 'Fixture' }] }), null);
});

test('old thermal drafts retain nominal throughput, balanced support and legacy recovery defaults', () => {
  const input = buildRangeInputFromDraft(draft());
  assert.equal(input.production_rate_ton_per_day, undefined);
  assert.equal(input.template_id, undefined);
  assert.equal(input.consumables, undefined);
  assert.equal(input.include_spent_value, false);
  assert.equal(input.reactor_type, 'fixed');
  assert.equal(input.catalyst_bulk_density, 50);
  assert.equal(input.components[0].price_per_lb, 7);
  assert.equal(input.components[1].wt_pct, 80);
  assert.equal(buildRangeInputFromDraft({ ...draft(), productionRate: '' }).production_rate_ton_per_day, undefined);
});

test('split support retains each fraction and each optional recipe instead of auto-balancing one row', () => {
  const value = draft();
  value.rows[1].wt_pct = 50;
  value.rows[1].recipe_consumption = recipe;
  value.rows.push({ ...value.rows[1], id: 'support2', name: 'Carbon', wt_pct: 30, recipe_consumption: undefined });
  const input = buildRangeInputFromDraft(value);
  assert.deepEqual(input.components.map((c) => c.wt_pct), [20, 50, 30]);
  assert.deepEqual(input.components[1].recipe_consumption, recipe);
  value.rows[2].wt_pct = 29;
  assert.equal(buildRangeInputFromDraft(value), null);
});

test('electrode range preserves its manufacturing scenario and material stack without thermal additions', () => {
  const input = buildRangeInputFromDraft({ ...draft(), catalystDomain: 'electrocatalyst', productionRate: 5, consumables: [{ name: 'Ignored thermal draft' }], electrocatalystConfig: {
    catalystMaterialKey: 'powder', ionomerMaterialKey: 'ionomer', membraneMaterialKey: 'membrane', substrateMaterialKey: 'substrate', activeAreaCm2: 25, catalystLoadingMgCm2: 0.5, ionomerToCatalystRatio: 0.3, templateId: 'pem_fuel_cell_ccm', manufacturingScenario: 'pilot_roll_to_roll',
  } });
  assert.equal(input.electrode_input.manufacturing_scenario, 'pilot_roll_to_roll');
  assert.equal(input.electrode_input.catalyst_material_key, 'powder');
  assert.equal(input.template_id, 'pem_fuel_cell_ccm');
  assert.equal(input.production_rate_ton_per_day, undefined);
  assert.equal(input.consumables, undefined);
});

test('the real range handler passes the currently selected reference price basis with the full draft input', async () => {
  const calculationInput = buildRangeInputFromDraft(draft());
  const calls = [];
  const handleRun = loadFunction('handleRun', {
    calculationInput, draft: draft(), basis: 'reference', nSim: 1000,
    activeBandPct: 30, promoterBandPct: 20, supportBandPct: 20, adjunctBandPct: 15, orderBandPct: 20,
    bandBounds: loadFunction('bandBounds'), setLoading() {}, setError(error) { assert.equal(error, ''); }, setResult() {}, setActiveSection() {},
    async runEstimateRange(...args) { calls.push(args); return {}; },
  });
  await handleRun();
  assert.equal(calls.length, 1);
  assert.deepEqual(calls[0][0], { ...calculationInput, price_basis: 'reference' });
  assert.equal(calls[0][1], 1000);
});
