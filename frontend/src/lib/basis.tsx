import { useState, type ReactNode } from 'react';
import type { PriceBasis } from './api';
import { BasisContext } from './basis-context';

const BASIS_KEY = 'comet_basis';

// "live" is the practical basis (daily quotes); "reference" is the academic
// basis (IMF and Johnson Matthey monthly averages). The choice follows the
// user across pages and sessions like the unit and language toggles.
export function BasisProvider({ children }: { children: ReactNode }) {
  const [basis, setBasis] = useState<PriceBasis>(() => {
    try {
      return window.localStorage.getItem(BASIS_KEY) === 'reference' ? 'reference' : 'live';
    } catch {
      return 'live';
    }
  });

  const toggle = () =>
    setBasis((previous) => {
      const next: PriceBasis = previous === 'live' ? 'reference' : 'live';
      try {
        window.localStorage.setItem(BASIS_KEY, next);
      } catch {
        // storage unavailable - keep the in-memory choice
      }
      return next;
    });

  return <BasisContext.Provider value={{ basis, toggle }}>{children}</BasisContext.Provider>;
}
