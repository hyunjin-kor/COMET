export interface InputEvidence {
  kind: 'literature' | 'measured' | 'supplier' | 'assumption';
  citation: string;
  locator?: string;
  url?: string;
  doi?: string;
  accessed_on?: string;
  recorded_value: number | string | boolean | null;
  note?: string;
}

export interface SourcedInputs { input_evidence?: Record<string, InputEvidence> }

export interface TemperatureSegment extends SourcedInputs {
  target_c: number | null;
  ramp_c_per_min?: number | null;
  hold_h?: number | null;
  ramp_power_kw?: number | null;
  hold_power_kw?: number | null;
}

export interface ProcessGas extends SourcedInputs {
  name: string;
  comparison_key?: string;
  flow_l_per_min?: number | null;
  duration_h?: number | null;
  duration_basis?: 'entered' | 'operation' | 'holds';
  price_usd_per_m3?: number | null;
  volume_basis: string;
}

export interface ManufacturingOperation extends SourcedInputs {
  name: string;
  intermediate_batch_id?: string;
  equipment?: string;
  equipment_comparison_key?: string;
  atmosphere?: string;
  pressure_bar_abs?: number | null;
  stirring_rpm?: number | null;
  ph?: number | null;
  solvent?: string;
  solvent_volume_ml?: number | null;
  repetitions?: number;
  start_temperature_c?: number | null;
  temperature_profile?: TemperatureSegment[];
  duration_h?: number | null;
  additional_time_h?: number | null;
  average_power_kw?: number | null;
  additional_power_kw?: number | null;
  measured_energy_kwh?: number | null;
  energy_basis?: 'power' | 'measured';
  equipment_usd_h?: number | null;
  attended_labor_h?: number | null;
  other_cost_usd?: number | null;
  gases?: ProcessGas[];
  purchases?: BatchPurchase[];
  notes?: string;
}

export interface BatchPurchase extends SourcedInputs {
  name: string;
  comparison_key?: string;
  quantity?: number | null;
  unit: 'kg' | 'g' | 'L' | 'mL' | 'mol' | 'mmol' | 'item';
  quantity_basis?: 'entered' | 'solvent_volume';
  price_usd_per_unit?: number | null;
  notes?: string;
}

export interface ManufacturingProtocol extends SourcedInputs {
  mode: 'record_only' | 'batch_cost';
  product_basis?: 'catalyst_powder' | 'electrode';
  materials_basis?: 'composition' | 'purchases';
  source_record_id?: string;
  finished_batch_mass_kg?: number | null;
  electricity_usd_kwh?: number | null;
  labor_usd_h?: number | null;
  selling_margin_fraction?: number;
  source_note?: string;
  intermediate_batches?: IntermediateBatch[];
  operations: ManufacturingOperation[];
}

export interface IntermediateBatch extends SourcedInputs {
  id: string;
  name: string;
  allocation_basis?: 'mass_used' | 'volume_used' | 'whole_batch';
  destination_batch_id?: string;
  produced_mass_kg?: number | null;
  used_mass_kg?: number | null;
  produced_volume_ml?: number | null;
  used_volume_ml?: number | null;
  notes?: string;
}

export interface LiteratureProtocol extends SourcedInputs {
  id: string;
  doi: string;
  title: string;
  url: string;
  sample: string;
  locator: string;
  boundary: 'catalyst_powder' | 'electrode';
  limitations: string[];
  operations: ManufacturingOperation[];
  intermediate_batches?: IntermediateBatch[];
  finished_batch_mass_kg?: number | null;
  review_date: string;
  verification: string;
}

export interface ManufacturingOperatingReference {
  id: string;
  label: string;
  label_ko: string;
  category: 'electricity' | 'labor' | 'equipment';
  value: number;
  unit: string;
  import_field: 'electricity_usd_kwh' | null;
  period: string;
  geography: string;
  scope: string;
  scope_ko: string;
  evidence: InputEvidence;
  supporting_urls?: string[];
}

export function applyOperatingReference(protocol: ManufacturingProtocol, reference: ManufacturingOperatingReference): ManufacturingProtocol {
  if (reference.import_field !== 'electricity_usd_kwh') return protocol;
  return { ...protocol, electricity_usd_kwh: reference.value,
    input_evidence: { ...protocol.input_evidence, electricity_usd_kwh: structuredClone(reference.evidence) } };
}

export interface ManufacturingEvidence {
  family: string;
  slug: string;
  title: string;
  status: 'screening_only' | 'source_mismatch' | 'variant_available';
  notes: string[];
  profile_ids: string[];
  profiles: LiteratureProtocol[];
  doi_count: number;
  crossref_verified_count: number;
  review_date: string;
}

export function adaptLiteratureProtocol(profile: LiteratureProtocol): ManufacturingProtocol {
  return {
    mode: 'record_only', product_basis: profile.boundary, source_record_id: profile.id,
    intermediate_batches: structuredClone(profile.intermediate_batches ?? []),
    finished_batch_mass_kg: profile.finished_batch_mass_kg,
    input_evidence: structuredClone(profile.input_evidence ?? {}),
    source_note: `${profile.sample}; ${profile.url}; ${profile.locator}. User adaptation: review composition, precursors and process boundary before costing. ${profile.limitations.join(' ')}`,
    operations: structuredClone(profile.operations).map((op) => ({ ...op, notes: `${op.notes ?? ''} [${profile.locator}; ${profile.doi}]` })),
  };
}

export interface ManufacturingReport {
  mode: ManufacturingProtocol['mode'];
  protocol: ManufacturingProtocol;
  complete: boolean;
  missing_inputs: string[];
  serial_operation_hours: number | null;
  allocated_operation_hours?: number | null;
  intermediate_batches?: Array<IntermediateBatch & { allocation_fraction: number | null; transfer_fraction: number | null }>;
  batch_processing_cost_usd: number | null;
  processing_cost_usd_kg: number | null;
  manufacturing_cost_usd_kg?: number;
  batch_materials_cost_usd?: number | null;
  purchases?: Array<{ operation: number; name: string; quantity: number | null; unit: string; price_usd_per_unit: number | null; cost_usd: number | null; cost_usd_kg: number | null; quantity_basis: string; incurred_cost_usd?: number | null; allocation_fraction?: number | null; intermediate_batch_id?: string }>;
  electricity_kwh_per_kg: number | null;
  batch_equivalents?: number;
  boundary: string;
  trace?: {
    protocol_sha256: string;
    inputs: Array<{ path: string; value: number | string | boolean | null; unit: string;
      effect: 'cost_input' | 'record_only' | 'inactive'; source_status: string; evidence: InputEvidence | null }>;
    calculations: Array<{ id: string; formula: string; input_paths: string[]; value: number | null; unit: string; operation: number | null }>;
    coverage: Record<string, number>;
    headline_uses_protocol: boolean;
    cost_ledger: Array<{ category: string; value: number; unit: string; basis: string }>;
    overhead_inputs?: { ga_fraction: number; sard_fraction: number; selling_margin_fraction: number; source_status: string };
    recovery_adjustment?: { enabled: boolean; gross_selling_price_usd_kg: number; applied_credit_usd_kg: number; net_cost_usd_kg: number; basis: string };
    note: string;
  };
  operations: Array<{
    index: number;
    name: string;
    repetitions: number;
    duration_h: number | null;
    electricity_kwh: number | null;
    cost_usd: number | null;
    costs_usd: Record<string, number> | null;
    incurred_cost_usd?: number | null;
    incurred_costs_usd?: Record<string, number> | null;
    allocation_fraction?: number | null;
    intermediate_batch_id?: string;
    gases: Array<{ name: string; duration_h: number | null; duration_basis: string; volume_m3: number | null; cost_usd: number | null; volume_basis: string }>;
  }>;
}
