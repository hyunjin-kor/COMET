import type { EstimateRangeResult } from './api';
import type { CalculatorResultSnapshot } from './calculator-session';

type CsvCell = string | number | null | undefined;

function csvEscape(cell: CsvCell): string {
  if (cell == null) return '';
  const text = String(cell);
  if (/[",\n\r]/.test(text)) return `"${text.replace(/"/g, '""')}"`;
  return text;
}

function rows(...lines: CsvCell[][]): string {
  return lines.map((line) => line.map(csvEscape).join(',')).join('\r\n');
}

function slugify(text: string): string {
  const slug = text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 60);
  return slug || 'estimate';
}

export function downloadCsv(filename: string, content: string): void {
  // BOM so Excel opens the file as UTF-8.
  const blob = new Blob(['\uFEFF' + content], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

export function resultCsvFilename(snapshot: CalculatorResultSnapshot): string {
  const composition =
    typeof snapshot.result.input_summary.composition === 'string'
      ? snapshot.result.input_summary.composition
      : 'estimate';
  const date = snapshot.generatedAt.slice(0, 10);
  return `comet-result-${slugify(composition)}-${date}.csv`;
}

export function buildResultCsv(snapshot: CalculatorResultSnapshot): string {
  const { result } = snapshot;
  const composition =
    typeof result.input_summary.composition === 'string' ? result.input_summary.composition : 'Catalyst estimate';
  const step = result.step_method;
  const sections: string[] = [];

  sections.push(
    rows(
      ['COMET result export'],
      ['Composition', composition],
      ['Catalyst domain', String(result.input_summary.catalyst_domain ?? 'thermal')],
      ['Generated at', snapshot.generatedAt],
      ['Order size (tons)', snapshot.orderSize],
      ['Production scale', step.scale],
      ['Campaign days', Number(step.campaign_days)],
    ),
  );

  sections.push(
    rows(
      ['Summary'],
      ['Metric', 'Value', 'Unit'],
      ['Estimated selling price', result.summary.estimated_price_per_lb, '$/lb'],
      ['Estimated selling price', result.summary.estimated_price_per_kg, '$/kg'],
      ['Net cost', result.summary.net_cost_per_lb, '$/lb'],
      ['Net cost', result.summary.net_cost_per_kg, '$/kg'],
      ['Materials share', result.summary.materials_pct, '% of selling price'],
      ['Processing share', result.summary.processing_pct, '% of selling price'],
    ),
  );

  const ledger: CsvCell[][] = [
    ['Cost build-up'],
    ['Item', 'Cost ($/lb)'],
    ['Materials', result.materials.total_materials_cost_per_lb],
    ['Processing', Number(step.processing_cost_per_lb)],
  ];
  if (typeof step.ga_per_lb === 'number') ledger.push(['Overhead (general and administrative)', step.ga_per_lb]);
  if (typeof step.sard_per_lb === 'number') ledger.push(['Sales, admin & R&D (S&ARD)', step.sard_per_lb]);
  if (typeof step.margin_per_lb === 'number') {
    ledger.push([`Margin (${Number(step.margin_pct).toFixed(1)}%)`, step.margin_per_lb]);
  }
  ledger.push(['Estimated selling price', step.estimated_price_per_lb]);
  sections.push(rows(...ledger));

  sections.push(
    rows(
      ['Materials breakdown'],
      ['Role', 'Name', 'wt%', 'Price ($/lb)', 'Precursor markup', 'Cost ($/lb catalyst)', 'Cost share (%)'],
      ...result.materials.components.map((component): CsvCell[] => [
        component.role,
        component.name,
        component.wt_pct,
        component.price_per_lb,
        component.precursor_markup,
        component.cost_per_lb_cat,
        component.cost_pct,
      ]),
    ),
  );

  const resolved = result.resolved_materials ?? [];
  if (resolved.length) {
    sections.push(
      rows(
        ['Price evidence'],
        [
          'Material',
          'Used for',
          'Price',
          'Unit',
          'Scope',
          'Quote year',
          'Source',
          'Pricing basis',
          'Escalation factor',
          'Live override',
          'Reference URL',
        ],
        ...resolved.map((material): CsvCell[] => [
          material.name,
          material.used_for,
          material.price,
          material.price_unit,
          material.price_scope,
          material.quote_year,
          material.quote_source,
          material.pricing_basis,
          material.escalation_factor,
          material.live_override?.applied ? material.live_override.live_source : 'no',
          material.reference_url,
        ]),
      ),
    );
  }

  const route = result.route_summary;
  if (route) {
    sections.push(
      rows(
        ['Preparation route'],
        ['Template', route.name],
        ['Steps', route.steps.join('; ')],
        ['Source', route.source],
        ...route.reference_urls.map((url, index): CsvCell[] => [`Reference ${index + 1}`, url]),
      ),
    );
  } else if (snapshot.stepLabels.length) {
    sections.push(rows(['Preparation route'], ['Steps', snapshot.stepLabels.join('; ')]));
  }

  const electrode = result.electrode_model;
  if (electrode) {
    sections.push(
      rows(
        ['Electrode assembly'],
        ['Metric', 'Value', 'Unit'],
        ['Active area', electrode.active_area_cm2, 'cm2'],
        ['Catalyst loading', electrode.catalyst_loading_mg_cm2, 'mg/cm2'],
        ['Electrode total', electrode.total_cost_usd, '$'],
        ['Cost per cm2', electrode.cost_per_cm2_usd, '$/cm2'],
        ['Cost per m2', electrode.cost_per_m2_usd, '$/m2'],
        ...electrode.breakdown.map((entry): CsvCell[] => [entry.label, entry.cost_usd, '$']),
      ),
    );
  }

  const spent = result.spent_catalyst;
  if (spent) {
    sections.push(
      rows(
        ['Spent catalyst recovery'],
        ['Metric', 'Value', 'Unit'],
        ['Metal', spent.metal_symbol, ''],
        ['Gross metal value', spent.V_metal_per_lb, '$/lb'],
        ['Recovery cost', spent.C_recovery_per_lb, '$/lb'],
        ['Reclaimed value', spent.V_reclaimed_per_lb, '$/lb'],
      ),
    );
  }

  const lca = result.lca;
  if (lca && lca.gwp_kg_co2eq_per_kg_catalyst != null) {
    sections.push(
      rows(
        ['Cradle-to-gate LCA'],
        ['Metric', 'Value', 'Unit'],
        ['GWP', lca.gwp_kg_co2eq_per_kg_catalyst, 'kg CO2-eq/kg catalyst'],
        ['CED', lca.ced_mj_per_kg_catalyst, 'MJ/kg catalyst'],
        ['Mass coverage', lca.coverage_pct, '%'],
        ['Reference', lca.reference.citation, ''],
      ),
    );
  }

  if (result.warnings?.length) {
    sections.push(rows(['Model scope warnings'], ...result.warnings.map((warning): CsvCell[] => [warning])));
  }

  return sections.join('\r\n\r\n') + '\r\n';
}

export function rangeCsvFilename(result: EstimateRangeResult): string {
  return `comet-range-${slugify(result.composition)}.csv`;
}

export function buildRangeCsv(result: EstimateRangeResult): string {
  const sections: string[] = [];
  sections.push(
    rows(
      ['COMET estimate range export'],
      ['Composition', result.composition],
      ['Catalyst domain', result.catalyst_domain],
      ['Application family', result.application_family],
      ['Simulations', result.n_simulations],
      ['Successful runs', result.n_successful],
      ['Unit', result.unit],
    ),
  );
  sections.push(
    rows(
      ['Distribution'],
      ['Statistic', `Value (${result.unit})`],
      ['Baseline', result.baseline_price_per_lb],
      ['Mean', result.mean],
      ['Std dev', result.std],
      ['Min', result.min],
      ['P5', result.p5],
      ['P25', result.p25],
      ['Median', result.median],
      ['P75', result.p75],
      ['P95', result.p95],
      ['Max', result.max],
    ),
  );
  const applied = Object.entries(result.uncertainties_applied);
  if (applied.length) {
    sections.push(
      rows(
        ['Applied uncertainties'],
        ['Parameter', 'Low bound', 'High bound'],
        ...applied.map(([parameter, bounds]): CsvCell[] => [parameter, bounds[0], bounds[1]]),
      ),
    );
  }
  return sections.join('\r\n\r\n') + '\r\n';
}
