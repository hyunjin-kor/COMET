import { NavLink } from 'react-router-dom';
import { useUnit } from '../../lib/use-unit';
import BrandMark from './BrandMark';
import { navigationItems } from './navigation';

export default function Sidebar() {
  const { unit, toggle } = useUnit();

  return (
    <aside className="hidden lg:block">
      <div className="surface-rail sticky top-[98px] overflow-hidden p-5">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(120,242,208,0.18),transparent_0_34%),radial-gradient(circle_at_bottom_right,rgba(239,195,108,0.12),transparent_0_26%)]" />

        <div className="relative flex flex-col gap-6">
          <div>
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="flex h-14 w-14 items-center justify-center rounded-[24px] border border-white/10 bg-white/8">
                  <BrandMark className="h-10 w-10" />
                </div>

                <div className="min-w-0">
                  <div className="font-display text-[1.9rem] leading-none text-white">CatPrice</div>
                  <div className="mt-1 text-xs leading-5 text-slate-400">
                    Industrial-scale catalyst cost estimation with live price references layered onto CatCost-style modules.
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-5 grid gap-2">
              <div className="rounded-[22px] border border-white/10 bg-white/6 px-4 py-3">
                <div className="cp-subtle-label !text-slate-400">Workspace mode</div>
                <div className="mt-2 text-sm font-semibold text-white">Desktop costing terminal</div>
                <div className="mt-1 text-xs leading-5 text-slate-400">
                  Inputs, libraries, outputs, comparison, and uncertainty analysis in one shell.
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div className="rounded-[22px] border border-white/10 bg-white/6 px-4 py-3">
                  <div className="cp-subtle-label !text-slate-400">Basis</div>
                  <div className="mt-2 text-sm font-semibold text-white">CatCost</div>
                </div>
                <div className="rounded-[22px] border border-white/10 bg-white/6 px-4 py-3">
                  <div className="cp-subtle-label !text-slate-400">View</div>
                  <div className="mt-2 text-sm font-semibold text-white">Live + indexed</div>
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-2 border-t border-white/10 pt-6">
            <div className="cp-subtle-label !text-slate-400">Navigation</div>
            {navigationItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  `group block rounded-[24px] border px-4 py-4 transition ${
                    isActive
                      ? 'border-[#7cf1d0]/18 bg-[linear-gradient(135deg,rgba(124,241,208,0.18),rgba(255,255,255,0.06))] shadow-[0_18px_38px_rgba(0,0,0,0.16)]'
                      : 'border-white/8 bg-white/[0.03] hover:border-white/14 hover:bg-white/[0.05]'
                  }`
                }
              >
                {({ isActive }) => (
                  <div className="flex items-start gap-3">
                    <div
                      className={`mt-0.5 flex h-11 w-11 flex-none items-center justify-center rounded-[18px] border transition ${
                        isActive
                          ? 'border-[#7cf1d0]/28 bg-[#7cf1d0]/14 text-[#bdfae7]'
                          : 'border-white/10 bg-white/6 text-slate-300 group-hover:text-white'
                      }`}
                    >
                      <item.Icon className="h-5 w-5" />
                    </div>

                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <div className="truncate text-sm font-semibold text-white">{item.label}</div>
                        {isActive && <span className="h-2 w-2 rounded-full bg-[#7cf1d0]" />}
                      </div>
                      <div className="mt-1 text-xs leading-5 text-slate-400">{item.subtitle}</div>
                    </div>
                  </div>
                )}
              </NavLink>
            ))}
          </div>

          <div className="border-t border-white/10 pt-6">
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="cp-subtle-label !text-slate-400">Output unit</div>
                <div className="mt-2 text-sm font-semibold text-white">Working display</div>
              </div>

              <button
                onClick={toggle}
                className="no-drag flex items-center gap-1 rounded-full border border-white/10 bg-white/6 p-1"
                title="Toggle output units"
              >
                <span
                  className={`rounded-full px-3 py-1.5 text-xs font-semibold transition ${
                    unit === 'kg' ? 'bg-[#7cf1d0] text-slate-950' : 'text-slate-300'
                  }`}
                >
                  kg
                </span>
                <span
                  className={`rounded-full px-3 py-1.5 text-xs font-semibold transition ${
                    unit === 'lb' ? 'bg-[#7cf1d0] text-slate-950' : 'text-slate-300'
                  }`}
                >
                  lb
                </span>
              </button>
            </div>

            <div className="mt-4 rounded-[24px] border border-white/10 bg-white/6 px-4 py-4">
              <div className="cp-subtle-label !text-slate-400">Methodology note</div>
              <div className="mt-2 text-xs leading-6 text-slate-400">
                CatCost integrates essential cost-estimation methods in a user-friendly tool; CatPrice follows that module structure and adds live market references plus a desktop workspace.
              </div>
              <div className="mt-3 text-[11px] leading-5 text-slate-500">
                Baddour et al. 2018 / Van Allsburg et al. 2022
              </div>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
