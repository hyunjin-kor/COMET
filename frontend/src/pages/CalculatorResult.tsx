import { lazy, Suspense, useLayoutEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  WorkspaceSectionFooter,
  WorkspaceSectionNav,
  useWorkspaceSections,
  type WorkspaceSection,
} from '../components/shared/WorkspaceSections';
import type { CostResult } from '../lib/api';
import { loadCalculatorResultSnapshot } from '../lib/calculator-session';
import { useUnit } from '../lib/use-unit';

const ResultBreakdownPieChart = lazy(() => import('../components/charts/ResultBreakdownPieChart'));

const CHART_COLORS = ['#3182f6', '#8b95a1', '#3182f6', '#7a9b8d', '#8b95a1', '#4e5968'];
const RESULT_SECTIONS: WorkspaceSection[] = [
  { id: 'summary', label: 'Result', summary: 'Headline price, scope, and active warnings.' },
  { id: 'manufacturing', label: 'Preparation Method', summary: 'Route, cost structure, and campaign basis.' },
  { id: 'environmental', label: 'Environmental', summary: 'Cradle-to-gate impact per kg of catalyst.' },
  { id: 'sources', label: 'Evidence', summary: 'Resolved source rows, normalization, and links.' },
];

function formatLcaNumber(value: number | null | undefined): string {
  if (value == null) return 'No data';
  if (value >= 10000) return value.toLocaleString('en-US', { maximumFractionDigits: 0 });
  if (value >= 100) return value.toLocaleString('en-US', { maximumFractionDigits: 1 });
  return value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 4 });
}

function lcaFactorStatusLabel(status: string): string {
  if (status === 'matched') return 'Matched';
  if (status === 'matched_alias') return 'Matched (alias)';
  if (status === 'explicitly_unsupported') return 'Not in dataset';
  return 'No factor';
}

function lcaFactorStatusTone(status: string): string {
  if (status === 'matched' || status === 'matched_alias') return 'border-emerald-200 bg-emerald-50 text-emerald-700';
  return 'border-amber-200 bg-amber-50 text-amber-700';
}

function sourceRecordLabel(priceScope: string, hasLink: boolean) {
  if (hasLink) {
    if (priceScope === 'literature_high_volume') return 'Public literature source';
    if (priceScope === 'vendor_lab') return 'Direct vendor source';
    return 'Public source linked';
  }
  if (priceScope === 'historical_bulk') return 'No public permalink';
  return 'Link not stored';
}

function sourceRecordTone(priceScope: string, hasLink: boolean) {
  if (hasLink) return 'border-emerald-200 bg-emerald-50 text-emerald-700';
  if (priceScope === 'historical_bulk') return 'border-amber-200 bg-amber-50 text-amber-700';
  return 'border-slate-200 bg-white text-slate-600';
}

function formatResolvedPack(material: NonNullable<CostResult['resolved_materials']>[number]) {
  if (!material.pack_quantity || !material.pack_unit) return 'Pack not stated';
  return `${material.pack_quantity} ${material.pack_unit} pack`;
}

function formatResolvedNormalization(
  material: NonNullable<CostResult['resolved_materials']>[number],
  toDisplay: (value: number) => number,
  fmtLabel: string,
) {
  if (typeof material.normalized_price_per_lb === 'number') {
    return `$${toDisplay(material.normalized_price_per_lb).toFixed(3)}${fmtLabel}`;
  }
  if (typeof material.normalized_price_per_cm2 === 'number') {
    return `$${material.normalized_price_per_cm2.toFixed(4)}/cm2`;
  }
  if (typeof material.normalized_price_per_ml === 'number') {
    return `$${material.normalized_price_per_ml.toFixed(4)}/mL`;
  }
  if (typeof material.normalized_price_per_kg_solids === 'number') {
    return `$${material.normalized_price_per_kg_solids.toFixed(2)}/kg solids`;
  }
  return 'Not stored';
}

function MetricTile({
  label,
  value,
  detail,
  dark = false,
}: {
  label: string;
  value: string;
  detail: string;
  dark?: boolean;
}) {
  return (
    <div className={dark ? 'cp-metric-tile-dark' : 'cp-metric-tile'}>
      <div className={`cp-subtle-label ${dark ? '!text-slate-400' : ''}`}>{label}</div>
      <div className={`mt-2 text-2xl font-display ${dark ? 'text-white' : 'text-slate-900'}`}>{value}</div>
      <div className={`mt-1 text-xs leading-5 ${dark ? 'text-slate-400' : 'text-slate-500'}`}>{detail}</div>
    </div>
  );
}

function RailRow({ label, value, detail }: { label: string; value: string; detail?: string }) {
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

function ChartFallback() {
  return (
    <div className="flex h-full min-h-[240px] items-center justify-center gap-3 rounded-[24px] border border-slate-200 bg-slate-50/80 text-center">
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-[#3182f6] border-t-transparent" />
      <div className="text-sm text-slate-600">Loading breakdown chart...</div>
    </div>
  );
}

export default function CalculatorResult() {
  const navigate = useNavigate();
  const { unit, toDisplay, fmtLabel, catLabel } = useUnit();
  const sectionState = useWorkspaceSections(RESULT_SECTIONS, 'result');
  const [snapshot] = useState(() => loadCalculatorResultSnapshot());

  useLayoutEffect(() => {
    window.scrollTo(0, 0);
    const timeout = window.setTimeout(() => window.scrollTo(0, 0), 0);
    return () => window.clearTimeout(timeout);
  }, []);

  function goBackToCalculator() {
    const historyIndex = typeof window !== 'undefined' ? window.history.state?.idx : 0;
    if (typeof historyIndex === 'number' && historyIndex > 0) {
      navigate(-1);
      return;
    }
    navigate('/');
  }

  if (!snapshot) {
    return (
      <section className="surface-card cp-enter overflow-hidden p-6 sm:p-7">
        <span className="section-kicker">Result</span>
        <h1 className="cp-heading-xl mt-4">No saved result is available yet.</h1>
        <p className="cp-body-copy mt-3 max-w-xl">
          Run an estimate from the cost estimate workspace first. The result then stays available for focused review.
        </p>
        <div className="mt-5">
          <button onClick={goBackToCalculator} className="cp-button-primary">
            Back to cost estimate
          </button>
        </div>
      </section>
    );
  }

  const snapshotState = snapshot;
  const { result } = snapshot;
  const altPrice = unit === 'kg' ? result.summary.estimated_price_per_lb : result.summary.estimated_price_per_kg;
  const altLabel = unit === 'kg' ? '/lb' : '/kg';
  const generatedAt = new Date(snapshot.generatedAt).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
  const composition =
    typeof result.input_summary.composition === 'string' ? result.input_summary.composition : 'Catalyst estimate';
  const catalystDomain =
    result.input_summary.catalyst_domain === 'electrocatalyst' ? 'Electrocatalyst' : 'Thermocatalyst';
  const routeSummary = result.route_summary ?? null;
  const electrodeModel = result.electrode_model ?? null;
  const spentCatalyst = result.spent_catalyst ?? null;
  const resolvedMaterials = result.resolved_materials ?? [];
  const publicSourceCount = resolvedMaterials.filter((material) => Boolean(material.reference_url)).length;
  const historicalOnlyCount = resolvedMaterials.filter(
    (material) => material.price_scope === 'historical_bulk' && !material.reference_url,
  ).length;
  const latestQuoteYear = resolvedMaterials.reduce<number | null>(
    (latest, material) => (material.quote_year && (!latest || material.quote_year > latest) ? material.quote_year : latest),
    null,
  );
  const routeReferenceCount = routeSummary?.reference_urls?.length ?? 0;
  const ledgerRows = [
    {
      label: 'Materials',
      value: `$${toDisplay(result.materials.total_materials_cost_per_lb).toFixed(3)}${fmtLabel}`,
      detail: `${result.summary.materials_pct.toFixed(1)}% of selling price`,
    },
    {
      label: 'Processing',
      value: `$${toDisplay(Number(result.step_method.processing_cost_per_lb)).toFixed(3)}${fmtLabel}`,
      detail: `${result.summary.processing_pct.toFixed(1)}% of selling price`,
    },
    typeof result.step_method.ga_per_lb === 'number'
      ? {
          label: 'G&A',
          value: `$${toDisplay(Number(result.step_method.ga_per_lb)).toFixed(3)}${fmtLabel}`,
          detail: 'General and administrative overhead',
        }
      : null,
    typeof result.step_method.sard_per_lb === 'number'
      ? {
          label: 'S&ARD',
          value: `$${toDisplay(Number(result.step_method.sard_per_lb)).toFixed(3)}${fmtLabel}`,
          detail: 'Selling, administrative, and R&D uplift',
        }
      : null,
    typeof result.step_method.margin_per_lb === 'number'
      ? {
          label: 'Margin',
          value: `$${toDisplay(Number(result.step_method.margin_per_lb)).toFixed(3)}${fmtLabel}`,
          detail: `${Number(result.step_method.margin_pct).toFixed(1)}% selling margin`,
        }
      : null,
  ].filter(Boolean) as Array<{ label: string; value: string; detail: string }>;
  const summaryRows = [
    {
      label: 'Materials',
      share: result.summary.materials_pct,
      value: `$${toDisplay(result.materials.total_materials_cost_per_lb).toFixed(3)}${fmtLabel}`,
    },
    {
      label: 'Processing',
      share: result.summary.processing_pct,
      value: `$${toDisplay(Number(result.step_method.processing_cost_per_lb)).toFixed(3)}${fmtLabel}`,
    },
    {
      label: 'G&A + margin',
      share: Math.max(0, 100 - result.summary.materials_pct - result.summary.processing_pct),
      value: 'Included',
    },
  ];
  const pieData = [
    ...result.materials.components.map((component) => ({
      name:
        component.role === 'support'
          ? `${component.name} support`
          : component.role === 'promoter'
            ? `${component.name} promoter`
            : component.name,
      value: component.cost_pct,
    })),
    { name: 'Processing', value: result.summary.processing_pct },
    { name: 'G&A + margin', value: Math.max(0, 100 - result.summary.materials_pct - result.summary.processing_pct) },
  ];

  function renderResultOverview() {
    return (
      <section className="surface-card p-4">
        <div className="grid gap-3 xl:grid-cols-[minmax(0,1.15fr)_repeat(3,minmax(0,1fr))]">
          <div className="rounded-[20px] border border-[#191f28] bg-[#191f28] p-4 text-white shadow-[0_8px_24px_rgba(15,23,42,0.18)]">
            <div className="cp-subtle-label !text-slate-400">Final result</div>
            <div className="mt-2 text-sm text-slate-300">{composition}</div>
            <div className="mt-4 flex items-end gap-3">
              <div className="font-display text-[clamp(2.5rem,4vw,4.4rem)] leading-none text-white">
                ${toDisplay(result.summary.estimated_price_per_lb).toFixed(2)}
              </div>
              <div className="pb-1 text-base text-slate-300">{fmtLabel}</div>
            </div>
            <div className="mt-2 text-xs leading-6 text-slate-300">
              Net cost ${toDisplay(result.summary.net_cost_per_lb).toFixed(2)}
              {fmtLabel} before selling margin treatment. Alternate view ${altPrice.toFixed(2)}
              {altLabel}.
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              <span className="cp-chip-dark">{catalystDomain}</span>
              <span className="cp-chip-dark">{result.step_method.scale} campaign</span>
              <span className="cp-chip-dark">{generatedAt}</span>
            </div>
          </div>

          <div className="rounded-[22px] border border-slate-900/8 bg-white/62 p-4">
            <div className="cp-subtle-label">Cost ledger</div>
            <div className="mt-3 space-y-1">
              {ledgerRows.map((row) => (
                <RailRow key={row.label} label={row.label} value={row.value} detail={row.detail} />
              ))}
            </div>
          </div>

          <div className="rounded-[22px] border border-slate-900/8 bg-white/62 p-4">
            <div className="cp-subtle-label">Evidence</div>
            <div className="mt-3 space-y-1">
              <RailRow
                label="Public links"
                value={`${publicSourceCount}/${resolvedMaterials.length || 0}`}
                detail={`${snapshotState.liveFeedCount} live / ${snapshotState.indexedFeedCount} indexed rows in the draft`}
              />
              <RailRow
                label="Latest quote year"
                value={latestQuoteYear ? String(latestQuoteYear) : 'N/A'}
                detail={`${historicalOnlyCount} archive-only material rows`}
              />
              <RailRow
                label="Route references"
                value={String(routeReferenceCount)}
                detail={routeReferenceCount ? 'Public route links stored' : 'No route link stored'}
              />
              {result.lca && result.lca.gwp_kg_co2eq_per_kg_catalyst != null ? (
                <RailRow
                  label="Cradle-to-gate GWP"
                  value={`${formatLcaNumber(result.lca.gwp_kg_co2eq_per_kg_catalyst)} kg CO2-eq/kg`}
                  detail={`${result.lca.coverage_pct}% mass coverage / Nuss & Eckelman 2014`}
                />
              ) : null}
            </div>
          </div>

          <div className="rounded-[22px] border border-slate-900/8 bg-white/62 p-4">
            <div className="cp-subtle-label">Preparation basis</div>
            <div className="mt-2 text-base font-semibold text-[#191f28]">
              {routeSummary?.name ?? snapshotState.benchmarkCandidate?.route.name ?? 'Direct workspace route'}
            </div>
            <div className="mt-3 space-y-1">
              <RailRow
                label="Campaign"
                value={`${snapshotState.orderSize} tons`}
                detail={`${result.step_method.scale} scale / ${Number(result.step_method.campaign_days).toFixed(1)} days`}
              />
              <RailRow
                label="Steps"
                value={String(snapshotState.stepLabels.length)}
                detail={snapshotState.stepLabels.length ? snapshotState.stepLabels.join(', ') : 'No step labels stored'}
              />
              <RailRow
                label="Mode"
                value={routeSummary?.manufacturing_mode ?? 'Manual selection'}
                detail={routeSummary?.application_family ?? snapshotState.benchmarkCandidate?.application_family ?? catalystDomain}
              />
            </div>
          </div>
        </div>
      </section>
    );
  }

  function renderSummarySection() {
    return (
      <section className="surface-card p-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="cp-subtle-label">Result</div>
            <div className="cp-heading-lg mt-2">Read the final estimate, route basis, and evidence together.</div>
            <div className="mt-1 text-xs leading-6 text-slate-500">
              Inputs stay in the cost estimate workspace. This screen is optimized for review, not editing.
            </div>
          </div>
          <button onClick={goBackToCalculator} className="cp-button-secondary px-4 py-2.5 text-sm">
            Back to cost estimate
          </button>
        </div>

        <div className="mt-4 grid gap-3 xl:grid-cols-[minmax(0,1.18fr)_minmax(320px,0.82fr)]">
          <div className="surface-ink relative overflow-hidden p-5 sm:p-6">
            <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(120,242,208,0.22),transparent_0_34%),radial-gradient(circle_at_bottom_right,rgba(239,195,108,0.12),transparent_0_28%)]" />
            <div className="relative">
              <div className="cp-subtle-label !text-slate-400">Estimated selling price</div>
              <div className="mt-2 text-sm text-slate-300">{composition}</div>
              <div className="mt-4 flex flex-wrap items-end gap-3">
                <div className="font-display text-[clamp(3rem,6vw,5.3rem)] leading-none text-white">
                  ${toDisplay(result.summary.estimated_price_per_lb).toFixed(2)}
                </div>
                <div className="pb-2 text-xl text-slate-300">{fmtLabel}</div>
              </div>
              <div className="mt-3 text-sm text-slate-300">
                Net cost ${toDisplay(result.summary.net_cost_per_lb).toFixed(2)}
                {fmtLabel} before selling margin treatment.
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                <span className="cp-chip-dark">{catalystDomain}</span>
                <span className="cp-chip-dark">{result.step_method.scale} campaign</span>
                <span className="cp-chip-dark">{generatedAt}</span>
                {snapshotState.benchmarkCandidate ? <span className="cp-chip-dark">Reference-loaded</span> : null}
              </div>
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <MetricTile label="Campaign" value={`${Number(result.step_method.campaign_days).toFixed(1)} d`} detail={`${snapshotState.orderSize} tons per order`} />
            <MetricTile label="Margin" value={`${Number(result.step_method.margin_pct).toFixed(1)}%`} detail="Selling margin basis" />
            <MetricTile label="Price sources" value={String(snapshotState.liveFeedCount + snapshotState.indexedFeedCount)} detail={`${snapshotState.liveFeedCount} live / ${snapshotState.indexedFeedCount} indexed`} />
            <MetricTile label="Public links" value={`${publicSourceCount}/${resolvedMaterials.length || 0}`} detail="Resolved rows with a public URL." />
          </div>
        </div>

        {result.warnings?.length ? (
          <div className="mt-4 rounded-[24px] border border-amber-200 bg-amber-50/80 p-4 text-sm text-amber-900">
            <div className="cp-subtle-label !text-amber-700">Model Scope</div>
            <div className="mt-2 space-y-2">
              {result.warnings.map((warning) => (
                <p key={warning} className="leading-6">
                  {warning}
                </p>
              ))}
            </div>
          </div>
        ) : null}

        {electrodeModel ? (
          <div className="mt-4 rounded-[24px] border border-slate-900/8 bg-white/58 p-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <div className="cp-subtle-label">Electrode Stack</div>
                <div className="cp-heading-sm mt-2">Area-based electrocatalyst layer model</div>
                <div className="mt-1 text-xs leading-6 text-slate-500">
                  Catalyst powder, ionomer, membrane, and substrate are costed on an active-area basis and displayed alongside the powder estimate.
                </div>
              </div>
              <span className="cp-chip">{electrodeModel.application_family}</span>
            </div>

            <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              <MetricTile label="Active area" value={`${electrodeModel.active_area_cm2.toFixed(1)} cm2`} detail="Per modeled layer" />
              <MetricTile label="Catalyst loading" value={`${electrodeModel.catalyst_loading_mg_cm2.toFixed(2)} mg/cm2`} detail="Dry catalyst loading" />
              <MetricTile label="Electrode total" value={`$${electrodeModel.total_cost_usd.toFixed(2)}`} detail="For selected active area" />
              <MetricTile label="Stack density" value={`$${electrodeModel.cost_per_cm2_usd.toFixed(3)}/cm2`} detail={`$${electrodeModel.cost_per_m2_usd.toFixed(2)}/m2`} />
            </div>
          </div>
        ) : null}

        {spentCatalyst ? (
          <div className="mt-4 rounded-[24px] border border-emerald-200 bg-emerald-50/80 p-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <div className="cp-subtle-label !text-emerald-700">Recovery scenario</div>
                <div className="cp-heading-sm mt-2">Spent catalyst value was included in the net-cost basis.</div>
                <div className="mt-1 text-xs leading-6 text-emerald-900">
                  This is an end-of-life recovery proxy. It is useful for early screening, but it does not yet model deactivation kinetics or regeneration frequency.
                </div>
              </div>
              <span className="cp-chip">{spentCatalyst.metal_symbol}</span>
            </div>

            <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              <MetricTile
                label="Gross metal value"
                value={`$${toDisplay(spentCatalyst.V_metal_per_lb).toFixed(2)}`}
                detail={`Per${catLabel}`}
              />
              <MetricTile
                label="Recovery cost"
                value={`$${toDisplay(spentCatalyst.C_recovery_per_lb).toFixed(2)}`}
                detail={`Per${catLabel}`}
              />
              <MetricTile
                label="Reclaimed value"
                value={`$${toDisplay(spentCatalyst.V_reclaimed_per_lb).toFixed(2)}`}
                detail={`Per${catLabel}`}
              />
              <MetricTile
                label="Loss basis"
                value={`${(spentCatalyst.loss_use_pct * 100).toFixed(1)}% / ${(spentCatalyst.loss_refining_pct * 100).toFixed(1)}%`}
                detail="Use loss / refining loss"
              />
            </div>
          </div>
        ) : null}
      </section>
    );
  }

  function renderManufacturingSection() {
    return (
      <section className="surface-card p-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="cp-subtle-label">Preparation Method</div>
            <div className="cp-heading-lg mt-2">Separate route logic from raw inputs.</div>
            <div className="mt-1 text-xs leading-6 text-slate-500">
              This surface is for campaign scale, selected preparation steps, route metadata, and the main cost split.
            </div>
          </div>
          <span className="cp-chip">{result.materials.components.length} materials</span>
        </div>

        <div className="mt-4 grid gap-2.5 sm:grid-cols-2">
          <MetricTile label="Active metals" value={String(snapshotState.activeMetalCount)} detail="Named active inputs" />
          <MetricTile label="Recipe load" value={`${snapshotState.nonSupportWt.toFixed(1)} wt%`} detail={`Support closes at ${snapshotState.supportWtPct.toFixed(1)} wt%`} />
          <MetricTile label="Support" value={snapshotState.selectedSupportName ?? 'Pending'} detail="Current support basis" />
          <MetricTile label="Preparation steps" value={String(snapshotState.stepLabels.length)} detail="Selected preparation steps" />
        </div>

        <div className="mt-4 grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(240px,0.88fr)]">
          <div className="rounded-[24px] border border-slate-900/8 bg-white/58 p-4">
            <div className="cp-subtle-label">Cost Structure</div>
            <div className="cp-heading-lg mt-2">Materials versus processing</div>
            <div className="mt-4 space-y-3">
              {summaryRows.map((item, index) => (
                <div key={item.label}>
                  <div className="flex items-center justify-between gap-3 text-sm">
                    <span className="text-slate-600">{item.label}</span>
                    <span className="font-semibold text-[#191f28]">{item.value}</span>
                  </div>
                  <div className="mt-2 h-2 rounded-full bg-slate-200/80">
                    <div
                      className="h-full rounded-full"
                      style={{ width: `${Math.max(item.share, 4)}%`, backgroundColor: CHART_COLORS[index] }}
                    />
                  </div>
                  <div className="mt-1 text-xs text-slate-500">{item.share.toFixed(1)}% share</div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[24px] border border-slate-900/8 bg-white/58 p-4">
            <div className="cp-heading-sm">Breakdown wheel</div>
            <div className="mt-1 text-xs text-slate-500">Materials, processing, and selling adjustments.</div>
            <div className="mt-4 h-[240px]">
              <Suspense fallback={<ChartFallback />}>
                <ResultBreakdownPieChart data={pieData} colors={CHART_COLORS} />
              </Suspense>
            </div>
            <div className="mt-2 grid gap-2 sm:grid-cols-2">
              {pieData.map((entry, index) => (
                <div key={entry.name} className="flex items-center gap-2 text-sm text-slate-600">
                  <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: CHART_COLORS[index % CHART_COLORS.length] }} />
                  {entry.name}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-4 rounded-[24px] border border-slate-900/8 bg-white/58 p-4">
          <div className="cp-subtle-label">Preparation Steps</div>
          <div className="mt-3 flex flex-wrap gap-2">
            {snapshotState.stepLabels.map((label) => (
              <span key={label} className="cp-chip">
                {label}
              </span>
            ))}
          </div>
        </div>

        {snapshotState.benchmarkCandidate ? (
          <div className="mt-4 rounded-[24px] border border-emerald-200 bg-emerald-50/80 p-4">
            <div className="cp-subtle-label !text-emerald-700">Reference baseline</div>
            <div className="mt-2 cp-heading-sm">{snapshotState.benchmarkCandidate.title}</div>
            <div className="mt-2 text-sm leading-6 text-emerald-900">{snapshotState.benchmarkCandidate.screening_summary}</div>
            <div className="mt-3 flex flex-wrap gap-2">
              <span className="cp-chip">{snapshotState.benchmarkCandidate.archetype}</span>
              <span className="cp-chip">{snapshotState.benchmarkCandidate.route.name}</span>
              <span className="cp-chip">
                {snapshotState.benchmarkCandidate.catalyst_domain === 'electrocatalyst' ? 'Electrocatalyst' : 'Thermocatalyst'}
              </span>
              <span className="cp-chip">Evidence {snapshotState.benchmarkCandidate.scores.evidence.toFixed(1)}</span>
            </div>
          </div>
        ) : null}

        {routeSummary ? (
          <div className="mt-4 rounded-[24px] border border-sky-200 bg-sky-50/75 p-4">
            <div className="cp-subtle-label !text-sky-700">Preparation method</div>
            <div className="mt-2 cp-heading-sm">{routeSummary.name}</div>
            <div className="mt-2 text-sm leading-6 text-sky-900">
              {routeSummary.route_note || 'Template-driven route metadata is attached to this estimate.'}
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              <span className="cp-chip">{routeSummary.manufacturing_mode}</span>
              <span className="cp-chip">{routeSummary.application_family}</span>
            </div>
            <div className="mt-4 grid gap-3 lg:grid-cols-3">
              <div>
                <div className="cp-subtle-label !text-sky-700">Pre-treatment</div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {routeSummary.preprocess.map((item) => (
                    <span key={item} className="cp-chip">
                      {item}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <div className="cp-subtle-label !text-sky-700">Synthesis</div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {routeSummary.synthesis.map((item) => (
                    <span key={item} className="cp-chip">
                      {item}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <div className="cp-subtle-label !text-sky-700">Post-treatment</div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {routeSummary.postprocess.map((item) => (
                    <span key={item} className="cp-chip">
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : null}

        {spentCatalyst ? (
          <div className="mt-4 rounded-[24px] border border-emerald-200 bg-emerald-50/80 p-4">
            <div className="cp-subtle-label !text-emerald-700">Lifecycle proxy</div>
            <div className="mt-2 text-sm leading-6 text-emerald-900">
              Net cost includes spent catalyst recovery for {spentCatalyst.metal_symbol}. The model uses support and reactor-type loss assumptions from the CatCost-style recovery proxy, not a full deactivation-regeneration cycle.
            </div>
          </div>
        ) : null}
      </section>
    );
  }

  function renderEnvironmentalSection() {
    const lca = result.lca;
    if (!lca) {
      return (
        <section className="surface-card p-4">
          <div className="cp-subtle-label">Environmental</div>
          <div className="cp-heading-lg mt-2">No LCA data attached to this estimate.</div>
          <div className="mt-2 text-xs leading-6 text-slate-500">
            Re-run the estimate to compute cradle-to-gate impact.
          </div>
        </section>
      );
    }

    const ref = lca.reference;
    const gwp = lca.gwp_kg_co2eq_per_kg_catalyst;
    const ced = lca.ced_mj_per_kg_catalyst;
    const coverage = lca.coverage_pct;
    const dataGap = lca.data_gap_pct;

    return (
      <section className="surface-card p-4">
        <div className="flex min-w-0 flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div className="min-w-0">
            <div className="cp-subtle-label">Environmental</div>
            <div className="cp-heading-lg mt-2">Cradle-to-gate impact per kg of catalyst</div>
            <div className="mt-1 text-xs leading-6 text-slate-500">
              Weighted-average over the wt% composition. Manufacturing-step emissions are not included in this version — only embodied material impact.
            </div>
          </div>
          <span className={`cp-chip shrink-0 ${dataGap > 0 ? 'border-amber-200 bg-amber-50 text-amber-700' : 'border-emerald-200 bg-emerald-50 text-emerald-700'}`}>
            {coverage}% covered
          </span>
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <MetricTile
            label="GWP (100a)"
            value={`${formatLcaNumber(gwp)} kg`}
            detail="kg CO2-eq per kg of finished catalyst (IPCC GWP100a)."
          />
          <MetricTile
            label="Cumulative energy demand"
            value={`${formatLcaNumber(ced)} MJ`}
            detail="Total primary energy per kg of finished catalyst."
          />
          <MetricTile
            label="Composition coverage"
            value={`${coverage}%`}
            detail={dataGap > 0 ? `${dataGap}% of mass has no verified factor.` : 'Every component has a verified factor.'}
          />
          <MetricTile
            label="Data source"
            value="Nuss & Eckelman 2014"
            detail="PLOS ONE 9(7): e101298 — CC BY 4.0."
          />
        </div>

        {lca.warnings.length > 0 ? (
          <div className="mt-4 rounded-[18px] border border-amber-200 bg-amber-50 px-4 py-3 text-sm leading-6 text-amber-900" role="status">
            <div className="font-semibold">LCA notes</div>
            <ul className="mt-2 list-disc space-y-1 pl-5">
              {lca.warnings.map((warning, idx) => (
                <li key={idx}>{warning}</li>
              ))}
            </ul>
          </div>
        ) : null}

        <div className="mt-5 overflow-hidden rounded-[24px] border border-slate-200">
          <table className="min-w-full text-left text-xs leading-6">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-3 py-2 font-semibold">Component</th>
                <th className="px-3 py-2 font-semibold">Role</th>
                <th className="px-3 py-2 font-semibold">wt%</th>
                <th className="px-3 py-2 font-semibold">Status</th>
                <th className="px-3 py-2 font-semibold text-right">GWP (kg CO2-eq/kg cat)</th>
                <th className="px-3 py-2 font-semibold text-right">CED (MJ/kg cat)</th>
              </tr>
            </thead>
            <tbody>
              {lca.per_component.map((entry, idx) => (
                <tr key={`${entry.name}-${idx}`} className="border-t border-slate-100">
                  <td className="px-3 py-2 font-semibold text-slate-900">
                    {entry.name}
                    {entry.matched_key && entry.matched_key !== entry.name ? (
                      <span className="ml-1 text-[10px] text-slate-500">(via {entry.matched_key})</span>
                    ) : null}
                  </td>
                  <td className="px-3 py-2 text-slate-600">{entry.role ?? '—'}</td>
                  <td className="px-3 py-2 text-slate-600">{entry.wt_pct.toFixed(2)}</td>
                  <td className="px-3 py-2">
                    <span className={`inline-flex rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.16em] ${lcaFactorStatusTone(entry.factor_status)}`}>
                      {lcaFactorStatusLabel(entry.factor_status)}
                    </span>
                  </td>
                  <td className="px-3 py-2 text-right font-mono text-slate-900">
                    {entry.gwp_contribution_kg_co2eq_per_kg_catalyst != null
                      ? formatLcaNumber(entry.gwp_contribution_kg_co2eq_per_kg_catalyst)
                      : '—'}
                  </td>
                  <td className="px-3 py-2 text-right font-mono text-slate-900">
                    {entry.ced_contribution_mj_per_kg_catalyst != null
                      ? formatLcaNumber(entry.ced_contribution_mj_per_kg_catalyst)
                      : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-5 rounded-[20px] border border-slate-200 bg-white/72 p-4">
          <div className="cp-subtle-label">Reference</div>
          <div className="mt-2 text-sm font-semibold text-slate-900">{ref.citation}</div>
          <div className="mt-1 text-xs leading-6 text-slate-600">
            {ref.table_of_origin}. Underlying LCI: {ref.underlying_lci_database}. Uncertainty: {ref.uncertainty_basis}. License: {ref.license}.
          </div>
          <div className="mt-2 text-xs">
            <a href={ref.url} target="_blank" rel="noreferrer" className="text-[#3182f6] underline-offset-4 hover:underline">
              Open the source paper (DOI {ref.doi})
            </a>
          </div>
          <div className="mt-3 text-xs leading-6 text-slate-500">{ref.notes}</div>
        </div>
      </section>
    );
  }

  function renderSourcesSection() {
    return (
      <section className="surface-card p-4">
        <div className="flex min-w-0 flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div className="min-w-0">
            <div className="cp-subtle-label">Evidence</div>
            <div className="cp-heading-lg mt-2">Resolved material sources and normalization</div>
            <div className="mt-1 text-xs leading-6 text-slate-500">
              Each record shows raw quote, pack basis, normalization basis, and public link status when available.
            </div>
          </div>
          <span className="cp-chip shrink-0">{snapshotState.selectedSupportName ?? 'Support'}</span>
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <MetricTile
            label="Resolved rows"
            value={String(resolvedMaterials.length)}
            detail="Material source rows used during estimate resolution."
          />
          <MetricTile label="Public links" value={String(publicSourceCount)} detail="Rows that open a public source page." />
          <MetricTile
            label="Archive-only"
            value={String(historicalOnlyCount)}
            detail="Historical rows without a stable public URL."
          />
          <MetricTile
            label="Route references"
            value={String(routeReferenceCount)}
            detail={latestQuoteYear ? `Latest quote year ${latestQuoteYear}` : 'No quote year stored'}
          />
        </div>

        <div className="mt-4 grid gap-3 xl:grid-cols-2">
          {result.materials.components.map((component, index) => (
            <div key={`${component.name}-${component.role}`} className="rounded-[24px] border border-slate-900/8 bg-white/58 p-4">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div className="min-w-0">
                  <div className="flex items-center gap-2.5">
                    <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: CHART_COLORS[index % CHART_COLORS.length] }} />
                    <div className="cp-heading-sm">{component.name}</div>
                  </div>
                  <div className="mt-1 text-[11px] uppercase tracking-[0.18em] text-slate-400">
                    {component.role.replace('_', ' ')}
                  </div>
                </div>
                <div className="text-left sm:text-right">
                  <div className="cp-subtle-label">Per catalyst</div>
                  <div className="mt-2 font-display text-[1.45rem] text-[#191f28]">
                    ${toDisplay(component.cost_per_lb_cat).toFixed(3)}
                    {catLabel}
                  </div>
                </div>
              </div>

              <div className="mt-4 grid gap-2.5 sm:grid-cols-3 xl:grid-cols-1 2xl:grid-cols-3">
                <MetricTile label="wt%" value={(component.wt_frac * 100).toFixed(1)} detail="Loaded into catalyst" />
                <MetricTile label="Unit price" value={`$${toDisplay(component.price_per_lb).toFixed(3)}`} detail={`Per${fmtLabel}`} />
                <MetricTile label="Share" value={`${Number(component.cost_pct).toFixed(1)}%`} detail="Of material cost stack" />
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 rounded-[22px] border border-slate-900/8 bg-white/60 p-4">
          <div className="flex items-center justify-between gap-3 text-sm">
            <span className="text-slate-600">Total material cost</span>
            <span className="font-semibold text-[#191f28]">
              ${toDisplay(result.materials.total_materials_cost_per_lb).toFixed(4)}
              {catLabel}
            </span>
          </div>
          <div className="mt-2 text-xs leading-6 text-slate-500">
            CatCost-style step basis with backend escalation and selling adjustments applied in the calculation engine.
          </div>
        </div>

        {resolvedMaterials.length > 0 ? (
          <div className="mt-4 rounded-[22px] border border-slate-900/8 bg-white/60 p-4">
            <div className="cp-subtle-label">Source Records</div>
            <div className="mt-3 grid gap-3">
              {resolvedMaterials.map((material) => (
                <div key={`${material.used_for}-${material.material_key}`} className="rounded-[18px] border border-slate-200 bg-white px-4 py-3">
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                    <div className="min-w-0">
                      <div className="font-semibold text-[#191f28]">{material.name}</div>
                      <div className="mt-1 text-xs text-slate-500">
                        {material.used_for} / {material.price_scope} / {material.pricing_basis}
                      </div>
                    </div>
                    <div className="text-left sm:text-right">
                      <div className="font-mono text-slate-900">
                        ${material.price.toFixed(material.price < 1 ? 4 : 2)} {material.price_unit}
                      </div>
                      <div className="mt-1 text-xs text-slate-500">
                        {material.quote_source}
                        {material.quote_year ? ` / ${material.quote_year}` : ''}
                      </div>
                      <div className="mt-2">
                        <span
                          className={`inline-flex rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.16em] ${sourceRecordTone(material.price_scope, Boolean(material.reference_url))}`}
                        >
                          {sourceRecordLabel(material.price_scope, Boolean(material.reference_url))}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="mt-3 grid gap-2.5 sm:grid-cols-3">
                    <div className="rounded-[16px] border border-slate-200 bg-slate-50/80 px-3 py-2.5">
                      <div className="cp-subtle-label">Pack Basis</div>
                      <div className="mt-1 text-sm font-semibold text-slate-900">{formatResolvedPack(material)}</div>
                    </div>
                    <div className="rounded-[16px] border border-slate-200 bg-slate-50/80 px-3 py-2.5">
                      <div className="cp-subtle-label">Normalization</div>
                      <div className="mt-1 text-sm font-semibold text-slate-900">
                        {formatResolvedNormalization(material, toDisplay, fmtLabel)}
                      </div>
                    </div>
                    <div className="rounded-[16px] border border-slate-200 bg-slate-50/80 px-3 py-2.5">
                      <div className="cp-subtle-label">Pricing Basis</div>
                      <div className="mt-1 text-sm font-semibold text-slate-900">
                        {material.pricing_basis.replace(/_/g, ' ')}
                      </div>
                    </div>
                  </div>
                  {material.live_override?.applied ? (
                    <div className="mt-3 rounded-[14px] border border-[#3182f6] bg-[#e8f2ff] px-3 py-2.5 text-xs leading-5 text-[#1957c2]">
                      <div className="font-bold uppercase tracking-[0.16em] text-[#1b64da]">
                        Live market quote in use
                      </div>
                      <div className="mt-1 text-[#191f28]">
                        Catalyst price uses the latest <span className="font-semibold">{material.live_override.live_source}</span> quote
                        of <span className="font-mono font-semibold">${material.live_override.live_price.toFixed(material.live_override.live_price < 1 ? 4 : 2)} {material.live_override.live_price_unit}</span>
                        {material.live_override.live_fetched_at
                          ? ` (fetched ${new Date(material.live_override.live_fetched_at).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })})`
                          : ''}
                        .
                      </div>
                      <div className="mt-1 text-[#4e5968]">
                        Offline fallback: <span className="font-mono">${material.live_override.fallback_price.toFixed(2)} {material.live_override.fallback_price_unit}</span> from {material.live_override.fallback_source}
                        {material.live_override.fallback_quote_year ? ` (${material.live_override.fallback_quote_year})` : ''}
                        .
                      </div>
                    </div>
                  ) : material.live_override && material.live_override.applied === false ? (
                    <div className="mt-3 rounded-[14px] border border-[#ffa800] bg-[#fff4dd] px-3 py-2.5 text-xs leading-5 text-[#7a5a00]">
                      <span className="font-bold uppercase tracking-[0.16em]">No live quote</span>
                      <span className="ml-2">
                        This metal can carry a live market quote, but none is stored. Using the static catalog price. Refresh the prices feed to populate.
                      </span>
                    </div>
                  ) : null}
                  {material.reference_url ? (
                    <a
                      href={material.reference_url}
                      target="_blank"
                      rel="noreferrer"
                      className="mt-2 inline-flex text-xs text-[#1b64da] underline underline-offset-2"
                    >
                      Open source
                    </a>
                  ) : (
                    <div className="mt-2 text-xs leading-5 text-slate-500">
                      {material.price_scope === 'historical_bulk'
                        ? 'Historical bulk row without a stable public permalink.'
                        : 'No public source URL stored for this row.'}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ) : null}

        {routeSummary?.reference_urls?.length ? (
          <div className="mt-4 rounded-[22px] border border-slate-900/8 bg-white/60 p-4">
            <div className="cp-subtle-label">Route References</div>
            <div className="mt-3 flex flex-wrap gap-2">
              {routeSummary.reference_urls.map((url) => (
                <a key={url} href={url} target="_blank" rel="noreferrer" className="cp-button-secondary px-3 py-2 text-xs">
                  Open route reference
                </a>
              ))}
            </div>
          </div>
        ) : null}
      </section>
    );
  }

  return (
    <div className="space-y-4">
      <section className="surface-card cp-enter overflow-hidden p-5 sm:p-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <span className="section-kicker">Result</span>
            <h1 className="cp-heading-xl mt-4">Read the estimate, route basis, and evidence in one place.</h1>
            <p className="cp-body-copy mt-3 max-w-2xl">
              This screen is for reading. Cost structure, preparation basis, and source records stay grouped without the editing workspace.
            </p>
          </div>
          <button onClick={goBackToCalculator} className="cp-button-primary">
            Back to cost estimate
          </button>
        </div>
      </section>

      {renderResultOverview()}

      <WorkspaceSectionNav
        sections={RESULT_SECTIONS}
        activeSectionId={sectionState.activeSectionId}
        activeIndex={sectionState.activeIndex}
        onSelect={sectionState.setActiveSection}
      />

      {sectionState.activeSection.id === 'summary' ? renderSummarySection() : null}
      {sectionState.activeSection.id === 'manufacturing' ? renderManufacturingSection() : null}
      {sectionState.activeSection.id === 'environmental' ? renderEnvironmentalSection() : null}
      {sectionState.activeSection.id === 'sources' ? renderSourcesSection() : null}

      <WorkspaceSectionFooter
        activeSection={sectionState.activeSection}
        activeIndex={sectionState.activeIndex}
        totalSections={RESULT_SECTIONS.length}
        onPrevious={sectionState.goPrevious}
        onNext={sectionState.goNext}
        canGoPrevious={sectionState.canGoPrevious}
        canGoNext={sectionState.canGoNext}
      />
    </div>
  );
}
