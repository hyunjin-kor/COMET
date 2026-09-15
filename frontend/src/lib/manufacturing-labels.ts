const labels: Record<string, [string, string]> = {
  finished_batch_mass_kg: ['Finished dry mass (kg)', '최종 건조 수득량 (kg)'],
  electricity_usd_kwh: ['Electricity tariff (USD/kWh)', '전력 단가 (USD/kWh)'],
  labor_usd_h: ['Labor rate (USD/person-hour)', '인건비 (USD/인·시간)'],
  selling_margin_fraction: ['Selling margin (fraction)', '판매 마진 (비율)'],
  name: ['Name', '이름'], equipment: ['Equipment', '장비'], atmosphere: ['Atmosphere', '분위기'],
  pressure_bar_abs: ['Absolute pressure (bar)', '절대압 (bar)'], stirring_rpm: ['Stirring (rpm)', '교반 (rpm)'],
  ph: ['pH', 'pH'], solvent: ['Solvent', '용매'], solvent_volume_ml: ['Solvent volume (mL)', '용매량 (mL)'],
  repetitions: ['Repetitions', '반복 횟수'], start_temperature_c: ['Starting temperature (°C)', '시작 온도 (°C)'],
  duration_h: ['Duration (h)', '시간 (h)'], additional_time_h: ['Extra time (h)', '추가 시간 (h)'],
  average_power_kw: ['Mean input power (kW)', '평균 입력 전력 (kW)'], additional_power_kw: ['Extra-time power (kW)', '추가 시간 전력 (kW)'],
  measured_energy_kwh: ['Measured electricity (kWh)', '실측 전력량 (kWh)'], energy_basis: ['Energy basis', '전력량 산정 방식'],
  equipment_usd_h: ['Equipment rate (USD/h)', '장비 단가 (USD/h)'], attended_labor_h: ['Attended labor (person-hours)', '직접 작업시간 (인·시간)'],
  other_cost_usd: ['Additional charges (USD)', '추가 비용 (USD)'],
  quantity: ['Purchased quantity', '구매량'], unit: ['Purchase unit', '구매 단위'], quantity_basis: ['Quantity basis', '구매량 기준'],
  price_usd_per_unit: ['Price per purchase unit (USD)', '구매 단위당 가격 (USD)'], materials_basis: ['Materials calculation basis', '재료비 계산 방식'],
  target_c: ['Target temperature (°C)', '목표 온도 (°C)'], ramp_c_per_min: ['Ramp rate (°C/min)', '승·강온 속도 (°C/min)'],
  hold_h: ['Hold time (h)', '유지 시간 (h)'], ramp_power_kw: ['Ramp power (kW)', '승·강온 전력 (kW)'], hold_power_kw: ['Hold power (kW)', '유지 전력 (kW)'],
  flow_l_per_min: ['Gas flow (L/min)', '가스 유량 (L/min)'], duration_basis: ['Gas duration basis', '가스 시간 기준'],
  price_usd_per_m3: ['Gas price (USD/m³)', '가스 단가 (USD/m³)'], volume_basis: ['Volume reference conditions', '체적 기준 조건'],
  mode: ['Calculation basis', '계산 방식'], product_basis: ['Product boundary', '제조 대상'],
  source_record_id: ['Literature record', '문헌 기록'], source_note: ['Protocol source note', '제조법 출처 메모'], notes: ['Procedure notes', '조작 메모'],
};

export function manufacturingInputLabel(field: string, lang: string) {
  return labels[field]?.[lang === 'ko' ? 1 : 0] ?? field;
}
