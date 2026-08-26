import { NavLink, useLocation } from 'react-router-dom';
import { useUnit } from '../../lib/use-unit';
import BrandMark from './BrandMark';
import { isNavigationPathActive, navigationItems } from './navigation';

function CollapseIcon({ collapsed }: { collapsed: boolean }) {
  return (
    <svg
      viewBox="0 0 16 16"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.6}
      className={`h-4 w-4 transition-transform duration-300 ${collapsed ? 'rotate-180' : ''}`}
      aria-hidden="true"
    >
      <path d="M9.5 4.5 6 8l3.5 3.5" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M12.5 4.5 9 8l3.5 3.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.45" />
    </svg>
  );
}

type SidebarProps = {
  collapsed: boolean;
  onToggleCollapsed: () => void;
};

export default function Sidebar({ collapsed, onToggleCollapsed }: SidebarProps) {
  const { unit, toggle } = useUnit();
  const location = useLocation();
  const hasTitlebar = typeof window !== 'undefined' && window.cometDesktop?.platform === 'win32';

  return (
    <aside className="hidden lg:block">
      <div className={`surface-rail sticky overflow-hidden ${hasTitlebar ? 'top-[46px]' : 'top-2'} ${collapsed ? 'p-2' : 'p-3'}`}>
        <div className="flex flex-col gap-5">
          <div className={collapsed ? 'flex flex-col items-center gap-2 pt-1.5' : 'flex items-center gap-2.5 px-1.5 pt-1.5'}>
            <BrandMark className="h-9 w-9 flex-none" />
            {collapsed ? null : (
              <div className="min-w-0 flex-1">
                <div className="font-display text-[1.2rem] leading-none text-[#191f28]">COMET</div>
                <div className="mt-1 text-[11px] text-[#b0b8c1]">Catalyst cost workspace</div>
              </div>
            )}
            <button
              type="button"
              onClick={onToggleCollapsed}
              className="no-drag flex h-7 w-7 flex-none items-center justify-center rounded-[8px] text-[#b0b8c1] transition hover:bg-[#f2f4f6] hover:text-[#4e5968]"
              title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
              aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
              aria-expanded={!collapsed}
            >
              <CollapseIcon collapsed={collapsed} />
            </button>
          </div>

          <nav className="space-y-0.5">
            {navigationItems.map((item) => {
              const isActive = isNavigationPathActive(location.pathname, item.to);

              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  aria-current={isActive ? 'page' : undefined}
                  title={collapsed ? item.label : undefined}
                  className={`group relative flex items-center rounded-[10px] transition ${
                    collapsed ? 'justify-center px-0 py-2.5' : 'gap-3 px-3 py-2.5'
                  } ${isActive ? 'bg-[#eef8f5]' : 'hover:bg-[#f4f6f7]'}`}
                >
                  {isActive ? (
                    <span className="absolute left-0 top-1/2 h-4 w-[3px] -translate-y-1/2 rounded-full bg-[#0d9488]" aria-hidden="true" />
                  ) : null}
                  <item.Icon
                    className={`h-[18px] w-[18px] flex-none transition ${
                      isActive ? 'text-[#0d9488]' : 'text-[#b0b8c1] group-hover:text-[#8b95a1]'
                    }`}
                  />
                  {collapsed ? (
                    <span className="sr-only">{item.label}</span>
                  ) : (
                    <div
                      className={`min-w-0 truncate text-sm transition ${
                        isActive ? 'font-semibold text-[#0f766e]' : 'font-medium text-[#4e5968] group-hover:text-[#191f28]'
                      }`}
                    >
                      {item.label}
                    </div>
                  )}
                </NavLink>
              );
            })}
          </nav>

          {collapsed ? (
            <div className="border-t border-[#f2f4f6] pb-1 pt-3">
              <button
                type="button"
                onClick={toggle}
                className="no-drag mx-auto flex h-8 w-10 items-center justify-center rounded-full bg-[#eef1f2] text-xs font-semibold text-[#0f766e] transition hover:bg-[#e6f5f2]"
                title={`Display unit: ${unit} (click to switch)`}
                aria-label={`Toggle output units, currently ${unit}`}
                aria-pressed={unit === 'lb'}
              >
                {unit}
              </button>
            </div>
          ) : (
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
          )}
        </div>
      </div>
    </aside>
  );
}
