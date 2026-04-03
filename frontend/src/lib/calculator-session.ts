import type { CostResult } from './api';

export type CalculatorRole = 'active_metal' | 'promoter' | 'support';
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
  orderSize: number;
  pricesUpdatedAt: string | null;
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
}

const DRAFT_KEY = 'catprice_calculator_draft';
const RESULT_KEY = 'catprice_calculator_result';

function canUseStorage(): boolean {
  return typeof window !== 'undefined' && typeof window.localStorage !== 'undefined';
}

function readJson<T>(key: string): T | null {
  if (!canUseStorage()) return null;

  try {
    const raw = window.localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : null;
  } catch {
    return null;
  }
}

function writeJson<T>(key: string, value: T): void {
  if (!canUseStorage()) return;
  window.localStorage.setItem(key, JSON.stringify(value));
}

export function loadCalculatorDraft(): CalculatorDraft | null {
  return readJson<CalculatorDraft>(DRAFT_KEY);
}

export function saveCalculatorDraft(draft: CalculatorDraft): void {
  writeJson(DRAFT_KEY, draft);
}

export function loadCalculatorResultSnapshot(): CalculatorResultSnapshot | null {
  return readJson<CalculatorResultSnapshot>(RESULT_KEY);
}

export function saveCalculatorResultSnapshot(snapshot: CalculatorResultSnapshot): void {
  writeJson(RESULT_KEY, snapshot);
}
