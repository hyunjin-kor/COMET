import { useEffect, useState } from 'react';
import { fetchManufacturingLiterature } from '../lib/api';
import { useLang } from '../lib/i18n';
import { applyOperatingReference, type ManufacturingOperatingReference, type ManufacturingProtocol } from '../lib/manufacturing';

export default function ManufacturingOperatingReferences({ value, onChange }: {
  value: ManufacturingProtocol; onChange: (value: ManufacturingProtocol) => void;
}) {
  const { lang } = useLang();
  const l = (en: string, ko: string) => lang === 'ko' ? ko : en;
  const [records, setRecords] = useState<ManufacturingOperatingReference[]>([]);
  const [selectedId, setSelectedId] = useState('');
  const [error, setError] = useState(false);
  useEffect(() => {
    let active = true;
    fetchManufacturingLiterature().then((data) => { if (active) setRecords(data.operating_references); })
      .catch(() => { if (active) setError(true); });
    return () => { active = false; };
  }, []);
  const selected = records.find((r) => r.id === selectedId) ?? records[0];
  return <details className="rounded-xl border border-slate-200 p-3">
    <summary className="cursor-pointer text-sm font-medium text-teal-800">{l('Operating data sources', '운영비 자료 출처')}</summary>
    <p className="mt-3 text-sm leading-6 text-slate-600">{l('Compare your operating inputs with dated public references. Tariffs can be applied as explicit scenarios; equipment ratings and historical wages remain reference information.',
      '운전 입력값을 날짜가 명시된 공개 자료와 대조합니다. 전력 단가는 시나리오 값으로 적용할 수 있으며, 장비 정격과 과거 임금은 참고 자료로 표시합니다.')}</p>
    {error && <p role="alert" className="mt-3 text-sm text-red-700">{l('Operating references could not be loaded.', '운영비 자료를 불러오지 못했습니다.')}</p>}
    {selected && <div className="mt-3 space-y-3">
      <label className="block text-sm">{l('Public reference', '공개 근거')}<select className="input-base mt-1 w-full" value={selected.id} onChange={(e) => setSelectedId(e.target.value)}>
        {records.map((r) => <option key={r.id} value={r.id}>{lang === 'ko' ? r.label_ko : r.label}</option>)}
      </select></label>
      <div className="text-lg font-semibold text-slate-900">{selected.value} <span className="text-sm font-normal">{selected.unit}</span></div>
      <p className="text-xs text-slate-500">{selected.geography} · {selected.period}</p>
      <p className="text-sm leading-6 text-slate-700">{lang === 'ko' ? selected.scope_ko : selected.scope}</p>
      <a className="block text-xs text-teal-800 underline" href={selected.evidence.url} target="_blank" rel="noreferrer">{selected.evidence.citation}</a>
      <p className="text-xs leading-5 text-slate-500">{selected.evidence.locator}</p>
      {selected.import_field && <button type="button" className="cp-button-secondary" onClick={() => onChange(applyOperatingReference(value, selected))}>
        {l('Apply tariff and preserve source', '전력 단가와 출처 적용')}</button>}
    </div>}
  </details>;
}
