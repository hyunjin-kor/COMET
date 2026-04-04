import type { ReactElement } from 'react';

type IconProps = {
  className?: string;
};

function CalculatorIcon({ className = '' }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} className={className}>
      <rect x="4" y="3.5" width="16" height="17" rx="2.5" />
      <path d="M8 8h8M8 12h4M8 16h3" strokeLinecap="round" />
      <path d="M15 14.5l1.8 1.8L20 13" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function PricesIcon({ className = '' }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} className={className}>
      <path d="M3 18.5h18" strokeLinecap="round" />
      <path d="M5 14.5 9 11l3 2 5-7 2 2" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="19" cy="8" r="1.25" fill="currentColor" stroke="none" />
    </svg>
  );
}

function CompareIcon({ className = '' }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} className={className}>
      <rect x="3" y="6" width="7.5" height="13" rx="1.8" />
      <rect x="13.5" y="6" width="7.5" height="13" rx="1.8" />
      <path d="M10.5 12h3" strokeLinecap="round" />
      <path d="M6.75 3.5v2.5M17.25 3.5v2.5" strokeLinecap="round" />
    </svg>
  );
}

function UncertaintyIcon({ className = '' }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} className={className}>
      <path d="M3.5 12s2.75-7 8.5-7 8.5 7 8.5 7-2.75 7-8.5 7-8.5-7-8.5-7Z" />
      <circle cx="12" cy="12" r="2.8" />
      <path d="M12 2v2M12 20v2M2 12h2M20 12h2" strokeLinecap="round" />
    </svg>
  );
}

function LibraryIcon({ className = '' }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} className={className}>
      <path d="M4.5 18.5A2.5 2.5 0 0 1 7 16h12.5" strokeLinecap="round" />
      <path d="M7 3h12.5v18H7A2.5 2.5 0 0 1 4.5 18.5v-13A2.5 2.5 0 0 1 7 3Z" />
      <path d="M9.5 8h6.5M9.5 12h4.5" strokeLinecap="round" />
    </svg>
  );
}

export type NavigationItem = {
  to: string;
  label: string;
  Icon: (props: IconProps) => ReactElement;
};

export const navigationItems: NavigationItem[] = [
  { to: '/', label: 'Calculator', Icon: CalculatorIcon },
  { to: '/prices', label: 'Market Board', Icon: PricesIcon },
  { to: '/decision', label: 'Decision Board', Icon: CompareIcon },
  { to: '/uncertainty', label: 'Uncertainty', Icon: UncertaintyIcon },
  { to: '/library', label: 'Library', Icon: LibraryIcon },
];

export function isNavigationPathActive(pathname: string, to: string): boolean {
  if (to === '/') {
    return pathname === '/' || pathname.startsWith('/calculator/');
  }

  return pathname === to || pathname.startsWith(`${to}/`);
}
