import { ScientificText } from './shared/ScientificText';
import { useState } from 'react';
import type { ProcessTemplate, TemplateCost } from '../lib/api';
import { useLang } from '../lib/i18n';
import { scientificSearchText } from '../lib/scientific-text';

interface Props {
  templates: ProcessTemplate[];
  costs: Record<string, TemplateCost>;
  selectedId: string | null;
  edited: boolean;
  loading: boolean;
  formatStep: (key: string) => string;
  formatCost: (value: number) => string;
  onSelect: (template: ProcessTemplate) => void;
  onReset: () => void;
}

export function ManufacturingMethods({ templates, costs, selectedId, edited, loading, formatStep, formatCost, onSelect, onReset }: Props) {
  const { t } = useLang();
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const selected = templates.find((template) => template.id === selectedId);
  const cost = selected ? costs[selected.id] : undefined;
  const steps = cost?.steps_fitted ?? selected?.steps ?? [];
  const uncosted = cost?.uncosted_operations ?? selected?.uncosted_operations ?? [];
  const search = scientificSearchText(query).trim().toLowerCase();
  const visible = templates.filter((template) => (!category || template.category === category)
    && scientificSearchText([template.name, template.description, ...template.example_catalysts].join(' ')).toLowerCase().includes(search));

  return (
    <section aria-label={t('Standard manufacturing methods')} className="overflow-hidden rounded-xl border border-slate-200 bg-white">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 px-4 py-3">
        <h3 className="text-sm font-semibold text-slate-900">{t('Standard manufacturing methods')} <span className="ml-2 font-normal tabular-nums text-slate-400">{templates.length}</span></h3>
        <p className="text-xs text-slate-500">{t('Choose a method, then adjust its operations below.')}</p>
      </div>
      <div className="grid lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <div className="min-w-0 border-b border-slate-200 lg:border-r lg:border-b-0">
          <div className="grid grid-cols-[minmax(0,1fr)_150px] gap-2 border-b border-slate-100 p-3">
            <input aria-label={t('Search manufacturing methods')} placeholder={t('Search method or catalyst')} value={query} onChange={(event) => setQuery(event.target.value)} className="input-base min-w-0 w-full !rounded-lg !py-2 text-sm" />
            <select aria-label={t('Method category')} value={category} onChange={(event) => setCategory(event.target.value)} className="input-base min-w-0 w-full !rounded-lg !py-2 text-sm">
              <option value="">{t('All categories')}</option>
              {[...new Set(templates.map((template) => template.category))].map((item) => <option key={item} value={item}>{t(item)}</option>)}
            </select>
          </div>
          <div className="h-[352px] overflow-y-auto overscroll-contain" data-testid="manufacturing-method-list">
            {visible.map((template) => {
              const active = template.id === selectedId;
              const price = costs[template.id]?.processing_cost_per_lb;
              return (
                <button key={template.id} type="button" aria-pressed={active} data-template-id={template.id} onClick={() => onSelect(template)}
                  className={`flex h-[88px] w-full items-center gap-3 border-b border-slate-100 border-l-[3px] px-3 text-left transition-colors focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-teal-600 ${active ? 'border-l-teal-600 bg-teal-50/70' : 'border-l-transparent bg-white hover:bg-slate-50'}`}>
                  <span className="min-w-0 flex-1">
                    <span className="line-clamp-2 text-[13px] font-medium leading-5 text-slate-900"><ScientificText text={template.name} /></span>
                    <span className="mt-1 block truncate text-[11px] text-slate-500"><ScientificText text={template.example_catalysts.join(', ')} /></span>
                  </span>
                  <span className="w-24 shrink-0 text-right">
                    <span className="block whitespace-nowrap font-mono text-xs text-slate-700"><ScientificText text={loading || price == null ? '—' : formatCost(price)} /></span>
                    <span className={`mt-1 block text-[10px] ${(costs[template.id]?.uncosted_operations ?? template.uncosted_operations)?.length ? 'text-amber-700' : 'text-slate-400'}`}><ScientificText text={(costs[template.id]?.uncosted_operations ?? template.uncosted_operations)?.length ? t('Partly costed') : t('Processing')} /></span>
                    <span className={`mt-2 inline-flex h-4 w-4 items-center justify-center rounded-full border ${active ? 'border-teal-600 bg-teal-600 text-white' : 'border-slate-300 text-transparent'}`} aria-hidden="true">✓</span>
                  </span>
                </button>
              );
            })}
            {!visible.length ? <p className="p-5 text-sm text-slate-500">{t('No matching methods. Try another search.')}</p> : null}
          </div>
        </div>
        <aside aria-label={t('Selected method details')} className="h-[416px] overflow-y-auto overscroll-contain bg-slate-50/55 p-5" data-testid="manufacturing-method-detail">
          {selected ? <>
            <div className="flex h-6 items-center justify-between gap-3 text-xs">
              <span className="min-w-0 truncate font-medium text-teal-700">{edited ? t('Method with edited operations') : t('Selected method')}</span>
              <button type="button" onClick={onReset} disabled={!edited} className="shrink-0 text-slate-600 underline underline-offset-4 disabled:invisible">{t('Restore method steps')}</button>
            </div>
            <h4 className="mt-2 text-lg font-semibold leading-7 text-slate-900"><ScientificText text={selected.name} /></h4>
            <div className="mt-4 flex items-center justify-between border-y border-slate-200 py-3">
              <span className="text-xs text-slate-500">{t('Standard processing cost')}</span>
              <span className="font-mono text-xl font-medium text-slate-900"><ScientificText text={loading || cost?.processing_cost_per_lb == null ? '—' : formatCost(cost.processing_cost_per_lb)} /></span>
            </div>
            <p className="mt-2 text-[11px] leading-5 text-slate-500">{t('Uses the standard method and default production rate; excludes materials.')}</p>
            <p className="mt-4 text-xs leading-6 text-slate-600"><ScientificText text={selected.description} /></p>
            <div className="mt-4 text-xs font-medium text-slate-700">{t('Standard method operations')} <span className="ml-1 tabular-nums text-slate-400">{steps.length}</span></div>
            <div className="mt-2 flex flex-wrap gap-1.5">
              {[...new Set(steps)].map((key) => <span key={key} className="rounded border border-slate-200 bg-white px-2 py-1 text-[11px] text-slate-600"><ScientificText text={formatStep(key)} /> <span className="font-mono text-slate-400">×{steps.filter((item) => item === key).length}</span></span>)}
            </div>
            {uncosted.length ? <div className="mt-4 border-l-2 border-amber-400 pl-3 text-xs leading-6 text-amber-900"><div className="font-semibold">{t('Not costed')}</div>{uncosted.map((item) => <p key={item}><ScientificText text={item} /></p>)}</div> : null}
            {cost?.substitutions.length ? <div className="mt-4 text-xs leading-6 text-slate-600"><div className="font-medium">{t('Scale-fitted')}</div>{cost.substitutions.map(({ from, to }) => <p key={`${from}-${to}`}><ScientificText text={formatStep(from)} /> → <ScientificText text={formatStep(to)} /></p>)}</div> : null}
            {cost?.dropped_steps.length ? <div className="mt-4 text-xs leading-6 text-amber-900"><div className="font-medium">{t('Unavailable at this production scale')}</div>{cost.dropped_steps.map((key, index) => <p key={`${key}-${index}`}><ScientificText text={formatStep(key)} /></p>)}</div> : null}
            {selected.source ? <details className="mt-4 text-xs text-slate-500"><summary className="cursor-pointer">{t('Source')}</summary><p className="mt-2 leading-6"><ScientificText text={selected.source} /></p></details> : null}
          </> : <div className="flex h-full flex-col justify-center px-4"><div className="text-lg font-semibold text-slate-800">{t('Choose a starting method')}</div><p className="mt-3 text-sm leading-7 text-slate-500">{t('Review the method here, or build your own route using the operation checkboxes below.')}</p></div>}
        </aside>
      </div>
    </section>
  );
}
