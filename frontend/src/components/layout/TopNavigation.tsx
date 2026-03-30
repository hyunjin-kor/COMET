import { NavLink } from 'react-router-dom';
import { useUnit } from '../../lib/use-unit';
import BrandMark from './BrandMark';
import { navigationItems } from './navigation';

export default function TopNavigation() {
  const { unit, toggle } = useUnit();

  return (
    <header className="sticky top-0 z-50 px-3 pb-3 pt-3 sm:px-4 lg:px-6">
      <div className="surface-card-soft overflow-hidden">
        <div className="drag-region relative border-b border-slate-900/8 px-4 pb-2 pt-[calc(env(titlebar-area-height,0px)+10px)]">
          <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(90deg,rgba(120,242,208,0.08),transparent_30%,transparent_70%,rgba(239,195,108,0.10))]" />
          <div className="relative flex items-center justify-between gap-3">
            <div className="text-[10px] font-semibold uppercase tracking-[0.28em] text-slate-500">
              Desktop Window
            </div>
            <div className="hidden h-6 w-32 rounded-full border border-slate-900/8 bg-white/40 xl:block" />
          </div>
        </div>

        <div className="no-drag relative px-4 py-3">
          <div className="flex flex-col gap-3">
            <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
              <div className="flex min-w-0 items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-[20px] border border-slate-900/8 bg-white/80 shadow-[0_14px_30px_rgba(23,34,51,0.08)]">
                  <BrandMark className="h-8 w-8" />
                </div>

                <div className="min-w-0">
                  <div className="font-display text-[1.7rem] leading-none text-slate-950">CatPrice</div>
                  <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-slate-500">
                    <span className="cp-chip">Catalyst cost intelligence</span>
                    <span className="cp-chip">Live metals</span>
                    <span className="cp-chip">Desktop workspace</span>
                  </div>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                <div className="hidden rounded-full border border-slate-300/70 bg-white/72 px-3 py-2 text-xs font-medium text-slate-600 md:block">
                  CatCost modules + live pricing
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
            </div>

            <nav className="flex gap-2 overflow-x-auto pb-1 lg:hidden">
              {navigationItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === '/'}
                  className={({ isActive }) =>
                    `group flex min-w-[180px] items-center gap-3 rounded-[20px] border px-4 py-3 transition ${
                      isActive
                        ? 'border-teal-300/55 bg-[linear-gradient(135deg,rgba(124,241,208,0.22),rgba(255,255,255,0.94))] shadow-[0_12px_28px_rgba(23,34,51,0.08)]'
                        : 'border-slate-300/70 bg-white/74 hover:border-slate-400/70 hover:bg-white'
                    }`
                  }
                >
                  {({ isActive }) => (
                    <>
                      <div
                        className={`flex h-10 w-10 flex-none items-center justify-center rounded-[16px] border transition ${
                          isActive
                            ? 'border-teal-300/55 bg-teal-50 text-teal-700'
                            : 'border-slate-300/60 bg-slate-50 text-slate-500 group-hover:text-slate-700'
                        }`}
                      >
                        <item.Icon className="h-5 w-5" />
                      </div>

                      <div className="min-w-0">
                        <div className="truncate text-sm font-semibold text-slate-900">{item.label}</div>
                        <div className="truncate text-xs text-slate-500">{item.subtitle}</div>
                      </div>
                    </>
                  )}
                </NavLink>
              ))}
            </nav>
          </div>
        </div>
      </div>
    </header>
  );
}
