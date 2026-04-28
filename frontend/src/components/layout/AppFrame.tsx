import { Suspense } from 'react';
import { Outlet } from 'react-router-dom';
import { useKeyboardShortcuts } from '../../lib/use-keyboard-shortcuts';
import KeyboardHints from './KeyboardHints';
import Sidebar from './Sidebar';
import TopNavigation from './TopNavigation';

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

  return (
    <div className="cp-shell relative min-h-screen overflow-x-hidden">
      <TopNavigation />

      <main className="mx-auto max-w-[1860px] px-3 pb-6 pt-2 sm:px-4 lg:px-5 lg:pt-1.5">
        <div className="grid gap-3 lg:grid-cols-[264px_minmax(0,1fr)] xl:gap-4">
          <Sidebar />

          <div className="min-w-0 pb-2">
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
