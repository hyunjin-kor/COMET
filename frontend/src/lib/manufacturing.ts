export interface TemperatureSegment {
  target_c: number | null;
  ramp_c_per_min?: number | null;
  hold_h?: number | null;
  ramp_power_kw?: number | null;
  hold_power_kw?: number | null;
}

export interface ProcessGas {
  name: string;
  flow_l_per_min?: number | null;
  duration_h?: number | null;
  price_usd_per_m3?: number | null;
  volume_basis: string;
}

export interface ManufacturingOperation {
  name: string;
  equipment?: string;
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
  notes?: string;
}

export interface ManufacturingProtocol {
  mode: 'record_only' | 'batch_cost';
  finished_batch_mass_kg?: number | null;
  electricity_usd_kwh?: number | null;
  labor_usd_h?: number | null;
  selling_margin_fraction?: number;
  source_note?: string;
  operations: ManufacturingOperation[];
}

export interface ManufacturingReport {
  mode: ManufacturingProtocol['mode'];
  protocol: ManufacturingProtocol;
  complete: boolean;
  missing_inputs: string[];
  serial_operation_hours: number | null;
  batch_processing_cost_usd: number | null;
  processing_cost_usd_kg: number | null;
  manufacturing_cost_usd_kg?: number;
  electricity_kwh_per_kg: number | null;
  batch_equivalents?: number;
  boundary: string;
  operations: Array<{
    index: number;
    name: string;
    repetitions: number;
    duration_h: number | null;
    electricity_kwh: number | null;
    cost_usd: number | null;
    costs_usd: Record<string, number> | null;
  }>;
}
