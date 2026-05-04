/** Number-formatting helpers for catalyst-cost displays. */

/**
 * Render a price value as a USD string with sensible decimal precision and
 * en-US thousand separators. Used everywhere the UI prints "$..." figures so
 * that long values like 309396.09 render as `$309,396.09` instead of
 * `$309396.09`. Returns `'$0'` for non-finite input.
 */
export function formatPrice(value: number | null | undefined): string {
  if (value == null || !Number.isFinite(value)) return '$0';
  const abs = Math.abs(value);
  let body: string;
  if (abs >= 100_000) {
    body = value.toLocaleString('en-US', { maximumFractionDigits: 0 });
  } else if (abs >= 1) {
    body = value.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  } else {
    body = value.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 4,
    });
  }
  return `$${body}`;
}
