import { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { useUnit } from '../../lib/use-unit';
import BrandMark from './BrandMark';
import { navigationItems } from './navigation';

function MinimizeIcon() {
  return (
    <svg viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth={1.5} className="h-3.5 w-3.5">
      <path d="M2.25 6.75h7.5" strokeLinecap="round" />
    </svg>
  );
}

function MaximizeIcon({ maximized }: { maximized: boolean }) {
  return maximized ? (
    <svg viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth={1.2} className="h-3.5 w-3.5">
      <path d="M3.25 2.75h5v5" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M2.75 4.25v5h5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ) : (
    <svg viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth={1.2} className="h-3.5 w-3.5">
      <rect x="2.5" y="2.5" width="7" height="7" rx="0.8" />
    </svg>
  );
}

function CloseIcon() {
  return (
    <svg viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth={1.5} className="h-3.5 w-3.5">
      <path d="M3 3l6 6M9 3 3 9" strokeLinecap="round" />
    </svg>
  );
}

export default function TopNavigation() {
  const { unit, toggle } = useUnit();
  const isWindowsDesktop = typeof window !== 'undefined' && window.catpriceDesktop?.platform === 'win32';
  const [isMaximized, setIsMaximized] = useState(false);

  useEffect(() => {
    if (!isWindowsDesktop) return undefined;

    void window.catpriceDesktop?.isWindowMaximized?.().then((value) => setIsMaximized(Boolean(value)));
    const unsubscribe = window.catpriceDesktop?.onWindowStateChanged?.((payload) => {
      setIsMaximized(Boolean(payload.isMaximized));
    });

    return unsubscribe;
  }, [isWindowsDesktop]);

  if (isWindowsDesktop) {
    return (
      <header className="sticky top-0 z-50 hidden lg:block">
        <div className="drag-region relative h-[38px] border-b border-slate-900/8 bg-[#fbf7f1]">
          <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(90deg,rgba(120,242,208,0.04),transparent_34%,rgba(239,195,108,0.05))]" />

          <div className="no-drag absolute right-0 top-0 flex h-full items-stretch">
            <button
              onClick={() => window.catpriceDesktop?.minimizeWindow?.()}
              className="flex w-12 items-center justify-center text-slate-500 transition hover:bg-slate-900/6 hover:text-slate-800"
              title="Minimize"
            >
              <MinimizeIcon />
            </button>

            <button
              onClick={() => window.catpriceDesktop?.toggleMaximizeWindow?.()}
              className="flex w-12 items-center justify-center text-slate-500 transition hover:bg-slate-900/6 hover:text-slate-800"
              title={isMaximized ? 'Restore' : 'Maximize'}
            >
              <MaximizeIcon maximized={isMaximized} />
            </button>

            <button
              onClick={() => window.catpriceDesktop?.closeWindow?.()}
              className="flex w-12 items-center justify-center text-slate-500 transition hover:bg-[#d95d5d] hover:text-white"
              title="Close"
            >
              <CloseIcon />
            </button>
          </div>
        </div>
      </header>
    );
  }

  return (
    <header className="sticky top-0 z-50 px-3 pb-2 pt-2 sm:px-4 lg:hidden">
      <div className="surface-card-soft overflow-hidden">
        <div className="drag-region relative border-b border-slate-900/8 px-4 pb-1.5 pt-[calc(env(titlebar-area-height,0px)+8px)]">
          <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(90deg,rgba(120,242,208,0.06),transparent_28%,transparent_72%,rgba(239,195,108,0.08))]" />
          <div className="relative flex items-center justify-between gap-3">
            <div className="text-[10px] font-semibold uppercase tracking-[0.28em] text-slate-500">Desktop Window</div>
            <div className="hidden h-6 w-28 rounded-full border border-slate-900/8 bg-white/40 xl:block" />
          </div>
        </div>

        <div className="no-drag px-4 py-2.5">
          <div className="flex items-center justify-between gap-3">
            <div className="flex min-w-0 items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-[16px] border border-slate-900/8 bg-white/80 shadow-[0_12px_24px_rgba(23,34,51,0.06)]">
                <BrandMark className="h-7 w-7" />
              </div>

              <div className="min-w-0">
                <div className="font-display text-[1.45rem] leading-none text-slate-950">CatPrice</div>
                <div className="mt-0.5 text-xs text-slate-500">Catalyst cost workspace</div>
              </div>
            </div>

            <button
              onClick={toggle}
              className="flex items-center gap-1 rounded-full border border-slate-300/70 bg-white/72 p-1 shadow-[0_10px_24px_rgba(23,34,51,0.05)]"
              title="Toggle output units"
            >
              <span
                className={`rounded-full px-3 py-1.5 text-xs font-semibold transition ${
                  unit === 'kg' ? 'bg-[#7cf1d0] text-slate-950' : 'text-slate-500'
                }`}
              >
                kg
              </span>
              <span
                className={`rounded-full px-3 py-1.5 text-xs font-semibold transition ${
                  unit === 'lb' ? 'bg-[#7cf1d0] text-slate-950' : 'text-slate-500'
                }`}
              >
                lb
              </span>
            </button>
          </div>

          <nav className="mt-3 flex gap-2 overflow-x-auto pb-1">
            {navigationItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  `group flex min-w-[148px] items-center gap-3 rounded-[18px] border px-3.5 py-2.5 transition ${
                    isActive
                      ? 'border-teal-300/55 bg-[linear-gradient(135deg,rgba(124,241,208,0.22),rgba(255,255,255,0.94))] shadow-[0_10px_24px_rgba(23,34,51,0.07)]'
                      : 'border-slate-300/70 bg-white/74 hover:border-slate-400/70 hover:bg-white'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <div
                      className={`flex h-9 w-9 flex-none items-center justify-center rounded-[14px] border transition ${
                        isActive
                          ? 'border-teal-300/55 bg-teal-50 text-teal-700'
                          : 'border-slate-300/60 bg-slate-50 text-slate-500 group-hover:text-slate-700'
                      }`}
                    >
                      <item.Icon className="h-[18px] w-[18px]" />
                    </div>

                    <div className="truncate text-sm font-semibold text-slate-900">{item.label}</div>
                  </>
                )}
              </NavLink>
            ))}
          </nav>
        </div>
      </div>
    </header>
  );
}
