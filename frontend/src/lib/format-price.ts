/** Number-formatting helpers for catalyst-cost displays. */

/**
 * Render a price value as a USD string with en-US thousand separators.
 * Precision grades with magnitude so small prices keep their information
 * (a $1.47/cm2 electrode must not display as "$1") while large ones stay
 * uncluttered: >= $100 whole dollars, $10-100 one decimal, $1-10 two
 * decimals, sub-$1 keeps 2-4 decimal places. Trailing zeros are trimmed.
 * Returns `'$0'` for non-finite input.
 */
export function formatPrice(value: number | null | undefined): string {
  if (value == null || !Number.isFinite(value)) return '$0';
  const abs = Math.abs(value);
  let body: string;
  if (abs >= 100) {
    body = value.toLocaleString('en-US', { maximumFractionDigits: 0 });
  } else if (abs >= 10) {
    body = value.toLocaleString('en-US', { maximumFractionDigits: 1 });
  } else if (abs >= 1) {
    body = value.toLocaleString('en-US', { maximumFractionDigits: 2 });
  } else {
    body = value.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 4,
    });
  }
  return `$${body}`;
}
