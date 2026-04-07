import { useLayoutEffect, useState } from 'react';
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
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

const CHART_COLORS = ['#78f2d0', '#88a8ff', '#efc36c', '#f3a08d', '#c5b7ff', '#8de0ff'];
const RESULT_SECTIONS: WorkspaceSection[] = [
  { id: 'summary', label: 'Result', summary: 'Headline price, scope, and active warnings.' },
  { id: 'manufacturing', label: 'Preparation Method', summary: 'Route, cost structure, and campaign basis.' },
  { id: 'sources', label: 'Evidence', summary: 'Resolved source rows, normalization, and links.' },
];

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
      <div className="text-right text-sm font-semibold text-slate-950">{value}</div>
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

  function renderEvidenceRail() {
    return (
      <div className="cp-inspector-rail">
        <section className="surface-rail overflow-hidden p-4">
          <div className="cp-subtle-label !text-slate-400">Evidence Rail</div>
          <div className="mt-2 text-sm text-slate-300">{composition}</div>
          <div className="mt-4 flex items-end gap-3">
            <div className="font-display text-[clamp(2.3rem,4vw,4rem)] leading-none text-white">
              ${toDisplay(result.summary.estimated_price_per_lb).toFixed(2)}
            </div>
            <div className="pb-1 text-sm text-slate-300">{fmtLabel}</div>
          </div>
          <div className="mt-2 text-xs leading-6 text-slate-400">
            Alternate view: ${altPrice.toFixed(2)}
            {altLabel}
          </div>
          <div className="mt-4 grid gap-2 sm:grid-cols-2 xl:grid-cols-1">
            <MetricTile
              dark
              label="Scope"
              value={catalystDomain}
              detail={`${snapshotState.orderSize} tons per order / ${result.step_method.scale} campaign`}
            />
            <MetricTile
              dark
              label="Source rows"
              value={`${publicSourceCount}/${resolvedMaterials.length || 0}`}
              detail={`${snapshotState.liveFeedCount} live and ${snapshotState.indexedFeedCount} indexed rows in the draft`}
            />
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <span className="cp-chip-dark">Generated {generatedAt}</span>
            <span className="cp-chip-dark">{snapshotState.selectedSupportName ?? 'Support pending'}</span>
            <span className="cp-chip-dark">{snapshotState.stepLabels.length} preparation steps</span>
            {snapshotState.benchmarkCandidate ? <span className="cp-chip-dark">{snapshotState.benchmarkCandidate.title}</span> : null}
          </div>
        </section>

        <section className="cp-rail-panel">
          <div className="cp-subtle-label">Cost Ledger</div>
          <div className="mt-2 text-lg font-semibold text-slate-950">Read how the price was assembled.</div>
          <div className="mt-3 space-y-1">
            {ledgerRows.map((row) => (
              <RailRow key={row.label} label={row.label} value={row.value} detail={row.detail} />
            ))}
            <RailRow
              label="Final result"
              value={`$${toDisplay(result.summary.estimated_price_per_lb).toFixed(2)}${fmtLabel}`}
              detail={`Net cost $${toDisplay(result.summary.net_cost_per_lb).toFixed(2)}${fmtLabel}`}
            />
          </div>
        </section>

        <section className="cp-rail-panel">
          <div className="cp-subtle-label">Route Audit</div>
          <div className="mt-2 text-lg font-semibold text-slate-950">
            {routeSummary?.name ?? snapshotState.benchmarkCandidate?.route.name ?? 'Direct workspace route'}
          </div>
          <div className="mt-3 space-y-1">
            <RailRow
              label="Preparation basis"
              value={routeSummary?.manufacturing_mode ?? 'Manual selection'}
              detail={routeSummary?.application_family ?? snapshotState.benchmarkCandidate?.application_family ?? catalystDomain}
            />
            <RailRow
              label="Steps"
              value={String(snapshotState.stepLabels.length)}
              detail={snapshotState.stepLabels.length ? snapshotState.stepLabels.join(', ') : 'No step labels stored'}
            />
            <RailRow
              label="References"
              value={String(routeReferenceCount)}
              detail={
                routeReferenceCount
                  ? `${routeReferenceCount} public route references stored`
                  : 'No route reference URL stored'
              }
            />
            <RailRow
              label="Latest quote year"
              value={latestQuoteYear ? String(latestQuoteYear) : 'N/A'}
              detail={`${historicalOnlyCount} archive-only material rows`}
            />
          </div>
          {result.warnings?.length ? (
            <div className="mt-3 rounded-[18px] border border-amber-200 bg-amber-50/80 px-3 py-3 text-xs leading-6 text-amber-900">
              {result.warnings[0]}
            </div>
          ) : null}
        </section>
      </div>
    );
  }

  function renderSummarySection() {
    return (
      <section className="surface-card p-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="cp-subtle-label">Result</div>
            <div className="cp-heading-lg mt-2">Read the latest estimate without editing noise.</div>
            <div className="mt-1 text-xs leading-6 text-slate-500">
              Inputs stay in the cost estimate workspace. This screen is optimized for reading scope, evidence, and the final selling price.
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
                    <span className="font-semibold text-slate-950">{item.value}</span>
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
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={pieData} innerRadius={64} outerRadius={96} dataKey="value" paddingAngle={3} stroke="transparent">
                    {pieData.map((entry, index) => (
                      <Cell key={entry.name} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value) => [`${Number(value).toFixed(1)}%`, 'Share']}
                    contentStyle={{
                      borderRadius: 18,
                      border: '1px solid rgba(31,47,72,0.10)',
                      background: 'rgba(255,251,245,0.96)',
                      color: '#142033',
                      fontSize: 12,
                      boxShadow: '0 18px 48px rgba(23,34,51,0.12)',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
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
                  <div className="mt-2 font-display text-[1.45rem] text-slate-950">
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
            <span className="font-semibold text-slate-950">
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
                      <div className="font-semibold text-slate-950">{material.name}</div>
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
                  {material.reference_url ? (
                    <a
                      href={material.reference_url}
                      target="_blank"
                      rel="noreferrer"
                      className="mt-2 inline-flex text-xs text-sky-700 underline underline-offset-2"
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
            <h1 className="cp-heading-xl mt-4">Keep the result separate from the editing workspace.</h1>
            <p className="cp-body-copy mt-3 max-w-2xl">
              This screen keeps the estimate, evidence, and preparation context visible at the same time, without sending you back through the input flow.
            </p>
          </div>
          <button onClick={goBackToCalculator} className="cp-button-primary">
            Back to cost estimate
          </button>
        </div>
      </section>

      <div className="cp-split-workspace">
        <div className="space-y-4">
          <WorkspaceSectionNav
            sections={RESULT_SECTIONS}
            activeSectionId={sectionState.activeSectionId}
            activeIndex={sectionState.activeIndex}
            onSelect={sectionState.setActiveSection}
          />

          {sectionState.activeSection.id === 'summary' ? renderSummarySection() : null}
          {sectionState.activeSection.id === 'manufacturing' ? renderManufacturingSection() : null}
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

        <div>{renderEvidenceRail()}</div>
      </div>
    </div>
  );
}
