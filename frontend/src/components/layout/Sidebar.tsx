import { NavLink } from 'react-router-dom';
import { useUnit } from '../../lib/use-unit';

const navItems = [
  {
    to: '/',
    label: 'Calculator',
    sub: 'Cost Estimator',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} className="w-5 h-5">
        <rect x="4" y="3" width="16" height="18" rx="2" />
        <path d="M8 7h8M8 11h5M8 15h3" strokeLinecap="round" />
        <path d="M15 14l2 2 3-3" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    to: '/prices',
    label: 'Metal Prices',
    sub: 'Live Market Data',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} className="w-5 h-5">
        <path d="M3 17l4-4 4 2 4-6 4 3" strokeLinecap="round" strokeLinejoin="round" />
        <circle cx="21" cy="12" r="1" fill="currentColor" stroke="none" />
        <path d="M3 21h18" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    to: '/compare',
    label: 'Compare',
    sub: 'Side-by-Side',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} className="w-5 h-5">
        <rect x="3" y="6" width="7" height="14" rx="1.5" />
        <rect x="14" y="6" width="7" height="14" rx="1.5" />
        <path d="M10 12h4" strokeLinecap="round" />
        <path d="M6 3v3M18 3v3" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    to: '/uncertainty',
    label: 'Uncertainty',
    sub: 'Monte Carlo',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} className="w-5 h-5">
        <path d="M2 12C2 12 5 4 12 4s10 8 10 8-3 8-10 8S2 12 2 12z" />
        <circle cx="12" cy="12" r="3" />
        <path d="M12 2v2M12 20v2M2 12H4M20 12h2" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    to: '/library',
    label: 'Library',
    sub: 'Materials & Steps',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} className="w-5 h-5">
        <path d="M4 19.5A2.5 2.5 0 016.5 17H20" strokeLinecap="round" />
        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z" />
        <path d="M9 7h6M9 11h4" strokeLinecap="round" />
      </svg>
    ),
  },
];

export default function Sidebar() {
  const { unit, toggle } = useUnit();
  return (
    <aside className="w-60 min-h-screen flex-shrink-0 select-none bg-[#0f1623] text-white">
      {/* Brand */}
      <div className="px-5 pb-5 pt-6">
        <div className="mb-1 flex items-center gap-3">
          <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 shadow-lg shadow-blue-900/40">
            <svg viewBox="0 0 24 24" fill="none" className="w-4.5 h-4.5">
              <path d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2V9M9 21H5a2 2 0 01-2-2V9m0 0h18" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div>
            <h1 className="text-[15px] font-bold leading-none tracking-tight text-white">CatPrice</h1>
            <p className="mt-0.5 text-[10px] leading-none text-slate-500">Catalyst Cost Estimator</p>
          </div>
        </div>
        <div className="mt-4 h-px bg-gradient-to-r from-slate-700 via-slate-600 to-transparent" />
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-0.5 px-3">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `group flex items-center gap-3 rounded-xl border px-3 py-2.5 text-sm transition-all duration-150 ${
                isActive
                  ? 'border-blue-500/30 bg-gradient-to-r from-blue-600/30 to-indigo-600/20 text-white shadow-sm'
                  : 'border-transparent text-slate-400 hover:bg-white/5 hover:text-slate-200'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <span className={`flex-shrink-0 transition-colors ${isActive ? 'text-blue-400' : 'text-slate-500 group-hover:text-slate-300'}`}>
                  {item.icon}
                </span>
                <div className="min-w-0">
                  <div className={`text-[13px] font-medium leading-none ${isActive ? 'text-white' : ''}`}>{item.label}</div>
                  <div className={`mt-0.5 text-[10px] leading-none transition-colors ${isActive ? 'text-blue-300/70' : 'text-slate-600 group-hover:text-slate-500'}`}>{item.sub}</div>
                </div>
                {isActive && (
                  <span className="ml-auto h-1.5 w-1.5 flex-shrink-0 rounded-full bg-blue-400" />
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4">
        <div className="mb-3 h-px bg-gradient-to-r from-slate-700 via-slate-600 to-transparent" />

        {/* Unit toggle */}
        <div className="mb-3 flex items-center justify-between">
          <span className="text-[10px] font-medium uppercase tracking-wider text-slate-500">Unit</span>
          <button
            onClick={toggle}
            className="flex h-6 items-center gap-0 rounded-full border border-slate-700 bg-slate-800 p-0.5 transition-all"
            title="Toggle kg / lb"
          >
            <span className={`flex h-5 items-center px-2.5 rounded-full text-[10px] font-bold transition-all ${
              unit === 'kg'
                ? 'bg-blue-500 text-white shadow-sm'
                : 'text-slate-500'
            }`}>kg</span>
            <span className={`flex h-5 items-center px-2.5 rounded-full text-[10px] font-bold transition-all ${
              unit === 'lb'
                ? 'bg-blue-500 text-white shadow-sm'
                : 'text-slate-500'
            }`}>lb</span>
          </button>
        </div>

        <div className="mb-3 h-px bg-gradient-to-r from-slate-700 via-slate-600 to-transparent" />
        <div className="flex items-center justify-between">
          <span className="text-[10px] text-slate-600 font-mono">v1.0.1</span>
          <span className="text-[10px] text-slate-600">All rights reserved</span>
        </div>
        <div className="mt-1.5 text-[9px] leading-relaxed text-slate-700">
          Based on CatCost methodology<br/>Baddour et al. 2018
        </div>
      </div>
    </aside>
  );
}
