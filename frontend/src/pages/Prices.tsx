import { useEffect, useState } from 'react';
import {
  XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, ReferenceLine, Area, AreaChart,
} from 'recharts';
import { fetchPrices, type MetalPrice } from '../lib/api';

type HistoryPoint = { date: string; price: number; open: number; high: number; low: number };
type Period = '1mo' | '3mo' | '6mo' | '1y' | '2y' | '5y';

const PERIOD_LABELS: Record<Period, string> = {
  '1mo': '1M', '3mo': '3M', '6mo': '6M', '1y': '1Y', '2y': '2Y', '5y': '5Y',
};

const LIVE_SYMBOLS = new Set(['Pt', 'Pd', 'Au', 'Ag', 'Cu', 'Al', 'Rh']);

const GROUP_ORDER = ['PGM', 'Precious', 'Base'];
const GROUPS: Record<string, { title: string; subtitle: string; symbols: string[]; accent: string }> = {
  PGM:     { title: 'Platinum Group Metals', subtitle: 'PGM',    symbols: ['Pt', 'Pd', 'Rh', 'Ru', 'Ir'], accent: 'violet' },
  Precious:{ title: 'Precious Metals',       subtitle: 'Noble',  symbols: ['Au', 'Ag'],                     accent: 'amber'  },
  Base:    { title: 'Base & Industrial',     subtitle: 'Metals', symbols: ['Ni', 'Co', 'Cu', 'Al', 'Mo', 'W', 'Fe'], accent: 'slate' },
};

const METAL_COLORS: Record<string, string> = {
  Pt: '#818cf8', Pd: '#6366f1', Rh: '#a78bfa',
  Ru: '#c084fc', Ir: '#e879f9',
  Au: '#fbbf24', Ag: '#94a3b8',
  Ni: '#34d399', Co: '#2dd4bf', Cu: '#fb923c',
  Al: '#60a5fa', Mo: '#a3a3a3', W: '#78716c', Fe: '#f87171',
};

function fmtPrice(price: number | null) {
  if (price == null) return '—';
  if (price >= 1000) return `$${price.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
  if (price >= 100)  return `$${price.toLocaleString(undefined, { maximumFractionDigits: 1 })}`;
  return `$${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 4 })}`;
}

function LiveBadge({ isLive }: { isLive: boolean }) {
  if (isLive) {
    return (
      <span className="inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/20">
        <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse" />
        LIVE
      </span>
    );
  }
  return (
    <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-100 text-slate-400 border border-slate-200">
      est.
    </span>
  );
}

export default function Prices() {
  const [prices, setPrices] = useState<(MetalPrice & { is_live?: boolean })[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selected, setSelected] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryPoint[]>([]);
  const [histLoading, setHistLoading] = useState(false);
  const [period, setPeriod] = useState<Period>('1y');
  const [lastUpdate, setLastUpdate] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    fetchPrices()
      .then((data) => {
        setPrices(data as (MetalPrice & { is_live?: boolean })[]);
        const live = (data as (MetalPrice & { is_live?: boolean })[]).find((p) => p.fetched_at && p.is_live);
        if (live?.fetched_at) setLastUpdate(live.fetched_at);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  useEffect(() => {
    if (!selected) return;
    setHistLoading(true);
    fetch(`/api/prices/${selected}/history?period=${period}`)
      .then((r) => r.json())
      .then((d) => setHistory(d.history || []))
      .catch(() => setHistory([]))
      .finally(() => setHistLoading(false));
  }, [selected, period]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await fetch('/api/prices/refresh', { method: 'POST' });
      load();
      if (selected) {
        const r = await fetch(`/api/prices/${selected}/history?period=${period}`);
        const d = await r.json();
        setHistory(d.history || []);
      }
    } catch { /* ignore */ }
    finally { setRefreshing(false); }
  };

  const priceMap = Object.fromEntries(prices.map((p) => [p.symbol, p]));
  const pctChange = history.length >= 2
    ? ((history[history.length - 1].price - history[0].price) / history[0].price) * 100
    : null;
  const isUp = pctChange != null && pctChange >= 0;

  if (loading) {
    return (
      <div className="p-6 flex items-center gap-3 text-slate-500">
        <span className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
        Loading prices…
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-slate-800">Metal Prices</h2>
          <p className="text-sm text-slate-400 mt-0.5">
            {lastUpdate
              ? `Live via Yahoo Finance · Updated ${new Date(lastUpdate).toLocaleTimeString()}`
              : 'Reference prices · CatCost 2018 + ChemPPI escalation'}
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold bg-slate-800 text-slate-200 rounded-xl hover:bg-slate-700 disabled:opacity-50 transition-colors border border-slate-700"
        >
          <svg className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          {refreshing ? 'Refreshing…' : 'Refresh'}
        </button>
      </div>

      {/* Price groups */}
      {GROUP_ORDER.map((gKey) => {
        const { title, subtitle, symbols } = GROUPS[gKey];
        const items = symbols.map((s) => priceMap[s]).filter(Boolean);
        if (!items.length) return null;
        return (
          <div key={gKey} className="mb-7">
            <div className="flex items-baseline gap-2 mb-3">
              <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider">{title}</h3>
              <span className="text-xs text-slate-400">{subtitle}</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-2.5">
              {items.map((p) => {
                const isLive = !!(p as MetalPrice & { is_live?: boolean }).is_live;
                const isSelected = selected === p.symbol;
                const accent = METAL_COLORS[p.symbol] || '#64748b';
                const canChart = LIVE_SYMBOLS.has(p.symbol);
                return (
                  <button
                    key={p.symbol}
                    onClick={() => canChart ? setSelected(isSelected ? null : p.symbol) : undefined}
                    className={`text-left rounded-2xl border p-4 transition-all duration-150 ${
                      isSelected
                        ? 'border-blue-400/50 bg-gradient-to-br from-slate-800 to-slate-900 shadow-xl shadow-blue-900/20'
                        : canChart
                        ? 'border-slate-200 bg-white hover:border-slate-300 hover:shadow-md cursor-pointer'
                        : 'border-slate-200 bg-white cursor-default'
                    }`}
                  >
                    {/* Symbol row */}
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span
                          className="w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold text-white"
                          style={{ background: accent }}
                        >
                          {p.symbol}
                        </span>
                      </div>
                      <LiveBadge isLive={isLive} />
                    </div>

                    {/* Name */}
                    <div className={`text-[11px] mb-2 truncate ${isSelected ? 'text-slate-400' : 'text-slate-400'}`}>
                      {p.name}
                    </div>

                    {/* Price */}
                    <div className={`text-xl font-bold tracking-tight ${isSelected ? 'text-white' : 'text-slate-900'}`}>
                      {fmtPrice(p.price)}
                    </div>
                    <div className={`text-[11px] mt-0.5 ${isSelected ? 'text-slate-500' : 'text-slate-400'}`}>
                      {p.unit}
                    </div>

                    {canChart && !isSelected && (
                      <div className="text-[10px] text-blue-400 mt-1.5 font-medium">view chart →</div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        );
      })}

      {/* History chart panel */}
      {selected && (
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden mt-2">
          {/* Chart header */}
          <div className="flex items-center justify-between px-5 pt-5 pb-4 border-b border-slate-100">
            <div className="flex items-center gap-3">
              <div
                className="w-9 h-9 rounded-xl flex items-center justify-center text-sm font-bold text-white shadow-sm"
                style={{ background: METAL_COLORS[selected] || '#64748b' }}
              >
                {selected}
              </div>
              <div>
                <div className="font-bold text-slate-800 text-sm">
                  {priceMap[selected]?.name || selected}
                </div>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="text-xs text-slate-400">Price history</span>
                  {pctChange != null && (
                    <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                      isUp ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-600'
                    }`}>
                      {isUp ? '▲' : '▼'} {Math.abs(pctChange).toFixed(1)}%
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Period selector */}
            <div className="flex gap-0.5 bg-slate-100 p-1 rounded-xl">
              {(Object.keys(PERIOD_LABELS) as Period[]).map((p) => (
                <button
                  key={p}
                  onClick={() => setPeriod(p)}
                  className={`px-2.5 py-1 text-xs rounded-lg font-semibold transition-all ${
                    period === p
                      ? 'bg-white shadow text-slate-800'
                      : 'text-slate-500 hover:text-slate-700'
                  }`}
                >
                  {PERIOD_LABELS[p]}
                </button>
              ))}
            </div>
          </div>

          {/* Chart body */}
          <div className="px-2 py-4">
            {histLoading ? (
              <div className="flex items-center justify-center h-52 text-slate-400 gap-2">
                <span className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                Loading…
              </div>
            ) : history.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-52 text-slate-400 gap-2">
                <svg className="w-8 h-8 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="text-sm">No history data for {selected}</span>
                <span className="text-xs">Charts available for: {[...LIVE_SYMBOLS].join(', ')}</span>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <AreaChart data={history} margin={{ top: 4, right: 16, bottom: 0, left: 4 }}>
                  <defs>
                    <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={METAL_COLORS[selected] || '#6366f1'} stopOpacity={0.15} />
                      <stop offset="95%" stopColor={METAL_COLORS[selected] || '#6366f1'} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                  <XAxis
                    dataKey="date"
                    tickFormatter={(d) => {
                      const date = new Date(d);
                      return period === '1mo'
                        ? date.toLocaleDateString('en', { month: 'short', day: 'numeric' })
                        : date.toLocaleDateString('en', { year: '2-digit', month: 'short' });
                    }}
                    interval="preserveStartEnd"
                    tick={{ fontSize: 11, fill: '#94a3b8' }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tickFormatter={(v) => `$${Number(v).toLocaleString()}`}
                    tick={{ fontSize: 11, fill: '#94a3b8' }}
                    width={72}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip
                    formatter={(v) => [`$${Number(v).toLocaleString()}`, priceMap[selected]?.unit || '']}
                    labelFormatter={(d) => new Date(d).toLocaleDateString('en', { year: 'numeric', month: 'long', day: 'numeric' })}
                    contentStyle={{ borderRadius: 12, border: '1px solid #e2e8f0', fontSize: 12, boxShadow: '0 4px 16px rgba(0,0,0,0.1)' }}
                  />
                  {history.length > 0 && (
                    <ReferenceLine y={history[0].price} stroke="#e2e8f0" strokeDasharray="4 4" strokeWidth={1} />
                  )}
                  <Area
                    type="monotone"
                    dataKey="price"
                    stroke={METAL_COLORS[selected] || '#6366f1'}
                    strokeWidth={2}
                    fill="url(#colorPrice)"
                    dot={false}
                    activeDot={{ r: 4, fill: METAL_COLORS[selected] || '#6366f1', strokeWidth: 0 }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* Stats row */}
          {history.length > 0 && !histLoading && (
            <div className="flex flex-wrap gap-6 px-5 py-3 border-t border-slate-100 bg-slate-50">
              {[
                { label: 'Current', value: fmtPrice(history[history.length - 1].price), color: 'text-slate-800' },
                { label: 'Period High', value: fmtPrice(Math.max(...history.map(h => h.high ?? h.price))), color: 'text-emerald-600' },
                { label: 'Period Low',  value: fmtPrice(Math.min(...history.map(h => h.low ?? h.price))),  color: 'text-red-500' },
              ].map(s => (
                <div key={s.label} className="flex items-center gap-2 text-sm">
                  <span className="text-slate-400">{s.label}</span>
                  <span className={`font-bold ${s.color}`}>{s.value}</span>
                </div>
              ))}
              <div className="ml-auto text-xs text-slate-400 self-center">
                Yahoo Finance · {history.length} pts
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
