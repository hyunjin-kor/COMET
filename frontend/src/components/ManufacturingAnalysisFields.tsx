import { useEffect, useState } from 'react';
import { fetchManufacturingVariables, runManufacturingSensitivity, type CostInput, type ManufacturingRange, type ManufacturingVariable, type ManufacturingSensitivity } from '../lib/api';
import { useLang } from '../lib/i18n';
import { manufacturingPathLabel } from '../lib/manufacturing-labels';
import { ScientificText } from './shared/ScientificText';

export default function ManufacturingAnalysisFields({ input, ranges, onChange }: {
  input: CostInput; ranges: ManufacturingRange[]; onChange: (value: ManufacturingRange[]) => void;
}) {
  const { lang } = useLang();
  const l = (en: string, ko: string) => lang === 'ko' ? ko : en;
  const [variables, setVariables] = useState<ManufacturingVariable[]>([]);
  const [selected, setSelected] = useState('');
  const [pending, setPending] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<ManufacturingSensitivity | null>(null);
  const serializedInput = JSON.stringify(input);
  useEffect(() => {
    let active = true;
    fetchManufacturingVariables(JSON.parse(serializedInput)).then((data) => { if (active) setVariables(data.variables); })
      .catch((e: unknown) => { if (active) setError(e instanceof Error ? e.message : String(e)); });
    return () => { active = false; };
  }, [serializedInput]);
  const protocol = input.manufacturing_protocol!;
  const label = (path: string) => manufacturingPathLabel(protocol, path, lang);
  const available = variables.filter((item) => !ranges.some((range) => range.path === item.path));
  const chosen = available.find((item) => item.path === selected) ?? available[0];
  const update = (next: ManufacturingRange[]) => { onChange(next); setResult(null); };
  async function load() {
    setPending(true); setError('');
    try { setVariables((await fetchManufacturingVariables(input)).variables); }
    catch (e) { setError(e instanceof Error ? e.message : String(e)); }
    finally { setPending(false); }
  }
  async function sensitivity() {
    setPending(true); setError(''); setResult(null);
    try { setResult(await runManufacturingSensitivity(input, ranges)); }
    catch (e) { setError(e instanceof Error ? e.message : String(e)); }
    finally { setPending(false); }
  }
  const display = (value: number | null) => value == null ? l('Not feasible', '계산 불가') : value.toLocaleString(lang, { maximumSignificantDigits: 6 });
  return <section className="mt-5 rounded-2xl border border-teal-200 bg-teal-50/40 p-4">
    <h3 className="font-semibold">{l('Manufacturing input ranges', '제조 조건별 분석 범위')}</h3>
    <p className="mt-2 text-sm leading-6 text-slate-600">{l('Select inputs that enter the batch cost and specify absolute lower and upper values. No uncertainty range is inferred from a paper. Monte Carlo samples selected inputs independently; all remaining conditions stay fixed.', '배치 원가에 연결된 입력을 선택하고 하한·상한을 실제 단위로 입력하세요. 문헌에서 불확실성 범위를 자동 추정하지 않습니다. Monte Carlo는 선택한 입력을 서로 독립적으로 변화시키고 나머지 조건을 고정합니다.')}</p>
    <p className="mt-2 text-xs leading-6 text-slate-600">{l('Changing temperature changes the entered heating schedule; it does not predict mean power or yield. Time-linked gas use follows the selected time. Infeasible combinations are reported and excluded from statistics.', '온도 변화는 입력한 승온 시간에 반영되며 평균전력·수율을 예측하지 않습니다. 시간에 연결한 가스 사용량은 함께 변합니다. 불가능한 조합은 보고하고 통계에서 제외합니다.')}</p>
    <button type="button" className="cp-button-secondary mt-3" disabled={pending} onClick={load}>{l('Load cost-linked inputs', '원가에 연결된 변수 불러오기')}</button>
    {!!variables.length && <div className="mt-3 flex flex-wrap items-end gap-2">
      <label className="min-w-0 flex-1 text-sm">{l('Input to vary', '변화시킬 입력')}<select className="input-base mt-1 w-full" value={chosen?.path ?? ''} onChange={(e) => setSelected(e.target.value)}>{available.map((item) => <option key={item.path} value={item.path}>{label(item.path)} · {item.value} {item.unit}</option>)}</select></label>
      <button type="button" className="cp-button-secondary" disabled={!chosen || ranges.length >= 40} onClick={() => chosen && update([...ranges, { path: chosen.path, low: chosen.value, high: chosen.value }])}>{l('Add input', '변수 추가')}</button>
    </div>}
    {ranges.map((range, index) => {
      const variable = variables.find((item) => item.path === range.path);
      return <div key={range.path} className="mt-3 rounded-xl border border-slate-200 bg-white p-3">
        <p className="text-sm font-medium"><ScientificText text={label(range.path)} /></p>
        <p className="mt-1 text-xs text-slate-500">{l('Baseline', '기준값')}: {variable?.value} {variable?.unit}</p>
        <div className="mt-2 grid grid-cols-2 gap-3">{(['low', 'high'] as const).map((key) => <label key={key} className="text-xs">{key === 'low' ? l('Lower value', '하한') : l('Upper value', '상한')}<input className="input-base mt-1 w-full" type="number" step={variable?.unit === 'count' ? 1 : 'any'} value={Number.isFinite(range[key]) ? range[key] : ''} onChange={(e) => update(ranges.map((row, n) => n === index ? { ...row, [key]: e.target.value === '' ? NaN : Number(e.target.value) } : row))} /></label>)}</div>
        <label className="mt-2 block text-xs">{l('Reason or evidence for these bounds', '범위의 근거 또는 가정')}<input className="input-base mt-1 w-full" value={range.rationale ?? ''} onChange={(e) => update(ranges.map((row, n) => n === index ? { ...row, rationale: e.target.value } : row))} /></label>
        {variable?.evidence && <p className="mt-2 text-xs leading-6 text-slate-600">{l('Baseline source', '기준 입력 출처')}: {variable.evidence.citation} · {variable.evidence.locator} · {l('Original value', '원문 값')} {String(variable.evidence.recorded_value)} {variable.unit}</p>}
        <button type="button" className="mt-2 text-xs text-teal-800 underline" onClick={() => update(ranges.filter((_, n) => n !== index))}>{l('Remove input', '변수 삭제')}</button>
      </div>;
    })}
    {!!ranges.length && <button type="button" className="cp-button-secondary mt-3" disabled={pending || ranges.some((r) => !Number.isFinite(r.low) || !Number.isFinite(r.high) || r.low > r.high)} onClick={sensitivity}>{l('Compare endpoints one input at a time', '변수별 하한·상한 원가 비교')}</button>}
    {error && <p role="alert" className="mt-3 text-sm text-red-700">{error}</p>}
    {result && <div className="mt-4 overflow-x-auto">
      <p className="text-sm font-medium">{l('Baseline', '기준 원가')}: {display(result.baseline_usd_kg)}{' USD/kg'}</p>
      <p className="mt-2 text-xs leading-6">{l('Each row changes one input while holding the rest fixed. Endpoint prices are scenarios, not confidence limits. The selected ranges also apply to the Monte Carlo run below.', '각 행에서 변수 하나만 바꾸고 나머지는 고정합니다. 끝점 원가는 시나리오이며 신뢰구간이 아닙니다. 선택한 범위는 아래 Monte Carlo 실행에도 적용됩니다.')}</p>
      <table className="mt-2 w-full text-left text-xs"><thead><tr>{[l('Input', '변수'), l('Lower input → USD/kg', '입력 하한 → USD/kg'), l('Upper input → USD/kg', '입력 상한 → USD/kg')].map((s) => <th key={s} className="p-2">{s}</th>)}</tr></thead><tbody>{result.rows.map((row) => <tr key={row.path} className="border-t border-slate-200"><td className="p-2"><ScientificText text={label(row.path)} /></td><td className="p-2">{display(row.low)}{' → '}{display(row.low_usd_kg)}{row.low_error && <p>{row.low_error}</p>}</td><td className="p-2">{display(row.high)}{' → '}{display(row.high_usd_kg)}{row.high_error && <p>{row.high_error}</p>}</td></tr>)}</tbody></table>
      <button type="button" className="cp-button-secondary mt-3" onClick={() => {
        const url = URL.createObjectURL(new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' }));
        const a = document.createElement('a'); a.href = url; a.download = 'COMET-manufacturing-sensitivity.json'; a.click(); URL.revokeObjectURL(url);
      }}>{l('Download sensitivity inputs and results', '민감도 입력·결과 내보내기')}</button>
    </div>}
  </section>;
}
