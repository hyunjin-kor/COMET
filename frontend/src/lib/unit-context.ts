import { createContext } from 'react';
import type { Unit } from './unit-conversion';

export interface UnitContextValue {
  unit: Unit;
  toggle: () => void;
  toDisplay: (perLb: number) => number;
  toInternal: (displayVal: number) => number;
  fmtLabel: string;
  catLabel: string;
}

export const UnitContext = createContext<UnitContextValue | null>(null);
