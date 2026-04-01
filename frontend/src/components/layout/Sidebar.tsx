import { NavLink } from 'react-router-dom';
import { useUnit } from '../../lib/use-unit';
import BrandMark from './BrandMark';
import { navigationItems } from './navigation';

export default function Sidebar() {
  const { unit, toggle } = useUnit();

  return (
    <aside className="hidden lg:block">
      <div className="surface-rail sticky top-[50px] overflow-hidden p-3.5">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(120,242,208,0.16),transparent_0_34%),radial-gradient(circle_at_bottom_right,rgba(239,195,108,0.10),transparent_0_24%)]" />

        <div className="relative flex flex-col gap-4">
          <div className="flex items-center gap-3 border-b border-white/10 pb-4">
            <div className="flex h-11 w-11 items-center justify-center rounded-[18px] border border-white/10 bg-white/8">
              <BrandMark className="h-8 w-8" />
            </div>

            <div className="min-w-0">
              <div className="font-display text-[1.45rem] leading-none text-white">CatPrice</div>
              <div className="mt-1 text-xs text-slate-400">Catalyst cost tools</div>
            </div>
          </div>

          <nav className="space-y-2">
            {navigationItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  `group flex items-center gap-3 rounded-[20px] border px-3 py-3 transition ${
                    isActive
                      ? 'border-[#7cf1d0]/20 bg-[linear-gradient(135deg,rgba(124,241,208,0.18),rgba(255,255,255,0.06))] shadow-[0_16px_34px_rgba(0,0,0,0.14)]'
                      : 'border-white/8 bg-white/[0.03] hover:border-white/14 hover:bg-white/[0.05]'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <div
                      className={`flex h-10 w-10 flex-none items-center justify-center rounded-[16px] border transition ${
                        isActive
                          ? 'border-[#7cf1d0]/28 bg-[#7cf1d0]/14 text-[#bdfae7]'
                          : 'border-white/10 bg-white/6 text-slate-300 group-hover:text-white'
                      }`}
                    >
                      <item.Icon className="h-5 w-5" />
                    </div>

                    <div className="min-w-0 text-sm font-semibold text-white">{item.label}</div>
                  </>
                )}
              </NavLink>
            ))}
          </nav>

          <div className="border-t border-white/10 pt-4">
            <div className="cp-subtle-label !text-slate-400">Unit</div>

            <button
              onClick={toggle}
              className="no-drag mt-3 flex w-full items-center gap-1 rounded-full border border-white/10 bg-white/6 p-1"
              title="Toggle output units"
            >
              <span
                className={`flex-1 rounded-full px-3 py-2 text-xs font-semibold transition ${
                  unit === 'kg' ? 'bg-[#7cf1d0] text-slate-950' : 'text-slate-300'
                }`}
              >
                kg
              </span>
              <span
                className={`flex-1 rounded-full px-3 py-2 text-xs font-semibold transition ${
                  unit === 'lb' ? 'bg-[#7cf1d0] text-slate-950' : 'text-slate-300'
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
