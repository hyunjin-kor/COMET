import { useState } from 'react';
import { useLang } from '../lib/i18n';
import type { InputEvidence, SourcedInputs } from '../lib/manufacturing';

import { manufacturingInputLabel } from '../lib/manufacturing-labels';

export default function ManufacturingInputSources({ record, fields, onChange }: {
  record: SourcedInputs; fields: string[]; onChange: (sources: Record<string, InputEvidence>) => void;
}) {
  const { lang } = useLang();
  const l = (en: string, ko: string) => lang === 'ko' ? ko : en;
  const [selected, setSelected] = useState(fields[0] ?? '');
  const [draft, setDraft] = useState<InputEvidence | null>(null);
  const sources = record.input_evidence ?? {};
  const current = Object.fromEntries(Object.entries(record))[selected] as InputEvidence['recorded_value'] | undefined;
  const shown = draft ?? sources[selected] ?? { kind: 'assumption', citation: '', recorded_value: current ?? null };
  const patch = (change: Partial<InputEvidence>) => setDraft({ ...shown, ...change });
  const modified = Object.entries(sources).filter(([field, source]) => (Object.fromEntries(Object.entries(record))[field] ?? null) !== source.recorded_value).length;
  const text = (key: 'citation' | 'locator' | 'url' | 'doi' | 'accessed_on' | 'note', label: string) => <label className="block text-xs text-slate-600">{label}<input className="input-base mt-1 w-full" value={shown[key] ?? ''} onChange={(e) => patch({ [key]: e.target.value })} /></label>;
  return <details className="mt-3 rounded-lg border border-slate-200 bg-slate-50 p-3">
    <summary className="cursor-pointer text-sm font-medium text-teal-900">{l('Sources for individual inputs', '입력 항목별 출처')} · {Object.keys(sources).length}{modified > 0 && <span className="ml-2 text-amber-800">{l(`${modified} modified`, `${modified}개 원래 값과 다름`)}</span>}</summary>
    <p className="mt-2 text-xs leading-6 text-slate-600">{l('Attach a source or an explicit assumption to each value. Saving captures its current value; later edits retain that snapshot. A citation does not certify the input.', '각 값에 문헌·실측·공급사 자료 또는 명시적인 가정을 연결합니다. 저장 당시 값은 이후 조건을 수정해도 남습니다. 출처 입력 자체가 검증을 의미하지는 않습니다.')}</p>
    <div className="mt-3 grid gap-3 sm:grid-cols-2">
      <label className="text-xs text-slate-600">{l('Input', '입력 항목')}<select className="input-base mt-1 w-full" value={selected} onChange={(e) => { setSelected(e.target.value); setDraft(null); }}>{fields.map((field) => <option key={field} value={field}>{manufacturingInputLabel(field, lang)}{sources[field] ? ' ✓' : ''}</option>)}</select></label>
      <label className="text-xs text-slate-600">{l('Evidence type', '근거 유형')}<select className="input-base mt-1 w-full" value={shown.kind} onChange={(e) => patch({ kind: e.target.value as InputEvidence['kind'] })}>
        <option value="literature">{l('Literature', '문헌')}</option><option value="measured">{l('Measured', '실측')}</option><option value="supplier">{l('Supplier data', '공급사 자료')}</option><option value="assumption">{l('Assumption', '가정')}</option>
      </select></label>
      {text('citation', l('Citation or record description (required)', '인용 또는 기록 설명 (필수)'))}
      {text('locator', l('Section, page, table or record identifier', '절·페이지·표 또는 기록 식별자'))}
      {text('url', l('Public source URL (optional)', '공개 출처 URL (선택)'))}
      {text('doi', l('DOI (optional)', 'DOI (선택)'))}
      {text('accessed_on', l('Access or measurement date', '열람일 또는 측정일'))}
      {text('note', l('Scope, conversion or assumption', '범위·단위 환산·가정'))}
    </div>
    <p className="mt-3 text-xs">{l('Current value', '현재 값')}: {String(current ?? l('Unknown', '미확인'))}{sources[selected] && <> · {l('Recorded value', '출처 저장 당시 값')}: {String(sources[selected]!.recorded_value ?? l('Unknown', '미확인'))}</>}</p>
    <div className="mt-3 flex flex-wrap gap-2">
      <button type="button" className="cp-button-secondary px-3 py-2 text-xs" disabled={!shown.citation.trim()} onClick={() => { onChange({ ...sources, [selected]: { ...shown, citation: shown.citation.trim(), recorded_value: current ?? null } }); setDraft(null); }}>{l('Save source with current value', '현재 값과 함께 출처 저장')}</button>
      {sources[selected] && <button type="button" className="cp-button-secondary px-3 py-2 text-xs" onClick={() => { const next = { ...sources }; delete next[selected]; onChange(next); setDraft(null); }}>{l('Remove this source', '이 출처 삭제')}</button>}
    </div>
  </details>;
}
