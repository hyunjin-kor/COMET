import { useEffect, useState } from 'react';
import {
  fetchMaterials,
  fetchSteps,
  fetchTemplates,
  type MaterialItem,
  type ProcessTemplate,
  type StepLibraryItem,
} from '../lib/api';
import { useUnit } from '../lib/use-unit';

type Tab = 'materials' | 'steps' | 'templates';

const CATEGORIES = ['', 'Precious Metal / PGM', 'Base Metal', 'Support', 'Chemical', 'Chemical / Solvent'];

function categoryTone(category: string) {
  if (!category) return 'border-slate-200 bg-white text-slate-600';
  const value = category.toLowerCase();
  if (value.includes('pgm') || value.includes('precious')) return 'border-amber-200 bg-amber-50 text-amber-700';
  if (value.includes('support')) return 'border-emerald-200 bg-emerald-50 text-emerald-700';
  if (value.includes('metal')) return 'border-sky-200 bg-sky-50 text-sky-700';
  if (value.includes('solvent')) return 'border-violet-200 bg-violet-50 text-violet-700';
  return 'border-slate-200 bg-white text-slate-600';
}

export default function Library() {
  const { toDisplay, fmtLabel } = useUnit();
  const [tab, setTab] = useState<Tab>('materials');
  const [materials, setMaterials] = useState<MaterialItem[]>([]);
  const [templates, setTemplates] = useState<ProcessTemplate[]>([]);
  const [steps, setSteps] = useState<StepLibraryItem[]>([]);
  const [category, setCategory] = useState('');
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(search), 300);
    return () => clearTimeout(timer);
  }, [search]);

  useEffect(() => {
    let cancelled = false;

    async function loadData() {
      setLoading(true);
      try {
        if (tab === 'materials') {
          const data = await fetchMaterials(category || undefined, debouncedSearch || undefined);
          if (!cancelled) {
            setMaterials(data);
          }
          return;
        }

        if (tab === 'templates') {
          const data = await fetchTemplates();
          if (!cancelled) setTemplates(data);
          return;
        }

        const data = await fetchSteps();
        if (!cancelled) setSteps(data);
      } catch {
        if (!cancelled) {
          setMaterials([]);
          setTemplates([]);
          setSteps([]);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void loadData();
    return () => {
      cancelled = true;
    };
  }, [tab, category, debouncedSearch]);

  return (
    <div className="space-y-4">
      <section className="surface-card cp-enter overflow-hidden px-5 py-6 sm:px-6" style={{ animationDelay: '0.06s' }}>
        <div className="flex flex-col gap-4 border-b border-slate-900/8 pb-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="cp-subtle-label">Library Mode</div>
            <h2 className="cp-heading-xl mt-2">Libraries and templates</h2>
            <p className="cp-body-copy mt-2 max-w-2xl">
              Switch between the Materials Library, Step Library, and template process paths from the same panel.
            </p>
          </div>

          <div className="cp-toolbar">
            {(['materials', 'steps', 'templates'] as Tab[]).map((value) => (
              <button
                key={value}
                onClick={() => setTab(value)}
                className={`rounded-[18px] px-4 py-2.5 text-xs font-semibold uppercase tracking-[0.18em] transition ${
                  tab === value
                    ? 'bg-slate-950 text-white shadow-[0_12px_24px_rgba(15,23,42,0.18)]'
                    : 'text-slate-500 hover:bg-white hover:text-slate-800'
                }`}
              >
                {value}
              </button>
            ))}
          </div>
        </div>

        {tab === 'materials' && (
          <>
            <div className="mt-5 grid gap-3 lg:grid-cols-[minmax(0,1fr)_240px]">
              <label className="block">
                <div className="cp-subtle-label">Search</div>
                <div className="mt-2">
                  <input
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                    placeholder="Search materials, formulas, or symbols"
                    className="input-base"
                  />
                </div>
              </label>

              <label className="block">
                <div className="cp-subtle-label">Category filter</div>
                <div className="mt-2">
                  <select value={category} onChange={(event) => setCategory(event.target.value)} className="input-base">
                    <option value="">All categories</option>
                    {CATEGORIES.filter(Boolean).map((value) => (
                      <option key={value} value={value}>
                        {value}
                      </option>
                    ))}
                  </select>
                </div>
              </label>
            </div>

            <div className="mt-5 overflow-hidden rounded-[28px] border border-slate-900/8 bg-white/58 backdrop-blur-xl">
              <div className="grid grid-cols-[minmax(0,1.4fr)_180px_160px_110px_160px] gap-3 border-b border-slate-900/8 bg-white/46 px-5 py-3 text-[11px] uppercase tracking-[0.18em] text-slate-500">
                <span>Material</span>
                <span>Category</span>
                <span className="text-right">Bulk price</span>
                <span className="text-right">Year</span>
                <span>Source</span>
              </div>

              {loading ? (
                <div className="px-5 py-8 text-sm text-slate-500">Loading materials...</div>
              ) : materials.length === 0 ? (
                <div className="px-5 py-8 text-sm text-slate-500">No materials match the current filters.</div>
              ) : (
                <div className="max-h-[62vh] divide-y divide-slate-900/8 overflow-auto">
                  {materials.map((material) => (
                    <div key={material.id} className="grid grid-cols-[minmax(0,1.4fr)_180px_160px_110px_160px] gap-3 px-5 py-3 text-sm">
                      <div className="min-w-0">
                        <div className="truncate font-semibold text-slate-950">{material.name}</div>
                        <div className="truncate text-xs text-slate-500">{material.symbol || material.formula || 'No symbol'}</div>
                      </div>
                      <div>
                        <span className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] ${categoryTone(material.category)}`}>
                          {material.category || 'Uncategorised'}
                        </span>
                      </div>
                      <div className="text-right font-mono text-slate-700">
                        {material.price != null ? `$${toDisplay(Number(material.price)).toFixed(3)}${fmtLabel}` : 'N/A'}
                      </div>
                      <div className="text-right text-slate-500">{material.quote_year ?? 'N/A'}</div>
                      <div className="truncate text-slate-500">{material.quote_source || 'N/A'}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}

        {tab === 'steps' && (
          <div className="mt-5 overflow-hidden rounded-[28px] border border-slate-900/8 bg-white/58 backdrop-blur-xl">
            <div className="grid grid-cols-[minmax(0,1.3fr)_120px_120px_120px_minmax(0,1fr)] gap-3 border-b border-slate-900/8 bg-white/46 px-5 py-3 text-[11px] uppercase tracking-[0.18em] text-slate-500">
              <span>Step</span>
              <span className="text-right">Small</span>
              <span className="text-right">Medium</span>
              <span className="text-right">Large</span>
              <span>Note</span>
            </div>

            {loading ? (
              <div className="px-5 py-8 text-sm text-slate-500">Loading step rates...</div>
            ) : (
              <div className="max-h-[62vh] divide-y divide-slate-900/8 overflow-auto">
                {steps.map((step) => (
                  <div key={step.key} className="grid grid-cols-[minmax(0,1.3fr)_120px_120px_120px_minmax(0,1fr)] gap-3 px-5 py-3 text-sm">
                    <div className="font-semibold text-slate-950">{step.name}</div>
                    <div className="text-right font-mono text-slate-700">{step.cost_small != null ? `$${step.cost_small}/hr` : 'N/A'}</div>
                    <div className="text-right font-mono text-slate-700">{step.cost_medium != null ? `$${step.cost_medium}/hr` : 'N/A'}</div>
                    <div className="text-right font-mono text-slate-700">{step.cost_large != null ? `$${step.cost_large}/hr` : 'N/A'}</div>
                    <div className="text-slate-500">{step.note || 'N/A'}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {tab === 'templates' && (
          <div className="mt-5 grid gap-4 lg:grid-cols-2">
            {loading ? (
              <div className="text-sm text-slate-500">Loading templates...</div>
            ) : (
              templates.map((template) => (
                <article key={template.id} className="surface-ghost p-5">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="cp-subtle-label">{template.category || 'Template'}</div>
                      <h3 className="cp-heading-lg mt-2">{template.name}</h3>
                    </div>
                    <span className="cp-chip">{template.steps.length} steps</span>
                  </div>

                  <p className="mt-3 text-sm leading-7 text-slate-600">{template.description}</p>

                  {template.example_catalysts.length > 0 && (
                    <div className="mt-4 flex flex-wrap gap-2">
                      {template.example_catalysts.map((value) => (
                        <span key={value} className="cp-chip">
                          {value}
                        </span>
                      ))}
                    </div>
                  )}

                  <div className="mt-4 flex flex-wrap gap-2">
                    {template.steps.map((step, index) => (
                      <span
                        key={`${template.id}-${step}-${index}`}
                        className="rounded-full border border-slate-200 bg-white/80 px-3 py-1 text-xs text-slate-600"
                      >
                        {step}
                      </span>
                    ))}
                  </div>
                </article>
              ))
            )}
          </div>
        )}
      </section>
    </div>
  );
}
