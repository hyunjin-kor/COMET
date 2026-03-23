import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { fetchPrices, type MetalPrice } from '../lib/api';

export default function Prices() {
  const [prices, setPrices] = useState<MetalPrice[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = () => {
    setLoading(true);
    fetchPrices()
      .then(setPrices)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await fetch('/api/prices/refresh', { method: 'POST' });
      load();
    } catch {
      // ignore
    } finally {
      setRefreshing(false);
    }
  };

  const pgm = prices.filter((p) => ['Pt', 'Pd', 'Rh', 'Ru', 'Ir'].includes(p.symbol));
  const precious = prices.filter((p) => ['Au', 'Ag'].includes(p.symbol));
  const base = prices.filter(
    (p) => !['Pt', 'Pd', 'Rh', 'Ru', 'Ir', 'Au', 'Ag'].includes(p.symbol)
  );

  // Chart data for PGM metals
  const pgmChartData = pgm.map((p) => ({
    symbol: p.symbol,
    price: p.price,
  }));

  const PriceGroup = ({ title, items }: { title: string; items: MetalPrice[] }) => (
    <div className="mb-6">
      <h3 className="text-lg font-semibold text-slate-700 mb-3">{title}</h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {items.map((p) => (
          <div
            key={p.symbol}
            className="bg-white border border-slate-200 rounded-xl p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex justify-between items-start">
              <div>
                <div className="text-lg font-bold text-slate-800">{p.symbol}</div>
                <div className="text-xs text-slate-400">{p.name}</div>
              </div>
              <span
                className={`text-xs px-2 py-0.5 rounded-full ${
                  p.source === 'reference'
                    ? 'bg-yellow-100 text-yellow-700'
                    : 'bg-green-100 text-green-700'
                }`}
              >
                {p.source}
              </span>
            </div>
            <div className="mt-3">
              <span className="text-xl font-bold text-slate-900">
                ${typeof p.price === 'number' ? p.price.toLocaleString() : p.price}
              </span>
              <span className="text-sm text-slate-400 ml-1">{p.unit}</span>
            </div>
            {p.fetched_at && (
              <div className="text-xs text-slate-400 mt-1">
                Updated: {new Date(p.fetched_at).toLocaleDateString()}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );

  if (loading) {
    return <div className="p-6 text-slate-500">Loading prices...</div>;
  }

  return (
    <div className="p-6 max-w-5xl">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-slate-800">Metal Prices</h2>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {refreshing ? 'Refreshing...' : 'Refresh Prices'}
        </button>
      </div>

      {/* PGM Bar Chart */}
      {pgmChartData.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-xl p-5 mb-6">
          <h3 className="font-semibold text-slate-700 mb-3">PGM Price Comparison ($/troy oz)</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={pgmChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="symbol" />
              <YAxis />
              <Tooltip formatter={(v: number) => [`$${v.toLocaleString()}`, 'Price']} />
              <Bar dataKey="price" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {pgm.length > 0 && <PriceGroup title="Platinum Group Metals (PGM)" items={pgm} />}
      {precious.length > 0 && <PriceGroup title="Precious Metals" items={precious} />}
      {base.length > 0 && <PriceGroup title="Base Metals" items={base} />}
    </div>
  );
}
