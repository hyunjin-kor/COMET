import { useEffect, useState } from 'react';
import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import {
  calculateCost,
  fetchPrices,
  refreshPrices as refreshPriceFeed,
  type ComponentInput,
  type CostInput,
  type CostResult,
  type MetalPrice,
} from '../lib/api';
import { useUnit } from '../lib/use-unit';

const TROY_OZ_PER_LB = 14.5833;
const KNOWN_METALS = ['Pt', 'Pd', 'Rh', 'Ru', 'Ir', 'Ni', 'Co', 'Cu', 'Fe', 'Mo', 'W', 'Au', 'Ag', 'Al'];
const CHART_COLORS = ['#78f2d0', '#88a8ff', '#efc36c', '#f3a08d', '#c5b7ff', '#8de0ff'];
const QUICK_ORDER_SIZES = [2, 20, 200];
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

type Role = 'active_metal' | 'promoter' | 'support';
type SourceType = 'live' | 'indexed' | 'manual';
type Scale = 'small' | 'medium' | 'large';
interface FeedPrice { price_per_lb: number; source_type: Exclude<SourceType, 'manual'>; source: string; }
interface Row { id: string; role: Role; name: string; wt_pct: number; price_per_lb: number; source_type: SourceType; source: string; }

let nextId = 1;
const uid = () => String(nextId++);
const toPerLb = (price: number, unit: string) => unit === '$/troy_oz' ? price * TROY_OZ_PER_LB : unit === '$/kg' ? price / 2.20462 : price;
const getScale = (tons: number): Scale => (tons < 5 ? 'small' : tons < 70 ? 'medium' : 'large');
const sourceTypeLabel = (sourceType: SourceType) => sourceType === 'live' ? 'Live' : sourceType === 'indexed' ? 'Indexed' : 'Manual';
const defaultRows = (): Row[] => [
  { id: uid(), role: 'active_metal', name: 'Ni', wt_pct: 20, price_per_lb: 0, source_type: 'manual', source: 'Manual input' },
  { id: uid(), role: 'support', name: 'Al2O3', wt_pct: 80, price_per_lb: 0.5, source_type: 'manual', source: 'Manual support default' },
];
const sourceTone = (sourceType: SourceType) =>
  sourceType === 'live' ? 'border-emerald-200 bg-emerald-50 text-emerald-700' : sourceType === 'indexed' ? 'border-amber-200 bg-amber-50 text-amber-700' : 'border-slate-200 bg-white text-slate-600';
const priceTone = (sourceType: SourceType) =>
  sourceType === 'live' ? 'border-emerald-200 bg-emerald-50/70 text-emerald-800' : sourceType === 'indexed' ? 'border-amber-200 bg-amber-50/70 text-amber-800' : '';
const scaleMeta = (scale: Scale) =>
  scale === 'small'
    ? { label: 'Small', rate: '1 t/day', classes: 'border-violet-200 bg-violet-50 text-violet-700' }
    : scale === 'medium'
      ? { label: 'Medium', rate: '10 t/day', classes: 'border-sky-200 bg-sky-50 text-sky-700' }
      : { label: 'Large', rate: '150 t/day', classes: 'border-teal-200 bg-teal-50 text-teal-700' };

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
  const { unit, toDisplay, toInternal, fmtLabel, catLabel } = useUnit();
  const [rows, setRows] = useState<Row[]>(defaultRows);
  const [steps, setSteps] = useState<string[]>(['mixer_slurry', 'incipient_wetness', 'dryer_rotary_100_300C']);
  const [orderSize, setOrderSize] = useState(20);
  const [result, setResult] = useState<CostResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [liveMap, setLiveMap] = useState<Record<string, FeedPrice>>({});
  const [pricesUpdatedAt, setPricesUpdatedAt] = useState<Date | null>(null);
  const currentScale = getScale(orderSize);
  const scale = scaleMeta(currentScale);

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

  const updateRow = (id: string, patch: Partial<Row>) => setRows((previous) => previous.map((row) => row.id === id ? { ...row, ...patch } : row));
  const onMaterialChange = (id: string, name: string) => updateRow(id, { name, price_per_lb: liveMap[name]?.price_per_lb ?? 0, source_type: liveMap[name]?.source_type ?? 'manual', source: liveMap[name]?.source ?? 'Manual input' });
  const addRow = (role: 'active_metal' | 'promoter') => setRows((previous) => {
    const row = { id: uid(), role, name: '', wt_pct: 0, price_per_lb: 0, source_type: 'manual' as const, source: 'Manual input' };
    const supportIndex = previous.findIndex((item) => item.role === 'support');
    return supportIndex === -1 ? [...previous, row] : [...previous.slice(0, supportIndex), row, ...previous.slice(supportIndex)];
  });
  const removeRow = (id: string) => setRows((previous) => previous.filter((row) => row.id !== id));
  const toggleStep = (stepKey: string) => setSteps((previous) => previous.includes(stepKey) ? previous.filter((item) => item !== stepKey) : [...previous, stepKey]);

  function toggleRowSource(id: string) {
    setRows((previous) => previous.map((row) => {
      if (row.id !== id) return row;
      const feed = liveMap[row.name];
      if (!feed) return row;
      return row.source_type === 'manual'
        ? { ...row, price_per_lb: feed.price_per_lb, source_type: feed.source_type, source: feed.source }
        : { ...row, source_type: 'manual', source: 'Manual input' };
    }));
  }

  const nonSupportWt = rows.filter((row) => row.role !== 'support').reduce((sum, row) => sum + row.wt_pct, 0);
  const supportWtPct = Math.max(0, 100 - nonSupportWt);
  const selectedSupport = rows.find((row) => row.role === 'support');
  const liveFeedCount = Object.values(liveMap).filter((feed) => feed.source_type === 'live').length;
  const indexedFeedCount = Object.values(liveMap).filter((feed) => feed.source_type === 'indexed').length;
  const activeMetalCount = rows.filter((row) => row.role === 'active_metal' && row.name.trim()).length;
  const isValid = activeMetalCount > 0 && nonSupportWt > 0 && nonSupportWt <= 100;
  const altPrice = result ? (unit === 'kg' ? result.summary.estimated_price_per_lb : result.summary.estimated_price_per_kg) : null;
  const altLabel = unit === 'kg' ? '/lb' : '/kg';
  const pieData = result ? [
    ...result.materials.components.map((component) => ({ name: component.role === 'support' ? `${component.name} support` : component.role === 'promoter' ? `${component.name} promoter` : component.name, value: component.cost_pct })),
    { name: 'Processing', value: result.summary.processing_pct },
    { name: 'G&A + margin', value: Math.max(0, 100 - result.summary.materials_pct - result.summary.processing_pct) },
  ] : [];

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
      setResult(await calculateCost(input));
    } catch (caughtError: unknown) {
      setError(caughtError instanceof Error ? caughtError.message : String(caughtError));
    } finally {
      setLoading(false);
    }
  }

  function sourceChip(row: Row) {
    const feed = liveMap[row.name];
    const dotClass = row.source_type === 'live' ? 'bg-emerald-500 shadow-[0_0_12px_rgba(16,185,129,0.32)]' : row.source_type === 'indexed' ? 'bg-amber-500' : 'bg-slate-500';
    const className = `inline-flex items-center gap-2 rounded-full border px-3 py-2 text-xs font-semibold transition ${sourceTone(row.source_type)}`;
    const content = <><span className={`h-2 w-2 rounded-full ${dotClass}`} /><span>{sourceTypeLabel(row.source_type)}</span></>;
    if (!feed) return <span className={`${className} cursor-default`} title={row.source}>{content}</span>;
    const title = row.source_type === 'manual' ? `Manual input. Switch to ${sourceTypeLabel(feed.source_type)} feed from ${feed.source}.` : `${row.source}. Switch back to manual input.`;
    return <button onClick={() => toggleRowSource(row.id)} title={title} className={className}>{content}</button>;
  }

  function priceField(row: Row) {
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
            <div className="flex items-center gap-2"><span className={`h-2.5 w-2.5 rounded-full ${copy.accent}`} /><h3 className="text-sm font-semibold text-slate-950">{copy.title}</h3></div>
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

  function renderResultPanel() {
    if (!result) {
      return (
        <section className="surface-card cp-enter flex min-h-[500px] flex-col justify-between overflow-hidden px-4 py-5 sm:px-5">
          <div>
            <span className="section-kicker">Estimate Outputs</span>
            <h2 className="mt-4 font-display text-[clamp(1.7rem,2.6vw,2.8rem)] leading-[0.98] text-slate-950">Outputs are ready once the estimate basis is complete.</h2>
            <p className="mt-3 max-w-xl text-sm leading-6 text-slate-600">Run the estimate to assemble materials, processing, and selling-price outputs from the current synthesis and business inputs.</p>
          </div>
          <div className="mt-6 space-y-3">
            <div className="surface-ghost overflow-hidden p-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="cp-subtle-label">Inputs Snapshot</div>
                  <div className="mt-2 text-lg font-semibold text-slate-950">Synthesis and business basis</div>
                </div>
                <span className="cp-chip">{selectedSupport?.name ?? 'Support pending'}</span>
              </div>
              <div className="mt-4 grid gap-2.5 sm:grid-cols-3">
                <MetricTile label="Active metals" value={String(activeMetalCount)} detail="Named active inputs" />
                <MetricTile label="Feed mix" value={`${liveFeedCount}/${indexedFeedCount}`} detail="Live / indexed feeds" />
                <MetricTile label="Next action" value="Run estimate" detail="Materials, processing, and margin populate here." />
              </div>
            </div>
            <div className="surface-ink overflow-hidden p-4">
              <div className="grid gap-2.5 lg:grid-cols-3">
                <MetricTile label="Recipe load" value={`${nonSupportWt.toFixed(1)} wt%`} detail={`Support auto-fills ${supportWtPct.toFixed(1)} wt%`} dark />
                <MetricTile label="Selected steps" value={String(steps.length)} detail={steps.length > 0 ? `${steps[0]}${steps.length > 1 ? ` +${steps.length - 1}` : ''}` : 'Choose at least one step'} dark />
                <MetricTile label="Scale window" value={scale.label} detail={`${orderSize} tons / ${scale.rate}`} dark />
              </div>
            </div>
            <div className="grid gap-2.5 sm:grid-cols-2">
              <MetricTile label="Tracked feeds" value={String(liveFeedCount + indexedFeedCount)} detail={`${liveFeedCount} live / ${indexedFeedCount} indexed`} />
              <MetricTile label="Support" value={selectedSupport?.name ?? 'Pending'} detail={`Current unit cost ${selectedSupport ? `$${toDisplay(selectedSupport.price_per_lb).toFixed(2)}${fmtLabel}` : 'N/A'}`} />
            </div>
          </div>
        </section>
      );
    }

    const summaryRows = [
      { label: 'Materials', share: result.summary.materials_pct, value: `$${toDisplay(result.materials.total_materials_cost_per_lb).toFixed(3)}${fmtLabel}` },
      { label: 'Processing', share: result.summary.processing_pct, value: `$${toDisplay(Number(result.step_method.processing_cost_per_lb)).toFixed(3)}${fmtLabel}` },
      { label: 'G&A + margin', share: Math.max(0, 100 - result.summary.materials_pct - result.summary.processing_pct), value: 'Included' },
    ];

    return (
      <section className="surface-card cp-enter overflow-hidden px-4 py-5 sm:px-5">
        <div className="surface-ink relative overflow-hidden p-4">
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(120,242,208,0.24),transparent_0_36%),radial-gradient(circle_at_bottom_right,rgba(239,195,108,0.15),transparent_0_28%)]" />
          <div className="relative grid gap-3 xl:grid-cols-[minmax(0,1.05fr)_300px]">
            <div>
              <div className="cp-subtle-label !text-slate-400">Estimated selling price</div>
              <div className="mt-4 flex flex-wrap items-end gap-3">
                <div className="font-display text-[clamp(2.6rem,5vw,4.7rem)] leading-none text-white">${toDisplay(result.summary.estimated_price_per_lb).toFixed(2)}</div>
                <div className="pb-1 text-lg text-slate-300">{fmtLabel}</div>
              </div>
              <div className="mt-3 text-sm text-slate-300">Alternate view: {altPrice != null ? `$${altPrice.toFixed(2)}${altLabel}` : 'n/a'}</div>
            </div>
            <div className="grid gap-2.5 sm:grid-cols-3 xl:grid-cols-1">
              <MetricTile label="Scale" value={result.step_method.scale} detail={`${orderSize} tons order`} dark />
              <MetricTile label="Campaign" value={`${Number(result.step_method.campaign_days).toFixed(1)} d`} detail={`${steps.length} selected steps`} dark />
              <MetricTile label="Margin" value={`${Number(result.step_method.margin_pct).toFixed(1)}%`} detail="Selling margin contribution" dark />
            </div>
          </div>
        </div>

        <div className="mt-4 grid gap-3 xl:grid-cols-[0.88fr_1.12fr]">
          <div className="space-y-3">
            <div className="surface-ghost p-4">
              <div className="flex items-center justify-between gap-3"><div><div className="cp-subtle-label">Cost Structure</div><div className="mt-2 text-xl font-semibold text-slate-950">Materials vs processing</div></div><span className="cp-chip">{result.materials.components.length} materials</span></div>
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

            <div className="surface-ghost p-4">
              <div className="text-sm font-semibold text-slate-950">Breakdown wheel</div>
              <div className="mt-1 text-xs text-slate-500">Materials, processing, and selling adjustments.</div>
              <div className="mt-3 h-[280px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={pieData} innerRadius={72} outerRadius={108} dataKey="value" paddingAngle={3} stroke="transparent">
                      {pieData.map((entry, index) => <Cell key={entry.name} fill={CHART_COLORS[index % CHART_COLORS.length]} />)}
                    </Pie>
                    <Tooltip formatter={(value) => [`${Number(value).toFixed(1)}%`, 'Share']} contentStyle={{ borderRadius: 18, border: '1px solid rgba(31,47,72,0.10)', background: 'rgba(255,251,245,0.96)', color: '#142033', fontSize: 12, boxShadow: '0 18px 48px rgba(23,34,51,0.12)' }} />
                    <Legend iconSize={10} iconType="circle" wrapperStyle={{ color: '#66748b', fontSize: 12 }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          <div className="surface-ghost p-4">
            <div className="flex items-center justify-between gap-3"><div><div className="cp-subtle-label">Material Ledger</div><div className="mt-2 text-xl font-semibold text-slate-950">Component-level catalyst cost</div></div><span className="cp-chip">{selectedSupport?.name ?? 'Support'}</span></div>
            <div className="mt-3 overflow-hidden rounded-[22px] border border-slate-900/8 bg-white/56">
              <div className="grid grid-cols-[minmax(0,1.4fr)_90px_110px_110px_72px] gap-3 border-b border-slate-900/8 bg-white/46 px-4 py-3 text-[11px] uppercase tracking-[0.18em] text-slate-500"><span>Material</span><span className="text-right">wt%</span><span className="text-right">Unit</span><span className="text-right">Catalyst</span><span className="text-right">Share</span></div>
              <div className="divide-y divide-slate-900/8">
                {result.materials.components.map((component, index) => (
                  <div key={`${component.name}-${component.role}`} className="grid grid-cols-[minmax(0,1.4fr)_90px_110px_110px_72px] gap-3 px-4 py-3 text-sm">
                    <div className="flex min-w-0 items-center gap-2.5"><span className="h-2.5 w-2.5 flex-none rounded-full" style={{ backgroundColor: CHART_COLORS[index % CHART_COLORS.length] }} /><div className="min-w-0"><div className="truncate text-slate-950">{component.name}</div><div className="text-xs text-slate-500">{component.role}</div></div></div>
                    <span className="text-right font-mono text-slate-700">{(component.wt_frac * 100).toFixed(1)}</span>
                    <span className="text-right font-mono text-slate-700">${toDisplay(component.price_per_lb).toFixed(3)}</span>
                    <span className="text-right font-mono text-slate-950">${toDisplay(component.cost_per_lb_cat).toFixed(3)}</span>
                    <span className="text-right font-mono text-slate-500">{component.cost_pct}%</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="mt-3 rounded-[22px] border border-slate-900/8 bg-white/60 p-4">
              <div className="flex items-center justify-between gap-3 text-sm"><span className="text-slate-600">Total material cost</span><span className="font-semibold text-slate-950">${toDisplay(result.materials.total_materials_cost_per_lb).toFixed(4)}{catLabel}</span></div>
              <div className="mt-2 text-xs leading-6 text-slate-500">CatCost step basis with backend escalation and margin treatment applied in the calculation engine.</div>
            </div>
          </div>
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

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1.02fr)_minmax(0,0.98fr)]">
        <section className="surface-card cp-enter overflow-hidden px-4 py-4 sm:px-5" style={{ animationDelay: '0.06s' }}>
          <div className="space-y-6">
            <div className="flex flex-col gap-4 border-b border-slate-900/8 pb-4 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <div className="cp-subtle-label">Synthesis Inputs</div>
                <h2 className="mt-2 text-2xl font-semibold text-slate-950">Enter catalyst composition and material pricing</h2>
                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">Use metal loading, support choice, and raw-material pricing as the starting synthesis inputs, then switch any row back to manual pricing when you need a procurement scenario.</p>
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
                <div><div className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-full bg-[#efc36c]" /><h3 className="text-sm font-semibold text-slate-950">Support</h3></div><p className="mt-1 text-xs leading-5 text-slate-500">Support loading closes the balance automatically after actives and promoters are set.</p></div>
                {rows.filter((row) => row.role === 'support').map((row) => (
                  <div key={row.id} className="mt-3.5 flex flex-wrap items-center gap-3">
                    <select value={row.name} onChange={(event) => { const support = SUPPORT_OPTIONS.find((item) => item.name === event.target.value); updateRow(row.id, { name: event.target.value, price_per_lb: support?.price ?? row.price_per_lb, source_type: 'manual', source: 'Manual support default' }); }} className="input-base min-w-[180px] flex-[1.3_1_260px] pr-10">
                      {SUPPORT_OPTIONS.map((support) => <option key={support.name} value={support.name}>{support.name} / {support.note}</option>)}
                    </select>
                    <div className="input-base flex min-w-[170px] flex-none items-center justify-between gap-3 bg-white/76"><span className="text-xs text-slate-500">Auto share</span><span className="font-mono text-slate-950">{supportWtPct.toFixed(1)} wt%</span></div>
                    {priceField(row)}
                  </div>
                ))}
              </div>
            </div>

            <div className="space-y-4 border-t border-slate-900/8 pt-4">
              <div><div className="cp-subtle-label">Step Method</div><h2 className="mt-2 text-2xl font-semibold text-slate-950">Map the lab procedure to industrial process steps</h2><p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">Choose the common manufacturing steps that best approximate the lab synthesis, and let order size set the small, medium, or large campaign basis.</p></div>
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
              <button onClick={handleCalculate} disabled={loading || !isValid || steps.length === 0} className="cp-button-primary min-w-[220px]">{loading ? <><span className="mr-2 inline-flex h-4 w-4 animate-spin rounded-full border-2 border-slate-950 border-t-transparent" />Calculating estimate</> : 'Calculate estimate'}</button>
              <div className="text-xs leading-6 text-slate-500">The estimate returns materials, processing, and selling-price contributions in one CatCost-style output bundle.</div>
            </div>
            {error ? <div className="rounded-[24px] border border-red-200 bg-red-50 px-4 py-4 text-sm text-red-700"><span className="font-semibold">Calculation failed.</span> {error}</div> : null}
          </div>
        </section>

        {renderResultPanel()}
      </div>
    </div>
  );
}
