import { useState } from 'react';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { apiUrl } from '../lib/api';
import { useUnit } from '../lib/use-unit';

interface Composition {
  label: string;
  metal_symbol: string;
  metal_price: number;
  metal_price_unit: string;
  metal_loading_wt_pct: number;
  support_name: string;
  support_price_per_lb: number;
  steps: string[];
  order_size_tons: number;
}

interface CompareResult {
  label: string;
  estimated_price_per_lb: number;
  materials_cost_per_lb: number;
  processing_cost_per_lb: number;
  scale: string;
}

const KNOWN_METALS = ['Ni', 'Co', 'Cu', 'Fe', 'Pt', 'Pd', 'Rh', 'Ru', 'Ir', 'Mo', 'W', 'Au', 'Ag', 'Al'];
const SUPPORT_OPTIONS = ['Al2O3', 'SiO2', 'TiO2', 'Carbon', 'ZSM-5', 'USY', 'CeO2', 'MgO', 'ZrO2'];
const PALETTE = ['#78f2d0', '#88a8ff', '#efc36c', '#f3a08d'];

function emptyComp(): Composition {
  return {
    label: '',
    metal_symbol: 'Ni',
    metal_price: 7.5,
    metal_price_unit: '$/lb',
    metal_loading_wt_pct: 15,
    support_name: 'Al2O3',
    support_price_per_lb: 0.5,
    steps: ['mixer_slurry', 'incipient_wetness', 'dryer_rotary_100_300C'],
    order_size_tons: 20,
  };
}

function scaleLabel(tons: number) {
  if (tons < 5) return 'Small';
  if (tons < 70) return 'Medium';
  return 'Large';
}

function ScenarioMetric({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="cp-metric-tile">
      <div className="cp-subtle-label">{label}</div>
      <div className="mt-2 text-2xl font-display text-slate-900">{value}</div>
      <div className="mt-1 text-xs leading-5 text-slate-500">{detail}</div>
    </div>
  );
}

function FieldBlock({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <div className="flex items-center justify-between gap-3">
        <span className="cp-subtle-label">{label}</span>
        {hint ? <span className="text-[11px] text-slate-400">{hint}</span> : null}
      </div>
      <div className="mt-2">{children}</div>
    </label>
  );
}

export default function Compare() {
  const { toDisplay, toInternal, fmtLabel } = useUnit();
  const [comps, setComps] = useState<Composition[]>([emptyComp(), emptyComp()]);
  const [results, setResults] = useState<CompareResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const updateComp = (index: number, field: keyof Composition, value: string | number) => {
    setComps((previous) => previous.map((comp, compIndex) => (compIndex === index ? { ...comp, [field]: value } : comp)));
  };

  const addComp = () => {
    if (comps.length < 4) setComps((previous) => [...previous, emptyComp()]);
  };

  const removeComp = (index: number) => {
    if (comps.length > 2) setComps((previous) => previous.filter((_, compIndex) => compIndex !== index));
  };

  const handleCompare = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await fetch(apiUrl('/compare'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ compositions: comps }),
      });

      if (!response.ok) throw new Error((await response.json()).detail);
      setResults((await response.json()).compositions);
    } catch (caughtError: unknown) {
      setError(caughtError instanceof Error ? caughtError.message : 'Compare failed');
    } finally {
      setLoading(false);
    }
  };

  const chartData = results.map((result) => ({
    name: result.label,
    Materials: +toDisplay(result.materials_cost_per_lb).toFixed(3),
    Processing: +toDisplay(result.processing_cost_per_lb).toFixed(3),
    'G&A + Margin': +toDisplay(
      result.estimated_price_per_lb - result.materials_cost_per_lb - result.processing_cost_per_lb,
    ).toFixed(3),
  }));

  const bestIdx = results.length
    ? results.reduce((bestIndex, result, index) =>
        result.estimated_price_per_lb < results[bestIndex].estimated_price_per_lb ? index : bestIndex,
      0)
    : -1;

  const bestScenario = bestIdx >= 0 ? results[bestIdx] : null;

  return (
    <div className="space-y-4">
      <div className="grid gap-4 xl:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]">
        <section className="surface-card cp-enter overflow-hidden px-5 py-6 sm:px-6" style={{ animationDelay: '0.06s' }}>
          <div className="flex flex-col gap-4 border-b border-slate-900/8 pb-5 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <div className="cp-subtle-label">Scenario Editor</div>
              <h2 className="cp-heading-xl mt-2">Configure estimate variants</h2>
              <p className="cp-body-copy mt-2 max-w-2xl">
                Each scenario keeps the same estimate structure but carries its own metal, support, loading, and
                campaign-size assumptions.
              </p>
            </div>

            {comps.length < 4 && (
              <button onClick={addComp} className="cp-button-secondary">
                Add scenario
              </button>
            )}
          </div>

          <div className="mt-5 space-y-4">
            {comps.map((composition, index) => (
              <article key={`${composition.label}-${index}`} className="surface-ghost overflow-hidden p-4 sm:p-5">
                <div className="flex flex-col gap-4 border-b border-slate-900/8 pb-4 sm:flex-row sm:items-start sm:justify-between">
                  <div className="flex min-w-0 items-start gap-3">
                    <div
                      className="flex h-11 w-11 flex-none items-center justify-center rounded-[18px] text-sm font-semibold text-slate-950"
                      style={{ backgroundColor: PALETTE[index] }}
                    >
                      {index + 1}
                    </div>

                    <div className="min-w-0">
                      <div className="cp-subtle-label">Scenario {index + 1}</div>
                      <input
                        value={composition.label}
                        onChange={(event) => updateComp(index, 'label', event.target.value)}
                        placeholder={`Scenario ${index + 1} label`}
                        className="mt-2 w-full bg-transparent font-display text-[1.45rem] leading-none text-slate-950 outline-none placeholder:text-slate-400"
                      />
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="cp-chip">{scaleLabel(composition.order_size_tons)} scale</span>
                    {comps.length > 2 && (
                      <button onClick={() => removeComp(index)} className="cp-button-secondary px-3 py-2 text-xs">
                        Remove
                      </button>
                    )}
                  </div>
                </div>

                <div className="mt-4 grid gap-4 md:grid-cols-2">
                  <FieldBlock label="Metal">
                    <select
                      value={composition.metal_symbol}
                      onChange={(event) => updateComp(index, 'metal_symbol', event.target.value)}
                      className="input-base"
                    >
                      {KNOWN_METALS.map((metal) => (
                        <option key={metal} value={metal}>
                          {metal}
                        </option>
                      ))}
                    </select>
                  </FieldBlock>

                  <FieldBlock label="Metal price" hint={fmtLabel}>
                    <input
                      type="number"
                      step="0.01"
                      value={toDisplay(composition.metal_price).toFixed(2)}
                      onChange={(event) => updateComp(index, 'metal_price', toInternal(Number(event.target.value)))}
                      className="input-base font-mono"
                    />
                  </FieldBlock>

                  <FieldBlock label="Loading" hint="wt%">
                    <input
                      type="number"
                      step="0.1"
                      min="0.1"
                      max="99"
                      value={composition.metal_loading_wt_pct}
                      onChange={(event) => updateComp(index, 'metal_loading_wt_pct', Number(event.target.value))}
                      className="input-base font-mono"
                    />
                  </FieldBlock>

                  <FieldBlock label="Order size" hint="tons">
                    <input
                      type="number"
                      step="1"
                      min="1"
                      value={composition.order_size_tons}
                      onChange={(event) => updateComp(index, 'order_size_tons', Number(event.target.value))}
                      className="input-base font-mono"
                    />
                  </FieldBlock>

                  <FieldBlock label="Support">
                    <select
                      value={composition.support_name}
                      onChange={(event) => updateComp(index, 'support_name', event.target.value)}
                      className="input-base"
                    >
                      {SUPPORT_OPTIONS.map((support) => (
                        <option key={support} value={support}>
                          {support}
                        </option>
                      ))}
                    </select>
                  </FieldBlock>

                  <FieldBlock label="Support price" hint={fmtLabel}>
                    <input
                      type="number"
                      step="0.01"
                      value={toDisplay(composition.support_price_per_lb).toFixed(2)}
                      onChange={(event) =>
                        updateComp(index, 'support_price_per_lb', toInternal(Number(event.target.value)))
                      }
                      className="input-base font-mono"
                    />
                  </FieldBlock>
                </div>

                <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-slate-500">
                  <span className="cp-chip">
                    ${toDisplay(composition.metal_price).toFixed(2)}
                    {fmtLabel} metal
                  </span>
                  <span className="cp-chip">{composition.metal_loading_wt_pct.toFixed(1)} wt% loading</span>
                  <span className="cp-chip">{composition.steps.length} process steps</span>
                </div>
              </article>
            ))}
          </div>

          <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center">
            <button onClick={handleCompare} disabled={loading} className="cp-button-primary min-w-[220px]">
              {loading ? (
                <>
                  <span className="mr-2 inline-flex h-4 w-4 animate-spin rounded-full border-2 border-slate-950 border-t-transparent" />
                  Comparing scenarios
                </>
              ) : (
                `Compare ${comps.length} scenarios`
              )}
            </button>

            <div className="text-xs leading-6 text-slate-500">
              The compare API returns materials, processing, and total estimated selling price for each submitted
              scenario.
            </div>
          </div>

          {error && <div className="mt-4 rounded-[24px] border border-red-200 bg-red-50 px-4 py-4 text-sm text-red-700">{error}</div>}
        </section>

        <section className="surface-card cp-enter overflow-hidden px-5 py-6 sm:px-6" style={{ animationDelay: '0.1s' }}>
          {!results.length ? (
            <div className="flex min-h-[520px] flex-col justify-between">
              <div>
                <span className="section-kicker">Ranking Board</span>
                <h2 className="cp-heading-xl mt-4">
                  Run a comparison to rank the estimate outputs.
                </h2>
                <p className="cp-body-copy mt-3 max-w-xl">
                  This board turns into a stacked cost chart and ranked scenario list once the backend returns a shared-basis comparison.
                </p>
              </div>

              <div className="grid gap-3 sm:grid-cols-3">
                <ScenarioMetric label="Best price" value="Pending" detail="Shown after compare run" />
                <ScenarioMetric label="Cost split" value="Pending" detail="Materials, processing, and margin" />
                <ScenarioMetric label="Scenario lead" value="Pending" detail="Lowest selling price highlighted" />
              </div>
            </div>
          ) : (
            <>
              <div className="surface-ink relative overflow-hidden p-5">
                <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(120,242,208,0.22),transparent_0_34%),radial-gradient(circle_at_bottom_right,rgba(239,195,108,0.15),transparent_0_26%)]" />

                <div className="relative flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
                  <div>
                    <div className="cp-subtle-label !text-slate-400">Lowest estimate</div>
                    <div className="mt-2 text-3xl font-display text-white">{bestScenario?.label}</div>
                    <div className="mt-2 text-sm text-slate-300">
                      Lowest returned estimate across {results.length} compared recipes.
                    </div>
                  </div>

                  {bestScenario && (
                    <div className="grid gap-3 sm:grid-cols-3 lg:min-w-[420px]">
                      <div className="cp-metric-tile-dark">
                        <div className="cp-subtle-label !text-slate-400">Total</div>
                        <div className="mt-2 text-xl font-display text-white">
                          ${toDisplay(bestScenario.estimated_price_per_lb).toFixed(3)}
                          {fmtLabel}
                        </div>
                      </div>
                      <div className="cp-metric-tile-dark">
                        <div className="cp-subtle-label !text-slate-400">Materials</div>
                        <div className="mt-2 text-xl font-display text-white">
                          ${toDisplay(bestScenario.materials_cost_per_lb).toFixed(3)}
                        </div>
                      </div>
                      <div className="cp-metric-tile-dark">
                        <div className="cp-subtle-label !text-slate-400">Scale</div>
                        <div className="mt-2 text-xl font-display text-white">{bestScenario.scale}</div>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <div className="mt-5 rounded-[28px] border border-slate-900/8 bg-white/62 p-5 backdrop-blur-xl">
                <div className="flex items-end justify-between gap-3">
                  <div>
                    <div className="cp-subtle-label">Stacked Cost Comparison</div>
                    <div className="cp-heading-lg mt-2">Materials, processing, and markup</div>
                  </div>
                  {bestScenario ? <span className="cp-chip">Best: {bestScenario.label}</span> : null}
                </div>

                <div className="mt-5 h-[320px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData} barSize={52}>
                      <CartesianGrid stroke="rgba(100,116,139,0.18)" vertical={false} />
                      <XAxis dataKey="name" tick={{ fill: '#66748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fill: '#66748b', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(value) => `$${value}`} />
                      <Tooltip
                        formatter={(value) => [`$${Number(value).toFixed(3)}${fmtLabel}`]}
                        contentStyle={{
                          borderRadius: 18,
                          border: '1px solid rgba(31,47,72,0.10)',
                          background: 'rgba(255,251,245,0.96)',
                          color: '#142033',
                          fontSize: 12,
                          boxShadow: '0 18px 48px rgba(23,34,51,0.12)',
                        }}
                      />
                      <Bar dataKey="Materials" stackId="a" fill="#78f2d0" radius={[6, 6, 0, 0]} />
                      <Bar dataKey="Processing" stackId="a" fill="#88a8ff" />
                      <Bar dataKey="G&A + Margin" stackId="a" fill="#efc36c" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="mt-5 space-y-3">
                {results.map((result, index) => (
                  <div
                    key={result.label}
                    className={`grid gap-3 rounded-[24px] border px-4 py-4 sm:grid-cols-[minmax(0,1fr)_auto_auto_auto] sm:items-center ${
                      index === bestIdx
                        ? 'border-emerald-200 bg-emerald-50/80'
                        : 'border-slate-900/8 bg-white/64'
                    }`}
                  >
                    <div className="flex min-w-0 items-center gap-3">
                      <span className="h-3 w-3 rounded-full" style={{ backgroundColor: PALETTE[index] }} />
                      <div className="min-w-0">
                        <div className="truncate font-semibold text-slate-950">{result.label}</div>
                        <div className="text-xs text-slate-500">{result.scale} scale</div>
                      </div>
                    </div>
                    <div className="text-sm text-slate-600">
                      Materials ${toDisplay(result.materials_cost_per_lb).toFixed(3)}
                    </div>
                    <div className="text-sm text-slate-600">
                      Processing ${toDisplay(result.processing_cost_per_lb).toFixed(3)}
                    </div>
                    <div className={`text-sm font-semibold ${index === bestIdx ? 'text-emerald-700' : 'text-slate-950'}`}>
                      ${toDisplay(result.estimated_price_per_lb).toFixed(3)}
                      {fmtLabel}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </section>
      </div>
    </div>
  );
}
