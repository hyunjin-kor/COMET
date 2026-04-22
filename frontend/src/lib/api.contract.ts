import {
  createEquipment,
  createMaterial,
  deleteEquipment,
  deleteMaterial,
  deleteSavedEstimate,
  fetchBenchmarkFamilies,
  fetchEquipmentDetail,
  fetchMaterial,
  fetchMaterialApplicationFamilies,
  fetchMaterialCategories,
  fetchMaterialDomains,
  fetchPrice,
  fetchPriceHistory,
  fetchPrices,
  fetchSavedEstimate,
  fetchSavedEstimates,
  fetchTemplateDetail,
  checkHealth,
  refreshPrices,
  fetchDecisionBenchmark,
  updateEquipment,
  updateMaterial,
  type DeleteResponse,
  type EquipmentCreateInput,
  type EquipmentItem,
  type EquipmentUpdateInput,
  type BenchmarkFamilySummary,
  type DecisionBenchmark,
  type MaterialCreateInput,
  type MaterialItem,
  type MaterialUpdateInput,
  type MetalPrice,
  type PriceHistoryQuery,
  type PriceHistoryResponse,
  type SavedEstimateDetail,
  type SavedEstimateQuery,
  type SavedEstimateSummary,
  type ProcessTemplate,
} from './api';

export const apiCrudContracts = {
  createEquipment,
  createMaterial,
  deleteEquipment,
  deleteMaterial,
  deleteSavedEstimate,
  fetchBenchmarkFamilies,
  fetchEquipmentDetail,
  fetchMaterial,
  fetchMaterialApplicationFamilies,
  fetchMaterialCategories,
  fetchMaterialDomains,
  fetchPrice,
  fetchPriceHistory,
  fetchPrices,
  fetchSavedEstimate,
  fetchSavedEstimates,
  fetchTemplateDetail,
  checkHealth,
  refreshPrices,
  fetchDecisionBenchmark,
  updateEquipment,
  updateMaterial,
} satisfies {
  checkHealth: () => Promise<{
    status: string;
    version: string;
    last_price_update: string | null;
    scheduler_running: boolean;
  }>;
  createEquipment: (input: EquipmentCreateInput) => Promise<EquipmentItem>;
  createMaterial: (input: MaterialCreateInput) => Promise<MaterialItem>;
  deleteEquipment: (equipmentId: number) => Promise<DeleteResponse>;
  deleteMaterial: (materialId: number) => Promise<DeleteResponse>;
  deleteSavedEstimate: (estimateId: number) => Promise<DeleteResponse>;
  fetchBenchmarkFamilies: () => Promise<{ families: BenchmarkFamilySummary[] }>;
  fetchDecisionBenchmark: (
    family: string,
    profile?: 'balanced' | 'cost-first' | 'evidence-first',
  ) => Promise<DecisionBenchmark>;
  fetchEquipmentDetail: (equipmentId: string | number) => Promise<EquipmentItem>;
  fetchMaterial: (materialId: number) => Promise<MaterialItem>;
  fetchMaterialApplicationFamilies: () => Promise<string[]>;
  fetchMaterialCategories: () => Promise<string[]>;
  fetchMaterialDomains: () => Promise<string[]>;
  fetchPrice: (symbol: string) => Promise<MetalPrice>;
  fetchPriceHistory: (symbol: string, query?: PriceHistoryQuery) => Promise<PriceHistoryResponse>;
  fetchPrices: () => Promise<MetalPrice[]>;
  fetchSavedEstimate: (estimateId: number) => Promise<SavedEstimateDetail>;
  fetchSavedEstimates: (query?: SavedEstimateQuery) => Promise<SavedEstimateSummary[]>;
  fetchTemplateDetail: (templateId: string) => Promise<ProcessTemplate>;
  refreshPrices: () => Promise<{ status: string; prices_fetched: number; updated_at: string }>;
  updateEquipment: (equipmentId: number, input: EquipmentUpdateInput) => Promise<EquipmentItem>;
  updateMaterial: (materialId: number, input: MaterialUpdateInput) => Promise<MaterialItem>;
};
