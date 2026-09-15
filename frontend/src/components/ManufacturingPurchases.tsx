import { useLang } from '../lib/i18n';
import type { BatchPurchase } from '../lib/manufacturing';
import ManufacturingInputSources from './ManufacturingInputSources';

export default function ManufacturingPurchases({ purchases = [], onChange }: { purchases?: BatchPurchase[]; onChange: (value: BatchPurchase[]) => void }) {
  const { lang } = useLang();
  const l = (en: string, ko: string) => lang === 'ko' ? ko : en;
  return <div className="mt-4">
    <div className="flex items-center justify-between gap-3"><span className="text-sm font-medium">{l('Purchased materials per repetition', '1회 운전의 재료 구매량')}</span><button type="button" className="cp-button-secondary px-3 py-2 text-xs" onClick={() => onChange([...purchases, { name: '', unit: 'kg' }])}>{l('Add purchase', '구매 항목 추가')}</button></div>
    {purchases.map((purchase, i) => {
      const change = (fields: Partial<BatchPurchase>) => onChange(purchases.map((p, j) => i === j ? { ...p, ...fields } : p));
      const priceUnit = `USD/${purchase.unit}`;
      return <div key={i} className="mt-3 grid gap-3 rounded-lg bg-slate-50 p-3 sm:grid-cols-2 lg:grid-cols-3">
        <label className="text-xs text-slate-600">{l('Precursor / support / solvent / consumable', '전구체·담체·용매·소모품 이름')}<input className="input-base mt-1 w-full" value={purchase.name} onChange={(e) => change({ name: e.target.value })} /></label>
        <label className="text-xs text-slate-600">{l('Quantity basis', '구매량 기준')}<select className="input-base mt-1 w-full" value={purchase.quantity_basis ?? 'entered'} onChange={(e) => change({ quantity_basis: e.target.value as BatchPurchase['quantity_basis'], quantity: null, ...(e.target.value === 'solvent_volume' ? { unit: 'mL' as const } : {}) })}>
          <option value="entered">{l('Enter purchased quantity', '구매량 직접 입력')}</option><option value="solvent_volume">{l('Use this operation’s solvent volume', '이 단계의 용매량 사용')}</option>
        </select></label>
        <label className="text-xs text-slate-600">{l('Quantity and price unit', '구매량·단가의 공통 단위')}<select className="input-base mt-1 w-full" disabled={purchase.quantity_basis === 'solvent_volume'} value={purchase.unit} onChange={(e) => change({ unit: e.target.value as BatchPurchase['unit'] })}>{['kg', 'g', 'L', 'mL', 'item'].map((unit) => <option key={unit} value={unit}>{unit}</option>)}</select></label>
        {purchase.quantity_basis !== 'solvent_volume' && <label className="text-xs text-slate-600">{l('Net purchased quantity', '순 구매량')} ({purchase.unit})<input type="number" min={0} step="any" className="input-base mt-1 w-full" value={purchase.quantity ?? ''} onChange={(e) => change({ quantity: e.target.value === '' ? null : Number(e.target.value) })} /></label>}
        <label className="text-xs text-slate-600">{l('Price', '단가')} ({priceUnit})<input type="number" min={0} step="any" className="input-base mt-1 w-full" value={purchase.price_usd_per_unit ?? ''} onChange={(e) => change({ price_usd_per_unit: e.target.value === '' ? null : Number(e.target.value) })} /></label>
        <label className="text-xs text-slate-600">{l('Purchase boundary and exclusions', '구매 범위·제외 항목')}<input className="input-base mt-1 w-full" value={purchase.notes ?? ''} onChange={(e) => change({ notes: e.target.value })} /></label>
        <button type="button" className="self-end cp-button-secondary px-3 py-2 text-xs" onClick={() => onChange(purchases.filter((_, j) => i !== j))}>{l('Remove purchase', '구매 항목 삭제')}</button>
        <div className="col-span-full"><ManufacturingInputSources record={purchase} fields={['name', 'quantity', 'unit', 'quantity_basis', 'price_usd_per_unit', 'notes']} onChange={(input_evidence) => change({ input_evidence })} /></div>
      </div>;
    })}
  </div>;
}
