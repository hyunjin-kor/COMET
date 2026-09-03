import { lazy } from 'react';
import { BrowserRouter, HashRouter, Navigate, Route, Routes } from 'react-router-dom';
import AppFrame from './components/layout/AppFrame';
import { BasisProvider } from './lib/basis';
import { LangProvider } from './lib/i18n';
import { UnitProvider } from './lib/units';

const Calculator = lazy(() => import('./pages/Calculator'));
const CalculatorResult = lazy(() => import('./pages/CalculatorResult'));
const CapEx = lazy(() => import('./pages/CapEx'));
const Compare = lazy(() => import('./pages/Compare'));
const Library = lazy(() => import('./pages/Library'));
const Prices = lazy(() => import('./pages/Prices'));
const Uncertainty = lazy(() => import('./pages/Uncertainty'));

export default function App() {
  const Router =
    typeof window !== 'undefined' && window.location.protocol === 'file:'
      ? HashRouter
      : BrowserRouter;

  return (
    <LangProvider>
    <UnitProvider>
    <BasisProvider>
      <Router>
        <Routes>
          <Route element={<AppFrame />}>
            <Route path="/" element={<Calculator />} />
            <Route path="/calculator/result" element={<CalculatorResult />} />
            <Route path="/prices" element={<Prices />} />
            <Route path="/benchmarks" element={<Compare />} />
            <Route path="/benchmarks/:family" element={<Compare />} />
            <Route path="/compare" element={<Compare />} />
            <Route path="/decision" element={<Compare />} />
            <Route path="/uncertainty" element={<Uncertainty />} />
            <Route path="/capex" element={<CapEx />} />
            <Route path="/library" element={<Library />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </Router>
    </BasisProvider>
    </UnitProvider>
    </LangProvider>
  );
}
