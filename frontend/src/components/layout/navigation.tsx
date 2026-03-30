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
  subtitle: string;
  eyebrow: string;
  summary: string;
  signals: { label: string; value: string }[];
  Icon: (props: IconProps) => ReactElement;
};

export const navigationItems: NavigationItem[] = [
  {
    to: '/',
    label: 'Calculator',
    subtitle: 'Organize inputs, materials, and step-method processing for one estimate.',
    eyebrow: 'Estimate Inputs',
    summary:
      'Translate synthesis inputs and business inputs into an industrial-scale catalyst estimate, with CatPrice layering live metal references onto a CatCost-style materials and step-method workflow.',
    signals: [
      { label: 'Inputs', value: 'Synthesis + business basis' },
      { label: 'Method', value: 'Materials + step method' },
      { label: 'Output', value: 'Estimate per kg and per lb' },
    ],
    Icon: CalculatorIcon,
  },
  {
    to: '/prices',
    label: 'Market Board',
    subtitle: 'Track the metal references behind materials and spent-catalyst valuation.',
    eyebrow: 'Price References',
    summary:
      'Monitor platinum-group, precious, and industrial metals with live and indexed references that extend the price-library logic used by CatCost materials and spent-catalyst workflows.',
    signals: [
      { label: 'Coverage', value: 'PGM, precious, and base metals' },
      { label: 'Source', value: 'Live + indexed references' },
      { label: 'History', value: 'Stored series and refresh' },
    ],
    Icon: PricesIcon,
  },
  {
    to: '/compare',
    label: 'Compare',
    subtitle: 'Benchmark alternative catalyst candidates on one estimate basis.',
    eyebrow: 'Scenario Comparison',
    summary:
      'Hold the estimate basis steady, vary composition and order assumptions, and compare how alternative catalyst candidates shift material, processing, and total estimated cost.',
    signals: [
      { label: 'Scenarios', value: '2 to 4 candidates' },
      { label: 'Basis', value: 'Shared estimate logic' },
      { label: 'Ranking', value: 'Lowest estimate highlighted' },
    ],
    Icon: CompareIcon,
  },
  {
    to: '/uncertainty',
    label: 'Uncertainty',
    subtitle: 'Study contributors to uncertainty in catalyst cost.',
    eyebrow: 'Uncertainty Analysis',
    summary:
      'Probe the range of plausible catalyst costs by sampling uncertainty in price and scale assumptions, echoing CatCost’s goal of helping researchers study cost uncertainty without building their own toolchain.',
    signals: [
      { label: 'Engine', value: 'Monte Carlo sampling' },
      { label: 'Envelope', value: 'P5 to P95 bands' },
      { label: 'Inputs', value: 'Price, support, and scale' },
    ],
    Icon: UncertaintyIcon,
  },
  {
    to: '/library',
    label: 'Library',
    subtitle: 'Browse the libraries that support a CatCost-style estimate.',
    eyebrow: 'Reference Catalog',
    summary:
      'Move through Materials Library rows, Step Library rates, and common process templates from one workspace, with CatPrice keeping the same module-oriented structure used in CatCost.',
    signals: [
      { label: 'Catalog', value: 'Materials, steps, templates' },
      { label: 'Search', value: 'Filter by term or category' },
      { label: 'Basis', value: 'CatCost-style libraries' },
    ],
    Icon: LibraryIcon,
  },
];

export function getNavigationItem(pathname: string): NavigationItem {
  const match = navigationItems.find((item) =>
    item.to === '/' ? pathname === '/' : pathname.startsWith(item.to),
  );

  return match ?? navigationItems[0];
}
