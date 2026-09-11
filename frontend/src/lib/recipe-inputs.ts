import type { ConsumableInput, PrecursorConsumption } from './api';

export type RecipeDraft = Omit<PrecursorConsumption, 'retained_component_fraction' | 'purity_fraction' | 'yield_fraction' | 'price_per_kg'> & {
  retained_component_fraction: number | '';
  purity_fraction: number | '';
  yield_fraction: number | '';
  price_per_kg: number | '';
};
export type ConsumableDraft = Omit<ConsumableInput, 'kg_per_kg_catalyst' | 'price_per_kg'> & {
  kg_per_kg_catalyst: number | '';
  price_per_kg: number | '';
};

export const blankRecipe = (): RecipeDraft => ({ precursor_name: '', retained_component_fraction: '', purity_fraction: '', yield_fraction: '', price_per_kg: '', source_note: '' });

export function validRecipe(recipe?: RecipeDraft): boolean {
  if (!recipe) return true;
  return Boolean(recipe.precursor_name.trim() && recipe.source_note.trim())
    && [recipe.retained_component_fraction, recipe.purity_fraction, recipe.yield_fraction].every((v) => typeof v === 'number' && Number.isFinite(v) && v > 0 && v <= 1)
    && typeof recipe.price_per_kg === 'number' && Number.isFinite(recipe.price_per_kg) && recipe.price_per_kg >= 0;
}

export function validConsumables(items: ConsumableDraft[]): boolean {
  return items.every((c) => c.name.trim() && c.source_note.trim()
    && typeof c.kg_per_kg_catalyst === 'number' && Number.isFinite(c.kg_per_kg_catalyst) && c.kg_per_kg_catalyst > 0
    && typeof c.price_per_kg === 'number' && Number.isFinite(c.price_per_kg) && c.price_per_kg >= 0);
}
