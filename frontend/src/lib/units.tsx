import { useState, type ReactNode } from 'react';
import { UnitContext } from './unit-context';
import { LB_PER_KG, type Unit } from './unit-conversion';

export function UnitProvider({ children }: { children: ReactNode }) {
  const [unit, setUnit] = useState<Unit>(() =>
    (localStorage.getItem('cattea_unit') as Unit) ?? 'kg'
  );

  const toggle = () => setUnit(prev => {
    const next = prev === 'kg' ? 'lb' : 'kg';
    localStorage.setItem('cattea_unit', next);
    return next;
  });

  const toDisplay = (perLb: number) => (unit === 'kg' ? perLb * LB_PER_KG : perLb);
  const toInternal = (v: number) => (unit === 'kg' ? v / LB_PER_KG : v);

  return (
    <UnitContext.Provider
      value={{
        unit,
        toggle,
        toDisplay,
        toInternal,
        fmtLabel: `/${unit}`,
        catLabel: `/${unit} cat`,
      }}
    >
      {children}
    </UnitContext.Provider>
  );
}
