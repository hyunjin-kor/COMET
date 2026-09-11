import { ScientificText } from './shared/ScientificText';
import type { CostResult } from '../lib/api';
import { useLang } from '../lib/i18n';

export function PracticalCostingResult({ result }: { result: CostResult }) {
  const { t } = useLang();
  const recipes = result.materials.components.filter((c) => c.recipe_consumption);
  const consumables = result.materials.consumables ?? [];
  return <div className="mt-4 space-y-4">
    {result.input_summary.production_rate_ton_per_day != null ? <section className="rounded-xl border border-slate-200 bg-white p-4">
      <h3 className="font-semibold">{t('Effective production rate')}</h3>
      <p className="mt-2 text-sm"><ScientificText text={String(result.step_method.production_rate_ton_per_day)} /> {t('short ton/day')} · {result.step_method.campaign_days} {t('days')}</p>
      <p className="mt-2 text-xs text-slate-600"><ScientificText text={String(result.input_summary.production_rate_note ?? '')} /></p>
    </section> : null}
    {recipes.length || consumables.length ? <section className="rounded-xl border border-slate-200 bg-white p-4">
      <h3 className="font-semibold">{t('Purchased-input mass balance')}</h3>
      <p className="mt-2 text-xs leading-6 text-slate-600">{t('Purchases per kg of finished catalyst. Recipe costs replace the corresponding component cost. Environmental impacts of these additional inputs are not included.')}</p>
      <div className="mt-3 overflow-x-auto"><table className="w-full text-left text-sm"><thead><tr><th className="p-2">{t('Material')}</th><th className="p-2">{t('Net purchase (kg/kg catalyst)')}</th><th className="p-2">{t('Cost (USD/kg catalyst)')}</th><th className="p-2">{t('Recipe source or assumption')}</th></tr></thead><tbody>
        {recipes.map((c, i) => { const r = c.recipe_consumption!; return <tr key={i} className="border-t border-slate-200"><td className="p-2"><ScientificText text={r.precursor_name} /> → <ScientificText text={c.name} /><div className="text-xs text-slate-500">{t('Content / purity / yield')}: {[r.retained_component_fraction, r.purity_fraction, r.yield_fraction].map((v) => `${(v * 100).toFixed(2)}%`).join(' / ')}</div></td><td className="p-2">{r.purchased_kg_per_kg_catalyst.toFixed(6)}</td><td className="p-2">{r.cost_per_kg_catalyst.toFixed(4)}</td><td className="p-2"><ScientificText text={r.source_note} /></td></tr>; })}
        {consumables.map((c, i) => <tr key={`consumable-${i}`} className="border-t border-slate-200"><td className="p-2"><ScientificText text={c.name} /></td><td className="p-2">{c.kg_per_kg_catalyst}</td><td className="p-2">{(c.kg_per_kg_catalyst * c.price_per_kg).toFixed(4)}</td><td className="p-2"><ScientificText text={c.source_note} /></td></tr>)}
      </tbody></table></div>
    </section> : null}
    {result.purchase_evidence?.length ? <section className="rounded-xl border border-slate-200 bg-white p-4"><h3 className="font-semibold">{t('Local purchase evidence')}</h3><p className="mt-2 text-xs text-slate-600">{t('User-supplied records; not independently verified.')}</p>{result.purchase_evidence.map((c, i) => <div key={i} className="mt-3 border-t border-slate-200 pt-3 text-sm"><strong><ScientificText text={c.name} /></strong><dl className="mt-2 grid gap-2 sm:grid-cols-2">{Object.entries(c.evidence).filter(([, v]) => v != null && v !== '').map(([key, value]) => <div key={key}><dt className="text-xs text-slate-500">{t(({ supplier: 'Supplier', quote_date: 'Quote date', quantity: 'Purchase quantity', quantity_unit: 'Quantity unit', grade: 'Material grade', cost_boundary: 'Cost boundary', reference: 'Evidence reference', notes: 'Evidence notes' } as Record<string, string>)[key] ?? key)}</dt><dd><ScientificText text={String(value)} /></dd></div>)}</dl></div>)}</section> : null}
  </div>;
}
