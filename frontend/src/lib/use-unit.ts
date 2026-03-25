import { useContext } from 'react';
import { UnitContext } from './unit-context';

export function useUnit() {
  const ctx = useContext(UnitContext);
  if (!ctx) throw new Error('useUnit requires UnitProvider');
  return ctx;
}
