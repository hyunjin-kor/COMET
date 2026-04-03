import { useLayoutEffect, useState } from 'react';
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import { useNavigate } from 'react-router-dom';
import { loadCalculatorResultSnapshot } from '../lib/calculator-session';
import { useUnit } from '../lib/use-unit';

const CHART_COLORS = ['#78f2d0', '#88a8ff', '#efc36c', '#f3a08d', '#c5b7ff', '#8de0ff'];

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
        <h1 className="cp-heading-xl mt-4">No saved result board is available yet.</h1>
        <p className="cp-body-copy mt-3 max-w-xl">Run a calculation from the calculator page first. The result board will then open as its own review surface and stay available for quick return.</p>
        <div className="mt-5">
          <button onClick={goBackToCalculator} className="cp-button-primary">Back to inputs</button>
        </div>
      </section>
    );
  }

  const { result } = snapshot;
  const altPrice = unit === 'kg' ? result.summary.estimated_price_per_lb : result.summary.estimated_price_per_kg;
  const altLabel = unit === 'kg' ? '/lb' : '/kg';
  const generatedAt = new Date(snapshot.generatedAt).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', hour12: true });
  const composition = typeof result.input_summary.composition === 'string' ? result.input_summary.composition : 'Catalyst estimate';
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
            <h1 className="cp-heading-xl mt-4">Read the estimate on a dedicated result board.</h1>
            <p className="cp-body-copy mt-3 max-w-2xl">Inputs stay on the calculator screen. This board is reserved for price reading, contribution review, and a clean path back to editing.</p>
          </div>
          <button onClick={goBackToCalculator} className="cp-button-primary">Back to inputs</button>
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
                <span className="cp-chip-dark">{snapshot.selectedSupportName ?? 'Support pending'}</span>
                <span className="cp-chip-dark">{snapshot.stepLabels.length} process steps</span>
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
        </section>
      </div>
    </div>
  );
}
