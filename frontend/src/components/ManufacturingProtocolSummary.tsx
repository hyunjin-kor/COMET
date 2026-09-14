import { useLang } from '../lib/i18n';
import type { ManufacturingReport } from '../lib/manufacturing';

export default function ManufacturingProtocolSummary({ report, compact = false }: { report: ManufacturingReport; compact?: boolean }) {
  const { lang } = useLang();
  const l = (en: string, ko: string) => lang === 'ko' ? ko : en;
  const v = (n: number | null | undefined, unit = '') => n == null ? l('Unknown', '미확인') : `${n.toLocaleString(undefined, { maximumFractionDigits: 4 })}${unit ? ` ${unit}` : ''}`;
  return <section className="mt-4 rounded-xl border border-teal-200 bg-white p-4">
    <h3 className="font-semibold text-slate-900">{l('Detailed manufacturing protocol', '상세 제조 조건')}</h3>
    <p className="mt-2 text-sm leading-6 text-slate-600">{report.mode === 'batch_cost'
      ? l('Costs use the entered batch operations. Temperature and time do not establish catalyst performance. Equipment rates exclude separately charged utilities and labor.',
          '입력한 배치 운전 조건으로 비용을 계산했습니다. 온도·시간으로 촉매 성능을 예측하지 않습니다. 장비 단가는 별도 계산한 유틸리티·인건비를 제외합니다.')
      : l('Conditions are recorded. The headline estimate still uses the Step Method.', '조건을 기록했습니다. 대표 추정값에는 Step Method를 사용합니다.')}</p>
    <div className="mt-3 grid gap-3 sm:grid-cols-3 text-sm">
      <div>{l('Dry batch output', '건조 수득량')}<div className="mt-1 font-semibold">{v(report.protocol.finished_batch_mass_kg, 'kg')}</div></div>
      <div>{l('Serial operation time / batch', '배치당 공정시간 합계')}<div className="mt-1 font-semibold">{v(report.serial_operation_hours, 'h')}</div></div>
      <div>{l('Processing cost', '가공비')}<div className="mt-1 font-semibold">{v(report.processing_cost_usd_kg, 'USD/kg')}</div></div>
      {report.manufacturing_cost_usd_kg != null && <div>{l('Materials + processing', '재료비 + 가공비')}<div className="mt-1 font-semibold">{v(report.manufacturing_cost_usd_kg, 'USD/kg')}</div></div>}
    </div>
    <p className="mt-3 text-xs leading-6 text-slate-500">{l('Time is the sum of operation-hours, not a schedule with parallel work. Order totals use linear batch equivalents. Blank gas lists exclude gas purchases; solvent records need separate purchased-consumable entries. Environmental results cover materials only in batch-cost mode.',
      '시간은 공정시간의 합계로, 병렬 작업을 고려한 일정이 아닙니다. 주문량 합계는 배치의 선형 반복입니다. 가스 목록이 비어 있으면 가스비를 제외하며, 용매는 구매 소모품을 별도 입력해야 합니다. 배치 원가 모드의 환경 결과는 재료만 반영합니다.')}</p>
    {!report.complete && <p className="mt-2 text-sm text-amber-800">{l('Operating-cost inputs are incomplete; no detailed cost is reported.', '운전비 입력이 불완전하여 상세 원가를 표시하지 않습니다.')}</p>}
    {!compact && <>
      <p className="mt-3 whitespace-pre-wrap text-xs text-slate-600">{report.protocol.source_note}</p>
      <div className="mt-2 text-xs text-slate-600">{l('Electricity / labor / selling margin', '전력 단가 / 인건비 / 판매 마진')}: {v(report.protocol.electricity_usd_kwh, 'USD/kWh')} / {v(report.protocol.labor_usd_h, 'USD/h')} / {v((report.protocol.selling_margin_fraction ?? 0) * 100, '%')}</div>
      {report.protocol.operations.map((op, i) => {
        const result = report.operations[i];
        const conditions = [op.equipment, op.atmosphere,
          op.pressure_bar_abs != null && v(op.pressure_bar_abs, 'bar abs'),
          op.stirring_rpm != null && v(op.stirring_rpm, 'rpm'),
          op.ph != null && `pH ${op.ph}`, op.solvent,
          op.solvent_volume_ml != null && v(op.solvent_volume_ml, 'mL')].filter(Boolean).join(' · ');
        return <details key={i} open className="mt-3 border-t border-slate-200 pt-3">
          <summary className="cursor-pointer text-sm font-semibold">{i + 1}. {op.name} ×{op.repetitions ?? 1}</summary>
          <p className="mt-2 text-xs leading-6 text-slate-600">{conditions}</p>
          <div className="mt-2 flex flex-wrap gap-4 text-sm"><span>{l('Time', '시간')}: {v(result?.duration_h, 'h')}</span><span>{l('Electricity', '전력량')}: {v(result?.electricity_kwh, 'kWh')}</span><span>{l('Cost per batch', '배치당 비용')}: {v(result?.cost_usd, 'USD')}</span></div>
          <p className="mt-2 text-xs">{l('Starting / operating temperature', '시작·운전 온도')}: {v(op.start_temperature_c, '°C')} / {l('Extra setup, cleaning, cooling', '추가 준비·세척·냉각')}: {v(op.additional_time_h, 'h')}</p>
          {!!op.temperature_profile?.length && <div className="mt-2 overflow-x-auto"><table className="w-full text-left text-xs"><thead><tr className="border-b border-slate-200">
            {[l('Target (°C)', '목표 (°C)'), l('Ramp (°C/min)', '승·강온 (°C/min)'), l('Hold (h)', '유지 (h)'), l('Ramp power (kW)', '승·강온 전력 (kW)'), l('Hold power (kW)', '유지 전력 (kW)')].map((label) => <th className="p-2" key={label}>{label}</th>)}</tr></thead>
            <tbody>{op.temperature_profile.map((s, j) => <tr key={j}>{[s.target_c, s.ramp_c_per_min, s.hold_h, s.ramp_power_kw, s.hold_power_kw].map((n, k) => <td className="p-2" key={k}>{v(n)}</td>)}</tr>)}</tbody></table></div>}
          {op.gases?.map((gas, j) => <p key={j} className="mt-2 text-xs">{gas.name}: {v(gas.flow_l_per_min, 'L/min')} × {v(gas.duration_h, 'h')}; {v(gas.price_usd_per_m3, 'USD/m³')} ({gas.volume_basis})</p>)}
          {result?.costs_usd && <div className="mt-2 flex flex-wrap gap-3 text-xs">{[
            ['electricity', l('Electricity', '전기')], ['equipment', l('Equipment', '장비')], ['labor', l('Labor', '인건비')], ['gas', l('Gas', '가스')], ['other', l('Other', '기타')],
          ].map(([key, label]) => <span key={key}>{label}: {v(result.costs_usd![key!], 'USD')}</span>)}</div>}
          <p className="mt-2 whitespace-pre-wrap text-xs leading-6 text-slate-600">{op.notes}</p>
        </details>;
      })}
      {!!report.missing_inputs.length && <details className="mt-3 text-xs text-amber-800"><summary className="cursor-pointer">{l('Missing inputs for batch costing', '배치 원가 계산에 필요한 미입력 항목')}</summary><ul className="mt-2 list-disc pl-5">{report.missing_inputs.map((s) => <li key={s}>{s}</li>)}</ul></details>}
    </>}
  </section>;
}
