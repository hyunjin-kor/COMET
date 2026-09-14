import { useLang } from '../lib/i18n';
import type { ManufacturingOperation, ManufacturingProtocol, TemperatureSegment } from '../lib/manufacturing';

function NumberField({ label, value, onChange, min = 0 }: {
  label: string; value?: number | null; onChange: (value: number | null) => void; min?: number;
}) {
  return <label className="flex flex-col justify-end text-xs text-slate-600"><span className="min-h-8 flex items-end">{label}</span><input type="number" step="any" min={min}
    className="input-base mt-1 w-full" value={value ?? ''}
    onChange={(e) => onChange(e.target.value === '' ? null : Number(e.target.value))} /></label>;
}

function TextField({ label, value, onChange }: { label: string; value?: string; onChange: (value: string) => void }) {
  return <label className="block text-xs text-slate-600">{label}<input className="input-base mt-1 w-full" value={value ?? ''}
    onChange={(e) => onChange(e.target.value)} /></label>;
}

export default function ManufacturingProtocolFields({ value, onChange }: {
  value?: ManufacturingProtocol; onChange: (value: ManufacturingProtocol | undefined) => void;
}) {
  const { lang } = useLang();
  const l = (en: string, ko: string) => lang === 'ko' ? ko : en;
  const patch = (change: Partial<ManufacturingProtocol>) => value && onChange({ ...value, ...change });
  const update = (index: number, change: Partial<ManufacturingOperation>) => value && patch({
    operations: value.operations.map((op, i) => i === index ? { ...op, ...change } : op),
  });
  const move = (index: number, offset: number) => {
    if (!value) return;
    const operations = [...value.operations];
    [operations[index], operations[index + offset]] = [operations[index + offset]!, operations[index]!];
    patch({ operations });
  };
  return <section className="rounded-2xl border border-teal-200 bg-white p-4" aria-label={l('Detailed manufacturing protocol', '상세 제조 조건')}>
    <label className="flex items-center gap-3 text-base font-semibold text-slate-900"><input type="checkbox" checked={!!value}
      onChange={(e) => onChange(e.target.checked ? { mode: 'record_only', operations: [{ name: l('Mixing', '혼합'), repetitions: 1 }] } : undefined)} />
      {l('Detailed manufacturing protocol', '상세 제조 조건')}</label>
    <p className="mt-2 text-sm leading-6 text-slate-600">{l('Record each operation in order, including repeated impregnation, drying, calcination and reduction. Blank values mean unknown, not zero.',
      '함침·건조·소성·환원을 반복하는 경우도 각 단계를 순서대로 기록합니다. 빈칸은 0이 아닌 미확인 값입니다.')}</p>
    {value && <div className="mt-4 space-y-4">
      <label className="block text-sm font-medium">{l('Calculation basis', '계산 방식')}<select className="input-base mt-2 w-full" value={value.mode}
        onChange={(e) => patch({ mode: e.target.value as ManufacturingProtocol['mode'] })}>
        <option value="record_only">{l('Record conditions; use Step Method cost', '조건 기록 · Step Method 원가 사용')}</option>
        <option value="batch_cost">{l('Calculate cost from batch operating inputs', '배치 운전 조건으로 원가 계산')}</option>
      </select></label>
      <p className="text-xs leading-6 text-slate-600">{value.mode === 'batch_cost'
        ? l('Batch costs replace empirical processing rates. Enter actual finished dry mass and operating costs at this batch scale. Order totals repeat identical batch costs linearly; this is not an industrial scale-up prediction.',
            '배치 비용이 경험식 가공비를 대체합니다. 해당 배치의 최종 건조 수득량과 운전 비용을 입력하세요. 주문량 합계는 같은 배치 비용의 선형 반복이며 산업 규모 확대 예측은 아닙니다.')
        : l('Conditions are saved, but do not change the Step Method headline price. Switch to batch costing once operating inputs are available.',
            '조건은 저장되지만 Step Method 가격을 바꾸지는 않습니다. 운전 자료가 준비되면 배치 원가 계산으로 전환하세요.')}</p>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <NumberField label={l('Finished dry batch mass (kg)', '최종 건조 수득량 (kg/배치)')} value={value.finished_batch_mass_kg} onChange={(v) => patch({ finished_batch_mass_kg: v })} />
        <NumberField label={l('Electricity tariff (USD/kWh)', '전력 단가 (USD/kWh)')} value={value.electricity_usd_kwh} onChange={(v) => patch({ electricity_usd_kwh: v })} />
        <NumberField label={l('Labor rate (USD/person-hour)', '인건비 (USD/인·시간)')} value={value.labor_usd_h} onChange={(v) => patch({ labor_usd_h: v })} />
        <NumberField label={l('Selling margin (%)', '판매 마진 (%)')} value={(value.selling_margin_fraction ?? 0) * 100} onChange={(v) => patch({ selling_margin_fraction: (v ?? 0) / 100 })} />
      </div>
      <TextField label={l('Protocol and operating-cost sources / assumptions', '제조 조건·운전비 출처 또는 가정')} value={value.source_note} onChange={(v) => patch({ source_note: v })} />
      {value.operations.map((op, index) => {
        const profile = op.temperature_profile ?? [];
        const segment = (i: number, change: Partial<TemperatureSegment>) => update(index, { temperature_profile: profile.map((s, j) => i === j ? { ...s, ...change } : s) });
        const measured = op.energy_basis === 'measured' || op.measured_energy_kwh != null;
        return <details key={index} open className="rounded-xl border border-slate-200 p-4">
          <summary className="cursor-pointer font-semibold text-slate-900">{index + 1}. {op.name || l('Unnamed operation', '단계 이름 미입력')}</summary>
          <div className="mt-3 flex flex-wrap justify-end gap-2">
            <button type="button" className="cp-button-secondary px-3 py-2 text-xs" disabled={index === 0} onClick={() => move(index, -1)}>{l('Move up', '위로')}</button>
            <button type="button" className="cp-button-secondary px-3 py-2 text-xs" disabled={index === value.operations.length - 1} onClick={() => move(index, 1)}>{l('Move down', '아래로')}</button>
            <button type="button" className="cp-button-secondary px-3 py-2 text-xs" onClick={() => patch({ operations: [...value.operations.slice(0, index + 1), structuredClone(op), ...value.operations.slice(index + 1)] })}>{l('Duplicate', '복제')}</button>
            <button type="button" className="cp-button-secondary px-3 py-2 text-xs" disabled={value.operations.length === 1} onClick={() => patch({ operations: value.operations.filter((_, i) => i !== index) })}>{l('Remove operation', '단계 삭제')}</button>
          </div>
          <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <TextField label={l('Operation name', '단계 이름')} value={op.name} onChange={(v) => update(index, { name: v })} />
            <TextField label={l('Equipment / model', '장비·모델')} value={op.equipment} onChange={(v) => update(index, { equipment: v })} />
            <NumberField label={l('Repetitions', '반복 횟수')} value={op.repetitions ?? 1} min={1} onChange={(v) => update(index, { repetitions: v ?? 1 })} />
            <TextField label={l('Atmosphere / gas composition', '분위기·가스 조성')} value={op.atmosphere} onChange={(v) => update(index, { atmosphere: v })} />
            <NumberField label={l('Absolute pressure (bar)', '절대압 (bar)')} value={op.pressure_bar_abs} onChange={(v) => update(index, { pressure_bar_abs: v })} />
            <NumberField label={l('Stirring / rotation (rpm)', '교반·회전 속도 (rpm)')} value={op.stirring_rpm} onChange={(v) => update(index, { stirring_rpm: v })} />
            <NumberField label={l('pH', 'pH')} value={op.ph} onChange={(v) => update(index, { ph: v })} />
            <TextField label={l('Solvent', '용매')} value={op.solvent} onChange={(v) => update(index, { solvent: v })} />
            <NumberField label={l('Solvent volume (mL/batch)', '용매량 (mL/배치)')} value={op.solvent_volume_ml} onChange={(v) => update(index, { solvent_volume_ml: v })} />
          </div>
          <p className="mt-2 text-xs text-slate-500">{l('Solvent quantities here are protocol records. Enter purchased solvent in Composition consumables for costing.', '이 용매량은 제조 조건 기록입니다. 구매 비용은 조성 화면의 소모품 항목에 입력하세요.')}</p>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <NumberField label={l(profile.length ? 'Starting temperature (°C)' : 'Operating temperature (°C)', profile.length ? '시작 온도 (°C)' : '운전 온도 (°C)')} min={-273.14} value={op.start_temperature_c} onChange={(v) => update(index, { start_temperature_c: v })} />
            {!profile.length && <NumberField label={l('Operating duration (h)', '운전 시간 (h)')} value={op.duration_h} onChange={(v) => update(index, { duration_h: v })} />}
            <NumberField label={l('Additional setup, cleaning, cooling (h)', '추가 준비·세척·냉각 시간 (h)')} value={op.additional_time_h} onChange={(v) => update(index, { additional_time_h: v })} />
          </div>
          <div className="mt-3 flex items-center justify-between gap-3"><span className="text-sm font-medium">{l('Temperature program', '온도 프로그램')}</span>
            <button type="button" className="cp-button-secondary px-3 py-2 text-xs" onClick={() => update(index, { duration_h: null, average_power_kw: null, temperature_profile: [...profile, { target_c: null }] })}>{l('Add ramp / hold', '승온·유지 구간 추가')}</button></div>
          {profile.map((s, i) => <div key={i} className="mt-3 grid gap-3 rounded-lg bg-slate-50 p-3 sm:grid-cols-3 lg:grid-cols-6">
            <NumberField label={`${i + 1}. ${l('Target (°C)', '목표 온도 (°C)')}`} min={-273.14} value={s.target_c} onChange={(v) => segment(i, { target_c: v })} />
            <NumberField label={l('Ramp (°C/min)', '승·강온 속도 (°C/min)')} value={s.ramp_c_per_min} onChange={(v) => segment(i, { ramp_c_per_min: v })} />
            <NumberField label={l('Hold (h)', '유지 시간 (h)')} value={s.hold_h} onChange={(v) => segment(i, { hold_h: v })} />
            {!measured && <><NumberField label={l('Mean ramp power (kW)', '승·강온 평균 입력전력 (kW)')} value={s.ramp_power_kw} onChange={(v) => segment(i, { ramp_power_kw: v })} />
              <NumberField label={l('Mean hold power (kW)', '유지 평균 입력전력 (kW)')} value={s.hold_power_kw} onChange={(v) => segment(i, { hold_power_kw: v })} /></>}
            <button type="button" className="self-end cp-button-secondary px-3 py-2 text-xs" onClick={() => update(index, { temperature_profile: profile.filter((_, j) => i !== j) })}>{l('Remove segment', '구간 삭제')}</button>
          </div>)}
          <details className="mt-4 border-t border-slate-200 pt-3" open={value.mode === 'batch_cost' || undefined}>
            <summary className="cursor-pointer text-sm font-medium">{l('Energy and operating costs per repetition', '1회 운전의 에너지·운전비')}</summary>
            <p className="mt-2 text-xs leading-6 text-slate-600">{l('Use measured input energy or mean input power, including furnace losses. Temperature alone cannot determine consumption. Measured kWh must be updated when conditions change. Enter 0 only when a cost is explicitly excluded.',
              '장비의 열손실이 포함된 측정 소비전력량 또는 평균 입력전력을 사용합니다. 온도만으로 소비량을 정하지 않습니다. 조건을 바꾸면 측정 kWh도 갱신하세요. 비용을 제외할 때만 0을 명시하세요.')}</p>
            <label className="mt-3 flex gap-2 text-xs"><input type="checkbox" checked={measured} onChange={(e) => update(index, e.target.checked
              ? { energy_basis: 'measured', measured_energy_kwh: null, average_power_kw: null, additional_power_kw: null, temperature_profile: profile.map((s) => ({ ...s, ramp_power_kw: null, hold_power_kw: null })) }
              : { energy_basis: 'power', measured_energy_kwh: null })} />{l('Use measured total electricity for this operation', '이 단계의 측정 전력량 사용')}</label>
            <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {measured ? <NumberField label={l('Measured electricity (kWh)', '측정 전력량 (kWh)')} value={op.measured_energy_kwh} onChange={(v) => update(index, { measured_energy_kwh: v })} /> : <>
                {!profile.length && <NumberField label={l('Mean input power (kW)', '평균 입력전력 (kW)')} value={op.average_power_kw} onChange={(v) => update(index, { average_power_kw: v })} />}
                <NumberField label={l('Additional-time mean power (kW)', '추가 시간 평균 입력전력 (kW)')} value={op.additional_power_kw} onChange={(v) => update(index, { additional_power_kw: v })} /></>}
              <NumberField label={l('Equipment only (USD/h)', '장비 비용만 (USD/h)')} value={op.equipment_usd_h} onChange={(v) => update(index, { equipment_usd_h: v })} />
              <NumberField label={l('Attended labor (person-hours)', '직접 작업시간 (인·시간)')} value={op.attended_labor_h} onChange={(v) => update(index, { attended_labor_h: v })} />
              <NumberField label={l('Other costs (USD)', '기타 비용 (USD)')} value={op.other_cost_usd} onChange={(v) => update(index, { other_cost_usd: v })} />
            </div>
            <p className="mt-2 text-xs text-slate-500">{l('Equipment rates exclude the electricity, gas and labor entered separately. Overnight hold time is not attended labor.', '장비 시간당 비용에서 별도 입력한 전기·가스·인건비는 제외하세요. 야간 유지 시간 전체를 직접 작업시간으로 계산하지 않습니다.')}</p>
          </details>
          <div className="mt-4 flex items-center justify-between"><span className="text-sm font-medium">{l('Reduction / purge gases', '환원·퍼지 가스')}</span>
            <button type="button" className="cp-button-secondary px-3 py-2 text-xs" onClick={() => update(index, { gases: [...(op.gases ?? []), { name: '', volume_basis: '' }] })}>{l('Add gas', '가스 추가')}</button></div>
          {!op.gases?.length && <p className="mt-2 text-xs text-slate-500">{l('No gas purchase is included. Add each purchased gas or premixed gas.', '가스 구매 비용 미반영. 사용하는 가스 또는 혼합가스를 각각 추가하세요.')}</p>}
          {op.gases?.map((gas, i) => {
            const change = (fields: Partial<typeof gas>) => update(index, { gases: op.gases!.map((g, j) => i === j ? { ...g, ...fields } : g) });
            return <div key={i} className="mt-3 grid gap-3 bg-slate-50 p-3 sm:grid-cols-2 lg:grid-cols-3">
              <TextField label={l('Gas / mixture name', '가스·혼합가스 이름')} value={gas.name} onChange={(v) => change({ name: v })} />
              <NumberField label={l('Flow (L/min)', '유량 (L/min)')} value={gas.flow_l_per_min} onChange={(v) => change({ flow_l_per_min: v })} />
              <NumberField label={l('Gas use time (h)', '가스 사용 시간 (h)')} value={gas.duration_h} onChange={(v) => change({ duration_h: v })} />
              <NumberField label={l('Gas price (USD/m³)', '가스 단가 (USD/m³)')} value={gas.price_usd_per_m3} onChange={(v) => change({ price_usd_per_m3: v })} />
              <TextField label={l('Shared flow / price reference T and P', '유량·단가의 공통 기준 온도·압력')} value={gas.volume_basis} onChange={(v) => change({ volume_basis: v })} />
              <button type="button" className="self-end cp-button-secondary px-3 py-2 text-xs" onClick={() => update(index, { gases: op.gases!.filter((_, j) => i !== j) })}>{l('Remove gas', '가스 삭제')}</button>
            </div>;
          })}
          <label className="mt-4 block text-xs text-slate-600">{l('Procedure, addition order, feed rate, recovery / yield and source notes', '조작·투입 순서·투입 속도·회수·수율·출처 메모')}<textarea className="input-base mt-1 w-full" rows={3}
            value={op.notes ?? ''} onChange={(e) => update(index, { notes: e.target.value })} /></label>
        </details>;
      })}
      <button type="button" className="cp-button-secondary px-3 py-2 text-xs" onClick={() => patch({ operations: [...value.operations, { name: '', repetitions: 1 }] })}>{l('Add operation', '제조 단계 추가')}</button>
    </div>}
  </section>;
}
