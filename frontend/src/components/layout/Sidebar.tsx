import { NavLink } from 'react-router-dom';

const navItems = [
  { to: '/', label: 'Calculator', icon: '=' },
  { to: '/prices', label: 'Metal Prices', icon: '$' },
  { to: '/compare', label: 'Compare', icon: '<>' },
  { to: '/uncertainty', label: 'Uncertainty', icon: '~' },
  { to: '/library', label: 'Library', icon: '#' },
];

export default function Sidebar() {
  return (
    <aside className="w-56 bg-slate-900 text-white min-h-screen flex flex-col">
      <div className="p-4 border-b border-slate-700">
        <h1 className="text-xl font-bold tracking-tight">CatPrice</h1>
        <p className="text-xs text-slate-400 mt-1">Catalyst Cost Estimator</p>
      </div>
      <nav className="flex-1 p-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`
            }
          >
            <span className="w-5 text-center font-mono">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="p-4 text-xs text-slate-500 border-t border-slate-700">
        v0.1.0 &middot; MIT License
      </div>
    </aside>
  );
}
