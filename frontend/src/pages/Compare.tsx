import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';

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

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'];

export default function Compare() {
  const [comps, setComps] = useState<Composition[]>([emptyComp(), emptyComp()]);
  const [results, setResults] = useState<CompareResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const updateComp = (i: number, field: keyof Composition, value: string | number) => {
    setComps((prev) => prev.map((c, idx) => (idx === i ? { ...c, [field]: value } : c)));
  };

  const addComp = () => {
    if (comps.length < 4) setComps([...comps, emptyComp()]);
  };

  const removeComp = (i: number) => {
    if (comps.length > 2) setComps(comps.filter((_, idx) => idx !== i));
  };

  const handleCompare = async () => {
    setLoading(true);
    setError('');
    try {
      const resp = await fetch('/api/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ compositions: comps }),
      });
      if (!resp.ok) throw new Error((await resp.json()).detail);
      const data = await resp.json();
      setResults(data.compositions);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Compare failed');
    } finally {
      setLoading(false);
    }
  };

  const chartData = results.map((r) => ({
    name: r.label,
    Materials: +r.materials_cost_per_lb.toFixed(2),
    Processing: +r.processing_cost_per_lb.toFixed(2),
    'Overhead & Margin': +(r.estimated_price_per_lb - r.materials_cost_per_lb - r.processing_cost_per_lb).toFixed(2),
  }));

  return (
    <div className="p-6 max-w-5xl">
      <h2 className="text-2xl font-bold text-slate-800 mb-6">Compare Compositions</h2>

      <div className="space-y-3 mb-4">
        {comps.map((c, i) => (
          <div key={i} className="bg-white border border-slate-200 rounded-xl p-4">
            <div className="flex items-center justify-between mb-3">
              <span className="font-semibold text-sm" style={{ color: COLORS[i] }}>
                Composition {i + 1}
              </span>
              {comps.length > 2 && (
                <button onClick={() => removeComp(i)} className="text-xs text-red-500 hover:text-red-700">
                  Remove
                </button>
              )}
            </div>
            <div className="grid grid-cols-4 gap-2">
              <input
                placeholder="Label"
                value={c.label}
                onChange={(e) => updateComp(i, 'label', e.target.value)}
                className="rounded border border-slate-300 px-2 py-1.5 text-sm"
              />
              <input
                placeholder="Metal"
                value={c.metal_symbol}
                onChange={(e) => updateComp(i, 'metal_symbol', e.target.value)}
                className="rounded border border-slate-300 px-2 py-1.5 text-sm"
              />
              <input
                type="number"
                placeholder="Loading wt%"
                value={c.metal_loading_wt_pct}
                onChange={(e) => updateComp(i, 'metal_loading_wt_pct', +e.target.value)}
                className="rounded border border-slate-300 px-2 py-1.5 text-sm"
              />
              <input
                type="number"
                placeholder="Order (tons)"
                value={c.order_size_tons}
                onChange={(e) => updateComp(i, 'order_size_tons', +e.target.value)}
                className="rounded border border-slate-300 px-2 py-1.5 text-sm"
              />
            </div>
          </div>
        ))}
      </div>

      <div className="flex gap-3 mb-6">
        {comps.length < 4 && (
          <button onClick={addComp} className="px-4 py-2 text-sm border border-slate-300 rounded-lg hover:bg-slate-50">
            + Add Composition
          </button>
        )}
        <button
          onClick={handleCompare}
          disabled={loading}
          className="px-6 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Comparing...' : 'Compare'}
        </button>
      </div>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm mb-4">{error}</div>}

      {results.length > 0 && (
        <>
          <div className="bg-white border border-slate-200 rounded-xl p-5 mb-4">
            <h3 className="font-semibold text-slate-700 mb-3">Stacked Cost Comparison</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="name" />
                <YAxis label={{ value: '$/lb', angle: -90, position: 'insideLeft' }} />
                <Tooltip formatter={(v: number) => `$${v.toFixed(2)}`} />
                <Legend />
                <Bar dataKey="Materials" stackId="a" fill="#3b82f6" />
                <Bar dataKey="Processing" stackId="a" fill="#10b981" />
                <Bar dataKey="Overhead & Margin" stackId="a" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 text-left text-slate-600">
                  <th className="px-4 py-3 font-medium">Composition</th>
                  <th className="px-4 py-3 font-medium">Scale</th>
                  <th className="px-4 py-3 font-medium text-right">Materials</th>
                  <th className="px-4 py-3 font-medium text-right">Processing</th>
                  <th className="px-4 py-3 font-medium text-right">Total Price</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {results.map((r, i) => (
                  <tr key={i}>
                    <td className="px-4 py-2.5 font-medium" style={{ color: COLORS[i] }}>{r.label}</td>
                    <td className="px-4 py-2.5 capitalize">{r.scale}</td>
                    <td className="px-4 py-2.5 text-right font-mono">${r.materials_cost_per_lb.toFixed(2)}</td>
                    <td className="px-4 py-2.5 text-right font-mono">${r.processing_cost_per_lb.toFixed(2)}</td>
                    <td className="px-4 py-2.5 text-right font-mono font-bold">${r.estimated_price_per_lb.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
