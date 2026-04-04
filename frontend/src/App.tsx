import { BrowserRouter, HashRouter, Route, Routes } from 'react-router-dom';
import AppFrame from './components/layout/AppFrame';
import Calculator from './pages/Calculator';
import CalculatorResult from './pages/CalculatorResult';
import Compare from './pages/Compare';
import Library from './pages/Library';
import Prices from './pages/Prices';
import Uncertainty from './pages/Uncertainty';
import { UnitProvider } from './lib/units';

export default function App() {
  const Router =
    typeof window !== 'undefined' && window.location.protocol === 'file:'
      ? HashRouter
      : BrowserRouter;

  return (
    <UnitProvider>
      <Router>
        <Routes>
          <Route element={<AppFrame />}>
            <Route path="/" element={<Calculator />} />
            <Route path="/calculator/result" element={<CalculatorResult />} />
            <Route path="/prices" element={<Prices />} />
            <Route path="/compare" element={<Compare />} />
            <Route path="/decision" element={<Compare />} />
            <Route path="/uncertainty" element={<Uncertainty />} />
            <Route path="/library" element={<Library />} />
          </Route>
        </Routes>
      </Router>
    </UnitProvider>
  );
}
