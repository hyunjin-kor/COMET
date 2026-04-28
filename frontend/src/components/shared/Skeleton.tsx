import type { CSSProperties } from 'react';

type SkeletonProps = {
  className?: string;
  style?: CSSProperties;
  /** Render as a circle for avatar / dot placeholders. */
  circle?: boolean;
  /** Force a specific width (Tailwind arbitrary value friendly). */
  width?: number | string;
  /** Force a specific height. Falls back to className-driven height. */
  height?: number | string;
};

/**
 * Editorial shimmer placeholder used while loading server data.
 *
 * The animation is purely CSS, runs on `transform`/`opacity` only, and is
 * suppressed by `prefers-reduced-motion: reduce` (handled globally in
 * `index.css`). The base color matches the warm cream surface palette
 * so the loading state never feels colder than the loaded content.
 */
export function Skeleton({ className = '', style, circle = false, width, height }: SkeletonProps) {
  const dims: CSSProperties = {
    ...(width != null ? { width } : null),
    ...(height != null ? { height } : null),
    ...style,
  };

  return (
    <span
      aria-hidden="true"
      className={`cp-skeleton ${circle ? 'rounded-full' : 'rounded-[10px]'} ${className}`}
      style={dims}
    />
  );
}

type SkeletonRowsProps = {
  /** How many list rows to render. */
  count?: number;
  /** Optional outer wrapper className. */
  className?: string;
};

/** Stacked list-row skeletons matching the cp-list-row geometry. */
export function SkeletonListRows({ count = 4, className = '' }: SkeletonRowsProps) {
  return (
    <div className={`space-y-2 ${className}`}>
      {Array.from({ length: count }, (_, idx) => (
        <div
          key={idx}
          className="grid w-full gap-3 rounded-[16px] border border-[rgba(28,22,14,0.07)] bg-[rgba(255,253,248,0.5)] px-4 py-3 sm:grid-cols-[minmax(0,1fr)_auto_auto] sm:items-center"
        >
          <div className="flex min-w-0 items-center gap-3">
            <Skeleton circle width={40} height={40} />
            <div className="min-w-0 flex-1 space-y-2">
              <Skeleton className="h-3.5 w-2/5" />
              <Skeleton className="h-2.5 w-3/4" />
            </div>
          </div>
          <Skeleton className="h-6 w-16 rounded-full" />
          <div className="text-right">
            <Skeleton className="ml-auto h-5 w-20" />
            <Skeleton className="mt-1 ml-auto h-2.5 w-12" />
          </div>
        </div>
      ))}
    </div>
  );
}

/** A single tile-shaped skeleton for status/metric cards. */
export function SkeletonTile({ className = '' }: { className?: string }) {
  return (
    <div className={`rounded-[16px] border border-[rgba(28,22,14,0.07)] bg-[rgba(255,253,248,0.5)] p-4 ${className}`}>
      <Skeleton className="h-2.5 w-1/3" />
      <Skeleton className="mt-3 h-7 w-2/5" />
      <Skeleton className="mt-2 h-2.5 w-3/4" />
    </div>
  );
}
