/** Number-formatting helpers for catalyst-cost displays. */

/**
 * Render a price value as a USD string with en-US thousand separators.
 * Prices >= $1 round to whole dollars (e.g. `$1,235`) so the UI doesn't get
 * cluttered with cents. Sub-$1 prices keep 2-4 decimal places so cheap
 * materials (e.g. $0.05/lb alumina) don't collapse to "$0". Returns `'$0'`
 * for non-finite input.
 */
export function formatPrice(value: number | null | undefined): string {
  if (value == null || !Number.isFinite(value)) return '$0';
  const abs = Math.abs(value);
  let body: string;
  if (abs >= 1) {
    body = value.toLocaleString('en-US', { maximumFractionDigits: 0 });
  } else {
    body = value.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 4,
    });
  }
  return `$${body}`;
}
