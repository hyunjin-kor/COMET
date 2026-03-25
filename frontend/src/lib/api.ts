const BASE = '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

// Calculator
export interface ComponentInput {
  role: 'active_metal' | 'promoter' | 'support';
  name: string;
  wt_pct: number;
  price_per_lb: number;
  precursor_markup?: number;
}

export interface CostInput {
  components: ComponentInput[];
  steps: string[];
  order_size_tons: number;
  ga_overhead_pct?: number;
  sard_pct?: number;
  basis_year?: number;
  target_year?: number;
  include_spent_value?: boolean;
  reactor_type?: string;
  catalyst_bulk_density?: number;
}

export interface ComponentBreakdown {
  role: string;
  name: string;
  wt_pct: number;
  wt_frac: number;
  price_per_lb: number;
  precursor_markup: number;
  cost_per_lb_cat: number;
  cost_pct: number;
}

export interface CostResult {
  input_summary: Record<string, unknown>;
  materials: {
    components: ComponentBreakdown[];
    total_materials_cost_per_lb: number;
  };
  step_method: {
    scale: string;
    campaign_days: number;
    processing_cost_per_lb: number;
    estimated_price_per_lb: number;
    estimated_price_per_kg: number;
    margin_pct: number;
    [key: string]: unknown;
  };
  summary: {
    estimated_price_per_lb: number;
    estimated_price_per_kg: number;
    net_cost_per_lb: number;
    net_cost_per_kg: number;
    materials_pct: number;
    processing_pct: number;
  };
}

export const calculateCost = (input: CostInput) =>
  request<CostResult>('/calculate', {
    method: 'POST',
    body: JSON.stringify(input),
  });

// Prices
export interface MetalPrice {
  symbol: string;
  name: string;
  price: number;
  unit: string;
  source: string;
  is_live: boolean;
  fetched_at: string | null;
}

export const fetchPrices = () => request<MetalPrice[]>('/prices');
export const fetchPrice = (symbol: string) => request<MetalPrice>(`/prices/${symbol}`);

// Materials
export interface MaterialItem {
  id: string | number;
  name: string;
  symbol: string | null;
  formula: string | null;
  category: string;
  mw: number | null;
  density: number | null;
  concentration_pct: number | null;
  price: number | null;
  price_unit: string | null;
  quote_year: number | null;
  quote_source: string;
  notes: string;
  has_lab_data: boolean;
  is_custom: boolean;
}

export const fetchMaterials = (category?: string, q?: string) => {
  const params = new URLSearchParams();
  if (category) params.set('category', category);
  if (q) params.set('q', q);
  const qs = params.toString();
  return request<MaterialItem[]>(`/materials${qs ? `?${qs}` : ''}`);
};

// Templates
export interface ProcessTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  example_catalysts: string[];
  steps: string[];
}

export const fetchTemplates = () => request<ProcessTemplate[]>('/materials/templates');

// Steps
export interface StepLibraryItem {
  name: string;
  key: string;
  cost_small: number | null;
  cost_medium: number | null;
  cost_large: number | null;
  note: string;
  basis: string;
}

export const fetchSteps = () =>
  request<StepLibraryItem[]>('/materials/steps');

// Health
export const checkHealth = () => request<{ status: string; version: string }>('/health');

// Refresh prices
export const refreshPrices = () =>
  request<{ status: string; prices_fetched: number }>('/prices/refresh', { method: 'POST' });
