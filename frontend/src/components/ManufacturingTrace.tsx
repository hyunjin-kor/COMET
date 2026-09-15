import { useLang } from '../lib/i18n';
import type { ManufacturingReport } from '../lib/manufacturing';
import { manufacturingInputLabel } from '../lib/manufacturing-labels';

export default function ManufacturingTrace({ report }: { report: ManufacturingReport }) {
  const { lang } = useLang();
  const l = (en: string, ko: string) => lang === 'ko' ? ko : en;
  const trace = report.trace;
  if (!trace) return null;
  const show = (value: unknown) => value == null ? l('Unknown', '미확인') : typeof value === 'number' ? value.toLocaleString(undefined, { maximumFractionDigits: 6 }) : String(value);
  const pathLabel = (path: string) => {
    const parts = path.split('.');
    const op = parts[0] === 'operations' ? report.protocol.operations[Number(parts[1])] : null;
    const batch = parts[0] === 'intermediate_batches' ? report.protocol.intermediate_batches?.[Number(parts[1])] : null;
    const segment = parts[2] === 'temperature_profile' ? `${l('segment', '구간')} ${Number(parts[3]) + 1}` : '';
    const gas = parts[2] === 'gases' ? op?.gases?.[Number(parts[3])]?.name : '';
    const purchase = parts[2] === 'purchases' ? op?.purchases?.[Number(parts[3])]?.name : '';
    return [batch?.name || op?.name, segment || gas || purchase, manufacturingInputLabel(parts.at(-1)!, lang)].filter(Boolean).join(' / ');
  };
  const statuses: Record<string, string> = {
    matches_record: l('Matches source snapshot', '출처 저장 당시 값과 일치'), modified: l('Changed from source snapshot', '출처 저장 당시 값과 다름'),
    missing: l('Unknown', '미확인'), default: l('Default value without source', '기본값 · 출처 없음'), unattributed: l('No input source', '항목 출처 없음'),
  };
  const kinds: Record<string, string> = { literature: l('Literature', '문헌'), measured: l('Measured', '실측'), supplier: l('Supplier', '공급사'), assumption: l('Assumption', '가정') };
  const categories: Record<string, string> = {
    materials: l('Materials', '재료비'), electricity: l('Electricity', '전기'), equipment: l('Equipment', '장비'), labor: l('Labor', '인건비'), gas: l('Gas', '가스'),
    other: l('Entered additional charges', '별도 입력한 추가 비용'), ga: l('General and administrative overhead', '일반관리비'), sard: l('Sales, administration, research and distribution', '판매·관리·연구·유통비'), margin: l('Profit margin', '판매 이익'),
  };
  const inputs = trace.inputs.filter((row) => row.effect !== 'inactive' && (row.evidence || row.unit && (row.effect === 'cost_input' || row.value != null)));
  const exportTrace = () => {
    const url = URL.createObjectURL(new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' }));
    const link = document.createElement('a'); link.href = url; link.download = 'COMET-manufacturing-trace.json'; link.click(); URL.revokeObjectURL(url);
  };
  return <details className="mt-4 rounded-lg border border-teal-200 p-3">
    <summary className="cursor-pointer text-sm font-semibold text-teal-900">{l('Input sources and calculation trace', '입력 근거와 계산 경로')}</summary>
    <p className="mt-2 text-xs leading-6 text-slate-600">{l('Evidence types describe the declared source. A matching value is not an independent validation. Conditions marked “record only” do not predict power, yield or activity.', '근거 유형은 등록된 출처를 나타냅니다. 값의 일치가 독립 검증을 의미하지 않습니다. 기록 전용 조건으로 전력·수율·활성을 예측하지 않습니다.')}</p>
    <p className="mt-2 text-xs font-medium">{l('Source coverage for active numeric cost inputs', '계산에 연결된 수치 입력의 근거 현황')}</p>
    <div className="mt-2 flex flex-wrap gap-3 text-xs">{Object.entries(trace.coverage).map(([key, count]) => <span key={key} className={key === 'modified' ? 'font-semibold text-amber-800' : ''}>{statuses[key] ?? key}: {count}</span>)}</div>
    <button type="button" className="mt-3 cp-button-secondary px-3 py-2 text-xs" onClick={exportTrace}>{l('Download inputs, sources and calculations', '입력·출처·계산 내보내기')}</button>
    {trace.overhead_inputs && <p className="mt-3 text-xs">{l('Entered overhead fractions', '입력한 간접비 비율')}: G&A {show(trace.overhead_inputs.ga_fraction * 100)}{'% · SARD '}{show(trace.overhead_inputs.sard_fraction * 100)}% · {l('Selling margin', '판매 마진')} {show(trace.overhead_inputs.selling_margin_fraction * 100)}%</p>}
    {trace.recovery_adjustment?.enabled && <p className="mt-3 text-xs leading-6">{l('Optional post-use recovery credit', '선택한 사용 후 회수 가치 공제')}: {show(trace.recovery_adjustment.applied_credit_usd_kg)}{' USD/kg · '}{l('Net cost after credit', '공제 후 순비용')}: {show(trace.recovery_adjustment.net_cost_usd_kg)}{' USD/kg. '}{l('This credit does not reduce manufacturing expenditure.', '이 공제는 제조 지출을 줄이는 항목이 아닙니다.')}</p>}
    {!!trace.cost_ledger.length && <div className="mt-4 overflow-x-auto"><p className="text-sm font-medium">{l('Selling-price contributions before recovery credit (USD/kg)', '회수 가치 공제 전 판매 단가 기여분 (USD/kg)')}</p><table className="mt-2 w-full text-left text-xs"><thead><tr><th className="p-2">{l('Category', '항목')}</th><th className="p-2 text-right">{'USD/kg'}</th></tr></thead><tbody>{trace.cost_ledger.map((row) => <tr className="border-t border-slate-100" key={row.category}><td className="p-2">{categories[row.category] ?? row.category}</td><td className="p-2 text-right tabular-nums">{show(row.value)}</td></tr>)}<tr className="border-t font-semibold"><td className="p-2">{l('Total', '합계')}</td><td className="p-2 text-right">{show(trace.cost_ledger.reduce((total, row) => total + row.value, 0))}</td></tr></tbody></table></div>}
    <div className="mt-4 space-y-2">{inputs.map((row) => <details key={row.path} className="rounded border border-slate-200 p-2 text-xs"><summary className="cursor-pointer leading-6"><span className="font-medium">{pathLabel(row.path)}</span>: {show(row.value)} {row.unit} · <span className={row.source_status === 'modified' ? 'text-amber-800 font-semibold' : 'text-slate-500'}>{statuses[row.source_status] ?? row.source_status}</span>{row.effect === 'record_only' && <span className="ml-2 text-slate-500">{l('Record only', '기록 전용')}</span>}</summary>
      {row.evidence ? <div className="mt-2 space-y-1 leading-6"><p>{kinds[row.evidence.kind]} · {row.evidence.citation}</p><p>{row.evidence.locator}</p>{row.evidence.url && /^https?:\/\//i.test(row.evidence.url) && <a className="break-all text-teal-700 underline" href={row.evidence.url} target="_blank" rel="noreferrer">{row.evidence.url}</a>}<p>{[row.evidence.doi, row.evidence.accessed_on].filter(Boolean).join(' · ')}</p><p>{l('Source snapshot', '출처 저장 당시 값')}: {show(row.evidence.recorded_value)} {row.unit}</p><p>{row.evidence.note}</p></div> : <p className="mt-2 text-slate-500">{l('No source has been attached to this input.', '이 입력 항목에 연결된 출처가 없습니다.')}</p>}
      <p className="mt-2 break-all text-slate-400">{row.path}</p>
    </details>)}</div>
    <details className="mt-4 text-xs"><summary className="cursor-pointer font-medium">{l('Equations and dependencies', '계산식과 연결 입력')}</summary>{trace.calculations.map((row) => <div key={row.id} className="mt-3 border-t border-slate-100 pt-2"><p className="font-medium">{pathLabel(row.id)}: {show(row.value)} {row.unit}</p><p className="mt-1 break-words font-mono">{row.formula}</p><p className="mt-1 leading-6 text-slate-500">{row.input_paths.map(pathLabel).join(' · ')}</p></div>)}</details>
    <p className="mt-4 break-all text-xs text-slate-400">{l('Protocol fingerprint', '제조 조건 식별 해시')}: {trace.protocol_sha256}</p>
  </details>;
}
