const SUB = '₀₁₂₃₄₅₆₇₈₉';
const SUP = '⁰¹²³⁴⁵⁶⁷⁸⁹';
const elements = new Set('H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og'.split(' '));
const subscript = (text: string) => text.replace(/[0-9nx+−-]/g, (char) => SUB[Number(char)] ?? ({ n: 'ₙ', x: 'ₓ', '+': '₊', '-': '₋', '−': '₋' }[char] ?? char));
const superscript = (text: string) => text.replace(/[0-9+−-]/g, (char) => SUP[Number(char)] ?? (char === '+' ? '⁺' : '⁻'));

export function scientificSearchText(text: string): string {
  return text.normalize('NFKC').replace(/−/g, '-');
}

function formula(text: string): string {
  const original = text;
  text = text.replace(/[₀-₉]/g, (char) => String(SUB.indexOf(char)));
  if (text.endsWith('.')) return formula(text.slice(0, -1)) + '.';
  const plane = text.match(/\(\d{3}\)$/);
  if (plane) return formula(text.slice(0, plane.index)) + plane[0];
  // These archive spellings are ambiguous source typos, not verified formulae.
  if (['Al23', 'Al203', 'A1203'].includes(text) || /^S\d+$/.test(text) && text !== 'S8') return original;
  if (/^P(?:1|5|10|25|50|75|90|95|99)$/.test(text)) return original;
  if (text === 'C12A7') return 'C₁₂A₇';
  if (text === 'Pt3M') return 'Pt₃M';
  if (text === 'CnH2n') return 'CₙH₂ₙ';
  if (text === 'CnH(2n+2)') return 'CₙH₂ₙ₊₂';
  if (/^[A-Z][a-z]?[nx]$/.test(text)) return original;
  if (/^(?:Co|Pt|Ni|Fe|Cu)0$/.test(text)) return `${text.slice(0, -1)}⁰`;
  if (/^(?:13C|14C|15N2?|18O2?)$/.test(text)) return superscript(text.slice(0, 2)) + formula(text.slice(2));
  if (/^CO2(?:RR|eq|e)$/.test(text)) return text.replace('CO2', 'CO₂');
  if (/^C\d+\+$/.test(text)) return `C${subscript(text.slice(1, -1))}+`;
  const charge = text.match(/\^(?:\{([0-9]*[+−-])\}|([0-9]*[+−-]))$/);
  let suffix = '';
  if (charge) {
    suffix = superscript((charge[1] ?? charge[2])!);
    text = text.slice(0, charge.index);
  } else if (/^(?:Fe|Co|Ni|Cu|Zn|Al|Ti|Cr|Mn|Ce|Pt|Pd|Ir|Ru|Rh|Au|Ag|Mg|Ca)\d*[+−-]$/.test(text)) {
    const parts = text.match(/^([A-Z][a-z]?)(\d*[+−-])$/)!;
    return parts[1]! + superscript(parts[2]!);
  } else if (/^(?:H|OH|NH4|NO3|HCO3|e)[+−-]$/.test(text)) {
    suffix = superscript(text.slice(-1));
    text = text.slice(0, -1);
    if (text === 'e') return `e${suffix}`;
  }
  const coefficient = text.match(/^(?:\d+|x(?=H2O$))/)?.[0] ?? '';
  text = text.slice(coefficient.length);
  const tokens = (text.match(/acac|[A-Z][a-z]?|\d+(?:\.\d+)?(?:[-+][nx])?|[nx]|[()[\]]/g) ?? [])
    .flatMap((token) => !elements.has(token) && /^[A-Z][nx]$/.test(token) ? [token[0]!, token[1]!] : [token]);
  if (tokens.join('') !== text) return original;
  let output = coefficient;
  let canCount = false;
  const brackets: string[] = [];
  for (const token of tokens) {
    if (elements.has(token) || token === 'acac') { output += token; canCount = true; }
    else if (token === '(' || token === '[') { brackets.push(token); output += token; canCount = false; }
    else if (token === ')' || token === ']') {
      if (/[([]$/.test(output) || brackets.pop() !== (token === ')' ? '(' : '[')) return original;
      output += token; canCount = true;
    } else if (canCount && (/^[nx]$/.test(token) || Number.parseFloat(token) > 0 && Number.parseFloat(token) < 100)) {
      output += subscript(token); canCount = false;
    } else return original;
  }
  return brackets.length || !tokens.length ? original : output + suffix;
}

export function formatScientificText(value: string | null | undefined): string {
  if (!value) return value ?? '';
  const protectedText = /(https?:\/\/[^\s<>"']+|www\.[^\s<>"']+|10\.\d{4,9}\/[^\s<>"']+|`[^`]*`|[\w.-]+\.(?:json|csv|xlsx?|pdf|md|py|exe|png|svg)\b|\bHS\d{4,}\b)/g;
  return value.split(protectedText).map((part, index) => {
    if (index % 2) return part;
    return part
      .replace(/\beg(?= occupancy\b)/g, 'e_g')
      .replace(/\b(mm|cm|km|m|ft|in|mol|kg|mg|g|ms|s|min|hr|h|mL|L|K|kPa|Pa|bar)(?:\^\{?([+−-]?\d+(?:\.\d+)?)\}?|([23]|-[1-3]))(?![\w])/g, (_, unit: string, power: string, compact: string) => unit + superscript(power ?? compact))
      .replace(/\^(?:\{([+−-]?\d+(?:\.\d+)?)\}|([+−-]?\d+(?:\.\d+)?))(?![\w+−-])/g, (_, braced: string, plain: string) => superscript(braced ?? plain))
      .replace(/(?<![\w])(?:\d+)?(?:[A-Za-z][A-Za-z0-9₀-₉.]*(?:\([A-Za-z0-9+]+\)[0-9]*)?|\([A-Za-z0-9]+\)[0-9]+)(?:[A-Za-z0-9₀-₉.]|[-+]x(?=[^a-z]|$))*(?:\^(?:\{\d*[+−-]\}|\d*[+−-])|[+−-](?![A-Za-z0-9]))?(?![\w])/g, formula)
      .replace(/(?<=[₀-₉A-Za-z)])\*(?=(?:\d+|x)H[₂2]O\b)/g, '·');
  }).join('');
}
