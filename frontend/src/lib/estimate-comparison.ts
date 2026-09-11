import { request, type CostResult, type PriceBasis } from './api';

export interface EstimateComparisonInput {
  estimate_ids: number[];
  reference_estimate_id: number;
  price_basis: PriceBasis;
  order_size_tons: number;
}

export interface EstimateComparisonResult {
  reference_estimate_id: number;
  catalyst_domain: string;
  application_family: string;
  unit: 'USD/lb' | 'USD/cm2';
  common_conditions: Record<string, unknown>;
  warnings: string[];
  price_snapshot: Array<{
    key: string;
    values: Record<string, number | string>;
    source_estimate_id: number;
    source_estimate_name: string;
    overridden_estimate_ids: number[];
    evidence: Record<string, unknown> | null;
  }>;
  estimates: Array<{
    estimate_id: number;
    name: string;
    saved_at: string;
    saved: CostResult;
    repriced_original_conditions: CostResult;
    common_conditions: CostResult;
    values: {
      saved: number | null;
      repriced_original_conditions: number | null;
      common_conditions: number | null;
    };
  }>;
}

export async function compareSavedEstimates(input: EstimateComparisonInput): Promise<EstimateComparisonResult> {
  return request<EstimateComparisonResult>('/estimates/compare', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  });
}
