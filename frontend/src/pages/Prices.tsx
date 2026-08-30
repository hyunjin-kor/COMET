import { lazy, Suspense, useCallback, useEffect, useState } from 'react';
import { FitPriceText } from '../components/shared/FitPriceText';
import { SkeletonListRows, SkeletonTile } from '../components/shared/Skeleton';
import { WorkspaceSectionFooter, WorkspaceSectionNav, useWorkspaceSections, type WorkspaceSection } from '../components/shared/WorkspaceSections';
import { fetchPriceHistory, fetchPrices, refreshPrices, type MetalPrice } from '../lib/api';
import { LB_PER_KG, TROY_OZ_PER_KG, TROY_OZ_PER_LB, type Unit } from '../lib/unit-conversion';
import { useLang } from '../lib/i18n';
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

// Data palette: brand teal for Pt, then visually distinct hues so PGM
// trend lines and avatars stay tellable apart.
const METAL_COLORS: Record<string, string> = {
  Pt: '#0d9488',
  Pd: '#0067ff',
  Rh: '#d6409f',
  Ru: '#e8590c',
  Ir: '#7da7ff',
  Au: '#ffa800',
  Ag: '#8b95a1',
  Ni: '#22c55e',
  Co: '#0099ff',
  Cu: '#f04452',
  Al: '#b0b8c1',
  Mo: '#7950f2',
  W: '#4e5968',
  Fe: '#fb6f5f',
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

function fmtConverted(value: number | null) {
  if (value == null) return 'N/A';
  if (Math.abs(value) >= 1) return `$${value.toLocaleString('en-US', { maximumFractionDigits: 0 })}`;
  return `$${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 4 })}`;
}

function fmtPrice(price: number | null, rawUnit: string, displayUnit: Unit) {
  if (price == null) return 'N/A';
  return fmtConverted(convertTrackedPrice(price, rawUnit, displayUnit));
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
    <div className="cp-metric-tile">
      <div className="cp-subtle-label">{label}</div>
      <div className="mt-1.5 text-2xl font-display text-[#191f28]">{value}</div>
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
      <div className="text-right text-sm font-semibold text-[#191f28]">{value}</div>
    </div>
  );
}

function DarkChartFallback({ label }: { label: string }) {
  return (
    <div className="flex h-full min-h-[320px] flex-col items-center justify-center gap-3 rounded-[28px] border border-white/10 bg-white/4 text-center">
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-[#0d9488] border-t-transparent" />
      <div className="text-sm text-slate-300">{label}</div>
    </div>
  );
}

export default function Prices() {
  const { unit } = useUnit();
  const { lang, t } = useLang();
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

  const load = useCallback((options?: { silent?: boolean }) => {
    if (!options?.silent) setLoading(true);
    setError(null);
    fetchPrices()
      .then((rows) => {
        setPrices(rows);
        setSelected((current) => current ?? rows[0]?.symbol ?? null);
      })
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : 'Failed to load metal prices');
      })
      .finally(() => {
        if (!options?.silent) setLoading(false);
      });
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  // Two-tier live polling while the page is open, using only free sources:
  //   - every 60s: Yahoo Finance quotes (Pt, Pd, Au, Ag, Cu, Al)
  //   - every 5 min: full refresh — also pulls Kitco / Johnson Matthey /
  //     Markets Insider so Rh, Ru, Ir, Ni, Co, Mo, W, Fe stay current
  //     without any paid API. The slower cadence keeps the scrapers polite.
  useEffect(() => {
    const yahooTick = async () => {
      try {
        await refreshPrices('yahoo');
        load({ silent: true });
      } catch {
        // Transient network blips shouldn't disturb the displayed quotes.
      }
    };
    const fullTick = async () => {
      try {
        await refreshPrices();
        load({ silent: true });
      } catch {
        // Transient network blips shouldn't disturb the displayed quotes.
      }
    };
    const yahooId = window.setInterval(yahooTick, 60_000);
    const fullId = window.setInterval(fullTick, 5 * 60_000);
    return () => {
      window.clearInterval(yahooId);
      window.clearInterval(fullId);
    };
  }, [load]);

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
      // Re-fetch silently — keep the current quote list visible so the user
      // doesn't see the whole page collapse to a skeleton during refresh.
      // The refresh button itself stays in its own spinner state.
      load({ silent: true });
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
    history.length >= 2 && history[0]!.price !== 0
      ? ((history[history.length - 1]!.price - history[0]!.price) / history[0]!.price) * 100
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
    // Backend freshness vocabulary is current / stale / reference — "current"
    // is the healthy state; everything else deserves a look.
    (row) => row.evidence.freshness_status.toLowerCase() !== 'current' || row.evidence.confidence_score < 75,
  ).length;

  if (loading) {
    return (
      <section className="surface-card cp-enter overflow-hidden px-5 py-6 sm:px-6">
        <div className="mb-5 flex flex-col gap-2">
          <div className="cp-subtle-label">Live Metal Prices</div>
          <div className="h-9 w-2/3 max-w-md rounded-[10px] bg-[rgba(229,232,235,0.55)] cp-skeleton" />
          <div className="h-3 w-3/4 max-w-xl rounded-[8px] bg-[rgba(229,232,235,0.45)] cp-skeleton" />
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
            <div className="mt-2 text-lg font-semibold text-[#191f28]">Choose a tracked symbol.</div>
            <div className="mt-2 text-xs leading-6 text-slate-500">The inspector keeps source quality, freshness, and normalization context visible.</div>
          </section>
        </div>
      );
    }

    return (
      <div className="cp-inspector-rail">
        <section className="surface-ink overflow-hidden p-4">
          <div className="cp-subtle-label !text-slate-400">{t('Selected Quote')}</div>
          <div className="mt-2 text-sm text-slate-300">{t(selectedRow.name)}</div>
          <div className="mt-3 flex items-end gap-3">
            <FitPriceText
              size="lg"
              text={fmtPrice(selectedRow.price, selectedRow.unit, unit)}
              className="min-w-0 text-white"
            />
            <div className="pb-1 text-sm text-slate-300">{displayTrackedUnit(selectedRow.unit, unit)}</div>
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            <SourceBadge sourceType={selectedRow.source_type} />
            <span className="cp-chip-dark">{t(selectedRow.evidence.label)}</span>
          </div>
          <button onClick={() => setActiveSection('history')} className="cp-button-ink mt-4 px-3 py-2 text-xs">
            {t('Open trend view')}
          </button>
        </section>

        <section className="cp-rail-panel">
          <div className="cp-subtle-label">{t('Source Basis')}</div>
          <div className="mt-2 text-lg font-semibold text-[#191f28]">{t('Inspect trust before you read the number.')}</div>
          <div className="mt-3 space-y-1">
            <InspectorRow label={t('Acquisition')} value={selectedRow.evidence.acquisition_mode} detail={t(sourceDescription(selectedRow))} />
            <InspectorRow label={t('Confidence')} value={String(selectedRow.evidence.confidence_score)} detail={selectedRow.evidence.transparency} />
            <InspectorRow label={t('Quote age')} value={selectedRow.evidence.freshness_status} detail={selectedRow.evidence.note} />
            <InspectorRow label={t('Refresh target')} value={selectedRow.evidence.freshness_target_hours != null ? `${selectedRow.evidence.freshness_target_hours} h` : 'N/A'} detail={t('Expected refresh horizon for this source type.')} />
          </div>
        </section>

        <section className="cp-rail-panel">
          <div className="cp-subtle-label">{t('Price Coverage')}</div>
          <div className="mt-3 grid gap-2 sm:grid-cols-2 xl:grid-cols-1">
            <StatusTile label={t('Tracked metals')} value={String(prices.length)} detail={t('Metals with a stored price basis.')} />
            <StatusTile label={t('Needs review')} value={String(reviewFlagCount)} detail={t('Stale quotes or low-confidence sources worth checking.')} />
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
              <h2 className="cp-heading-xl">{t('Live Metal Prices')}</h2>
              <p className="cp-body-copy mt-1.5 max-w-2xl">
                {t('Scan the tracked metals, then inspect the evidence, quote age, and source quality for the selected metal.')}
              </p>
            </div>

            <div className="flex min-w-[280px] flex-col gap-2 rounded-[22px] border border-slate-200 bg-white/76 px-4 py-3 sm:items-end">
              <div className="cp-subtle-label">{t('Quote Status')}</div>
              <div className="text-right">
                <div className="text-sm font-semibold text-[#191f28]">
                  {refreshing ? t('Refreshing live quotes') : latestFetchedAt ? t('Live quotes loaded') : t('Stored pricing basis')}
                </div>
                <div className="mt-1 text-xs leading-5 text-slate-500">
                  {latestFetchedAt
                    ? (lang === 'ko' ? `금속 ${liveQuoteCount}종 실시간 갱신 ${formatSyncStamp(latestFetchedAt)}` : `${liveQuoteCount} metals updated live ${formatSyncStamp(latestFetchedAt)}`)
                    : t('Indexed and manual prices are available even before a live refresh.')}
                </div>
              </div>
              <button onClick={handleRefresh} disabled={refreshing} className="cp-button-secondary px-4 py-2.5 text-sm">
                <span className={`mr-2 inline-flex h-4 w-4 rounded-full border-2 border-current border-t-transparent ${refreshing ? 'animate-spin' : ''}`} />
                {refreshing ? t('Refreshing now') : t('Refresh quotes')}
              </button>
            </div>
          </div>

          {error ? (
            <div className="mb-4 rounded-[18px] border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700" role="alert">
              {error}
            </div>
          ) : null}

          <div className="mb-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <StatusTile label={t('Tracked metals')} value={String(prices.length)} detail={t('Metals with a stored price basis.')} />
            <StatusTile label={t('Live coverage')} value={`${liveQuoteCount}/${prices.length}`} detail={t('Metals backed by current live sources.')} />
            <StatusTile label={t('Indexed & manual quotes')} value={String(indexedQuoteCount + manualQuoteCount)} detail={lang === 'ko' ? `지수 ${indexedQuoteCount}건, 수동 ${manualQuoteCount}건 시세를 계속 사용할 수 있습니다.` : `${indexedQuoteCount} indexed and ${manualQuoteCount} manual quotes remain usable.`} />
            <StatusTile label={t('Needs review')} value={String(reviewFlagCount)} detail={t('Stale quotes or low-confidence sources worth checking.')} />
          </div>

          <div className="space-y-4">
            {GROUP_ORDER.map((groupKey) => {
              const group = GROUPS[groupKey];
              if (!group) return null;
              const rows = group.symbols
                .map((symbol) => priceMap[symbol])
                .filter((row): row is MetalPrice => row !== undefined);
              if (!rows.length) return null;

              return (
                <div key={groupKey} className="surface-ghost overflow-hidden p-4">
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <div className="cp-subtle-label">{t(group.title)}</div>
                    <span className="cp-chip">{lang === 'ko' ? `${rows.length}종` : `${rows.length} metals`}</span>
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
                              className="flex h-10 w-10 items-center justify-center rounded-[18px] text-sm font-semibold text-[#191f28]"
                              style={{ backgroundColor: METAL_COLORS[row.symbol] || '#0d9488' }}
                            >
                              {row.symbol}
                            </span>
                            <div className="min-w-0">
                              <div className="truncate font-semibold text-[#191f28]">{t(row.name)}</div>
                              <div className="truncate text-xs text-slate-500">
                                {t(sourceDescription(row))} / {t(row.evidence.label)}
                              </div>
                            </div>
                          </div>

                          <SourceBadge sourceType={row.source_type} />

                          <div className="text-left sm:text-right">
                            <div className="text-lg font-display text-[#191f28]">{fmtPrice(row.price, row.unit, unit)}</div>
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
            <div className="cp-subtle-label">{t('Evidence Surface')}</div>
            <div className="mt-2 text-lg font-semibold text-[#191f28]">{t('Choose a metal to inspect its history.')}</div>
          </section>
        </div>
      );
    }

    const currentValue = displayHistory.length > 0 ? displayHistory[displayHistory.length - 1]!.price : null;
    const periodHigh = displayHistory.length > 0 ? Math.max(...displayHistory.map((point) => point.high ?? point.price)) : null;
    const periodLow = displayHistory.length > 0 ? Math.min(...displayHistory.map((point) => point.low ?? point.price)) : null;

    return (
      <div className="cp-inspector-rail">
        <section className="cp-rail-panel">
          <div className="cp-subtle-label">{t('Trend Evidence')}</div>
          <div className="mt-2 text-lg font-semibold text-[#191f28]">{t(selectedRow.name)}</div>
          <div className="mt-3 space-y-1">
            <InspectorRow label="Current" value={fmtConverted(currentValue)} detail={displayTrackedUnit(selectedRow.unit, unit)} />
            <InspectorRow label={t('Period high')} value={fmtConverted(periodHigh)} />
            <InspectorRow label={t('Period low')} value={fmtConverted(periodLow)} detail={historySource || t('Stored metal price series')} />
            <InspectorRow label={t('Direction')} value={pctChange != null ? `${pctChange >= 0 ? '+' : ''}${pctChange.toFixed(1)}%` : 'N/A'} detail={lang === 'ko' ? `${PERIOD_LABELS[period]} 구간` : `${PERIOD_LABELS[period]} window`} />
          </div>
        </section>

        <section className="cp-rail-panel">
          <div className="cp-subtle-label">{t('Source Audit')}</div>
          <div className="mt-3 space-y-1">
            <InspectorRow label={t('Evidence tier')} value={t(selectedRow.evidence.label)} detail={selectedRow.evidence.note} />
            <InspectorRow label={t('Transparency')} value={selectedRow.evidence.transparency} detail={selectedRow.evidence.acquisition_mode} />
            <InspectorRow label={t('Quote age')} value={selectedRow.evidence.freshness_status} detail={selectedRow.evidence.age_hours != null ? (lang === 'ko' ? `${selectedRow.evidence.age_hours.toFixed(1)}시간 경과` : `${selectedRow.evidence.age_hours.toFixed(1)} h old`) : t('Age not stored')} />
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
              <div className="cp-subtle-label !text-slate-400">{t('Selected Metal')}</div>
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
                    period === value ? 'bg-[#0d9488] text-[#191f28]' : 'text-slate-300 hover:bg-white/8'
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
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-[#0d9488] border-t-transparent" />
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
                      selectedColor={METAL_COLORS[selected || 'Pt'] || '#0d9488'}
                    />
                  </Suspense>
                </div>

                <div className="mt-5 grid gap-3 sm:grid-cols-3">
                  <div className="cp-metric-tile-dark">
                    <div className="cp-subtle-label !text-slate-400">{t('Current')}</div>
                    <div className="mt-2 text-xl font-display text-white">{fmtConverted(displayHistory[displayHistory.length - 1]!.price)}</div>
                    <div className="mt-1 text-xs leading-5 text-slate-400">{selectedDisplayUnit}</div>
                  </div>
                  <div className="cp-metric-tile-dark">
                    <div className="cp-subtle-label !text-slate-400">{t('Period high')}</div>
                    <div className="mt-2 text-xl font-display text-white">
                      {fmtConverted(Math.max(...displayHistory.map((point) => point.high ?? point.price)))}
                    </div>
                    <div className="mt-1 text-xs leading-5 text-slate-400">{t('Maximum observed value')}</div>
                  </div>
                  <div className="cp-metric-tile-dark">
                    <div className="cp-subtle-label !text-slate-400">{t('Period low')}</div>
                    <div className="mt-2 text-xl font-display text-white">
                      {fmtConverted(Math.min(...displayHistory.map((point) => point.low ?? point.price)))}
                    </div>
                    <div className="mt-1 text-xs leading-5 text-slate-400">{historySource || 'Stored metal price series'}</div>
                  </div>
                </div>

                {selectedRow ? (
                  <div className="mt-4 grid gap-3 sm:grid-cols-3">
                    <div className="rounded-[22px] border border-white/10 bg-white/6 p-3">
                      <div className="cp-subtle-label !text-slate-400">{t('Evidence tier')}</div>
                      <div className="mt-2 text-sm font-semibold text-white">{t(selectedRow.evidence.label)}</div>
                      <div className="mt-1 text-xs leading-5 text-slate-400">{selectedRow.evidence.note}</div>
                    </div>
                    <div className="rounded-[22px] border border-white/10 bg-white/6 p-3">
                      <div className="cp-subtle-label !text-slate-400">{t('Confidence')}</div>
                      <div className="mt-2 text-sm font-semibold text-white">{selectedRow.evidence.confidence_score}</div>
                      <div className="mt-1 text-xs leading-5 text-slate-400">{selectedRow.evidence.transparency}</div>
                    </div>
                    <div className="rounded-[22px] border border-white/10 bg-white/6 p-3">
                      <div className="cp-subtle-label !text-slate-400">{t('Quote age')}</div>
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
    <div className="flex flex-col gap-4">
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
