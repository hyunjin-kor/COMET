import { useLang } from '../lib/i18n';
import ManufacturingInputSources from './ManufacturingInputSources';
import type { IntermediateBatch, ManufacturingProtocol } from '../lib/manufacturing';

export default function ManufacturingIntermediateBatches({ value, onChange }: {
  value: ManufacturingProtocol; onChange: (value: ManufacturingProtocol) => void;
}) {
  const { lang } = useLang();
  const l = (en: string, ko: string) => lang === 'ko' ? ko : en;
  const batches = value.intermediate_batches ?? [];
  const update = (id: string, change: Partial<IntermediateBatch>) => onChange({ ...value,
    intermediate_batches: batches.map((batch) => batch.id === id ? { ...batch, ...change } : batch) });
  return <details className="rounded-xl border border-slate-200 p-4" open={batches.length > 0 || undefined}>
    <summary className="cursor-pointer text-sm font-semibold">{l('Intermediate batches and aliquots', '중간 생성물 배치와 분취량')}</summary>
    <p className="mt-3 text-xs leading-6 text-slate-600">{l(
      'When only part of an intermediate batch is used, assign its preparation operations and choose the receiving batch. Costs use mass transferred / mass recovered on the same material basis. Successive transfers multiply these fractions. Leave unreported recovery blank.',
      '중간 생성물 일부를 사용했다면 제조 단계와 투입 대상 배치를 연결하세요. 같은 물질·질량 기준의 사용량/회수량으로 비용을 배분합니다. 분취가 이어지면 각 비율을 곱합니다. 회수량이 보고되지 않았으면 비워 두세요.')}</p>
    <p className="mt-2 text-xs leading-6 text-slate-600">{l(
      'Mass allocation leaves the unused share with recoverable inventory; whole-batch charging assigns all costs to the receiving batch. Each intermediate has one destination; splits across multiple branches and co-products are not modeled. Do not enter internal transfers as purchases.',
      '질량 배분은 남은 비용을 회수 가능한 재고에 남기고, 전체 배치 방식은 전액을 투입 대상 배치에 부담시킵니다. 각 중간 배치는 한 곳에만 연결하며 여러 경로로 나누는 분기와 공동생산물은 계산하지 않습니다. 내부 이동량을 구매로 다시 넣지 마세요.')}</p>
    {batches.map((batch, index) => {
      const assigned = value.operations.some((op) => op.intermediate_batch_id === batch.id) || batches.some((item) => item.destination_batch_id === batch.id);
      return <div key={batch.id} className="mt-3 rounded-lg bg-slate-50 p-3">
        <label className="block text-xs">{`${index + 1}. ${l('Intermediate name', '중간 생성물 이름')}`}<input className="input-base mt-1 w-full" value={batch.name} onChange={(e) => update(batch.id, { name: e.target.value })} /></label>
        <label className="mt-3 block text-xs">{l('Cost allocation', '비용 배분 기준')}<select className="input-base mt-1 w-full" value={batch.allocation_basis ?? 'mass_used'} onChange={(e) => update(batch.id, { allocation_basis: e.target.value as IntermediateBatch['allocation_basis'] })}><option value="mass_used">{l('Used mass fraction; remainder held in inventory', '사용 질량 비율 · 잔여분은 재고')}</option><option value="whole_batch">{l('Charge whole batch; no inventory credit', '전체 배치 비용 · 재고 공제 없음')}</option></select></label>
        <label className="mt-3 block text-xs">{l('Receiving batch', '투입 대상 배치')}<select className="input-base mt-1 w-full" value={batch.destination_batch_id ?? ''} onChange={(e) => update(batch.id, { destination_batch_id: e.target.value })}><option value="">{l('Final catalyst batch', '최종 촉매 배치')}</option>{batches.filter((item) => item.id !== batch.id).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
        <div className="mt-3 grid gap-3 sm:grid-cols-2">{(['produced_mass_kg', 'used_mass_kg'] as const).map((key) => <label key={key} className="text-xs">{key === 'produced_mass_kg' ? l('Mass recovered from this batch (kg)', '이 배치에서 회수한 질량 (kg)') : l('Mass used in receiving batch (kg)', '투입 대상 배치에 사용한 질량 (kg)')}<input type="number" min="0" step="any" className="input-base mt-1 w-full" value={batch[key] ?? ''} onChange={(e) => update(batch.id, { [key]: e.target.value === '' ? null : Number(e.target.value) })} /></label>)}</div>
        <label className="mt-3 block text-xs">{l('Recovery, transfer and inventory assumptions', '회수·분취·잔여 재고에 대한 근거 또는 가정')}<textarea className="input-base mt-1 w-full" rows={2} value={batch.notes ?? ''} onChange={(e) => update(batch.id, { notes: e.target.value })} /></label>
        <ManufacturingInputSources record={batch} fields={['allocation_basis', 'destination_batch_id', 'produced_mass_kg', 'used_mass_kg', 'notes']} onChange={(input_evidence) => update(batch.id, { input_evidence })} />
        <button type="button" disabled={assigned} className="mt-3 cp-button-secondary px-3 py-2 text-xs disabled:opacity-40" onClick={() => onChange({ ...value, intermediate_batches: batches.filter((item) => item.id !== batch.id) })}>{l('Remove intermediate batch', '중간 배치 삭제')}</button>
        <p className="mt-2 text-xs text-slate-500">{assigned ? l('Reassign connected operations and transfers before removing this entry.', '삭제하려면 연결된 제조 단계와 분취 대상 배치를 먼저 바꾸세요.') : l('Select this batch in the preparation operations below.', '아래 제조 단계에서 이 배치를 선택하세요.')}</p>
      </div>;
    })}
    <button type="button" className="mt-3 cp-button-secondary px-3 py-2 text-xs" onClick={() => onChange({ ...value, intermediate_batches: [...batches, { id: crypto.randomUUID(), name: l('Intermediate', '중간 생성물') }] })}>{l('Add intermediate batch', '중간 배치 추가')}</button>
  </details>;
}
