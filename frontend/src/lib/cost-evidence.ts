import { apiUrl } from './api';

export interface PurchaseEvidence {
  supplier?: string;
  quote_date?: string;
  quantity?: number;
  quantity_unit?: string;
  grade?: string;
  cost_boundary?: string;
  reference?: string;
  notes?: string;
}

export interface ObservedComponent {
  name: string;
  wt_pct: number;
  grade?: string;
}

export interface ActualCostObservation {
  observed_price: number;
  currency: string;
  price_unit: 'lb' | 'kg' | 'cm2';
  observation_date: string;
  price_period?: string;
  order_size_tons?: number;
  production_rate_ton_per_day?: number;
  components: ObservedComponent[];
  template_id?: string;
  steps: string[];
  cost_boundary: 'material_purchase' | 'full_manufacturing_cost' | 'full_selling_price' | 'full_net_after_recovery' | 'other';
  cost_scope_note: string;
  production_conditions_note: string;
  source: string;
  evidence_type: 'supplier_quote' | 'invoice' | 'production_record' | 'public_literature' | 'other';
  verified_by_user: boolean;
  notes: string;
}

export interface CostObservationSummary {
  expected_reference: {
    catalyst_domain: string;
    components: { name: string | null; wt_pct: number | null; grade: string | null }[];
    order_size_tons: number | null;
    production_rate_ton_per_day: number | null;
    template_id: string | null;
    steps: string[];
    price_period: string | null;
    price_basis: string;
  };
  observations: {
    id: string;
    recorded_at: string;
    observation: ActualCostObservation;
    assessment: {
      eligible: boolean;
      exclusion_reasons: string[];
      predicted_price: number | null;
      signed_error_pct: number | null;
      absolute_percentage_error: number | null;
      verification: string;
    };
  }[];
  eligible_count: number;
  mape_pct: number | null;
  verification: string;
}

async function evidenceRequest(estimateId: number, observation?: ActualCostObservation, signal?: AbortSignal) {
  const response = await fetch(apiUrl(`/estimates/${estimateId}/observations`), {
    method: observation ? 'POST' : 'GET',
    headers: { 'Content-Type': 'application/json' },
    body: observation ? JSON.stringify(observation) : undefined,
    signal,
  });
  const body = await response.json();
  if (!response.ok) {
    const detail = body.detail;
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }
  return body as CostObservationSummary;
}

export function fetchCostObservations(estimateId: number, signal?: AbortSignal) {
  return evidenceRequest(estimateId, undefined, signal);
}

export function addCostObservation(estimateId: number, observation: ActualCostObservation) {
  return evidenceRequest(estimateId, observation);
}
