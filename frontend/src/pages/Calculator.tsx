import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  calculateCost,
  fetchPrices,
  refreshPrices as refreshPriceFeed,
  type ComponentInput,
  type CostInput,
  type MetalPrice,
} from '../lib/api';
import {
  loadCalculatorDraft,
  loadCalculatorResultSnapshot,
  saveCalculatorDraft,
  saveCalculatorResultSnapshot,
  type CalculatorResultSnapshot,
  type CalculatorRow,
} from '../lib/calculator-session';
import { useUnit } from '../lib/use-unit';

const TROY_OZ_PER_LB = 14.5833;
const KNOWN_METALS = ['Pt', 'Pd', 'Rh', 'Ru', 'Ir', 'Ni', 'Co', 'Cu', 'Fe', 'Mo', 'W', 'Au', 'Ag', 'Al'];
const QUICK_ORDER_SIZES = [2, 20, 200];
const DEFAULT_STEPS = ['mixer_slurry', 'incipient_wetness', 'dryer_rotary_100_300C'];
const SUPPORT_OPTIONS = [
  { name: 'Al2O3', price: 0.5, note: 'Alumina, default refinery support' },
  { name: 'SiO2', price: 0.3, note: 'Silica support' },
  { name: 'TiO2', price: 1.2, note: 'Titania support' },
  { name: 'Carbon', price: 1.5, note: 'Activated carbon' },
  { name: 'ZSM-5', price: 3, note: 'Zeolite, MFI family' },
  { name: 'USY', price: 2.5, note: 'FCC-grade zeolite' },
  { name: 'CeO2', price: 2, note: 'Ceria support' },
  { name: 'MgO', price: 0.4, note: 'Magnesia support' },
  { name: 'ZrO2', price: 5, note: 'Zirconia support' },
  { name: 'SiO2-Al2O3', price: 0.8, note: 'Silica-alumina blend' },
] as const;
const ALL_STEPS = [
  { key: 'mixer_dry_blender', label: 'Dry Blender', category: 'Mixing', scales: ['small', 'medium', 'large'] },
  { key: 'mixer_slurry', label: 'Slurry Mixer', category: 'Mixing', scales: ['small', 'medium', 'large'] },
  { key: 'incipient_wetness', label: 'Incipient Wetness', category: 'Impregnation', scales: ['small', 'medium', 'large'] },
  { key: 'reactor_simple', label: 'Simple Reactor', category: 'Reaction', scales: ['small', 'medium', 'large'] },
  { key: 'reactor_multistep', label: 'Multistep Reactor', category: 'Reaction', scales: ['small', 'medium', 'large'] },
  { key: 'crystallizer', label: 'Crystallizer', category: 'Reaction', scales: ['small', 'medium', 'large'] },
  { key: 'dryer_batch_vacuum_tray', label: 'Vacuum Tray Dryer', category: 'Drying', scales: ['small'] },
  { key: 'dryer_rotary_40_100C', label: 'Rotary Dryer 40-100 C', category: 'Drying', scales: ['small', 'medium', 'large'] },
  { key: 'dryer_rotary_100_300C', label: 'Rotary Dryer 100-300 C', category: 'Drying', scales: ['small', 'medium', 'large'] },
  { key: 'dryer_spray', label: 'Spray Dryer', category: 'Drying', scales: ['medium', 'large'] },
  { key: 'kiln_batch', label: 'Batch Kiln', category: 'Calcination', scales: ['small'] },
  { key: 'kiln_continuous_direct', label: 'Continuous Kiln Direct', category: 'Calcination', scales: ['medium', 'large'] },
  { key: 'kiln_continuous_indirect', label: 'Continuous Kiln Indirect', category: 'Calcination', scales: ['medium', 'large'] },
  { key: 'filter_belt_vacuum', label: 'Belt Vacuum Filter', category: 'Separation', scales: ['small', 'medium', 'large'] },
  { key: 'filter_plate_frame', label: 'Plate and Frame Filter', category: 'Separation', scales: ['small'] },
  { key: 'filter_rotary_vacuum', label: 'Rotary Vacuum Filter', category: 'Separation', scales: ['medium', 'large'] },
  { key: 'extruder_with_feeder', label: 'Extruder with Feeder', category: 'Forming', scales: ['small', 'medium', 'large'] },
  { key: 'ball_forming', label: 'Ball Forming', category: 'Forming', scales: ['small', 'medium'] },
  { key: 'mill', label: 'Mill', category: 'Size Reduction', scales: ['small', 'medium', 'large'] },
  { key: 'flare', label: 'Flare', category: 'Utilities', scales: ['small', 'medium', 'large'] },
  { key: 'scrubber_nox', label: 'NOx Scrubber', category: 'Utilities', scales: ['small', 'medium', 'large'] },
] as const;
const STEP_CATEGORIES = [...new Set(ALL_STEPS.map((step) => step.category))];

type SourceType = CalculatorRow['source_type'];
type Scale = 'small' | 'medium' | 'large';
type FeedPrice = { price_per_lb: number; source_type: Exclude<SourceType, 'manual'>; source: string };

function uid() {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') return crypto.randomUUID();
  return `row-${Date.now()}-${Math.random().toString(16).slice(2, 10)}`;
}

const toPerLb = (price: number, unit: string) => unit === '$/troy_oz' ? price * TROY_OZ_PER_LB : unit === '$/kg' ? price / 2.20462 : price;
const getScale = (tons: number): Scale => (tons < 5 ? 'small' : tons < 70 ? 'medium' : 'large');
const sourceTypeLabel = (sourceType: SourceType) => sourceType === 'live' ? 'Live' : sourceType === 'indexed' ? 'Indexed' : 'Manual';
const defaultRows = (): CalculatorRow[] => [
  { id: uid(), role: 'active_metal', name: 'Ni', wt_pct: 20, price_per_lb: 0, source_type: 'manual', source: 'Manual input' },
  { id: uid(), role: 'support', name: 'Al2O3', wt_pct: 80, price_per_lb: 0.5, source_type: 'manual', source: 'Manual support default' },
];
const sourceTone = (sourceType: SourceType) => sourceType === 'live' ? 'border-emerald-200 bg-emerald-50 text-emerald-700' : sourceType === 'indexed' ? 'border-amber-200 bg-amber-50 text-amber-700' : 'border-slate-200 bg-white text-slate-600';
const priceTone = (sourceType: SourceType) => sourceType === 'live' ? 'border-emerald-200 bg-emerald-50/70 text-emerald-800' : sourceType === 'indexed' ? 'border-amber-200 bg-amber-50/70 text-amber-800' : '';
const scaleMeta = (scale: Scale) => scale === 'small' ? { label: 'Small', rate: '1 t/day', classes: 'border-violet-200 bg-violet-50 text-violet-700' } : scale === 'medium' ? { label: 'Medium', rate: '10 t/day', classes: 'border-sky-200 bg-sky-50 text-sky-700' } : { label: 'Large', rate: '150 t/day', classes: 'border-teal-200 bg-teal-50 text-teal-700' };
const formatStepLabel = (stepKey: string) => ALL_STEPS.find((step) => step.key === stepKey)?.label ?? stepKey;

function MetricTile({ label, value, detail, dark = false }: { label: string; value: string; detail: string; dark?: boolean }) {
  return (
    <div className={dark ? 'cp-metric-tile-dark' : 'cp-metric-tile'}>
      <div className={`cp-subtle-label ${dark ? '!text-slate-400' : ''}`}>{label}</div>
      <div className={`mt-2 text-2xl font-display ${dark ? 'text-white' : 'text-slate-900'}`}>{value}</div>
      <div className={`mt-1 text-xs leading-5 ${dark ? 'text-slate-400' : 'text-slate-500'}`}>{detail}</div>
    </div>
  );
}

export default function Calculator() {
  const navigate = useNavigate();
  const { toDisplay, toInternal, fmtLabel } = useUnit();
  const storedDraft = loadCalculatorDraft();
  const [rows, setRows] = useState<CalculatorRow[]>(() => storedDraft?.rows?.length ? storedDraft.rows : defaultRows());
  const [steps, setSteps] = useState<string[]>(() => storedDraft?.steps?.length ? storedDraft.steps : DEFAULT_STEPS);
  const [orderSize, setOrderSize] = useState<number>(() => storedDraft?.orderSize ?? 20);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [liveMap, setLiveMap] = useState<Record<string, FeedPrice>>({});
  const [latestSnapshot, setLatestSnapshot] = useState<CalculatorResultSnapshot | null>(() => loadCalculatorResultSnapshot());
  const [pricesUpdatedAt, setPricesUpdatedAt] = useState<Date | null>(() => storedDraft?.pricesUpdatedAt ? new Date(storedDraft.pricesUpdatedAt) : null);
  const currentScale = getScale(orderSize);
  const scale = scaleMeta(currentScale);

  useEffect(() => {
    saveCalculatorDraft({ rows, steps, orderSize, pricesUpdatedAt: pricesUpdatedAt ? pricesUpdatedAt.toISOString() : null });
  }, [orderSize, pricesUpdatedAt, rows, steps]);

  useEffect(() => {
    setSteps((previous) => previous.filter((key) => {
      const step = ALL_STEPS.find((item) => item.key === key);
      return step ? (step.scales as readonly Scale[]).includes(currentScale) : false;
    }));
  }, [currentScale]);

  useEffect(() => {
    async function loadPrices() {
      try {
        const prices = await fetchPrices();
        const map = toFeedMap(prices);
        setLiveMap(map);
        setPricesUpdatedAt(new Date());
        setRows((previous) => previous.map((row) => row.role === 'support' || !map[row.name] ? row : { ...row, price_per_lb: map[row.name].price_per_lb, source_type: map[row.name].source_type, source: map[row.name].source }));
      } catch {}
    }

    void loadPrices();
  }, []);

  useEffect(() => {
    setRows((previous) => previous.map((row) => row.role === 'support' || row.source_type === 'manual' || !liveMap[row.name] ? row : { ...row, price_per_lb: liveMap[row.name].price_per_lb, source_type: liveMap[row.name].source_type, source: liveMap[row.name].source }));
  }, [liveMap]);

  function toFeedMap(prices: MetalPrice[]) {
    const map: Record<string, FeedPrice> = {};
    for (const price of prices) {
      if (price.source_type === 'manual') continue;
      map[price.symbol] = { price_per_lb: toPerLb(price.price, price.unit), source_type: price.source_type as Exclude<SourceType, 'manual'>, source: price.source };
    }
    return map;
  }

  async function syncPrices() {
    setRefreshing(true);
    try {
      await refreshPriceFeed();
      setLiveMap(toFeedMap(await fetchPrices()));
      setPricesUpdatedAt(new Date());
    } finally {
      setRefreshing(false);
    }
  }

  const updateRow = (id: string, patch: Partial<CalculatorRow>) => setRows((previous) => previous.map((row) => row.id === id ? { ...row, ...patch } : row));
  const onMaterialChange = (id: string, name: string) => updateRow(id, { name, price_per_lb: liveMap[name]?.price_per_lb ?? 0, source_type: liveMap[name]?.source_type ?? 'manual', source: liveMap[name]?.source ?? 'Manual input' });
  const addRow = (role: 'active_metal' | 'promoter') => setRows((previous) => {
    const row: CalculatorRow = { id: uid(), role, name: '', wt_pct: 0, price_per_lb: 0, source_type: 'manual', source: 'Manual input' };
    const supportIndex = previous.findIndex((item) => item.role === 'support');
    return supportIndex === -1 ? [...previous, row] : [...previous.slice(0, supportIndex), row, ...previous.slice(supportIndex)];
  });
  const removeRow = (id: string) => setRows((previous) => previous.filter((row) => row.id !== id));
  const toggleStep = (stepKey: string) => setSteps((previous) => previous.includes(stepKey) ? previous.filter((item) => item !== stepKey) : [...previous, stepKey]);
  const nonSupportWt = rows.filter((row) => row.role !== 'support').reduce((sum, row) => sum + row.wt_pct, 0);
  const supportWtPct = Math.max(0, 100 - nonSupportWt);
  const selectedSupport = rows.find((row) => row.role === 'support');
  const liveFeedCount = Object.values(liveMap).filter((feed) => feed.source_type === 'live').length;
  const indexedFeedCount = Object.values(liveMap).filter((feed) => feed.source_type === 'indexed').length;
  const activeMetalCount = rows.filter((row) => row.role === 'active_metal' && row.name.trim()).length;
  const isValid = activeMetalCount > 0 && nonSupportWt > 0 && nonSupportWt <= 100;

  function toggleRowSource(id: string) {
    setRows((previous) => previous.map((row) => {
      if (row.id !== id) return row;
      const feed = liveMap[row.name];
      if (!feed) return row;
      return row.source_type === 'manual' ? { ...row, price_per_lb: feed.price_per_lb, source_type: feed.source_type, source: feed.source } : { ...row, source_type: 'manual', source: 'Manual input' };
    }));
  }

  async function handleCalculate() {
    if (!isValid || steps.length === 0) return;
    setLoading(true);
    setError('');

    try {
      const supportRow = rows.find((row) => row.role === 'support');
      if (!supportRow) throw new Error('Support is required.');

      const components: ComponentInput[] = [
        ...rows.filter((row) => row.role !== 'support').map((row) => ({ role: row.role, name: row.name, wt_pct: row.wt_pct, price_per_lb: row.price_per_lb })),
        { role: 'support', name: supportRow.name, wt_pct: supportWtPct, price_per_lb: supportRow.price_per_lb },
      ];
      const input: CostInput = { components, steps, order_size_tons: orderSize };
      const result = await calculateCost(input);
      const snapshot: CalculatorResultSnapshot = {
        result,
        orderSize,
        steps,
        stepLabels: steps.map(formatStepLabel),
        selectedSupportName: supportRow.name,
        activeMetalCount,
        liveFeedCount,
        indexedFeedCount,
        nonSupportWt,
        supportWtPct,
        generatedAt: new Date().toISOString(),
      };

      saveCalculatorResultSnapshot(snapshot);
      setLatestSnapshot(snapshot);
      navigate('/calculator/result');
    } catch (caughtError: unknown) {
      setError(caughtError instanceof Error ? caughtError.message : String(caughtError));
    } finally {
      setLoading(false);
    }
  }

  function sourceChip(row: CalculatorRow) {
    const feed = liveMap[row.name];
    const dotClass = row.source_type === 'live' ? 'bg-emerald-500 shadow-[0_0_12px_rgba(16,185,129,0.32)]' : row.source_type === 'indexed' ? 'bg-amber-500' : 'bg-slate-500';
    const className = `inline-flex items-center gap-2 rounded-full border px-3 py-2 text-xs font-semibold transition ${sourceTone(row.source_type)}`;
    const content = <><span className={`h-2 w-2 rounded-full ${dotClass}`} /><span>{sourceTypeLabel(row.source_type)}</span></>;
    if (!feed) return <span className={`${className} cursor-default`} title={row.source}>{content}</span>;
    const title = row.source_type === 'manual' ? `Manual input. Switch to ${sourceTypeLabel(feed.source_type)} feed from ${feed.source}.` : `${row.source}. Switch back to manual input.`;
    return <button onClick={() => toggleRowSource(row.id)} title={title} className={className}>{content}</button>;
  }

  function priceField(row: CalculatorRow) {
    const locked = row.source_type !== 'manual';
    return (
      <div className="flex flex-none items-center gap-2">
        <span className="text-xs text-slate-500">$</span>
        <input type="number" step="0.01" min="0" value={toDisplay(row.price_per_lb).toFixed(2)} readOnly={locked} onChange={(event) => !locked && updateRow(row.id, { price_per_lb: toInternal(Number(event.target.value)) })} className={`input-base w-32 text-right font-mono ${priceTone(row.source_type)} ${locked ? 'cursor-not-allowed' : ''}`} />
        <span className="text-xs text-slate-500">{fmtLabel}</span>
      </div>
    );
  }

  function renderRows(role: 'active_metal' | 'promoter') {
    const items = rows.filter((row) => row.role === role);
    const copy = role === 'active_metal'
      ? { title: 'Active metals', description: 'These rows drive live feed mapping and the primary catalyst cost basis.', accent: 'bg-[#78f2d0]', button: 'Add active metal', placeholder: 'At least one active metal is required.' }
      : { title: 'Promoters', description: 'Optional promoter metals or additives that influence recipe cost.', accent: 'bg-[#88a8ff]', button: 'Add promoter', placeholder: 'No promoters added yet.' };

    return (
      <div className="space-y-3">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <div className="flex items-center gap-2"><span className={`h-2.5 w-2.5 rounded-full ${copy.accent}`} /><h3 className="cp-heading-sm">{copy.title}</h3></div>
            <p className="mt-1 text-xs leading-6 text-slate-500">{copy.description}</p>
          </div>
          <button onClick={() => addRow(role)} className="cp-button-secondary px-3 py-2 text-xs">{copy.button}</button>
        </div>
        {items.length === 0 ? <div className="rounded-[24px] border border-dashed border-slate-300 bg-white/44 px-4 py-4 text-sm text-slate-500">{copy.placeholder}</div> : (
          <div className="space-y-3">
            {items.map((row) => (
              <div key={row.id} className="surface-ghost p-4">
                <div className="flex flex-wrap items-center gap-3">
                  {role === 'active_metal'
                    ? <select value={row.name} onChange={(event) => onMaterialChange(row.id, event.target.value)} className="input-base min-w-[160px] flex-[1.4_1_220px] pr-10"><option value="">Select metal</option>{KNOWN_METALS.map((metal) => <option key={metal} value={metal}>{metal}</option>)}</select>
                    : <input type="text" list="known-metal-options" value={row.name} onChange={(event) => onMaterialChange(row.id, event.target.value)} placeholder="e.g. Re, K, Sn, Ce" className="input-base min-w-[160px] flex-[1.4_1_220px]" />}
                  <div className="flex flex-none items-center gap-2"><input type="number" step="0.1" min="0" max="100" value={row.wt_pct} onChange={(event) => updateRow(row.id, { wt_pct: Number(event.target.value) })} className="input-base w-28 text-right font-mono" /><span className="text-xs text-slate-500">wt%</span></div>
                  {sourceChip(row)}
                  {priceField(row)}
                  <button onClick={() => removeRow(row.id)} className="flex h-10 w-10 flex-none items-center justify-center rounded-[18px] border border-slate-300 bg-white/74 text-slate-400 transition hover:border-red-300 hover:bg-red-50 hover:text-red-700" aria-label="Remove row">x</button>
                </div>
                <div className="mt-3 text-xs text-slate-500">{row.source}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  function renderLaunchPanel() {
    const latestGenerated = latestSnapshot ? new Date(latestSnapshot.generatedAt).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true }) : null;
    return (
      <section className="surface-card cp-enter flex min-h-[500px] flex-col justify-between overflow-hidden px-4 py-5 sm:px-5">
        <div>
          <span className="section-kicker">Result Board</span>
          <h2 className="cp-heading-xl mt-4">Outputs open on their own review surface.</h2>
          <p className="cp-body-copy mt-3 max-w-xl">Calculate the estimate, move into a dedicated result board, then come back here when you want to tune composition, support, or the selected process path.</p>
        </div>
        <div className="mt-6 space-y-3">
          <div className="surface-ink overflow-hidden p-4">
            <div className="cp-subtle-label !text-slate-400">Latest board</div>
            <div className="mt-3 flex flex-wrap items-end gap-3">
              <div className="font-display text-[clamp(2.25rem,4vw,3.9rem)] leading-none text-white">{latestSnapshot ? `$${toDisplay(latestSnapshot.result.summary.estimated_price_per_lb).toFixed(2)}` : 'Pending'}</div>
              <div className="pb-1 text-lg text-slate-300">{latestSnapshot ? fmtLabel : ''}</div>
            </div>
            <div className="mt-2 text-sm text-slate-300">{latestSnapshot ? `Generated ${latestGenerated} with ${latestSnapshot.selectedSupportName ?? 'support'} as the current basis.` : 'No result board created yet. The first successful estimate will open it automatically.'}</div>
            <div className="mt-4 grid gap-2.5 sm:grid-cols-3 xl:grid-cols-1">
              <MetricTile label="Current scale" value={scale.label} detail={`${orderSize} tons / ${scale.rate}`} dark />
              <MetricTile label="Selected steps" value={String(steps.length)} detail={steps.length > 0 ? `${formatStepLabel(steps[0])}${steps.length > 1 ? ` +${steps.length - 1}` : ''}` : 'Choose at least one'} dark />
              <MetricTile label="Tracked feeds" value={String(liveFeedCount + indexedFeedCount)} detail={`${liveFeedCount} live / ${indexedFeedCount} indexed`} dark />
            </div>
          </div>
          <div className="grid gap-2.5 sm:grid-cols-2">
            <MetricTile label="Recipe load" value={`${nonSupportWt.toFixed(1)} wt%`} detail={`Support auto-fills ${supportWtPct.toFixed(1)} wt%`} />
            <MetricTile label="Support" value={selectedSupport?.name ?? 'Pending'} detail={selectedSupport ? `${selectedSupport.source_type === 'manual' ? 'Manual' : 'Feed-linked'} pricing` : 'Support pending'} />
          </div>
          <button onClick={() => navigate('/calculator/result')} disabled={!latestSnapshot} className="cp-button-secondary w-full justify-center">Open latest result board</button>
        </div>
      </section>
    );
  }

  const validationMessage = isValid
    ? `Recipe balance is valid: ${nonSupportWt.toFixed(1)} wt% actives and promoters, ${supportWtPct.toFixed(1)} wt% support.`
    : activeMetalCount === 0
      ? 'Add at least one active metal before running the estimate.'
      : nonSupportWt > 100
        ? 'Active metals and promoters exceed 100 wt%.'
        : 'Enter a valid non-zero loading for the active portion of the recipe.';

  return (
    <div className="space-y-3">
      <datalist id="known-metal-options">{KNOWN_METALS.map((metal) => <option key={metal} value={metal} />)}</datalist>

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1.08fr)_minmax(320px,0.92fr)]">
        <section className="surface-card cp-enter overflow-hidden px-4 py-4 sm:px-5" style={{ animationDelay: '0.06s' }}>
          <div className="space-y-6">
            <div className="flex flex-col gap-4 border-b border-slate-900/8 pb-4 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <div className="cp-subtle-label">Synthesis Inputs</div>
                <h2 className="cp-heading-xl mt-2">Enter catalyst composition and material pricing</h2>
                <p className="cp-body-copy mt-2 max-w-2xl">Use metal loading, support choice, and raw-material pricing as the starting synthesis inputs, then switch any row back to manual pricing when you need a procurement scenario.</p>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <span className="cp-chip">{pricesUpdatedAt ? `Feed synced ${pricesUpdatedAt.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })}` : 'Feed status pending'}</span>
                <button onClick={syncPrices} disabled={refreshing} className="cp-button-secondary"><span className={`mr-2 inline-flex h-4 w-4 rounded-full border-2 border-current border-t-transparent ${refreshing ? 'animate-spin' : ''}`} />{refreshing ? 'Refreshing feed' : 'Refresh feed'}</button>
              </div>
            </div>

            <div className="grid gap-2.5 md:grid-cols-3">
              <MetricTile label="Tracked metals" value={String(liveFeedCount + indexedFeedCount)} detail={`${liveFeedCount} live / ${indexedFeedCount} indexed`} />
              <MetricTile label="Process steps" value={String(steps.length)} detail={steps.length > 0 ? 'Active process path' : 'Select at least one step'} />
              <MetricTile label="Current scale" value={scale.label} detail={`${orderSize} tons / ${scale.rate}`} />
            </div>

            <div className="space-y-3.5">
              {renderRows('active_metal')}
              {renderRows('promoter')}
              <div className="surface-ghost p-3.5">
                <div><div className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-full bg-[#efc36c]" /><h3 className="cp-heading-sm">Support</h3></div><p className="mt-1 text-xs leading-5 text-slate-500">Support loading closes the balance automatically after actives and promoters are set.</p></div>
                {rows.filter((row) => row.role === 'support').map((row) => (
                  <div key={row.id} className="mt-3.5 flex flex-wrap items-center gap-3">
                    <select value={row.name} onChange={(event) => { const support = SUPPORT_OPTIONS.find((item) => item.name === event.target.value); updateRow(row.id, { name: event.target.value, price_per_lb: support?.price ?? row.price_per_lb, source_type: 'manual', source: 'Manual support default' }); }} className="input-base min-w-[180px] flex-[1.3_1_260px] pr-10">{SUPPORT_OPTIONS.map((support) => <option key={support.name} value={support.name}>{support.name} / {support.note}</option>)}</select>
                    <div className="input-base flex min-w-[170px] flex-none items-center justify-between gap-3 bg-white/76"><span className="text-xs text-slate-500">Auto share</span><span className="font-mono text-slate-950">{supportWtPct.toFixed(1)} wt%</span></div>
                    {priceField(row)}
                  </div>
                ))}
              </div>
            </div>

            <div className="space-y-4 border-t border-slate-900/8 pt-4">
              <div><div className="cp-subtle-label">Step Method</div><h2 className="cp-heading-xl mt-2">Map the lab procedure to industrial process steps</h2><p className="cp-body-copy mt-2 max-w-2xl">Choose the common manufacturing steps that best approximate the lab synthesis, and let order size set the small, medium, or large campaign basis.</p></div>
              <div className="surface-ghost p-3.5">
                <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-end">
                  <div><div className="cp-subtle-label">Order size</div><div className="mt-3 flex flex-wrap items-center gap-3"><input type="number" min="1" step="1" value={orderSize} onChange={(event) => setOrderSize(Math.max(1, Number(event.target.value)))} className="input-base w-32 text-center font-mono" /><span className="text-sm text-slate-500">tons per campaign</span><span className={`rounded-full border px-3 py-1 text-xs font-semibold ${scale.classes}`}>{scale.label} / {scale.rate}</span></div></div>
                  <div className="cp-toolbar">{QUICK_ORDER_SIZES.map((size) => <button key={size} onClick={() => setOrderSize(size)} className={`rounded-[16px] px-3 py-2 text-xs font-semibold transition ${orderSize === size ? 'bg-slate-950 text-white' : 'text-slate-600 hover:bg-white hover:text-slate-900'}`}>{size} tons</button>)}</div>
                </div>
              </div>
              <div className="grid gap-3 lg:grid-cols-2 xl:grid-cols-3">
                {STEP_CATEGORIES.map((category) => (
                  <div key={category} className="surface-ghost p-3.5">
                    <div className="cp-subtle-label">{category}</div>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {ALL_STEPS.filter((step) => step.category === category).map((step) => {
                        const available = (step.scales as readonly Scale[]).includes(currentScale);
                        const checked = steps.includes(step.key);
                        const availabilityLabel = step.scales.length === 3 ? null : step.scales.map((item) => item[0].toUpperCase()).join('/');
                        return <button key={step.key} onClick={() => available && toggleStep(step.key)} disabled={!available} title={available ? step.label : `Not available at ${scale.label.toLowerCase()} scale`} className={`rounded-[16px] border px-3 py-2 text-left text-sm transition ${!available ? 'cursor-not-allowed border-slate-200 bg-slate-100 text-slate-400' : checked ? 'border-teal-200 bg-teal-50 text-teal-700' : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300'}`}><div className="font-medium">{step.label}</div>{availabilityLabel ? <div className="mt-1 text-[10px] uppercase tracking-[0.18em] text-slate-400">{availabilityLabel}</div> : null}</button>;
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className={`rounded-[24px] border px-4 py-4 text-sm ${isValid ? 'border-emerald-200 bg-emerald-50 text-emerald-800' : 'border-amber-200 bg-amber-50 text-amber-800'}`}>{validationMessage}</div>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
              <button onClick={handleCalculate} disabled={loading || !isValid || steps.length === 0} className="cp-button-primary min-w-[250px]">{loading ? <><span className="mr-2 inline-flex h-4 w-4 animate-spin rounded-full border-2 border-slate-950 border-t-transparent" />Calculating board</> : 'Calculate and open result board'}</button>
              <div className="text-xs leading-6 text-slate-500">The result board opens as a separate screen with full output readability and a direct path back to the inputs.</div>
            </div>
            {error ? <div className="rounded-[24px] border border-red-200 bg-red-50 px-4 py-4 text-sm text-red-700"><span className="font-semibold">Calculation failed.</span> {error}</div> : null}
          </div>
        </section>

        {renderLaunchPanel()}
      </div>
    </div>
  );
}
