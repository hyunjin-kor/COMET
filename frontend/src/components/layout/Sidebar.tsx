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
    <aside className="w-60 bg-[#0f1623] text-white min-h-screen flex flex-col select-none flex-shrink-0">
      {/* Brand */}
      <div className="px-5 pt-6 pb-5">
        <div className="flex items-center gap-3 mb-1">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center flex-shrink-0 shadow-lg shadow-blue-900/40">
            <svg viewBox="0 0 24 24" fill="none" className="w-4.5 h-4.5">
              <path d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2V9M9 21H5a2 2 0 01-2-2V9m0 0h18" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div>
            <h1 className="text-[15px] font-bold tracking-tight text-white leading-none">CatPrice</h1>
            <p className="text-[10px] text-slate-500 mt-0.5 leading-none">Catalyst Cost Estimator</p>
          </div>
        </div>
        <div className="mt-4 h-px bg-gradient-to-r from-slate-700 via-slate-600 to-transparent" />
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 space-y-0.5">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `group flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-all duration-150 ${
                isActive
                  ? 'bg-gradient-to-r from-blue-600/30 to-indigo-600/20 text-white border border-blue-500/30 shadow-sm'
                  : 'text-slate-400 hover:bg-white/5 hover:text-slate-200 border border-transparent'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <span className={`flex-shrink-0 transition-colors ${isActive ? 'text-blue-400' : 'text-slate-500 group-hover:text-slate-300'}`}>
                  {item.icon}
                </span>
                <div className="min-w-0">
                  <div className={`font-medium leading-none text-[13px] ${isActive ? 'text-white' : ''}`}>{item.label}</div>
                  <div className={`text-[10px] mt-0.5 leading-none transition-colors ${isActive ? 'text-blue-300/70' : 'text-slate-600 group-hover:text-slate-500'}`}>{item.sub}</div>
                </div>
                {isActive && (
                  <span className="ml-auto w-1.5 h-1.5 rounded-full bg-blue-400 flex-shrink-0" />
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-5 py-4">
        <div className="h-px bg-gradient-to-r from-slate-700 via-slate-600 to-transparent mb-3" />

        {/* Unit toggle */}
        <div className="flex items-center justify-between mb-3">
          <span className="text-[10px] text-slate-500 font-medium uppercase tracking-wider">Unit</span>
          <button
            onClick={toggle}
            className="flex items-center h-6 rounded-full bg-slate-800 border border-slate-700 p-0.5 gap-0 transition-all"
            title="Toggle kg / lb"
          >
            <span className={`px-2.5 h-5 rounded-full text-[10px] font-bold transition-all ${
              unit === 'kg'
                ? 'bg-blue-500 text-white shadow-sm'
                : 'text-slate-500'
            }`}>kg</span>
            <span className={`px-2.5 h-5 rounded-full text-[10px] font-bold transition-all ${
              unit === 'lb'
                ? 'bg-blue-500 text-white shadow-sm'
                : 'text-slate-500'
            }`}>lb</span>
          </button>
        </div>

        <div className="h-px bg-gradient-to-r from-slate-700 via-slate-600 to-transparent mb-3" />
        <div className="flex items-center justify-between">
          <span className="text-[10px] text-slate-600 font-mono">v0.1.0</span>
          <span className="text-[10px] text-slate-600">MIT License</span>
        </div>
        <div className="mt-1.5 text-[9px] text-slate-700 leading-relaxed">
          Based on CatCost methodology<br/>Baddour et al. 2018
        </div>
      </div>
    </aside>
  );
}
