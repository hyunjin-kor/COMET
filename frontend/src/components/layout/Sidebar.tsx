import { NavLink, useLocation } from 'react-router-dom';
import { useUnit } from '../../lib/use-unit';
import BrandMark from './BrandMark';
import { isNavigationPathActive, navigationItems } from './navigation';

export default function Sidebar() {
  const { unit, toggle } = useUnit();
  const location = useLocation();

  return (
    <aside className="hidden lg:block">
      <div className="surface-rail sticky top-[46px] overflow-hidden p-3">
        <div className="flex flex-col gap-5">
          <div className="flex items-center gap-2.5 px-1.5 pt-1.5">
            <BrandMark className="h-9 w-9" />
            <div className="min-w-0">
              <div className="font-display text-[1.2rem] leading-none text-[#191f28]">CatPrice</div>
              <div className="mt-1 text-[11px] text-[#b0b8c1]">Catalyst cost workspace</div>
            </div>
          </div>

          <nav className="space-y-0.5">
            {navigationItems.map((item) => {
              const isActive = isNavigationPathActive(location.pathname, item.to);

              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  aria-current={isActive ? 'page' : undefined}
                  className={`group relative flex items-center gap-3 rounded-[10px] px-3 py-2.5 transition ${
                    isActive ? 'bg-[#eef8f5]' : 'hover:bg-[#f4f6f7]'
                  }`}
                >
                  {isActive ? (
                    <span className="absolute left-0 top-1/2 h-4 w-[3px] -translate-y-1/2 rounded-full bg-[#0d9488]" aria-hidden="true" />
                  ) : null}
                  <item.Icon
                    className={`h-[18px] w-[18px] flex-none transition ${
                      isActive ? 'text-[#0d9488]' : 'text-[#b0b8c1] group-hover:text-[#8b95a1]'
                    }`}
                  />
                  <div
                    className={`min-w-0 truncate text-sm transition ${
                      isActive ? 'font-semibold text-[#0f766e]' : 'font-medium text-[#4e5968] group-hover:text-[#191f28]'
                    }`}
                  >
                    {item.label}
                  </div>
                </NavLink>
              );
            })}
          </nav>

          <div className="border-t border-[#f2f4f6] px-1.5 pb-1 pt-4">
            <div className="flex items-center justify-between gap-3">
              <div className="text-xs font-medium text-[#8b95a1]">Display unit</div>

              <button
                type="button"
                onClick={toggle}
                className="no-drag flex items-center rounded-full bg-[#eef1f2] p-0.5"
                title="Toggle output units"
                aria-label={`Toggle output units, currently ${unit}`}
                aria-pressed={unit === 'lb'}
              >
                <span
                  aria-hidden="true"
                  className={`rounded-full px-3 py-1 text-xs font-semibold transition ${
                    unit === 'kg' ? 'bg-[#0d9488] text-white' : 'text-[#8b95a1]'
                  }`}
                >
                  kg
                </span>
                <span
                  aria-hidden="true"
                  className={`rounded-full px-3 py-1 text-xs font-semibold transition ${
                    unit === 'lb' ? 'bg-[#0d9488] text-white' : 'text-[#8b95a1]'
                  }`}
                >
                  lb
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
