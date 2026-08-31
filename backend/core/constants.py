"""Manufacturing coefficients, thermodynamic constants, and scale factors.

All constants are sourced from public literature (Peters & Timmerhaus,
Baddour et al. 2018, Van Allsburg et al. 2022).
"""

# --- Unit conversion constants ---
KG_PER_LB = 0.453592
LB_PER_KG = 2.20462
G_PER_TROY_OZ = 31.1035
LB_PER_TROY_OZ = 0.0685714
TROY_OZ_PER_LB = 14.5833
LB_PER_TON = 2000  # short ton
LB_PER_METRIC_TON = 2204.62

# --- Step Method constants (Chapter 6) ---
STEP_COSTS: dict[str, dict[str, float | None]] = {
    "ball_forming":              {"small": 100, "medium": 150, "large": None},
    "crystallizer":              {"small": 100, "medium": 200, "large": 300},
    "dryer_batch_vacuum_tray":   {"small": 50,  "medium": None, "large": None},
    "dryer_rotary_40_100C":      {"small": 75,  "medium": 100, "large": 200},
    "dryer_rotary_100_300C":     {"small": 100, "medium": 150, "large": 300},
    "dryer_spray":               {"small": None, "medium": 300, "large": 550},
    "extruder_with_feeder":      {"small": 100, "medium": 200, "large": 425},
    "filter_belt_vacuum":        {"small": 125, "medium": 175, "large": 400},
    "filter_plate_frame":        {"small": 75,  "medium": None, "large": None},
    "filter_rotary_vacuum":      {"small": None, "medium": 100, "large": 300},
    "flare":                     {"small": 50,  "medium": 75,  "large": 150},
    "incipient_wetness":         {"small": 75,  "medium": 100, "large": 200},
    "kiln_batch":                {"small": 75,  "medium": None, "large": None},
    "kiln_continuous_direct":    {"small": None, "medium": 225, "large": 400},
    "kiln_continuous_indirect":  {"small": None, "medium": 175, "large": 325},
    "mill":                      {"small": 50,  "medium": 100, "large": 200},
    "mixer_dry_blender":         {"small": 50,  "medium": 100, "large": 200},
    "mixer_slurry":              {"small": 75,  "medium": 100, "large": 200},
    "membrane_pretreatment":     {"small": 30,  "medium": 60,  "large": 200},
    "substrate_pretreatment":    {"small": 30,  "medium": 60,  "large": 200},
    "ion_exchange_conversion":   {"small": 30,  "medium": 60,  "large": 200},
    "ionomer_ink_homogenization":{"small": 75,  "medium": 100, "large": 200},
    "ultrasonic_dispersion":     {"small": 75,  "medium": 100, "large": 200},
    "ccm_coating_pass":          {"small": 75,  "medium": 100, "large": 200},
    "electrode_drying_low_temp": {"small": 75,  "medium": 100, "large": 200},
    "hot_press_lamination":      {"small": 100, "medium": 200, "large": 425},
    "reactor_simple":            {"small": 30,  "medium": 60,  "large": 200},
    "reactor_multistep":         {"small": 100, "medium": 175, "large": 600},
    "electrochemical_break_in":  {"small": 30,  "medium": 60,  "large": 200},
    "scrubber_nox":              {"small": 35,  "medium": 75,  "large": 200},
}

SCALE_THRESHOLDS: dict[str, tuple[float, float]] = {
    "small":  (1, 5),
    "medium": (5, 70),
    "large":  (70, 1000),
}

PRODUCTION_RATES: dict[str, float] = {
    "small": 1,     # tons/day
    "medium": 10,
    "large": 150,
}

CLEANING_TIME: dict[str, float] = {
    "small": 0.5,   # days
    "medium": 1.0,
    "large": 1.0,
}

HOURS_PER_DAY = 24  # continuous operation

# --- Selling margin regression (Figure 6.3) ---
MARGIN_COEFFICIENT = 39.192
MARGIN_EXPONENT = -0.23360

# --- Default overhead factors ---
DEFAULT_GA_OVERHEAD_PCT = 0.05   # General & Administrative
DEFAULT_SARD_PCT = 0.05          # Sales, Admin, R&D

# --- CapEx Factors (Table 7.1, Peters & Timmerhaus) ---
CAPEX_FACTORS_DEFAULT: dict[str, float] = {
    # Direct Capital
    "purchased_equipment": 1.00,
    "installation": 0.47,
    "instrumentation": 0.36,
    "piping": 0.68,
    "electrical": 0.11,
    "buildings": 0.18,
    "yard_improvements": 0.10,
    "service_facilities": 0.70,
    "land": 0.06,
    # Indirect Capital
    "engineering_supervision": 0.33,
    "construction": 0.41,
    "legal": 0.04,
    "contractors_fee": 0.19,
    "contingency": 0.44,
    # Working Capital
    "working_capital": 0.89,
}

# --- OpEx Factors (Table 7.2) ---
OPEX_FACTORS_DEFAULT: dict[str, float] = {
    "supervisory_clerical": 0.18,
    "laboratory": 0.15,
    "maintenance_repair": 0.05,
    "operating_supplies": 0.15,
    "local_taxes": 0.025,
    "insurance": 0.008,
    "rent": 0.10,
    "plant_overhead": 0.60,
    "administration": 0.20,
    "distribution_marketing": 0.10,
    "rnd": 0.05,
}

# --- Spent catalyst recovery (Chapter 9) ---
LOSSES_USE: dict[str, dict[str, dict[str, float]]] = {
    "TiO2":      {"fixed": {"support": 0.02, "metal": 0.10}, "slurry": {"support": 0.03, "metal": 0.125}},
    "Al2O3":     {"fixed": {"support": 0.02, "metal": 0.03}, "slurry": {"support": 0.02, "metal": 0.04}},
    "SiO2":      {"fixed": {"support": 0.02, "metal": 0.03}, "slurry": {"support": 0.02, "metal": 0.04}},
    "Carbon":    {"fixed": {"support": 0.02, "metal": 0.025}, "slurry": {"support": 0.06, "metal": 0.05}},
    "Carbonate": {"fixed": {"support": 0.05, "metal": 0.05}, "slurry": {"support": 0.05, "metal": 0.05}},
    "Clay":      {"fixed": {"support": 0.05, "metal": 0.05}, "slurry": {"support": 0.05, "metal": 0.05}},
    "ZrO2":      {"fixed": {"support": 0.02, "metal": 0.10}, "slurry": {"support": 0.03, "metal": 0.125}},
    "Sponge of metal (no support)": {
        "fixed": {"support": 0.0, "metal": 0.05},
        "slurry": {"support": 0.0, "metal": 0.05},
    },
}

LOSSES_REFINING: dict[str, dict[str, float]] = {
    "Pd": {"high": 0.04, "low": 0.01, "avg": 0.025},
    "Pt": {"high": 0.03, "low": 0.01, "avg": 0.020},
    "Rh": {"high": 0.10, "low": 0.05, "avg": 0.075},
    "Ru": {"high": 0.25, "low": 0.15, "avg": 0.200},
    "Au": {"avg": 0.10},
    "Ir": {"avg": 0.10},
    "Ag": {"avg": 0.025},
    "Ni": {"avg": 0.20},
    "Co": {"avg": 0.20},
    "Cu": {"high": 0.25, "low": 0.15, "avg": 0.20},
    "W": {"high": 0.25, "low": 0.15, "avg": 0.20},
    "Mo": {"high": 0.30, "low": 0.20, "avg": 0.25},
    "Fe": {"avg": 0.40},
    "Al": {"avg": 0.70},
}

REFINING_CHARGES: dict[str, float] = {  # $/TrOz recovered
    "Pt": 14.5, "Pd": 12.5, "Rh": 16.0, "Au": 11.0,
    "Ru": 20.0, "Ir": 25.0, "Ag": 11.5,
}

DEFAULT_THERMOX_PER_LB = 0.1375
DEFAULT_INCOMING_PER_FT3 = 110.0
SUPPORT_RECOVERY_COSTS: dict[str, dict[str, float]] = {
    "Al2O3": {"thermox_per_lb": 0.1375, "incoming_fee_per_ft3": 115.5},
    "Carbon": {"thermox_per_lb": 0.1375, "incoming_fee_per_ft3": 104.5},
    "Carbonate": {"thermox_per_lb": 0.1375, "incoming_fee_per_ft3": 115.5},
    "Clay": {"thermox_per_lb": 0.1375, "incoming_fee_per_ft3": 115.5},
    "SiO2": {"thermox_per_lb": 0.1375, "incoming_fee_per_ft3": 115.5},
    "Sponge of metal (no support)": {"thermox_per_lb": 0.1375, "incoming_fee_per_ft3": 86.5},
    "TiO2": {"thermox_per_lb": 0.1375, "incoming_fee_per_ft3": 115.5},
    "ZrO2": {"thermox_per_lb": 0.1375, "incoming_fee_per_ft3": 115.5},
}

# --- Equipment cost scaling ---
DEFAULT_SCALING_EXPONENT = 0.6  # Six-tenths rule
