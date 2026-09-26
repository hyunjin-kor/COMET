import type { ProcessTemplate, TemplateCost } from './api';

export interface PreparationSelection {
  steps: string[];
  basis: string[];
  substitutions?: Array<{ from: string; to: string }>;
}

export function togglePreparationStep(selection: PreparationSelection, key: string): PreparationSelection {
  if (selection.steps.includes(key)) {
    return { ...selection, steps: selection.steps.filter((step) => step !== key) };
  }
  const selected = new Set([...selection.steps, key]);
  const basisKeys = new Set(selection.basis);
  return {
    ...selection,
    steps: [
      ...selection.basis.filter((step) => selected.has(step)),
      ...selection.steps.filter((step) => !basisKeys.has(step)),
      ...(!basisKeys.has(key) ? [key] : []),
    ],
  };
}

export function fitPreparationSelection(
  selection: PreparationSelection,
  cost: Pick<TemplateCost, 'steps_fitted' | 'substitutions'>,
  available: string[],
): PreparationSelection {
  const removed = new Set(selection.basis.filter((key) => !selection.steps.includes(key)));
  selection.substitutions?.forEach(({ from, to }) => { if (removed.has(to)) removed.add(from); });
  cost.substitutions.forEach(({ from, to }) => { if (removed.has(from)) removed.add(to); });
  const additions = selection.steps.filter((key) => !selection.basis.includes(key) && available.includes(key));
  return {
    steps: [...cost.steps_fitted.filter((key) => !removed.has(key)), ...additions],
    basis: [...cost.steps_fitted],
    substitutions: cost.substitutions,
  };
}

export function sameSteps(left: string[], right: string[]) {
  const orderedRight = [...right].sort();
  return left.length === right.length && [...left].sort().every((key, index) => key === orderedRight[index]);
}

export function isThermalTemplateReady(
  selectedId: string | null,
  costs: Record<string, TemplateCost>,
  steps: string[],
  orderSize: number,
  costOrderSize: number | null,
  edited = false,
) {
  if (!selectedId) return true;
  const fitted = costs[selectedId]?.steps_fitted;
  return orderSize === costOrderSize && !!fitted?.length && (edited || sameSteps(fitted, steps));
}

export function matchThermalTemplate(
  templates: ProcessTemplate[],
  costs: Record<string, TemplateCost>,
  steps: string[],
  selectedId: string | null,
) {
  const selected = templates.find((template) => template.id === selectedId);
  if (!selected) return null;
  const fitted = costs[selected.id]?.steps_fitted;
  return sameSteps(fitted?.length ? fitted : selected.steps, steps) ? selected : null;
}
