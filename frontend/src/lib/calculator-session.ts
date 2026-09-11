import type { ApplicationFamily, CostInput, CostResult, DecisionCandidate } from './api';
import type { PurchaseEvidence } from './cost-evidence';
import type { ConsumableDraft, RecipeDraft } from './recipe-inputs';

export type CalculatorRole = 'active_metal' | 'active_catalyst' | 'promoter' | 'support';
export type CalculatorSourceType = 'live' | 'indexed' | 'manual';

export interface CalculatorRow {
  id: string;
  role: CalculatorRole;
  name: string;
  material_key?: string | null;
  symbol?: string | null;
  selection_key?: string | null;
  wt_pct: number;
  price_per_lb: number;
  source_type: CalculatorSourceType;
  source: string;
  recipe_consumption?: RecipeDraft;
  purchase_evidence?: PurchaseEvidence;
}

export interface CalculatorDraft {
  rows: CalculatorRow[];
  steps: string[];
  preparationStepBasis?: string[];
  preparationStepSubstitutions?: Array<{ from: string; to: string }>;
  thermalTemplateId?: string | null;
  catalystDomain: 'thermal' | 'electrocatalyst';
  applicationFamily?: ApplicationFamily;
  orderSize: number;
  productionRate?: number | '';
  productionRateNote?: string;
  consumables?: ConsumableDraft[];
  pricesUpdatedAt: string | null;
  includeSpentValue?: boolean;
  reactorType?: 'fixed' | 'slurry';
  catalystBulkDensity?: number;
  electrocatalystConfig?: {
    catalystMaterialKey: string;
    ionomerMaterialKey: string;
    membraneMaterialKey: string;
    substrateMaterialKey: string;
    activeAreaCm2: number;
    catalystLoadingMgCm2: number;
    ionomerToCatalystRatio: number;
    templateId: string;
    manufacturingScenario?: '' | 'rnd_batch' | 'pilot_roll_to_roll';
  } | null;
  benchmarkCandidate?: CalculatorBenchmarkPreset | null;
}

export interface CalculatorResultSnapshot {
  savedEstimateId?: number;
  result: CostResult;
  orderSize: number;
  steps: string[];
  stepLabels: string[];
  selectedSupportName: string | null;
  activeMetalCount: number;
  liveFeedCount: number;
  indexedFeedCount: number;
  nonSupportWt: number;
  supportWtPct: number;
  generatedAt: string;
  benchmarkCandidate?: CalculatorBenchmarkPreset | null;
  costInput?: CostInput | null;
}

export type CalculatorBenchmarkPreset = Pick<
  DecisionCandidate,
  'slug' | 'title' | 'archetype' | 'screening_basis' | 'screening_summary' | 'catalyst_domain' | 'application_family' | 'route' | 'scores' | 'decision_notes'
>;

const DRAFT_KEY = 'comet_calculator_draft';
const RESULT_KEY = 'comet_calculator_result';

function canUseStorage(): boolean {
  return typeof window !== 'undefined' && typeof window.localStorage !== 'undefined';
}

function canUseSessionStorage(): boolean {
  return typeof window !== 'undefined' && typeof window.sessionStorage !== 'undefined';
}

function readSessionJson<T>(key: string): T | null {
  if (!canUseSessionStorage()) return null;

  try {
    const raw = window.sessionStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : null;
  } catch {
    return null;
  }
}

function writeSessionJson<T>(key: string, value: T): void {
  if (!canUseSessionStorage()) return;
  window.sessionStorage.setItem(key, JSON.stringify(value));
}

export function loadCalculatorDraft(): CalculatorDraft | null {
  if (canUseStorage()) {
    // Clear legacy persistent drafts so reopening the desktop app starts clean.
    window.localStorage.removeItem(DRAFT_KEY);
  }
  return readSessionJson<CalculatorDraft>(DRAFT_KEY);
}

export function saveCalculatorDraft(draft: CalculatorDraft): void {
  writeSessionJson(DRAFT_KEY, draft);
}

export function loadCalculatorResultSnapshot(): CalculatorResultSnapshot | null {
  if (canUseStorage()) {
    // Clear legacy persistent results so restarting the desktop app starts clean.
    window.localStorage.removeItem(RESULT_KEY);
  }
  return readSessionJson<CalculatorResultSnapshot>(RESULT_KEY);
}

export function saveCalculatorResultSnapshot(snapshot: CalculatorResultSnapshot): void {
  writeSessionJson(RESULT_KEY, snapshot);
}
