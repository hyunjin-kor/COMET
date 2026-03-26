import { BrowserRouter, HashRouter, Route, Routes } from 'react-router-dom';
import Sidebar from './components/layout/Sidebar';
import Calculator from './pages/Calculator';
import Prices from './pages/Prices';
import Library from './pages/Library';
import Compare from './pages/Compare';
import Uncertainty from './pages/Uncertainty';
import { UnitProvider } from './lib/units';

export default function App() {
  const Router = typeof window !== 'undefined' && window.location.protocol === 'file:' ? HashRouter : BrowserRouter;

  return (
    <UnitProvider>
      <Router>
        <div className="flex min-h-screen bg-transparent text-slate-900">
          <Sidebar />
          <main className="flex-1 overflow-auto min-w-0">
            <Routes>
              <Route path="/" element={<Calculator />} />
              <Route path="/prices" element={<Prices />} />
              <Route path="/compare" element={<Compare />} />
              <Route path="/uncertainty" element={<Uncertainty />} />
              <Route path="/library" element={<Library />} />
            </Routes>
          </main>
        </div>
      </Router>
    </UnitProvider>
  );
}
