/**
 * `<FitPriceText>` — a headline-price display that shrinks its font when the
 * formatted string gets long.
 *
 * Length-based font buckets set the preferred size. Measure the available
 * width as well so a narrow result card never splits the amount across lines.
 *
 * Three named scales:
 *   - `xl`   used for the FINAL RESULT and Estimated-selling-price hero cards
 *   - `lg`   used for the selected-metal price hero on /prices
 *   - `md`   reserved for inline metric tiles and other smaller surfaces
 */

import { useLayoutEffect, useRef } from 'react';

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
    { max: 6,  font: 'clamp(1.9rem, 3.4vw, 3.0rem)' },
    { max: 8,  font: 'clamp(1.5rem, 2.6vw, 2.3rem)' },
    { max: 11, font: 'clamp(1.3rem, 2.3vw, 1.9rem)' },
    { max: 14, font: 'clamp(1.15rem, 2.1vw, 1.7rem)' },
    { max: 99, font: 'clamp(1.0rem, 1.9vw, 1.5rem)' },
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
  const containerRef = useRef<HTMLDivElement>(null);
  const textRef = useRef<HTMLSpanElement>(null);
  const buckets = BUCKETS[size];
  const bucket = buckets.find((entry) => text.length <= entry.max) ?? buckets[buckets.length - 1]!;

  useLayoutEffect(() => {
    const container = containerRef.current;
    const content = textRef.current;
    if (!container || !content) return;
    let active = true;
    const fit = () => {
      if (!active) return;
      content.style.fontSize = '';
      const available = container.clientWidth;
      const natural = content.getBoundingClientRect().width;
      if (available > 0 && natural > available) {
        const preferred = Number.parseFloat(getComputedStyle(container).fontSize);
        content.style.fontSize = `${preferred * available / natural}px`;
      }
    };
    fit();
    const observer = new ResizeObserver(fit);
    observer.observe(container);
    window.addEventListener('resize', fit);
    void document.fonts.ready.then(fit);
    return () => {
      active = false;
      observer.disconnect();
      window.removeEventListener('resize', fit);
    };
  }, [text, size]);

  return (
    <div
      ref={containerRef}
      className={`min-w-0 max-w-full font-display tabular-nums leading-[1.05] whitespace-nowrap ${className}`}
      style={{ fontSize: bucket.font }}
    >
      <span ref={textRef} className="inline-block">{text}</span>
    </div>
  );
}
