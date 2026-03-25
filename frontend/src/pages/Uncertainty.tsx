import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';
import { useUnit } from '../lib/use-unit';

interface MCResult {
  mean: number;
  median: number;
  std: number;
  min: number;
  max: number;
  p5: number;
  p25: number;
  p75: number;
  p95: number;
  n_simulations: number;
  n_successful: number;
}

const KNOWN_METALS = ['Ni', 'Co', 'Pt', 'Pd', 'Rh', 'Ru', 'Cu', 'Fe', 'Mo', 'W'];

export default function Uncertainty() {
  const { unit, toDisplay, toInternal, fmtLabel } = useUnit();
  const [result, setResult] = useState<MCResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]   = useState('');

  const [metalSymbol, setMetalSymbol]   = useState('Ni');
  const [metalPriceInternal, setMetalPriceInternal] = useState(7.5); // always $/lb internally
  const [loadingPct, setLoadingPct]   = useState(15);
  const [orderSize, setOrderSize]     = useState(20);
  const [nSim, setNSim]               = useState(1000);

  const handleRun = async () => {
    setLoading(true); setError('');
    try {
      const resp = await fetch('/api/uncertainty', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          metal_symbol: metalSymbol,
          metal_price: metalPriceInternal,
          metal_price_unit: '$/lb',
          metal_loading_wt_pct: loadingPct,
          order_size_tons: orderSize,
          n_simulations: nSim,
          uncertainties: {
            metal_price:         [0.7, 1.3],
            support_price_per_lb:[0.8, 1.2],
            order_size_tons:     [0.8, 1.2],
          },
        }),
      });
      if (!resp.ok) throw new Error((await resp.json()).detail);
      setResult(await resp.json());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  // Percentile histogram data
  const d = (v: number) => toDisplay(v);
  const histData = result ? [
    { range: `$${d(result.min).toFixed(1)}–${d(result.p5).toFixed(1)}`,      value: 5,  label: 'Bottom 5%',   fill: '#fca5a5' },
    { range: `$${d(result.p5).toFixed(1)}–${d(result.p25).toFixed(1)}`,      value: 20, label: '5–25th pctl', fill: '#fde68a' },
    { range: `$${d(result.p25).toFixed(1)}–${d(result.median).toFixed(1)}`,  value: 25, label: '25–50th pctl',fill: '#6ee7b7' },
    { range: `$${d(result.median).toFixed(1)}–${d(result.p75).toFixed(1)}`,  value: 25, label: '50–75th pctl',fill: '#6ee7b7' },
    { range: `$${d(result.p75).toFixed(1)}–${d(result.p95).toFixed(1)}`,     value: 20, label: '75–95th pctl',fill: '#fde68a' },
    { range: `$${d(result.p95).toFixed(1)}–${d(result.max).toFixed(1)}`,     value: 5,  label: 'Top 5%',      fill: '#fca5a5' },
  ] : [];

  return (
    <div className="p-6 max-w-4xl">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-xl font-bold text-slate-800">Uncertainty Analysis</h2>
        <p className="text-sm text-slate-400 mt-0.5">
          Monte Carlo simulation — 입력 불확실성에 따른 제조원가 범위를 추정합니다
        </p>
      </div>

      {/* Parameter card */}
      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-5 mb-5">
        <h3 className="font-semibold text-slate-700 text-sm mb-4">Simulation Parameters</h3>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
          <div>
            <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Metal</label>
            <select
              value={metalSymbol}
              onChange={e => setMetalSymbol(e.target.value)}
              className="w-full input-base"
            >
              {KNOWN_METALS.map(m => <option key={m}>{m}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Price ($/{unit})</label>
            <input
              type="number" step="0.01"
              value={toDisplay(metalPriceInternal).toFixed(2)}
              onChange={e => setMetalPriceInternal(toInternal(+e.target.value))}
              className="w-full input-base font-mono"
            />
          </div>
          <div>
            <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Loading (wt%)</label>
            <input
              type="number" step="0.5"
              value={loadingPct}
              onChange={e => setLoadingPct(+e.target.value)}
              className="w-full input-base font-mono"
            />
          </div>
          <div>
            <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Order (tons)</label>
            <input
              type="number" step="1"
              value={orderSize}
              onChange={e => setOrderSize(+e.target.value)}
              className="w-full input-base font-mono"
            />
          </div>
          <div>
            <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Simulations</label>
            <input
              type="number" step="100" min="100" max="10000"
              value={nSim}
              onChange={e => setNSim(+e.target.value)}
              className="w-full input-base font-mono"
            />
          </div>
        </div>

        {/* Uncertainty ranges note */}
        <div className="bg-slate-50 rounded-xl px-4 py-3 text-xs text-slate-500 mb-4 border border-slate-100">
          <span className="font-semibold text-slate-600">Assumed uncertainty ranges:</span>
          &nbsp; Metal price ±30% · Support price ±20% · Order size ±20% &nbsp;
          <span className="text-slate-400">(uniform distribution)</span>
        </div>

        <button
          onClick={handleRun}
          disabled={loading}
          className="px-6 py-2.5 text-sm font-semibold bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-xl hover:from-violet-700 hover:to-purple-700 disabled:opacity-50 transition-all shadow-md shadow-violet-500/20"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Running {nSim.toLocaleString()} simulations…
            </span>
          ) : (
            `Run Monte Carlo (${nSim.toLocaleString()} simulations) →`
          )}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm mb-4">
          <span className="font-medium">Error:</span> {error}
        </div>
      )}

      {result && (
        <div className="space-y-4">
          {/* KPI cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <StatCard
              label="Mean"
              value={`$${d(result.mean).toFixed(2)}${fmtLabel}`}
              sub="Average cost"
              color="bg-gradient-to-br from-violet-500 to-purple-600"
            />
            <StatCard
              label="Median"
              value={`$${d(result.median).toFixed(2)}${fmtLabel}`}
              sub="50th percentile"
              color="bg-gradient-to-br from-blue-500 to-indigo-600"
            />
            <StatCard
              label="90% CI"
              value={`$${d(result.p5).toFixed(2)} – $${d(result.p95).toFixed(2)}`}
              sub="5th–95th percentile"
              color="bg-gradient-to-br from-emerald-500 to-teal-600"
              small
            />
            <StatCard
              label="Std Dev"
              value={`$${d(result.std).toFixed(3)}`}
              sub={`Range: $${d(result.min).toFixed(2)}–$${d(result.max).toFixed(2)}`}
              color="bg-gradient-to-br from-slate-600 to-slate-700"
            />
          </div>

          {/* Distribution chart */}
          <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-5">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-semibold text-slate-700 text-sm">Cost Distribution</h3>
                <p className="text-xs text-slate-400 mt-0.5">{result.n_successful.toLocaleString()} successful simulations</p>
              </div>
              <div className="flex items-center gap-3 text-xs text-slate-500">
                <span className="flex items-center gap-1">
                  <span className="w-3 h-3 rounded-sm bg-emerald-200 inline-block" />
                  IQR (25–75%)
                </span>
                <span className="flex items-center gap-1">
                  <span className="w-3 h-3 rounded-sm bg-amber-200 inline-block" />
                  5–25% / 75–95%
                </span>
                <span className="flex items-center gap-1">
                  <span className="w-3 h-3 rounded-sm bg-red-200 inline-block" />
                  Tails
                </span>
              </div>
            </div>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={histData} barSize={56}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="range" tick={{ fontSize: 10, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                <YAxis
                  label={{ value: 'Share (%)', angle: -90, position: 'insideLeft', style: { fontSize: 11, fill: '#94a3b8' } }}
                  tick={{ fontSize: 11, fill: '#94a3b8' }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  formatter={(v) => [`${v}% of simulations`, 'Distribution']}
                  contentStyle={{ borderRadius: 12, border: '1px solid #e2e8f0', fontSize: 12 }}
                />
                <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                  {histData.map((entry, i) => (
                    <Cell key={i} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Percentile table */}
          <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
            <div className="px-5 py-3.5 border-b border-slate-100">
              <h3 className="font-semibold text-slate-700 text-sm">Percentile Summary</h3>
            </div>
            <div className="grid grid-cols-7 text-center text-xs divide-x divide-slate-100">
              {[
                { label: 'Min',    value: d(result.min),    color: 'text-red-600' },
                { label: 'P5',     value: d(result.p5),     color: 'text-orange-500' },
                { label: 'P25',    value: d(result.p25),    color: 'text-amber-500' },
                { label: 'Median', value: d(result.median), color: 'text-emerald-600' },
                { label: 'P75',    value: d(result.p75),    color: 'text-amber-500' },
                { label: 'P95',    value: d(result.p95),    color: 'text-orange-500' },
                { label: 'Max',    value: d(result.max),    color: 'text-red-600' },
              ].map(p => (
                <div key={p.label} className="py-3.5">
                  <div className="text-slate-400 mb-1">{p.label}</div>
                  <div className={`font-bold font-mono ${p.color}`}>${p.value.toFixed(2)}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({
  label, value, sub, color, small,
}: { label: string; value: string; sub: string; color: string; small?: boolean }) {
  return (
    <div className={`${color} rounded-2xl p-4 text-white shadow-md`}>
      <div className="text-xs opacity-70 font-semibold uppercase tracking-wider mb-2">{label}</div>
      <div className={`font-bold tracking-tight leading-tight ${small ? 'text-base' : 'text-2xl'}`}>{value}</div>
      <div className="text-xs opacity-60 mt-1.5">{sub}</div>
    </div>
  );
}
