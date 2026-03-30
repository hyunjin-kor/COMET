import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import { getNavigationItem } from './navigation';
import TopNavigation from './TopNavigation';

export default function AppFrame() {
  const location = useLocation();
  const current = getNavigationItem(location.pathname);

  return (
    <div className="cp-shell relative min-h-screen overflow-x-hidden">
      <TopNavigation />

      <main className="mx-auto max-w-[1680px] px-3 pb-7 pt-3 sm:px-4 lg:px-5">
        <div className="grid gap-4 lg:grid-cols-[288px_minmax(0,1fr)] xl:gap-4">
          <Sidebar />

          <div className="min-w-0 space-y-4">
            <header className="surface-card relative overflow-hidden px-5 py-5 sm:px-6 lg:px-6">
              <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(120,242,208,0.2),transparent_0_28%),radial-gradient(circle_at_bottom_left,rgba(239,195,108,0.15),transparent_0_26%)]" />
              <div className="pointer-events-none absolute right-5 top-5 h-32 w-32 rounded-full border border-white/30 bg-white/10 blur-3xl" />
              <div className="pointer-events-none absolute bottom-0 left-0 right-0 h-18 bg-[linear-gradient(180deg,transparent,rgba(255,255,255,0.28))]" />

              <div className="relative space-y-5">
                <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_320px] xl:items-start">
                  <div className="max-w-4xl">
                    <span className="section-kicker">{current.eyebrow}</span>

                    <div className="mt-4 flex items-start gap-4">
                      <div className="hidden h-12 w-12 items-center justify-center rounded-[20px] border border-slate-900/8 bg-white/72 text-slate-900 shadow-[0_14px_28px_rgba(23,34,51,0.08)] sm:flex">
                        <current.Icon className="h-6 w-6" />
                      </div>

                      <div className="min-w-0">
                        <div className="cp-subtle-label">{current.subtitle}</div>
                        <h1 className="mt-2 max-w-3xl font-display text-[clamp(2rem,3vw,3rem)] leading-[0.98] text-slate-950">
                          {current.label}
                        </h1>
                        <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600 sm:text-[15px]">
                          {current.summary}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="surface-ink relative overflow-hidden p-4">
                    <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_18%_18%,rgba(120,242,208,0.24),transparent_0_32%),radial-gradient(circle_at_84%_12%,rgba(239,195,108,0.14),transparent_0_24%)]" />

                    <div className="relative">
                      <div className="flex items-center justify-between gap-3">
                        <div>
                          <div className="cp-subtle-label !text-slate-400">Workspace Readout</div>
                          <div className="mt-1 text-lg font-semibold text-white">Signal board</div>
                        </div>
                        <span className="cp-chip-dark">Desktop</span>
                      </div>

                      <p className="mt-3 text-sm leading-6 text-slate-300">
                        The current workspace keeps the costing flow, market references, and estimate outputs on one readable desktop surface.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="grid gap-3 md:grid-cols-3">
                  {current.signals.map((signal, index) => (
                    <div
                      key={signal.label}
                      className="cp-metric-tile cp-enter"
                      style={{ animationDelay: `${0.05 * (index + 1)}s` }}
                    >
                      <div className="cp-subtle-label">{signal.label}</div>
                      <div className="mt-2 text-base font-semibold text-slate-950">{signal.value}</div>
                    </div>
                  ))}
                </div>
              </div>
            </header>

            <div className="min-w-0 pb-2">
              <Outlet />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
