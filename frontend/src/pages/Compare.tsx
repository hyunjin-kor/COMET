import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';
import { useUnit } from '../lib/use-unit';

interface Composition {
  label: string;
  metal_symbol: string;
  metal_price: number;
  metal_price_unit: string;
  metal_loading_wt_pct: number;
  support_name: string;
  support_price_per_lb: number;
  steps: string[];
  order_size_tons: number;
}

interface CompareResult {
  label: string;
  estimated_price_per_lb: number;
  materials_cost_per_lb: number;
  processing_cost_per_lb: number;
  scale: string;
}

const emptyComp = (): Composition => ({
  label: '',
  metal_symbol: 'Ni',
  metal_price: 7.5,
  metal_price_unit: '$/lb',
  metal_loading_wt_pct: 15,
  support_name: 'Al2O3',
  support_price_per_lb: 0.5,
  steps: ['mixer_slurry', 'incipient_wetness', 'dryer_rotary_100_300C'],
  order_size_tons: 20,
});

const PALETTE = [
  { bg: 'from-blue-500 to-blue-600',    border: 'border-blue-200',   text: 'text-blue-700',   dot: '#3b82f6', badge: 'bg-blue-100 text-blue-700' },
  { bg: 'from-emerald-500 to-teal-600', border: 'border-emerald-200', text: 'text-emerald-700', dot: '#10b981', badge: 'bg-emerald-100 text-emerald-700' },
  { bg: 'from-amber-500 to-orange-500', border: 'border-amber-200',  text: 'text-amber-700',  dot: '#f59e0b', badge: 'bg-amber-100 text-amber-700' },
  { bg: 'from-rose-500 to-red-600',     border: 'border-rose-200',   text: 'text-rose-700',   dot: '#ef4444', badge: 'bg-rose-100 text-rose-700' },
];

const SUPPORT_OPTIONS = ['Al2O3', 'SiO2', 'TiO2', 'Carbon', 'ZSM-5', 'USY', 'CeO2', 'MgO', 'ZrO2'];
const KNOWN_METALS = ['Ni', 'Co', 'Cu', 'Fe', 'Pt', 'Pd', 'Rh', 'Ru', 'Ir', 'Mo', 'W', 'Au', 'Ag', 'Al'];

function scaleLabel(tons: number) {
  if (tons < 5)  return 'Small';
  if (tons < 70) return 'Medium';
  return 'Large';
}

export default function Compare() {
  const { unit, toDisplay, toInternal, fmtLabel } = useUnit();
  const [comps, setComps]     = useState<Composition[]>([emptyComp(), emptyComp()]);
  const [results, setResults] = useState<CompareResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');

  const updateComp = (i: number, field: keyof Composition, value: string | number) => {
    setComps(prev => prev.map((c, idx) => idx === i ? { ...c, [field]: value } : c));
  };

  const addComp = () => {
    if (comps.length < 4) setComps([...comps, emptyComp()]);
  };

  const removeComp = (i: number) => {
    if (comps.length > 2) setComps(comps.filter((_, idx) => idx !== i));
  };

  const handleCompare = async () => {
    setLoading(true); setError('');
    try {
      const resp = await fetch('/api/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ compositions: comps }),
      });
      if (!resp.ok) throw new Error((await resp.json()).detail);
      setResults((await resp.json()).compositions);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Compare failed');
    } finally {
      setLoading(false);
    }
  };

  const chartData = results.map((r) => ({
    name: r.label,
    Materials:     +toDisplay(r.materials_cost_per_lb).toFixed(3),
    Processing:    +toDisplay(r.processing_cost_per_lb).toFixed(3),
    'G&A + Margin': +toDisplay(r.estimated_price_per_lb - r.materials_cost_per_lb - r.processing_cost_per_lb).toFixed(3),
  }));

  const bestIdx = results.length
    ? results.reduce((bi, r, i) => r.estimated_price_per_lb < results[bi].estimated_price_per_lb ? i : bi, 0)
    : -1;

  return (
    <div className="p-6 max-w-6xl">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-xl font-bold text-slate-800">Compare Compositions</h2>
        <p className="text-sm text-slate-400 mt-0.5">최대 4가지 촉매 조성을 side-by-side로 비교합니다</p>
      </div>

      {/* Composition cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
        {comps.map((c, i) => {
          const pal = PALETTE[i];
          return (
            <div key={i} className={`bg-white rounded-2xl border ${pal.border} shadow-sm overflow-hidden`}>
              {/* Card header strip */}
              <div className={`bg-gradient-to-r ${pal.bg} px-4 py-2.5 flex items-center justify-between`}>
                <div className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-white/20 text-white text-xs font-bold flex items-center justify-center">
                    {i + 1}
                  </span>
                  <input
                    value={c.label}
                    onChange={e => updateComp(i, 'label', e.target.value)}
                    placeholder={`Composition ${i + 1}`}
                    className="bg-transparent text-white text-sm font-semibold placeholder-white/60 outline-none w-40"
                  />
                </div>
                {comps.length > 2 && (
                  <button
                    onClick={() => removeComp(i)}
                    className="text-white/70 hover:text-white text-lg leading-none transition-colors"
                  >
                    ×
                  </button>
                )}
              </div>

              {/* Fields grid */}
              <div className="p-4 grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Active Metal</label>
                  <select
                    value={c.metal_symbol}
                    onChange={e => updateComp(i, 'metal_symbol', e.target.value)}
                    className="w-full input-base"
                  >
                    {KNOWN_METALS.map(m => <option key={m}>{m}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Price ($/{unit})</label>
                  <input
                    type="number" step="0.01"
                    value={toDisplay(c.metal_price).toFixed(2)}
                    onChange={e => updateComp(i, 'metal_price', toInternal(+e.target.value))}
                    className="w-full input-base font-mono"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Loading (wt%)</label>
                  <input
                    type="number" step="0.5" min="0.1" max="99"
                    value={c.metal_loading_wt_pct}
                    onChange={e => updateComp(i, 'metal_loading_wt_pct', +e.target.value)}
                    className="w-full input-base font-mono"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Order (tons)</label>
                  <div className="relative">
                    <input
                      type="number" step="1" min="1"
                      value={c.order_size_tons}
                      onChange={e => updateComp(i, 'order_size_tons', +e.target.value)}
                      className="w-full input-base font-mono pr-16"
                    />
                    <span className="absolute right-2 top-1/2 -translate-y-1/2 text-[10px] text-slate-400">
                      {scaleLabel(c.order_size_tons)}
                    </span>
                  </div>
                </div>
                <div>
                  <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Support</label>
                  <select
                    value={c.support_name}
                    onChange={e => updateComp(i, 'support_name', e.target.value)}
                    className="w-full input-base"
                  >
                    {SUPPORT_OPTIONS.map(s => <option key={s}>{s}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Support ($/{unit})</label>
                  <input
                    type="number" step="0.01"
                    value={toDisplay(c.support_price_per_lb).toFixed(2)}
                    onChange={e => updateComp(i, 'support_price_per_lb', toInternal(+e.target.value))}
                    className="w-full input-base font-mono"
                  />
                </div>
              </div>
            </div>
          );
        })}

        {/* Add button card */}
        {comps.length < 4 && (
          <button
            onClick={addComp}
            className="h-full min-h-[160px] rounded-2xl border-2 border-dashed border-slate-200 hover:border-blue-300 hover:bg-blue-50/30 transition-all flex flex-col items-center justify-center gap-2 text-slate-400 hover:text-blue-500"
          >
            <div className="w-10 h-10 rounded-xl border-2 border-current flex items-center justify-center text-2xl font-light leading-none">+</div>
            <span className="text-sm font-medium">Add Composition</span>
          </button>
        )}
      </div>

      {/* Action row */}
      <div className="flex items-center gap-3 mb-6">
        <button
          onClick={handleCompare}
          disabled={loading}
          className="px-6 py-2.5 text-sm font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 transition-all shadow-md shadow-blue-500/20"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Comparing…
            </span>
          ) : (
            `Compare ${comps.length} Compositions →`
          )}
        </button>
        {results.length > 0 && (
          <span className="text-xs text-slate-400">{results.length} results ready</span>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm mb-4">
          <span className="font-medium">Error:</span> {error}
        </div>
      )}

      {/* Results */}
      {results.length > 0 && (
        <div className="space-y-4">
          {/* Chart */}
          <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-slate-700 text-sm">Stacked Cost Comparison</h3>
              <span className="text-xs text-slate-400">$/{unit} catalyst</span>
            </div>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={chartData} barSize={48}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis
                  tickFormatter={(v) => `$${v}/${unit}`}
                  tick={{ fontSize: 11, fill: '#94a3b8' }}
                  axisLine={false}
                  tickLine={false}
                  width={48}
                />
                <Tooltip
                  formatter={(v) => [`$${Number(v).toFixed(3)}/${unit}`]}
                  contentStyle={{ borderRadius: 12, border: '1px solid #e2e8f0', fontSize: 12 }}
                />
                <Legend iconSize={8} iconType="circle" wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="Materials"   stackId="a" fill="#6366f1" />
                <Bar dataKey="Processing"  stackId="a" fill="#10b981" />
                <Bar dataKey="G&A + Margin" stackId="a" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Table */}
          <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
            <div className="px-5 py-3.5 border-b border-slate-100">
              <h3 className="font-semibold text-slate-700 text-sm">Detailed Breakdown</h3>
            </div>
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 text-left text-slate-500 text-xs">
                  <th className="px-5 py-3 font-semibold uppercase tracking-wider">Composition</th>
                  <th className="px-4 py-3 font-semibold uppercase tracking-wider">Scale</th>
                  <th className="px-4 py-3 font-semibold uppercase tracking-wider text-right">Materials</th>
                  <th className="px-4 py-3 font-semibold uppercase tracking-wider text-right">Processing</th>
                  <th className="px-4 py-3 font-semibold uppercase tracking-wider text-right">Total Price</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {results.map((r, i) => {
                  const pal = PALETTE[i];
                  const isBest = i === bestIdx;
                  return (
                    <tr key={i} className="hover:bg-slate-50 transition-colors">
                      <td className="px-5 py-3">
                        <div className="flex items-center gap-2">
                          <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: pal.dot }} />
                          <span className="font-semibold text-slate-800">{r.label}</span>
                          {isBest && (
                            <span className="text-[10px] font-bold bg-emerald-100 text-emerald-700 px-1.5 py-0.5 rounded-full">BEST</span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${pal.badge}`}>
                          {r.scale}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right font-mono text-slate-600">${toDisplay(r.materials_cost_per_lb).toFixed(3)}</td>
                      <td className="px-4 py-3 text-right font-mono text-slate-600">${toDisplay(r.processing_cost_per_lb).toFixed(3)}</td>
                      <td className="px-4 py-3 text-right font-mono font-bold text-slate-800">${toDisplay(r.estimated_price_per_lb).toFixed(3)}{fmtLabel}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
