import { useLang } from '../lib/i18n';
import { blankRecipe, validRecipe, type ConsumableDraft, type RecipeDraft } from '../lib/recipe-inputs';

export function RecipeConsumptionFields({ value, onChange }: { value?: RecipeDraft; onChange: (value?: RecipeDraft) => void }) {
  const { t } = useLang();
  return <div className="mt-3 rounded-xl border border-slate-200 bg-white p-3">
    <label className="flex items-center gap-2 text-sm font-medium"><input type="checkbox" checked={Boolean(value)} onChange={(e) => onChange(e.target.checked ? blankRecipe() : undefined)} />{t('Use a purchased-precursor recipe')}</label>
    {value ? <>
      <p className="mt-2 text-xs leading-6 text-slate-600">{t('Enter the purchased precursor price. Content is the represented finished component in pure precursor; purity and retention yield are separate fractions. No markup or automatic solvent recovery is added.')}</p>
      <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        <label className="text-xs">{t('Purchased precursor')}<input className="input-base mt-1 w-full" value={value.precursor_name} onChange={(e) => onChange({ ...value, precursor_name: e.target.value })} /></label>
        <label className="text-xs">{t('Precursor purchase price (USD/kg)')}<input className="input-base mt-1 w-full" type="number" min="0" step="any" value={value.price_per_kg} onChange={(e) => onChange({ ...value, price_per_kg: e.target.value === '' ? '' : Number(e.target.value) })} /></label>
        {([
          ['retained_component_fraction', 'Component content in pure precursor (%)'],
          ['purity_fraction', 'Purchased precursor purity (%)'],
          ['yield_fraction', 'Component retention yield (%)'],
        ] as const).map(([key, label]) => <label key={key} className="text-xs">{t(label)}<input className="input-base mt-1 w-full" type="number" min="0" max="100" step="any" value={value[key] === '' ? '' : Number((value[key] * 100).toPrecision(12))} onChange={(e) => onChange({ ...value, [key]: e.target.value === '' ? '' : Number(e.target.value) / 100 })} /></label>)}
        <label className="text-xs sm:col-span-2 xl:col-span-3">{t('Recipe source or assumption')}<input className="input-base mt-1 w-full" value={value.source_note} onChange={(e) => onChange({ ...value, source_note: e.target.value })} /></label>
      </div>
      {!validRecipe(value) ? <p className="mt-2 text-xs text-amber-800">{t('Complete all recipe fields; percentages must be greater than zero and at most 100.')}</p> : null}
    </> : null}
  </div>;
}

export function ConsumablesFields({ value, onChange }: { value: ConsumableDraft[]; onChange: (value: ConsumableDraft[]) => void }) {
  const { t } = useLang();
  const update = (index: number, patch: Partial<ConsumableDraft>) => onChange(value.map((c, i) => i === index ? { ...c, ...patch } : c));
  return <div className="mt-4 rounded-xl border border-slate-200 bg-white p-4">
    <div className="flex flex-wrap items-center justify-between gap-3"><h3 className="font-semibold">{t('Solvent and washing consumption')}</h3><button className="cp-button-secondary" disabled={value.length >= 30} onClick={() => onChange([...value, { name: '', kg_per_kg_catalyst: '', price_per_kg: '', source_note: '' }])}>{t('Add purchased consumable')}</button></div>
    <p className="mt-2 text-xs leading-6 text-slate-600">{t('Net purchased kg per kg of finished catalyst. Enter recovered solvent only through a documented net purchase amount. These inputs change cost; their environmental impacts are not yet included.')}</p>
    {value.map((c, i) => <div key={i} className="mt-3 grid gap-3 rounded-lg border border-slate-200 p-3 sm:grid-cols-3">
      <label className="text-xs">{t('Consumable name')}<input className="input-base mt-1 w-full" value={c.name} onChange={(e) => update(i, { name: e.target.value })} /></label>
      <label className="text-xs">{t('Net purchase (kg/kg catalyst)')}<input className="input-base mt-1 w-full" type="number" min="0" step="any" value={c.kg_per_kg_catalyst} onChange={(e) => update(i, { kg_per_kg_catalyst: e.target.value === '' ? '' : Number(e.target.value) })} /></label>
      <label className="text-xs">{t('Consumable price (USD/kg)')}<input className="input-base mt-1 w-full" type="number" min="0" step="any" value={c.price_per_kg} onChange={(e) => update(i, { price_per_kg: e.target.value === '' ? '' : Number(e.target.value) })} /></label>
      <label className="text-xs sm:col-span-2">{t('Recipe source or assumption')}<input className="input-base mt-1 w-full" value={c.source_note} onChange={(e) => update(i, { source_note: e.target.value })} /></label>
      <button className="cp-button-secondary self-end" onClick={() => onChange(value.filter((_, j) => j !== i))}>{t('Remove consumable')}</button>
    </div>)}
  </div>;
}
