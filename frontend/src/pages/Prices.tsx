import { lazy, Suspense, useCallback, useEffect, useState } from 'react';
import { SkeletonListRows, SkeletonTile } from '../components/shared/Skeleton';
import { WorkspaceSectionFooter, WorkspaceSectionNav, useWorkspaceSections, type WorkspaceSection } from '../components/shared/WorkspaceSections';
import { fetchPriceHistory, fetchPrices, refreshPrices, type MetalPrice } from '../lib/api';
import { LB_PER_KG, TROY_OZ_PER_KG, TROY_OZ_PER_LB, type Unit } from '../lib/unit-conversion';
import { useUnit } from '../lib/use-unit';

const MetalTrendChart = lazy(() => import('../components/charts/MetalTrendChart'));

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
  Pt: '#c96442',
  Pd: '#7c8db5',
  Rh: '#a48bc8',
  Ru: '#b8825d',
  Ir: '#c9a96a',
  Au: '#d4a857',
  Ag: '#9ba6b8',
  Ni: '#7a9b8d',
  Co: '#6b85a8',
  Cu: '#b56e52',
  Al: '#a8b0bd',
  Mo: '#9b8c7a',
  W: '#7d756c',
  Fe: '#a85a4c',
};

const FEED_SECTIONS: WorkspaceSection[] = [
  { id: 'quotes', label: 'Prices', summary: 'Choose the metal price to inspect.' },
  { id: 'history', label: 'History', summary: 'Read source quality, freshness, and trend.' },
];

function convertTrackedPrice(price: number, rawUnit: string, displayUnit: Unit) {
  if (rawUnit === '$/lb') return displayUnit === 'kg' ? price * LB_PER_KG : price;
  if (rawUnit === '$/kg') return displayUnit === 'lb' ? price / LB_PER_KG : price;
  if (rawUnit === '$/troy_oz') return displayUnit === 'kg' ? price * TROY_OZ_PER_KG : price * TROY_OZ_PER_LB;
  return price;
}

function displayTrackedUnit(rawUnit: string, displayUnit: Unit) {
  if (rawUnit === '$/lb' || rawUnit === '$/kg' || rawUnit === '$/troy_oz') return `$/${displayUnit}`;
  return rawUnit;
}

function formatSyncStamp(value: string | null) {
  if (!value) return 'Awaiting live refresh';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Awaiting live refresh';

  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
}

function fmtPrice(price: number | null, rawUnit: string, displayUnit: Unit) {
  if (price == null) return 'N/A';
  const converted = convertTrackedPrice(price, rawUnit, displayUnit);
  if (converted >= 1000) return `$${converted.toLocaleString('en-US', { maximumFractionDigits: 0 })}`;
  if (converted >= 100) return `$${converted.toLocaleString('en-US', { maximumFractionDigits: 1 })}`;
  return `$${converted.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 4 })}`;
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

function StatusTile({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="rounded-[22px] border border-slate-900/8 bg-white/58 p-4">
      <div className="cp-subtle-label">{label}</div>
      <div className="mt-2 text-2xl font-display text-[#1a1612]">{value}</div>
      <div className="mt-1 text-xs leading-5 text-slate-500">{detail}</div>
    </div>
  );
}

function InspectorRow({ label, value, detail }: { label: string; value: string; detail?: string }) {
  return (
    <div className="cp-data-row">
      <div>
        <div className="cp-subtle-label">{label}</div>
        {detail ? <div className="mt-1 text-xs leading-5 text-slate-500">{detail}</div> : null}
      </div>
      <div className="text-right text-sm font-semibold text-[#1a1612]">{value}</div>
    </div>
  );
}

function DarkChartFallback({ label }: { label: string }) {
  return (
    <div className="flex h-full min-h-[320px] flex-col items-center justify-center gap-3 rounded-[28px] border border-white/10 bg-white/4 text-center">
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-[#c96442] border-t-transparent" />
      <div className="text-sm text-slate-300">{label}</div>
    </div>
  );
}

export default function Prices() {
  const { unit } = useUnit();
  const {
    activeSection,
    activeSectionId,
    activeIndex,
    canGoNext,
    canGoPrevious,
    goNext,
    goPrevious,
    setActiveSection,
  } = useWorkspaceSections(FEED_SECTIONS, 'feed');
  const [prices, setPrices] = useState<MetalPrice[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryPoint[]>([]);
  const [historySource, setHistorySource] = useState<string | null>(null);
  const [histLoading, setHistLoading] = useState(false);
  const [period, setPeriod] = useState<Period>('1y');

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    fetchPrices()
      .then((rows) => {
        setPrices(rows);
        setSelected((current) => current ?? rows[0]?.symbol ?? null);
      })
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : 'Failed to load metal prices');
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(load, [load]);

  useEffect(() => {
    if (!selected) return;

    let cancelled = false;
    setHistLoading(true);
    fetchPriceHistory(selected, { period })
      .then((payload) => {
        if (cancelled) return;
        setHistory(payload.history ?? []);
        setHistorySource(payload.source ?? null);
      })
      .catch(() => {
        if (cancelled) return;
        setHistory([]);
        setHistorySource(null);
      })
      .finally(() => {
        if (!cancelled) setHistLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [selected, period]);

  const handleRefresh = async () => {
    setRefreshing(true);
    setError(null);

    try {
      await refreshPrices();
      load();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to refresh metal prices');
    } finally {
      setRefreshing(false);
    }
  };

  const priceMap = Object.fromEntries(prices.map((row) => [row.symbol, row]));
  const selectedRow = selected ? priceMap[selected] : null;
  const displayHistory = selectedRow
    ? history.map((point) => ({
        ...point,
        price: convertTrackedPrice(point.price, selectedRow.unit, unit),
        open: convertTrackedPrice(point.open, selectedRow.unit, unit),
        high: convertTrackedPrice(point.high, selectedRow.unit, unit),
        low: convertTrackedPrice(point.low, selectedRow.unit, unit),
      }))
    : history;
  const selectedDisplayUnit = selectedRow ? displayTrackedUnit(selectedRow.unit, unit) : '';
  const pctChange =
    history.length >= 2 && history[0].price !== 0
      ? ((history[history.length - 1].price - history[0].price) / history[0].price) * 100
      : null;
  const isUp = pctChange != null && pctChange >= 0;
  const latestFetchedAt = prices.reduce<string | null>((latest, row) => {
    if (!row.fetched_at) return latest;
    const time = new Date(row.fetched_at).getTime();
    if (Number.isNaN(time)) return latest;
    if (latest == null) return row.fetched_at;
    return time > new Date(latest).getTime() ? row.fetched_at : latest;
  }, null);
  const liveQuoteCount = prices.filter((row) => row.source_type === 'live').length;
  const indexedQuoteCount = prices.filter((row) => row.source_type === 'indexed').length;
  const manualQuoteCount = prices.filter((row) => row.source_type === 'manual').length;
  const reviewFlagCount = prices.filter(
    (row) => row.evidence.freshness_status.toLowerCase() !== 'fresh' || row.evidence.confidence_score < 75,
  ).length;

  if (loading) {
    return (
      <section className="surface-card cp-enter overflow-hidden px-5 py-6 sm:px-6">
        <div className="mb-5 flex flex-col gap-2">
          <div className="cp-subtle-label">Live Metal Prices</div>
          <div className="h-9 w-2/3 max-w-md rounded-[10px] bg-[rgba(232,220,200,0.55)] cp-skeleton" />
          <div className="h-3 w-3/4 max-w-xl rounded-[8px] bg-[rgba(232,220,200,0.45)] cp-skeleton" />
        </div>
        <div className="mb-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 4 }, (_, idx) => (
            <SkeletonTile key={idx} />
          ))}
        </div>
        <div className="space-y-4">
          {['Platinum Group Metals', 'Precious Metals', 'Industrial Metals'].map((title, idx) => (
            <div key={title} className="surface-ghost overflow-hidden p-4">
              <div className="mb-3 flex items-center justify-between gap-3">
                <div className="cp-subtle-label">{title}</div>
                <span className="cp-chip">Loading…</span>
              </div>
              <SkeletonListRows count={idx === 2 ? 5 : 3} />
            </div>
          ))}
        </div>
      </section>
    );
  }

  function renderQuotesInspector() {
    if (!selectedRow) {
      return (
        <div className="cp-inspector-rail">
          <section className="cp-rail-panel">
            <div className="cp-subtle-label">Evidence Surface</div>
            <div className="mt-2 text-lg font-semibold text-[#1a1612]">Choose a tracked symbol.</div>
            <div className="mt-2 text-xs leading-6 text-slate-500">The inspector keeps source quality, freshness, and normalization context visible.</div>
          </section>
        </div>
      );
    }

    return (
      <div className="cp-inspector-rail">
        <section className="surface-ink overflow-hidden p-4">
          <div className="cp-subtle-label !text-slate-400">Selected Quote</div>
          <div className="mt-2 text-sm text-slate-300">{selectedRow.name}</div>
          <div className="mt-3 flex items-end gap-3">
            <div className="font-display text-[clamp(2.2rem,4vw,3.7rem)] leading-none text-white">
              {fmtPrice(selectedRow.price, selectedRow.unit, unit)}
            </div>
            <div className="pb-1 text-sm text-slate-300">{displayTrackedUnit(selectedRow.unit, unit)}</div>
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            <SourceBadge sourceType={selectedRow.source_type} />
            <span className="cp-chip-dark">{selectedRow.evidence.label}</span>
          </div>
          <button onClick={() => setActiveSection('history')} className="cp-button-ink mt-4 px-3 py-2 text-xs">
            Open trend view
          </button>
        </section>

        <section className="cp-rail-panel">
          <div className="cp-subtle-label">Source Basis</div>
          <div className="mt-2 text-lg font-semibold text-[#1a1612]">Inspect trust before you read the number.</div>
          <div className="mt-3 space-y-1">
            <InspectorRow label="Acquisition" value={selectedRow.evidence.acquisition_mode} detail={sourceDescription(selectedRow)} />
            <InspectorRow label="Confidence" value={String(selectedRow.evidence.confidence_score)} detail={selectedRow.evidence.transparency} />
            <InspectorRow label="Freshness" value={selectedRow.evidence.freshness_status} detail={selectedRow.evidence.note} />
            <InspectorRow label="Target window" value={selectedRow.evidence.freshness_target_hours != null ? `${selectedRow.evidence.freshness_target_hours} h` : 'N/A'} detail="Expected refresh horizon for this source type." />
          </div>
        </section>

        <section className="cp-rail-panel">
          <div className="cp-subtle-label">Feed Coverage</div>
          <div className="mt-3 grid gap-2 sm:grid-cols-2 xl:grid-cols-1">
            <StatusTile label="Tracked symbols" value={String(prices.length)} detail="Metals visible in the desktop feed." />
            <StatusTile label="Needs review" value={String(reviewFlagCount)} detail="Freshness or confidence flags worth checking." />
          </div>
        </section>
      </div>
    );
  }

  function renderQuotes() {
    return (
      <div className="cp-split-workspace">
        <section className="surface-card cp-enter overflow-hidden px-5 py-6 sm:px-6" style={{ animationDelay: '0.06s' }}>
          <div className="mb-5 flex flex-col gap-4 border-b border-slate-900/8 pb-5 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <div className="cp-subtle-label">Live Metal Prices</div>
              <h2 className="cp-heading-xl mt-2">Monitor live and indexed metal price basis.</h2>
              <p className="cp-body-copy mt-2 max-w-2xl">
                Scan the tracked symbols first, then inspect evidence, freshness, and source quality for the selected metal.
              </p>
            </div>

            <div className="flex min-w-[280px] flex-col gap-2 rounded-[22px] border border-slate-200 bg-white/76 px-4 py-3 sm:items-end">
              <div className="cp-subtle-label">Quote Status</div>
              <div className="text-right">
                <div className="text-sm font-semibold text-[#1a1612]">
                  {refreshing ? 'Refreshing live quotes' : latestFetchedAt ? 'Live quotes loaded' : 'Stored pricing basis'}
                </div>
                <div className="mt-1 text-xs leading-5 text-slate-500">
                  {latestFetchedAt
                    ? `${liveQuoteCount} live symbols synced ${formatSyncStamp(latestFetchedAt)}`
                    : 'Indexed and manual prices are available even before a live refresh.'}
                </div>
              </div>
              <button onClick={handleRefresh} disabled={refreshing} className="cp-button-secondary px-4 py-2.5 text-sm">
                <span className={`mr-2 inline-flex h-4 w-4 rounded-full border-2 border-current border-t-transparent ${refreshing ? 'animate-spin' : ''}`} />
                {refreshing ? 'Refreshing now' : 'Refresh quotes'}
              </button>
            </div>
          </div>

          {error ? (
            <div className="mb-4 rounded-[18px] border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700" role="alert">
              {error}
            </div>
          ) : null}

          <div className="mb-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <StatusTile label="Tracked symbols" value={String(prices.length)} detail="Metals visible in the desktop feed." />
            <StatusTile label="Live coverage" value={`${liveQuoteCount}/${prices.length}`} detail="Symbols backed by current live sources." />
            <StatusTile label="Fallback rows" value={String(indexedQuoteCount + manualQuoteCount)} detail={`${indexedQuoteCount} indexed and ${manualQuoteCount} manual rows remain usable.`} />
            <StatusTile label="Needs review" value={String(reviewFlagCount)} detail="Freshness or confidence flags worth checking." />
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

                  <div className="space-y-2">
                    {rows.map((row) => {
                      const active = selected === row.symbol;
                      return (
                        <button
                          key={row.symbol}
                          onClick={() => {
                            setSelected(row.symbol);
                          }}
                          className={`grid w-full gap-3 px-4 py-3 text-left transition sm:grid-cols-[minmax(0,1fr)_auto_auto] sm:items-center ${active ? 'cp-list-row cp-list-row-active' : 'cp-list-row'}`}
                        >
                          <div className="flex min-w-0 items-center gap-3">
                            <span
                              className="flex h-10 w-10 items-center justify-center rounded-[18px] text-sm font-semibold text-[#1a1612]"
                              style={{ backgroundColor: METAL_COLORS[row.symbol] || '#c96442' }}
                            >
                              {row.symbol}
                            </span>
                            <div className="min-w-0">
                              <div className="truncate font-semibold text-[#1a1612]">{row.name}</div>
                              <div className="truncate text-xs text-slate-500">
                                {sourceDescription(row)} / {row.evidence.label}
                              </div>
                            </div>
                          </div>

                          <SourceBadge sourceType={row.source_type} />

                          <div className="text-left sm:text-right">
                            <div className="text-lg font-display text-[#1a1612]">{fmtPrice(row.price, row.unit, unit)}</div>
                            <div className="text-xs text-slate-500">{displayTrackedUnit(row.unit, unit)}</div>
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
        <div>{renderQuotesInspector()}</div>
      </div>
    );
  }

  function renderHistoryRail() {
    if (!selectedRow) {
      return (
        <div className="cp-inspector-rail">
          <section className="cp-rail-panel">
            <div className="cp-subtle-label">Evidence Surface</div>
            <div className="mt-2 text-lg font-semibold text-[#1a1612]">Choose a symbol to inspect its history.</div>
          </section>
        </div>
      );
    }

    const currentValue = displayHistory.length > 0 ? displayHistory[displayHistory.length - 1].price : null;
    const periodHigh = displayHistory.length > 0 ? Math.max(...displayHistory.map((point) => point.high ?? point.price)) : null;
    const periodLow = displayHistory.length > 0 ? Math.min(...displayHistory.map((point) => point.low ?? point.price)) : null;

    return (
      <div className="cp-inspector-rail">
        <section className="cp-rail-panel">
          <div className="cp-subtle-label">Trend Evidence</div>
          <div className="mt-2 text-lg font-semibold text-[#1a1612]">{selectedRow.name}</div>
          <div className="mt-3 space-y-1">
            <InspectorRow label="Current" value={currentValue != null ? fmtPrice(currentValue, selectedRow.unit, unit) : 'N/A'} detail={displayTrackedUnit(selectedRow.unit, unit)} />
            <InspectorRow label="Period high" value={periodHigh != null ? fmtPrice(periodHigh, selectedRow.unit, unit) : 'N/A'} />
            <InspectorRow label="Period low" value={periodLow != null ? fmtPrice(periodLow, selectedRow.unit, unit) : 'N/A'} detail={historySource || 'Stored metal price series'} />
            <InspectorRow label="Direction" value={pctChange != null ? `${pctChange >= 0 ? '+' : ''}${pctChange.toFixed(1)}%` : 'N/A'} detail={`${PERIOD_LABELS[period]} window`} />
          </div>
        </section>

        <section className="cp-rail-panel">
          <div className="cp-subtle-label">Source Audit</div>
          <div className="mt-3 space-y-1">
            <InspectorRow label="Evidence tier" value={selectedRow.evidence.label} detail={selectedRow.evidence.note} />
            <InspectorRow label="Transparency" value={selectedRow.evidence.transparency} detail={selectedRow.evidence.acquisition_mode} />
            <InspectorRow label="Freshness" value={selectedRow.evidence.freshness_status} detail={selectedRow.evidence.age_hours != null ? `${selectedRow.evidence.age_hours.toFixed(1)} h old` : 'Age not stored'} />
          </div>
        </section>
      </div>
    );
  }

  function renderTrend() {
    return (
      <div className="cp-split-workspace">
        <section className="surface-card cp-enter overflow-hidden px-5 py-6 sm:px-6" style={{ animationDelay: '0.1s' }}>
          <div className="surface-ink overflow-hidden p-5">
          <div className="flex flex-col gap-4 border-b border-white/10 pb-5 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <div className="cp-subtle-label !text-slate-400">Selected Metal</div>
              <h2 className="font-display mt-2 text-[clamp(1.75rem,2.4vw,2.35rem)] leading-[1.0] text-white">{selectedRow?.name ?? 'Choose a metal'}</h2>
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
                    period === value ? 'bg-[#c96442] text-[#1a1612]' : 'text-slate-300 hover:bg-white/8'
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
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-[#c96442] border-t-transparent" />
                Loading history...
              </div>
            ) : displayHistory.length === 0 ? (
              <div className="flex h-[320px] flex-col items-center justify-center gap-3 rounded-[28px] border border-dashed border-white/10 bg-white/4 text-center">
                <div className="font-display text-2xl text-white">No stored price history</div>
                <div className="max-w-md text-sm leading-7 text-slate-400">
                  Refresh quotes or choose a symbol that already has stored history.
                </div>
                <button
                  type="button"
                  onClick={handleRefresh}
                  disabled={refreshing}
                  className="cp-button-ink mt-2 px-4 py-2 text-xs"
                >
                  {refreshing ? 'Refreshing now…' : 'Refresh quotes'}
                </button>
              </div>
            ) : (
              <>
                <div className="h-[320px]">
                  <Suspense fallback={<DarkChartFallback label="Loading trend chart..." />}>
                    <MetalTrendChart
                      data={displayHistory}
                      period={period}
                      selectedDisplayUnit={selectedDisplayUnit}
                      selectedColor={METAL_COLORS[selected || 'Pt'] || '#c96442'}
                    />
                  </Suspense>
                </div>

                <div className="mt-5 grid gap-3 sm:grid-cols-3">
                  <div className="cp-metric-tile-dark">
                    <div className="cp-subtle-label !text-slate-400">Current</div>
                    <div className="mt-2 text-xl font-display text-white">{fmtPrice(displayHistory[displayHistory.length - 1].price, selectedRow?.unit ?? '$/lb', unit)}</div>
                    <div className="mt-1 text-xs leading-5 text-slate-400">{selectedDisplayUnit}</div>
                  </div>
                  <div className="cp-metric-tile-dark">
                    <div className="cp-subtle-label !text-slate-400">Period high</div>
                    <div className="mt-2 text-xl font-display text-white">
                      {fmtPrice(Math.max(...displayHistory.map((point) => point.high ?? point.price)), selectedRow?.unit ?? '$/lb', unit)}
                    </div>
                    <div className="mt-1 text-xs leading-5 text-slate-400">Maximum observed value</div>
                  </div>
                  <div className="cp-metric-tile-dark">
                    <div className="cp-subtle-label !text-slate-400">Period low</div>
                    <div className="mt-2 text-xl font-display text-white">
                      {fmtPrice(Math.min(...displayHistory.map((point) => point.low ?? point.price)), selectedRow?.unit ?? '$/lb', unit)}
                    </div>
                    <div className="mt-1 text-xs leading-5 text-slate-400">{historySource || 'Stored metal price series'}</div>
                  </div>
                </div>

                {selectedRow ? (
                  <div className="mt-4 grid gap-3 sm:grid-cols-3">
                    <div className="rounded-[22px] border border-white/10 bg-white/6 p-3">
                      <div className="cp-subtle-label !text-slate-400">Evidence tier</div>
                      <div className="mt-2 text-sm font-semibold text-white">{selectedRow.evidence.label}</div>
                      <div className="mt-1 text-xs leading-5 text-slate-400">{selectedRow.evidence.note}</div>
                    </div>
                    <div className="rounded-[22px] border border-white/10 bg-white/6 p-3">
                      <div className="cp-subtle-label !text-slate-400">Confidence</div>
                      <div className="mt-2 text-sm font-semibold text-white">{selectedRow.evidence.confidence_score}</div>
                      <div className="mt-1 text-xs leading-5 text-slate-400">{selectedRow.evidence.transparency}</div>
                    </div>
                    <div className="rounded-[22px] border border-white/10 bg-white/6 p-3">
                      <div className="cp-subtle-label !text-slate-400">Freshness</div>
                      <div className="mt-2 text-sm font-semibold text-white">{selectedRow.evidence.freshness_status}</div>
                      <div className="mt-1 text-xs leading-5 text-slate-400">{selectedRow.evidence.acquisition_mode}</div>
                    </div>
                  </div>
                ) : null}
              </>
            )}
          </div>
          </div>
        </section>
        <div>{renderHistoryRail()}</div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <WorkspaceSectionNav
        sections={FEED_SECTIONS}
        activeSectionId={activeSectionId}
        activeIndex={activeIndex}
        onSelect={setActiveSection}
      />
      {activeSection.id === 'quotes' ? renderQuotes() : activeSection.id === 'history' ? renderTrend() : null}
      <WorkspaceSectionFooter
        activeSection={activeSection}
        activeIndex={activeIndex}
        totalSections={FEED_SECTIONS.length}
        onPrevious={goPrevious}
        onNext={goNext}
        canGoPrevious={canGoPrevious}
        canGoNext={canGoNext}
      />
    </div>
  );
}
