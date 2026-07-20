import { Suspense, useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
import { useKeyboardShortcuts } from '../../lib/use-keyboard-shortcuts';
import KeyboardHints from './KeyboardHints';
import Sidebar from './Sidebar';
import TopNavigation from './TopNavigation';

const SIDEBAR_COLLAPSED_KEY = 'catprice.sidebar.collapsed';

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
  const { hintsVisible, closeHints } = useKeyboardShortcuts();
  // The Windows desktop shell adds a 38px custom titlebar above <main>;
  // subtract it so short pages still end flush with the viewport.
  const hasTitlebar = typeof window !== 'undefined' && window.catpriceDesktop?.platform === 'win32';
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

      <main className="mx-auto max-w-[1860px] px-3 pb-4 pt-2 sm:px-4 lg:px-5 lg:pt-1.5">
        <div
          className={`grid gap-3 transition-[grid-template-columns] duration-300 ease-[cubic-bezier(0.2,1,0.32,1)] xl:gap-4 ${
            sidebarCollapsed ? 'lg:grid-cols-[68px_minmax(0,1fr)]' : 'lg:grid-cols-[264px_minmax(0,1fr)]'
          }`}
        >
          <Sidebar collapsed={sidebarCollapsed} onToggleCollapsed={() => setSidebarCollapsed((value) => !value)} />

          <div className={`flex min-w-0 flex-col ${hasTitlebar ? 'min-h-[calc(100vh-60px)]' : 'min-h-[calc(100vh-22px)]'}`}>
            <Suspense fallback={<RouteLoadingFallback />}>
              <Outlet />
            </Suspense>
          </div>
        </div>
      </main>

      <KeyboardHints visible={hintsVisible} onClose={closeHints} />
    </div>
  );
}
