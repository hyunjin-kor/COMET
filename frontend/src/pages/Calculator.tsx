import { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import {
  fetchPrices,
  calculateCost,
  type ComponentInput,
  type CostInput,
  type CostResult,
  type MetalPrice,
} from '../lib/api';
import { useUnit } from '../lib/use-unit';

// ── constants ─────────────────────────────────────────────────────────────────

const TROY_OZ_PER_LB = 14.5833;
function toPerLb(price: number, unit: string): number {
  if (unit === '$/troy_oz') return price * TROY_OZ_PER_LB;
  if (unit === '$/kg') return price / 2.20462;
  return price;
}

const KNOWN_METALS = ['Pt', 'Pd', 'Rh', 'Ru', 'Ir', 'Ni', 'Co', 'Cu', 'Fe', 'Mo', 'W', 'Au', 'Ag', 'Al'];

const SUPPORT_OPTIONS = [
  { name: 'Al2O3',      price: 0.50, note: 'Alumina — most common' },
  { name: 'SiO2',       price: 0.30, note: 'Silica' },
  { name: 'TiO2',       price: 1.20, note: 'Titania' },
  { name: 'Carbon',     price: 1.50, note: 'Activated Carbon' },
  { name: 'ZSM-5',      price: 3.00, note: 'Zeolite (MFI)' },
  { name: 'USY',        price: 2.50, note: 'Zeolite (FAU) — FCC' },
  { name: 'CeO2',       price: 2.00, note: 'Ceria' },
  { name: 'MgO',        price: 0.40, note: 'Magnesia' },
  { name: 'ZrO2',       price: 5.00, note: 'Zirconia' },
  { name: 'SiO2-Al2O3', price: 0.80, note: 'Silica-Alumina' },
];
const SUPPORT_OPTION_MAP = Object.fromEntries(SUPPORT_OPTIONS.map((option) => [option.name, option]));

// scales: which scales each step supports (CatCost Table 6.1)
// null = not available at that scale
const ALL_STEPS = [
  { key: 'mixer_dry_blender',        label: 'Dry Blender',              category: 'Mixing',         scales: ['small','medium','large'] },
  { key: 'mixer_slurry',             label: 'Slurry Mixer',             category: 'Mixing',         scales: ['small','medium','large'] },
  { key: 'incipient_wetness',        label: 'Incipient Wetness',        category: 'Impregnation',   scales: ['small','medium','large'] },
  { key: 'reactor_simple',           label: 'Reactor — Simple',         category: 'Reaction',       scales: ['small','medium','large'] },
  { key: 'reactor_multistep',        label: 'Reactor — Multistep',      category: 'Reaction',       scales: ['small','medium','large'] },
  { key: 'crystallizer',             label: 'Crystallizer',             category: 'Reaction',       scales: ['small','medium','large'] },
  { key: 'dryer_batch_vacuum_tray',  label: 'Dryer — Batch Vacuum',     category: 'Drying',         scales: ['small'] },
  { key: 'dryer_rotary_40_100C',     label: 'Dryer — Rotary 40–100°C', category: 'Drying',         scales: ['small','medium','large'] },
  { key: 'dryer_rotary_100_300C',    label: 'Dryer — Rotary 100–300°C',category: 'Drying',         scales: ['small','medium','large'] },
  { key: 'dryer_spray',              label: 'Spray Dryer',              category: 'Drying',         scales: ['medium','large'] },
  { key: 'kiln_batch',               label: 'Kiln — Batch',             category: 'Calcination',    scales: ['small'] },
  { key: 'kiln_continuous_direct',   label: 'Kiln — Direct',            category: 'Calcination',    scales: ['medium','large'] },
  { key: 'kiln_continuous_indirect', label: 'Kiln — Indirect',          category: 'Calcination',    scales: ['medium','large'] },
  { key: 'filter_belt_vacuum',       label: 'Belt Vacuum Filter',       category: 'Separation',     scales: ['small','medium','large'] },
  { key: 'filter_plate_frame',       label: 'Plate & Frame Filter',     category: 'Separation',     scales: ['small'] },
  { key: 'filter_rotary_vacuum',     label: 'Rotary Vacuum Filter',     category: 'Separation',     scales: ['medium','large'] },
  { key: 'extruder_with_feeder',     label: 'Extruder + Feeder',        category: 'Forming',        scales: ['small','medium','large'] },
  { key: 'ball_forming',             label: 'Ball Forming',             category: 'Forming',        scales: ['small','medium'] },
  { key: 'mill',                     label: 'Mill',                     category: 'Size Reduction', scales: ['small','medium','large'] },
  { key: 'flare',                    label: 'Flare',                    category: 'Utilities',      scales: ['small','medium','large'] },
  { key: 'scrubber_nox',             label: 'NOx Scrubber',             category: 'Utilities',      scales: ['small','medium','large'] },
];

function getScale(orderSizeTons: number): 'small' | 'medium' | 'large' {
  if (orderSizeTons < 5)  return 'small';
  if (orderSizeTons < 70) return 'medium';
  return 'large';
}


const STEP_CATEGORIES = [...new Set(ALL_STEPS.map(s => s.category))];
const CHART_COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

// ── types ─────────────────────────────────────────────────────────────────────

type Role = 'active_metal' | 'promoter' | 'support';

interface Row {
  id: string;
  role: Role;
  name: string;
  wt_pct: number;
  price_per_lb: number;
  is_live: boolean;
}

let _id = 1;
const uid = () => String(_id++);

const makeDefaultRows = (): Row[] => [
  { id: uid(), role: 'active_metal', name: 'Ni',    wt_pct: 20, price_per_lb: 0,    is_live: false },
  { id: uid(), role: 'support',      name: 'Al2O3', wt_pct: 80, price_per_lb: 0.50, is_live: false },
];

// ── main component ────────────────────────────────────────────────────────────

export default function Calculator() {
  const { unit, toDisplay, toInternal, fmtLabel, catLabel } = useUnit();
  const [rows, setRows]           = useState<Row[]>(makeDefaultRows);
  const [steps, setSteps]         = useState<string[]>(['mixer_slurry', 'incipient_wetness', 'dryer_rotary_100_300C']);
  const [orderSize, setOrderSize] = useState(20);

  const currentScale = getScale(orderSize);

  // Auto-deselect steps that become unavailable when scale changes
  useEffect(() => {
    setSteps(prev => prev.filter(key => {
      const s = ALL_STEPS.find(s => s.key === key);
      return s ? s.scales.includes(currentScale) : false;
    }));
  }, [currentScale]);
  const [result, setResult]       = useState<CostResult | null>(null);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState('');
  const [liveMap, setLiveMap]     = useState<Record<string, { price_per_lb: number; is_live: boolean }>>({});
  const [pricesUpdatedAt, setPricesUpdatedAt] = useState<Date | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  // Load live prices on mount
  // is_live: true  = confirmed live from API/scraper (LIVE mode)
  // is_live: false = ChemPPI-escalated reference price (REF mode, read-only toggle disabled)
  useEffect(() => {
    fetchPrices()
      .then((prices: MetalPrice[]) => {
        const m: Record<string, { price_per_lb: number; is_live: boolean }> = {};
        for (const p of prices) {
          m[p.symbol] = { price_per_lb: toPerLb(p.price, p.unit), is_live: p.is_live };
        }
        setLiveMap(m);
        setPricesUpdatedAt(new Date());
        setRows(prev => prev.map(row => {
          if (row.role !== 'support' && m[row.name]) {
            // Use the API's is_live flag — reference prices are NOT live
            return { ...row, price_per_lb: m[row.name].price_per_lb, is_live: m[row.name].is_live };
          }
          return row;
        }));
      })
      .catch(() => {});
  }, []);

  // Keep LIVE-mode rows in sync whenever liveMap refreshes
  useEffect(() => {
    setRows(prev => prev.map(row => {
      if (row.is_live && liveMap[row.name]) {
        return { ...row, price_per_lb: liveMap[row.name].price_per_lb };
      }
      return row;
    }));
  }, [liveMap]);

async function refreshLivePrices() {
    setRefreshing(true);
    try {
      await fetch('/api/prices/refresh', { method: 'POST' });
      const prices: MetalPrice[] = await fetchPrices();
      const m: Record<string, { price_per_lb: number; is_live: boolean }> = {};
      for (const p of prices) {
        m[p.symbol] = { price_per_lb: toPerLb(p.price, p.unit), is_live: p.is_live };
      }
      setLiveMap(m);
      setPricesUpdatedAt(new Date());
    } catch { /* ignore */ }
    finally { setRefreshing(false); }
  }

  function toggleRowLive(id: string) {
    setRows(prev => prev.map(r => {
      if (r.id !== id) return r;
      if (r.is_live) {
        // Switch to MANUAL — keep current price, unlock field
        return { ...r, is_live: false };
      } else {
        // Switch to LIVE — pull latest from liveMap if available
        const lp = liveMap[r.name];
        return lp ? { ...r, price_per_lb: lp.price_per_lb, is_live: true } : r;
      }
    }));
  }

  // Derived values
  const nonSupportWt  = rows.filter(r => r.role !== 'support').reduce((s, r) => s + r.wt_pct, 0);
  const supportWtPct  = Math.max(0, 100 - nonSupportWt);
  const hasActiveMetal = rows.some(r => r.role === 'active_metal' && r.name.trim() !== '');
  const hasSupport     = rows.some(r => r.role === 'support');
  const isValid        = hasActiveMetal && hasSupport && nonSupportWt > 0 && nonSupportWt <= 100;

  function updateRow(id: string, patch: Partial<Row>) {
    setRows(prev => prev.map(r => r.id === id ? { ...r, ...patch } : r));
  }

  function onMetalChange(id: string, name: string) {
    const lp = liveMap[name];
    // Default to LIVE mode only if the API confirmed a live price for this metal
    updateRow(id, { name, price_per_lb: lp?.price_per_lb ?? 0, is_live: lp?.is_live ?? false });
  }

  function addRow(role: 'active_metal' | 'promoter') {
    const newRow: Row = { id: uid(), role, name: '', wt_pct: 0, price_per_lb: 0, is_live: false };
    setRows(prev => {
      const supportIdx = prev.findIndex(r => r.role === 'support');
      if (supportIdx === -1) return [...prev, newRow];
      return [...prev.slice(0, supportIdx), newRow, ...prev.slice(supportIdx)];
    });
  }

  function removeRow(id: string) {
    setRows(prev => prev.filter(r => r.id !== id));
  }

  function toggleStep(key: string) {
    setSteps(prev => prev.includes(key) ? prev.filter(s => s !== key) : [...prev, key]);
  }

  async function handleCalculate() {
    if (!isValid || steps.length === 0) return;
    setLoading(true);
    setError('');
    try {
      const supportRow = rows.find(r => r.role === 'support');
      if (!supportRow) throw new Error('Support is required');

      const components: ComponentInput[] = [
        ...rows.filter(r => r.role !== 'support').map(r => ({
          role: r.role,
          name: r.name,
          wt_pct: r.wt_pct,
          price_per_lb: r.price_per_lb,
        })),
        {
          role: 'support' as const,
          name: supportRow.name,
          wt_pct: supportWtPct,
          price_per_lb: supportRow.price_per_lb,
        },
      ];

      const input: CostInput = { components, steps, order_size_tons: orderSize };
      const res = await calculateCost(input);
      setResult(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setError(msg || 'Calculation failed');
    } finally {
      setLoading(false);
    }
  }

  const pieData = result ? [
    ...result.materials.components.map(c => ({
      name: `${c.name}${c.role === 'support' ? ' (Support)' : c.role === 'promoter' ? ' (Promoter)' : ''}`,
      value: c.cost_pct,
    })),
    { name: 'Processing', value: result.summary.processing_pct },
    { name: 'G&A + Margin', value: Math.max(0, 100 - result.summary.materials_pct - result.summary.processing_pct) },
  ] : [];

  const scaleLabel =
    currentScale === 'small'  ? 'Small · 1 t/day' :
    currentScale === 'medium' ? 'Medium · 10 t/day' :
                                'Large · 150 t/day';

  const scaleBadge =
    currentScale === 'small'  ? 'bg-violet-100 text-violet-700' :
    currentScale === 'medium' ? 'bg-blue-100 text-blue-700' :
                                'bg-teal-100 text-teal-700';

  // ── render ─────────────────────────────────────────────────────────────────
  return (
    <div className="w-full px-7 py-7">
      {/* Page Header */}
      <div className="mb-7 flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <span className="section-kicker">Catalyst Workspace</span>
          <h2 className="mt-3 text-[30px] font-semibold tracking-[-0.03em] text-slate-900">Catalyst Cost Calculator</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
            Step Method 기준으로 활성금속, 촉매 지지체, 공정 단계를 조합해서 제조원가를 빠르게 추정합니다.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <span className="rounded-full border border-slate-200 bg-white/80 px-3 py-1.5 text-xs font-medium text-slate-600 shadow-sm">
            Live metal pricing
          </span>
          <span className="rounded-full border border-slate-200 bg-white/80 px-3 py-1.5 text-xs font-medium text-slate-600 shadow-sm">
            Plant-scale workflow
          </span>
          <span className="rounded-full border border-slate-200 bg-white/80 px-3 py-1.5 text-xs font-medium text-slate-600 shadow-sm">
            {steps.length} process steps selected
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-[minmax(0,1.06fr)_minmax(380px,0.94fr)]">

        {/* ── LEFT: Inputs ───────────────────────────────────────────────── */}
        <div className="space-y-4">

          {/* Card 1 — Composition */}
          <div className="surface-card p-6 space-y-4">
            <div className="flex flex-wrap items-start justify-between gap-3 border-b border-slate-100 pb-4">
              <h3 className="font-semibold text-slate-800 flex items-center gap-2.5 text-sm">
                <span className="w-5 h-5 rounded-full bg-indigo-600 text-white text-[10px] flex items-center justify-center font-bold">1</span>
                Catalyst Composition
              </h3>
              <div className="flex flex-wrap items-center gap-2">
                {pricesUpdatedAt && (
                  <span className="text-[11px] text-slate-400">
                    시세 기준 {pricesUpdatedAt.toLocaleTimeString()}
                  </span>
                )}
                <button
                  onClick={refreshLivePrices}
                  disabled={refreshing}
                  title="실시간 금속 시세 새로고침"
                  className="flex items-center gap-1 px-2 py-1 rounded-lg text-[11px] font-medium bg-slate-100 hover:bg-emerald-50 text-slate-500 hover:text-emerald-700 border border-slate-200 hover:border-emerald-300 transition-all disabled:opacity-50"
                >
                  <svg className={`w-3 h-3 ${refreshing ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  {refreshing ? '갱신 중…' : '시세 갱신'}
                </button>
              </div>
            </div>

            {/* Active Metals */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-indigo-500" />
                  <span className="text-xs font-semibold text-indigo-700 uppercase tracking-wider">Active Metals</span>
                </div>
                <button
                  onClick={() => addRow('active_metal')}
                  className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 transition-colors"
                >
                  + Add
                </button>
              </div>
              <div className="space-y-2">
                {rows.filter(r => r.role === 'active_metal').map(row => {
                  const metalInfo = liveMap[row.name];
                  const hasLive   = metalInfo?.is_live === true;    // confirmed API live
                  const hasRef    = metalInfo !== undefined && !hasLive; // reference/escalated
                  return (
                  <div key={row.id} className="flex flex-wrap items-center gap-2 rounded-2xl border border-slate-200/80 bg-slate-50/70 p-2.5">
                    <select
                      value={row.name}
                      onChange={e => onMetalChange(row.id, e.target.value)}
                      className="input-base min-w-[11rem] flex-[1_1_15rem] bg-white"
                    >
                      <option value="">— select —</option>
                      {KNOWN_METALS.map(m => <option key={m}>{m}</option>)}
                    </select>
                    <div className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-3 py-2">
                      <input
                        type="number" step="0.1" min="0" max="100"
                        value={row.wt_pct}
                        onChange={e => updateRow(row.id, { wt_pct: +e.target.value })}
                        className="w-11 border-0 bg-transparent p-0 text-right text-sm font-medium font-mono text-slate-800 focus:outline-none"
                      />
                      <span className="text-[11px] text-slate-400">wt%</span>
                    </div>

                    {/* Price mode indicator */}
                    {row.is_live ? (
                      // LIVE mode — clickable, switches to MANUAL
                      <button
                        onClick={() => toggleRowLive(row.id)}
                        title="실시간 시세 연동 중 · 클릭하면 수동 입력으로 전환"
                        className="flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-bold whitespace-nowrap border bg-emerald-50 text-emerald-700 border-emerald-300 hover:bg-emerald-100 transition-all"
                      >
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                        LIVE
                      </button>
                    ) : hasLive ? (
                      // MANUAL mode but live is available — clickable, switches to LIVE
                      <button
                        onClick={() => toggleRowLive(row.id)}
                        title="클릭하면 실시간 시세로 전환"
                        className="flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-bold whitespace-nowrap border bg-slate-100 text-slate-500 border-slate-200 hover:bg-slate-200 transition-all"
                      >
                        <span className="w-1.5 h-1.5 rounded-full bg-slate-400" />
                        MANUAL
                      </button>
                    ) : hasRef ? (
                      // REF mode — ChemPPI-escalated reference, no live feed available
                      <span
                        title="2018 CatCost 기준가 + ChemPPI 물가 보정 · 유료 API 키 설정 시 실시간 전환 가능"
                        className="flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-bold whitespace-nowrap border bg-amber-50 text-amber-600 border-amber-200 cursor-help"
                      >
                        <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                        REF
                      </span>
                    ) : null}

                    <div className={`flex items-center gap-2 rounded-2xl border px-3 py-2 ${
                      row.is_live
                        ? 'border-emerald-300 bg-emerald-50 text-emerald-800'
                        : 'border-slate-200 bg-white'
                    }`}>
                      <span className="text-[11px] text-slate-400">$</span>
                      <input
                        type="number" step="0.01" min="0"
                        value={toDisplay(row.price_per_lb).toFixed(2)}
                        readOnly={row.is_live}
                        onChange={e => !row.is_live && updateRow(row.id, { price_per_lb: toInternal(+e.target.value) })}
                        className={`w-14 border-0 bg-transparent p-0 text-right text-sm font-medium font-mono focus:outline-none ${
                          row.is_live ? 'cursor-not-allowed select-none text-emerald-800' : 'text-slate-800'
                        }`}
                      />
                      <span className="text-[11px] text-slate-400">{fmtLabel}</span>
                    </div>
                    <button
                      onClick={() => removeRow(row.id)}
                      className="w-6 h-6 flex items-center justify-center rounded-lg text-slate-300 hover:text-red-500 hover:bg-red-50 transition-colors text-base"
                    >
                      ×
                    </button>
                  </div>
                  );
                })}
                {rows.filter(r => r.role === 'active_metal').length === 0 && (
                  <p className="text-xs text-slate-400 pl-3.5">None — click + Add</p>
                )}
              </div>
            </div>

            {/* Promoters */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-purple-500" />
                  <span className="text-xs font-semibold text-purple-700 uppercase tracking-wider">
                    Promoters <span className="text-slate-400 normal-case font-normal">(optional)</span>
                  </span>
                </div>
                <button
                  onClick={() => addRow('promoter')}
                  className="text-xs font-semibold text-purple-600 hover:text-purple-800 transition-colors"
                >
                  + Add
                </button>
              </div>
              <div className="space-y-2">
                {rows.filter(r => r.role === 'promoter').map(row => {
                  const metalInfo = liveMap[row.name];
                  const hasLive   = metalInfo?.is_live === true;
                  const hasRef    = metalInfo !== undefined && !hasLive;
                  return (
                  <div key={row.id} className="flex flex-wrap items-center gap-2 rounded-2xl border border-slate-200/80 bg-slate-50/70 p-2.5">
                    <input
                      type="text"
                      value={row.name}
                      onChange={e => onMetalChange(row.id, e.target.value)}
                      placeholder="e.g. Re, K, Sn, Ce"
                      className="input-base min-w-[11rem] flex-[1_1_15rem] bg-white"
                    />
                    <div className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-3 py-2">
                      <input
                        type="number" step="0.1" min="0" max="100"
                        value={row.wt_pct}
                        onChange={e => updateRow(row.id, { wt_pct: +e.target.value })}
                        className="w-11 border-0 bg-transparent p-0 text-right text-sm font-medium font-mono text-slate-800 focus:outline-none"
                      />
                      <span className="text-[11px] text-slate-400">wt%</span>
                    </div>
                    {row.is_live ? (
                      <button onClick={() => toggleRowLive(row.id)} title="실시간 시세 연동 중 · 클릭하면 수동 전환"
                        className="flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-bold whitespace-nowrap border bg-emerald-50 text-emerald-700 border-emerald-300 hover:bg-emerald-100">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />LIVE
                      </button>
                    ) : hasLive ? (
                      <button onClick={() => toggleRowLive(row.id)} title="클릭하면 실시간 시세로 전환"
                        className="flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-bold whitespace-nowrap border bg-slate-100 text-slate-500 border-slate-200 hover:bg-slate-200">
                        <span className="w-1.5 h-1.5 rounded-full bg-slate-400" />MANUAL
                      </button>
                    ) : hasRef ? (
                      <span title="참조가 (CatCost 2018 + ChemPPI)" className="flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-bold whitespace-nowrap border bg-amber-50 text-amber-600 border-amber-200 cursor-help">
                        <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />REF
                      </span>
                    ) : null}
                    <div className={`flex items-center gap-2 rounded-2xl border px-3 py-2 ${
                      row.is_live
                        ? 'border-emerald-300 bg-emerald-50 text-emerald-800'
                        : 'border-slate-200 bg-white'
                    }`}>
                      <span className="text-[11px] text-slate-400">$</span>
                      <input
                        type="number" step="0.01" min="0"
                        value={toDisplay(row.price_per_lb).toFixed(2)}
                        readOnly={row.is_live}
                        onChange={e => !row.is_live && updateRow(row.id, { price_per_lb: toInternal(+e.target.value) })}
                        className={`w-14 border-0 bg-transparent p-0 text-right text-sm font-medium font-mono focus:outline-none ${
                          row.is_live ? 'cursor-not-allowed text-emerald-800' : 'text-slate-800'
                        }`}
                      />
                      <span className="text-[11px] text-slate-400">{fmtLabel}</span>
                    </div>
                    <button onClick={() => removeRow(row.id)}
                      className="w-6 h-6 flex items-center justify-center rounded-lg text-slate-300 hover:text-red-500 hover:bg-red-50 transition-colors text-base">×</button>
                  </div>
                  );
                })}
                {rows.filter(r => r.role === 'promoter').length === 0 && (
                  <p className="text-xs text-slate-400 pl-3.5">None</p>
                )}
              </div>
            </div>

            {/* Support */}
            <div>
              <div className="flex items-center gap-1.5 mb-2">
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                <span className="text-xs font-semibold text-emerald-700 uppercase tracking-wider">Support</span>
              </div>
              {rows.filter(r => r.role === 'support').map(row => (
                <div key={row.id} className="flex flex-wrap items-start gap-2 rounded-2xl border border-slate-200/80 bg-slate-50/70 p-2.5">
                  <div className="min-w-[12rem] flex-[1_1_18rem]">
                    <select
                      value={row.name}
                      onChange={e => {
                        const sp = SUPPORT_OPTIONS.find(s => s.name === e.target.value);
                        updateRow(row.id, { name: e.target.value, price_per_lb: sp?.price ?? row.price_per_lb });
                      }}
                      className="input-base bg-white"
                    >
                      {SUPPORT_OPTIONS.map(s => (
                        <option key={s.name} value={s.name}>{s.name}</option>
                      ))}
                    </select>
                    <p className="mt-1 pl-1 text-[11px] text-slate-500">
                      {SUPPORT_OPTION_MAP[row.name]?.note ?? 'Support material'}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-slate-100 px-3 py-2 text-slate-600">
                    <span className="w-11 text-right font-mono text-sm">
                      {supportWtPct.toFixed(1)}
                    </span>
                    <span className="text-[11px] text-slate-400">wt%</span>
                    <span className="rounded-full bg-white px-2 py-0.5 text-[10px] text-slate-400">auto</span>
                  </div>
                  <div className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-3 py-2">
                    <span className="text-[11px] text-slate-400">$</span>
                    <input
                      type="number" step="0.01" min="0"
                      value={toDisplay(row.price_per_lb).toFixed(2)}
                      onChange={e => updateRow(row.id, { price_per_lb: toInternal(+e.target.value) })}
                      className="w-14 border-0 bg-transparent p-0 text-right text-sm font-medium font-mono text-slate-800 focus:outline-none"
                    />
                    <span className="text-[11px] text-slate-400">{fmtLabel}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Validation bar */}
            <div className={`flex items-center gap-2.5 text-xs rounded-xl px-3.5 py-2.5 border ${
              isValid
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                : 'bg-amber-50 text-amber-700 border-amber-200'
            }`}>
              <div className={`w-4 h-4 rounded-full flex items-center justify-center font-bold flex-shrink-0 text-[10px] ${
                isValid ? 'bg-emerald-200 text-emerald-700' : 'bg-amber-200 text-amber-700'
              }`}>
                {isValid ? '✓' : '!'}
              </div>
              <span>
                {isValid
                  ? `Composition OK · active ${nonSupportWt.toFixed(1)}% + support ${supportWtPct.toFixed(1)}%`
                  : !hasActiveMetal
                  ? 'Active metal을 최소 1개 추가하세요'
                  : nonSupportWt > 100
                  ? 'Active + Promoter 합계가 100%를 초과합니다'
                  : 'Active metal 비율을 입력하세요'
                }
              </span>
            </div>
          </div>

          {/* Card 2 — Process */}
          <div className="surface-card p-6 space-y-4">
            <h3 className="font-semibold text-slate-800 flex items-center gap-2.5 text-sm">
              <span className="w-5 h-5 rounded-full bg-indigo-600 text-white text-[10px] flex items-center justify-center font-bold">2</span>
              Manufacturing Process
            </h3>

            {/* Order size */}
            <div className="flex flex-wrap items-center gap-3 pb-3 border-b border-slate-100">
              <span className="text-sm text-slate-500 w-24 flex-shrink-0">Order Size</span>
              <input
                type="number" min="1" step="1"
                value={orderSize}
                onChange={e => setOrderSize(Math.max(1, +e.target.value))}
                className="w-24 input-base text-center font-mono"
              />
              <span className="text-xs text-slate-400">tons</span>
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${scaleBadge}`}>
                {scaleLabel}
              </span>
            </div>

            {/* Steps */}
            <div>
              <div className="flex items-center justify-between mb-2.5">
                <span className="text-sm text-slate-600 font-medium">Processing Steps</span>
                <span className="text-xs text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
                  {steps.length} selected
                </span>
              </div>
              <div className="space-y-3 max-h-64 overflow-y-auto pr-1">
                {STEP_CATEGORIES.map(cat => (
                  <div key={cat}>
                    <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5 px-1">
                      {cat}
                    </div>
                    <div className="grid grid-cols-2 gap-1">
                      {ALL_STEPS.filter(s => s.category === cat).map(step => {
                        const s = step;
                        const available = s.scales.includes(currentScale);
                        const checked   = steps.includes(s.key);
                        // which scales does this step support? show as badge if not all
                        const scalesAll = s.scales.length === 3;
                        const scaleBadgeText = scalesAll ? null
                          : s.scales.map(sc => sc[0].toUpperCase()).join('/'); // e.g. "S", "M/L"
                        return (
                          <label
                            key={s.key}
                            title={available ? undefined : `Not available at ${currentScale} scale (only: ${s.scales.join(', ')})`}
                            className={`flex items-center gap-2 px-2.5 py-2 rounded-lg text-xs transition-all select-none ${
                              !available
                                ? 'opacity-35 cursor-not-allowed text-slate-400 border border-transparent'
                                : checked
                                ? 'cursor-pointer bg-indigo-50 text-indigo-700 border border-indigo-200 font-medium'
                                : 'cursor-pointer text-slate-600 hover:bg-slate-50 border border-transparent hover:border-slate-200'
                            }`}
                          >
                            <input
                              type="checkbox"
                              checked={checked}
                              disabled={!available}
                              onChange={() => available && toggleStep(s.key)}
                              className="rounded flex-shrink-0 accent-indigo-600"
                            />
                            <span className="flex-1 leading-tight">{s.label}</span>
                            {scaleBadgeText && (
                              <span className={`text-[9px] px-1 py-0.5 rounded font-bold flex-shrink-0 ${
                                available
                                  ? 'bg-slate-200 text-slate-500'
                                  : 'bg-red-100 text-red-400'
                              }`}>
                                {scaleBadgeText}
                              </span>
                            )}
                          </label>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Calculate button */}
          <button
            onClick={handleCalculate}
            disabled={loading || !isValid || steps.length === 0}
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3.5 rounded-xl font-semibold text-sm hover:from-blue-700 hover:to-indigo-700 disabled:opacity-40 transition-all shadow-lg shadow-blue-500/25 disabled:shadow-none"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Calculating…
              </span>
            ) : (
              'Calculate Manufacturing Cost →'
            )}
          </button>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm">
              <span className="font-medium">Error:</span> {error}
            </div>
          )}
        </div>

        {/* ── RIGHT: Results ─────────────────────────────────────────────── */}
        {result ? (
          <div className="space-y-4 xl:sticky xl:top-7 self-start">

            {/* KPI cards */}
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-2xl p-5 bg-gradient-to-br from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/20">
                <div className="text-xs opacity-70 font-medium uppercase tracking-wider mb-2">Estimated Cost</div>
                <div className="text-3xl font-bold tracking-tight">
                  ${toDisplay(result.summary.estimated_price_per_lb).toFixed(2)}
                  <span className="text-sm font-normal opacity-60 ml-0.5">{fmtLabel}</span>
                </div>
                <div className="text-sm opacity-60 mt-1">
                  ${(unit === 'kg' ? result.summary.estimated_price_per_lb : result.summary.estimated_price_per_kg).toFixed(2)}/{unit === 'kg' ? 'lb' : 'kg'}
                </div>
              </div>
              <div className="rounded-2xl p-5 bg-gradient-to-br from-slate-700 to-slate-800 text-white shadow-lg">
                <div className="text-xs opacity-70 font-medium uppercase tracking-wider mb-2">Production Scale</div>
                <div className="text-3xl font-bold tracking-tight capitalize">
                  {result.step_method.scale}
                </div>
                <div className="text-sm opacity-60 mt-1">
                  {Number(result.step_method.campaign_days).toFixed(1)}-day campaign
                </div>
              </div>
            </div>

            {/* Donut chart */}
            <div className="surface-card overflow-hidden">
              <div className="px-5 pt-4 pb-2">
                <h3 className="font-semibold text-slate-700 text-sm">Cost Breakdown</h3>
              </div>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%" cy="50%"
                    innerRadius={52} outerRadius={80}
                    dataKey="value"
                    paddingAngle={2}
                  >
                    {pieData.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} strokeWidth={0} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(v) => [`${Number(v).toFixed(1)}%`, 'Share']}
                    contentStyle={{ borderRadius: 10, border: '1px solid #e2e8f0', fontSize: 12 }}
                  />
                  <Legend iconSize={8} iconType="circle" wrapperStyle={{ fontSize: 11, paddingTop: 4 }} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Materials breakdown */}
            <div className="surface-card p-5">
              <h3 className="font-semibold text-slate-700 text-sm mb-3">Materials Breakdown</h3>
              <div className="space-y-2.5">
                {result.materials.components.map((c, i) => (
                  <div key={i} className="flex items-center gap-2.5">
                    <span
                      className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                      style={{ background: CHART_COLORS[i % CHART_COLORS.length] }}
                    />
                    <span className="flex-1 text-sm font-medium text-slate-700 truncate">{c.name}</span>
                    <span className="text-xs text-slate-400 w-14 text-right tabular-nums">
                      {(c.wt_frac * 100).toFixed(1)} wt%
                    </span>
                    <span className="text-xs text-slate-500 font-mono w-20 text-right tabular-nums">
                      ${toDisplay(c.price_per_lb).toFixed(3)}{fmtLabel}
                    </span>
                    <span className="text-xs font-mono text-slate-700 w-24 text-right tabular-nums">
                      ${toDisplay(c.cost_per_lb_cat).toFixed(4)}{catLabel}
                    </span>
                    <span className="text-xs text-slate-400 w-9 text-right tabular-nums font-medium">
                      {c.cost_pct}%
                    </span>
                  </div>
                ))}
                <div className="border-t border-slate-100 pt-2.5 flex justify-between text-sm font-semibold text-slate-800">
                  <span>Total Materials</span>
                  <span className="font-mono">
                    ${toDisplay(result.materials.total_materials_cost_per_lb).toFixed(4)}{fmtLabel}
                  </span>
                </div>
              </div>
            </div>

            {/* Cost summary */}
            <div className="surface-card p-5">
              <h3 className="font-semibold text-slate-700 text-sm mb-3">Cost Summary</h3>
              <div className="rounded-xl overflow-hidden border border-slate-100">
                <div className="flex items-center justify-between px-4 py-2.5 border-b border-slate-100">
                  <span className="text-sm text-slate-600">Materials</span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded-full">
                      {result.summary.materials_pct}%
                    </span>
                    <span className="text-sm font-mono font-medium text-slate-700">
                      ${toDisplay(result.materials.total_materials_cost_per_lb).toFixed(4)}{fmtLabel}
                    </span>
                  </div>
                </div>
                <div className="flex items-center justify-between px-4 py-2.5 border-b border-slate-100">
                  <span className="text-sm text-slate-600">Step Method Processing</span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded-full">
                      {result.summary.processing_pct}%
                    </span>
                    <span className="text-sm font-mono font-medium text-slate-700">
                      ${toDisplay(Number(result.step_method.processing_cost_per_lb)).toFixed(4)}{fmtLabel}
                    </span>
                  </div>
                </div>
                <div className="flex items-center justify-between px-4 py-2.5 border-b border-slate-100">
                  <span className="text-sm text-slate-400">G&A + SARD</span>
                  <span className="text-sm font-mono text-slate-400">included</span>
                </div>
                <div className="flex items-center justify-between px-4 py-2.5 border-b border-slate-100">
                  <span className="text-sm text-slate-400">
                    Selling Margin ({Number(result.step_method.margin_pct).toFixed(1)}%)
                  </span>
                  <span className="text-sm font-mono text-slate-400">included</span>
                </div>
                <div className="flex justify-between items-center px-4 py-3 bg-gradient-to-r from-blue-50 to-indigo-50 border-t border-blue-100">
                  <span className="font-bold text-sm text-blue-800">Estimated Selling Price</span>
                  <span className="font-mono font-bold text-blue-800 text-sm">
                    ${toDisplay(result.summary.estimated_price_per_lb).toFixed(4)}{fmtLabel}
                    &nbsp;=&nbsp;
                    ${(unit === 'kg' ? result.summary.estimated_price_per_lb : result.summary.estimated_price_per_kg).toFixed(2)}/{unit === 'kg' ? 'lb' : 'kg'}
                  </span>
                </div>
              </div>
              <p className="text-xs text-slate-400 mt-2.5">
                * CatCost Step Method basis. 2017 → {new Date().getFullYear()} ChemPPI escalation applied.
              </p>
            </div>

          </div>
        ) : (
          /* Empty state */
          <div className="surface-card flex min-h-[520px] flex-col justify-between overflow-hidden p-7">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">Results Canvas</p>
                <h3 className="mt-3 text-2xl font-semibold tracking-[-0.03em] text-slate-900">Estimate preview</h3>
                <p className="mt-2 max-w-sm text-sm leading-6 text-slate-500">
                  좌측 입력을 마치고 계산을 실행하면 원가, 재료비 비중, 처리 단계 비용이 여기에 정리됩니다.
                </p>
              </div>
              <div className="rounded-full border border-emerald-100 bg-emerald-50 px-3 py-1 text-[11px] font-medium text-emerald-700">
                Ready for run
              </div>
            </div>
            <div className="flex flex-col items-center justify-center rounded-[28px] border border-dashed border-slate-200 bg-[linear-gradient(135deg,rgba(59,130,246,0.05),rgba(255,255,255,0.65))] px-6 py-14 text-center">
              <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-3xl border border-slate-200 bg-white shadow-sm">
              <svg viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="1.5" className="w-7 h-7">
                <path d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2V9M9 21H5a2 2 0 01-2-2V9m0 0h18" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              </div>
              <div className="text-base font-semibold text-slate-700">결과가 여기에 표시됩니다</div>
              <div className="mt-2 max-w-sm text-sm leading-6 text-slate-500">
                조성과 공정을 입력한 뒤 계산을 실행하면 제조원가, 비용 분해, 규모별 처리비가 이 패널에 나타납니다.
              </div>
            </div>
            <div className="grid gap-3 sm:grid-cols-3">
              <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
                <div className="text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">Materials</div>
                <div className="mt-2 text-sm font-medium text-slate-700">Active metal, promoter, support</div>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
                <div className="text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">Processing</div>
                <div className="mt-2 text-sm font-medium text-slate-700">Campaign duration and step cost</div>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
                <div className="text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">Decision</div>
                <div className="mt-2 text-sm font-medium text-slate-700">Selling price and cost balance</div>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
