import { Suspense, useEffect, useState } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../../lib/auth';
import { useLang } from '../../lib/i18n';
import { useKeyboardShortcuts } from '../../lib/use-keyboard-shortcuts';
import KeyboardHints from './KeyboardHints';
import Sidebar from './Sidebar';
import TopNavigation from './TopNavigation';

const SIDEBAR_COLLAPSED_KEY = 'comet.sidebar.collapsed';

function RouteLoadingFallback() {
  return (
    <div className="rounded-[28px] border border-slate-200/70 bg-white/82 p-6 shadow-[0_20px_50px_rgba(15,23,42,0.06)]">
      <div className="space-y-4">
        <div className="h-3 w-28 animate-pulse rounded-full bg-slate-200/90" />
        <div className="h-10 w-80 max-w-full animate-pulse rounded-full bg-slate-200/80" />
        <div className="h-32 animate-pulse rounded-[24px] bg-slate-100/90" />
        <div className="grid gap-3 md:grid-cols-2">
          <div className="h-24 animate-pulse rounded-[22px] bg-slate-100/90" />
          <div className="h-24 animate-pulse rounded-[22px] bg-slate-100/90" />
        </div>
      </div>
    </div>
  );
}

export default function AppFrame() {
  const { session } = useAuth();
  const { t } = useLang();
  const aboutTitle = t('About COMET');
  const aboutDescription = t('Independently developed catalyst manufacturing cost, environmental screening and decision analysis software.');
  const aboutWorkflow = t('Traceable prices, explicit manufacturing boundaries and reproducible comparisons.');
  const aboutPriorWork = t('Prior work for adopted thermal costing: Baddour et al. (2018); Van Allsburg et al. (2022), CatCost.');
  const aboutButton = t('OK');
  useEffect(() => {
    void window.cometDesktop?.setAboutCopy?.({ title: aboutTitle, description: aboutDescription, workflow: aboutWorkflow, priorWork: aboutPriorWork, button: aboutButton });
  }, [aboutTitle, aboutDescription, aboutWorkflow, aboutPriorWork, aboutButton]);
  const location = useLocation();
  const inactive = session.account && !session.account.subscription.can_start_work;
  const { hintsVisible, closeHints } = useKeyboardShortcuts();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(
    () => typeof window !== 'undefined' && window.localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === '1',
  );

  useEffect(() => {
    window.localStorage.setItem(SIDEBAR_COLLAPSED_KEY, sidebarCollapsed ? '1' : '0');
  }, [sidebarCollapsed]);

  return (
    // overflow-x-clip (not -hidden): a hidden overflow ancestor becomes the
    // scroll container for position:sticky and freezes the sidebar in place.
    <div className="cp-shell relative min-h-screen overflow-x-clip">
      <TopNavigation />
      {session.mode === 'hosted' && <div className="mx-auto flex max-w-[1860px] items-center justify-between gap-4 px-5 py-3 text-sm">
        <span className="text-slate-500">{t('Research workspace')}</span>
        <Link to="/account" className="font-medium text-slate-700">{t('Account')} · {session.account?.username}</Link>
      </div>}

      <main className="mx-auto max-w-[1860px] px-3 pb-4 pt-2 sm:px-4 lg:px-5 lg:pt-1.5">
        <div
          className={`grid gap-3 transition-[grid-template-columns] duration-300 ease-[cubic-bezier(0.2,1,0.32,1)] xl:gap-4 ${
            sidebarCollapsed ? 'lg:grid-cols-[68px_minmax(0,1fr)]' : 'lg:grid-cols-[264px_minmax(0,1fr)]'
          }`}
        >
          <Sidebar collapsed={sidebarCollapsed} onToggleCollapsed={() => setSidebarCollapsed((value) => !value)} />

          <div className="flex min-w-0 flex-col">
            <Suspense fallback={<RouteLoadingFallback />}>
              {inactive && !['/account', '/library', '/prices'].includes(location.pathname) ? <section className="rounded-2xl border border-slate-200 bg-white p-8"><h1 className="text-xl font-semibold">{t('New calculations are paused')}</h1><p className="mt-3 text-sm text-slate-600">{t('Your saved work remains available in your account.')}</p><Link to="/account" className="mt-5 inline-block text-sm font-medium text-blue-700">{t('Open saved work')}</Link></section> : <Outlet />}
            </Suspense>
          </div>
        </div>
      </main>

      <KeyboardHints visible={hintsVisible} onClose={closeHints} />
    </div>
  );
}
