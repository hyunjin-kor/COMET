import { useEffect, useState } from 'react';
import { fetchMaterials, fetchTemplates, type MaterialItem, type ProcessTemplate } from '../lib/api';

type Tab = 'materials' | 'templates';

export default function Library() {
  const [tab, setTab] = useState<Tab>('materials');
  const [materials, setMaterials] = useState<MaterialItem[]>([]);
  const [templates, setTemplates] = useState<ProcessTemplate[]>([]);
  const [category, setCategory] = useState('');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    if (tab === 'materials') {
      fetchMaterials(category || undefined, search || undefined)
        .then(setMaterials)
        .catch(() => {})
        .finally(() => setLoading(false));
    } else {
      fetchTemplates()
        .then(setTemplates)
        .catch(() => {})
        .finally(() => setLoading(false));
    }
  }, [tab, category, search]);

  return (
    <div className="p-6 max-w-5xl">
      <h2 className="text-2xl font-bold text-slate-800 mb-6">Library</h2>

      {/* Tab bar */}
      <div className="flex gap-1 mb-4 bg-slate-100 rounded-lg p-1 w-fit">
        {(['materials', 'templates'] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-1.5 text-sm rounded-md capitalize transition-colors ${
              tab === t ? 'bg-white shadow text-slate-800 font-medium' : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === 'materials' && (
        <>
          {/* Filters */}
          <div className="flex gap-3 mb-4">
            <input
              type="text"
              placeholder="Search materials..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            >
              <option value="">All categories</option>
              <option value="metal">Metals</option>
              <option value="support">Supports</option>
            </select>
          </div>

          {/* Materials table */}
          {loading ? (
            <div className="text-slate-500">Loading...</div>
          ) : (
            <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-50 text-left text-slate-600">
                    <th className="px-4 py-3 font-medium">Name</th>
                    <th className="px-4 py-3 font-medium">Symbol</th>
                    <th className="px-4 py-3 font-medium">Category</th>
                    <th className="px-4 py-3 font-medium text-right">Price</th>
                    <th className="px-4 py-3 font-medium">Unit</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {materials.map((m) => (
                    <tr key={m.id} className="hover:bg-slate-50">
                      <td className="px-4 py-2.5 font-medium text-slate-800">{m.name}</td>
                      <td className="px-4 py-2.5 font-mono text-slate-600">{m.symbol || '-'}</td>
                      <td className="px-4 py-2.5">
                        <span
                          className={`text-xs px-2 py-0.5 rounded-full ${
                            m.category === 'metal'
                              ? 'bg-blue-100 text-blue-700'
                              : 'bg-green-100 text-green-700'
                          }`}
                        >
                          {m.category}
                        </span>
                      </td>
                      <td className="px-4 py-2.5 text-right font-mono">
                        ${m.price.toLocaleString()}
                      </td>
                      <td className="px-4 py-2.5 text-slate-500">{m.price_unit}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {tab === 'templates' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {loading ? (
            <div className="text-slate-500">Loading...</div>
          ) : (
            templates.map((t) => (
              <div key={t.id} className="bg-white border border-slate-200 rounded-xl p-5">
                <h3 className="font-semibold text-slate-800">{t.name}</h3>
                <p className="text-sm text-slate-500 mt-1">{t.description}</p>
                <div className="flex flex-wrap gap-1 mt-3">
                  {t.example_catalysts.map((c) => (
                    <span
                      key={c}
                      className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded"
                    >
                      {c}
                    </span>
                  ))}
                </div>
                <div className="mt-3 text-xs text-slate-400">
                  Steps: {t.steps.length} &middot; {t.steps.join(' → ')}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
