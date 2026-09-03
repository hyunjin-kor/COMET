import { createContext } from 'react';
import type { PriceBasis } from './api';

export interface BasisContextValue {
  basis: PriceBasis;
  toggle: () => void;
}

export const BasisContext = createContext<BasisContextValue | null>(null);
