import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from 'recharts';

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

export default function Uncertainty() {
  const [result, setResult] = useState<MCResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [metalSymbol, setMetalSymbol] = useState('Ni');
  const [metalPrice, setMetalPrice] = useState(7.5);
  const [loading_pct, setLoadingPct] = useState(15);
  const [orderSize, setOrderSize] = useState(20);
  const [nSim, setNSim] = useState(1000);

  const handleRun = async () => {
    setLoading(true);
    setError('');
    try {
      const resp = await fetch('/api/uncertainty', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          metal_symbol: metalSymbol,
          metal_price: metalPrice,
          metal_price_unit: '$/lb',
          metal_loading_wt_pct: loading_pct,
          order_size_tons: orderSize,
          n_simulations: nSim,
          uncertainties: {
            metal_price: [0.7, 1.3],
            support_price_per_lb: [0.8, 1.2],
            order_size_tons: [0.8, 1.2],
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

  // Create histogram-like data from percentiles
  const histData = result
    ? [
        { range: `$${result.min.toFixed(1)}-${result.p5.toFixed(1)}`, value: 5, fill: '#fca5a5' },
        { range: `$${result.p5.toFixed(1)}-${result.p25.toFixed(1)}`, value: 20, fill: '#fcd34d' },
        { range: `$${result.p25.toFixed(1)}-${result.median.toFixed(1)}`, value: 25, fill: '#86efac' },
        { range: `$${result.median.toFixed(1)}-${result.p75.toFixed(1)}`, value: 25, fill: '#86efac' },
        { range: `$${result.p75.toFixed(1)}-${result.p95.toFixed(1)}`, value: 20, fill: '#fcd34d' },
        { range: `$${result.p95.toFixed(1)}-${result.max.toFixed(1)}`, value: 5, fill: '#fca5a5' },
      ]
    : [];

  return (
    <div className="p-6 max-w-5xl">
      <h2 className="text-2xl font-bold text-slate-800 mb-6">Uncertainty Analysis</h2>
      <p className="text-sm text-slate-500 mb-4">
        Monte Carlo simulation to estimate the range of possible catalyst costs given input uncertainties.
      </p>

      <div className="bg-white border border-slate-200 rounded-xl p-5 mb-4">
        <h3 className="font-semibold text-slate-700 mb-3">Parameters</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <label className="block">
            <span className="text-xs text-slate-500">Metal</span>
            <input value={metalSymbol} onChange={(e) => setMetalSymbol(e.target.value)} className="mt-1 block w-full rounded border border-slate-300 px-2 py-1.5 text-sm" />
          </label>
          <label className="block">
            <span className="text-xs text-slate-500">Price ($/lb)</span>
            <input type="number" value={metalPrice} onChange={(e) => setMetalPrice(+e.target.value)} className="mt-1 block w-full rounded border border-slate-300 px-2 py-1.5 text-sm" />
          </label>
          <label className="block">
            <span className="text-xs text-slate-500">Loading (wt%)</span>
            <input type="number" value={loading_pct} onChange={(e) => setLoadingPct(+e.target.value)} className="mt-1 block w-full rounded border border-slate-300 px-2 py-1.5 text-sm" />
          </label>
          <label className="block">
            <span className="text-xs text-slate-500">Order (tons)</span>
            <input type="number" value={orderSize} onChange={(e) => setOrderSize(+e.target.value)} className="mt-1 block w-full rounded border border-slate-300 px-2 py-1.5 text-sm" />
          </label>
          <label className="block">
            <span className="text-xs text-slate-500">Simulations</span>
            <input type="number" value={nSim} onChange={(e) => setNSim(+e.target.value)} className="mt-1 block w-full rounded border border-slate-300 px-2 py-1.5 text-sm" />
          </label>
        </div>
        <button
          onClick={handleRun}
          disabled={loading}
          className="mt-4 px-6 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Running...' : 'Run Monte Carlo'}
        </button>
      </div>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm mb-4">{error}</div>}

      {result && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-3">
              <div className="text-xs text-blue-600">Mean</div>
              <div className="text-xl font-bold text-blue-800">${result.mean.toFixed(2)}/lb</div>
            </div>
            <div className="bg-green-50 border border-green-200 rounded-xl p-3">
              <div className="text-xs text-green-600">Median</div>
              <div className="text-xl font-bold text-green-800">${result.median.toFixed(2)}/lb</div>
            </div>
            <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-3">
              <div className="text-xs text-yellow-600">90% CI Range</div>
              <div className="text-lg font-bold text-yellow-800">
                ${result.p5.toFixed(2)} - ${result.p95.toFixed(2)}
              </div>
            </div>
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-3">
              <div className="text-xs text-slate-600">Std Dev</div>
              <div className="text-xl font-bold text-slate-800">${result.std.toFixed(3)}</div>
            </div>
          </div>

          {/* Distribution Chart */}
          <div className="bg-white border border-slate-200 rounded-xl p-5">
            <h3 className="font-semibold text-slate-700 mb-3">
              Cost Distribution ({result.n_successful.toLocaleString()} simulations)
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={histData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="range" tick={{ fontSize: 11 }} />
                <YAxis label={{ value: 'Percentile %', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <ReferenceLine y={0} stroke="#000" />
                <Bar dataKey="value" name="Distribution %" radius={[4, 4, 0, 0]}>
                  {histData.map((entry, i) => (
                    <Bar key={i} dataKey="value" fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  );
}
