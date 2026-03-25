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

const CATEGORIES = [
  '',
  'Precious Metal / PGM',
  'Base Metal',
  'Support',
  'Chemical',
  'Chemical / Solvent',
];

function categoryBadge(cat: string) {
  if (!cat) return { bg: 'bg-slate-100 text-slate-500 border-slate-200', dot: 'bg-slate-400' };
  const c = cat.toLowerCase();
  if (c.includes('pgm') || c.includes('precious')) return { bg: 'bg-yellow-50 text-yellow-800 border-yellow-200', dot: 'bg-yellow-500' };
  if (c.includes('base metal') || c.includes('metal')) return { bg: 'bg-blue-50 text-blue-700 border-blue-200', dot: 'bg-blue-500' };
  if (c.includes('support'))  return { bg: 'bg-emerald-50 text-emerald-700 border-emerald-200', dot: 'bg-emerald-500' };
  if (c.includes('solvent'))  return { bg: 'bg-purple-50 text-purple-700 border-purple-200', dot: 'bg-purple-500' };
  return { bg: 'bg-slate-100 text-slate-500 border-slate-200', dot: 'bg-slate-400' };
}


export default function Library() {
  const { unit, toDisplay, fmtLabel } = useUnit();
  const [tab, setTab]                 = useState<Tab>('materials');
  const [materials, setMaterials]     = useState<MaterialItem[]>([]);
  const [templates, setTemplates]     = useState<ProcessTemplate[]>([]);
  const [steps, setSteps]             = useState<StepLibraryItem[]>([]);
  const [category, setCategory]       = useState('');
  const [search, setSearch]           = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [loading, setLoading]         = useState(true);
  const [totalShown, setTotalShown]   = useState(0);

  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(search), 400);
    return () => clearTimeout(t);
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
            setTotalShown(data.length);
          }
          return;
        }

        if (tab === 'templates') {
          const data = await fetchTemplates();
          if (!cancelled) {
            setTemplates(data);
          }
          return;
        }

        const data = await fetchSteps();
        if (!cancelled) {
          setSteps(data);
        }
      } catch {
        if (!cancelled && tab === 'materials') {
          setMaterials([]);
          setTotalShown(0);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadData();
    return () => {
      cancelled = true;
    };
  }, [tab, category, debouncedSearch]);

  const TAB_ITEMS: { key: Tab; label: string; count?: number }[] = [
    { key: 'materials', label: 'Materials', count: tab === 'materials' ? totalShown : undefined },
    { key: 'steps',     label: 'Steps',     count: tab === 'steps' ? steps.length : undefined },
    { key: 'templates', label: 'Templates', count: tab === 'templates' ? templates.length : undefined },
  ];

  return (
    <div className="p-6 max-w-7xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-slate-800">Library</h2>
          <p className="text-sm text-slate-400 mt-0.5">원료, 공정 단계, 공정 템플릿 참조 데이터</p>
        </div>
        <div className="text-xs text-slate-400 bg-slate-100 px-3 py-1.5 rounded-full border border-slate-200">
          Source: CatCost v1.1.1
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-5 bg-slate-100 rounded-xl p-1 w-fit border border-slate-200">
        {TAB_ITEMS.map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`flex items-center gap-1.5 px-4 py-2 text-sm rounded-lg font-medium transition-all ${
              tab === t.key
                ? 'bg-white text-slate-800 shadow-sm border border-slate-200'
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            {t.label}
            {t.count != null && (
              <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-semibold ${
                tab === t.key ? 'bg-blue-100 text-blue-600' : 'bg-slate-200 text-slate-500'
              }`}>
                {t.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* ── Materials Tab ── */}
      {tab === 'materials' && (
        <>
          <div className="flex gap-3 mb-3">
            <div className="relative flex-1">
              <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                placeholder="Search 606 materials…"
                value={search}
                onChange={e => setSearch(e.target.value)}
                className="w-full input-base pl-9"
              />
            </div>
            <select
              value={category}
              onChange={e => setCategory(e.target.value)}
              className="input-base min-w-[180px]"
            >
              <option value="">All categories</option>
              {CATEGORIES.filter(Boolean).map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
          <p className="text-xs text-slate-400 mb-3">
            Showing <strong>{totalShown}</strong> of 606 materials (max 200) · Use search to filter
          </p>

          {loading ? (
            <LoadingSpinner />
          ) : materials.length === 0 ? (
            <EmptyState message="No materials found" />
          ) : (
            <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
              <table className="w-full text-sm">
                <thead className="sticky top-0 z-10">
                  <tr className="bg-slate-50 text-slate-500 border-b border-slate-200">
                    <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider">Material</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider">Type</th>
                    <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider">Bulk Price ($/{unit})</th>
                    <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider">Year</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider">Source</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 max-h-[62vh] overflow-auto">
                  {materials.map(m => {
                    const { bg, dot } = categoryBadge(m.category);
                    return (
                      <tr key={m.id} className="hover:bg-slate-50 transition-colors">
                        <td className="px-5 py-2.5">
                          <div className="flex items-center gap-2 font-medium text-slate-800">
                            <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${dot}`} />
                            <span className="truncate max-w-xs" title={m.name}>{m.name}</span>
                            {m.is_custom && (
                              <span className="text-[10px] bg-indigo-100 text-indigo-600 px-1.5 py-0.5 rounded font-semibold flex-shrink-0">custom</span>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-2.5">
                          <span className={`text-[11px] px-2 py-0.5 rounded-full border font-medium ${bg}`}>
                            {m.category || '—'}
                          </span>
                        </td>
                        <td className="px-4 py-2.5 text-right font-mono text-slate-700 text-xs">
                          {m.price != null
                            ? `$${toDisplay(Number(m.price)).toFixed(3)}${fmtLabel}`
                            : <span className="text-slate-300">—</span>}
                        </td>
                        <td className="px-4 py-2.5 text-right text-slate-400 text-xs tabular-nums">
                          {m.quote_year || <span className="text-slate-300">—</span>}
                        </td>
                        <td className="px-4 py-2.5 text-slate-400 text-xs max-w-[140px]">
                          <span className="truncate block" title={m.quote_source}>{m.quote_source || '—'}</span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {/* ── Steps Tab ── */}
      {tab === 'steps' && (
        <>
          <div className="bg-amber-50 border border-amber-200 rounded-xl px-4 py-2.5 text-xs text-amber-700 mb-4 flex items-center gap-2">
            <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Processing step costs in <strong>&nbsp;$/hr&nbsp;</strong> · Mid-2017 basis (ChemPPI-escalated in calculations) · Three plant scales
          </div>

          {loading ? (
            <LoadingSpinner />
          ) : (
            <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200">
                    <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Step Name</th>
                    <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-violet-500">
                      Small
                      <div className="font-normal text-slate-400 normal-case">1 t/day</div>
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-blue-500">
                      Medium
                      <div className="font-normal text-slate-400 normal-case">10 t/day</div>
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-teal-500">
                      Large
                      <div className="font-normal text-slate-400 normal-case">150 t/day</div>
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-400">Note</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {steps.map((s, i) => (
                    <tr key={i} className="hover:bg-slate-50 transition-colors">
                      <td className="px-5 py-3 font-medium text-slate-800">{s.name}</td>
                      {(['cost_small', 'cost_medium', 'cost_large'] as const).map((field, fi) => {
                        const val = s[field];
                        const colors = ['text-violet-700 bg-violet-50', 'text-blue-700 bg-blue-50', 'text-teal-700 bg-teal-50'];
                        return (
                          <td key={fi} className="px-4 py-3 text-right">
                            {val != null ? (
                              <span className={`font-mono text-xs px-2 py-0.5 rounded ${colors[fi]}`}>
                                ${val}/hr
                              </span>
                            ) : (
                              <span className="text-slate-200 text-xs">—</span>
                            )}
                          </td>
                        );
                      })}
                      <td className="px-4 py-3 text-xs text-slate-400">{s.note || ''}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {/* ── Templates Tab ── */}
      {tab === 'templates' && (
        <>
          {loading ? (
            <LoadingSpinner />
          ) : templates.length === 0 ? (
            <EmptyState message="No templates found" />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {templates.map(t => (
                <div key={t.id} className="bg-white border border-slate-200 rounded-2xl shadow-sm p-5 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <h3 className="font-bold text-slate-800 text-sm leading-snug">{t.name}</h3>
                    <span className="text-[10px] bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full whitespace-nowrap flex-shrink-0">
                      {t.steps.length} steps
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 mb-3 leading-relaxed">{t.description}</p>

                  {t.example_catalysts.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mb-3">
                      {t.example_catalysts.map(c => (
                        <span key={c} className="text-[11px] bg-blue-50 text-blue-700 border border-blue-100 px-2 py-0.5 rounded-full font-medium">
                          {c}
                        </span>
                      ))}
                    </div>
                  )}

                  {t.steps.length > 0 && (
                    <div className="flex flex-wrap items-center gap-1 mt-2">
                      {t.steps.map((step, si) => (
                        <span key={si} className="flex items-center gap-1">
                          <span className="text-[10px] bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded font-mono">{step}</span>
                          {si < t.steps.length - 1 && <span className="text-slate-300 text-xs">→</span>}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center py-16 text-slate-400 gap-3">
      <span className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      Loading…
    </div>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-slate-400 gap-2">
      <svg className="w-10 h-10 text-slate-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <span className="text-sm">{message}</span>
    </div>
  );
}
