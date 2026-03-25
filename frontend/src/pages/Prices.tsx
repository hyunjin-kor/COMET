import { useEffect, useState } from 'react';
import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { fetchPrices, type MetalPrice } from '../lib/api';

type HistoryPoint = { date: string; price: number; open: number; high: number; low: number };
type Period = '1mo' | '3mo' | '6mo' | '1y' | '2y' | '5y';

const PERIOD_LABELS: Record<Period, string> = {
  '1mo': '1M',
  '3mo': '3M',
  '6mo': '6M',
  '1y': '1Y',
  '2y': '2Y',
  '5y': '5Y',
};

const GROUP_ORDER = ['PGM', 'Precious', 'Base'];
const GROUPS: Record<string, { title: string; subtitle: string; symbols: string[] }> = {
  PGM: { title: 'Platinum Group Metals', subtitle: 'PGM', symbols: ['Pt', 'Pd', 'Rh', 'Ru', 'Ir'] },
  Precious: { title: 'Precious Metals', subtitle: 'Noble', symbols: ['Au', 'Ag'] },
  Base: { title: 'Base & Industrial', subtitle: 'Metals', symbols: ['Ni', 'Co', 'Cu', 'Al', 'Mo', 'W', 'Fe'] },
};

const METAL_COLORS: Record<string, string> = {
  Pt: '#818cf8',
  Pd: '#6366f1',
  Rh: '#a78bfa',
  Ru: '#c084fc',
  Ir: '#e879f9',
  Au: '#fbbf24',
  Ag: '#94a3b8',
  Ni: '#34d399',
  Co: '#2dd4bf',
  Cu: '#fb923c',
  Al: '#60a5fa',
  Mo: '#a3a3a3',
  W: '#78716c',
  Fe: '#f87171',
};

function fmtPrice(price: number | null) {
  if (price == null) return 'N/A';
  if (price >= 1000) return `$${price.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
  if (price >= 100) return `$${price.toLocaleString(undefined, { maximumFractionDigits: 1 })}`;
  return `$${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 4 })}`;
}

function sourceBadgeStyles(sourceType: MetalPrice['source_type']) {
  if (sourceType === 'live') {
    return {
      text: 'LIVE',
      className: 'border-emerald-500/20 bg-emerald-500/10 text-emerald-600',
      dot: 'bg-emerald-400 animate-pulse',
    };
  }
  if (sourceType === 'indexed') {
    return {
      text: 'INDEXED',
      className: 'border-amber-200 bg-amber-50 text-amber-700',
      dot: 'bg-amber-400',
    };
  }
  return {
    text: 'MANUAL',
    className: 'border-slate-200 bg-slate-100 text-slate-600',
    dot: 'bg-slate-400',
  };
}

function SourceBadge({ sourceType }: { sourceType: MetalPrice['source_type'] }) {
  const badge = sourceBadgeStyles(sourceType);
  return (
    <span className={`inline-flex items-center gap-1 rounded-full border px-1.5 py-0.5 text-[10px] font-semibold ${badge.className}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${badge.dot}`} />
      {badge.text}
    </span>
  );
}

function sourceSummary(rows: (MetalPrice & { is_live?: boolean })[]) {
  const liveCount = rows.filter((row) => row.source_type === 'live').length;
  const indexedCount = rows.filter((row) => row.source_type === 'indexed').length;
  return `${liveCount} live · ${indexedCount} indexed`;
}

function sourceDescription(row: MetalPrice) {
  if (row.source_type === 'live') return row.source;
  if (row.source_type === 'indexed') return 'CatCost reference + ChemPPI trend adjustment';
  return 'Manual price input';
}

export default function Prices() {
  const [prices, setPrices] = useState<(MetalPrice & { is_live?: boolean })[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selected, setSelected] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryPoint[]>([]);
  const [historySource, setHistorySource] = useState<string | null>(null);
  const [histLoading, setHistLoading] = useState(false);
  const [period, setPeriod] = useState<Period>('1y');
  const [lastUpdate, setLastUpdate] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    fetchPrices()
      .then((data) => {
        const rows = data as (MetalPrice & { is_live?: boolean })[];
        setPrices(rows);
        const freshest = rows.find((row) => row.fetched_at);
        if (freshest?.fetched_at) setLastUpdate(freshest.fetched_at);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  useEffect(() => {
    if (!selected) return;
    setHistLoading(true);
    fetch(`/api/prices/${selected}/history?period=${period}`)
      .then((response) => response.json())
      .then((payload) => {
        setHistory(payload.history || []);
        setHistorySource(payload.source || null);
      })
      .catch(() => {
        setHistory([]);
        setHistorySource(null);
      })
      .finally(() => setHistLoading(false));
  }, [selected, period]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await fetch('/api/prices/refresh', { method: 'POST' });
      load();
      if (selected) {
        const response = await fetch(`/api/prices/${selected}/history?period=${period}`);
        const payload = await response.json();
        setHistory(payload.history || []);
        setHistorySource(payload.source || null);
      }
    } catch {
      // Keep the current snapshot if refresh fails.
    } finally {
      setRefreshing(false);
    }
  };

  const priceMap = Object.fromEntries(prices.map((row) => [row.symbol, row]));
  const pctChange = history.length >= 2
    ? ((history[history.length - 1].price - history[0].price) / history[0].price) * 100
    : null;
  const isUp = pctChange != null && pctChange >= 0;

  if (loading) {
    return (
      <div className="flex items-center gap-3 p-6 text-slate-500">
        <span className="h-4 w-4 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
        Loading prices...
      </div>
    );
  }

  return (
    <div className="max-w-7xl p-6">
      <div className="mb-6 flex items-start justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-800">Metal Prices</h2>
          <p className="mt-0.5 text-sm text-slate-400">
            {lastUpdate
              ? `Feeds and indexed benchmarks · Updated ${new Date(lastUpdate).toLocaleTimeString()}`
              : 'Live feeds and indexed benchmarks'}
          </p>
          <p className="mt-1 text-xs text-slate-400">{sourceSummary(prices)}</p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-800 px-3.5 py-2 text-xs font-semibold text-slate-200 transition-colors hover:bg-slate-700 disabled:opacity-50"
        >
          <svg className={`h-3.5 w-3.5 ${refreshing ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          {refreshing ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {GROUP_ORDER.map((groupKey) => {
        const { title, subtitle, symbols } = GROUPS[groupKey];
        const items = symbols.map((symbol) => priceMap[symbol]).filter(Boolean);
        if (!items.length) return null;
        return (
          <div key={groupKey} className="mb-7">
            <div className="mb-3 flex items-baseline gap-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">{title}</h3>
              <span className="text-xs text-slate-400">{subtitle}</span>
            </div>
            <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
              {items.map((priceRow) => {
                const isSelected = selected === priceRow.symbol;
                const accent = METAL_COLORS[priceRow.symbol] || '#64748b';
                return (
                  <button
                    key={priceRow.symbol}
                    onClick={() => setSelected(isSelected ? null : priceRow.symbol)}
                    className={`text-left rounded-2xl border p-4 transition-all duration-150 ${
                      isSelected
                        ? 'border-blue-400/50 bg-gradient-to-br from-slate-800 to-slate-900 shadow-xl shadow-blue-900/20'
                        : 'cursor-pointer border-slate-200 bg-white hover:border-slate-300 hover:shadow-md'
                    }`}
                  >
                    <div className="mb-2 flex items-center justify-between">
                      <span
                        className="flex h-7 w-7 items-center justify-center rounded-lg text-xs font-bold text-white"
                        style={{ background: accent }}
                      >
                        {priceRow.symbol}
                      </span>
                      <SourceBadge sourceType={priceRow.source_type} />
                    </div>

                    <div className="mb-2 truncate text-[11px] text-slate-400">{priceRow.name}</div>

                    <div className={`text-xl font-bold tracking-tight ${isSelected ? 'text-white' : 'text-slate-900'}`}>
                      {fmtPrice(priceRow.price)}
                    </div>
                    <div className={`mt-0.5 text-[11px] ${isSelected ? 'text-slate-500' : 'text-slate-400'}`}>
                      {priceRow.unit}
                    </div>
                    <div className={`mt-2 truncate text-[10px] ${isSelected ? 'text-slate-500' : 'text-slate-400'}`}>
                      {sourceDescription(priceRow)}
                    </div>

                    {!isSelected && (
                      <div className="mt-1.5 text-[10px] font-medium text-blue-400">view history →</div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        );
      })}

      {selected && (
        <div className="mt-2 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div className="flex items-center justify-between border-b border-slate-100 px-5 pb-4 pt-5">
            <div className="flex items-center gap-3">
              <div
                className="flex h-9 w-9 items-center justify-center rounded-xl text-sm font-bold text-white shadow-sm"
                style={{ background: METAL_COLORS[selected] || '#64748b' }}
              >
                {selected}
              </div>
              <div>
                <div className="text-sm font-bold text-slate-800">
                  {priceMap[selected]?.name || selected}
                </div>
                <div className="mt-0.5 flex items-center gap-2">
                  <span className="text-xs text-slate-400">Price history</span>
                  {pctChange != null && (
                    <span className={`rounded-full px-2 py-0.5 text-xs font-bold ${
                      isUp ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-600'
                    }`}>
                      {isUp ? '↑' : '↓'} {Math.abs(pctChange).toFixed(1)}%
                    </span>
                  )}
                </div>
              </div>
            </div>

            <div className="flex gap-0.5 rounded-xl bg-slate-100 p-1">
              {(Object.keys(PERIOD_LABELS) as Period[]).map((value) => (
                <button
                  key={value}
                  onClick={() => setPeriod(value)}
                  className={`rounded-lg px-2.5 py-1 text-xs font-semibold transition-all ${
                    period === value
                      ? 'bg-white text-slate-800 shadow'
                      : 'text-slate-500 hover:text-slate-700'
                  }`}
                >
                  {PERIOD_LABELS[value]}
                </button>
              ))}
            </div>
          </div>

          <div className="px-2 py-4">
            {histLoading ? (
              <div className="flex h-52 items-center justify-center gap-2 text-slate-400">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
                Loading...
              </div>
            ) : history.length === 0 ? (
              <div className="flex h-52 flex-col items-center justify-center gap-2 text-slate-400">
                <svg className="h-8 w-8 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="text-sm">No history data for {selected}</span>
                <span className="text-xs">This symbol has no stored trend series yet.</span>
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
                    tickFormatter={(dateValue) => {
                      const date = new Date(dateValue);
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
                    tickFormatter={(value) => `$${Number(value).toLocaleString()}`}
                    tick={{ fontSize: 11, fill: '#94a3b8' }}
                    width={72}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip
                    formatter={(value) => [`$${Number(value).toLocaleString()}`, priceMap[selected]?.unit || '']}
                    labelFormatter={(dateValue) => new Date(dateValue).toLocaleDateString('en', { year: 'numeric', month: 'long', day: 'numeric' })}
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

          {history.length > 0 && !histLoading && (
            <div className="flex flex-wrap gap-6 border-t border-slate-100 bg-slate-50 px-5 py-3">
              {[
                { label: 'Current', value: fmtPrice(history[history.length - 1].price), color: 'text-slate-800' },
                { label: 'Period High', value: fmtPrice(Math.max(...history.map((point) => point.high ?? point.price))), color: 'text-emerald-600' },
                { label: 'Period Low', value: fmtPrice(Math.min(...history.map((point) => point.low ?? point.price))), color: 'text-red-500' },
              ].map((stat) => (
                <div key={stat.label} className="flex items-center gap-2 text-sm">
                  <span className="text-slate-400">{stat.label}</span>
                  <span className={`font-bold ${stat.color}`}>{stat.value}</span>
                </div>
              ))}
              <div className="ml-auto self-center text-xs text-slate-400">
                {(historySource || 'Stored series')} · {history.length} pts
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
