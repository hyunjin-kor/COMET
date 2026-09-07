/* eslint-disable react-refresh/only-export-components */
import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react';
import { request } from './api';
import { useLang } from './i18n';
import { hostedRequestState, invalidateBrowserAccount, notifyOtherTabs, SESSION_CHANGE_KEY, SESSION_INVALID_EVENT, setBrowserAccount } from './hosted-session';

export interface AccountSession {
  mode: 'desktop' | 'hosted';
  authenticated: boolean;
  account: {
    id: string;
    username: string;
    organization_id: string;
    subscription: { status: 'pending' | 'active' | 'expired' | 'revoked'; can_start_work: boolean; starts_at: number | null; ends_at: number | null; seat_limit: number };
  } | null;
}

const AuthContext = createContext<{
  session: AccountSession;
  refresh: () => Promise<void>;
  signOut: () => Promise<void>;
} | null>(null);

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error('Account provider is required');
  return value;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const { t, lang, toggle } = useLang();
  const [session, setSession] = useState<AccountSession | null>(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const accept = useCallback((next: AccountSession) => {
    setBrowserAccount(next.mode, next.account?.id ?? null);
    setSession(next);
  }, []);
  const refresh = useCallback(async () => {
    const generation = hostedRequestState().generation;
    const next = await request<AccountSession>('/auth/session');
    if (generation !== hostedRequestState().generation) return;
    accept(next);
    setError('');
  }, [accept]);

  useEffect(() => {
    let alive = true;
    void request<AccountSession>('/auth/session').then((next) => { if (alive) accept(next); })
      .catch(() => { if (alive) setError('Cannot connect to COMET. Try again.'); });
    const invalid = () => setSession({ mode: 'hosted', authenticated: false, account: null });
    const otherTab = (event: StorageEvent) => {
      if (event.key === SESSION_CHANGE_KEY) invalidateBrowserAccount();
    };
    window.addEventListener(SESSION_INVALID_EVENT, invalid);
    window.addEventListener('storage', otherTab);
    return () => { alive = false; window.removeEventListener(SESSION_INVALID_EVENT, invalid); window.removeEventListener('storage', otherTab); };
  }, [accept]);

  useEffect(() => {
    if (session?.mode !== 'hosted' || !session.authenticated) return;
    const check = () => {
      if (document.visibilityState === 'visible') void refresh().catch(() => invalidateBrowserAccount());
    };
    window.addEventListener('focus', check);
    document.addEventListener('visibilitychange', check);
    return () => { window.removeEventListener('focus', check); document.removeEventListener('visibilitychange', check); };
  }, [session?.mode, session?.authenticated, refresh]);

  async function signOut() {
    await request('/auth/logout', { method: 'POST' });
    invalidateBrowserAccount(); notifyOtherTabs();
  }

  if (!session || (session.mode === 'hosted' && !session.authenticated)) {
    return <main className="grid min-h-screen place-items-center bg-[#f7f8fa] px-5 py-12">
      <section className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <div className="mb-10 flex items-center justify-between"><span className="font-display text-xl font-bold tracking-tight">COMET</span><button type="button" onClick={toggle} className="text-sm text-slate-500">{lang === 'ko' ? 'English' : '한국어'}</button></div>
        <h1 className="text-2xl font-semibold text-slate-900">{t('Your research workspace')}</h1>
        <p className="mt-3 text-sm leading-6 text-slate-500">{t('Sign in with the account provided by your organization.')}</p>
        {error && <p role="alert" className="mt-5 text-sm text-red-700">{t(error)}</p>}
        {!session ? <button className="mt-6 text-sm text-blue-700" onClick={() => void refresh().catch(() => setError('Cannot connect to COMET. Try again.'))}>{t(error ? 'Try again' : 'Connecting to COMET…')}</button> :
          <form className="mt-7 space-y-5" onSubmit={async (event) => {
            event.preventDefault();
            const form = event.currentTarget;
            const values = new FormData(form);
            setBusy(true); setError('');
            try {
              const next = await request<AccountSession>('/auth/login', { method: 'POST', body: JSON.stringify({ username: values.get('username'), password: values.get('password') }) });
              form.reset(); accept(next); notifyOtherTabs();
            } catch { setError('Sign-in failed. Check your details or try again later.'); }
            finally { setBusy(false); }
          }}>
            <label className="block text-sm font-medium text-slate-700">{t('Account name')}<input name="username" autoComplete="username" required minLength={3} maxLength={128} className="mt-2 block w-full rounded-lg border border-slate-300 px-3 py-2.5" /></label>
            <label className="block text-sm font-medium text-slate-700">{t('Password')}<input name="password" type="password" autoComplete="current-password" required maxLength={128} className="mt-2 block w-full rounded-lg border border-slate-300 px-3 py-2.5" /></label>
            <button disabled={busy} className="w-full rounded-lg bg-[#191f28] px-4 py-3 text-sm font-semibold text-white disabled:opacity-50">{t(busy ? 'Signing in…' : 'Sign in')}</button>
            <p className="text-xs leading-5 text-slate-500">{t('Need account access? Contact your organization administrator.')}</p>
          </form>}
      </section>
    </main>;
  }
  return <AuthContext.Provider value={{ session, refresh, signOut }}><div key={session.account?.id ?? 'desktop'}>{children}</div></AuthContext.Provider>;
}
