import { useState } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { calculateCost, type CostInput, type CostResult } from '../lib/api';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

const defaultInput: CostInput = {
  metal_symbol: 'Ni',
  metal_price: 7.5,
  metal_price_unit: '$/lb',
  metal_loading_wt_pct: 15,
  support_name: 'Al2O3',
  support_price_per_lb: 0.5,
  steps: ['mixer_slurry', 'incipient_wetness', 'dryer_rotary_100_300C'],
  order_size_tons: 20,
};

export default function Calculator() {
  const [input, setInput] = useState<CostInput>(defaultInput);
  const [result, setResult] = useState<CostResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await calculateCost(input);
      setResult(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Calculation failed');
    } finally {
      setLoading(false);
    }
  };

  const update = (field: keyof CostInput, value: string | number) => {
    setInput((prev) => ({ ...prev, [field]: value }));
  };

  const pieData = result
    ? [
        { name: 'Materials', value: result.summary.materials_pct },
        { name: 'Processing', value: result.summary.processing_pct },
        {
          name: 'Overhead & Margin',
          value: Math.max(0, 100 - result.summary.materials_pct - result.summary.processing_pct),
        },
      ]
    : [];

  return (
    <div className="p-6 max-w-5xl">
      <h2 className="text-2xl font-bold text-slate-800 mb-6">Catalyst Cost Calculator</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="bg-white border border-slate-200 rounded-xl p-5 space-y-4">
            <h3 className="font-semibold text-slate-700">Composition</h3>

            <div className="grid grid-cols-2 gap-3">
              <label className="block">
                <span className="text-sm text-slate-600">Metal Symbol</span>
                <input
                  type="text"
                  value={input.metal_symbol}
                  onChange={(e) => update('metal_symbol', e.target.value)}
                  className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                />
              </label>
              <label className="block">
                <span className="text-sm text-slate-600">Metal Price</span>
                <input
                  type="number"
                  step="0.01"
                  value={input.metal_price}
                  onChange={(e) => update('metal_price', +e.target.value)}
                  className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                />
              </label>
              <label className="block">
                <span className="text-sm text-slate-600">Price Unit</span>
                <select
                  value={input.metal_price_unit}
                  onChange={(e) => update('metal_price_unit', e.target.value)}
                  className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                >
                  <option value="$/troy_oz">$/troy oz</option>
                  <option value="$/lb">$/lb</option>
                  <option value="$/kg">$/kg</option>
                </select>
              </label>
              <label className="block">
                <span className="text-sm text-slate-600">Loading (wt%)</span>
                <input
                  type="number"
                  step="0.1"
                  value={input.metal_loading_wt_pct}
                  onChange={(e) => update('metal_loading_wt_pct', +e.target.value)}
                  className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                />
              </label>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <label className="block">
                <span className="text-sm text-slate-600">Support</span>
                <select
                  value={input.support_name}
                  onChange={(e) => update('support_name', e.target.value)}
                  className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                >
                  <option value="Al2O3">Al2O3 (Alumina)</option>
                  <option value="SiO2">SiO2 (Silica)</option>
                  <option value="TiO2">TiO2 (Titania)</option>
                  <option value="Carbon">Activated Carbon</option>
                  <option value="ZSM-5">ZSM-5 Zeolite</option>
                  <option value="USY">USY Zeolite</option>
                </select>
              </label>
              <label className="block">
                <span className="text-sm text-slate-600">Support Price ($/lb)</span>
                <input
                  type="number"
                  step="0.01"
                  value={input.support_price_per_lb}
                  onChange={(e) => update('support_price_per_lb', +e.target.value)}
                  className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                />
              </label>
            </div>

            <label className="block">
              <span className="text-sm text-slate-600">Order Size (tons)</span>
              <input
                type="number"
                step="1"
                value={input.order_size_tons}
                onChange={(e) => update('order_size_tons', +e.target.value)}
                className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            </label>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {loading ? 'Calculating...' : 'Calculate Cost'}
          </button>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}
        </form>

        {/* Results */}
        {result && (
          <div className="space-y-4">
            {/* Summary Cards */}
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                <div className="text-sm text-blue-600">Estimated Price</div>
                <div className="text-2xl font-bold text-blue-800">
                  ${result.summary.estimated_price_per_lb.toFixed(2)}
                  <span className="text-sm font-normal">/lb</span>
                </div>
                <div className="text-xs text-blue-500 mt-1">
                  ${result.summary.estimated_price_per_kg.toFixed(2)}/kg
                </div>
              </div>
              <div className="bg-green-50 border border-green-200 rounded-xl p-4">
                <div className="text-sm text-green-600">Scale</div>
                <div className="text-2xl font-bold text-green-800 capitalize">
                  {result.step_method.scale}
                </div>
                <div className="text-xs text-green-500 mt-1">
                  {result.step_method.campaign_days} day campaign
                </div>
              </div>
            </div>

            {/* Pie Chart */}
            <div className="bg-white border border-slate-200 rounded-xl p-5">
              <h3 className="font-semibold text-slate-700 mb-3">Cost Breakdown</h3>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    dataKey="value"
                    label={({ name, value }) => `${name} ${value.toFixed(1)}%`}
                  >
                    {pieData.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(v: number) => `${v.toFixed(1)}%`} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Detail Table */}
            <div className="bg-white border border-slate-200 rounded-xl p-5">
              <h3 className="font-semibold text-slate-700 mb-3">Cost Details</h3>
              <table className="w-full text-sm">
                <tbody className="divide-y divide-slate-100">
                  <tr>
                    <td className="py-1.5 text-slate-500">Materials Cost</td>
                    <td className="py-1.5 text-right font-mono">
                      ${result.materials.total_materials_cost_per_lb.toFixed(4)}/lb
                    </td>
                  </tr>
                  <tr>
                    <td className="py-1.5 text-slate-500">Processing Cost</td>
                    <td className="py-1.5 text-right font-mono">
                      ${result.step_method.processing_cost_per_lb.toFixed(4)}/lb
                    </td>
                  </tr>
                  <tr>
                    <td className="py-1.5 text-slate-500">Margin</td>
                    <td className="py-1.5 text-right font-mono">
                      {result.step_method.margin_pct}%
                    </td>
                  </tr>
                  <tr className="font-semibold">
                    <td className="py-1.5">Total Estimated Price</td>
                    <td className="py-1.5 text-right font-mono">
                      ${result.summary.estimated_price_per_lb.toFixed(4)}/lb
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
