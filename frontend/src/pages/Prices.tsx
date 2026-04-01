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
import { apiUrl, fetchPrices, type MetalPrice } from '../lib/api';

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
const GROUPS: Record<string, { title: string; symbols: string[] }> = {
  PGM: { title: 'Platinum Group Metals', symbols: ['Pt', 'Pd', 'Rh', 'Ru', 'Ir'] },
  Precious: { title: 'Precious Metals', symbols: ['Au', 'Ag'] },
  Base: { title: 'Industrial Metals', symbols: ['Ni', 'Co', 'Cu', 'Al', 'Mo', 'W', 'Fe'] },
};

const METAL_COLORS: Record<string, string> = {
  Pt: '#78f2d0',
  Pd: '#88a8ff',
  Rh: '#c5b7ff',
  Ru: '#8de0ff',
  Ir: '#9df8e3',
  Au: '#efc36c',
  Ag: '#d7dcee',
  Ni: '#53d4b5',
  Co: '#71b8ff',
  Cu: '#f3a08d',
  Al: '#9bb8ff',
  Mo: '#d8d3cf',
  W: '#aba39a',
  Fe: '#ff908d',
};

function fmtPrice(price: number | null) {
  if (price == null) return 'N/A';
  if (price >= 1000) return `$${price.toLocaleString('en-US', { maximumFractionDigits: 0 })}`;
  if (price >= 100) return `$${price.toLocaleString('en-US', { maximumFractionDigits: 1 })}`;
  return `$${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 4 })}`;
}

function sourceDescription(row: MetalPrice) {
  if (row.source_type === 'live') return row.source;
  if (row.source_type === 'indexed') return 'Indexed reference aligned with CatCost-style library pricing';
  return 'Manual price input';
}

function SourceBadge({ sourceType }: { sourceType: MetalPrice['source_type'] }) {
  const badge =
    sourceType === 'live'
      ? { label: 'Live', classes: 'border-emerald-200 bg-emerald-50 text-emerald-700', dot: 'bg-emerald-500' }
      : sourceType === 'indexed'
        ? { label: 'Indexed', classes: 'border-amber-200 bg-amber-50 text-amber-700', dot: 'bg-amber-500' }
        : { label: 'Manual', classes: 'border-slate-200 bg-white text-slate-600', dot: 'bg-slate-500' };

  return (
    <span className={`inline-flex items-center gap-2 rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.18em] ${badge.classes}`}>
      <span className={`h-2 w-2 rounded-full ${badge.dot}`} />
      {badge.label}
    </span>
  );
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

  const load = () => {
    setLoading(true);
    fetchPrices()
      .then((data) => {
        const rows = data as (MetalPrice & { is_live?: boolean })[];
        setPrices(rows);
        if (!selected && rows.length > 0) setSelected(rows[0].symbol);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  useEffect(() => {
    if (!selected) return;

    setHistLoading(true);
    fetch(apiUrl(`/prices/${selected}/history?period=${period}`))
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
      await fetch(apiUrl('/prices/refresh'), { method: 'POST' });
      load();
    } finally {
      setRefreshing(false);
    }
  };

  const priceMap = Object.fromEntries(prices.map((row) => [row.symbol, row]));
  const selectedRow = selected ? priceMap[selected] : null;
  const pctChange = history.length >= 2 ? ((history[history.length - 1].price - history[0].price) / history[0].price) * 100 : null;
  const isUp = pctChange != null && pctChange >= 0;

  if (loading) {
    return (
      <div className="surface-card flex items-center gap-3 px-5 py-6 text-slate-600">
        <span className="h-4 w-4 animate-spin rounded-full border-2 border-[#78f2d0] border-t-transparent" />
        Loading market board...
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-4 xl:grid-cols-[minmax(0,0.94fr)_minmax(0,1.06fr)]">
        <section className="surface-card cp-enter overflow-hidden px-5 py-6 sm:px-6" style={{ animationDelay: '0.06s' }}>
          <div className="mb-5 flex flex-col gap-4 border-b border-slate-900/8 pb-5 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <div className="cp-subtle-label">Quote Board</div>
              <h2 className="mt-2 text-2xl font-semibold text-slate-950">Metals reference board</h2>
              <p className="mt-2 max-w-2xl text-sm leading-7 text-slate-600">
                Grouped view for PGM, precious, and industrial metals with clear provenance for each live or indexed reference.
              </p>
            </div>

            <button onClick={handleRefresh} disabled={refreshing} className="cp-button-secondary">
              <span className={`mr-2 inline-flex h-4 w-4 rounded-full border-2 border-current border-t-transparent ${refreshing ? 'animate-spin' : ''}`} />
              {refreshing ? 'Refreshing feed' : 'Refresh quotes'}
            </button>
          </div>

          <div className="space-y-4">
            {GROUP_ORDER.map((groupKey) => {
              const group = GROUPS[groupKey];
              const rows = group.symbols.map((symbol) => priceMap[symbol]).filter(Boolean);
              if (!rows.length) return null;

              return (
                <div key={groupKey} className="surface-ghost overflow-hidden p-4">
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <div className="cp-subtle-label">{group.title}</div>
                    <span className="cp-chip">{rows.length} symbols</span>
                  </div>

                  <div className="divide-y divide-slate-900/8 overflow-hidden rounded-[24px] border border-slate-900/8 bg-white/56">
                    {rows.map((row) => {
                      const active = selected === row.symbol;
                      return (
                        <button
                          key={row.symbol}
                          onClick={() => setSelected(row.symbol)}
                          className={`grid w-full gap-3 px-4 py-3 text-left transition sm:grid-cols-[minmax(0,1fr)_auto_auto] sm:items-center ${
                            active ? 'bg-emerald-50/75' : 'bg-transparent hover:bg-white/80'
                          }`}
                        >
                          <div className="flex min-w-0 items-center gap-3">
                            <span
                              className="flex h-10 w-10 items-center justify-center rounded-[18px] text-sm font-semibold text-slate-950"
                              style={{ backgroundColor: METAL_COLORS[row.symbol] || '#78f2d0' }}
                            >
                              {row.symbol}
                            </span>
                            <div className="min-w-0">
                              <div className="truncate font-semibold text-slate-950">{row.name}</div>
                              <div className="truncate text-xs text-slate-500">{sourceDescription(row)}</div>
                            </div>
                          </div>

                          <SourceBadge sourceType={row.source_type} />

                          <div className="text-left sm:text-right">
                            <div className="text-lg font-display text-slate-950">{fmtPrice(row.price)}</div>
                            <div className="text-xs text-slate-500">{row.unit}</div>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        <section className="surface-card cp-enter overflow-hidden px-5 py-6 sm:px-6" style={{ animationDelay: '0.1s' }}>
          <div className="surface-ink overflow-hidden p-5">
            <div className="flex flex-col gap-4 border-b border-white/10 pb-5 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <div className="cp-subtle-label !text-slate-400">Selected Trend</div>
                <h2 className="mt-2 text-2xl font-semibold text-white">{selectedRow?.name ?? 'Choose a metal'}</h2>
                <div className="mt-2 flex flex-wrap items-center gap-2">
                  {selectedRow ? <SourceBadge sourceType={selectedRow.source_type} /> : null}
                  {pctChange != null ? (
                    <span
                      className={`rounded-full border px-3 py-1 text-xs font-semibold ${
                        isUp ? 'border-emerald-300/30 bg-emerald-400/10 text-emerald-100' : 'border-rose-300/30 bg-rose-400/10 text-rose-100'
                      }`}
                    >
                      {isUp ? '+' : '-'}
                      {Math.abs(pctChange).toFixed(1)}%
                    </span>
                  ) : null}
                </div>
              </div>

              <div className="flex gap-2 rounded-[18px] border border-white/10 bg-white/6 p-1">
                {(Object.keys(PERIOD_LABELS) as Period[]).map((value) => (
                  <button
                    key={value}
                    onClick={() => setPeriod(value)}
                    className={`rounded-[16px] px-3 py-2 text-xs font-semibold transition ${
                      period === value ? 'bg-[#78f2d0] text-slate-950' : 'text-slate-300 hover:bg-white/8'
                    }`}
                  >
                    {PERIOD_LABELS[value]}
                  </button>
                ))}
              </div>
            </div>

            <div className="mt-5">
              {histLoading ? (
                <div className="flex h-[320px] items-center justify-center gap-3 text-slate-300">
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-[#78f2d0] border-t-transparent" />
                  Loading history...
                </div>
              ) : history.length === 0 ? (
                <div className="flex h-[320px] flex-col items-center justify-center gap-2 rounded-[28px] border border-dashed border-white/10 bg-white/4 text-center">
                  <div className="font-display text-2xl text-white">No stored price history</div>
                  <div className="max-w-md text-sm leading-7 text-slate-400">
                    Select a symbol with available history or refresh the feed once the backend has stored trend data
                    for this metal.
                  </div>
                </div>
              ) : (
                <>
                  <div className="h-[320px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={history} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
                        <defs>
                          <linearGradient id="priceFill" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={METAL_COLORS[selected || 'Pt'] || '#78f2d0'} stopOpacity={0.3} />
                            <stop offset="95%" stopColor={METAL_COLORS[selected || 'Pt'] || '#78f2d0'} stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid stroke="rgba(255,255,255,0.08)" vertical={false} />
                        <XAxis
                          dataKey="date"
                          tick={{ fill: '#94a3b8', fontSize: 11 }}
                          axisLine={false}
                          tickLine={false}
                          tickFormatter={(value) =>
                            new Date(value).toLocaleDateString(
                              'en-US',
                              period === '1mo' ? { month: 'short', day: 'numeric' } : { year: '2-digit', month: 'short' },
                            )
                          }
                        />
                        <YAxis
                          tick={{ fill: '#94a3b8', fontSize: 11 }}
                          axisLine={false}
                          tickLine={false}
                          tickFormatter={(value) => `$${Number(value).toLocaleString('en-US')}`}
                          width={72}
                        />
                        <Tooltip
                          formatter={(value) => [`$${Number(value).toLocaleString('en-US')}`, selectedRow?.unit ?? '']}
                          labelFormatter={(value) =>
                            new Date(value).toLocaleDateString('en-US', {
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric',
                            })
                          }
                          contentStyle={{
                            borderRadius: 18,
                            border: '1px solid rgba(255,255,255,0.10)',
                            background: '#0b1522',
                            color: '#e2e8f0',
                            fontSize: 12,
                          }}
                        />
                        {history.length > 0 ? <ReferenceLine y={history[0].price} stroke="rgba(255,255,255,0.12)" strokeDasharray="4 4" /> : null}
                        <Area
                          type="monotone"
                          dataKey="price"
                          stroke={METAL_COLORS[selected || 'Pt'] || '#78f2d0'}
                          strokeWidth={2.2}
                          fill="url(#priceFill)"
                          dot={false}
                          activeDot={{ r: 4 }}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="mt-5 grid gap-3 sm:grid-cols-3">
                    <div className="cp-metric-tile-dark">
                      <div className="cp-subtle-label !text-slate-400">Current</div>
                      <div className="mt-2 text-xl font-display text-white">{fmtPrice(history[history.length - 1].price)}</div>
                      <div className="mt-1 text-xs leading-5 text-slate-400">{selectedRow?.unit ?? ''}</div>
                    </div>
                    <div className="cp-metric-tile-dark">
                      <div className="cp-subtle-label !text-slate-400">Period high</div>
                      <div className="mt-2 text-xl font-display text-white">
                        {fmtPrice(Math.max(...history.map((point) => point.high ?? point.price)))}
                      </div>
                      <div className="mt-1 text-xs leading-5 text-slate-400">Maximum observed value</div>
                    </div>
                    <div className="cp-metric-tile-dark">
                      <div className="cp-subtle-label !text-slate-400">Period low</div>
                      <div className="mt-2 text-xl font-display text-white">
                        {fmtPrice(Math.min(...history.map((point) => point.low ?? point.price)))}
                      </div>
                      <div className="mt-1 text-xs leading-5 text-slate-400">{historySource || 'Stored metal price series'}</div>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
