import { ScientificText } from '../components/shared/ScientificText';
import { lazy, Suspense, useLayoutEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import CostEvidencePanel from '../components/CostEvidencePanel';
import { PracticalCostingResult } from '../components/PracticalCostingResult';
import { FitPriceText } from '../components/shared/FitPriceText';
import {
  WorkspaceSectionFooter,
  WorkspaceSectionNav,
  useWorkspaceSections,
  type WorkspaceSection,
} from '../components/shared/WorkspaceSections';
import { saveEstimate, type CostResult } from '../lib/api';
import { LB_PER_KG, TROY_OZ_PER_LB } from '../lib/unit-conversion';
import { loadCalculatorResultSnapshot, saveCalculatorResultSnapshot } from '../lib/calculator-session';
import { buildResultCsv, downloadCsv, resultCsvFilename } from '../lib/export-csv';
import { formatPrice } from '../lib/format-price';
import { electrodeCostRows } from '../lib/electrode-result';
import { useLang } from '../lib/i18n';
import { useUnit } from '../lib/use-unit';

const ResultBreakdownPieChart = lazy(() => import('../components/charts/ResultBreakdownPieChart'));

// Toss-aligned categorical palette: every entry is visually distinct so the
// donut and the cost-share bars never paint two slices in the same hue.
const CHART_COLORS = [
  '#0d9488', // Toss blue
  '#22c55e', // green
  '#ffa800', // amber
  '#f04452', // red
  '#7950f2', // purple
  '#0099ff', // cyan
  '#fb6f5f', // coral
  '#4e5968', // slate
];
const RESULT_SECTIONS: WorkspaceSection[] = [
  { id: 'summary', label: 'Result', summary: 'Headline price, scope, and active warnings.' },
  { id: 'manufacturing', label: 'Preparation Method', summary: 'Route, cost structure, and production scale.' },
  { id: 'environmental', label: 'Environmental', summary: 'Cradle-to-gate impact per kg of catalyst.' },
  { id: 'sources', label: 'Evidence', summary: 'Resolved source rows, normalization, and links.' },
];

const domainDisplay = (domain: string) =>
  domain === 'electrocatalyst' ? 'Electrocatalyst' : domain === 'thermal' ? 'Thermocatalyst' : domain;
const applicationDisplay = (family: string) =>
  family === 'fuel_cell' ? 'Fuel Cell'
    : family === 'direct_methanol_fuel_cell' ? 'DMFC'
      : family === 'electrolyzer' ? 'Electrolyzer'
        : family === 'general' ? 'General'
          : family === 'thermal' ? 'Thermocatalyst'
            : family;
const modeDisplay = (mode: string) => (/^[a-z_]+$/.test(mode) ? mode.replace(/_/g, ' ').toUpperCase() : mode);

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
    return `${formatPrice(toDisplay(material.normalized_price_per_lb))}${fmtLabel}`;
  }
  if (typeof material.normalized_price_per_cm2 === 'number') {
    return `${formatPrice(material.normalized_price_per_cm2)}/cm²`;
  }
  if (typeof material.normalized_price_per_ml === 'number') {
    return `${formatPrice(material.normalized_price_per_ml)}/mL`;
  }
  if (typeof material.normalized_price_per_kg_solids === 'number') {
    return `${formatPrice(material.normalized_price_per_kg_solids)}/kg solids`;
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
      <div className={`cp-subtle-label ${dark ? '!text-slate-400' : ''}`}><ScientificText text={label} /></div>
      <div className={`mt-2 text-2xl font-display ${dark ? 'text-white' : 'text-slate-900'}`}><ScientificText text={value} /></div>
      <div className={`mt-1 text-xs leading-5 ${dark ? 'text-slate-400' : 'text-slate-600'}`}><ScientificText text={detail} /></div>
    </div>
  );
}

function RailRow({ label, value, detail }: { label: string; value: string; detail?: string }) {
  return (
    <div className="cp-data-row">
      <div>
        <div className="cp-subtle-label"><ScientificText text={label} /></div>
        {detail ? <div className="mt-1 text-xs leading-5 text-slate-600"><ScientificText text={detail} /></div> : null}
      </div>
      <div className="text-right text-sm font-semibold text-[#191f28]"><ScientificText text={value} /></div>
    </div>
  );
}

function ChartFallback() {
  const { t } = useLang();
  return (
    <div className="flex h-full min-h-[240px] items-center justify-center gap-3 rounded-[24px] border border-slate-200 bg-slate-50/80 text-center">
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-[#0d9488] border-t-transparent" />
      <div className="text-sm text-slate-600">{t("Loading breakdown chart...")}</div>
    </div>
  );
}

function quotePerLb(price: number, unitLabel: string | null | undefined): number | null {
  if (price == null || !unitLabel) return null;
  if (unitLabel === '$/lb') return price;
  if (unitLabel === '$/kg') return price / LB_PER_KG;
  if (unitLabel === '$/troy_oz') return price * TROY_OZ_PER_LB;
  if (unitLabel === '$/g') return price * 453.59237;
  return null;
}

export default function CalculatorResult() {
  const navigate = useNavigate();
  const { unit, toDisplay, fmtLabel, catLabel } = useUnit();
  const { lang, t } = useLang();
  const sectionState = useWorkspaceSections(RESULT_SECTIONS, 'result');
  const [snapshot, setSnapshot] = useState(() => loadCalculatorResultSnapshot());
  const [saveName, setSaveName] = useState('');
  const [saveState, setSaveState] = useState<'idle' | 'saving' | 'saved' | 'failed'>('idle');

  async function handleSaveEstimate() {
    if (!snapshot?.costInput || saveState === 'saving') return;
    const name = saveName.trim()
      || (typeof snapshot.result.input_summary.composition === 'string'
        ? snapshot.result.input_summary.composition
        : 'Untitled estimate');
    setSaveState('saving');
    try {
      const saved = await saveEstimate(snapshot.costInput, name);
      const savedSnapshot = { ...snapshot, savedEstimateId: saved.id, result: saved.result };
      setSnapshot(savedSnapshot);
      saveCalculatorResultSnapshot(savedSnapshot);
      setSaveState('saved');
    } catch {
      setSaveState('failed');
    }
  }

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
        <h1 className="cp-heading-xl">{t('No saved result yet')}</h1>
        <p className="cp-body-copy mt-2 max-w-xl">
          {t('Run an estimate from the cost estimate workspace first. The result then stays available for focused review.')}
        </p>
        <div className="mt-5">
          <button onClick={goBackToCalculator} className="cp-button-primary">
            {t('Back to cost estimate')}
          </button>
        </div>
      </section>
    );
  }

  const snapshotState = snapshot;
  const { result } = snapshot;
  const benchmarkCandidate =
    snapshot.benchmarkCandidate && snapshot.benchmarkCandidate.catalyst_domain === result.input_summary.catalyst_domain
      ? snapshot.benchmarkCandidate
      : null;
  const altPrice = unit === 'kg' ? result.summary.estimated_price_per_lb : result.summary.estimated_price_per_kg;
  const altLabel = unit === 'kg' ? '/lb' : '/kg';
  const generatedAt = new Date(snapshot.generatedAt).toLocaleString(lang === 'ko' ? 'ko-KR' : 'en-US', {
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
  const costingScope = result.costing_scope ?? null;
  const electrodeModel = result.electrode_model ?? null;
  const spentCatalyst = electrodeModel ? null : result.spent_catalyst ?? null;
  const resolvedMaterials = result.resolved_materials ?? [];
  const recipeReferenceKeys = new Set(snapshotState.costInput?.components
    ?.filter((component) => component.recipe_consumption && component.material_key)
    .map((component) => component.material_key) ?? []);
  const publicSourceCount = resolvedMaterials.filter((material) => Boolean(material.reference_url)).length;
  const historicalOnlyCount = resolvedMaterials.filter(
    (material) => material.price_scope === 'historical_bulk' && !material.reference_url,
  ).length;
  const latestQuoteYear = resolvedMaterials.reduce<number | null>(
    (latest, material) => (material.quote_year && (!latest || material.quote_year > latest) ? material.quote_year : latest),
    null,
  );
  const routeReferenceCount = routeSummary?.reference_urls?.length ?? 0;
  const pctOfSelling = (pct: number) => (lang === 'ko' ? `판매가의 ${pct.toFixed(1)}%` : `${pct.toFixed(1)}% of selling price`);
  const electrodeRows = electrodeCostRows(result);
  const ledgerRows = electrodeRows ? electrodeRows.map((item) => ({
    label: item.label,
    value: `${formatPrice(item.costPerCm2)}/cm²`,
    detail: `${item.share.toFixed(1)}%`,
  })) : [
    {
      label: 'Materials',
      value: `${formatPrice(toDisplay(result.materials.total_materials_cost_per_lb))}${fmtLabel}`,
      detail: pctOfSelling(result.summary.materials_pct),
    },
    {
      label: 'Processing',
      value: `${formatPrice(toDisplay(Number(result.step_method.processing_cost_per_lb)))}${fmtLabel}`,
      detail: pctOfSelling(result.summary.processing_pct),
    },
    typeof result.step_method.ga_per_lb === 'number'
      ? {
          label: 'Overhead (general and administrative)',
          value: `${formatPrice(toDisplay(Number(result.step_method.ga_per_lb)))}${fmtLabel}`,
          detail: t('General and administrative overhead'),
        }
      : null,
    typeof result.step_method.sard_per_lb === 'number'
      ? {
          label: 'Sales, admin & R&D (S&ARD)',
          value: `${formatPrice(toDisplay(Number(result.step_method.sard_per_lb)))}${fmtLabel}`,
          detail: t('Selling, administrative, and R&D uplift'),
        }
      : null,
    typeof result.step_method.margin_per_lb === 'number'
      ? {
          label: 'Margin',
          value: `${formatPrice(toDisplay(Number(result.step_method.margin_per_lb)))}${fmtLabel}`,
          detail: lang === 'ko' ? `판매 마진 ${Number(result.step_method.margin_pct).toFixed(1)}%` : `${Number(result.step_method.margin_pct).toFixed(1)}% selling margin`,
        }
      : null,
  ].filter(Boolean) as Array<{ label: string; value: string; detail: string }>;
  const summaryRows = electrodeRows ? electrodeRows.map((item) => ({
    label: item.label,
    share: item.share,
    value: `${formatPrice(item.costPerCm2)}/cm²`,
  })) : [
    {
      label: 'Materials',
      share: result.summary.materials_pct,
      value: `${formatPrice(toDisplay(result.materials.total_materials_cost_per_lb))}${fmtLabel}`,
    },
    {
      label: 'Processing',
      share: result.summary.processing_pct,
      value: `${formatPrice(toDisplay(Number(result.step_method.processing_cost_per_lb)))}${fmtLabel}`,
    },
    {
      label: 'Overhead + margin',
      share: Math.max(0, 100 - result.summary.materials_pct - result.summary.processing_pct),
      value: 'Included',
    },
  ];
  const sellingPriceShare = (costPerLb: number) => result.summary.estimated_price_per_lb > 0
    ? costPerLb / result.summary.estimated_price_per_lb * 100 : 0;
  const pieData = electrodeRows ? electrodeRows.map((item) => ({ name: item.label, value: item.share })) : [
    ...result.materials.components.map((component) => ({
      name:
        component.role === 'support'
          ? `${component.name} support`
          : component.role === 'promoter'
            ? `${component.name} promoter`
            : component.name,
      value: sellingPriceShare(component.cost_per_lb_cat),
    })),
    ...(result.materials.consumables ?? []).map((consumable) => ({
      name: consumable.name,
      value: sellingPriceShare(consumable.cost_per_lb_cat),
    })),
    { name: 'Processing', value: sellingPriceShare(Number(result.step_method.processing_cost_per_lb)) },
    { name: 'Overhead + margin', value: sellingPriceShare(Math.max(0,
      result.summary.estimated_price_per_lb - result.materials.total_materials_cost_per_lb
      - Number(result.step_method.processing_cost_per_lb))) },
  ];

  function renderCostingScope(detailed: boolean) {
    if (!costingScope) return null;
    const partial = costingScope.status === 'partial';
    const proxyCount = costingScope.costed_steps.filter((step) => step.status === 'proxy').length;
    const stepName = (key: string) => costingScope.costed_steps.find((step) => step.step === key)?.name ?? key.replace(/_/g, ' ');
    return (
      <div className={`mt-4 rounded-[20px] border p-4 ${partial ? 'border-amber-200 bg-amber-50/80 text-amber-950' : 'border-slate-200 bg-slate-50/80 text-slate-700'}`}>
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="cp-subtle-label">{t('Costing scope')}</div>
          <span className="cp-chip">{partial ? t('Partly costed') : costingScope.status === 'proxy' ? t('Includes proxy equipment') : t('Selected steps priced')}</span>
        </div>
        <p className="mt-2 text-sm leading-6"><ScientificText text={costingScope.boundary} /></p>
        {costingScope.area_cost_boundary ? <p className="mt-2 text-sm leading-6"><ScientificText text={costingScope.area_cost_boundary} /></p> : null}
        <div className="mt-2 flex flex-wrap gap-2 text-xs">
          <span>{t('Costed steps')}: {costingScope.costed_steps.length}</span>
          <span>{t('Proxy rates')}: {proxyCount}</span>
          <span>{t('Scale substitutions')}: {costingScope.substitutions.length}</span>
          <span>{t('Uncosted operations')}: {costingScope.uncosted_operations.length + costingScope.dropped_steps.length + costingScope.omitted_template_steps.length}</span>
        </div>
        {costingScope.route_modified ? <p className="mt-2 text-sm font-semibold">{t('Modified from the selected template')}. {t('The result uses the actual steps listed below; the template name is a reference.')}</p> : null}
        {detailed ? (
          <div className="mt-4 space-y-4">
            {costingScope.uncosted_operations.length ? <div>
              <div className="cp-subtle-label">{t('Uncosted operations')}</div>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm">{costingScope.uncosted_operations.map((operation, index) => <li key={index}><ScientificText text={operation} /></li>)}</ul>
            </div> : null}
            {costingScope.substitutions.length ? <div>
              <div className="cp-subtle-label">{t('Scale substitutions')}</div>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm">{costingScope.substitutions.map((entry, index) => <li key={index}><ScientificText text={stepName(entry.from)} /> → <ScientificText text={stepName(entry.to)} /></li>)}</ul>
            </div> : null}
            {costingScope.dropped_steps.length ? <p className="text-sm"><strong>{t('Unavailable at this scale')}:</strong> <ScientificText text={costingScope.dropped_steps.map(stepName).join(', ')} /></p> : null}
            {costingScope.omitted_template_steps.length ? <p className="text-sm"><strong>{t('Omitted template steps')}:</strong> <ScientificText text={costingScope.omitted_template_steps.map(stepName).join(', ')} /></p> : null}
            {costingScope.added_steps.length ? <p className="text-sm"><strong>{t('Added steps')}:</strong> <ScientificText text={costingScope.added_steps.map(stepName).join(', ')} /></p> : null}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead><tr className="border-b border-slate-200">
                  <th className="py-2 pr-3">{t('Actual costed steps')}</th>
                  <th className="py-2 pr-3">{t('Status')}</th>
                  <th className="py-2">{t('Source')}</th>
                </tr></thead>
                <tbody>{costingScope.costed_steps.map((entry, index) => <tr key={index} className="border-b border-slate-200/60 align-top">
                  <td className="py-2 pr-3"><ScientificText text={entry.name} /></td>
                  <td className="py-2 pr-3 whitespace-nowrap">{entry.status === 'proxy' ? t('Proxy rate') : t('Costed step')}</td>
                  <td className="py-2">{entry.reference_url ? <a href={entry.reference_url} target="_blank" rel="noreferrer" className="underline"><ScientificText text={entry.source} /></a> : entry.source}<div className="mt-1 text-slate-500"><ScientificText text={entry.basis} /></div></td>
                </tr>)}</tbody>
              </table>
            </div>
          </div>
        ) : null}
      </div>
    );
  }

  function renderResultOverview() {
    return (
      <section className="surface-card p-4">
        <div className="grid gap-3 xl:grid-cols-[minmax(0,1.15fr)_repeat(3,minmax(0,1fr))]">
          <div className="min-w-0 overflow-hidden rounded-[20px] border border-[#191f28] bg-[#191f28] p-4 text-white shadow-[0_8px_24px_rgba(15,23,42,0.18)]">
            <div className="cp-subtle-label !text-slate-400">{t('Final result')}</div>
            <div className="mt-2 text-sm text-slate-300"><ScientificText text={composition} /></div>
            <div className="mt-4 flex items-end gap-3">
              <FitPriceText
                size="xl"
                text={electrodeModel
                  ? formatPrice(electrodeModel.cost_per_cm2_usd)
                  : formatPrice(toDisplay(result.summary.estimated_price_per_lb))}
                className="min-w-0 text-white"
              />
              <div className="pb-1 text-base text-slate-300"><ScientificText text={electrodeModel ? '/cm²' : fmtLabel} /></div>
            </div>
            <div className="mt-2 text-xs leading-6 text-slate-300">
              {electrodeModel ? (
                lang === 'ko' ? (
                  <>유효 면적 cm²당 전극 조립체 원가입니다 (모델 면적 {electrodeModel.active_area_cm2.toFixed(1)} cm²). 질량 기준으로는 공급사 포장 단가 기준 {formatPrice(toDisplay(result.summary.estimated_price_per_lb))}{fmtLabel}입니다.</>
                ) : (
                  <>
                    {t("Electrode-stack cost per cm² of active area (")}{electrodeModel.active_area_cm2.toFixed(1)} {t("cm² modeled). Per-mass view")} {formatPrice(toDisplay(result.summary.estimated_price_per_lb))}
                    {fmtLabel} {t("on vendor-pack material prices.")}
                  </>
                )
              ) : (
                lang === 'ko' ? (
                  <>폐촉매 회수 가치를 뺀 순원가 {formatPrice(toDisplay(result.summary.net_cost_per_lb))}{fmtLabel}. 다른 단위로는 {formatPrice(altPrice)}<ScientificText text={altLabel} />.</>
                ) : (
                  <>
                    {t("Net cost")} {formatPrice(toDisplay(result.summary.net_cost_per_lb))}
                    {fmtLabel} {t('after recovery value, with selling margin included. Alternate view')} {formatPrice(altPrice)}
                    <ScientificText text={altLabel} />.
                  </>
                )
              )}
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              <span className="cp-chip-dark">{t(domainDisplay(catalystDomain))}</span>
              {!electrodeModel ? <span className="cp-chip-dark"><ScientificText text={lang === 'ko' ? t(result.step_method.scale) : `${result.step_method.scale} scale`} /></span> : null}
              <span className="cp-chip-dark"><ScientificText text={generatedAt} /></span>
            </div>
          </div>

          <div className="rounded-[22px] border border-slate-900/8 bg-white/62 p-4">
            <div className="cp-subtle-label">{t('Cost build-up')}</div>
            <div className="mt-3 space-y-1">
              {ledgerRows.map((row) => (
                <RailRow key={row.label} label={t(row.label)} value={row.value} detail={row.detail} />
              ))}
            </div>
          </div>

          <div className="rounded-[22px] border border-slate-900/8 bg-white/62 p-4">
            <div className="cp-subtle-label">{t('Evidence')}</div>
            <div className="mt-3 space-y-1">
              <RailRow
                label={t('Public links')}
                value={`${publicSourceCount}/${resolvedMaterials.length || 0}`}
                detail={electrodeModel ? t('Electrode material sources') : lang === 'ko' ? `실시간 ${snapshotState.liveFeedCount}건 / 지수 보정 ${snapshotState.indexedFeedCount}건` : `${snapshotState.liveFeedCount} live / ${snapshotState.indexedFeedCount} indexed rows in the draft`}
              />
              <RailRow
                label={t('Latest quote year')}
                value={latestQuoteYear ? String(latestQuoteYear) : 'N/A'}
                detail={lang === 'ko' ? `보관 자료 재료 ${historicalOnlyCount}건` : `${historicalOnlyCount} archive-only material rows`}
              />
              <RailRow
                label={t('Route references')}
                value={String(routeReferenceCount)}
                detail={routeReferenceCount ? t('Public route links stored') : t('No route link stored')}
              />
              {result.lca && result.lca.gwp_kg_co2eq_per_kg_catalyst != null ? (
                <RailRow
                  label={t("Cradle-to-gate GWP")}
                  value={`${formatLcaNumber(result.lca.gwp_kg_co2eq_per_kg_catalyst)} kg CO2-eq/kg`}
                  detail={`${result.lca.coverage_pct}% ${t('mass coverage / Nuss & Eckelman 2014')}`}
                />
              ) : null}
            </div>
          </div>

          <div className="rounded-[22px] border border-slate-900/8 bg-white/62 p-4">
            <div className="cp-subtle-label">{t('Preparation basis')}</div>
            <div className="mt-2 text-base font-semibold text-[#191f28]">
              <ScientificText text={routeSummary?.name ?? benchmarkCandidate?.route.name ?? t('Custom route')} />
            </div>
            {costingScope?.route_modified ? (
              <p className="mt-2 text-xs font-semibold text-amber-800">{t('Modified from the selected template')}</p>
            ) : null}
            <div className="mt-3 space-y-1">
              {electrodeModel ? <RailRow
                label={t('Active area')}
                value={`${electrodeModel.active_area_cm2.toFixed(1)} cm²`}
                detail={t('Per modeled layer')}
              /> : <RailRow
                label={t('Production scale')}
                value={lang === 'ko' ? `${snapshotState.orderSize}톤` : `${snapshotState.orderSize} tons`}
                detail={lang === 'ko' ? `${t(result.step_method.scale)} / ${Number(result.step_method.campaign_days).toFixed(1)}일` : `${result.step_method.scale} scale / ${Number(result.step_method.campaign_days).toFixed(1)} days`}
              />}
              <RailRow
                label={t('Steps')}
                value={String(snapshotState.stepLabels.length)}
                detail={snapshotState.stepLabels.length ? snapshotState.stepLabels.map((label) => t(label)).join(', ') : t('No step labels stored')}
              />
              <RailRow
                label={t('Mode')}
                value={routeSummary?.manufacturing_mode ? modeDisplay(routeSummary.manufacturing_mode) : t('Manual selection')}
                detail={t(applicationDisplay(routeSummary?.application_family ?? benchmarkCandidate?.application_family ?? catalystDomain))}
              />
              <RailRow
                label={t('Price basis')}
                value={result.input_summary.price_basis === 'reference' ? t('Academic (monthly averages)') : t('Practical (live quotes)')}
                detail={result.input_summary.price_basis === 'reference'
                  ? t('IMF PCPS and Johnson Matthey monthly averages; the latest published month prices the estimate.')
                  : t('Live quotes at the time of the estimate.')}
              />
            </div>
          </div>
        </div>
        {renderCostingScope(false)}
      </section>
    );
  }

  function renderSummarySection() {
    return (
      <section className="surface-card p-4">
        <div className="grid gap-3 xl:grid-cols-[minmax(0,1.18fr)_minmax(320px,0.82fr)]">
          <div className="surface-ink relative overflow-hidden p-5 sm:p-6">
            <div className="relative min-w-0">
              <div className="cp-subtle-label !text-slate-400">
                {electrodeModel ? t('Estimated electrode cost') : t('Estimated selling price')}
              </div>
              <div className="mt-2 text-sm text-slate-300"><ScientificText text={composition} /></div>
              <div className="mt-4 flex flex-wrap items-end gap-3">
                <FitPriceText
                  size="xl"
                  text={electrodeModel
                    ? formatPrice(electrodeModel.cost_per_cm2_usd)
                    : formatPrice(toDisplay(result.summary.estimated_price_per_lb))}
                  className="min-w-0 text-white"
                />
                <div className="pb-2 text-xl text-slate-300"><ScientificText text={electrodeModel ? '/cm²' : fmtLabel} /></div>
              </div>
              <div className="mt-3 text-sm text-slate-300">
                {electrodeModel ? (
                  lang === 'ko' ? (
                    <>유효 면적 cm²당 전극 조립체 원가입니다. 질량 기준으로는 공급사 포장 단가 기준 {formatPrice(toDisplay(result.summary.estimated_price_per_lb))}{fmtLabel}입니다.</>
                  ) : (
                    <>
                      {t("Electrode-stack cost per cm² of active area. Per-mass view")}{' '}
                      {formatPrice(toDisplay(result.summary.estimated_price_per_lb))}
                      {fmtLabel} {t("on vendor-pack material prices.")}
                    </>
                  )
                ) : (
                  lang === 'ko' ? (
                    <>폐촉매 회수 가치를 뺀 순원가 {formatPrice(toDisplay(result.summary.net_cost_per_lb))}{fmtLabel}.</>
                  ) : (
                    <>
                      {t("Net cost")} {formatPrice(toDisplay(result.summary.net_cost_per_lb))}
                      {fmtLabel} {t('after recovery value, with selling margin included.')}
                    </>
                  )
                )}
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                <span className="cp-chip-dark">{t(domainDisplay(catalystDomain))}</span>
                {!electrodeModel ? <span className="cp-chip-dark"><ScientificText text={lang === 'ko' ? t(result.step_method.scale) : `${result.step_method.scale} scale`} /></span> : null}
                <span className="cp-chip-dark"><ScientificText text={generatedAt} /></span>
                {benchmarkCandidate ? <span className="cp-chip-dark">{t('Reference-loaded')}</span> : null}
              </div>
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            {electrodeModel ? <>
              <MetricTile label={t('Active area')} value={`${electrodeModel.active_area_cm2.toFixed(1)} cm²`} detail={t('Per modeled layer')} />
              <MetricTile label={t('Electrode total')} value={formatPrice(electrodeModel.total_cost_usd)} detail={t('For selected active area')} />
            </> : <>
              <MetricTile label={t('Production time')} value={`${Number(result.step_method.campaign_days).toFixed(1)} d`} detail={lang === 'ko' ? `${snapshotState.orderSize}톤 1회 생산` : `${snapshotState.orderSize} tons per run`} />
              <MetricTile label={t('Margin')} value={`${Number(result.step_method.margin_pct).toFixed(1)}%`} detail={t('Selling margin basis')} />
            </>}
            <MetricTile label={t('Price sources')} value={String(electrodeModel ? resolvedMaterials.length : snapshotState.liveFeedCount + snapshotState.indexedFeedCount)} detail={electrodeModel ? t('Electrode material sources') : lang === 'ko' ? `실시간 ${snapshotState.liveFeedCount}건 / 지수 보정 ${snapshotState.indexedFeedCount}건` : `${snapshotState.liveFeedCount} live / ${snapshotState.indexedFeedCount} indexed`} />
            <MetricTile label={t('Public links')} value={`${publicSourceCount}/${resolvedMaterials.length || 0}`} detail={t('Resolved rows with a public URL.')} />
          </div>
        </div>

        {result.warnings?.length ? (
          <div className="mt-4 rounded-[24px] border border-amber-200 bg-amber-50/80 p-4 text-sm text-amber-900">
            <div className="cp-subtle-label !text-amber-700">{t('Model Scope')}</div>
            <div className="mt-2 space-y-2">
              {result.warnings.map((warning) => (
                <p key={warning} className="leading-6">
                  <ScientificText text={warning} />
                </p>
              ))}
            </div>
          </div>
        ) : null}

        {electrodeModel ? (
          <div className="mt-4 rounded-[24px] border border-slate-900/8 bg-white/58 p-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <div className="cp-subtle-label">{t('Electrode Assembly')}</div>
                <div className="cp-heading-sm mt-2">{t('Area-based electrocatalyst layer model')}</div>
                <div className="mt-1 text-xs leading-6 text-slate-600">
                  {t('Catalyst powder, ionomer, membrane, and substrate are costed on an active-area basis and displayed alongside the powder estimate.')}
                </div>
              </div>
              <span className="cp-chip">{t(applicationDisplay(electrodeModel.application_family))}</span>
            </div>

            <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              <MetricTile label={t('Active area')} value={`${electrodeModel.active_area_cm2.toFixed(1)} cm²`} detail={t('Per modeled layer')} />
              <MetricTile label={t('Catalyst loading')} value={`${electrodeModel.catalyst_loading_mg_cm2.toFixed(2)} mg/cm²`} detail={t('Dry catalyst loading')} />
              <MetricTile label={t('Electrode total')} value={formatPrice(electrodeModel.total_cost_usd)} detail={t('For selected active area')} />
              <MetricTile label={t('Cost per area')} value={`${formatPrice(electrodeModel.cost_per_cm2_usd)}/cm²`} detail={`${formatPrice(electrodeModel.cost_per_m2_usd)}/m²`} />
            </div>
            {electrodeModel.manufacturing ? (
              <div className="mt-4 rounded-[16px] border border-slate-200 bg-slate-50/80 p-4 text-xs leading-6 text-slate-600">
                <div className="cp-subtle-label">{t('Manufacturing line cost')}</div>
                <div className="mt-1">
                  <ScientificText text={electrodeModel.manufacturing.label} />: {formatPrice(electrodeModel.manufacturing_cost_usd ?? 0)} {t("added (")}{electrodeModel.manufacturing.usd_per_cm2.toFixed(4)} {t("$/cm² — equipment, labor, facility; consumables stay priced as materials). Derived from")} {electrodeModel.manufacturing.eur_per_m2.toFixed(1)} {t("€/m² at EUR→USD")} {electrodeModel.manufacturing.eur_to_usd}
                  {' '}(<ScientificText text={electrodeModel.manufacturing.fx_basis} />).{' '}
                  <a className="underline" href={electrodeModel.manufacturing.reference_url} target="_blank" rel="noreferrer">{t("Source")}</a>
                </div>
              </div>
            ) : null}
          </div>
        ) : null}

        {spentCatalyst ? (
          <div className="mt-4 rounded-[24px] border border-emerald-200 bg-emerald-50/80 p-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <div className="cp-subtle-label !text-emerald-700">{t('Recovery scenario')}</div>
                <div className="cp-heading-sm mt-2">{t('Spent catalyst value was included in the net-cost basis.')}</div>
                <div className="mt-1 text-xs leading-6 text-emerald-900">
                  {t('This is a simplified end-of-life recovery credit. It is useful for early screening, but it does not yet model deactivation kinetics or regeneration frequency.')}
                </div>
              </div>
              <span className="cp-chip"><ScientificText text={spentCatalyst.metal_symbol} /></span>
            </div>

            <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              <MetricTile
                label={t('Gross metal value')}
                value={formatPrice(toDisplay(spentCatalyst.V_metal_per_lb))}
                detail={lang === 'ko' ? `촉매 ${unit}당` : `Per${catLabel}`}
              />
              <MetricTile
                label={t('Recovery cost')}
                value={formatPrice(toDisplay(spentCatalyst.C_recovery_per_lb))}
                detail={lang === 'ko' ? `촉매 ${unit}당` : `Per${catLabel}`}
              />
              <MetricTile
                label={t('Reclaimed value')}
                value={formatPrice(toDisplay(spentCatalyst.V_reclaimed_per_lb))}
                detail={lang === 'ko' ? `촉매 ${unit}당` : `Per${catLabel}`}
              />
              <MetricTile
                label={t('Loss basis')}
                value={`${spentCatalyst.loss_use_pct.toFixed(1)}% / ${spentCatalyst.loss_refining_pct.toFixed(1)}%`}
                detail={t('Use loss / refining loss')}
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
            <div className="cp-subtle-label">{t('Preparation Method')}</div>
            <div className="cp-heading-lg mt-2">{t('Separate route logic from raw inputs.')}</div>
            <div className="mt-1 text-xs leading-6 text-slate-600">
              {t('This surface is for production scale, selected preparation steps, route metadata, and the main cost split.')}
            </div>
          </div>
          <span className="cp-chip"><ScientificText text={lang === 'ko' ? `재료 ${result.materials.components.length}종` : `${result.materials.components.length} material${result.materials.components.length === 1 ? '' : 's'}`} /></span>
        </div>

        <div className="mt-4 grid gap-2.5 sm:grid-cols-2">
          {electrodeModel ? (
            <>
              <MetricTile label={t('Catalyst powder')} value={resolvedMaterials.find((material) => material.used_for === 'electrode:catalyst_powder')?.name ?? composition} detail={t('Selected catalyst powder')} />
              <MetricTile label={t('Catalyst loading')} value={`${Number(electrodeModel.catalyst_loading_mg_cm2).toFixed(2)} mg/cm²`} detail={t('Dry catalyst loading')} />
              <MetricTile label={t('Active area')} value={`${Number(electrodeModel.active_area_cm2).toFixed(1)} cm²`} detail={t('Per modeled layer')} />
            </>
          ) : (
            <>
              <MetricTile label={t('Active metals')} value={String(snapshotState.activeMetalCount)} detail={t('Named active inputs')} />
              <MetricTile label={t('Active-phase loading')} value={`${snapshotState.nonSupportWt.toFixed(1)} wt%`} detail={lang === 'ko' ? `담체 ${snapshotState.supportWtPct.toFixed(1)} wt%` : `Support closes at ${snapshotState.supportWtPct.toFixed(1)} wt%`} />
              <MetricTile label={t('Support')} value={snapshotState.selectedSupportName ?? t('Pending')} detail={t('Current support basis')} />
            </>
          )}
          <MetricTile label={t('Preparation steps')} value={String(snapshotState.stepLabels.length)} detail={t('Selected preparation steps')} />
        </div>

        <div className="mt-4 grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(240px,0.88fr)]">
          <div className="rounded-[24px] border border-slate-900/8 bg-white/58 p-4">
            <div className="cp-subtle-label">{t('Cost Structure')}</div>
            <div className="cp-heading-lg mt-2">{electrodeModel ? t('Electrode Assembly') : t('Materials versus processing')}</div>
            <div className="mt-4 space-y-3">
              {summaryRows.map((item, index) => (
                <div key={item.label}>
                  <div className="flex items-center justify-between gap-3 text-sm">
                    <span className="text-slate-600">{t(item.label)}</span>
                    <span className="font-semibold text-[#191f28]"><ScientificText text={item.value === 'Included' ? t('Included') : item.value} /></span>
                  </div>
                  <div className="mt-2 h-2 rounded-full bg-slate-200/80">
                    <div
                      className="h-full rounded-full"
                      style={{ width: `${Math.max(item.share, 4)}%`, backgroundColor: CHART_COLORS[index] }}
                    />
                  </div>
                  <div className="mt-1 text-xs text-slate-600">{lang === 'ko' ? `비중 ${item.share.toFixed(1)}%` : `${item.share.toFixed(1)}% share`}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[24px] border border-slate-900/8 bg-white/58 p-4">
            <div className="cp-heading-sm">{t('Cost breakdown')}</div>
            <div className="mt-1 text-xs text-slate-600">{electrodeModel ? t('For selected active area') : t('Materials, processing, and selling adjustments.')}</div>
            <div className="mt-4 h-[240px]">
              <Suspense fallback={<ChartFallback />}>
                <ResultBreakdownPieChart data={pieData} colors={CHART_COLORS} />
              </Suspense>
            </div>
            <div className="mt-2 grid gap-2 sm:grid-cols-2">
              {pieData.map((entry, index) => (
                <div key={entry.name} className="flex items-center gap-2 text-sm text-slate-600">
                  <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: CHART_COLORS[index % CHART_COLORS.length] }} />
                  {t(entry.name)}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-4 rounded-[24px] border border-slate-900/8 bg-white/58 p-4">
          <div className="cp-subtle-label">{t('Preparation Steps')}</div>
          <div className="mt-3 flex flex-wrap gap-2">
            {snapshotState.stepLabels.map((label) => (
              <span key={label} className="cp-chip">
                {t(label)}
              </span>
            ))}
          </div>
        </div>

        {benchmarkCandidate ? (
          <div className="mt-4 rounded-[24px] border border-emerald-200 bg-emerald-50/80 p-4">
            <div className="cp-subtle-label !text-emerald-700">{t('Reference baseline')}</div>
            <div className="mt-2 cp-heading-sm"><ScientificText text={benchmarkCandidate.title} /></div>
            <div className="mt-2 text-sm leading-6 text-emerald-900"><ScientificText text={benchmarkCandidate.screening_summary} /></div>
            <div className="mt-3 flex flex-wrap gap-2">
              <span className="cp-chip"><ScientificText text={benchmarkCandidate.archetype} /></span>
              <span className="cp-chip"><ScientificText text={benchmarkCandidate.route.name} /></span>
              <span className="cp-chip">
                {t(benchmarkCandidate.catalyst_domain === 'electrocatalyst' ? 'Electrocatalyst' : 'Thermocatalyst')}
              </span>
              <span className="cp-chip">{t('Price evidence')} {benchmarkCandidate.scores.evidence.toFixed(1)}</span>
            </div>
          </div>
        ) : null}

        {renderCostingScope(true)}
        <PracticalCostingResult result={result} />

        {routeSummary ? (
          <div className="mt-4 rounded-[24px] border border-sky-200 bg-sky-50/75 p-4">
            <div className="cp-subtle-label !text-sky-700">{t('Preparation method')}</div>
            <div className="mt-2 cp-heading-sm"><ScientificText text={routeSummary.name} /></div>
            {costingScope?.route_modified ? <p className="mt-2 text-sm font-semibold text-amber-800">{t('Modified from the selected template')}</p> : null}
            <div className="mt-2 text-sm leading-6 text-sky-900">
              <ScientificText text={routeSummary.route_note || t('The route template details are attached to this estimate.')} />
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              <span className="cp-chip"><ScientificText text={modeDisplay(routeSummary.manufacturing_mode)} /></span>
              <span className="cp-chip">{t(applicationDisplay(routeSummary.application_family))}</span>
            </div>
            <div className="mt-4 grid gap-3 lg:grid-cols-3">
              <div>
                <div className="cp-subtle-label !text-sky-700">{t('Pre-treatment')}</div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {routeSummary.preprocess.map((item) => (
                    <span key={item} className="cp-chip">
                      <ScientificText text={item} />
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <div className="cp-subtle-label !text-sky-700">{t('Synthesis')}</div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {routeSummary.synthesis.map((item) => (
                    <span key={item} className="cp-chip">
                      <ScientificText text={item} />
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <div className="cp-subtle-label !text-sky-700">{t('Post-treatment')}</div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {routeSummary.postprocess.map((item) => (
                    <span key={item} className="cp-chip">
                      <ScientificText text={item} />
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : null}

        {spentCatalyst ? (
          <div className="mt-4 rounded-[24px] border border-emerald-200 bg-emerald-50/80 p-4">
            <div className="cp-subtle-label !text-emerald-700">{t("Lifecycle proxy")}</div>
            <div className="mt-2 text-sm leading-6 text-emerald-900">
              {t("Net cost includes spent catalyst recovery for")} <ScientificText text={spentCatalyst.metal_symbol} />{t(". The model uses support and reactor-type loss assumptions from the CatCost-style recovery proxy, not a full deactivation-regeneration cycle.")}
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
          <div className="cp-subtle-label">{t('Environmental')}</div>
          <div className="cp-heading-lg mt-2">{t('No LCA data attached to this estimate.')}</div>
          <div className="mt-2 text-xs leading-6 text-slate-600">
            {t('Re-run the estimate to compute cradle-to-gate impact.')}
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
            <div className="cp-subtle-label">{t('Environmental')}</div>
            <div className="cp-heading-lg mt-2">{t('Cradle-to-gate impact per kg of catalyst')}</div>
            <div className="mt-1 text-xs leading-6 text-slate-600">
              {t('Weighted-average over the wt% composition. Manufacturing-step emissions are not included in this version — only embodied material impact.')}
            </div>
          </div>
          <span className={`cp-chip shrink-0 ${dataGap > 0 ? 'border-amber-200 bg-amber-50 text-amber-700' : 'border-emerald-200 bg-emerald-50 text-emerald-700'}`}>
            <ScientificText text={lang === 'ko' ? `반영률 ${coverage}%` : `${coverage}% covered`} />
          </span>
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <MetricTile
            label={t("GWP (100a)")}
            value={`${formatLcaNumber(gwp)} kg`}
            detail={t('kg CO2-eq per kg of finished catalyst (IPCC GWP100a).')}
          />
          <MetricTile
            label={t('Cumulative energy demand')}
            value={`${formatLcaNumber(ced)} MJ`}
            detail={t('Total primary energy per kg of finished catalyst.')}
          />
          <MetricTile
            label={t('Composition coverage')}
            value={`${coverage}%`}
            detail={dataGap > 0 ? (lang === 'ko' ? `질량의 ${dataGap}%에 검증된 계수가 없습니다.` : `${dataGap}% of mass has no verified factor.`) : t('Every component has a verified factor.')}
          />
          <MetricTile
            label={t('Data source')}
            value="Nuss & Eckelman 2014"
            detail="PLOS ONE 9(7): e101298 — CC BY 4.0."
          />
        </div>

        {lca.warnings.length > 0 ? (
          <div className="mt-4 rounded-[18px] border border-amber-200 bg-amber-50 px-4 py-3 text-sm leading-6 text-amber-900" role="status">
            <div className="font-semibold">{t('LCA notes')}</div>
            <ul className="mt-2 list-disc space-y-1 pl-5">
              {lca.warnings.map((warning, idx) => (
                <li key={idx}><ScientificText text={warning} /></li>
              ))}
            </ul>
          </div>
        ) : null}

        <div className="mt-5 overflow-hidden rounded-[24px] border border-slate-200">
          <table className="min-w-full text-left text-xs leading-6">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-3 py-2 font-semibold">{t('Component')}</th>
                <th className="px-3 py-2 font-semibold">{t('Role')}</th>
                <th className="px-3 py-2 font-semibold">wt%</th>
                <th className="px-3 py-2 font-semibold">{t('Status')}</th>
                <th className="px-3 py-2 font-semibold text-right">{t("GWP (kg CO2-eq/kg cat)")}</th>
                <th className="px-3 py-2 font-semibold text-right">{t("CED (MJ/kg cat)")}</th>
              </tr>
            </thead>
            <tbody>
              {lca.per_component.map((entry, idx) => (
                <tr key={`${entry.name}-${idx}`} className="border-t border-slate-100">
                  <td className="px-3 py-2 font-semibold text-slate-900">
                    <ScientificText text={entry.name} />
                    {entry.matched_key && entry.matched_key !== entry.name ? (
                      <span className="ml-1 text-xs text-slate-600">{t("(via")} <ScientificText text={entry.matched_key} />)</span>
                    ) : null}
                  </td>
                  <td className="px-3 py-2 text-slate-600"><ScientificText text={entry.role ?? '—'} /></td>
                  <td className="px-3 py-2 text-slate-600">{entry.wt_pct.toFixed(2)}</td>
                  <td className="px-3 py-2">
                    <span className={`inline-flex rounded-full border px-2 py-0.5 text-xs font-semibold uppercase tracking-[0.16em] ${lcaFactorStatusTone(entry.factor_status)}`}>
                      <ScientificText text={lcaFactorStatusLabel(entry.factor_status)} />
                    </span>
                  </td>
                  <td className="px-3 py-2 text-right font-mono text-slate-900">
                    <ScientificText text={entry.gwp_contribution_kg_co2eq_per_kg_catalyst != null
                      ? formatLcaNumber(entry.gwp_contribution_kg_co2eq_per_kg_catalyst)
                      : '—'} />
                  </td>
                  <td className="px-3 py-2 text-right font-mono text-slate-900">
                    <ScientificText text={entry.ced_contribution_mj_per_kg_catalyst != null
                      ? formatLcaNumber(entry.ced_contribution_mj_per_kg_catalyst)
                      : '—'} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-5 rounded-[20px] border border-slate-200 bg-white/72 p-4">
          <div className="cp-subtle-label">{t('Reference')}</div>
          <div className="mt-2 text-sm font-semibold text-slate-900"><ScientificText text={ref.citation} /></div>
          <div className="mt-1 text-xs leading-6 text-slate-600">
            <ScientificText text={ref.table_of_origin} />{t(". Underlying LCI:")} <ScientificText text={ref.underlying_lci_database} />{t(". Uncertainty:")} <ScientificText text={ref.uncertainty_basis} />{t(". License:")} <ScientificText text={ref.license} />.
          </div>
          <div className="mt-2 text-xs">
            <a href={ref.url} target="_blank" rel="noreferrer" className="text-[#0f766e] underline-offset-4 hover:underline">
              {t('Open the source paper')} (DOI <ScientificText text={ref.doi} />)
            </a>
          </div>
          <div className="mt-3 text-xs leading-6 text-slate-600"><ScientificText text={ref.notes} /></div>
        </div>
      </section>
    );
  }

  function renderSourcesSection() {
    return (
      <section className="surface-card p-4">
        <div className="flex min-w-0 flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div className="min-w-0">
            <div className="cp-subtle-label">{t('Evidence')}</div>
            <div className="cp-heading-lg mt-2">{t('Resolved material sources and normalization')}</div>
            <div className="mt-1 text-xs leading-6 text-slate-600">
              {t('Each record shows raw quote, pack basis, normalization basis, and public link status when available.')}
            </div>
          </div>
          <span className="cp-chip shrink-0"><ScientificText text={snapshotState.selectedSupportName ?? 'Support'} /></span>
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <MetricTile
            label={t('Resolved rows')}
            value={String(resolvedMaterials.length)}
            detail={t('Material source rows used during estimate resolution.')}
          />
          <MetricTile label={t('Public links')} value={String(publicSourceCount)} detail={t('Rows that open a public source page.')} />
          <MetricTile
            label={t('Archive-only')}
            value={String(historicalOnlyCount)}
            detail={t('Historical rows without a stable public URL.')}
          />
          <MetricTile
            label={t('Route references')}
            value={String(routeReferenceCount)}
            detail={latestQuoteYear ? (lang === 'ko' ? `최신 견적 연도 ${latestQuoteYear}` : `Latest quote year ${latestQuoteYear}`) : t('No quote year stored')}
          />
        </div>

        <div className="mt-4 grid gap-3 xl:grid-cols-2">
          {result.materials.components.map((component, index) => (
            <div key={`${component.name}-${component.role}`} className="rounded-[24px] border border-slate-900/8 bg-white/58 p-4">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div className="min-w-0">
                  <div className="flex items-center gap-2.5">
                    <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: CHART_COLORS[index % CHART_COLORS.length] }} />
                    <div className="cp-heading-sm"><ScientificText text={component.name} /></div>
                  </div>
                  <div className="mt-1 text-xs uppercase tracking-[0.18em] text-slate-400">
                    <ScientificText text={component.role.replace('_', ' ')} />
                  </div>
                </div>
                <div className="text-left sm:text-right">
                  <div className="cp-subtle-label">{t('Per catalyst')}</div>
                  <div className="mt-2 font-display text-[1.45rem] text-[#191f28]">
                    {formatPrice(toDisplay(component.cost_per_lb_cat))}
                    <ScientificText text={catLabel} />
                  </div>
                </div>
              </div>

              <div className="mt-4 grid gap-2.5 sm:grid-cols-3 xl:grid-cols-1 2xl:grid-cols-3">
                <MetricTile label="wt%" value={(component.wt_frac * 100).toFixed(1)} detail={t('Loaded into catalyst')} />
                <MetricTile label={component.recipe_consumption ? t('Purchased precursor unit price') : t('Unit price')} value={formatPrice(toDisplay(component.recipe_consumption ? component.recipe_consumption.price_per_kg / LB_PER_KG : component.price_per_lb))} detail={`${t('Per unit mass')} (${unit})`} />
                <MetricTile label={t('Share')} value={`${Number(component.cost_pct).toFixed(1)}%`} detail={t('Of material cost')} />
              </div>
              {component.recipe_consumption ? <p className="mt-3 text-xs leading-6 text-slate-600">
                {t('Recipe purchase price replaces the component price in material cost. Reference component price:')} {formatPrice(toDisplay(component.price_per_lb))}{fmtLabel}.
              </p> : null}
            </div>
          ))}
        </div>

        <div className="mt-4 rounded-[22px] border border-slate-900/8 bg-white/60 p-4">
          <div className="flex items-center justify-between gap-3 text-sm">
            <span className="text-slate-600">{t('Total material cost')}</span>
            <span className="font-semibold text-[#191f28]">
              {formatPrice(toDisplay(result.materials.total_materials_cost_per_lb))}
              <ScientificText text={catLabel} />
            </span>
          </div>
          <div className="mt-2 text-xs leading-6 text-slate-600">
            {t('CatCost Step Method rates, brought to this year with the chemical price index, plus overhead and selling margin.')}
          </div>
        </div>

        {resolvedMaterials.length === 0 ? (
          <div className="mt-4 rounded-[22px] border border-slate-900/8 bg-white/60 p-4">
            <div className="cp-subtle-label">{t('Source Records')}</div>
            <div className="mt-3 text-sm leading-6 text-slate-600">
              {t('No resolved source rows — this estimate ran on manual price entries. Pick library materials in the cost estimate workspace to populate per-row provenance.')}
            </div>
          </div>
        ) : (
          <div className="mt-4 rounded-[22px] border border-slate-900/8 bg-white/60 p-4">
            <div className="cp-subtle-label">{t('Source Records')}</div>
            <div className="mt-3 grid gap-3">
              {resolvedMaterials.map((material) => (
                <div key={`${material.used_for}-${material.material_key}`} className="rounded-[18px] border border-slate-200 bg-white px-4 py-3">
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                    <div className="min-w-0">
                      <div className="font-semibold text-[#191f28]"><ScientificText text={material.name} /></div>
                      <div className="mt-1 text-xs text-slate-600">
                        <ScientificText text={material.used_for} /> / <ScientificText text={material.price_scope} /> / <ScientificText text={material.pricing_basis} />
                      </div>
                    </div>
                    <div className="text-left sm:text-right">
                      <div className="font-mono text-slate-900">
                        {formatPrice(material.price)} <ScientificText text={material.price_unit} />
                      </div>
                      {material.normalized_price_per_lb != null && material.price_unit !== `$${fmtLabel}` ? (
                        <div className="mt-0.5 font-mono text-xs text-slate-600">
                          ≈ {formatPrice(toDisplay(material.normalized_price_per_lb))}{fmtLabel} {recipeReferenceKeys.has(material.material_key) ? t('reference price only') : t('in calculator')}
                        </div>
                      ) : null}
                      <div className="mt-1 text-xs text-slate-600">
                        <ScientificText text={material.quote_source} />
                        <ScientificText text={material.quote_year ? ` / ${material.quote_year}` : ''} />
                      </div>
                      <div className="mt-2 flex flex-wrap items-center gap-2 sm:justify-end">
                        <span
                          className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold uppercase tracking-[0.16em] ${sourceRecordTone(material.price_scope, Boolean(material.reference_url))}`}
                        >
                          {t(sourceRecordLabel(material.price_scope, Boolean(material.reference_url)))}
                        </span>
                        {material.reference_url ? (
                          <a
                            href={material.reference_url}
                            target="_blank"
                            rel="noreferrer"
                            className="text-xs font-semibold text-[#0f766e] underline underline-offset-2"
                          >
                            {t('Open source')} ↗
                          </a>
                        ) : null}
                      </div>
                    </div>
                  </div>
                  {recipeReferenceKeys.has(material.material_key) ? <p className="mt-3 rounded-lg bg-amber-50 p-3 text-xs leading-6 text-amber-900">
                    {t('This library quote is retained as a reference. The purchased-precursor recipe supplies the price used for this component cost.')}
                  </p> : null}
                  <div className="mt-3 grid gap-2.5 sm:grid-cols-3">
                    <div className="rounded-[16px] border border-slate-200 bg-slate-50/80 px-3 py-2.5">
                      <div className="cp-subtle-label">{t('Pack Basis')}</div>
                      <div className="mt-1 text-sm font-semibold text-slate-900"><ScientificText text={formatResolvedPack(material)} /></div>
                    </div>
                    <div className="rounded-[16px] border border-slate-200 bg-slate-50/80 px-3 py-2.5">
                      <div className="cp-subtle-label">{t('Normalization')}</div>
                      <div className="mt-1 text-sm font-semibold text-slate-900">
                        <ScientificText text={formatResolvedNormalization(material, toDisplay, fmtLabel)} />
                      </div>
                    </div>
                    <div className="rounded-[16px] border border-slate-200 bg-slate-50/80 px-3 py-2.5">
                      <div className="cp-subtle-label">{t('Pricing Basis')}</div>
                      <div className="mt-1 text-sm font-semibold text-slate-900">
                        <ScientificText text={material.pricing_basis.replace(/_/g, ' ')} />
                      </div>
                    </div>
                  </div>
                  {!recipeReferenceKeys.has(material.material_key) && material.escalation_factor != null && material.escalation_factor !== 1 && material.escalation_basis_year ? (
                    <div className="mt-3 rounded-[14px] border border-[#7950f2] bg-[#f3edff] px-3 py-2.5 text-xs leading-5 text-[#4d2eb5]">
                      <div className="font-bold uppercase tracking-[0.16em] text-[#4d2eb5]">
                        {t("Inflated to")} {material.escalation_target_year ?? new Date().getFullYear()} {t("basis")}
                      </div>
                      <div className="mt-1 text-[#191f28]">
                        {t("Original")} {material.escalation_basis_year} {t("quote of")}{' '}
                        <span className="font-mono font-semibold">{formatPrice(toDisplay(material.raw_price_per_lb ?? material.price))}{fmtLabel}</span>{' '}
                        {t("is multiplied by ChemPPI factor")}{' '}
                        <span className="font-mono font-semibold">×{material.escalation_factor.toFixed(2)}</span>{' '}
                        {t("to land at the in-calculator value")}{' '}
                        <span className="font-mono font-semibold">{formatPrice(toDisplay(material.normalized_price_per_lb ?? 0))}{fmtLabel}</span>.
                      </div>
                      <div className="mt-1 text-[#4e5968]">
                        {t("ChemPPI tracks chemical-manufacturing producer prices and is the same index CatCost uses for materials and operating costs.")}
                      </div>
                    </div>
                  ) : null}
                  {!recipeReferenceKeys.has(material.material_key) && material.live_override?.applied ? (
                    <div className="mt-3 rounded-[14px] border border-[#0d9488] bg-[#e6f5f2] px-3 py-2.5 text-xs leading-5 text-[#115e59]">
                      <div className="font-bold uppercase tracking-[0.16em] text-[#0f766e]">
                        {material.live_override.basis === 'reference' ? t('Monthly reference quote in use') : t('Live market quote in use')}
                      </div>
                      <div className="mt-1 text-[#191f28]">
                        {t("Catalyst price uses the latest")} <span className="font-semibold"><ScientificText text={material.live_override.live_source} /></span> {t("quote of")} <span className="font-mono font-semibold">{formatPrice(material.live_override.live_price)} <ScientificText text={material.live_override.live_price_unit} /></span>
                        {(() => {
                          const perLb = quotePerLb(material.live_override.live_price, material.live_override.live_price_unit);
                          return perLb != null && material.live_override.live_price_unit !== `$${fmtLabel}`
                            ? <> (≈ <span className="font-mono font-semibold">{formatPrice(toDisplay(perLb))}{fmtLabel}</span>)</>
                            : null;
                        })()}
                        {material.live_override.live_fetched_at
                          ? material.live_override.basis === 'reference'
                            ? ` (${t('Observation month')} ${material.live_override.live_fetched_at.slice(0, 7)})`
                            : ` (${t('Fetched')} ${new Date(material.live_override.live_fetched_at).toLocaleString(lang === 'ko' ? 'ko-KR' : 'en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })})`
                          : ''}
                        .
                      </div>
                      <div className="mt-1 text-[#4e5968]">
                        {t('Original library price:')} <span className="font-mono">{formatPrice(material.live_override.fallback_price)} <ScientificText text={material.live_override.fallback_price_unit} /></span> {t("from")} <ScientificText text={material.live_override.fallback_source} />
                        <ScientificText text={material.live_override.fallback_quote_year ? ` (${material.live_override.fallback_quote_year})` : ''} />
                        .
                        {material.live_override.fallback_reference_url ? (
                          <> <a href={material.live_override.fallback_reference_url} target="_blank" rel="noreferrer" className="underline underline-offset-2">{t('Open original library source')} ↗</a></>
                        ) : null}
                      </div>
                    </div>
                  ) : !recipeReferenceKeys.has(material.material_key) && material.live_override && material.live_override.applied === false ? (
                    <div className="mt-3 rounded-[14px] border border-[#ffa800] bg-[#fff4dd] px-3 py-2.5 text-xs leading-5 text-[#7a5a00]">
                      <span className="font-bold uppercase tracking-[0.16em]">{t("No live quote")}</span>
                      <span className="ml-2">
                        {t("This metal can carry a live market quote, but none is stored. Using the static catalog price. Refresh the prices feed to populate.")}
                      </span>
                    </div>
                  ) : null}
                  {!material.reference_url ? (
                    <div className="mt-2 text-xs leading-5 text-slate-600">
                      {material.price_scope === 'historical_bulk'
                        ? t('Historical bulk row without a stable public permalink.')
                        : t('No public source URL stored for this row.')}
                    </div>
                  ) : null}
                </div>
              ))}
            </div>
          </div>
        )}

        {routeSummary?.reference_urls?.length ? (
          <div className="mt-4 rounded-[22px] border border-slate-900/8 bg-white/60 p-4">
            <div className="cp-subtle-label">{t("Route References")}</div>
            <div className="mt-3 flex flex-wrap gap-2">
              {routeSummary.reference_urls.map((url) => (
                <a key={url} href={url} target="_blank" rel="noreferrer" className="cp-button-secondary px-3 py-2 text-xs">
                  {t("Open route reference")}
                </a>
              ))}
            </div>
          </div>
        ) : null}
      </section>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <section className="surface-card cp-enter overflow-hidden p-5 sm:p-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="cp-heading-xl">{t('Result')}</h1>
            <p className="cp-body-copy mt-1.5 max-w-2xl">
              {t('The estimate, route basis, and evidence in one place — grouped for reading, separate from the editing workspace.')}
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            {snapshotState.costInput ? (
              <div className="flex items-center gap-2">
                <input
                  value={saveName}
                  onChange={(event) => { setSaveName(event.target.value); if (saveState !== 'idle') setSaveState('idle'); }}
                  placeholder={t('Estimate name')}
                  className="input-base w-44 px-3 py-2 text-sm"
                />
                <button
                  onClick={() => void handleSaveEstimate()}
                  disabled={saveState === 'saving'}
                  className="cp-button-secondary px-4 py-2"
                >
                  {saveState === 'saving' ? t('Saving…') : saveState === 'saved' ? t('Saved ✓') : saveState === 'failed' ? t('Retry save') : t('Save estimate')}
                </button>
              </div>
            ) : null}
            <button
              onClick={() => downloadCsv(resultCsvFilename(snapshotState), buildResultCsv(snapshotState))}
              className="cp-button-secondary px-4 py-2"
            >
              {t('Export CSV')}
            </button>
            <button onClick={goBackToCalculator} className="cp-button-primary">
              {t('Back to cost estimate')}
            </button>
          </div>
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
      {sectionState.activeSection.id === 'sources' ? <CostEvidencePanel savedEstimateId={snapshotState.savedEstimateId ?? null} /> : null}

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
