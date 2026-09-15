import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import test from 'node:test';

const require = createRequire(new URL('../frontend/package.json', import.meta.url));
const ts = require('typescript');
const { outputText } = ts.transpileModule(readFileSync(new URL('../frontend/src/lib/manufacturing.ts', import.meta.url), 'utf8'), {
  compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 },
});
const { adaptLiteratureProtocol, applyOperatingReference } = await import(`data:text/javascript;base64,${Buffer.from(outputText).toString('base64')}`);
const library = JSON.parse(readFileSync(new URL('../backend/data/manufacturing_literature.json', import.meta.url), 'utf8'));
const references = JSON.parse(readFileSync(new URL('../backend/data/manufacturing_operating_references.json', import.meta.url), 'utf8')).references;

test('import preserves specimen evidence and unknown prices without mutating the library', () => {
  const profile = library.profiles.find((p) => p.id === 'ni-silica-gen1-2024');
  const original = structuredClone(profile);
  const imported = adaptLiteratureProtocol(profile);
  assert.equal(imported.mode, 'record_only');
  assert.equal(imported.finished_batch_mass_kg, undefined);
  const item = imported.operations[0].purchases[0];
  assert.equal(item.input_evidence.quantity.recorded_value, 2);
  assert.equal(item.price_usd_per_unit, undefined);
  item.quantity = 3;
  assert.equal(item.input_evidence.quantity.recorded_value, 2);
  assert.deepEqual(profile, original);
});

test('tariff import is explicit, preserves other inputs, and detaches source snapshot', () => {
  const protocol = { mode: 'record_only', electricity_usd_kwh: 99, operations: [{ name: 'Synthetic operation' }] };
  const ref = references.find((r) => r.id === 'eia-us-industrial-2025-preliminary');
  const imported = applyOperatingReference(protocol, ref);
  assert.equal(imported.electricity_usd_kwh, 0.0862);
  assert.equal(protocol.electricity_usd_kwh, 99);
  assert.deepEqual(imported.operations, protocol.operations);
  imported.input_evidence.electricity_usd_kwh.recorded_value = 999;
  assert.equal(ref.evidence.recorded_value, 0.0862);
});

test('equipment ratings and historical wages cannot silently become operating inputs', () => {
  const protocol = { mode: 'record_only', operations: [{ name: 'Synthetic operation' }] };
  for (const ref of references.filter((r) => !r.import_field)) {
    assert.equal(applyOperatingReference(protocol, ref), protocol);
    assert.equal(protocol.labor_usd_h, undefined);
    assert.equal(protocol.operations[0].average_power_kw, undefined);
  }
});

test('literature aliquots retain unknown recovery and source values independently', () => {
  const profile = { ...library.profiles[0], intermediate_batches: [{ id: 'support', name: 'Synthetic support',
    produced_mass_kg: null, used_mass_kg: .001, input_evidence: { used_mass_kg: { kind: 'assumption', citation: 'Synthetic import', recorded_value: .001 } } }],
    operations: [{ name: 'Prepare support', intermediate_batch_id: 'support' }, { name: 'Use aliquot' }] };
  const imported = adaptLiteratureProtocol(profile);
  assert.equal(imported.intermediate_batches[0].produced_mass_kg, null);
  assert.equal(imported.operations[0].intermediate_batch_id, 'support');
  imported.intermediate_batches[0].used_mass_kg = .002;
  assert.equal(imported.intermediate_batches[0].input_evidence.used_mass_kg.recorded_value, .001);
  assert.equal(profile.intermediate_batches[0].used_mass_kg, .001);
});
