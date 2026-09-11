import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import ts from '../frontend/node_modules/typescript/lib/typescript.js';

const source = readFileSync(new URL('../frontend/src/lib/scientific-text.ts', import.meta.url), 'utf8');
const js = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 } }).outputText;
const { formatScientificText: format, scientificSearchText } = await import(`data:text/javascript;base64,${Buffer.from(js).toString('base64')}`);

test('stoichiometry, repeated groups and hydrate coefficients have distinct positions', () => {
  assert.equal(format('Ni/Al2O3, Ni(NO3)2*6H2O; (NH4)6Mo7O24*4H2O'), 'Ni/Al₂O₃, Ni(NO₃)₂·6H₂O; (NH₄)₆Mo₇O₂₄·4H₂O');
  assert.equal(format('2H2 + O2 -> 2H2O'), '2H₂ + O₂ -> 2H₂O');
  assert.equal(format('Pt3Ni(111) / g-C3N4 / Fe-N4 / Ru/C12A7'), 'Pt₃Ni(111) / g-C₃N₄ / Fe-N₄ / Ru/C₁₂A₇');
  assert.equal(format('MoO2(acac)2'), 'MoO₂(acac)₂');
  assert.equal(format('C3-oxygenate selectivity; perovskite eg occupancy'), 'C₃-oxygenate selectivity; perovskite e_g occupancy');
  assert.equal(format('H2PtCl6*xH2O; (NH4)6H2W12O40*xH2O'), 'H₂PtCl₆·xH₂O; (NH₄)₆H₂W₁₂O₄₀·xH₂O');
});
test('fractional and variable stoichiometry are not mistaken for powers or model numbers', () => {
  assert.equal(format('Ba0.5Sr0.5Co0.8Fe0.2O3; CeO2-x; Fe1-xO; TaOx; CnH2n; CnH(2n+2)'), 'Ba₀.₅Sr₀.₅Co₀.₈Fe₀.₂O₃; CeO₂₋ₓ; Fe₁₋ₓO; TaOₓ; CₙH₂ₙ; CₙH₂ₙ₊₂');
});
test('ionic charge, zero-valent metals and explicitly identified isotope mass are superscripts', () => {
  assert.equal(format('Ni3+ Fe3+ Cu+-Ti3+ NH4+ OH- e- Co0 Pt0 15N2 SO4^2-'), 'Ni³⁺ Fe³⁺ Cu⁺-Ti³⁺ NH₄⁺ OH⁻ e⁻ Co⁰ Pt⁰ ¹⁵N₂ SO₄²⁻');
  assert.equal(format('C5+ hydrocarbons; CO2RR; CO2-eq'), 'C₅+ hydrocarbons; CO₂RR; CO₂-eq');
});
test('area, volume, inverse units and numerical powers use superscripts', () => {
  assert.equal(format('mg/cm2; mA cm-2; lb/ft3; cm3(STP); m2 g-1; mol h^-1; (size)^0.6'), 'mg/cm²; mA cm⁻²; lb/ft³; cm³(STP); m² g⁻¹; mol h⁻¹; (size)⁰.⁶');
});
test('URLs, DOI, identifiers, product grades and source ambiguities remain intact', () => {
  const untouched = 'Run estimate Can Sin Tin https://example.org/Al2O3.pdf?x=CO2 10.1234/CO2.2026 `Ni3+` Al2O3.csv CO2_route HS281820 ZSM-5 SAPO-34 XC72R D50-R GWP100a Figure S1 Table S38 Al23 Al203 A1203 2026-09-07 v1.4.0';
  assert.equal(format(untouched), untouched);
  assert.equal(format('P5 / P25 / P50 / P75 / P95'), 'P5 / P25 / P50 / P75 / P95');
});
test('formatting is idempotent and search accepts displayed subscripts and powers', () => {
  const text = 'Ni(NO3)2*6H2O; Fe3+; 15N2; CeO2-x; kg CO2-eq; cm2';
  assert.equal(format(format(text)), format(text));
  assert.equal(scientificSearchText('Al₂O₃ cm² Fe³⁺'), 'Al2O3 cm2 Fe3+');
});
