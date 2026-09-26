import { useEffect, useState } from 'react';
import { fetchSavedEstimate, fetchSavedEstimates, request, type SavedEstimateDetail, type SavedEstimateSummary } from '../lib/api';
import { ScientificText } from '../components/shared/ScientificText';
import { useAuth } from '../lib/auth';
import { invalidateBrowserAccount, notifyOtherTabs } from '../lib/hosted-session';
import { useLang } from '../lib/i18n';

export default function Account() {
  const { session, signOut, refresh } = useAuth();
  const { t, lang } = useLang();
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const [saved, setSaved] = useState<SavedEstimateSummary[]>([]);
  const [selected, setSelected] = useState<SavedEstimateDetail | null>(null);
  const accountId = session.account?.id;
  useEffect(() => {
    if (!accountId) return;
    let active = true;
    void fetchSavedEstimates({ limit: 200 }).then((items) => { if (active) setSaved(items); })
      .catch(() => { if (active) setMessage('Could not load saved work. Try again.'); });
    return () => { active = false; };
  }, [accountId]);
  const account = session.account;
  if (!account) return <p className="p-6">{t('Desktop use does not require an account.')}</p>;
  const subscription = account.subscription;
  const status = { active: t('Subscription active'), pending: t('Subscription pending'), expired: t('Subscription expired'), revoked: t('Subscription ended') }[subscription.status];
  return <section className="mx-auto w-full max-w-3xl rounded-2xl border border-slate-200 bg-white p-6 sm:p-9">
    <div className="flex flex-wrap items-start justify-between gap-4"><div><p className="text-sm text-slate-500">{t('Account')}</p><h1 className="mt-2 text-2xl font-semibold">{account.username}</h1></div><button type="button" onClick={() => void signOut().catch(() => setMessage('Sign-out failed. Try again before leaving this device.'))} className="rounded-lg border border-slate-300 px-4 py-2 text-sm">{t('Sign out')}</button></div>
    <div className="my-8 rounded-xl bg-slate-50 p-5">
      <p className="font-medium">{status}</p>
      <p className="mt-2 text-sm text-slate-600">{subscription.ends_at ? `${t('Access period ends')}: ${new Date(subscription.ends_at * 1000).toLocaleString(lang === 'ko' ? 'ko-KR' : 'en-US')}` : t('Your administrator will confirm the access period.')}</p>
      {!subscription.can_start_work && <p className="mt-3 text-sm leading-6 text-slate-600">{t('New calculations are paused. Your saved work remains available to view and export.')}</p>}
      <button type="button" onClick={() => void refresh().catch(() => setMessage('Cannot connect to COMET. Try again.'))} className="mt-4 text-sm text-blue-700">{t('Refresh subscription status')}</button>
    </div>
    <p className="mb-7 text-sm leading-6 text-slate-500">{t('Your saved formulations are private to this account. Save your work before signing out; unsaved inputs are cleared.')}</p>
    <h2 className="font-semibold">{t('Saved work')}</h2>
    <p className="mt-2 text-xs text-slate-500">{t('Most recent 200 items. Download includes the saved inputs and result.')}</p>
    <ul className="mt-4 divide-y divide-slate-100">
      {saved.map((item) => <li key={item.id} className="flex flex-wrap items-center justify-between gap-3 py-3"><div><p className="text-sm font-medium"><ScientificText text={item.name} /></p><p className="mt-1 text-xs text-slate-500">{item.created_at}</p></div><div className="flex gap-4"><button className="text-sm text-blue-700" onClick={() => void fetchSavedEstimate(item.id).then(setSelected).catch(() => setMessage('Could not load saved work. Try again.'))}>{t('View saved result')}</button><button className="text-sm text-blue-700" onClick={async () => {
        try {
          const detail = await fetchSavedEstimate(item.id);
          const url = URL.createObjectURL(new Blob([JSON.stringify(detail, null, 2)], { type: 'application/json' }));
          const link = document.createElement('a'); link.href = url; link.download = `comet-estimate-${item.id}.json`; link.click();
          setTimeout(() => URL.revokeObjectURL(url), 1000);
        } catch { setMessage('Could not load saved work. Try again.'); }
      }}>{t('Download saved calculation')}</button></div></li>)}
    </ul>
    {saved.length === 0 && <p className="mt-4 text-sm text-slate-500">{t('No saved calculations yet.')}</p>}
    {selected && <div className="mt-5 rounded-xl border border-slate-200 p-5">
      <h3 className="font-medium"><ScientificText text={selected.name} /></h3>
      <p className="mt-3 text-xl font-semibold">{selected.result.electrode_model
        ? `$${selected.result.electrode_model.cost_per_m2_usd.toLocaleString(lang === 'ko' ? 'ko-KR' : 'en-US', { maximumFractionDigits: 2 })} /m²`
        : `$${selected.result.summary.estimated_price_per_kg.toLocaleString(lang === 'ko' ? 'ko-KR' : 'en-US', { maximumFractionDigits: 2 })} /kg`}</p>
      <p className="mt-2 text-sm text-slate-500">{t('Historical saved result; no new calculation was performed.')}</p>
      <p className="mt-3 text-sm"><ScientificText text={selected.result.route_summary?.name ?? selected.result.electrode_model?.application_family ?? selected.support_name} /></p>
    </div>}
    <form className="mt-8 border-t border-slate-200 pt-7" onSubmit={async (event) => {
      event.preventDefault(); const form = event.currentTarget; const values = new FormData(form);
      if (values.get('new_password') !== values.get('confirm_password')) { setMessage('New passwords do not match.'); return; }
      setBusy(true); setMessage('');
      try {
        await request('/auth/password', { method: 'POST', body: JSON.stringify({ current_password: values.get('current_password'), new_password: values.get('new_password') }) });
        form.reset(); invalidateBrowserAccount(); notifyOtherTabs();
      } catch { setMessage('Password change failed. Check your current password or try again later.'); }
      finally { setBusy(false); }
    }}>
      <h2 className="font-semibold">{t('Change password')}</h2><p className="mt-2 text-sm text-slate-500">{t('Use 15–128 characters. Changing your password signs out all sessions.')}</p>
      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <label className="text-sm sm:col-span-2">{t('Current password')}<input name="current_password" type="password" autoComplete="current-password" required maxLength={128} className="mt-2 block w-full rounded-lg border border-slate-300 px-3 py-2" /></label>
        <label className="text-sm">{t('New password')}<input name="new_password" type="password" autoComplete="new-password" required minLength={15} maxLength={128} className="mt-2 block w-full rounded-lg border border-slate-300 px-3 py-2" /></label>
        <label className="text-sm">{t('Confirm new password')}<input name="confirm_password" type="password" autoComplete="new-password" required minLength={15} maxLength={128} className="mt-2 block w-full rounded-lg border border-slate-300 px-3 py-2" /></label>
      </div>
      {message && <p role="alert" className="mt-4 text-sm text-red-700">{t(message)}</p>}
      <button disabled={busy} className="mt-5 rounded-lg bg-[#191f28] px-4 py-2.5 text-sm text-white disabled:opacity-50">{t('Change password')}</button>
    </form>
  </section>;
}
