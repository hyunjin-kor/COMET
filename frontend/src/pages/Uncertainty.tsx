import type { ReactNode } from 'react';
import { useState } from 'react';
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { apiUrl } from '../lib/api';
import { useUnit } from '../lib/use-unit';

interface MCResult {
  mean: number;
  median: number;
  std: number;
  min: number;
  max: number;
  p5: number;
  p25: number;
  p75: number;
  p95: number;
  n_simulations: number;
  n_successful: number;
}

const KNOWN_METALS = ['Ni', 'Co', 'Pt', 'Pd', 'Rh', 'Ru', 'Cu', 'Fe', 'Mo', 'W'];

function StatTile({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="cp-metric-tile">
      <div className="cp-subtle-label">{label}</div>
      <div className="mt-2 text-2xl font-display text-slate-900">{value}</div>
      <div className="mt-1 text-xs leading-5 text-slate-500">{detail}</div>
    </div>
  );
}

function StatTileDark({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="cp-metric-tile-dark">
      <div className="cp-subtle-label !text-slate-400">{label}</div>
      <div className="mt-2 text-2xl font-display text-white">{value}</div>
      <div className="mt-1 text-xs leading-5 text-slate-400">{detail}</div>
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
  children: ReactNode;
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

export default function Uncertainty() {
  const { toDisplay, toInternal, fmtLabel } = useUnit();
  const [result, setResult] = useState<MCResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [metalSymbol, setMetalSymbol] = useState('Ni');
  const [metalPriceInternal, setMetalPriceInternal] = useState(7.5);
  const [loadingPct, setLoadingPct] = useState(15);
  const [orderSize, setOrderSize] = useState(20);
  const [nSim, setNSim] = useState(1000);

  const d = (value: number) => toDisplay(value);
  const histData = result
    ? [
        { range: `${d(result.min).toFixed(1)}-${d(result.p5).toFixed(1)}`, value: 5, fill: '#f3a08d' },
        { range: `${d(result.p5).toFixed(1)}-${d(result.p25).toFixed(1)}`, value: 20, fill: '#efc36c' },
        { range: `${d(result.p25).toFixed(1)}-${d(result.median).toFixed(1)}`, value: 25, fill: '#78f2d0' },
        { range: `${d(result.median).toFixed(1)}-${d(result.p75).toFixed(1)}`, value: 25, fill: '#78f2d0' },
        { range: `${d(result.p75).toFixed(1)}-${d(result.p95).toFixed(1)}`, value: 20, fill: '#88a8ff' },
        { range: `${d(result.p95).toFixed(1)}-${d(result.max).toFixed(1)}`, value: 5, fill: '#efc36c' },
      ]
    : [];

  const handleRun = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await fetch(apiUrl('/uncertainty'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          metal_symbol: metalSymbol,
          metal_price: metalPriceInternal,
          metal_price_unit: '$/lb',
          metal_loading_wt_pct: loadingPct,
          order_size_tons: orderSize,
          n_simulations: nSim,
          uncertainties: {
            metal_price: [0.7, 1.3],
            support_price_per_lb: [0.8, 1.2],
            order_size_tons: [0.8, 1.2],
          },
        }),
      });

      if (!response.ok) throw new Error((await response.json()).detail);
      setResult(await response.json());
    } catch (caughtError: unknown) {
      setError(caughtError instanceof Error ? caughtError.message : 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="grid gap-4 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
        <section className="surface-card cp-enter overflow-hidden px-5 py-6 sm:px-6" style={{ animationDelay: '0.06s' }}>
          <div className="border-b border-slate-900/8 pb-5">
            <div className="cp-subtle-label">Scenario Inputs</div>
            <h2 className="mt-2 text-2xl font-semibold text-slate-950">Uncertainty inputs</h2>
            <p className="mt-2 max-w-2xl text-sm leading-7 text-slate-600">
              Choose a metal and baseline assumptions, then sample the uncertainty envelope for the estimate inputs that matter most.
            </p>
          </div>

          <div className="mt-5 grid gap-4 md:grid-cols-2">
            <FieldBlock label="Metal symbol">
              <select value={metalSymbol} onChange={(event) => setMetalSymbol(event.target.value)} className="input-base">
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
                value={toDisplay(metalPriceInternal).toFixed(2)}
                onChange={(event) => setMetalPriceInternal(toInternal(Number(event.target.value)))}
                className="input-base font-mono"
              />
            </FieldBlock>

            <FieldBlock label="Loading" hint="wt%">
              <input
                type="number"
                step="0.5"
                value={loadingPct}
                onChange={(event) => setLoadingPct(Number(event.target.value))}
                className="input-base font-mono"
              />
            </FieldBlock>

            <FieldBlock label="Order size" hint="tons">
              <input
                type="number"
                step="1"
                value={orderSize}
                onChange={(event) => setOrderSize(Number(event.target.value))}
                className="input-base font-mono"
              />
            </FieldBlock>

            <FieldBlock label="Simulation count" hint="100 to 10000">
              <input
                type="number"
                step="100"
                min="100"
                max="10000"
                value={nSim}
                onChange={(event) => setNSim(Number(event.target.value))}
                className="input-base font-mono"
              />
            </FieldBlock>
          </div>

          <div className="mt-5 grid gap-3 sm:grid-cols-3">
            <div className="cp-metric-tile">
              <div className="cp-subtle-label">Metal price band</div>
              <div className="mt-2 text-lg font-semibold text-slate-950">+/- 30%</div>
              <div className="mt-1 text-xs leading-5 text-slate-500">Uniform sampling range</div>
            </div>
            <div className="cp-metric-tile">
              <div className="cp-subtle-label">Support price band</div>
              <div className="mt-2 text-lg font-semibold text-slate-950">+/- 20%</div>
              <div className="mt-1 text-xs leading-5 text-slate-500">Fixed envelope in API payload</div>
            </div>
            <div className="cp-metric-tile">
              <div className="cp-subtle-label">Campaign size band</div>
              <div className="mt-2 text-lg font-semibold text-slate-950">+/- 20%</div>
              <div className="mt-1 text-xs leading-5 text-slate-500">Applied to order-size sampling</div>
            </div>
          </div>

          <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center">
            <button onClick={handleRun} disabled={loading} className="cp-button-primary min-w-[240px]">
              {loading ? (
                <>
                  <span className="mr-2 inline-flex h-4 w-4 animate-spin rounded-full border-2 border-slate-950 border-t-transparent" />
                  Running simulation
                </>
              ) : (
                `Run Monte Carlo (${nSim.toLocaleString('en-US')})`
              )}
            </button>

            <div className="text-xs leading-6 text-slate-500">
              Percentile bands and the distribution sketch update on the right after the sampling run completes.
            </div>
          </div>

          {error && <div className="mt-4 rounded-[24px] border border-red-200 bg-red-50 px-4 py-4 text-sm text-red-700">{error}</div>}
        </section>

        <section className="surface-card cp-enter overflow-hidden px-5 py-6 sm:px-6" style={{ animationDelay: '0.1s' }}>
          {!result ? (
            <div className="flex min-h-[520px] flex-col justify-between">
              <div>
                <span className="section-kicker">Distribution Output</span>
                <h2 className="mt-4 font-display text-[clamp(1.7rem,2.6vw,2.7rem)] leading-[0.98] text-slate-950">
                  Run the analysis to reveal the estimate envelope.
                </h2>
                <p className="mt-3 max-w-xl text-sm leading-7 text-slate-600">
                  This panel shows percentile bands, distribution shape, and simulation success counts after the backend finishes sampling.
                </p>
              </div>

              <div className="grid gap-3 sm:grid-cols-3">
                <StatTile label="Mean" value="Pending" detail="Average estimate" />
                <StatTile label="Median" value="Pending" detail="50th percentile" />
                <StatTile label="P5-P95" value="Pending" detail="90% interval" />
              </div>
            </div>
          ) : (
            <>
              <div className="surface-ink overflow-hidden p-5">
                <div className="grid gap-3 sm:grid-cols-4">
                  <StatTileDark label="Mean" value={`$${d(result.mean).toFixed(2)}${fmtLabel}`} detail="Average outcome" />
                  <StatTileDark label="Median" value={`$${d(result.median).toFixed(2)}${fmtLabel}`} detail="50th percentile" />
                  <StatTileDark
                    label="P5-P95"
                    value={`$${d(result.p5).toFixed(2)}-$${d(result.p95).toFixed(2)}`}
                    detail="90% interval"
                  />
                  <StatTileDark
                    label="Std dev"
                    value={`$${d(result.std).toFixed(3)}`}
                    detail={`${result.n_successful.toLocaleString('en-US')} successful runs`}
                  />
                </div>
              </div>

              <div className="mt-5 rounded-[28px] border border-slate-900/8 bg-white/62 p-5 backdrop-blur-xl">
                <div className="cp-subtle-label">Distribution Sketch</div>
                <div className="mt-2 text-xl font-semibold text-slate-950">Percentile-weighted shape</div>

                <div className="mt-5 h-[280px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={histData} barSize={54}>
                      <CartesianGrid stroke="rgba(100,116,139,0.18)" vertical={false} />
                      <XAxis dataKey="range" tick={{ fill: '#66748b', fontSize: 10 }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fill: '#66748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                      <Tooltip
                        formatter={(value) => [`${value}%`, 'Share of simulations']}
                        contentStyle={{
                          borderRadius: 18,
                          border: '1px solid rgba(31,47,72,0.10)',
                          background: 'rgba(255,251,245,0.96)',
                          color: '#142033',
                          fontSize: 12,
                          boxShadow: '0 18px 48px rgba(23,34,51,0.12)',
                        }}
                      />
                      <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                        {histData.map((entry) => (
                          <Cell key={entry.range} fill={entry.fill} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="mt-5 grid gap-3 sm:grid-cols-7">
                {[
                  ['Min', result.min],
                  ['P5', result.p5],
                  ['P25', result.p25],
                  ['Median', result.median],
                  ['P75', result.p75],
                  ['P95', result.p95],
                  ['Max', result.max],
                ].map(([label, value]) => (
                  <div key={String(label)} className="rounded-[22px] border border-slate-900/8 bg-white/62 px-3 py-4 text-center">
                    <div className="cp-subtle-label">{label}</div>
                    <div className="mt-2 font-mono text-sm text-slate-950">${d(Number(value)).toFixed(2)}</div>
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
