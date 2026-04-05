import { useLayoutEffect, useState } from 'react';
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import { useNavigate } from 'react-router-dom';
import { loadCalculatorResultSnapshot } from '../lib/calculator-session';
import { useUnit } from '../lib/use-unit';

const CHART_COLORS = ['#78f2d0', '#88a8ff', '#efc36c', '#f3a08d', '#c5b7ff', '#8de0ff'];

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

function MetricTile({ label, value, detail, dark = false }: { label: string; value: string; detail: string; dark?: boolean }) {
  return (
    <div className={dark ? 'cp-metric-tile-dark' : 'cp-metric-tile'}>
      <div className={`cp-subtle-label ${dark ? '!text-slate-400' : ''}`}>{label}</div>
      <div className={`mt-2 text-2xl font-display ${dark ? 'text-white' : 'text-slate-900'}`}>{value}</div>
      <div className={`mt-1 text-xs leading-5 ${dark ? 'text-slate-400' : 'text-slate-500'}`}>{detail}</div>
    </div>
  );
}

export default function CalculatorResult() {
  const navigate = useNavigate();
  const { unit, toDisplay, fmtLabel, catLabel } = useUnit();
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
        <span className="section-kicker">Estimate Board</span>
        <h1 className="cp-heading-xl mt-4">No saved estimate board is available yet.</h1>
        <p className="cp-body-copy mt-3 max-w-xl">Run an estimate from the build workspace first. The estimate board will then stay available for quick review.</p>
        <div className="mt-5">
          <button onClick={goBackToCalculator} className="cp-button-primary">Back to build</button>
        </div>
      </section>
    );
  }

  const { result } = snapshot;
  const altPrice = unit === 'kg' ? result.summary.estimated_price_per_lb : result.summary.estimated_price_per_kg;
  const altLabel = unit === 'kg' ? '/lb' : '/kg';
  const generatedAt = new Date(snapshot.generatedAt).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', hour12: true });
  const composition = typeof result.input_summary.composition === 'string' ? result.input_summary.composition : 'Catalyst estimate';
  const catalystDomain = result.input_summary.catalyst_domain === 'electrocatalyst' ? 'Electrocatalyst' : 'Thermocatalyst';
  const routeSummary = result.route_summary ?? null;
  const electrodeModel = result.electrode_model ?? null;
  const resolvedMaterials = result.resolved_materials ?? [];
  const summaryRows = [
    { label: 'Materials', share: result.summary.materials_pct, value: `$${toDisplay(result.materials.total_materials_cost_per_lb).toFixed(3)}${fmtLabel}` },
    { label: 'Processing', share: result.summary.processing_pct, value: `$${toDisplay(Number(result.step_method.processing_cost_per_lb)).toFixed(3)}${fmtLabel}` },
    { label: 'G&A + margin', share: Math.max(0, 100 - result.summary.materials_pct - result.summary.processing_pct), value: 'Included' },
  ];
  const pieData = [
    ...result.materials.components.map((component) => ({ name: component.role === 'support' ? `${component.name} support` : component.role === 'promoter' ? `${component.name} promoter` : component.name, value: component.cost_pct })),
    { name: 'Processing', value: result.summary.processing_pct },
    { name: 'G&A + margin', value: Math.max(0, 100 - result.summary.materials_pct - result.summary.processing_pct) },
  ];

  return (
    <div className="space-y-4">
      <section className="surface-card cp-enter overflow-hidden p-5 sm:p-6">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
          <div className="max-w-3xl">
            <span className="section-kicker">Estimate Board</span>
            <h1 className="cp-heading-xl mt-4">Read the estimate on a dedicated board.</h1>
            <p className="cp-body-copy mt-3 max-w-2xl">Inputs stay in the build workspace. This board is for reading cost, route, and source evidence without editing noise.</p>
          </div>
          <button onClick={goBackToCalculator} className="cp-button-primary">Back to build</button>
        </div>

        <div className="mt-5 grid gap-4 xl:grid-cols-[minmax(0,1.18fr)_minmax(340px,0.82fr)]">
          <div className="surface-ink relative overflow-hidden p-5 sm:p-6">
            <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(120,242,208,0.22),transparent_0_34%),radial-gradient(circle_at_bottom_right,rgba(239,195,108,0.12),transparent_0_28%)]" />
            <div className="relative">
              <div className="cp-subtle-label !text-slate-400">Estimated selling price</div>
              <div className="mt-2 text-sm text-slate-300">{composition}</div>
              <div className="mt-4 flex flex-wrap items-end gap-3">
                <div className="font-display text-[clamp(3rem,6vw,5.3rem)] leading-none text-white">${toDisplay(result.summary.estimated_price_per_lb).toFixed(2)}</div>
                <div className="pb-2 text-xl text-slate-300">{fmtLabel}</div>
              </div>
              <div className="mt-3 text-sm text-slate-300">Alternate view: ${altPrice.toFixed(2)}{altLabel}</div>
              <div className="mt-5 flex flex-wrap gap-2">
                <span className="cp-chip-dark">Generated {generatedAt}</span>
                <span className="cp-chip-dark">{catalystDomain}</span>
                <span className="cp-chip-dark">{snapshot.selectedSupportName ?? 'Support pending'}</span>
                <span className="cp-chip-dark">{snapshot.stepLabels.length} process steps</span>
                {snapshot.benchmarkCandidate ? <span className="cp-chip-dark">{snapshot.benchmarkCandidate.title}</span> : null}
              </div>
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <MetricTile label="Scale" value={result.step_method.scale} detail={`${snapshot.orderSize} tons per order`} />
            <MetricTile label="Campaign" value={`${Number(result.step_method.campaign_days).toFixed(1)} d`} detail={`${snapshot.stepLabels.length} selected steps`} />
            <MetricTile label="Margin" value={`${Number(result.step_method.margin_pct).toFixed(1)}%`} detail="Selling margin contribution" />
            <MetricTile label="Tracked feeds" value={String(snapshot.liveFeedCount + snapshot.indexedFeedCount)} detail={`${snapshot.liveFeedCount} live / ${snapshot.indexedFeedCount} indexed`} />
          </div>
        </div>
      </section>

      {result.warnings?.length ? (
        <section className="surface-card border border-amber-200 bg-amber-50/70 p-4 text-sm text-amber-900">
          <div className="cp-subtle-label !text-amber-700">Model Scope</div>
          <div className="mt-2 space-y-2">
            {result.warnings.map((warning) => (
              <p key={warning} className="leading-6">{warning}</p>
            ))}
          </div>
        </section>
      ) : null}

      {electrodeModel ? (
        <section className="surface-card p-4">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <div className="cp-subtle-label">Electrode Stack</div>
              <div className="cp-heading-lg mt-2">Area-based electrocatalyst cost model</div>
              <div className="mt-1 text-xs leading-6 text-slate-500">
                Catalyst powder, ionomer, membrane, and substrate are costed on an active-area basis and shown alongside the CatCost powder estimate.
              </div>
            </div>
            <span className="cp-chip">{electrodeModel.application_family}</span>
          </div>

          <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <MetricTile label="Active area" value={`${electrodeModel.active_area_cm2.toFixed(1)} cm2`} detail="Per modeled electrode / CCM" />
            <MetricTile label="Catalyst loading" value={`${electrodeModel.catalyst_loading_mg_cm2.toFixed(2)} mg/cm2`} detail="Dry catalyst powder loading" />
            <MetricTile label="Electrode total" value={`$${electrodeModel.total_cost_usd.toFixed(2)}`} detail="For selected active area" />
            <MetricTile label="Stack cost density" value={`$${electrodeModel.cost_per_cm2_usd.toFixed(3)}/cm2`} detail={`$${electrodeModel.cost_per_m2_usd.toFixed(2)}/m2`} />
          </div>

          <div className="mt-4 grid gap-3 xl:grid-cols-4">
            {electrodeModel.breakdown.map((item) => (
              <div key={item.label} className="rounded-[22px] border border-slate-900/8 bg-white/60 p-4">
                <div className="cp-subtle-label">{item.label}</div>
                <div className="mt-2 font-display text-[1.6rem] text-slate-950">${item.cost_usd.toFixed(3)}</div>
                <div className="mt-1 text-xs leading-6 text-slate-500">
                  {item.label === 'Ionomer' ? `Pricing mode: ${electrodeModel.ionomer_pricing_mode}` : 'Included in active-area model'}
                </div>
              </div>
            ))}
          </div>
        </section>
      ) : null}

      <div className="grid gap-4 xl:grid-cols-[minmax(360px,0.84fr)_minmax(0,1.16fr)]">
        <section className="surface-card p-4">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <div className="cp-subtle-label">Basis + Structure</div>
              <div className="cp-heading-lg mt-2">Read the estimate at a glance</div>
            </div>
            <span className="cp-chip">{result.materials.components.length} materials</span>
          </div>

          <div className="mt-4 grid gap-2.5 sm:grid-cols-2">
            <MetricTile label="Active metals" value={String(snapshot.activeMetalCount)} detail="Named active inputs" />
            <MetricTile label="Recipe load" value={`${snapshot.nonSupportWt.toFixed(1)} wt%`} detail={`Support closes at ${snapshot.supportWtPct.toFixed(1)} wt%`} />
            <MetricTile label="Support" value={snapshot.selectedSupportName ?? 'Pending'} detail="Current support basis" />
            <MetricTile label="Process path" value={String(snapshot.stepLabels.length)} detail="Selected manufacturing steps" />
          </div>

          <div className="mt-4 grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(240px,0.88fr)]">
            <div className="rounded-[24px] border border-slate-900/8 bg-white/58 p-4">
              <div className="cp-subtle-label">Cost Structure</div>
              <div className="cp-heading-lg mt-2">Materials vs processing</div>
              <div className="mt-4 space-y-3">
                {summaryRows.map((item, index) => (
                  <div key={item.label}>
                    <div className="flex items-center justify-between gap-3 text-sm"><span className="text-slate-600">{item.label}</span><span className="font-semibold text-slate-950">{item.value}</span></div>
                    <div className="mt-2 h-2 rounded-full bg-slate-200/80"><div className="h-full rounded-full" style={{ width: `${Math.max(item.share, 4)}%`, backgroundColor: CHART_COLORS[index] }} /></div>
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
                      {pieData.map((entry, index) => <Cell key={entry.name} fill={CHART_COLORS[index % CHART_COLORS.length]} />)}
                    </Pie>
                    <Tooltip formatter={(value) => [`${Number(value).toFixed(1)}%`, 'Share']} contentStyle={{ borderRadius: 18, border: '1px solid rgba(31,47,72,0.10)', background: 'rgba(255,251,245,0.96)', color: '#142033', fontSize: 12, boxShadow: '0 18px 48px rgba(23,34,51,0.12)' }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-2 grid gap-2 sm:grid-cols-2">
                {pieData.map((entry, index) => (
                  <div key={entry.name} className="flex items-center gap-2 text-sm text-slate-600"><span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: CHART_COLORS[index % CHART_COLORS.length] }} />{entry.name}</div>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-4 border-t border-slate-900/8 pt-4">
            <div className="cp-subtle-label">Process Path</div>
            <div className="mt-3 flex flex-wrap gap-2">
              {snapshot.stepLabels.map((label) => <span key={label} className="cp-chip">{label}</span>)}
            </div>
          </div>

          {snapshot.benchmarkCandidate ? (
            <div className="mt-4 rounded-[24px] border border-emerald-200 bg-emerald-50/80 p-4">
              <div className="cp-subtle-label !text-emerald-700">Reference route context</div>
              <div className="mt-2 cp-heading-sm">{snapshot.benchmarkCandidate.title}</div>
              <div className="mt-2 text-sm leading-6 text-emerald-900">{snapshot.benchmarkCandidate.screening_summary}</div>
              <div className="mt-3 flex flex-wrap gap-2">
                <span className="cp-chip">{snapshot.benchmarkCandidate.archetype}</span>
                <span className="cp-chip">{snapshot.benchmarkCandidate.route.name}</span>
                <span className="cp-chip">{snapshot.benchmarkCandidate.catalyst_domain === 'electrocatalyst' ? 'Electrocatalyst' : 'Thermocatalyst'}</span>
                <span className="cp-chip">Evidence {snapshot.benchmarkCandidate.scores.evidence.toFixed(1)}</span>
              </div>
            </div>
          ) : null}

          {routeSummary ? (
            <div className="mt-4 rounded-[24px] border border-sky-200 bg-sky-50/75 p-4">
              <div className="cp-subtle-label !text-sky-700">Manufacturing route</div>
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
                    {routeSummary.preprocess.map((item) => <span key={item} className="cp-chip">{item}</span>)}
                  </div>
                </div>
                <div>
                  <div className="cp-subtle-label !text-sky-700">Synthesis</div>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {routeSummary.synthesis.map((item) => <span key={item} className="cp-chip">{item}</span>)}
                  </div>
                </div>
                <div>
                  <div className="cp-subtle-label !text-sky-700">Post-treatment</div>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {routeSummary.postprocess.map((item) => <span key={item} className="cp-chip">{item}</span>)}
                  </div>
                </div>
              </div>
            </div>
          ) : null}
        </section>

        <section className="surface-card p-4">
          <div className="flex min-w-0 flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div className="min-w-0">
              <div className="cp-subtle-label">Material Ledger</div>
              <div className="cp-heading-lg mt-2">Catalyst component ledger</div>
              <div className="mt-1 text-xs leading-6 text-slate-500">Per-component loading, source cost, and contribution inside the selling-price estimate.</div>
            </div>
            <span className="cp-chip shrink-0">{snapshot.selectedSupportName ?? 'Support'}</span>
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
                    <div className="mt-1 text-[11px] uppercase tracking-[0.18em] text-slate-400">{component.role.replace('_', ' ')}</div>
                  </div>
                  <div className="text-left sm:text-right">
                    <div className="cp-subtle-label">Per cat</div>
                    <div className="mt-2 font-display text-[1.45rem] text-slate-950">${toDisplay(component.cost_per_lb_cat).toFixed(3)}</div>
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
            <div className="flex items-center justify-between gap-3 text-sm"><span className="text-slate-600">Total material cost</span><span className="font-semibold text-slate-950">${toDisplay(result.materials.total_materials_cost_per_lb).toFixed(4)}{catLabel}</span></div>
            <div className="mt-2 text-xs leading-6 text-slate-500">CatCost step basis with backend escalation and margin treatment applied in the calculation engine.</div>
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
                        <div className="mt-1 text-xs text-slate-500">{material.quote_source}{material.quote_year ? ` / ${material.quote_year}` : ''}</div>
                        <div className="mt-2">
                          <span className={`inline-flex rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.16em] ${sourceRecordTone(material.price_scope, Boolean(material.reference_url))}`}>
                            {sourceRecordLabel(material.price_scope, Boolean(material.reference_url))}
                          </span>
                        </div>
                      </div>
                    </div>
                    {material.reference_url ? (
                      <a href={material.reference_url} target="_blank" rel="noreferrer" className="mt-2 inline-flex text-xs text-sky-700 underline underline-offset-2">
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
        </section>
      </div>
    </div>
  );
}
