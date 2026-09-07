import { useState } from 'react';
import { fetchSavedEstimate, type PriceBasis, type SavedEstimateDetail, type SavedEstimateSummary } from '../lib/api';
import { compareSavedEstimates, type EstimateComparisonResult } from '../lib/estimate-comparison';
import { formatPrice } from '../lib/format-price';
import { useLang } from '../lib/i18n';
import { useUnit } from '../lib/use-unit';

interface Props {
  savedEstimates: SavedEstimateSummary[];
  priceBasis: PriceBasis;
}

export function SavedEstimateComparison({ savedEstimates, priceBasis }: Props) {
  const { t } = useLang();
  const { toDisplay, fmtLabel } = useUnit();
  const [selected, setSelected] = useState<number[]>([]);
  const [reference, setReference] = useState<SavedEstimateDetail | null>(null);
  const [orderSize, setOrderSize] = useState('20');
  const [result, setResult] = useState<EstimateComparisonResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const available = selected.filter((id) => savedEstimates.some((item) => item.id === id));
  const hasReference = reference !== null && available.includes(reference.id);
  const canShowResult = result !== null
    && result.common_conditions.price_basis === priceBasis
    && result.estimates.every((row) => available.includes(row.estimate_id));

  async function chooseReference(id: number) {
    setBusy(true);
    setError('');
    setResult(null);
    try {
      const detail = await fetchSavedEstimate(id);
      setReference(detail);
      setOrderSize(String(detail.order_size_tons));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    } finally {
      setBusy(false);
    }
  }

  async function runComparison() {
    if (!hasReference || !reference) return;
    setBusy(true);
    setError('');
    setResult(null);
    try {
      setResult(await compareSavedEstimates({
        estimate_ids: available,
        reference_estimate_id: reference.id,
        price_basis: priceBasis,
        order_size_tons: Number(orderSize),
      }));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    } finally {
      setBusy(false);
    }
  }

  const electrodeConditions = reference?.input.electrode_input as Record<string, unknown> | undefined;
  function displayPrice(value: number | null) {
    if (value === null) return t('Not available');
    return result?.unit === 'USD/cm2'
      ? `${formatPrice(value)}/cm²`
      : `${formatPrice(toDisplay(value))}${fmtLabel}`;
  }

  return (
    <section className="mt-4 surface-ghost p-4" aria-label={t('Compare saved estimates')}>
      <h3 className="text-base font-semibold text-slate-900">{t('Compare saved estimates')}</h3>
      <p className="mt-2 text-xs leading-6 text-slate-600">
        {t('Select 2–4 saved estimates in the same catalyst domain and application. Shared prices and operating conditions make differences easier to assess.')}
      </p>
      <div className="mt-3 grid max-h-56 gap-2 overflow-y-auto sm:grid-cols-2">
        {savedEstimates.map((saved) => (
          <label key={saved.id} className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white p-3 text-sm">
            <input type="checkbox" checked={available.includes(saved.id)}
              disabled={busy || (!available.includes(saved.id) && available.length >= 4)}
              onChange={(event) => {
                setSelected(event.target.checked ? [...available, saved.id] : available.filter((id) => id !== saved.id));
                setResult(null);
              }} />
            <span className="min-w-0 break-words">{saved.name}</span>
          </label>
        ))}
      </div>
      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <label className="text-xs font-semibold text-slate-600">
          {t('Reference estimate for common conditions')}
          <select value={hasReference ? reference!.id : ''} disabled={busy}
            onChange={(event) => { if (event.target.value) void chooseReference(Number(event.target.value)); }}
            className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm">
            <option value="">{t('Choose a reference estimate')}</option>
            {savedEstimates.filter((item) => available.includes(item.id)).map((item) => (
              <option key={item.id} value={item.id}>{item.name}</option>
            ))}
          </select>
        </label>
        <label className="text-xs font-semibold text-slate-600">
          {t('Shared production quantity (short tons)')}
          <input type="number" min="0.001" step="any" value={orderSize} disabled={busy}
            onChange={(event) => { setOrderSize(event.target.value); setResult(null); }}
            className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm" />
        </label>
      </div>
      {hasReference && reference ? (
        <div className="mt-3 rounded-xl border border-slate-200 bg-white p-3 text-xs leading-6 text-slate-600">
          <p>{t('Shared price basis')}: {priceBasis}</p>
          <p>{t('Target year')}: {String(reference.input.target_year ?? '')} · {t('G&A overhead')}: {Number(reference.input.ga_overhead_pct ?? 0) * 100}% · {t('SARD')}: {Number(reference.input.sard_pct ?? 0) * 100}%</p>
          <p>{t('Price-index base year')}: {String(reference.input.basis_year ?? '')} · {t('Reactor type')}: {String(reference.input.reactor_type ?? '')} · {t('Catalyst bulk density')}: {String(reference.input.catalyst_bulk_density ?? '')} lb/ft³</p>
          <p>{t('Recovery value')}: {reference.input.include_spent_value ? t('Included') : t('Not included')} · {t('Effective production rate')}: {reference.input.production_rate_ton_per_day == null ? t('Scale default') : `${reference.input.production_rate_ton_per_day} ${t('short ton/day')}`}</p>
          {electrodeConditions ? <p>{t('Active area')}: {String(electrodeConditions.active_area_cm2)} {t('cm² ·')} {t('Catalyst loading')}: {String(electrodeConditions.catalyst_loading_mg_cm2)} {t('mg/cm² ·')} {t('Ionomer / catalyst')}: {String(electrodeConditions.ionomer_to_catalyst_ratio)} · {t('Manufacturing scenario')}: {String(electrodeConditions.manufacturing_scenario ?? t('Not included'))}</p> : null}
          <p>{t('The reference also supplies the price-index base year, recovery assumptions and production-rate note. Composition, recipe amounts and manufacturing steps stay with each estimate.')}</p>
          <p>{t('For conflicting manual prices, the reference estimate takes priority; materials absent there use the lowest selected estimate ID. Precursor and consumable names must distinguish grades.')}</p>
        </div>
      ) : null}
      <button type="button" onClick={() => void runComparison()}
        disabled={busy || available.length < 2 || !hasReference || !Number.isFinite(Number(orderSize)) || Number(orderSize) <= 0}
        className="cp-button-primary mt-4">
        {busy ? t('Working…') : t('Compare under common conditions')}
      </button>
      {error ? <p role="alert" className="mt-3 text-sm text-red-700">{error}</p> : null}
      {result && canShowResult ? (
        <div className="mt-4 space-y-4">
          <p className="text-xs leading-6 text-slate-600">{result.unit === 'USD/cm2' ? t('Comparison metric: electrode assembly cost per area.') : t('Comparison metric: selling price including margin, less recovery value.')}</p>
          <div className="overflow-x-auto rounded-xl border border-slate-200">
            <table className="w-full min-w-[620px] bg-white text-left text-xs">
              <thead className="bg-slate-50"><tr>
                <th className="p-3">{t('Saved estimate')}</th>
                <th className="p-3">{t('Saved historical result')}</th>
                <th className="p-3">{t('Shared prices, original conditions')}</th>
                <th className="p-3">{t('Shared prices and conditions')}</th>
              </tr></thead>
              <tbody>{result.estimates.map((row) => (
                <tr key={row.estimate_id} className="border-t border-slate-200">
                  <th className="p-3 font-medium">{row.name}<span className="mt-1 block text-slate-500">{String(row.common_conditions.input_summary.composition ?? '')}</span><span className="mt-1 block text-slate-500">{row.common_conditions.route_summary?.name ?? t('Custom steps')}</span></th>
                  <td className="whitespace-nowrap p-3">{displayPrice(row.values.saved)}</td>
                  <td className="whitespace-nowrap p-3">{displayPrice(row.values.repriced_original_conditions)}</td>
                  <td className="whitespace-nowrap p-3 font-semibold">{displayPrice(row.values.common_conditions)}</td>
                </tr>
              ))}</tbody>
            </table>
          </div>
          <div className="rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs leading-6 text-amber-900">
            <p className="font-semibold">{t('Comparison limitations')}</p>
            {result.warnings.map((warning) => <p key={warning}>{warning}</p>)}
            {result.estimates.map((row) => <details key={row.estimate_id} className="mt-2">
              <summary>{row.name} · {t('Costing scope and warnings')}</summary>
              {row.common_conditions.costing_scope ? <>
                <p>{t('Costing status')}: {row.common_conditions.costing_scope.status}</p>
                <p>{row.common_conditions.costing_scope.boundary}</p>
                <p>{t('Uncosted operations')}: {row.common_conditions.costing_scope.uncosted_operations.join(', ') || t('None declared')}</p>
                <p>{t('Scale substitutions')}: {row.common_conditions.costing_scope.substitutions.map((item) => `${item.from} → ${item.to}`).join(', ') || t('None declared')}</p>
              </> : null}
              {(row.common_conditions.warnings ?? []).map((warning) => <p key={warning}>{warning}</p>)}
            </details>)}
          </div>
          <details className="rounded-xl border border-slate-200 bg-white p-3 text-xs">
            <summary className="cursor-pointer font-semibold">{t('Harmonized price snapshot')}</summary>
            {result.price_snapshot.map((price) => <div key={price.key} className="mt-2 border-t border-slate-100 pt-2 break-words">
              <p className="font-medium">{price.key}</p>
              <p>{Object.entries(price.values).map(([key, value]) => `${key}: ${value}`).join(' · ')}</p>
              <p>{t('Price source estimate')}: {price.source_estimate_name} (#{price.source_estimate_id}){price.overridden_estimate_ids.length ? ` · ${t('Replaced saved prices')}: ${price.overridden_estimate_ids.join(', ')}` : ''}</p>
            </div>)}
          </details>
        </div>
      ) : null}
    </section>
  );
}
