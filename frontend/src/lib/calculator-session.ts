import type { ApplicationFamily, CostResult, DecisionCandidate } from './api';

export type CalculatorRole = 'active_metal' | 'active_catalyst' | 'promoter' | 'support';
export type CalculatorSourceType = 'live' | 'indexed' | 'manual';

export interface CalculatorRow {
  id: string;
  role: CalculatorRole;
  name: string;
  wt_pct: number;
  price_per_lb: number;
  source_type: CalculatorSourceType;
  source: string;
}

export interface CalculatorDraft {
  rows: CalculatorRow[];
  steps: string[];
  catalystDomain: 'thermal' | 'electrocatalyst';
  applicationFamily?: ApplicationFamily;
  orderSize: number;
  pricesUpdatedAt: string | null;
  electrocatalystConfig?: {
    catalystMaterialKey: string;
    ionomerMaterialKey: string;
    membraneMaterialKey: string;
    substrateMaterialKey: string;
    activeAreaCm2: number;
    catalystLoadingMgCm2: number;
    ionomerToCatalystRatio: number;
    templateId: string;
  } | null;
  benchmarkCandidate?: CalculatorBenchmarkPreset | null;
}

export interface CalculatorResultSnapshot {
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
}

export type CalculatorBenchmarkPreset = Pick<
  DecisionCandidate,
  'slug' | 'title' | 'archetype' | 'screening_basis' | 'screening_summary' | 'catalyst_domain' | 'application_family' | 'route' | 'scores' | 'decision_notes'
>;

const DRAFT_KEY = 'catprice_calculator_draft';
const RESULT_KEY = 'catprice_calculator_result';

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
