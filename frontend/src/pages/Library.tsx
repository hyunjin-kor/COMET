import { useEffect, useState } from 'react';
import { SkeletonListRows } from '../components/shared/Skeleton';
import { WorkspaceSectionFooter, WorkspaceSectionNav, useWorkspaceSections, type WorkspaceSection } from '../components/shared/WorkspaceSections';
import {
  type CatalystDomain,
  fetchMaterials,
  fetchSteps,
  fetchTemplates,
  type MaterialItem,
  type ProcessTemplate,
  type StepLibraryItem,
} from '../lib/api';

type Tab = 'materials' | 'steps' | 'templates';

const CATEGORIES = ['', 'Precious Metal / PGM', 'Base Metal', 'Support', 'Chemical', 'Chemical / Solvent'];
const APPLICATION_OPTIONS = [
  { value: '', label: 'All applications' },
  { value: 'general', label: 'General' },
  { value: 'fuel_cell', label: 'Fuel Cell' },
  { value: 'direct_methanol_fuel_cell', label: 'DMFC' },
  { value: 'electrolyzer', label: 'Electrolyzer' },
];
const DOMAIN_OPTIONS: Array<{ value: '' | CatalystDomain; label: string }> = [
  { value: '', label: 'All domains' },
  { value: 'thermal', label: 'Thermocatalyst' },
  { value: 'electrocatalyst', label: 'Electrocatalyst' },
  { value: 'general', label: 'General' },
  { value: 'both', label: 'Both' },
];
const LIBRARY_SECTIONS: WorkspaceSection[] = [
  { id: 'materials', label: 'Materials', summary: 'Source rows with quote and trust metadata.' },
  { id: 'steps', label: 'Steps', summary: 'Hourly step rates by campaign scale.' },
  { id: 'templates', label: 'Templates', summary: 'Route templates and processing stages.' },
];

function categoryTone(category: string) {
  if (!category) return 'border-slate-200 bg-white text-slate-600';
  const value = category.toLowerCase();
  if (value.includes('pgm') || value.includes('precious')) return 'border-amber-200 bg-amber-50 text-amber-700';
  if (value.includes('support')) return 'border-emerald-200 bg-emerald-50 text-emerald-700';
  if (value.includes('metal')) return 'border-sky-200 bg-sky-50 text-sky-700';
  if (value.includes('solvent')) return 'border-violet-200 bg-violet-50 text-violet-700';
  return 'border-slate-200 bg-white text-slate-600';
}

function domainTone(domain: CatalystDomain | string) {
  const value = domain.toLowerCase();
  if (value === 'electrocatalyst') return 'border-cyan-200 bg-cyan-50 text-cyan-700';
  if (value === 'both') return 'border-fuchsia-200 bg-fuchsia-50 text-fuchsia-700';
  if (value === 'general') return 'border-slate-200 bg-white text-slate-600';
  return 'border-orange-200 bg-orange-50 text-orange-700';
}

function domainLabel(domain: CatalystDomain | string) {
  if (domain === 'electrocatalyst') return 'Electrocatalyst';
  if (domain === 'both') return 'Both';
  if (domain === 'general') return 'General';
  return 'Thermocatalyst';
}

function applicationLabel(application: string) {
  if (application === 'fuel_cell') return 'Fuel Cell';
  if (application === 'direct_methanol_fuel_cell') return 'DMFC';
  if (application === 'electrolyzer') return 'Electrolyzer';
  return 'General';
}

function applicationTone(application: string) {
  if (application === 'fuel_cell') return 'border-rose-200 bg-rose-50 text-rose-700';
  if (application === 'direct_methanol_fuel_cell') return 'border-lime-200 bg-lime-50 text-lime-700';
  if (application === 'electrolyzer') return 'border-indigo-200 bg-indigo-50 text-indigo-700';
  return 'border-slate-200 bg-white text-slate-600';
}

function formatPack(material: MaterialItem) {
  if (!material.pack_quantity || !material.pack_unit) return 'Pack not stated';
  return `${material.pack_quantity} ${material.pack_unit} pack`;
}

function formatRawPrice(material: MaterialItem) {
  if (material.price == null || !material.price_unit) return 'N/A';
  return `$${Number(material.price).toFixed(material.price < 1 ? 4 : 2)} ${material.price_unit}`;
}

function priceScopeLabel(scope: string) {
  if (scope === 'literature_high_volume') return 'Literature HV';
  if (scope === 'vendor_lab') return 'Vendor Lab';
  return 'Historical Bulk';
}

function pricingBasisLabel(basis: string) {
  if (!basis) return 'basis not stated';
  return basis.replace(/_/g, ' ');
}

function sourceTrustLabel(material: MaterialItem) {
  if (material.reference_url) {
    if (material.price_scope === 'literature_high_volume') return 'Public literature source';
    if (material.price_scope === 'vendor_lab') return 'Direct vendor source';
    return 'Public source linked';
  }
  if (material.price_scope === 'historical_bulk') return 'No public permalink';
  return 'Link not stored';
}

function sourceTrustTone(material: MaterialItem) {
  if (material.reference_url) return 'border-emerald-200 bg-emerald-50 text-emerald-700';
  if (material.price_scope === 'historical_bulk') return 'border-amber-200 bg-amber-50 text-amber-700';
  return 'border-slate-200 bg-white text-slate-600';
}

function LibraryMetricTile({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="rounded-[22px] border border-slate-900/8 bg-white/58 p-4">
      <div className="cp-subtle-label">{label}</div>
      <div className="mt-2 text-2xl font-display text-[#1a1612]">{value}</div>
      <div className="mt-1 text-xs leading-5 text-slate-500">{detail}</div>
    </div>
  );
}

function InspectorRow({ label, value, detail }: { label: string; value: string; detail?: string }) {
  return (
    <div className="cp-data-row">
      <div>
        <div className="cp-subtle-label">{label}</div>
        {detail ? <div className="mt-1 text-xs leading-5 text-slate-500">{detail}</div> : null}
      </div>
      <div className="text-right text-sm font-semibold text-[#1a1612]">{value}</div>
    </div>
  );
}

export default function Library() {
  const sectionState = useWorkspaceSections(LIBRARY_SECTIONS, 'library');
  const tab = sectionState.activeSection.id as Tab;
  const [materials, setMaterials] = useState<MaterialItem[]>([]);
  const [templates, setTemplates] = useState<ProcessTemplate[]>([]);
  const [steps, setSteps] = useState<StepLibraryItem[]>([]);
  const [category, setCategory] = useState('');
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [catalystDomain, setCatalystDomain] = useState<'' | CatalystDomain>('');
  const [applicationFamily, setApplicationFamily] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedMaterialId, setSelectedMaterialId] = useState<string | null>(null);
  const [selectedStepKey, setSelectedStepKey] = useState<string | null>(null);
  const [selectedTemplateId, setSelectedTemplateId] = useState<string | null>(null);
  const publicLinkCount = materials.filter((material) => Boolean(material.reference_url)).length;
  const electrocatalystCount = materials.filter((material) => material.catalyst_domain === 'electrocatalyst').length;
  const historicalOnlyCount = materials.filter(
    (material) => material.price_scope === 'historical_bulk' && !material.reference_url,
  ).length;
  const selectedMaterial = materials.find((material) => String(material.id) === selectedMaterialId) ?? materials[0] ?? null;
  const selectedStep = steps.find((step) => step.key === selectedStepKey) ?? steps[0] ?? null;
  const selectedTemplate = templates.find((template) => template.id === selectedTemplateId) ?? templates[0] ?? null;

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(search), 300);
    return () => clearTimeout(timer);
  }, [search]);

  useEffect(() => {
    let cancelled = false;

    async function loadData() {
      setLoading(true);
        try {
        if (tab === 'materials') {
          const data = await fetchMaterials(
            category || undefined,
            debouncedSearch || undefined,
            catalystDomain || undefined,
            applicationFamily || undefined,
          );
          if (!cancelled) {
            setMaterials(data);
          }
          return;
        }

        if (tab === 'templates') {
          const data = await fetchTemplates(catalystDomain || undefined);
          if (!cancelled) setTemplates(data);
          return;
        }

        const data = await fetchSteps();
        if (!cancelled) setSteps(data);
      } catch {
        if (!cancelled) {
          setMaterials([]);
          setTemplates([]);
          setSteps([]);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void loadData();
    return () => {
      cancelled = true;
    };
  }, [tab, category, debouncedSearch, catalystDomain, applicationFamily]);

  useEffect(() => {
    if (materials.length === 0) {
      setSelectedMaterialId(null);
      return;
    }
    if (!selectedMaterialId || !materials.some((material) => String(material.id) === selectedMaterialId)) {
      setSelectedMaterialId(String(materials[0].id));
    }
  }, [materials, selectedMaterialId]);

  useEffect(() => {
    if (steps.length === 0) {
      setSelectedStepKey(null);
      return;
    }
    if (!selectedStepKey || !steps.some((step) => step.key === selectedStepKey)) {
      setSelectedStepKey(steps[0].key);
    }
  }, [selectedStepKey, steps]);

  useEffect(() => {
    if (templates.length === 0) {
      setSelectedTemplateId(null);
      return;
    }
    if (!selectedTemplateId || !templates.some((template) => template.id === selectedTemplateId)) {
      setSelectedTemplateId(templates[0].id);
    }
  }, [selectedTemplateId, templates]);

  return (
    <div className="space-y-4">
      <section className="surface-card cp-enter overflow-hidden px-5 py-6 sm:px-6" style={{ animationDelay: '0.06s' }}>
        <div className="flex flex-col gap-4 border-b border-slate-900/8 pb-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="cp-subtle-label">Source Library</div>
            <h2 className="cp-heading-xl mt-2">Inspect material sources, step rates, and route templates.</h2>
            <p className="cp-body-copy mt-2 max-w-2xl">
              Keep quote basis, route structure, and domain filters in one library so the costing workflow stays auditable.
            </p>
          </div>
          <span className="cp-chip">{tab}</span>
        </div>

        <div className="mt-5">
          <WorkspaceSectionNav
            sections={LIBRARY_SECTIONS}
            activeSectionId={sectionState.activeSectionId}
            activeIndex={sectionState.activeIndex}
            onSelect={sectionState.setActiveSection}
          />
        </div>

        {tab === 'materials' && (
          <>
            <div className="mt-5 grid gap-3 lg:grid-cols-[minmax(0,1fr)_220px_220px_220px]">
              <label className="block">
                <div className="cp-subtle-label">Search</div>
                <div className="mt-2">
                  <input
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                    placeholder="Search materials, formulas, or symbols"
                    className="input-base"
                  />
                </div>
              </label>

              <label className="block">
                <div className="cp-subtle-label">Category filter</div>
                <div className="mt-2">
                  <select value={category} onChange={(event) => setCategory(event.target.value)} className="input-base">
                    <option value="">All categories</option>
                    {CATEGORIES.filter(Boolean).map((value) => (
                      <option key={value} value={value}>
                        {value}
                      </option>
                    ))}
                  </select>
                </div>
              </label>

              <label className="block">
                <div className="cp-subtle-label">Catalyst domain</div>
                <div className="mt-2">
                  <select
                    value={catalystDomain}
                    onChange={(event) => setCatalystDomain(event.target.value as '' | CatalystDomain)}
                    className="input-base"
                  >
                    {DOMAIN_OPTIONS.map((option) => (
                      <option key={option.label} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
              </label>

              <label className="block">
                <div className="cp-subtle-label">Application</div>
                <div className="mt-2">
                  <select
                    value={applicationFamily}
                    onChange={(event) => setApplicationFamily(event.target.value)}
                    className="input-base"
                  >
                    {APPLICATION_OPTIONS.map((option) => (
                      <option key={option.label} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
              </label>
            </div>

            <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              <LibraryMetricTile label="Filtered rows" value={String(materials.length)} detail="Material rows visible under the current filters." />
              <LibraryMetricTile label="Public links" value={String(publicLinkCount)} detail="Rows that open a source page directly." />
              <LibraryMetricTile label="Electrocatalyst rows" value={String(electrocatalystCount)} detail="Rows tagged for electrocatalyst workflows." />
              <LibraryMetricTile label="Archive-only rows" value={String(historicalOnlyCount)} detail="Historical bulk rows without a stable public URL." />
            </div>

            <div className="cp-split-workspace mt-5">
              <div className="overflow-hidden rounded-[28px] border border-slate-900/8 bg-white/58 backdrop-blur-xl">
                <div className="border-b border-slate-900/8 bg-slate-50/80 px-5 py-3 text-xs leading-6 text-slate-600">
                  Public URLs open directly when available. Historical bulk rows remain visible, but many do not have a stable public permalink.
                </div>

                {loading ? (
                  <div className="px-4 py-4">
                    <SkeletonListRows count={6} />
                  </div>
                ) : materials.length === 0 ? (
                  <div className="flex flex-col items-start gap-3 px-5 py-8 text-sm text-slate-500">
                    <div>
                      <div className="font-semibold text-[#1a1612]">No materials match the current filters.</div>
                      <div className="mt-1 text-xs leading-5 text-slate-500">
                        Try clearing the search box or category filter to see the full library.
                      </div>
                    </div>
                    {(search || category) ? (
                      <button
                        type="button"
                        onClick={() => {
                          setSearch('');
                          setCategory('');
                        }}
                        className="cp-button-secondary px-3.5 py-2 text-xs"
                      >
                        Clear filters
                      </button>
                    ) : null}
                  </div>
                ) : (
                  <div className="max-h-[68vh] space-y-2 overflow-auto px-4 py-4">
                    {materials.map((material) => {
                      const active = selectedMaterial?.id === material.id;
                      return (
                        <div
                          key={material.id}
                          onClick={() => setSelectedMaterialId(String(material.id))}
                          className={`${active ? 'cp-list-row cp-list-row-active' : 'cp-list-row'} cursor-pointer`}
                        >
                          <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                            <div className="min-w-0">
                              <div className="truncate font-semibold text-[#1a1612]">{material.name}</div>
                              <div className="truncate text-xs text-slate-500">{material.symbol || material.formula || 'No symbol'}</div>
                              {material.notes ? <div className="mt-1 text-xs leading-5 text-slate-500">{material.notes}</div> : null}
                            </div>
                            <div className="text-left lg:text-right">
                              <div className="font-mono text-slate-900">{formatRawPrice(material)}</div>
                              <div className="mt-1 text-xs text-slate-500">{formatPack(material)}</div>
                            </div>
                          </div>
                          <div className="mt-3 flex flex-wrap gap-2">
                            <span className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] ${domainTone(material.catalyst_domain)}`}>{domainLabel(material.catalyst_domain)}</span>
                            <span className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] ${applicationTone(material.application_family)}`}>{applicationLabel(material.application_family)}</span>
                            <span className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] ${categoryTone(material.category)}`}>{material.category || 'Uncategorised'}</span>
                            <span className={`inline-flex rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.16em] ${sourceTrustTone(material)}`}>{sourceTrustLabel(material)}</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              <div className="cp-inspector-rail">
                <section className="cp-rail-panel">
                  <div className="cp-subtle-label">Source Detail</div>
                  <div className="mt-2 text-lg font-semibold text-[#1a1612]">{selectedMaterial?.name ?? 'Choose a material row'}</div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {selectedMaterial ? <span className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] ${domainTone(selectedMaterial.catalyst_domain)}`}>{domainLabel(selectedMaterial.catalyst_domain)}</span> : null}
                    {selectedMaterial ? <span className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] ${applicationTone(selectedMaterial.application_family)}`}>{applicationLabel(selectedMaterial.application_family)}</span> : null}
                    {selectedMaterial ? <span className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] ${categoryTone(selectedMaterial.category)}`}>{selectedMaterial.category || 'Uncategorised'}</span> : null}
                  </div>
                  {selectedMaterial ? (
                    <>
                      <div className="mt-4 space-y-1">
                        <InspectorRow label="Quote" value={formatRawPrice(selectedMaterial)} detail={formatPack(selectedMaterial)} />
                        <InspectorRow label="Scope" value={priceScopeLabel(selectedMaterial.price_scope)} detail={pricingBasisLabel(selectedMaterial.pricing_basis)} />
                        <InspectorRow label="Quote year" value={selectedMaterial.quote_year ? String(selectedMaterial.quote_year) : 'N/A'} detail={selectedMaterial.quote_source || 'Source not stated'} />
                        <InspectorRow label="Trust" value={sourceTrustLabel(selectedMaterial)} detail={selectedMaterial.reference_url ? 'Public URL available.' : 'Public URL not stored.'} />
                      </div>
                      {selectedMaterial.notes ? (
                        <div className="mt-3 rounded-[18px] border border-slate-900/8 bg-white/72 px-3 py-3 text-xs leading-6 text-slate-600">
                          {selectedMaterial.notes}
                        </div>
                      ) : null}
                      {selectedMaterial.reference_url ? (
                        <a href={selectedMaterial.reference_url} target="_blank" rel="noreferrer" className="cp-button-secondary mt-3 w-full px-3 py-2 text-xs">
                          Open source
                        </a>
                      ) : null}
                    </>
                  ) : (
                    <div className="mt-3 text-xs leading-6 text-slate-500">Choose a row from the record list to inspect its source basis here.</div>
                  )}
                </section>
              </div>
            </div>
          </>
        )}

        {tab === 'steps' && (
          <div className="cp-split-workspace mt-5">
            <div className="overflow-hidden rounded-[28px] border border-slate-900/8 bg-white/58 backdrop-blur-xl">
              {loading ? (
                <div className="px-5 py-8 text-sm text-slate-500">Loading step rates...</div>
              ) : (
                <div className="max-h-[68vh] space-y-2 overflow-auto px-4 py-4">
                  {steps.map((step) => {
                    const active = selectedStep?.key === step.key;
                    return (
                      <button
                        key={step.key}
                        onClick={() => setSelectedStepKey(step.key)}
                        className={`${active ? 'cp-list-row cp-list-row-active' : 'cp-list-row'} w-full text-left`}
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <div className="font-semibold text-[#1a1612]">{step.name}</div>
                            <div className="mt-1 text-xs text-slate-500">{step.basis}</div>
                          </div>
                          <span className="cp-chip">{step.key}</span>
                        </div>
                        <div className="mt-3 grid gap-2 sm:grid-cols-3">
                          <div className="rounded-[16px] border border-slate-900/8 bg-white/72 px-3 py-2 text-xs text-slate-600">Small: {step.cost_small != null ? `$${step.cost_small}/hr` : 'N/A'}</div>
                          <div className="rounded-[16px] border border-slate-900/8 bg-white/72 px-3 py-2 text-xs text-slate-600">Medium: {step.cost_medium != null ? `$${step.cost_medium}/hr` : 'N/A'}</div>
                          <div className="rounded-[16px] border border-slate-900/8 bg-white/72 px-3 py-2 text-xs text-slate-600">Large: {step.cost_large != null ? `$${step.cost_large}/hr` : 'N/A'}</div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>

            <div className="cp-inspector-rail">
              <section className="cp-rail-panel">
                <div className="cp-subtle-label">Step Detail</div>
                <div className="mt-2 text-lg font-semibold text-[#1a1612]">{selectedStep?.name ?? 'Choose a step row'}</div>
                {selectedStep ? (
                  <>
                    <div className="mt-3 space-y-1">
                      <InspectorRow label="Small" value={selectedStep.cost_small != null ? `$${selectedStep.cost_small}/hr` : 'N/A'} />
                      <InspectorRow label="Medium" value={selectedStep.cost_medium != null ? `$${selectedStep.cost_medium}/hr` : 'N/A'} />
                      <InspectorRow label="Large" value={selectedStep.cost_large != null ? `$${selectedStep.cost_large}/hr` : 'N/A'} />
                      <InspectorRow label="Basis" value={selectedStep.basis || 'N/A'} detail={selectedStep.key} />
                    </div>
                    <div className="mt-3 rounded-[18px] border border-slate-900/8 bg-white/72 px-3 py-3 text-xs leading-6 text-slate-600">
                      {selectedStep.note || 'No additional note stored for this step.'}
                    </div>
                  </>
                ) : (
                  <div className="mt-3 text-xs leading-6 text-slate-500">Choose a step to inspect the hourly-rate basis here.</div>
                )}
              </section>
            </div>
          </div>
        )}

        {tab === 'templates' && (
          <div className="mt-5 space-y-4">
            <div className="flex justify-end">
              <label className="block min-w-[220px]">
                <div className="cp-subtle-label">Catalyst domain</div>
                <div className="mt-2">
                  <select
                    value={catalystDomain}
                    onChange={(event) => setCatalystDomain(event.target.value as '' | CatalystDomain)}
                    className="input-base"
                  >
                    {DOMAIN_OPTIONS.map((option) => (
                      <option key={option.label} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
              </label>
            </div>

            <div className="cp-split-workspace">
              <div className="space-y-3">
                {loading ? (
                  <div className="text-sm text-slate-500">Loading templates...</div>
                ) : (
                  templates.map((template) => {
                    const active = selectedTemplate?.id === template.id;
                    return (
                      <button
                        key={template.id}
                        onClick={() => setSelectedTemplateId(template.id)}
                        className={`${active ? 'cp-list-row cp-list-row-active' : 'cp-list-row'} w-full text-left`}
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <div className="cp-subtle-label">{template.category || 'Template'}</div>
                            <div className="cp-heading-sm mt-2">{template.name}</div>
                          </div>
                          <div className="flex flex-wrap gap-2">
                            <span className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] ${domainTone(template.catalyst_domain)}`}>{domainLabel(template.catalyst_domain)}</span>
                            <span className="cp-chip">{template.steps.length} steps</span>
                          </div>
                        </div>
                        <div className="mt-3 text-sm leading-7 text-slate-600">{template.description}</div>
                      </button>
                    );
                  })
                )}
              </div>

              <div className="cp-inspector-rail">
                <section className="cp-rail-panel">
                  <div className="cp-subtle-label">Route Audit</div>
                  <div className="mt-2 text-lg font-semibold text-[#1a1612]">{selectedTemplate?.name ?? 'Choose a template'}</div>
                  {selectedTemplate ? (
                    <>
                      <div className="mt-3 flex flex-wrap gap-2">
                        <span className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] ${domainTone(selectedTemplate.catalyst_domain)}`}>{domainLabel(selectedTemplate.catalyst_domain)}</span>
                        {selectedTemplate.application_family ? <span className="cp-chip">{applicationLabel(selectedTemplate.application_family)}</span> : null}
                        {selectedTemplate.manufacturing_mode ? <span className="cp-chip">{selectedTemplate.manufacturing_mode}</span> : null}
                      </div>
                      <div className="mt-3 space-y-1">
                        <InspectorRow label="Steps" value={String(selectedTemplate.steps.length)} detail={selectedTemplate.source || 'Source not stated'} />
                        <InspectorRow label="Examples" value={selectedTemplate.example_catalysts.length ? String(selectedTemplate.example_catalysts.length) : '0'} detail="Stored catalyst examples in this route." />
                      </div>
                      <div className="mt-3 rounded-[18px] border border-slate-900/8 bg-white/72 px-3 py-3 text-xs leading-6 text-slate-600">
                        {selectedTemplate.route_note || selectedTemplate.description}
                      </div>
                      {(selectedTemplate.preprocess?.length || selectedTemplate.synthesis?.length || selectedTemplate.postprocess?.length) ? (
                        <div className="mt-3 space-y-3">
                          {selectedTemplate.preprocess?.length ? <div><div className="cp-subtle-label">Pre-treatment</div><div className="mt-2 flex flex-wrap gap-2">{selectedTemplate.preprocess.map((value) => <span key={value} className="cp-chip">{value}</span>)}</div></div> : null}
                          {selectedTemplate.synthesis?.length ? <div><div className="cp-subtle-label">Synthesis</div><div className="mt-2 flex flex-wrap gap-2">{selectedTemplate.synthesis.map((value) => <span key={value} className="cp-chip">{value}</span>)}</div></div> : null}
                          {selectedTemplate.postprocess?.length ? <div><div className="cp-subtle-label">Post-treatment</div><div className="mt-2 flex flex-wrap gap-2">{selectedTemplate.postprocess.map((value) => <span key={value} className="cp-chip">{value}</span>)}</div></div> : null}
                        </div>
                      ) : null}
                    </>
                  ) : (
                    <div className="mt-3 text-xs leading-6 text-slate-500">Choose a route template to inspect its preparation stages and audit fields here.</div>
                  )}
                </section>
              </div>
            </div>
          </div>
        )}

        <div className="mt-5">
          <WorkspaceSectionFooter
            activeSection={sectionState.activeSection}
            activeIndex={sectionState.activeIndex}
            totalSections={LIBRARY_SECTIONS.length}
            onPrevious={sectionState.goPrevious}
            onNext={sectionState.goNext}
            canGoPrevious={sectionState.canGoPrevious}
            canGoNext={sectionState.canGoNext}
          />
        </div>
      </section>
    </div>
  );
}
