/**
 * `<FitPriceText>` — a headline-price display that shrinks its font when the
 * formatted string gets long.
 *
 * The container box stays the same; only the font-size changes. Sizing is
 * picked from a small set of buckets keyed off `text.length` so the result is
 * deterministic and SSR-stable (no ResizeObserver, no measurement flicker).
 *
 * Three named scales:
 *   - `xl`   used for the FINAL RESULT and Estimated-selling-price hero cards
 *   - `lg`   used for the selected-metal price hero on /prices
 *   - `md`   reserved for inline metric tiles and other smaller surfaces
 */

type FitSize = 'xl' | 'lg' | 'md';

type Bucket = { max: number; font: string };

const BUCKETS: Record<FitSize, Bucket[]> = {
  xl: [
    { max: 8,  font: 'clamp(2.6rem, 4.6vw, 4.4rem)' },
    { max: 11, font: 'clamp(2.0rem, 3.6vw, 3.4rem)' },
    { max: 14, font: 'clamp(1.6rem, 2.8vw, 2.5rem)' },
    { max: 99, font: 'clamp(1.2rem, 2.2vw, 1.9rem)' },
  ],
  lg: [
    { max: 8,  font: 'clamp(2.0rem, 3.6vw, 3.4rem)' },
    { max: 11, font: 'clamp(1.6rem, 2.8vw, 2.5rem)' },
    { max: 14, font: 'clamp(1.3rem, 2.4vw, 2.0rem)' },
    { max: 99, font: 'clamp(1.1rem, 2.0vw, 1.6rem)' },
  ],
  md: [
    { max: 8,  font: 'clamp(1.6rem, 2.6vw, 2.4rem)' },
    { max: 11, font: 'clamp(1.3rem, 2.2vw, 2.0rem)' },
    { max: 14, font: 'clamp(1.1rem, 1.9vw, 1.7rem)' },
    { max: 99, font: 'clamp(0.95rem, 1.6vw, 1.4rem)' },
  ],
};

export function FitPriceText({
  text,
  size = 'xl',
  className = '',
}: {
  text: string;
  size?: FitSize;
  className?: string;
}) {
  const buckets = BUCKETS[size];
  const bucket = buckets.find((entry) => text.length <= entry.max) ?? buckets[buckets.length - 1]!;
  return (
    <div
      className={`font-display tabular-nums leading-[1.05] [overflow-wrap:anywhere] ${className}`}
      style={{ fontSize: bucket.font }}
    >
      {text}
    </div>
  );
}
