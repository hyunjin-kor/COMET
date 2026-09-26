import { Fragment } from 'react';
import { formatScientificText } from '../../lib/scientific-text';

export function ScientificText({ text }: { text: string | null | undefined }) {
  const formatted = formatScientificText(text);
  return <>{formatted.split(/(e_g(?= occupancy\b)|[₀-₉ₙₓ₊₋]+(?:\.[₀-₉]+)?|[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻]+(?:\.[⁰¹²³⁴⁵⁶⁷⁸⁹]+)?)/g).map((part, index) => {
    if (part === 'e_g') return <Fragment key={index}>e<sub className="text-[0.75em] leading-none">g</sub></Fragment>;
    if (/^[₀-₉ₙₓ₊₋]/.test(part)) return <sub key={index} className="text-[0.75em] leading-none">{part.normalize('NFKC')}</sub>;
    if (/^[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻]/.test(part)) return <sup key={index} className="text-[0.75em] leading-none">{part.normalize('NFKC')}</sup>;
    return <Fragment key={index}>{part}</Fragment>;
  })}</>;
}
