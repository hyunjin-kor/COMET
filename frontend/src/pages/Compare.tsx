import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  fetchBenchmarkFamilies,
  fetchDecisionBenchmark,
  type BenchmarkFamilySummary,
  type DecisionBenchmark,
  type DecisionCandidate,
} from '../lib/api';
import {
  saveCalculatorDraft,
  type CalculatorBenchmarkPreset,
  type CalculatorRow,
} from '../lib/calculator-session';
import { useUnit } from '../lib/use-unit';

type DecisionProfile = 'balanced' | 'cost-first' | 'evidence-first';

const PROFILE_OPTIONS: Array<{
  id: DecisionProfile;
  label: string;
  note: string;
}> = [
  { id: 'balanced', label: 'Balanced', note: 'Economics, evidence, route, and performance' },
  { id: 'cost-first', label: 'Cost-first', note: 'Bias toward lowest current catalyst cost' },
  { id: 'evidence-first', label: 'Evidence-first', note: 'Reward stronger source transparency and route reproducibility' },
];

function uid() {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') return crypto.randomUUID();
  return `row-${Date.now()}-${Math.random().toString(16).slice(2, 10)}`;
}

function scoreTone(score: number) {
  if (score >= 80) return 'text-emerald-700';
  if (score >= 60) return 'text-slate-950';
  return 'text-amber-700';
}

function sourceTone(sourceType: string) {
  if (sourceType === 'live') return 'border-emerald-200 bg-emerald-50 text-emerald-700';
  if (sourceType === 'indexed') return 'border-amber-200 bg-amber-50 text-amber-700';
  return 'border-slate-200 bg-white text-slate-600';
}

function catalystDomainLabel(domain: 'thermal' | 'electrocatalyst') {
  return domain === 'electrocatalyst' ? 'Electrocatalyst' : 'Thermocatalyst';
}

function applicationFamilyLabel(value: string) {
  if (value === 'fuel_cell') return 'Fuel Cell';
  if (value === 'electrolyzer') return 'Electrolyzer';
  if (value === 'direct_methanol_fuel_cell') return 'DMFC';
  return 'General';
}

function toBenchmarkPreset(candidate: DecisionCandidate): CalculatorBenchmarkPreset {
  return {
    slug: candidate.slug,
    title: candidate.title,
    archetype: candidate.archetype,
    screening_basis: candidate.screening_basis,
    screening_summary: candidate.screening_summary,
    catalyst_domain: candidate.catalyst_domain,
    application_family: candidate.application_family,
    route: candidate.route,
    scores: candidate.scores,
    decision_notes: candidate.decision_notes,
  };
}

function toCalculatorRows(candidate: DecisionCandidate): CalculatorRow[] {
  return candidate.components.map((component) => ({
    id: uid(),
    role: component.role as CalculatorRow['role'],
    name: component.name,
    wt_pct: component.wt_pct,
    price_per_lb: component.price_per_lb,
    source_type:
      component.source_type === 'live' || component.source_type === 'indexed'
        ? component.source_type
        : 'manual',
    source: component.pricing_note || component.source,
  }));
}

function MetricTile({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="cp-metric-tile">
      <div className="cp-subtle-label">{label}</div>
      <div className="mt-2 text-2xl font-display text-slate-950">{value}</div>
      <div className="mt-1 text-xs leading-5 text-slate-500">{detail}</div>
    </div>
  );
}

export default function Compare() {
  const navigate = useNavigate();
  const { toDisplay, fmtLabel } = useUnit();
  const [profile, setProfile] = useState<DecisionProfile>('balanced');
  const [families, setFamilies] = useState<BenchmarkFamilySummary[]>([]);
  const [family, setFamily] = useState('');
  const [benchmark, setBenchmark] = useState<DecisionBenchmark | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeSlug, setActiveSlug] = useState<string | null>(null);

  useEffect(() => {
    fetchBenchmarkFamilies()
      .then((payload) => {
        if (payload.families.length === 0) {
          setError('No benchmark families are available.');
          setLoading(false);
          return;
        }
        setFamilies(payload.families);
        setFamily((current) => current || payload.families[0]?.family || '');
      })
      .catch((caughtError: unknown) => {
        setError(caughtError instanceof Error ? caughtError.message : 'Failed to load benchmark library');
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    if (!family) return;

    setLoading(true);
    setError('');
    fetchDecisionBenchmark(family, profile)
      .then((payload) => {
        setBenchmark(payload);
        setActiveSlug((current) => current ?? payload.winner?.slug ?? payload.candidates[0]?.slug ?? null);
      })
      .catch((caughtError: unknown) => {
        setError(caughtError instanceof Error ? caughtError.message : 'Failed to load benchmark library');
      })
      .finally(() => setLoading(false));
  }, [family, profile]);

  const candidates = benchmark?.candidates ?? [];
  const activeFamily = useMemo(
    () => families.find((item) => item.family === family) ?? null,
    [families, family],
  );
  const activeCandidate = useMemo(
    () => candidates.find((candidate) => candidate.slug === activeSlug) ?? benchmark?.winner ?? null,
    [activeSlug, benchmark?.winner, candidates],
  );

  function loadIntoCalculator(candidate: DecisionCandidate) {
    saveCalculatorDraft({
      rows: toCalculatorRows(candidate),
      steps: candidate.route.steps,
      catalystDomain: candidate.catalyst_domain,
      applicationFamily: candidate.application_family,
      orderSize: Number(candidate.estimate.input_summary.order_size_tons ?? 20),
      pricesUpdatedAt: benchmark?.price_basis_updated_at ?? null,
      electrocatalystConfig: candidate.catalyst_domain === 'electrocatalyst'
        ? {
            catalystMaterialKey: '',
            ionomerMaterialKey: '',
            membraneMaterialKey: '',
            substrateMaterialKey: '',
            activeAreaCm2: 25,
            catalystLoadingMgCm2: 0.3,
            ionomerToCatalystRatio: 0.8,
            templateId: candidate.route.calculator_template_id ?? 'pem_fuel_cell_ccm',
          }
        : null,
      benchmarkCandidate: toBenchmarkPreset(candidate),
    });
    navigate('/');
  }

  if (loading) {
    return (
      <div className="surface-card flex items-center gap-3 px-5 py-6 text-slate-600">
        <span className="h-4 w-4 animate-spin rounded-full border-2 border-[#78f2d0] border-t-transparent" />
        Loading benchmark library...
      </div>
    );
  }

  if (error || !benchmark || !activeCandidate) {
    return (
      <section className="surface-card cp-enter overflow-hidden p-6 sm:p-7">
        <span className="section-kicker">Benchmark Library</span>
        <h1 className="cp-heading-xl mt-4">Benchmark library is unavailable.</h1>
        <p className="cp-body-copy mt-3 max-w-xl">
          {error || 'The selected reference family did not return any candidate data.'}
        </p>
      </section>
    );
  }

  const winner = benchmark.winner;
  const updatedAt = benchmark.price_basis_updated_at
    ? new Date(benchmark.price_basis_updated_at).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true,
      })
    : 'Reference basis';

  return (
    <div className="space-y-4">
      <section className="surface-card cp-enter overflow-hidden p-5 sm:p-6">
        <div className="grid gap-4 xl:grid-cols-[minmax(0,1.1fr)_minmax(330px,0.9fr)]">
          <div className="surface-ink relative overflow-hidden p-5 sm:p-6">
            <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(120,242,208,0.22),transparent_0_32%),radial-gradient(circle_at_bottom_right,rgba(239,195,108,0.14),transparent_0_28%)]" />
            <div className="relative">
              <div className="cp-subtle-label !text-slate-400">Benchmark Library</div>
              <h1 className="mt-3 font-display text-[clamp(2rem,4vw,3.5rem)] leading-[0.94] text-white">
                Optional reference routes for catalyst screening.
              </h1>
              <div className="mt-3 flex flex-wrap gap-2">
                {activeFamily ? <span className="cp-chip-dark">{activeFamily.title}</span> : null}
                {benchmark.reaction ? <span className="cp-chip-dark">{benchmark.reaction}</span> : null}
                <span className="cp-chip-dark">{catalystDomainLabel(benchmark.catalyst_domain)}</span>
                <span className="cp-chip-dark">{applicationFamilyLabel(benchmark.application_family)}</span>
                <span className="cp-chip-dark">{benchmark.decision_profile.label}</span>
                <span className="cp-chip-dark">Updated {updatedAt}</span>
              </div>
              <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-300">
                {benchmark.objective} Use this screen for optional literature-backed sanity checks, then load any route
                into the calculator and continue editing without reaction-specific lock-in.
              </p>

              {winner ? (
                <div className="mt-6 rounded-[26px] border border-white/10 bg-white/6 p-4">
                  <div className="cp-subtle-label !text-slate-400">Current reference winner</div>
                  <div className="mt-2 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                    <div>
                      <div className="text-2xl font-display text-white">{winner.title}</div>
                      <div className="mt-1 text-sm text-slate-300">{winner.archetype}</div>
                    </div>
                    <div className="text-left sm:text-right">
                      <div className="text-3xl font-display text-white">
                        ${toDisplay(winner.summary.landed_cost_per_lb).toFixed(2)}
                      </div>
                      <div className="mt-1 text-sm text-slate-300">{fmtLabel}</div>
                    </div>
                  </div>
                  <div className="mt-4 grid gap-3 sm:grid-cols-3">
                    <div className="cp-metric-tile-dark">
                      <div className="cp-subtle-label !text-slate-400">Total score</div>
                      <div className="mt-2 text-xl font-display text-white">{winner.scores.total.toFixed(1)}</div>
                    </div>
                    <div className="cp-metric-tile-dark">
                      <div className="cp-subtle-label !text-slate-400">Evidence</div>
                      <div className="mt-2 text-xl font-display text-white">{winner.scores.evidence.toFixed(1)}</div>
                    </div>
                    <div className="cp-metric-tile-dark">
                      <div className="cp-subtle-label !text-slate-400">Window</div>
                      <div className="mt-2 text-xl font-display text-white">
                        {winner.summary.temperature_window_c[0]}-{winner.summary.temperature_window_c[1]} C
                      </div>
                    </div>
                  </div>
                </div>
              ) : null}
            </div>
          </div>

          <div className="space-y-3">
            <div className="surface-ghost p-4">
              <div className="cp-subtle-label">Reference family</div>
              <div className="mt-3 flex flex-wrap gap-2">
                {families.map((option) => (
                  <button
                    key={option.family}
                    onClick={() => setFamily(option.family)}
                    className={`rounded-[18px] border px-3 py-2 text-left text-sm transition ${
                      option.family === family
                        ? 'border-teal-200 bg-teal-50 text-teal-700'
                        : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300'
                    }`}
                  >
                    <div className="font-semibold">{option.title}</div>
                    <div className="mt-1 text-xs leading-5 text-slate-500">
                      {catalystDomainLabel(option.catalyst_domain)} / {applicationFamilyLabel(option.application_family)}
                    </div>
                    <div className="mt-1 text-xs leading-5 text-slate-500">
                      {option.candidate_count} routes, {option.citation_count} references
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <div className="surface-ghost p-4">
              <div className="cp-subtle-label">Ranking profile</div>
              <div className="mt-3 flex flex-wrap gap-2">
                {PROFILE_OPTIONS.map((option) => (
                  <button
                    key={option.id}
                    onClick={() => setProfile(option.id)}
                    className={`rounded-[18px] border px-3 py-2 text-left text-sm transition ${
                      option.id === profile
                        ? 'border-teal-200 bg-teal-50 text-teal-700'
                        : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300'
                    }`}
                  >
                    <div className="font-semibold">{option.label}</div>
                    <div className="mt-1 text-xs leading-5 text-slate-500">{option.note}</div>
                  </button>
                ))}
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              <MetricTile
                label="Economics"
                value={`${Math.round(benchmark.decision_profile.weights.economics * 100)}%`}
                detail="Current-price bias"
              />
              <MetricTile
                label="Evidence"
                value={`${Math.round(benchmark.decision_profile.weights.evidence * 100)}%`}
                detail="Source confidence weight"
              />
              <MetricTile
                label="Route"
                value={`${Math.round(benchmark.decision_profile.weights.route * 100)}%`}
                detail="Manufacturing confidence"
              />
              <MetricTile
                label="Performance"
                value={`${Math.round(benchmark.decision_profile.weights.performance * 100)}%`}
                detail="Activity / operating window"
              />
            </div>
          </div>
        </div>
      </section>

      <div className="grid gap-4 xl:grid-cols-[minmax(360px,0.82fr)_minmax(0,1.18fr)]">
        <section className="surface-card p-4">
          <div className="flex items-start justify-between gap-3">
            <div>
              <div className="cp-subtle-label">Reference routes</div>
              <div className="cp-heading-lg mt-2">How do these routes compare right now?</div>
            </div>
            <span className="cp-chip">{candidates.length} candidates</span>
          </div>

          <div className="mt-4 space-y-3">
            {candidates.map((candidate, index) => {
              const active = activeCandidate.slug === candidate.slug;
              return (
                <button
                  key={candidate.slug}
                  onClick={() => setActiveSlug(candidate.slug)}
                  className={`w-full rounded-[24px] border px-4 py-4 text-left transition ${
                    active
                      ? 'border-emerald-200 bg-emerald-50/80'
                      : 'border-slate-900/8 bg-white/64 hover:bg-white/88'
                  }`}
                >
                  <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                    <div className="min-w-0">
                      <div className="flex items-center gap-3">
                        <span className="flex h-9 w-9 items-center justify-center rounded-[16px] border border-slate-900/8 bg-white/72 text-sm font-semibold text-slate-950">
                          {index + 1}
                        </span>
                        <div className="min-w-0">
                          <div className="truncate font-semibold text-slate-950">{candidate.title}</div>
                          <div className="mt-1 text-xs text-slate-500">{candidate.archetype}</div>
                        </div>
                      </div>
                      <div className="mt-3 text-sm leading-6 text-slate-600">{candidate.screening_summary}</div>
                    </div>

                    <div className="grid shrink-0 gap-2 text-right sm:min-w-[150px]">
                      <div>
                        <div className="cp-subtle-label">Landed</div>
                        <div className="mt-2 text-2xl font-display text-slate-950">
                          ${toDisplay(candidate.summary.landed_cost_per_lb).toFixed(2)}
                        </div>
                        <div className="text-xs text-slate-500">{fmtLabel}</div>
                      </div>
                      <div className={`text-sm font-semibold ${scoreTone(candidate.scores.total)}`}>
                        Score {candidate.scores.total.toFixed(1)}
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 grid gap-2.5 sm:grid-cols-4">
                    {(
                      [
                        ['Economics', candidate.scores.economics],
                        ['Evidence', candidate.scores.evidence],
                        ['Route', candidate.scores.route],
                        ['Performance', candidate.scores.performance],
                      ] as const
                    ).map(([label, score]) => (
                      <div key={label}>
                        <div className="flex items-center justify-between gap-2 text-xs text-slate-500">
                          <span>{label}</span>
                          <span>{score.toFixed(1)}</span>
                        </div>
                        <div className="mt-1.5 h-2 rounded-full bg-slate-200/80">
                          <div
                            className="h-full rounded-full bg-[linear-gradient(90deg,#78f2d0,#88a8ff)]"
                            style={{ width: `${Math.max(8, Math.min(score, 100))}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </button>
              );
            })}
          </div>
        </section>

        <section className="surface-card p-4">
          <div className="flex flex-col gap-3 border-b border-slate-900/8 pb-4 sm:flex-row sm:items-start sm:justify-between">
            <div className="min-w-0">
              <div className="cp-subtle-label">Selected reference route</div>
              <div className="cp-heading-lg mt-2">{activeCandidate.title}</div>
              <div className="mt-1 text-sm text-slate-500">{activeCandidate.archetype}</div>
              <div className="mt-2 flex flex-wrap gap-2">
                <span className="cp-chip">{catalystDomainLabel(activeCandidate.catalyst_domain)}</span>
                <span className="cp-chip">{applicationFamilyLabel(activeCandidate.application_family)}</span>
              </div>
            </div>

            <button onClick={() => loadIntoCalculator(activeCandidate)} className="cp-button-primary">
              Load as starting point
            </button>
          </div>

          <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            <MetricTile
              label="Landed cost"
              value={`$${toDisplay(activeCandidate.summary.landed_cost_per_lb).toFixed(2)}`}
              detail={fmtLabel}
            />
            <MetricTile
              label="Materials"
              value={`$${toDisplay(activeCandidate.summary.materials_cost_per_lb).toFixed(2)}`}
              detail="Raw material stack"
            />
            <MetricTile
              label="Processing"
              value={`$${toDisplay(activeCandidate.summary.processing_cost_per_lb).toFixed(2)}`}
              detail="Step-method operations"
            />
            <MetricTile
              label="Route extras"
              value={`$${toDisplay(activeCandidate.summary.route_extra_cost_per_lb).toFixed(2)}`}
              detail="QA + activation + route overhead"
            />
          </div>

          <div className="mt-4 grid gap-4 xl:grid-cols-[minmax(0,1.05fr)_minmax(330px,0.95fr)]">
            <div className="space-y-4">
              <div className="surface-ghost p-4">
                <div className="cp-subtle-label">Manufacturing route</div>
                <div className="mt-2 cp-heading-sm">{activeCandidate.route.name}</div>
                <div className="mt-2 text-sm leading-7 text-slate-600">{activeCandidate.route.route_note}</div>
                <div className="mt-3 flex flex-wrap gap-2">
                  <span className="cp-chip">{activeCandidate.route.manufacturing_mode}</span>
                  <span className="cp-chip">{activeCandidate.summary.temperature_window_c[0]}-{activeCandidate.summary.temperature_window_c[1]} C</span>
                  <span className="cp-chip">{activeCandidate.summary.scale} scale</span>
                </div>

                <div className="mt-4 grid gap-3 md:grid-cols-3">
                  {(
                    [
                      ['Preprocess', activeCandidate.route.preprocess],
                      ['Synthesis', activeCandidate.route.synthesis],
                      ['Postprocess', activeCandidate.route.postprocess],
                    ] as Array<[string, string[]]>
                  ).map(([label, items]) => (
                    <div key={label} className="rounded-[22px] border border-slate-900/8 bg-white/64 p-3">
                      <div className="cp-subtle-label">{label}</div>
                      <div className="mt-3 space-y-2">
                        {items.map((item) => (
                          <div key={item} className="text-sm leading-6 text-slate-700">
                            {item}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-4 rounded-[22px] border border-slate-900/8 bg-white/64 p-3">
                  <div className="cp-subtle-label">Quality gates</div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {activeCandidate.route.quality_gates.map((item) => (
                      <span key={item} className="cp-chip">
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="surface-ghost p-4">
                <div className="cp-subtle-label">Component evidence</div>
                <div className="mt-4 space-y-3">
                  {activeCandidate.components.map((component) => (
                    <div
                      key={`${component.name}-${component.role}`}
                      className="rounded-[22px] border border-slate-900/8 bg-white/64 px-4 py-3"
                    >
                      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                        <div>
                          <div className="font-semibold text-slate-950">{component.name}</div>
                          <div className="mt-1 text-xs uppercase tracking-[0.18em] text-slate-400">
                            {component.role.replace('_', ' ')}
                          </div>
                        </div>
                        <div className="text-left sm:text-right">
                          <div className="text-lg font-display text-slate-950">
                            ${toDisplay(component.cost_per_lb_cat).toFixed(2)}
                          </div>
                          <div className="text-xs text-slate-500">{component.cost_pct.toFixed(1)}% of materials</div>
                        </div>
                      </div>

                      <div className="mt-3 flex flex-wrap items-center gap-2">
                        <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${sourceTone(component.source_type)}`}>
                          {component.source_type}
                        </span>
                        <span className="cp-chip">{component.evidence.label}</span>
                        <span className="cp-chip">Confidence {component.evidence.confidence_score}</span>
                      </div>
                      <div className="mt-3 text-sm leading-6 text-slate-600">{component.pricing_note}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="surface-ghost p-4">
                <div className="cp-subtle-label">Ranking readout</div>
                <div className="mt-4 space-y-3">
                  {(
                    [
                      ['Economics', activeCandidate.scores.economics, 'Current landed catalyst cost'],
                      ['Evidence', activeCandidate.scores.evidence, 'Source confidence across price drivers'],
                      ['Route', activeCandidate.scores.route, 'Manufacturing reproducibility and maturity'],
                      ['Performance', activeCandidate.scores.performance, 'Activity / operating window credit'],
                    ] as const
                  ).map(([label, score, detail]) => (
                    <div key={label}>
                      <div className="flex items-center justify-between gap-2 text-sm">
                        <span className="font-semibold text-slate-900">{label}</span>
                        <span className={scoreTone(score)}>{score.toFixed(1)}</span>
                      </div>
                      <div className="mt-2 h-2 rounded-full bg-slate-200/80">
                        <div
                          className="h-full rounded-full bg-[linear-gradient(90deg,#78f2d0,#88a8ff)]"
                          style={{ width: `${Math.max(8, Math.min(score, 100))}%` }}
                        />
                      </div>
                      <div className="mt-1 text-xs leading-5 text-slate-500">{detail}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="surface-ghost p-4">
                <div className="cp-subtle-label">Reference notes</div>
                <div className="mt-3 space-y-2">
                  {activeCandidate.decision_notes.map((note) => (
                    <div key={note} className="rounded-[18px] border border-slate-900/8 bg-white/64 px-3 py-2 text-sm leading-6 text-slate-700">
                      {note}
                    </div>
                  ))}
                </div>
              </div>

              <div className="surface-ghost p-4">
                <div className="cp-subtle-label">Evidence anchors</div>
                <div className="mt-3 space-y-3">
                  {activeCandidate.literature_basis.map((item) => (
                    <a
                      key={item.id}
                      href={item.url}
                      target="_blank"
                      rel="noreferrer"
                      className="block rounded-[18px] border border-slate-900/8 bg-white/64 px-3 py-3 transition hover:bg-white"
                    >
                      <div className="font-semibold text-slate-950">{item.label}</div>
                      <div className="mt-1 text-xs uppercase tracking-[0.18em] text-slate-400">{item.kind}</div>
                      <div className="mt-2 text-sm leading-6 text-slate-600">{item.note}</div>
                    </a>
                  ))}
                </div>

                <div className="mt-4 space-y-3">
                  {activeCandidate.catalog_quotes.map((quote) => (
                    <a
                      key={quote.id}
                      href={quote.url}
                      target="_blank"
                      rel="noreferrer"
                      className="block rounded-[18px] border border-slate-900/8 bg-white/64 px-3 py-3 transition hover:bg-white"
                    >
                      <div className="font-semibold text-slate-950">{quote.material}</div>
                      <div className="mt-2 flex flex-wrap gap-2">
                        <span className="cp-chip">{quote.pack_size}</span>
                        <span className="cp-chip">${quote.price_usd.toFixed(2)} pack</span>
                        <span className="cp-chip">${quote.normalized_price_per_lb.toFixed(0)}/lb normalized</span>
                      </div>
                      <div className="mt-2 text-sm leading-6 text-slate-600">{quote.note}</div>
                    </a>
                  ))}
                </div>
              </div>

              <div className="surface-ghost p-4">
                <div className="cp-subtle-label">Family literature bank</div>
                <div className="mt-2 text-xs leading-6 text-slate-500">
                  High-confidence references attached to the active family. Candidate cards use subsets of this bank.
                </div>
                <div className="mt-3 space-y-3">
                  {benchmark.citations.map((item) => (
                    <a
                      key={item.id}
                      href={item.url}
                      target="_blank"
                      rel="noreferrer"
                      className="block rounded-[18px] border border-slate-900/8 bg-white/64 px-3 py-3 transition hover:bg-white"
                    >
                      <div className="flex flex-wrap items-center gap-2">
                        <div className="font-semibold text-slate-950">{item.label}</div>
                        <span className="cp-chip">{item.kind}</span>
                      </div>
                      <div className="mt-2 text-sm leading-6 text-slate-600">{item.note}</div>
                    </a>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
