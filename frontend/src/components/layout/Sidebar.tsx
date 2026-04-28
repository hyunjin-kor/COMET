import { NavLink, useLocation } from 'react-router-dom';
import { useUnit } from '../../lib/use-unit';
import BrandMark from './BrandMark';
import { isNavigationPathActive, navigationItems } from './navigation';

export default function Sidebar() {
  const { unit, toggle } = useUnit();
  const location = useLocation();

  return (
    <aside className="hidden lg:block">
      <div className="surface-rail sticky top-[40px] overflow-hidden p-3">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(120,242,208,0.16),transparent_0_34%),radial-gradient(circle_at_bottom_right,rgba(239,195,108,0.10),transparent_0_24%)]" />

        <div className="relative flex flex-col gap-4">
          <div className="flex items-center gap-3 border-b border-white/10 pb-4">
            <div className="flex h-11 w-11 items-center justify-center rounded-[16px] border border-white/10 bg-white/8">
              <BrandMark className="h-8 w-8" />
            </div>

            <div className="min-w-0">
              <div className="font-display text-[1.45rem] leading-none text-white">CatPrice</div>
              <div className="mt-1 text-xs text-slate-400">Catalyst cost workspace</div>
            </div>
          </div>

          <div>
            <div className="cp-subtle-label !text-slate-400">Workflow</div>
          </div>

          <nav className="space-y-1.5">
            {navigationItems.map((item) => {
              const isActive = isNavigationPathActive(location.pathname, item.to);

              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={`group flex items-center gap-3 rounded-[18px] border px-3 py-3 transition ${
                    isActive
                      ? 'border-[#c96442]/18 bg-[linear-gradient(135deg,rgba(124,241,208,0.14),rgba(255,255,255,0.06))] shadow-[0_12px_26px_rgba(0,0,0,0.12)]'
                      : 'border-white/8 bg-white/[0.025] hover:border-white/14 hover:bg-white/[0.05]'
                  }`}
                >
                  <div
                    className={`flex h-10 w-10 flex-none items-center justify-center rounded-[16px] border transition ${
                      isActive
                        ? 'border-[#c96442]/22 bg-[#c96442]/12 text-[#f0d9cb]'
                        : 'border-white/10 bg-white/6 text-slate-300 group-hover:text-white'
                    }`}
                  >
                    <item.Icon className="h-5 w-5" />
                  </div>

                  <div className="min-w-0 text-sm font-semibold text-white">{item.label}</div>
                </NavLink>
              );
            })}
          </nav>

          <div className="border-t border-white/10 pt-4">
            <div className="cp-subtle-label !text-slate-400">Display Unit</div>

            <button
              type="button"
              onClick={toggle}
              className="no-drag mt-3 flex w-full items-center gap-1 rounded-full border border-white/10 bg-white/6 p-1"
              title="Toggle output units"
              aria-label={`Toggle output units, currently ${unit}`}
              aria-pressed={unit === 'lb'}
            >
              <span
                aria-hidden="true"
                className={`flex-1 rounded-full px-3 py-2 text-xs font-semibold transition ${
                  unit === 'kg' ? 'bg-[#c96442] text-[#1a1612]' : 'text-slate-300'
                }`}
              >
                kg
              </span>
              <span
                aria-hidden="true"
                className={`flex-1 rounded-full px-3 py-2 text-xs font-semibold transition ${
                  unit === 'lb' ? 'bg-[#c96442] text-[#1a1612]' : 'text-slate-300'
                }`}
              >
                lb
              </span>
            </button>
          </div>
        </div>
      </div>
    </aside>
  );
}
