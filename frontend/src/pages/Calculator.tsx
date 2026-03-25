import { useEffect, useState } from 'react';
import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import {
  calculateCost,
  fetchPrices,
  type ComponentInput,
  type CostInput,
  type CostResult,
  type MetalPrice,
} from '../lib/api';
import { useUnit } from '../lib/use-unit';

const TROY_OZ_PER_LB = 14.5833;
const KNOWN_METALS = ['Pt', 'Pd', 'Rh', 'Ru', 'Ir', 'Ni', 'Co', 'Cu', 'Fe', 'Mo', 'W', 'Au', 'Ag', 'Al'];
const CHART_COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];
const SUPPORT_OPTIONS = [
  { name: 'Al2O3', price: 0.5, note: 'Alumina - most common' },
  { name: 'SiO2', price: 0.3, note: 'Silica' },
  { name: 'TiO2', price: 1.2, note: 'Titania' },
  { name: 'Carbon', price: 1.5, note: 'Activated carbon' },
  { name: 'ZSM-5', price: 3, note: 'Zeolite (MFI)' },
  { name: 'USY', price: 2.5, note: 'Zeolite (FAU) - FCC' },
  { name: 'CeO2', price: 2, note: 'Ceria' },
  { name: 'MgO', price: 0.4, note: 'Magnesia' },
  { name: 'ZrO2', price: 5, note: 'Zirconia' },
  { name: 'SiO2-Al2O3', price: 0.8, note: 'Silica-alumina' },
] as const;
const SUPPORT_OPTION_MAP = Object.fromEntries(SUPPORT_OPTIONS.map((option) => [option.name, option]));
const ALL_STEPS = [
  { key: 'mixer_dry_blender', label: 'Dry Blender', category: 'Mixing', scales: ['small', 'medium', 'large'] },
  { key: 'mixer_slurry', label: 'Slurry Mixer', category: 'Mixing', scales: ['small', 'medium', 'large'] },
  { key: 'incipient_wetness', label: 'Incipient Wetness', category: 'Impregnation', scales: ['small', 'medium', 'large'] },
  { key: 'reactor_simple', label: 'Reactor - Simple', category: 'Reaction', scales: ['small', 'medium', 'large'] },
  { key: 'reactor_multistep', label: 'Reactor - Multistep', category: 'Reaction', scales: ['small', 'medium', 'large'] },
  { key: 'crystallizer', label: 'Crystallizer', category: 'Reaction', scales: ['small', 'medium', 'large'] },
  { key: 'dryer_batch_vacuum_tray', label: 'Dryer - Batch Vacuum', category: 'Drying', scales: ['small'] },
  { key: 'dryer_rotary_40_100C', label: 'Dryer - Rotary 40-100 C', category: 'Drying', scales: ['small', 'medium', 'large'] },
  { key: 'dryer_rotary_100_300C', label: 'Dryer - Rotary 100-300 C', category: 'Drying', scales: ['small', 'medium', 'large'] },
  { key: 'dryer_spray', label: 'Spray Dryer', category: 'Drying', scales: ['medium', 'large'] },
  { key: 'kiln_batch', label: 'Kiln - Batch', category: 'Calcination', scales: ['small'] },
  { key: 'kiln_continuous_direct', label: 'Kiln - Direct', category: 'Calcination', scales: ['medium', 'large'] },
  { key: 'kiln_continuous_indirect', label: 'Kiln - Indirect', category: 'Calcination', scales: ['medium', 'large'] },
  { key: 'filter_belt_vacuum', label: 'Belt Vacuum Filter', category: 'Separation', scales: ['small', 'medium', 'large'] },
  { key: 'filter_plate_frame', label: 'Plate & Frame Filter', category: 'Separation', scales: ['small'] },
  { key: 'filter_rotary_vacuum', label: 'Rotary Vacuum Filter', category: 'Separation', scales: ['medium', 'large'] },
  { key: 'extruder_with_feeder', label: 'Extruder + Feeder', category: 'Forming', scales: ['small', 'medium', 'large'] },
  { key: 'ball_forming', label: 'Ball Forming', category: 'Forming', scales: ['small', 'medium'] },
  { key: 'mill', label: 'Mill', category: 'Size Reduction', scales: ['small', 'medium', 'large'] },
  { key: 'flare', label: 'Flare', category: 'Utilities', scales: ['small', 'medium', 'large'] },
  { key: 'scrubber_nox', label: 'NOx Scrubber', category: 'Utilities', scales: ['small', 'medium', 'large'] },
] as const;
const STEP_CATEGORIES = [...new Set(ALL_STEPS.map((step) => step.category))];

type Role = 'active_metal' | 'promoter' | 'support';
type SourceType = 'live' | 'indexed' | 'manual';
type Scale = 'small' | 'medium' | 'large';

interface FeedPrice {
  price_per_lb: number;
  source_type: Exclude<SourceType, 'manual'>;
  source: string;
}

interface Row {
  id: string;
  role: Role;
  name: string;
  wt_pct: number;
  price_per_lb: number;
  source_type: SourceType;
  source: string;
}

let nextId = 1;
const uid = () => String(nextId++);

function toPerLb(price: number, unit: string): number {
  if (unit === '$/troy_oz') return price * TROY_OZ_PER_LB;
  if (unit === '$/kg') return price / 2.20462;
  return price;
}

function getScale(orderSizeTons: number): Scale {
  if (orderSizeTons < 5) return 'small';
  if (orderSizeTons < 70) return 'medium';
  return 'large';
}

function sourceTypeLabel(sourceType: SourceType) {
  return sourceType === 'live' ? 'LIVE' : sourceType === 'indexed' ? 'INDEXED' : 'MANUAL';
}

function sourceBadgeClass(sourceType: SourceType) {
  if (sourceType === 'live') return 'border-emerald-300 bg-emerald-50 text-emerald-700 hover:bg-emerald-100';
  if (sourceType === 'indexed') return 'border-amber-200 bg-amber-50 text-amber-700 hover:bg-amber-100';
  return 'border-slate-200 bg-slate-100 text-slate-500 hover:bg-slate-200';
}

function priceFieldClass(sourceType: SourceType) {
  if (sourceType === 'live') return 'border-emerald-300 bg-emerald-50 text-emerald-800';
  if (sourceType === 'indexed') return 'border-amber-200 bg-amber-50 text-amber-800';
  return 'border-slate-200 bg-white';
}

function priceInputClass(sourceType: SourceType) {
  if (sourceType === 'live') return 'cursor-not-allowed select-none text-emerald-800';
  if (sourceType === 'indexed') return 'cursor-not-allowed select-none text-amber-800';
  return 'text-slate-800';
}

function defaultRows(): Row[] {
  return [
    { id: uid(), role: 'active_metal', name: 'Ni', wt_pct: 20, price_per_lb: 0, source_type: 'manual', source: 'Manual input' },
    { id: uid(), role: 'support', name: 'Al2O3', wt_pct: 80, price_per_lb: 0.5, source_type: 'manual', source: 'Manual support default' },
  ];
}

export default function Calculator() {
  const { unit, toDisplay, toInternal, fmtLabel, catLabel } = useUnit();
  const [rows, setRows] = useState<Row[]>(defaultRows);
  const [steps, setSteps] = useState<string[]>(['mixer_slurry', 'incipient_wetness', 'dryer_rotary_100_300C']);
  const [orderSize, setOrderSize] = useState(20);
  const [result, setResult] = useState<CostResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [liveMap, setLiveMap] = useState<Record<string, FeedPrice>>({});
  const [pricesUpdatedAt, setPricesUpdatedAt] = useState<Date | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const currentScale = getScale(orderSize);

  useEffect(() => {
    setSteps((prev) =>
      prev.filter((key) => {
        const step = ALL_STEPS.find((item) => item.key === key);
        return step ? (step.scales as readonly Scale[]).includes(currentScale) : false;
      }),
    );
  }, [currentScale]);

  function toFeedMap(prices: MetalPrice[]) {
    const map: Record<string, FeedPrice> = {};
    for (const price of prices) {
      if (price.source_type === 'manual') continue;
      map[price.symbol] = {
        price_per_lb: toPerLb(price.price, price.unit),
        source_type: price.source_type as Exclude<SourceType, 'manual'>,
        source: price.source,
      };
    }
    return map;
  }

  useEffect(() => {
    fetchPrices()
      .then((prices) => {
        const map = toFeedMap(prices);
        setLiveMap(map);
        setPricesUpdatedAt(new Date());
        setRows((prev) =>
          prev.map((row) =>
            row.role === 'support' || !map[row.name]
              ? row
              : { ...row, price_per_lb: map[row.name].price_per_lb, source_type: map[row.name].source_type, source: map[row.name].source },
          ),
        );
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    setRows((prev) =>
      prev.map((row) =>
        row.role === 'support' || row.source_type === 'manual' || !liveMap[row.name]
          ? row
          : { ...row, price_per_lb: liveMap[row.name].price_per_lb, source_type: liveMap[row.name].source_type, source: liveMap[row.name].source },
      ),
    );
  }, [liveMap]);

  async function refreshPrices() {
    setRefreshing(true);
    try {
      await fetch('/api/prices/refresh', { method: 'POST' });
      setLiveMap(toFeedMap(await fetchPrices()));
      setPricesUpdatedAt(new Date());
    } finally {
      setRefreshing(false);
    }
  }

  function updateRow(id: string, patch: Partial<Row>) {
    setRows((prev) => prev.map((row) => (row.id === id ? { ...row, ...patch } : row)));
  }

  function onMetalChange(id: string, name: string) {
    const feed = liveMap[name];
    updateRow(id, {
      name,
      price_per_lb: feed?.price_per_lb ?? 0,
      source_type: feed?.source_type ?? 'manual',
      source: feed?.source ?? 'Manual input',
    });
  }

  function toggleRowSource(id: string) {
    setRows((prev) =>
      prev.map((row) => {
        if (row.id !== id) return row;
        const feed = liveMap[row.name];
        if (!feed) return row;
        return row.source_type === 'manual'
          ? { ...row, price_per_lb: feed.price_per_lb, source_type: feed.source_type, source: feed.source }
          : { ...row, source_type: 'manual', source: 'Manual input' };
      }),
    );
  }

  function addRow(role: 'active_metal' | 'promoter') {
    const newRow: Row = { id: uid(), role, name: '', wt_pct: 0, price_per_lb: 0, source_type: 'manual', source: 'Manual input' };
    setRows((prev) => {
      const supportIndex = prev.findIndex((row) => row.role === 'support');
      return supportIndex === -1 ? [...prev, newRow] : [...prev.slice(0, supportIndex), newRow, ...prev.slice(supportIndex)];
    });
  }

  function removeRow(id: string) {
    setRows((prev) => prev.filter((row) => row.id !== id));
  }

  const nonSupportWt = rows.filter((row) => row.role !== 'support').reduce((sum, row) => sum + row.wt_pct, 0);
  const supportWtPct = Math.max(0, 100 - nonSupportWt);
  const hasActiveMetal = rows.some((row) => row.role === 'active_metal' && row.name.trim() !== '');
  const isValid = hasActiveMetal && nonSupportWt > 0 && nonSupportWt <= 100;
  const scaleLabel = currentScale === 'small' ? 'Small / 1 t/day' : currentScale === 'medium' ? 'Medium / 10 t/day' : 'Large / 150 t/day';
  const scaleBadge = currentScale === 'small' ? 'bg-violet-100 text-violet-700' : currentScale === 'medium' ? 'bg-blue-100 text-blue-700' : 'bg-teal-100 text-teal-700';
  const trackedFeeds = Object.keys(liveMap).length;

  async function handleCalculate() {
    if (!isValid || steps.length === 0) return;
    setLoading(true);
    setError('');
    try {
      const supportRow = rows.find((row) => row.role === 'support');
      if (!supportRow) throw new Error('Support is required');
      const components: ComponentInput[] = [
        ...rows.filter((row) => row.role !== 'support').map((row) => ({ role: row.role, name: row.name, wt_pct: row.wt_pct, price_per_lb: row.price_per_lb })),
        { role: 'support', name: supportRow.name, wt_pct: supportWtPct, price_per_lb: supportRow.price_per_lb },
      ];
      const input: CostInput = { components, steps, order_size_tons: orderSize };
      setResult(await calculateCost(input));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  const pieData = result
    ? [
        ...result.materials.components.map((component) => ({
          name: `${component.name}${component.role === 'support' ? ' (Support)' : component.role === 'promoter' ? ' (Promoter)' : ''}`,
          value: component.cost_pct,
        })),
        { name: 'Processing', value: result.summary.processing_pct },
        { name: 'G&A + Margin', value: Math.max(0, 100 - result.summary.materials_pct - result.summary.processing_pct) },
      ]
    : [];

  function sourceTitle(row: Row, feed?: FeedPrice) {
    if (row.source_type === 'manual') {
      return feed ? `Manual input. Click to use ${sourceTypeLabel(feed.source_type)} pricing from ${feed.source}.` : 'Manual input. No tracked feed is available.';
    }
    return `${row.source}. Click to switch to manual input.`;
  }

  function renderSourceChip(row: Row) {
    const feed = liveMap[row.name];
    const dot = row.source_type === 'live' ? 'bg-emerald-500 animate-pulse' : row.source_type === 'indexed' ? 'bg-amber-400' : 'bg-slate-400';
    const className = `flex items-center gap-1 rounded-lg border px-2 py-1 text-[10px] font-bold whitespace-nowrap transition-all ${sourceBadgeClass(row.source_type)}`;
    const content = (
      <>
        <span className={`h-1.5 w-1.5 rounded-full ${dot}`} />
        {sourceTypeLabel(row.source_type)}
      </>
    );
    return feed ? (
      <button onClick={() => toggleRowSource(row.id)} title={sourceTitle(row, feed)} className={className}>
        {content}
      </button>
    ) : (
      <span title={sourceTitle(row)} className={`${className} cursor-default`}>
        {content}
      </span>
    );
  }

  function renderPriceField(row: Row) {
    const locked = row.source_type !== 'manual';
    return (
      <div className={`flex items-center gap-2 rounded-2xl border px-3 py-2 ${priceFieldClass(row.source_type)}`}>
        <span className="text-[11px] text-slate-400">$</span>
        <input
          type="number"
          step="0.01"
          min="0"
          value={toDisplay(row.price_per_lb).toFixed(2)}
          readOnly={locked}
          onChange={(e) => !locked && updateRow(row.id, { price_per_lb: toInternal(+e.target.value) })}
          className={`w-16 border-0 bg-transparent p-0 text-right text-sm font-medium font-mono focus:outline-none ${priceInputClass(row.source_type)}`}
        />
        <span className="text-[11px] text-slate-400">{fmtLabel}</span>
      </div>
    );
  }

  function renderRows(role: 'active_metal' | 'promoter') {
    const items = rows.filter((row) => row.role === role);
    const accent = role === 'active_metal'
      ? { dot: 'bg-indigo-500', text: 'text-indigo-700', button: 'text-indigo-600 hover:text-indigo-800', title: 'Active Metals', empty: 'No active metals yet.' }
      : { dot: 'bg-purple-500', text: 'text-purple-700', button: 'text-purple-600 hover:text-purple-800', title: 'Promoters', empty: 'No promoters added.' };
    return (
      <div>
        <div className="mb-2 flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <span className={`h-2 w-2 rounded-full ${accent.dot}`} />
            <span className={`text-xs font-semibold uppercase tracking-wider ${accent.text}`}>
              {accent.title} {role === 'promoter' && <span className="font-normal normal-case text-slate-400">(optional)</span>}
            </span>
          </div>
          <button onClick={() => addRow(role)} className={`text-xs font-semibold transition-colors ${accent.button}`}>+ Add</button>
        </div>
        <div className="space-y-2">
          {items.map((row) => (
            <div key={row.id} className="flex flex-wrap items-center gap-2 rounded-2xl border border-slate-200/80 bg-slate-50/70 p-2.5">
              {role === 'active_metal' ? (
                <select value={row.name} onChange={(e) => onMetalChange(row.id, e.target.value)} className="input-base min-w-[11rem] flex-[1_1_15rem] bg-white">
                  <option value="">Select metal</option>
                  {KNOWN_METALS.map((metal) => <option key={metal} value={metal}>{metal}</option>)}
                </select>
              ) : (
                <input type="text" list="known-metal-options" value={row.name} onChange={(e) => onMetalChange(row.id, e.target.value)} placeholder="e.g. Re, K, Sn, Ce" className="input-base min-w-[11rem] flex-[1_1_15rem] bg-white" />
              )}
              <div className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-3 py-2">
                <input type="number" step="0.1" min="0" max="100" value={row.wt_pct} onChange={(e) => updateRow(row.id, { wt_pct: +e.target.value })} className="w-11 border-0 bg-transparent p-0 text-right text-sm font-medium font-mono text-slate-800 focus:outline-none" />
                <span className="text-[11px] text-slate-400">wt%</span>
              </div>
              {renderSourceChip(row)}
              {renderPriceField(row)}
              <button onClick={() => removeRow(row.id)} className="flex h-6 w-6 items-center justify-center rounded-lg text-base text-slate-300 transition-colors hover:bg-red-50 hover:text-red-500" aria-label="Remove row">x</button>
              <p className="basis-full pl-1 text-[11px] text-slate-400">{row.source_type === 'manual' ? 'Using manual input for this material.' : row.source}</p>
            </div>
          ))}
          {items.length === 0 && <p className="pl-3.5 text-xs text-slate-400">{accent.empty}</p>}
        </div>
      </div>
    );
  }

  function renderResultsPanel() {
    if (!result) return null;
    return (
      <div className="self-start space-y-4 xl:sticky xl:top-7">
        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-600 p-5 text-white shadow-lg shadow-blue-500/20">
            <div className="mb-2 text-xs font-medium uppercase tracking-wider opacity-70">Estimated Cost</div>
            <div className="text-3xl font-bold tracking-tight">${toDisplay(result.summary.estimated_price_per_lb).toFixed(2)}<span className="ml-0.5 text-sm font-normal opacity-60">{fmtLabel}</span></div>
            <div className="mt-1 text-sm opacity-60">${(unit === 'kg' ? result.summary.estimated_price_per_lb : result.summary.estimated_price_per_kg).toFixed(2)}/{unit === 'kg' ? 'lb' : 'kg'}</div>
          </div>
          <div className="rounded-2xl bg-gradient-to-br from-slate-700 to-slate-800 p-5 text-white shadow-lg">
            <div className="mb-2 text-xs font-medium uppercase tracking-wider opacity-70">Production Scale</div>
            <div className="text-3xl font-bold capitalize tracking-tight">{result.step_method.scale}</div>
            <div className="mt-1 text-sm opacity-60">{Number(result.step_method.campaign_days).toFixed(1)}-day campaign</div>
          </div>
        </div>
        <div className="surface-card overflow-hidden">
          <div className="px-5 pb-2 pt-4"><h3 className="text-sm font-semibold text-slate-700">Cost Breakdown</h3></div>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={52} outerRadius={80} dataKey="value" paddingAngle={2}>
                {pieData.map((_, index) => <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} strokeWidth={0} />)}
              </Pie>
              <Tooltip formatter={(value) => [`${Number(value).toFixed(1)}%`, 'Share']} contentStyle={{ borderRadius: 10, border: '1px solid #e2e8f0', fontSize: 12 }} />
              <Legend iconSize={8} iconType="circle" wrapperStyle={{ fontSize: 11, paddingTop: 4 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="surface-card p-5">
          <h3 className="mb-3 text-sm font-semibold text-slate-700">Materials Breakdown</h3>
          <div className="space-y-2.5">
            {result.materials.components.map((component, index) => (
              <div key={index} className="flex items-center gap-2.5">
                <span className="h-2.5 w-2.5 flex-shrink-0 rounded-full" style={{ background: CHART_COLORS[index % CHART_COLORS.length] }} />
                <span className="flex-1 truncate text-sm font-medium text-slate-700">{component.name}</span>
                <span className="w-14 text-right text-xs tabular-nums text-slate-400">{(component.wt_frac * 100).toFixed(1)} wt%</span>
                <span className="w-20 text-right font-mono text-xs tabular-nums text-slate-500">${toDisplay(component.price_per_lb).toFixed(3)}{fmtLabel}</span>
                <span className="w-24 text-right font-mono text-xs tabular-nums text-slate-700">${toDisplay(component.cost_per_lb_cat).toFixed(4)}{catLabel}</span>
                <span className="w-9 text-right text-xs font-medium tabular-nums text-slate-400">{component.cost_pct}%</span>
              </div>
            ))}
            <div className="flex justify-between border-t border-slate-100 pt-2.5 text-sm font-semibold text-slate-800"><span>Total Materials</span><span className="font-mono">${toDisplay(result.materials.total_materials_cost_per_lb).toFixed(4)}{fmtLabel}</span></div>
          </div>
        </div>
        <div className="surface-card p-5">
          <h3 className="mb-3 text-sm font-semibold text-slate-700">Cost Summary</h3>
          <div className="overflow-hidden rounded-xl border border-slate-100">
            <div className="flex items-center justify-between border-b border-slate-100 px-4 py-2.5"><span className="text-sm text-slate-600">Materials</span><div className="flex items-center gap-2"><span className="rounded-full bg-slate-100 px-1.5 py-0.5 text-xs text-slate-400">{result.summary.materials_pct}%</span><span className="text-sm font-medium font-mono text-slate-700">${toDisplay(result.materials.total_materials_cost_per_lb).toFixed(4)}{fmtLabel}</span></div></div>
            <div className="flex items-center justify-between border-b border-slate-100 px-4 py-2.5"><span className="text-sm text-slate-600">Step Method Processing</span><div className="flex items-center gap-2"><span className="rounded-full bg-slate-100 px-1.5 py-0.5 text-xs text-slate-400">{result.summary.processing_pct}%</span><span className="text-sm font-medium font-mono text-slate-700">${toDisplay(Number(result.step_method.processing_cost_per_lb)).toFixed(4)}{fmtLabel}</span></div></div>
            <div className="flex items-center justify-between border-b border-slate-100 px-4 py-2.5"><span className="text-sm text-slate-400">G&A + SARD</span><span className="text-sm font-mono text-slate-400">included</span></div>
            <div className="flex items-center justify-between border-b border-slate-100 px-4 py-2.5"><span className="text-sm text-slate-400">Selling Margin ({Number(result.step_method.margin_pct).toFixed(1)}%)</span><span className="text-sm font-mono text-slate-400">included</span></div>
            <div className="flex items-center justify-between border-t border-blue-100 bg-gradient-to-r from-blue-50 to-indigo-50 px-4 py-3"><span className="text-sm font-bold text-blue-800">Estimated Selling Price</span><span className="text-sm font-bold font-mono text-blue-800">${toDisplay(result.summary.estimated_price_per_lb).toFixed(4)}{fmtLabel}&nbsp;=&nbsp;${(unit === 'kg' ? result.summary.estimated_price_per_lb : result.summary.estimated_price_per_kg).toFixed(2)}/{unit === 'kg' ? 'lb' : 'kg'}</span></div>
          </div>
          <p className="mt-2.5 text-xs text-slate-400">* CatCost Step Method basis. 2017-{new Date().getFullYear()} ChemPPI escalation applied.</p>
        </div>
      </div>
    );
  }

  function renderEmptyPanel() {
    return (
      <div className="surface-card flex min-h-[520px] flex-col justify-between overflow-hidden p-7">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">Results Canvas</p>
            <h3 className="mt-3 text-2xl font-semibold tracking-[-0.03em] text-slate-900">Estimate preview</h3>
            <p className="mt-2 max-w-sm text-sm leading-6 text-slate-500">Run a calculation to see selling price, material share, and processing cost in one place.</p>
          </div>
          <div className="rounded-full border border-emerald-100 bg-emerald-50 px-3 py-1 text-[11px] font-medium text-emerald-700">Ready to calculate</div>
        </div>
        <div className="flex flex-col items-center justify-center rounded-[28px] border border-dashed border-slate-200 bg-[linear-gradient(135deg,rgba(59,130,246,0.05),rgba(255,255,255,0.65))] px-6 py-14 text-center">
          <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-3xl border border-slate-200 bg-white shadow-sm">
            <svg viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="1.5" className="h-7 w-7"><path d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2V9M9 21H5a2 2 0 01-2-2V9m0 0h18" strokeLinecap="round" strokeLinejoin="round" /></svg>
          </div>
          <div className="text-base font-semibold text-slate-700">Results appear here</div>
          <div className="mt-2 max-w-sm text-sm leading-6 text-slate-500">Enter composition and process steps, then run Calculate to generate the cost summary and breakdown.</div>
        </div>
        <div className="grid gap-3 sm:grid-cols-3">
          <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3"><div className="text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">Materials</div><div className="mt-2 text-sm font-medium text-slate-700">Active metal, promoter, support</div></div>
          <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3"><div className="text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">Processing</div><div className="mt-2 text-sm font-medium text-slate-700">Campaign duration and step cost</div></div>
          <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3"><div className="text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">Decision</div><div className="mt-2 text-sm font-medium text-slate-700">Selling price and cost balance</div></div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full px-7 py-7">
      <div className="mb-7 flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <span className="section-kicker">Catalyst Workspace</span>
          <h2 className="mt-3 text-[30px] font-semibold tracking-[-0.03em] text-slate-900">Catalyst Cost Calculator</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">Combine composition, price sources, and plant-scale steps to estimate catalyst selling cost.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <span className="rounded-full border border-slate-200 bg-white/80 px-3 py-1.5 text-xs font-medium text-slate-600 shadow-sm">{trackedFeeds} tracked feeds</span>
          <span className="rounded-full border border-slate-200 bg-white/80 px-3 py-1.5 text-xs font-medium text-slate-600 shadow-sm">Live + indexed + manual pricing</span>
          <span className="rounded-full border border-slate-200 bg-white/80 px-3 py-1.5 text-xs font-medium text-slate-600 shadow-sm">{steps.length} process steps selected</span>
        </div>
      </div>

      <datalist id="known-metal-options">{KNOWN_METALS.map((metal) => <option key={metal} value={metal} />)}</datalist>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-[minmax(0,1.06fr)_minmax(380px,0.94fr)]">
        <div className="space-y-4">
          <div className="surface-card space-y-4 p-6">
            <div className="flex flex-wrap items-start justify-between gap-3 border-b border-slate-100 pb-4">
              <h3 className="flex items-center gap-2.5 text-sm font-semibold text-slate-800"><span className="flex h-5 w-5 items-center justify-center rounded-full bg-indigo-600 text-[10px] font-bold text-white">1</span>Catalyst Composition</h3>
              <div className="flex flex-wrap items-center gap-2">
                {pricesUpdatedAt && <span className="text-[11px] text-slate-400">Prices refreshed {pricesUpdatedAt.toLocaleTimeString()}</span>}
                <button onClick={refreshPrices} disabled={refreshing} className="flex items-center gap-1 rounded-lg border border-slate-200 bg-slate-100 px-2 py-1 text-[11px] font-medium text-slate-500 transition-all hover:border-emerald-300 hover:bg-emerald-50 hover:text-emerald-700 disabled:opacity-50">
                  <svg className={`h-3 w-3 ${refreshing ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
                  {refreshing ? 'Refreshing...' : 'Refresh prices'}
                </button>
              </div>
            </div>
            {renderRows('active_metal')}
            {renderRows('promoter')}
            <div>
              <div className="mb-2 flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-emerald-500" /><span className="text-xs font-semibold uppercase tracking-wider text-emerald-700">Support</span></div>
              {rows.filter((row) => row.role === 'support').map((row) => (
                <div key={row.id} className="flex flex-wrap items-start gap-2 rounded-2xl border border-slate-200/80 bg-slate-50/70 p-2.5">
                  <div className="min-w-[12rem] flex-[1_1_18rem]">
                    <select value={row.name} onChange={(e) => {
                      const support = SUPPORT_OPTIONS.find((item) => item.name === e.target.value);
                      updateRow(row.id, { name: e.target.value, price_per_lb: support?.price ?? row.price_per_lb, source_type: 'manual', source: 'Manual support default' });
                    }} className="input-base bg-white">
                      {SUPPORT_OPTIONS.map((support) => <option key={support.name} value={support.name}>{support.name}</option>)}
                    </select>
                    <p className="mt-1 pl-1 text-[11px] text-slate-500">{SUPPORT_OPTION_MAP[row.name]?.note ?? 'Support material'}</p>
                  </div>
                  <div className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-slate-100 px-3 py-2 text-slate-600"><span className="w-11 text-right font-mono text-sm">{supportWtPct.toFixed(1)}</span><span className="text-[11px] text-slate-400">wt%</span><span className="rounded-full bg-white px-2 py-0.5 text-[10px] text-slate-400">auto</span></div>
                  <span className={`flex items-center gap-1 rounded-lg border px-2 py-1 text-[10px] font-bold whitespace-nowrap ${sourceBadgeClass(row.source_type)}`}><span className="h-1.5 w-1.5 rounded-full bg-slate-400" />MANUAL</span>
                  {renderPriceField(row)}
                  <p className="basis-full pl-1 text-[11px] text-slate-400">Support pricing is managed manually.</p>
                </div>
              ))}
            </div>
            <div className={`flex items-center gap-2.5 rounded-xl border px-3.5 py-2.5 text-xs ${isValid ? 'border-emerald-200 bg-emerald-50 text-emerald-700' : 'border-amber-200 bg-amber-50 text-amber-700'}`}>
              <div className={`flex h-4 w-4 flex-shrink-0 items-center justify-center rounded-full text-[10px] font-bold ${isValid ? 'bg-emerald-200 text-emerald-700' : 'bg-amber-200 text-amber-700'}`}>{isValid ? 'OK' : '!'}</div>
              <span>{isValid ? `Composition OK - active ${nonSupportWt.toFixed(1)}% + support ${supportWtPct.toFixed(1)}%` : !hasActiveMetal ? 'Add at least one active metal.' : nonSupportWt > 100 ? 'Active metal + promoter loading cannot exceed 100%.' : 'Set a positive active metal loading.'}</span>
            </div>
          </div>

          <div className="surface-card space-y-4 p-6">
            <h3 className="flex items-center gap-2.5 text-sm font-semibold text-slate-800"><span className="flex h-5 w-5 items-center justify-center rounded-full bg-indigo-600 text-[10px] font-bold text-white">2</span>Manufacturing Process</h3>
            <div className="flex flex-wrap items-center gap-3 border-b border-slate-100 pb-3">
              <span className="w-24 flex-shrink-0 text-sm text-slate-500">Order Size</span>
              <input type="number" min="1" step="1" value={orderSize} onChange={(e) => setOrderSize(Math.max(1, +e.target.value))} className="input-base w-24 text-center font-mono" />
              <span className="text-xs text-slate-400">tons</span>
              <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${scaleBadge}`}>{scaleLabel}</span>
            </div>
            <div>
              <div className="mb-2.5 flex items-center justify-between"><span className="text-sm font-medium text-slate-600">Processing Steps</span><span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-400">{steps.length} selected</span></div>
              <div className="max-h-64 space-y-3 overflow-y-auto pr-1">
                {STEP_CATEGORIES.map((category) => (
                  <div key={category}>
                    <div className="mb-1.5 px-1 text-[10px] font-semibold uppercase tracking-wider text-slate-400">{category}</div>
                    <div className="grid grid-cols-2 gap-1">
                      {ALL_STEPS.filter((step) => step.category === category).map((step) => {
                        const available = (step.scales as readonly Scale[]).includes(currentScale);
                        const checked = steps.includes(step.key);
                        const scaleText = step.scales.length === 3 ? null : step.scales.map((scale) => scale[0].toUpperCase()).join('/');
                        return (
                          <label key={step.key} title={available ? undefined : `Not available at ${currentScale} scale`} className={`flex select-none items-center gap-2 rounded-lg border px-2.5 py-2 text-xs transition-all ${!available ? 'cursor-not-allowed border-transparent text-slate-400 opacity-35' : checked ? 'cursor-pointer border-indigo-200 bg-indigo-50 font-medium text-indigo-700' : 'cursor-pointer border-transparent text-slate-600 hover:border-slate-200 hover:bg-slate-50'}`}>
                            <input type="checkbox" checked={checked} disabled={!available} onChange={() => setSteps((prev) => prev.includes(step.key) ? prev.filter((item) => item !== step.key) : [...prev, step.key])} className="flex-shrink-0 rounded accent-indigo-600" />
                            <span className="flex-1 leading-tight">{step.label}</span>
                            {scaleText && <span className={`flex-shrink-0 rounded px-1 py-0.5 text-[9px] font-bold ${available ? 'bg-slate-200 text-slate-500' : 'bg-red-100 text-red-400'}`}>{scaleText}</span>}
                          </label>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <button onClick={handleCalculate} disabled={loading || !isValid || steps.length === 0} className="w-full rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 py-3.5 text-sm font-semibold text-white shadow-lg shadow-blue-500/25 transition-all hover:from-blue-700 hover:to-indigo-700 disabled:opacity-40 disabled:shadow-none">
            {loading ? <span className="flex items-center justify-center gap-2"><span className="h-4 w-4 rounded-full border-2 border-white border-t-transparent animate-spin" />Calculating...</span> : 'Calculate Manufacturing Cost'}
          </button>
          {error && <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"><span className="font-medium">Error:</span> {error}</div>}
        </div>
        {result ? renderResultsPanel() : renderEmptyPanel()}
      </div>
    </div>
  );
}
