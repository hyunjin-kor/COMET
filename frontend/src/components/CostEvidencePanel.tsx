import { useEffect, useState, type FormEvent } from 'react';
import { useLang } from '../lib/i18n';
import {
  addCostObservation,
  fetchCostObservations,
  type ActualCostObservation,
  type CostObservationSummary,
  type PurchaseEvidence,
} from '../lib/cost-evidence';

const inputClass = 'w-full min-w-0 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800';

export function PurchaseEvidenceFields({ value, onChange }: {
  value?: PurchaseEvidence;
  onChange: (value: PurchaseEvidence | undefined) => void;
}) {
  const { t } = useLang();
  const evidence = value ?? {};
  const update = (key: keyof PurchaseEvidence, next: string | number | undefined) => {
    const updated = { ...evidence, [key]: next };
    onChange(Object.values(updated).some((item) => item !== undefined && item !== '') ? updated : undefined);
  };
  return (
    <details className="mt-2 rounded-lg border border-slate-200 bg-slate-50 p-3">
      <summary className="cursor-pointer text-sm font-medium text-slate-700">{t('Purchase evidence (optional)')}</summary>
      <p className="mt-2 text-xs leading-5 text-slate-500">{t('Stored with this estimate on this device. User-supplied evidence is not independently verified.')}</p>
      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        <label className="text-xs text-slate-600">{t('Supplier')}<input className={inputClass} value={evidence.supplier ?? ''} onChange={(event) => update('supplier', event.target.value || undefined)} maxLength={300} /></label>
        <label className="text-xs text-slate-600">{t('Quote date')}<input className={inputClass} type="date" value={evidence.quote_date ?? ''} onChange={(event) => update('quote_date', event.target.value || undefined)} /></label>
        <label className="text-xs text-slate-600">{t('Purchase quantity')}<input className={inputClass} type="number" min="0.000001" step="any" value={evidence.quantity ?? ''} onChange={(event) => update('quantity', event.target.value === '' ? undefined : Number(event.target.value))} /></label>
        <label className="text-xs text-slate-600">{t('Purchase quantity unit')}<input className={inputClass} value={evidence.quantity_unit ?? ''} onChange={(event) => update('quantity_unit', event.target.value || undefined)} maxLength={40} /></label>
        <label className="text-xs text-slate-600">{t('Material grade')}<input className={inputClass} value={evidence.grade ?? ''} onChange={(event) => update('grade', event.target.value || undefined)} maxLength={300} /></label>
        <label className="text-xs text-slate-600">{t('Purchase cost inclusions')}<input className={inputClass} value={evidence.cost_boundary ?? ''} onChange={(event) => update('cost_boundary', event.target.value || undefined)} maxLength={500} /></label>
        <label className="text-xs text-slate-600 sm:col-span-2">{t('Local document reference or source URL')}<input className={inputClass} value={evidence.reference ?? ''} onChange={(event) => update('reference', event.target.value || undefined)} maxLength={1000} /></label>
        <label className="text-xs text-slate-600 sm:col-span-2">{t('Purchase evidence notes')}<textarea className={inputClass} value={evidence.notes ?? ''} onChange={(event) => update('notes', event.target.value || undefined)} maxLength={2000} rows={2} /></label>
      </div>
    </details>
  );
}

type ObservationDraft = {
  price: string; currency: string; unit: ActualCostObservation['price_unit']; date: string;
  month: string; quantity: string; rate: string; template: string; steps: string;
  components: { name: string; wt: string; grade: string }[];
  boundary: ActualCostObservation['cost_boundary']; source: string;
  evidenceType: ActualCostObservation['evidence_type']; scopeNote: string;
  conditionsNote: string; notes: string; confirmed: boolean;
};

function emptyDraft(): ObservationDraft {
  return {
    price: '', currency: 'USD', unit: 'kg', date: '', month: '', quantity: '', rate: '',
    template: '', steps: '', components: [{ name: '', wt: '', grade: '' }],
    boundary: 'material_purchase', source: '', evidenceType: 'supplier_quote',
    scopeNote: '', conditionsNote: '', notes: '', confirmed: false,
  };
}

export function CostEvidencePanel({ savedEstimateId }: { savedEstimateId: number | null }) {
  const { t } = useLang();
  const [loaded, setLoaded] = useState<{ estimateId: number; summary: CostObservationSummary } | null>(null);
  const summary = loaded?.estimateId === savedEstimateId ? loaded.summary : null;
  const [draft, setDraft] = useState<ObservationDraft>(emptyDraft);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (savedEstimateId === null) return;
    const controller = new AbortController();
    fetchCostObservations(savedEstimateId, controller.signal)
      .then((next) => { setLoaded({ estimateId: savedEstimateId, summary: next }); setDraft(emptyDraft()); setError(''); })
      .catch((failure: unknown) => {
        if (!controller.signal.aborted) setError(failure instanceof Error ? failure.message : String(failure));
      });
    return () => controller.abort();
  }, [savedEstimateId]);

  const update = <K extends keyof ObservationDraft>(key: K, value: ObservationDraft[K]) => setDraft((old) => ({ ...old, [key]: value }));
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (savedEstimateId === null) return;
    setBusy(true);
    setError('');
    try {
      const next = await addCostObservation(savedEstimateId, {
        observed_price: Number(draft.price), currency: draft.currency, price_unit: draft.unit,
        observation_date: draft.date, price_period: draft.month || undefined,
        order_size_tons: draft.quantity ? Number(draft.quantity) : undefined,
        production_rate_ton_per_day: draft.rate ? Number(draft.rate) : undefined,
        components: draft.components.filter((item) => item.name.trim() || item.wt).map((item) => ({
          name: item.name, wt_pct: Number(item.wt), grade: item.grade || undefined,
        })),
        template_id: draft.template || undefined,
        steps: draft.steps.split(',').map((item) => item.trim()).filter(Boolean),
        cost_boundary: draft.boundary, cost_scope_note: draft.scopeNote,
        production_conditions_note: draft.conditionsNote, source: draft.source,
        evidence_type: draft.evidenceType, verified_by_user: draft.confirmed, notes: draft.notes,
      });
      setLoaded({ estimateId: savedEstimateId, summary: next });
      setDraft(emptyDraft());
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : String(failure));
    } finally {
      setBusy(false);
    }
  }

  const reference = summary?.expected_reference;
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5" aria-label={t('Local actual-cost evidence')}>
      <h3 className="text-base font-semibold text-slate-900">{t('Local actual-cost evidence')}</h3>
      <p className="mt-2 text-sm leading-6 text-slate-500">{t('Purchase quotes and actual production costs are stored separately. Errors are calculated only when documented full-cost conditions match the saved estimate.')}</p>
      <p className="mt-1 text-xs text-amber-700">{t('User-supplied evidence; not independently verified. No record is published externally.')}</p>
      {savedEstimateId === null ? <p className="mt-4 text-sm text-slate-600">{t('Save this estimate before adding local observations.')}</p> : <>
        {error && <p className="mt-3 text-sm text-red-700" role="alert">{error}</p>}
        {summary && <div className="mt-4 rounded-lg bg-slate-50 p-3 text-sm">
          <span>{t('Eligible observations')}: {summary.eligible_count}</span>
          <span className="ml-4">{t('Mean absolute percentage error')}: {summary.mape_pct === null ? t('Not estimable') : `${summary.mape_pct.toFixed(2)}%`}</span>
        </div>}
        {reference && <details className="mt-4 text-sm">
          <summary className="cursor-pointer font-medium text-slate-700">{t('Saved comparison conditions')}</summary>
          <dl className="mt-2 grid gap-2 text-xs text-slate-600 sm:grid-cols-2">
            <div><dt>{t('Price month')}</dt><dd>{reference.price_period ?? t('Unknown')}</dd></div>
            <div><dt>{t('Production quantity (short tons)')}</dt><dd>{reference.order_size_tons ?? t('Unknown')}</dd></div>
            <div><dt>{t('Effective production rate (short tons/day)')}</dt><dd>{reference.production_rate_ton_per_day ?? t('Unknown')}</dd></div>
            <div><dt>{t('Template ID')}</dt><dd>{reference.template_id ?? t('Custom steps')}</dd></div>
            <div className="sm:col-span-2"><dt>{t('Manufacturing step keys')}</dt><dd className="break-words">{reference.steps.join(', ') || t('Unknown')}</dd></div>
            {reference.components.map((component, index) => <div key={index}><dt>{component.name ?? t('Unknown')}</dt><dd>{component.wt_pct?.toFixed(3)}{' wt%'} · {component.grade ?? t('Grade not recorded')}</dd></div>)}
          </dl>
          <p className="mt-2 text-xs text-slate-500">{t('Missing saved grades or price months prevent error assessment. Add purchase evidence and recalculate a new estimate when the source is available.')}</p>
        </details>}
        <details className="mt-4 rounded-lg border border-slate-200 p-3">
          <summary className="cursor-pointer text-sm font-semibold text-slate-700">{t('Add local observation')}</summary>
          <form onSubmit={(event) => { void submit(event); }} className="mt-3 space-y-4">
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              <label className="text-xs text-slate-600">{t('Observed unit price')}<input required className={inputClass} type="number" min="0.000001" step="any" value={draft.price} onChange={(event) => update('price', event.target.value)} /></label>
              <label className="text-xs text-slate-600">{t('Currency')}<select className={inputClass} value={draft.currency} onChange={(event) => update('currency', event.target.value)}><option>{'USD'}</option><option>{'EUR'}</option><option>{'KRW'}</option></select></label>
              <label className="text-xs text-slate-600">{t('Price denominator')}<select className={inputClass} value={draft.unit} onChange={(event) => update('unit', event.target.value as ObservationDraft['unit'])}><option value="kg">kg</option><option value="lb">lb</option><option value="cm2">cm²</option></select></label>
              <label className="text-xs text-slate-600">{t('Observation date')}<input required className={inputClass} type="date" value={draft.date} onChange={(event) => update('date', event.target.value)} /></label>
              <label className="text-xs text-slate-600">{t('Observed price month')}<input className={inputClass} type="month" value={draft.month} onChange={(event) => update('month', event.target.value)} /></label>
              <label className="text-xs text-slate-600">{t('Evidence type')}<select className={inputClass} value={draft.evidenceType} onChange={(event) => update('evidenceType', event.target.value as ObservationDraft['evidenceType'])}>
                <option value="supplier_quote">{t('Supplier quote')}</option><option value="invoice">{t('Completed transaction invoice')}</option><option value="production_record">{t('Actual production record')}</option><option value="public_literature">{t('Public literature observation')}</option><option value="other">{t('Other evidence')}</option>
              </select></label>
              <label className="text-xs text-slate-600 sm:col-span-2 lg:col-span-3">{t('Observed cost boundary')}<select className={inputClass} value={draft.boundary} onChange={(event) => update('boundary', event.target.value as ObservationDraft['boundary'])}>
                <option value="material_purchase">{t('Material purchase only')}</option><option value="full_manufacturing_cost">{t('Full manufacturing cost including overhead, before selling margin')}</option><option value="full_selling_price">{t('Full selling price including margin, before recovery credit')}</option><option value="full_net_after_recovery">{t('Full selling price after recovery credit')}</option><option value="other">{t('Other boundary')}</option>
              </select></label>
              <label className="text-xs text-slate-600 sm:col-span-2 lg:col-span-3">{t('Local document reference or source URL')}<input required minLength={3} maxLength={1000} className={inputClass} value={draft.source} onChange={(event) => update('source', event.target.value)} /></label>
            </div>
            <details className="rounded-lg bg-slate-50 p-3">
              <summary className="cursor-pointer text-sm font-medium">{t('Observed production conditions for error assessment')}</summary>
              <div className="mt-3 grid gap-3 sm:grid-cols-2">
                <label className="text-xs text-slate-600">{t('Production quantity (short tons)')}<input className={inputClass} type="number" min="0.000001" step="any" value={draft.quantity} onChange={(event) => update('quantity', event.target.value)} /></label>
                <label className="text-xs text-slate-600">{t('Effective production rate (short tons/day)')}<input className={inputClass} type="number" min="0.000001" step="any" value={draft.rate} onChange={(event) => update('rate', event.target.value)} /></label>
                <label className="text-xs text-slate-600">{t('Observed template ID')}<input className={inputClass} maxLength={200} value={draft.template} onChange={(event) => update('template', event.target.value)} /></label>
                <label className="text-xs text-slate-600">{t('Observed step keys (comma separated)')}<input className={inputClass} value={draft.steps} onChange={(event) => update('steps', event.target.value)} /></label>
              </div>
              <fieldset className="mt-3 space-y-2">
                <legend className="text-xs text-slate-600">{t('Observed finished-catalyst composition')}</legend>
                {draft.components.map((component, index) => <div key={index} className="grid grid-cols-3 gap-2">
                  <label className="text-xs text-slate-600">{t('Component name')}<input className={inputClass} maxLength={200} value={component.name} onChange={(event) => update('components', draft.components.map((item, row) => row === index ? { ...item, name: event.target.value } : item))} /></label>
                  <label className="text-xs text-slate-600">{t('Observed wt%')}<input className={inputClass} type="number" min="0.000001" max="100" step="any" value={component.wt} onChange={(event) => update('components', draft.components.map((item, row) => row === index ? { ...item, wt: event.target.value } : item))} /></label>
                  <label className="text-xs text-slate-600">{t('Observed grade')}<input className={inputClass} maxLength={300} value={component.grade} onChange={(event) => update('components', draft.components.map((item, row) => row === index ? { ...item, grade: event.target.value } : item))} /></label>
                </div>)}
                <button type="button" className="text-xs font-medium text-teal-700" disabled={draft.components.length >= 20} onClick={() => update('components', [...draft.components, { name: '', wt: '', grade: '' }])}>{t('Add observed component')}</button>
              </fieldset>
              <label className="mt-3 block text-xs text-slate-600">{t('Observed cost inclusions and exclusions')}<textarea className={inputClass} rows={2} maxLength={2000} value={draft.scopeNote} onChange={(event) => update('scopeNote', event.target.value)} /></label>
              <label className="mt-3 block text-xs text-slate-600">{t('Production conditions documented in the source')}<textarea className={inputClass} rows={2} maxLength={2000} value={draft.conditionsNote} onChange={(event) => update('conditionsNote', event.target.value)} /></label>
            </details>
            <label className="block text-xs text-slate-600">{t('Observation notes')}<textarea className={inputClass} rows={2} maxLength={2000} value={draft.notes} onChange={(event) => update('notes', event.target.value)} /></label>
            <label className="flex items-start gap-2 text-sm text-slate-600"><input type="checkbox" className="mt-1" checked={draft.confirmed} onChange={(event) => update('confirmed', event.target.checked)} />{t('I checked this source and entered its actual conditions. This is my confirmation, not independent verification.')}</label>
            <button type="submit" disabled={busy || !summary} className="rounded-lg bg-teal-700 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50">{busy ? t('Saving observation...') : t('Save observation locally')}</button>
          </form>
        </details>
        {summary?.observations.map((row) => <details key={row.id} className="mt-3 rounded-lg border border-slate-200 p-3 text-sm">
          <summary className="cursor-pointer font-medium text-slate-700">{row.observation.observation_date} · {row.observation.currency} {row.observation.observed_price}/{row.observation.price_unit} · {row.assessment.eligible ? t('Eligible for local error assessment') : t('Excluded from error assessment')}</summary>
          <p className="mt-2 break-words text-xs text-slate-500">{row.observation.source}</p>
          {row.assessment.eligible ? <p className="mt-2 text-sm">{t('Signed error (estimate minus observation)')}: {row.assessment.signed_error_pct?.toFixed(2)}% · {t('Absolute percentage error')}: {row.assessment.absolute_percentage_error?.toFixed(2)}%</p> : <ul className="mt-2 list-disc space-y-1 pl-4 text-xs text-amber-800">{row.assessment.exclusion_reasons.map((reason) => <li key={reason}>{reason}</li>)}</ul>}
        </details>)}
      </>}
    </section>
  );
}

export default CostEvidencePanel;
