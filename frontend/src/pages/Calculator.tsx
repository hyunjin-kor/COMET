import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { WorkspaceSectionFooter, WorkspaceSectionNav, useWorkspaceSections, type WorkspaceSection } from '../components/shared/WorkspaceSections';
import {
  type ApplicationFamily,
  type CatalystDomain,
  calculateCost,
  fetchMaterials,
  fetchPrices,
  fetchTemplates,
  refreshPrices as refreshPriceFeed,
  type ComponentInput,
  type CostInput,
  type MaterialItem,
  type MetalPrice,
  type ProcessTemplate,
} from '../lib/api';
import {
  loadCalculatorDraft,
  loadCalculatorResultSnapshot,
  saveCalculatorDraft,
  saveCalculatorResultSnapshot,
  type CalculatorBenchmarkPreset,
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
  { key: 'ionomer_ink_homogenization', label: 'Ionomer Ink Homogenization', category: 'Mixing', scales: ['small', 'medium', 'large'] },
  { key: 'ultrasonic_dispersion', label: 'Ultrasonic Dispersion', category: 'Mixing', scales: ['small', 'medium', 'large'] },
  { key: 'incipient_wetness', label: 'Incipient Wetness', category: 'Impregnation', scales: ['small', 'medium', 'large'] },
  { key: 'ccm_coating_pass', label: 'CCM Coating Pass', category: 'Impregnation', scales: ['small', 'medium', 'large'] },
  { key: 'reactor_simple', label: 'Simple Reactor', category: 'Reaction', scales: ['small', 'medium', 'large'] },
  { key: 'reactor_multistep', label: 'Multistep Reactor', category: 'Reaction', scales: ['small', 'medium', 'large'] },
  { key: 'membrane_pretreatment', label: 'Membrane Pretreatment', category: 'Reaction', scales: ['small', 'medium', 'large'] },
  { key: 'substrate_pretreatment', label: 'Substrate Pretreatment', category: 'Reaction', scales: ['small', 'medium', 'large'] },
  { key: 'ion_exchange_conversion', label: 'Ion-Exchange Conversion', category: 'Reaction', scales: ['small', 'medium', 'large'] },
  { key: 'electrochemical_break_in', label: 'Electrochemical Break-In', category: 'Reaction', scales: ['small', 'medium', 'large'] },
  { key: 'crystallizer', label: 'Crystallizer', category: 'Reaction', scales: ['small', 'medium', 'large'] },
  { key: 'dryer_batch_vacuum_tray', label: 'Vacuum Tray Dryer', category: 'Drying', scales: ['small'] },
  { key: 'dryer_rotary_40_100C', label: 'Rotary Dryer 40-100 C', category: 'Drying', scales: ['small', 'medium', 'large'] },
  { key: 'dryer_rotary_100_300C', label: 'Rotary Dryer 100-300 C', category: 'Drying', scales: ['small', 'medium', 'large'] },
  { key: 'electrode_drying_low_temp', label: 'Electrode Drying <100 C', category: 'Drying', scales: ['small', 'medium', 'large'] },
  { key: 'dryer_spray', label: 'Spray Dryer', category: 'Drying', scales: ['medium', 'large'] },
  { key: 'kiln_batch', label: 'Batch Kiln', category: 'Calcination', scales: ['small'] },
  { key: 'kiln_continuous_direct', label: 'Continuous Kiln Direct', category: 'Calcination', scales: ['medium', 'large'] },
  { key: 'kiln_continuous_indirect', label: 'Continuous Kiln Indirect', category: 'Calcination', scales: ['medium', 'large'] },
  { key: 'filter_belt_vacuum', label: 'Belt Vacuum Filter', category: 'Separation', scales: ['small', 'medium', 'large'] },
  { key: 'filter_plate_frame', label: 'Plate and Frame Filter', category: 'Separation', scales: ['small'] },
  { key: 'filter_rotary_vacuum', label: 'Rotary Vacuum Filter', category: 'Separation', scales: ['medium', 'large'] },
  { key: 'extruder_with_feeder', label: 'Extruder with Feeder', category: 'Forming', scales: ['small', 'medium', 'large'] },
  { key: 'hot_press_lamination', label: 'Hot Press Lamination', category: 'Forming', scales: ['small', 'medium', 'large'] },
  { key: 'ball_forming', label: 'Ball Forming', category: 'Forming', scales: ['small', 'medium'] },
  { key: 'mill', label: 'Mill', category: 'Size Reduction', scales: ['small', 'medium', 'large'] },
  { key: 'flare', label: 'Flare', category: 'Utilities', scales: ['small', 'medium', 'large'] },
  { key: 'scrubber_nox', label: 'NOx Scrubber', category: 'Utilities', scales: ['small', 'medium', 'large'] },
] as const;
const STEP_CATEGORIES = [...new Set(ALL_STEPS.map((step) => step.category))];
const ELECTRO_APPLICATION_OPTIONS: Array<{ value: ApplicationFamily; label: string; detail: string }> = [
  { value: 'fuel_cell', label: 'Fuel Cell', detail: 'PEMFC and hydrogen-air MEA / CCM workflows.' },
  { value: 'electrolyzer', label: 'Electrolyzer', detail: 'PEM water electrolysis catalyst and membrane routes.' },
  { value: 'direct_methanol_fuel_cell', label: 'DMFC', detail: 'PtRu-centered methanol oxidation routes.' },
  { value: 'general', label: 'General', detail: 'Use when the application family is still undecided.' },
];
const ESTIMATE_SECTIONS: WorkspaceSection[] = [
  { id: 'type', label: 'Catalyst Type', summary: 'Choose thermocatalyst or electrocatalyst.' },
  { id: 'composition', label: 'Composition', summary: 'Set recipe rows or the electrode stack.' },
  { id: 'manufacturing', label: 'Preparation Method', summary: 'Set campaign scale and preparation steps.' },
  { id: 'result', label: 'Result', summary: 'Run the estimate and open the result screen.' },
];

type SourceType = CalculatorRow['source_type'];
type Scale = 'small' | 'medium' | 'large';
type FeedPrice = { price_per_lb: number; source_type: Exclude<SourceType, 'manual'>; source: string };
type ElectrocatalystDraft = {
  catalystMaterialKey: string;
  ionomerMaterialKey: string;
  membraneMaterialKey: string;
  substrateMaterialKey: string;
  activeAreaCm2: number;
  catalystLoadingMgCm2: number;
  ionomerToCatalystRatio: number;
  templateId: string;
};

function uid() {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') return crypto.randomUUID();
  return `row-${Date.now()}-${Math.random().toString(16).slice(2, 10)}`;
}

const toPerLb = (price: number, unit: string) => unit === '$/troy_oz' ? price * TROY_OZ_PER_LB : unit === '$/kg' ? price / 2.20462 : price;
const getScale = (tons: number): Scale => (tons < 5 ? 'small' : tons < 70 ? 'medium' : 'large');
const sourceTypeLabel = (sourceType: SourceType) => sourceType === 'live' ? 'Live' : sourceType === 'indexed' ? 'Indexed' : 'Manual';
const defaultRows = (): CalculatorRow[] => [
  { id: uid(), role: 'active_metal', name: 'Ni', wt_pct: 20, price_per_lb: 0, source_type: 'manual', source: 'Manual input' },
  defaultSupportRow(),
];
const sourceTone = (sourceType: SourceType) => sourceType === 'live' ? 'border-emerald-200 bg-emerald-50 text-emerald-700' : sourceType === 'indexed' ? 'border-amber-200 bg-amber-50 text-amber-700' : 'border-slate-200 bg-white text-slate-600';
const priceTone = (sourceType: SourceType) => sourceType === 'live' ? 'border-emerald-200 bg-emerald-50/70 text-emerald-800' : sourceType === 'indexed' ? 'border-amber-200 bg-amber-50/70 text-amber-800' : '';
const scaleMeta = (scale: Scale) => scale === 'small' ? { label: 'Small', rate: '1 t/day', classes: 'border-violet-200 bg-violet-50 text-violet-700' } : scale === 'medium' ? { label: 'Medium', rate: '10 t/day', classes: 'border-sky-200 bg-sky-50 text-sky-700' } : { label: 'Large', rate: '150 t/day', classes: 'border-teal-200 bg-teal-50 text-teal-700' };
const formatStepLabel = (stepKey: string) => ALL_STEPS.find((step) => step.key === stepKey)?.label ?? stepKey;
const catalystDomainLabel = (domain: Extract<CatalystDomain, 'thermal' | 'electrocatalyst'>) => domain === 'electrocatalyst' ? 'Electrocatalyst' : 'Thermocatalyst';
const defaultElectrocatalystConfig = (): ElectrocatalystDraft => ({
  catalystMaterialKey: '',
  ionomerMaterialKey: '',
  membraneMaterialKey: '',
  substrateMaterialKey: '',
  activeAreaCm2: 25,
  catalystLoadingMgCm2: 0.5,
  ionomerToCatalystRatio: 0.8,
  templateId: 'pem_fuel_cell_ccm',
});

function defaultSupportRow(): CalculatorRow {
  return {
    id: uid(),
    role: 'support',
    name: 'Al2O3',
    wt_pct: 80,
    price_per_lb: 0.5,
    source_type: 'manual',
    source: 'Manual support default',
  };
}

function ensureThermalRows(rows: CalculatorRow[]) {
  const thermalRows = rows.filter((row) => row.role === 'active_metal' || row.role === 'promoter' || row.role === 'support');
  const hasActiveMetal = thermalRows.some((row) => row.role === 'active_metal');
  if (!hasActiveMetal) return defaultRows();
  if (!thermalRows.some((row) => row.role === 'support')) return [...thermalRows, defaultSupportRow()];
  return thermalRows;
}

function hasNamedRow(row: CalculatorRow) {
  return row.name.trim().length > 0;
}

function isCompletedThermalRow(row: CalculatorRow) {
  return hasNamedRow(row) && row.wt_pct > 0;
}

function isIncompleteThermalRow(row: CalculatorRow) {
  const hasName = hasNamedRow(row);
  const hasWeight = row.wt_pct > 0;
  return hasName !== hasWeight;
}

function applicationFamilyLabel(value: ApplicationFamily) {
  return ELECTRO_APPLICATION_OPTIONS.find((option) => option.value === value)?.label ?? value;
}

function priceScopeLabel(scope?: string) {
  switch (scope) {
    case 'literature_high_volume':
      return 'Literature high-volume';
    case 'historical_bulk':
      return 'Historical bulk';
    case 'vendor_lab':
      return 'Vendor lab';
    default:
      return scope ?? 'Unspecified';
  }
}

function pricingBasisDisplay(value?: string) {
  if (!value) return 'basis not stated';
  return value.replace(/_/g, ' ');
}

function materialSourceTrust(material: MaterialItem) {
  if (material.reference_url) {
    if (material.price_scope === 'literature_high_volume') return 'Public literature source';
    if (material.price_scope === 'vendor_lab') return 'Direct vendor source';
    return 'Public source linked';
  }
  if (material.price_scope === 'historical_bulk') return 'No public permalink';
  return 'Link not stored';
}

function materialQuoteLabel(material?: MaterialItem | null) {
  if (!material?.price_unit || material.price == null) return 'Price not available';
  const formatted = material.price < 1 ? material.price.toFixed(4) : material.price.toFixed(2);
  return `$${formatted} ${material.price_unit}`;
}

function materialOptionLabel(material: MaterialItem) {
  return `${material.name} [${priceScopeLabel(material.price_scope)} | ${materialQuoteLabel(material)}]`;
}

function preferredScopeRank(material: MaterialItem) {
  switch (material.price_scope) {
    case 'literature_high_volume':
      return 0;
    case 'historical_bulk':
      return 1;
    case 'vendor_lab':
      return 2;
    default:
      return 3;
  }
}

function electrocatalystTemplateRank(
  material: MaterialItem,
  category: string,
  applicationFamily: ApplicationFamily,
  templateId: string,
) {
  const text = `${material.name} ${material.formula ?? ''} ${material.symbol ?? ''}`.toLowerCase();
  const symbol = (material.symbol ?? '').toLowerCase();
  const exactFamilyRank =
    material.application_family === applicationFamily
      ? 0
      : material.application_family === 'general'
        ? 1
        : 2;

  if (applicationFamily !== 'electrolyzer') {
    return exactFamilyRank;
  }

  const isPemElectrolyzer = templateId === 'pem_electrolyzer_ccm';
  const isPfsa = text.includes('pfsa') || text.includes('aquivion');
  const isAem = text.includes('aem') || text.includes('piperion') || text.includes('sustainion') || text.includes('pdt');
  const isTitanium = text.includes('titanium') || text.includes('ptl') || text.includes('frit');
  const isNickel = text.includes('nickel');
  const isCarbon = text.includes('carbon');

  if (category === 'Ionomer' || category === 'Membrane') {
    if (isPemElectrolyzer) return isPfsa ? 0 : isAem ? 1 : 2;
    return isAem ? 0 : isPfsa ? 1 : 2;
  }

  if (category === 'Gas Diffusion Layer') {
    if (isPemElectrolyzer) return isTitanium ? 0 : isCarbon ? 1 : isNickel ? 2 : 3;
    return isNickel ? 0 : isCarbon ? 1 : isTitanium ? 2 : 3;
  }

  if (category === 'Electrocatalyst Powder') {
    if (isPemElectrolyzer) {
      if (symbol === 'ir') return 0;
      if (symbol === 'ru') return 1;
      if (symbol === 'ptir') return 2;
      return 3;
    }
    if (symbol === 'ni') return 0;
    if (symbol === 'ag') return 1;
    if (symbol === 'ir' || symbol === 'ru') return 2;
    return 3;
  }

  return exactFamilyRank;
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

function CompactValueRow({ label, value, detail }: { label: string; value: string; detail?: string }) {
  return (
    <div className="cp-data-row">
      <div>
        <div className="cp-subtle-label">{label}</div>
        {detail ? <div className="mt-1 text-xs leading-5 text-slate-500">{detail}</div> : null}
      </div>
      <div className="text-right text-sm font-semibold text-slate-950">{value}</div>
    </div>
  );
}

export default function Calculator() {
  const navigate = useNavigate();
  const { toDisplay, toInternal, fmtLabel } = useUnit();
  const sectionState = useWorkspaceSections(ESTIMATE_SECTIONS, 'estimate');
  const storedDraft = loadCalculatorDraft();
  const [rows, setRows] = useState<CalculatorRow[]>(() => storedDraft?.rows?.length ? storedDraft.rows : defaultRows());
  const [steps, setSteps] = useState<string[]>(() => storedDraft?.steps?.length ? storedDraft.steps : DEFAULT_STEPS);
  const [catalystDomain, setCatalystDomain] = useState<'thermal' | 'electrocatalyst'>(() => storedDraft?.catalystDomain ?? 'thermal');
  const [applicationFamily, setApplicationFamily] = useState<ApplicationFamily>(() => storedDraft?.applicationFamily ?? 'fuel_cell');
  const [electrocatalystConfig, setElectrocatalystConfig] = useState<ElectrocatalystDraft>(() => storedDraft?.electrocatalystConfig ?? defaultElectrocatalystConfig());
  const [orderSize, setOrderSize] = useState<number>(() => storedDraft?.orderSize ?? 20);
  const [includeSpentValue, setIncludeSpentValue] = useState<boolean>(() => storedDraft?.includeSpentValue ?? false);
  const [reactorType, setReactorType] = useState<'fixed' | 'slurry'>(() => storedDraft?.reactorType ?? 'fixed');
  const [catalystBulkDensity, setCatalystBulkDensity] = useState<number>(() => storedDraft?.catalystBulkDensity ?? 50);
  const [selectedBenchmark] = useState<CalculatorBenchmarkPreset | null>(() => storedDraft?.benchmarkCandidate ?? null);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [liveMap, setLiveMap] = useState<Record<string, FeedPrice>>({});
  const [electroMaterials, setElectroMaterials] = useState<MaterialItem[]>([]);
  const [electroTemplates, setElectroTemplates] = useState<ProcessTemplate[]>([]);
  const [latestSnapshot, setLatestSnapshot] = useState<CalculatorResultSnapshot | null>(() => loadCalculatorResultSnapshot());
  const [pricesUpdatedAt, setPricesUpdatedAt] = useState<Date | null>(() => storedDraft?.pricesUpdatedAt ? new Date(storedDraft.pricesUpdatedAt) : null);
  const currentScale = getScale(orderSize);
  const scale = scaleMeta(currentScale);

  useEffect(() => {
    saveCalculatorDraft({
      rows,
      steps,
      catalystDomain,
      applicationFamily,
      orderSize,
      pricesUpdatedAt: pricesUpdatedAt ? pricesUpdatedAt.toISOString() : null,
      includeSpentValue,
      reactorType,
      catalystBulkDensity,
      electrocatalystConfig,
      benchmarkCandidate: selectedBenchmark,
    });
  }, [
    applicationFamily,
    catalystBulkDensity,
    catalystDomain,
    electrocatalystConfig,
    includeSpentValue,
    orderSize,
    pricesUpdatedAt,
    reactorType,
    rows,
    selectedBenchmark,
    steps,
  ]);

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
    async function loadElectrocatalystReferences() {
      try {
        const [materials, templates] = await Promise.all([
          fetchMaterials(undefined, undefined, 'electrocatalyst', applicationFamily),
          fetchTemplates('electrocatalyst'),
        ]);
        setElectroMaterials(materials);
        setElectroTemplates(
          templates.filter((template) => !template.application_family || template.application_family === applicationFamily || template.application_family === 'general'),
        );
      } catch {
        setElectroMaterials([]);
        setElectroTemplates([]);
      }
    }

    void loadElectrocatalystReferences();
  }, [applicationFamily]);

  useEffect(() => {
    if (catalystDomain !== 'electrocatalyst') return;
    const activeTemplate = electroTemplates.find((template) => template.id === electrocatalystConfig.templateId) ?? electroTemplates[0];
    if (!activeTemplate) return;

    if (activeTemplate.id !== electrocatalystConfig.templateId) {
      setElectrocatalystConfig((previous) => ({ ...previous, templateId: activeTemplate.id }));
      return;
    }

    setSteps(activeTemplate.steps);
  }, [catalystDomain, electroTemplates, electrocatalystConfig.templateId]);

  useEffect(() => {
    if (catalystDomain !== 'electrocatalyst' || electroMaterials.length === 0) return;

    const compareElectroPreference = (left: MaterialItem, right: MaterialItem, category: string) => {
      const templateDelta =
        electrocatalystTemplateRank(left, category, applicationFamily, electrocatalystConfig.templateId)
        - electrocatalystTemplateRank(right, category, applicationFamily, electrocatalystConfig.templateId);
      if (templateDelta !== 0) return templateDelta;
      const scopeDelta = preferredScopeRank(left) - preferredScopeRank(right);
      if (scopeDelta !== 0) return scopeDelta;
      const leftPrice = left.price ?? Number.POSITIVE_INFINITY;
      const rightPrice = right.price ?? Number.POSITIVE_INFINITY;
      if (leftPrice !== rightPrice) return leftPrice - rightPrice;
      return left.name.localeCompare(right.name);
    };

    const pickPreferredKey = (options: MaterialItem[], category: string) => {
      if (options.length === 0) return '';
      const preferred = [...options].sort((left, right) => compareElectroPreference(left, right, category));
      return String(preferred[0]?.id ?? '');
    };

    const shouldReplaceSelection = (currentKey: string, options: MaterialItem[], category: string) => {
      const preferredKey = pickPreferredKey(options, category);
      if (!currentKey) return preferredKey;
      const current = options.find((material) => String(material.id) === currentKey);
      const preferred = options.find((material) => String(material.id) === preferredKey);
      if (!current || !preferred) return preferredKey;
      return compareElectroPreference(current, preferred, category) > 0 ? preferredKey : '';
    };

    const catalystOptions = electroMaterials.filter((material) => material.category === 'Electrocatalyst Powder');
    const ionomerRows = electroMaterials.filter((material) => material.category === 'Ionomer');
    const membraneRows = electroMaterials.filter((material) => material.category === 'Membrane');
    const substrateRows = electroMaterials.filter((material) => material.category === 'Gas Diffusion Layer');

    const nextPatch: Partial<ElectrocatalystDraft> = {};
    const catalystPreferred = shouldReplaceSelection(
      electrocatalystConfig.catalystMaterialKey,
      catalystOptions,
      'Electrocatalyst Powder',
    );
    if (catalystPreferred) {
      nextPatch.catalystMaterialKey = catalystPreferred;
    }
    const ionomerPreferred = shouldReplaceSelection(
      electrocatalystConfig.ionomerMaterialKey,
      ionomerRows,
      'Ionomer',
    );
    if (ionomerPreferred) {
      nextPatch.ionomerMaterialKey = ionomerPreferred;
    }
    const membranePreferred = shouldReplaceSelection(
      electrocatalystConfig.membraneMaterialKey,
      membraneRows,
      'Membrane',
    );
    if (membranePreferred) {
      nextPatch.membraneMaterialKey = membranePreferred;
    }
    const substratePreferred = shouldReplaceSelection(
      electrocatalystConfig.substrateMaterialKey,
      substrateRows,
      'Gas Diffusion Layer',
    );
    if (substratePreferred) {
      nextPatch.substrateMaterialKey = substratePreferred;
    }
    if (electroTemplates.length > 0 && !electroTemplates.some((template) => template.id === electrocatalystConfig.templateId)) {
      nextPatch.templateId = electroTemplates[0]?.id ?? electrocatalystConfig.templateId;
    }

    if (Object.keys(nextPatch).length > 0) {
      setElectrocatalystConfig((previous) => ({ ...previous, ...nextPatch }));
    }
  }, [
    catalystDomain,
    electroMaterials,
    electroTemplates,
    electrocatalystConfig.catalystMaterialKey,
    electrocatalystConfig.ionomerMaterialKey,
    electrocatalystConfig.membraneMaterialKey,
    electrocatalystConfig.substrateMaterialKey,
    electrocatalystConfig.templateId,
  ]);

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

  const activeBenchmark = selectedBenchmark?.catalyst_domain === catalystDomain ? selectedBenchmark : null;
  const activeElectroTemplate =
    catalystDomain === 'electrocatalyst'
      ? electroTemplates.find((template) => template.id === electrocatalystConfig.templateId) ?? null
      : null;
  const electroMaterialMap = new Map(electroMaterials.map((material) => [String(material.id), material]));
  const catalystPowders = electroMaterials.filter((material) => material.category === 'Electrocatalyst Powder');
  const ionomerOptions = electroMaterials.filter((material) => material.category === 'Ionomer');
  const membraneOptions = electroMaterials.filter((material) => material.category === 'Membrane');
  const substrateOptions = electroMaterials.filter((material) => material.category === 'Gas Diffusion Layer');
  const selectedCatalystMaterial = electroMaterialMap.get(electrocatalystConfig.catalystMaterialKey) ?? null;
  const selectedIonomerMaterial = electroMaterialMap.get(electrocatalystConfig.ionomerMaterialKey) ?? null;
  const selectedMembraneMaterial = electroMaterialMap.get(electrocatalystConfig.membraneMaterialKey) ?? null;
  const selectedSubstrateMaterial = electroMaterialMap.get(electrocatalystConfig.substrateMaterialKey) ?? null;

  function handleCatalystDomainChange(nextDomain: 'thermal' | 'electrocatalyst') {
    if (nextDomain === catalystDomain) return;
    setCatalystDomain(nextDomain);
    setError('');

    if (nextDomain === 'thermal') {
      setRows((previous) => ensureThermalRows(previous));
      const thermalBenchmarkSteps =
        selectedBenchmark?.catalyst_domain === 'thermal'
          ? selectedBenchmark.route.steps
          : DEFAULT_STEPS.filter((key) => {
              const step = ALL_STEPS.find((item) => item.key === key);
              return step ? (step.scales as readonly Scale[]).includes(currentScale) : false;
            });
      setSteps(thermalBenchmarkSteps);
      return;
    }

    if (selectedBenchmark?.catalyst_domain === 'electrocatalyst') {
      setApplicationFamily(selectedBenchmark.application_family);
    }
  }

  const updateRow = (id: string, patch: Partial<CalculatorRow>) => setRows((previous) => previous.map((row) => row.id === id ? { ...row, ...patch } : row));
  const onMaterialChange = (id: string, name: string) => updateRow(id, { name, price_per_lb: liveMap[name]?.price_per_lb ?? 0, source_type: liveMap[name]?.source_type ?? 'manual', source: liveMap[name]?.source ?? 'Manual input' });
  const updateElectroConfig = (patch: Partial<ElectrocatalystDraft>) => setElectrocatalystConfig((previous) => ({ ...previous, ...patch }));
  const addRow = (role: 'active_metal' | 'promoter') => setRows((previous) => {
    const row: CalculatorRow = { id: uid(), role, name: '', wt_pct: 0, price_per_lb: 0, source_type: 'manual', source: 'Manual input' };
    const supportIndex = previous.findIndex((item) => item.role === 'support');
    return supportIndex === -1 ? [...previous, row] : [...previous.slice(0, supportIndex), row, ...previous.slice(supportIndex)];
  });
  const removeRow = (id: string) => setRows((previous) => previous.filter((row) => row.id !== id));
  const toggleStep = (stepKey: string) => setSteps((previous) => previous.includes(stepKey) ? previous.filter((item) => item !== stepKey) : [...previous, stepKey]);
  const thermalDraftRows = rows.filter((row) => row.role !== 'support');
  const completedThermalRows = thermalDraftRows.filter(isCompletedThermalRow);
  const incompleteThermalRows = thermalDraftRows.filter(isIncompleteThermalRow);
  const nonSupportWt = completedThermalRows.reduce((sum, row) => sum + row.wt_pct, 0);
  const supportWtPct = Math.max(0, 100 - nonSupportWt);
  const liveFeedCount = Object.values(liveMap).filter((feed) => feed.source_type === 'live').length;
  const indexedFeedCount = Object.values(liveMap).filter((feed) => feed.source_type === 'indexed').length;
  const activeMetalCount = completedThermalRows.filter((row) => row.role === 'active_metal').length;
  const isThermalValid = activeMetalCount > 0 && nonSupportWt > 0 && nonSupportWt < 100 && incompleteThermalRows.length === 0;
  const isElectroValid = Boolean(
    electrocatalystConfig.catalystMaterialKey
      && electrocatalystConfig.ionomerMaterialKey
      && electrocatalystConfig.membraneMaterialKey
      && electrocatalystConfig.substrateMaterialKey
      && activeElectroTemplate,
  );
  const isValid = catalystDomain === 'electrocatalyst' ? isElectroValid : isThermalValid;
  const latestSnapshotForCurrentCase = latestSnapshot
    && latestSnapshot.result.input_summary.catalyst_domain === catalystDomain
    && (
      catalystDomain !== 'electrocatalyst'
      || latestSnapshot.result.input_summary.application_family === applicationFamily
    )
      ? latestSnapshot
      : null;

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
      let input: CostInput;
      let supportName: string | null = null;

      if (catalystDomain === 'electrocatalyst') {
        input = {
          catalyst_domain: 'electrocatalyst',
          application_family: applicationFamily,
          template_id: electrocatalystConfig.templateId || undefined,
          order_size_tons: orderSize,
          steps,
          components: [{
            role: 'active_catalyst',
            material_key: electrocatalystConfig.catalystMaterialKey,
            wt_pct: 100,
            name: selectedCatalystMaterial?.name ?? 'Electrocatalyst powder',
          }],
          electrode_input: {
            application_family: applicationFamily,
            catalyst_material_key: electrocatalystConfig.catalystMaterialKey,
            ionomer_material_key: electrocatalystConfig.ionomerMaterialKey,
            membrane_material_key: electrocatalystConfig.membraneMaterialKey,
            substrate_material_key: electrocatalystConfig.substrateMaterialKey,
            active_area_cm2: electrocatalystConfig.activeAreaCm2,
            catalyst_loading_mg_cm2: electrocatalystConfig.catalystLoadingMgCm2,
            ionomer_to_catalyst_ratio: electrocatalystConfig.ionomerToCatalystRatio,
          },
        };
      } else {
        const supportRow = rows.find((row) => row.role === 'support');
        if (!supportRow) throw new Error('Support is required.');
        supportName = supportRow.name;

        const components: ComponentInput[] = [
          ...completedThermalRows.map((row) => ({ role: row.role, name: row.name, wt_pct: row.wt_pct, price_per_lb: row.price_per_lb })),
          { role: 'support', name: supportRow.name, wt_pct: supportWtPct, price_per_lb: supportRow.price_per_lb },
        ];
        input = {
          components,
          steps,
          catalyst_domain: catalystDomain,
          application_family: applicationFamily,
          order_size_tons: orderSize,
          include_spent_value: includeSpentValue,
          reactor_type: reactorType,
          catalyst_bulk_density: catalystBulkDensity,
        };
      }

      const result = await calculateCost(input);
      const snapshot: CalculatorResultSnapshot = {
        result,
        orderSize,
        steps,
        stepLabels: steps.map(formatStepLabel),
        selectedSupportName: supportName ?? selectedSubstrateMaterial?.name ?? null,
        activeMetalCount,
        liveFeedCount,
        indexedFeedCount,
        nonSupportWt,
        supportWtPct,
        generatedAt: new Date().toISOString(),
        benchmarkCandidate: selectedBenchmark,
      };

      saveCalculatorResultSnapshot(snapshot);
      setLatestSnapshot(snapshot);
      navigate('/calculator/result');
    } catch (caughtError: unknown) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : typeof caughtError === 'string'
            ? caughtError
            : 'Unexpected calculation error. Review the composition rows and try again.',
      );
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
    const title = row.source_type === 'manual' ? `Manual input. Switch to ${sourceTypeLabel(feed.source_type)} pricing from ${feed.source}.` : `${row.source}. Switch back to manual input.`;
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

  function renderElectroMaterialCard(label: string, material: MaterialItem | null, fallback: string) {
    return (
      <div className="rounded-[24px] border border-slate-900/8 bg-white/72 p-4">
        <div className="cp-subtle-label">{label}</div>
        <div className="mt-2 font-semibold text-slate-950">{material?.name ?? fallback}</div>
        <div className="mt-1 text-sm text-slate-600">{material ? materialQuoteLabel(material) : 'Select a library record to lock pricing.'}</div>
        {material ? (
          <div className="mt-2 space-y-2">
            <div className="text-xs leading-6 text-slate-500">
              {priceScopeLabel(material.price_scope)} / {pricingBasisDisplay(material.pricing_basis)}
              {material.quote_year ? ` / ${material.quote_year}` : ''}
              {material.quote_source ? ` / ${material.quote_source}` : ''}
            </div>
            <span className={`inline-flex rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.16em] ${
              material.reference_url ? 'border-emerald-200 bg-emerald-50 text-emerald-700' : 'border-amber-200 bg-amber-50 text-amber-700'
            }`}>
              {materialSourceTrust(material)}
            </span>
            {material.reference_url ? (
              <a
                href={material.reference_url}
                target="_blank"
                rel="noreferrer"
                className="block text-xs text-sky-700 underline underline-offset-2"
              >
                Open source
              </a>
            ) : null}
          </div>
        ) : null}
      </div>
    );
  }

  function renderElectrocatalystPanel() {
    return (
      <div className="space-y-4">
        <div className="surface-ghost p-4">
          <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_320px] xl:items-start">
            <div>
              <div className="cp-subtle-label">Electrode stack</div>
              <div className="cp-heading-lg mt-2">Set the stack first, then price the preparation method.</div>
              <p className="mt-2 text-sm leading-7 text-slate-600">
                Catalyst powder, ionomer, membrane, and substrate each keep their own source record.
              </p>
              <p className="mt-2 text-xs leading-6 text-slate-500">
                Defaults prefer higher-confidence literature or sourced vendor rows when they exist.
              </p>
            </div>
            <div className="rounded-[24px] border border-slate-900/8 bg-white/72 p-4">
              <div className="cp-subtle-label">Application family</div>
              <div className="mt-3 grid gap-2">
                {ELECTRO_APPLICATION_OPTIONS.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => setApplicationFamily(option.value)}
                    className={`rounded-[18px] border px-3 py-3 text-left transition ${
                      applicationFamily === option.value
                        ? 'border-slate-950 bg-slate-950 text-white'
                        : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300'
                    }`}
                  >
                    <div className="font-semibold">{option.label}</div>
                    <div className={`mt-1 text-xs leading-5 ${applicationFamily === option.value ? 'text-slate-300' : 'text-slate-500'}`}>
                      {option.detail}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="grid gap-4 xl:grid-cols-2">
          <div className="surface-ghost p-4">
            <div className="cp-subtle-label">Material stack</div>
            <div className="mt-3 grid gap-3">
              <label className="block">
                <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Catalyst powder</div>
                <select value={electrocatalystConfig.catalystMaterialKey} onChange={(event) => updateElectroConfig({ catalystMaterialKey: event.target.value })} className="input-base mt-2">
                  <option value="">Select catalyst powder</option>
                  {catalystPowders.map((material) => (
                    <option key={String(material.id)} value={String(material.id)}>
                      {materialOptionLabel(material)}
                    </option>
                  ))}
                </select>
              </label>

              <label className="block">
                <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Ionomer</div>
                <select value={electrocatalystConfig.ionomerMaterialKey} onChange={(event) => updateElectroConfig({ ionomerMaterialKey: event.target.value })} className="input-base mt-2">
                  <option value="">Select ionomer</option>
                  {ionomerOptions.map((material) => (
                    <option key={String(material.id)} value={String(material.id)}>
                      {materialOptionLabel(material)}
                    </option>
                  ))}
                </select>
              </label>

              <label className="block">
                <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Membrane</div>
                <select value={electrocatalystConfig.membraneMaterialKey} onChange={(event) => updateElectroConfig({ membraneMaterialKey: event.target.value })} className="input-base mt-2">
                  <option value="">Select membrane</option>
                  {membraneOptions.map((material) => (
                    <option key={String(material.id)} value={String(material.id)}>
                      {materialOptionLabel(material)}
                    </option>
                  ))}
                </select>
              </label>

              <label className="block">
                <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Substrate / GDL</div>
                <select value={electrocatalystConfig.substrateMaterialKey} onChange={(event) => updateElectroConfig({ substrateMaterialKey: event.target.value })} className="input-base mt-2">
                  <option value="">Select substrate / GDL</option>
                  {substrateOptions.map((material) => (
                    <option key={String(material.id)} value={String(material.id)}>
                      {materialOptionLabel(material)}
                    </option>
                  ))}
                </select>
              </label>
            </div>
          </div>

          <div className="surface-ghost p-4">
            <div className="cp-subtle-label">Electrode geometry</div>
            <div className="mt-3 grid gap-3 sm:grid-cols-2">
              <label className="block">
                <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Active area</div>
                <div className="mt-2 flex items-center gap-2">
                  <input type="number" min="1" step="0.1" value={electrocatalystConfig.activeAreaCm2} onChange={(event) => updateElectroConfig({ activeAreaCm2: Number(event.target.value) })} className="input-base text-right font-mono" />
                  <span className="text-xs text-slate-500">cm2</span>
                </div>
              </label>

              <label className="block">
                <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Catalyst loading</div>
                <div className="mt-2 flex items-center gap-2">
                  <input type="number" min="0.01" step="0.01" value={electrocatalystConfig.catalystLoadingMgCm2} onChange={(event) => updateElectroConfig({ catalystLoadingMgCm2: Number(event.target.value) })} className="input-base text-right font-mono" />
                  <span className="text-xs text-slate-500">mg/cm2</span>
                </div>
              </label>

              <label className="block sm:col-span-2">
                <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Ionomer / catalyst ratio</div>
                <div className="mt-2 flex items-center gap-2">
                  <input type="number" min="0" step="0.05" value={electrocatalystConfig.ionomerToCatalystRatio} onChange={(event) => updateElectroConfig({ ionomerToCatalystRatio: Number(event.target.value) })} className="input-base max-w-[180px] text-right font-mono" />
                  <span className="text-xs text-slate-500">dry ionomer mass / catalyst powder mass</span>
                </div>
              </label>

              <label className="block sm:col-span-2">
                <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Preparation template</div>
                <select value={electrocatalystConfig.templateId} onChange={(event) => updateElectroConfig({ templateId: event.target.value })} className="input-base mt-2">
                  {electroTemplates.map((template) => (
                    <option key={template.id} value={template.id}>
                      {template.name}
                    </option>
                  ))}
                </select>
              </label>
            </div>
          </div>
        </div>

        <div className="grid gap-3 xl:grid-cols-4">
          {renderElectroMaterialCard('Catalyst powder', selectedCatalystMaterial, 'Choose a catalyst powder')}
          {renderElectroMaterialCard('Ionomer', selectedIonomerMaterial, 'Choose an ionomer')}
          {renderElectroMaterialCard('Membrane', selectedMembraneMaterial, 'Choose a membrane')}
          {renderElectroMaterialCard('Substrate / GDL', selectedSubstrateMaterial, 'Choose a substrate or GDL')}
        </div>

        {activeElectroTemplate ? (
          <div className="rounded-[24px] border border-emerald-200 bg-emerald-50/80 p-4">
            <div className="cp-subtle-label !text-emerald-700">Selected preparation template</div>
            <div className="mt-2 cp-heading-sm">{activeElectroTemplate.name}</div>
            <div className="mt-2 text-sm leading-6 text-emerald-900">{activeElectroTemplate.description}</div>
            <div className="mt-3 flex flex-wrap gap-2">
              <span className="cp-chip">{applicationFamilyLabel(applicationFamily)}</span>
              {activeElectroTemplate.manufacturing_mode ? <span className="cp-chip">{activeElectroTemplate.manufacturing_mode}</span> : null}
              <span className="cp-chip">{activeElectroTemplate.steps.length} steps</span>
            </div>
            <div className="mt-4 grid gap-3 lg:grid-cols-3">
              <div>
                <div className="cp-subtle-label !text-emerald-700">Pre-treatment</div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {(activeElectroTemplate.preprocess ?? []).map((item) => <span key={item} className="cp-chip">{item}</span>)}
                </div>
              </div>
              <div>
                <div className="cp-subtle-label !text-emerald-700">Synthesis / coating</div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {(activeElectroTemplate.synthesis ?? []).map((item) => <span key={item} className="cp-chip">{item}</span>)}
                </div>
              </div>
              <div>
                <div className="cp-subtle-label !text-emerald-700">Post-treatment</div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {(activeElectroTemplate.postprocess ?? []).map((item) => <span key={item} className="cp-chip">{item}</span>)}
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    );
  }

  function renderRows(role: 'active_metal' | 'promoter') {
    const items = rows.filter((row) => row.role === role);
      const copy = role === 'active_metal'
      ? { title: 'Active metals', description: 'These rows define the core cost basis and live price mapping.', accent: 'bg-[#78f2d0]', button: 'Add active metal', placeholder: 'At least one active metal is required.' }
      : { title: 'Promoters', description: 'Optional additives that change recipe cost and preparation choice.', accent: 'bg-[#88a8ff]', button: 'Add promoter', placeholder: 'No promoters added yet.' };

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

  function renderWorkspaceSummary() {
    const latestGenerated = latestSnapshotForCurrentCase
      ? new Date(latestSnapshotForCurrentCase.generatedAt).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })
      : null;
    const manualOverrideCount = catalystDomain === 'electrocatalyst'
      ? 0
      : rows.filter((row) => row.source_type === 'manual' && row.name.trim().length > 0).length;
    const recipeSummary = catalystDomain === 'electrocatalyst'
      ? `${selectedCatalystMaterial?.name ?? 'Catalyst'}, ${selectedIonomerMaterial?.name ?? 'Ionomer'}, ${selectedMembraneMaterial?.name ?? 'Membrane'}`
      : `${activeMetalCount} active metal${activeMetalCount === 1 ? '' : 's'} / ${supportWtPct.toFixed(1)} wt% support`;
    const preparationSummary =
      catalystDomain === 'electrocatalyst'
        ? activeElectroTemplate?.name ?? 'Select a preparation template'
        : activeBenchmark?.route.name ?? 'Manual step selection';
    const recoverySummary = catalystDomain === 'thermal'
      ? includeSpentValue
        ? `Recovery proxy on / ${reactorType} bed / ${catalystBulkDensity.toFixed(1)} lb/ft3`
        : 'Recovery proxy off'
      : applicationFamilyLabel(applicationFamily);

    return (
      <section className="surface-card p-4">
        <div className="grid gap-3 xl:grid-cols-[minmax(0,1.1fr)_minmax(0,1fr)_minmax(0,1fr)_minmax(0,1fr)]">
          <div className="rounded-[22px] border border-slate-900/8 bg-white/62 p-4">
            <div className="flex items-start justify-between gap-3">
              <div className="cp-subtle-label">Price basis</div>
              <button onClick={syncPrices} disabled={refreshing} className="cp-button-secondary px-3 py-2 text-xs">
                <span className={`mr-2 inline-flex h-3.5 w-3.5 rounded-full border-2 border-current border-t-transparent ${refreshing ? 'animate-spin' : ''}`} />
                {refreshing ? 'Refreshing' : 'Refresh'}
              </button>
            </div>
            <div className="mt-3 space-y-1">
              <CompactValueRow
                label="Status"
                value={refreshing ? 'Refreshing' : pricesUpdatedAt ? 'Ready' : 'Pending'}
                detail={pricesUpdatedAt
                  ? `${liveFeedCount} live / ${indexedFeedCount} indexed rows synced ${pricesUpdatedAt.toLocaleTimeString('en-US', {
                      hour: 'numeric',
                      minute: '2-digit',
                      hour12: true,
                    })}`
                  : 'Indexed and manual rows stay usable before the next live refresh.'}
              />
              <CompactValueRow label="Manual overrides" value={String(manualOverrideCount)} detail="Rows still detached from tracked feeds." />
            </div>
          </div>

          <div className="rounded-[22px] border border-slate-900/8 bg-white/62 p-4">
            <div className="cp-subtle-label">Current case</div>
            <div className="mt-2 text-base font-semibold text-slate-950">{catalystDomainLabel(catalystDomain)}</div>
            <div className="mt-2 text-sm leading-6 text-slate-600">{recipeSummary}</div>
            <div className="mt-3 flex flex-wrap gap-2">
              <span className="cp-chip">{catalystDomainLabel(catalystDomain)}</span>
              {catalystDomain === 'electrocatalyst' ? <span className="cp-chip">{applicationFamilyLabel(applicationFamily)}</span> : null}
              {activeBenchmark ? <span className="cp-chip">{activeBenchmark.title}</span> : null}
            </div>
          </div>

          <div className="rounded-[22px] border border-slate-900/8 bg-white/62 p-4">
            <div className="cp-subtle-label">Preparation basis</div>
            <div className="mt-2 text-base font-semibold text-slate-950">{preparationSummary}</div>
            <div className="mt-2 space-y-1">
              <CompactValueRow label="Campaign" value={`${orderSize} tons`} detail={`${scale.label} scale / ${scale.rate}`} />
              <CompactValueRow
                label="Steps"
                value={String(steps.length)}
                detail={steps.length > 0 ? `${formatStepLabel(steps[0])}${steps.length > 1 ? ` +${steps.length - 1}` : ''}` : 'Choose at least one step'}
              />
              <CompactValueRow
                label={catalystDomain === 'thermal' ? 'Recovery' : 'Family'}
                value={recoverySummary}
                detail={
                  catalystDomain === 'thermal'
                    ? 'Optional spent catalyst value proxy for recovery-sensitive screening.'
                    : 'Electrode stack family currently selected.'
                }
              />
            </div>
          </div>

          <div className="rounded-[22px] border border-slate-900/8 bg-[linear-gradient(180deg,#0f172a,#18253b)] p-4 text-white shadow-[0_14px_34px_rgba(15,23,42,0.14)]">
            <div className="flex items-start justify-between gap-3">
              <div className="cp-subtle-label !text-slate-400">Latest result</div>
              <button onClick={() => navigate('/calculator/result')} disabled={!latestSnapshotForCurrentCase} className="cp-button-ink px-3 py-2 text-xs">
                Open
              </button>
            </div>
            <div className="mt-3 flex items-end gap-2">
              <div className="font-display text-[2.35rem] leading-none text-white">
                {latestSnapshotForCurrentCase ? `$${toDisplay(latestSnapshotForCurrentCase.result.summary.estimated_price_per_lb).toFixed(2)}` : 'Pending'}
              </div>
              <div className="pb-1 text-sm text-slate-300">{latestSnapshotForCurrentCase ? fmtLabel : ''}</div>
            </div>
            <div className="mt-2 text-xs leading-6 text-slate-300">
              {latestSnapshotForCurrentCase
                ? `Generated ${latestGenerated}. ${latestSnapshotForCurrentCase.selectedSupportName ?? 'Support'} remained the active basis.`
                : 'No matching result for this workflow yet. Run the estimate once to populate this summary.'}
            </div>
          </div>
        </div>
      </section>
    );
  }

  function renderSetupSection() {
    return (
      <section className="surface-card p-5">
        <div>
          <div className="cp-subtle-label">Catalyst type</div>
          <h2 className="cp-heading-lg mt-2">Choose the workflow before you edit the recipe.</h2>
          <p className="mt-2 max-w-2xl text-sm leading-7 text-slate-600">
            Thermocatalyst keeps bulk composition and support balance together. Electrocatalyst separates catalyst powder, ionomer, membrane, and substrate.
          </p>
        </div>

        <div className="mt-5 grid gap-3 lg:grid-cols-2">
          {([
            {
              value: 'thermal' as const,
              title: 'Thermocatalyst',
              note: 'Use bulk composition, support share, and plant-style preparation steps in one estimate.',
              detail: 'Best for supported metal catalysts, mixed oxides, zeolites, and reforming or cracking routes.',
            },
            {
              value: 'electrocatalyst' as const,
              title: 'Electrocatalyst',
              note: 'Split the electrode stack into catalyst powder, ionomer, membrane, and substrate.',
              detail: 'Best for PEMFC, PEMWE, DMFC, and other electrode-preparation workflows.',
            },
          ]).map((option) => {
            const active = catalystDomain === option.value;
            return (
              <button
                key={option.value}
                onClick={() => handleCatalystDomainChange(option.value)}
                className={`rounded-[22px] border px-4 py-4 text-left transition ${
                  active
                    ? 'border-slate-950 bg-white shadow-[0_10px_24px_rgba(15,23,42,0.06)]'
                    : 'border-slate-200 bg-white/70 hover:border-slate-300 hover:bg-white'
                }`}
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="cp-heading-sm">{option.title}</div>
                  <span className={`inline-flex h-6 min-w-6 items-center justify-center rounded-full px-2 text-[10px] font-semibold uppercase tracking-[0.16em] ${
                    active ? 'bg-slate-950 text-white' : 'bg-slate-100 text-slate-500'
                  }`}>
                    {active ? 'On' : 'Off'}
                  </span>
                </div>
                <div className="mt-3 text-sm leading-6 text-slate-700">{option.note}</div>
                <div className="mt-2 text-xs leading-6 text-slate-500">{option.detail}</div>
              </button>
            );
          })}
        </div>

        <div className="mt-4 rounded-[20px] border border-slate-200 bg-slate-50/80 px-4 py-3 text-sm leading-6 text-slate-600">
          Changing workflow does not auto-advance. Review the selected mode, then move with <span className="font-semibold text-slate-950">Next</span>.
        </div>
      </section>
    );
  }

  function renderInputsSection() {
    if (catalystDomain === 'electrocatalyst') {
      return (
        <section className="surface-card p-5">
          <div>
            <div className="cp-subtle-label">Composition</div>
            <h2 className="cp-heading-lg mt-2">Build the electrode stack.</h2>
            <p className="mt-2 text-sm leading-7 text-slate-600">
              Choose the stored material records first, then tune the geometric inputs used for area-based costing.
            </p>
          </div>
          <div className="mt-5">{renderElectrocatalystPanel()}</div>
        </section>
      );
    }

    return (
      <section className="surface-card p-5">
        <div>
          <div className="cp-subtle-label">Composition</div>
          <h2 className="cp-heading-lg mt-2">Define the catalyst recipe.</h2>
          <p className="mt-2 text-sm leading-7 text-slate-600">
            Keep active metals and promoters explicit. Support share closes automatically so the mass basis stays readable.
          </p>
        </div>

        <div className="mt-5 space-y-3.5">
        {renderRows('active_metal')}
        {renderRows('promoter')}
        <div className="surface-ghost p-3.5">
          <div>
            <div className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-full bg-[#efc36c]" /><h3 className="cp-heading-sm">Support</h3></div>
            <p className="mt-1 text-xs leading-5 text-slate-500">Support share closes the mass balance automatically.</p>
          </div>
          {rows.filter((row) => row.role === 'support').map((row) => (
            <div key={row.id} className="mt-3.5 flex flex-wrap items-center gap-3">
              <select value={row.name} onChange={(event) => { const support = SUPPORT_OPTIONS.find((item) => item.name === event.target.value); updateRow(row.id, { name: event.target.value, price_per_lb: support?.price ?? row.price_per_lb, source_type: 'manual', source: 'Manual support default' }); }} className="input-base min-w-[180px] flex-[1.3_1_260px] pr-10">{SUPPORT_OPTIONS.map((support) => <option key={support.name} value={support.name}>{support.name} / {support.note}</option>)}</select>
              <div className="input-base flex min-w-[170px] flex-none items-center justify-between gap-3 bg-white/76"><span className="text-xs text-slate-500">Auto share</span><span className="font-mono text-slate-950">{supportWtPct.toFixed(1)} wt%</span></div>
              {priceField(row)}
            </div>
          ))}
        </div>
        </div>
      </section>
    );
  }

  function renderManufacturingSection() {
    return (
      <section className="surface-card p-5">
        <div>
          <div className="cp-subtle-label">Preparation method</div>
          <h2 className="cp-heading-lg mt-2">Choose the preparation basis.</h2>
          <p className="mt-2 text-sm leading-7 text-slate-600">
            {catalystDomain === 'electrocatalyst'
              ? 'Templates add pretreatment, coating, drying, lamination, and break-in steps. Adjust them if the lab route differs.'
              : 'Pick the industrial steps that best approximate the synthesis route, then let campaign size set the scale basis.'}
          </p>
        </div>

        <div className="mt-5 space-y-4">
        {activeBenchmark ? (
          <div className="rounded-[24px] border border-emerald-200 bg-emerald-50/80 px-4 py-4 text-sm text-emerald-900">
            <div className="cp-subtle-label !text-emerald-700">Loaded reference baseline</div>
            <div className="mt-2 font-semibold">{activeBenchmark.route.name}</div>
            <div className="mt-2 leading-6">{activeBenchmark.screening_summary}</div>
            <div className="mt-3 flex flex-wrap gap-2">
              <span className="cp-chip">{catalystDomainLabel(activeBenchmark.catalyst_domain)}</span>
              <span className="cp-chip">{applicationFamilyLabel(activeBenchmark.application_family)}</span>
            </div>
          </div>
        ) : null}
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
        {catalystDomain === 'thermal' ? (
          <div className="rounded-[24px] border border-slate-900/8 bg-white/72 p-4">
            <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
              <div className="max-w-2xl">
                <div className="cp-subtle-label">Recovery scenario</div>
                <div className="cp-heading-sm mt-2">Optional spent catalyst value proxy</div>
                <p className="mt-2 text-sm leading-7 text-slate-600">
                  Use this when the catalyst contains recoverable metal and end-of-life value matters to the screening decision.
                </p>
                <p className="mt-2 text-xs leading-6 text-slate-500">
                  Current engine includes support loss, reactor-type loss, refining loss, and recovery cost. Full deactivation and regeneration-cycle modeling is not yet included.
                </p>
              </div>
              <button
                onClick={() => setIncludeSpentValue((previous) => !previous)}
                className={`rounded-[18px] border px-4 py-2.5 text-sm font-semibold transition ${
                  includeSpentValue
                    ? 'border-emerald-200 bg-emerald-50 text-emerald-800'
                    : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300'
                }`}
              >
                {includeSpentValue ? 'Recovery on' : 'Recovery off'}
              </button>
            </div>

            <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
              <label className="block">
                <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Reactor type</div>
                <select
                  value={reactorType}
                  onChange={(event) => setReactorType(event.target.value as 'fixed' | 'slurry')}
                  className="input-base mt-2"
                >
                  <option value="fixed">Fixed bed</option>
                  <option value="slurry">Slurry</option>
                </select>
              </label>

              <label className="block">
                <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Bulk density</div>
                <div className="mt-2 flex items-center gap-2">
                  <input
                    type="number"
                    min="1"
                    step="0.1"
                    value={catalystBulkDensity}
                    onChange={(event) => setCatalystBulkDensity(Math.max(1, Number(event.target.value) || 1))}
                    className="input-base w-full text-right font-mono"
                  />
                  <span className="text-xs text-slate-500">lb/ft3</span>
                </div>
              </label>

              <div className="rounded-[18px] border border-slate-200 bg-slate-50/80 px-4 py-3">
                <div className="cp-subtle-label">Screening use</div>
                <div className="mt-2 text-sm leading-6 text-slate-700">
                  Best for Pt, Pd, Rh, Ru, Ir, Ni, and Co routes where salvage value changes the commercial basis.
                </div>
              </div>
            </div>
          </div>
        ) : null}
        </div>
      </section>
    );
  }

  const validationMessage = catalystDomain === 'electrocatalyst'
    ? isValid
      ? `Electrocatalyst stack is ready: ${selectedCatalystMaterial?.name ?? 'catalyst'}, ${selectedIonomerMaterial?.name ?? 'ionomer'}, ${selectedMembraneMaterial?.name ?? 'membrane'}, and ${selectedSubstrateMaterial?.name ?? 'GDL'} are all sourced from the library.`
      : 'Select catalyst powder, ionomer, membrane, substrate / GDL, and a preparation template before running the estimate.'
    : isValid
      ? `Recipe balance is valid: ${nonSupportWt.toFixed(1)} wt% actives and promoters, ${supportWtPct.toFixed(1)} wt% support.`
      : incompleteThermalRows.length > 0
        ? `Complete or remove ${incompleteThermalRows.length} unfinished composition row${incompleteThermalRows.length > 1 ? 's' : ''} before running the estimate.`
        : activeMetalCount === 0
        ? 'Add at least one active metal before running the estimate.'
        : nonSupportWt >= 100
          ? 'Active metals and promoters must stay below 100 wt% so support remains positive.'
          : 'Enter a valid non-zero loading for the active portion of the recipe.';

  const activeWorkspaceSection = sectionState.activeSection.id === 'type'
    ? renderSetupSection()
    : sectionState.activeSection.id === 'composition'
      ? renderInputsSection()
      : sectionState.activeSection.id === 'manufacturing'
        ? renderManufacturingSection()
        : (
          <section className="surface-card p-4">
            <div className={`rounded-[24px] border px-4 py-4 text-sm ${isValid ? 'border-emerald-200 bg-emerald-50 text-emerald-800' : 'border-amber-200 bg-amber-50 text-amber-800'}`}>{validationMessage}</div>
            <div className="mt-4 grid gap-3 sm:grid-cols-3">
              <MetricTile label="Catalyst type" value={catalystDomainLabel(catalystDomain)} detail="Current case basis" />
              <MetricTile label="Preparation steps" value={String(steps.length)} detail={steps.length > 0 ? 'Ready for execution' : 'Choose at least one step'} />
              <MetricTile label="Campaign basis" value={`${orderSize} tons`} detail={`${scale.label} / ${scale.rate}`} />
            </div>
            <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center">
              <button onClick={handleCalculate} disabled={loading || !isValid || steps.length === 0} className="cp-button-primary min-w-[250px]">{loading ? <><span className="mr-2 inline-flex h-4 w-4 animate-spin rounded-full border-2 border-slate-950 border-t-transparent" />Running estimate</> : 'Run estimate'}</button>
              <div className="text-xs leading-6 text-slate-500">The result screen opens separately and keeps this draft intact.</div>
            </div>
            {error ? <div className="mt-4 rounded-[24px] border border-red-200 bg-red-50 px-4 py-4 text-sm text-red-700"><span className="font-semibold">Calculation failed.</span> {error}</div> : null}
          </section>
        );

  return (
    <div className="space-y-4">
      <datalist id="known-metal-options">{KNOWN_METALS.map((metal) => <option key={metal} value={metal} />)}</datalist>
      <section className="surface-card cp-enter overflow-hidden px-4 py-4 sm:px-5" style={{ animationDelay: '0.06s' }}>
        <div className="space-y-5">
          <div className="flex flex-col gap-4 border-b border-slate-900/8 pb-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <div className="cp-subtle-label">Cost Estimate</div>
              <h2 className="cp-heading-xl mt-2">Estimate catalyst preparation cost with traceable inputs.</h2>
              <p className="cp-body-copy mt-2 max-w-2xl">
                {catalystDomain === 'electrocatalyst'
                  ? 'Move in order: choose workflow, build the stack, set the preparation basis, then run the result.'
                  : 'Move in order: choose workflow, define the recipe, set the preparation basis, then run the result.'}
              </p>
            </div>
            <span className="cp-chip">{sectionState.activeSection.label}</span>
          </div>
        </div>
      </section>

      <WorkspaceSectionNav sections={ESTIMATE_SECTIONS} activeSectionId={sectionState.activeSectionId} activeIndex={sectionState.activeIndex} onSelect={sectionState.setActiveSection} />

      {renderWorkspaceSummary()}

      <div className="space-y-4">{activeWorkspaceSection}</div>

      <WorkspaceSectionFooter
        activeSection={sectionState.activeSection}
        activeIndex={sectionState.activeIndex}
        totalSections={ESTIMATE_SECTIONS.length}
        onPrevious={sectionState.goPrevious}
        onNext={sectionState.goNext}
        canGoPrevious={sectionState.canGoPrevious}
        canGoNext={sectionState.canGoNext}
      />
    </div>
  );
}
