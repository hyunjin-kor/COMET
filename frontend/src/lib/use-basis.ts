import { useContext } from 'react';
import { BasisContext } from './basis-context';

export function useBasis() {
  const ctx = useContext(BasisContext);
  if (!ctx) throw new Error('useBasis requires BasisProvider');
  return ctx;
}
