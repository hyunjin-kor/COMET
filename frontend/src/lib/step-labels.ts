// Display names for unit-operation keys, mirroring ALL_STEPS in Calculator.tsx.
// Used where only the raw key is stored (e.g. the saved draft) so users never
// see snake_case identifiers.
const STEP_LABELS: Record<string, string> = {
  mixer_dry_blender: 'Dry Blender',
  mixer_slurry: 'Slurry Mixer',
  ionomer_ink_homogenization: 'Ionomer Ink Homogenization',
  ultrasonic_dispersion: 'Ultrasonic Dispersion',
  incipient_wetness: 'Incipient Wetness',
  ccm_coating_pass: 'CCM Coating Pass',
  reactor_simple: 'Simple Reactor',
  reactor_multistep: 'Multistep Reactor',
  membrane_pretreatment: 'Membrane Pretreatment',
  substrate_pretreatment: 'Substrate Pretreatment',
  ion_exchange_conversion: 'Ion-Exchange Conversion',
  electrochemical_break_in: 'Electrochemical Break-In',
  crystallizer: 'Crystallizer',
  dryer_batch_vacuum_tray: 'Vacuum Tray Dryer',
  'dryer_rotary_40_100C': 'Rotary Dryer 40-100 C',
  'dryer_rotary_100_300C': 'Rotary Dryer 100-300 C',
  electrode_drying_low_temp: 'Electrode Drying <100 C',
  dryer_spray: 'Spray Dryer',
  kiln_batch: 'Batch Kiln',
  kiln_continuous_direct: 'Continuous Kiln Direct',
  kiln_continuous_indirect: 'Continuous Kiln Indirect',
  filter_belt_vacuum: 'Belt Vacuum Filter',
  filter_plate_frame: 'Plate and Frame Filter',
  filter_rotary_vacuum: 'Rotary Vacuum Filter',
  extruder_with_feeder: 'Extruder with Feeder',
  hot_press_lamination: 'Hot Press Lamination',
  ball_forming: 'Ball Forming',
  mill: 'Mill',
  flare: 'Flare',
  scrubber_nox: 'NOx Scrubber',
};

export function stepDisplayLabel(stepKey: string): string {
  return STEP_LABELS[stepKey] ?? stepKey.replace(/_/g, ' ');
}
