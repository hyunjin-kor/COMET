import { useEffect, useState } from 'react';
import { fetchManufacturingLiterature } from '../lib/api';
import { useLang } from '../lib/i18n';
import { adaptLiteratureProtocol, type LiteratureProtocol, type ManufacturingEvidence, type ManufacturingProtocol } from '../lib/manufacturing';
import { ScientificText } from './shared/ScientificText';

export default function ManufacturingLiterature({ evidence, onSelect }: {
  evidence?: ManufacturingEvidence;
  onSelect?: (protocol: ManufacturingProtocol) => void;
}) {
  const { lang } = useLang();
  const l = (en: string, ko: string) => lang === 'ko' ? ko : en;
  const [library, setLibrary] = useState<LiteratureProtocol[]>([]);
  const [error, setError] = useState(false);
  const [selectedId, setSelectedId] = useState('');
  const [query, setQuery] = useState('');
  useEffect(() => {
    if (evidence) return;
    let active = true;
    fetchManufacturingLiterature().then((data) => { if (active) setLibrary(data.profiles); })
      .catch(() => { if (active) setError(true); });
    return () => { active = false; };
  }, [evidence]);
  const profiles = evidence?.profiles ?? library;
  const filtered = profiles.filter((p) => `${p.sample} ${p.title} ${p.doi}`.toLowerCase().includes(query.toLowerCase()));
  const selected = filtered.find((p) => p.id === selectedId) ?? filtered[0];
  return <section className="rounded-2xl border border-slate-200 bg-white p-4" aria-label={l('Literature preparation records', '문헌 제조법')}>
    <div className="flex flex-wrap items-center justify-between gap-2">
      <h3 className="font-semibold text-slate-900">{l('Literature preparation records', '문헌 제조법')}</h3>
      <span className="text-xs text-slate-500">{l('Reviewed', '검토일')} {evidence?.review_date ?? selected?.review_date ?? ''}</span>
    </div>
    {evidence && <div className="mt-3 rounded-lg bg-amber-50 p-3 text-sm leading-6 text-amber-950">
      <strong>{evidence.status === 'source_mismatch'
        ? l('Catalog sample differs from its source', '카탈로그 시료와 출처의 불일치')
        : evidence.profile_ids.length ? l('Source-specific variants available', '문헌 시료별 제조법 확인 가능')
          : l('Exact preparation not verified', '정확한 제조법 확인 못 함')}</strong>
      {evidence.notes.map((note) => <p className="mt-2" key={note}><ScientificText text={note} /></p>)}
      <p className="mt-2 text-xs">{l('DOIs verified in Crossref', 'Crossref DOI 확인')}: {evidence.crossref_verified_count}/{evidence.doi_count} · {l('Bibliographic verification does not validate a recipe.', '문헌정보 확인이 제조법 검증을 의미하지는 않습니다.')}</p>
    </div>}
    <p className="mt-3 text-sm leading-6 text-slate-600">{l('Each record describes a named specimen. Check composition, precursor chemistry and powder/electrode boundary before adapting it. Unreported conditions remain blank.',
      '각 기록은 원문의 특정 시료를 설명합니다. 조성·전구체·분말 또는 전극 범위를 확인한 뒤 적용하세요. 원문에 없는 조건은 빈칸으로 남깁니다.')}</p>
    {error && <p role="alert" className="mt-3 text-sm text-red-700">{l('Preparation records could not be loaded.', '문헌 제조법을 불러오지 못했습니다.')}</p>}
    {profiles.length > 0 && <>
      {profiles.length > 5 && <label className="mt-3 block text-sm">{l('Find a specimen or DOI', '시료·DOI 검색')}<input className="input-base mt-1 w-full" value={query} onChange={(e) => setQuery(e.target.value)} /></label>}
      <label className="mt-3 block text-sm">{l('Published specimen', '문헌 시료')}<select className="input-base mt-1 w-full" value={selected?.id ?? ''} onChange={(e) => setSelectedId(e.target.value)}>
        {!filtered.length && <option value="">{l('No matching record', '검색 결과 없음')}</option>}
        {filtered.map((p) => <option key={p.id} value={p.id}>{p.sample}</option>)}
      </select></label>
    </>}
    {selected && <div className="mt-4 space-y-3">
      <a className="block text-sm font-medium text-teal-800 underline" href={selected.url} target="_blank" rel="noreferrer"><ScientificText text={selected.title} /></a>
      <p className="text-xs leading-5 text-slate-500">{selected.doi} · {selected.locator}</p>
      <span className="cp-chip">{selected.boundary === 'electrode' ? l('Electrode preparation', '전극 제조') : l('Catalyst powder preparation', '촉매 분말 제조')}</span>
      <ol className="space-y-2">
        {selected.operations.map((op, i) => <li key={i} className="rounded-lg border border-slate-100 p-3 text-sm leading-6">
          <div className="font-medium text-slate-900">{i + 1}. <ScientificText text={op.name} /></div>
          <div className="mt-1 flex flex-wrap gap-x-3 text-teal-800">
            {(op.temperature_profile ?? []).map((s, j) => <span key={j}>{s.target_c ?? '?'} °C · {s.hold_h ?? '?'} h · {s.ramp_c_per_min ?? '?'} °C/min</span>)}
            {op.duration_h != null && <span>{Number(op.duration_h.toFixed(4))} h</span>}
            {op.atmosphere && <span>{op.atmosphere}</span>}
          </div>
          <p className="text-slate-600"><ScientificText text={op.notes ?? ''} /></p>
          {!!op.purchases?.length && <ul className="mt-2 space-y-1 border-t border-slate-100 pt-2 text-xs text-slate-600">
            {op.purchases.map((purchase, j) => <li key={j}><ScientificText text={purchase.name} />: {purchase.quantity ?? l('Not reported', '미확인')} {purchase.unit}</li>)}
          </ul>}
        </li>)}
      </ol>
      {selected.limitations.map((note) => <p key={note} className="text-sm leading-6 text-amber-900"><ScientificText text={note} /></p>)}
      {onSelect && <button type="button" className="cp-button-secondary" onClick={() => onSelect(adaptLiteratureProtocol(selected))}>{l('Use as editable preparation record', '편집 가능한 제조 기록으로 가져오기')}</button>}
      <p className="text-xs leading-5 text-slate-500">{l('Imports use record-only mode. They do not change cost estimates or supply measured equipment power, batch output or factory-scale costs.',
        '기록 모드로 가져옵니다. 원가를 자동 변경하거나 장비 실측 전력·배치 수득량·공장 규모 비용을 채워 넣지 않습니다.')}</p>
    </div>}
  </section>;
}
