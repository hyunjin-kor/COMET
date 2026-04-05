import { useEffect, useState } from 'react';
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

function sourceLinkLabel(material: MaterialItem) {
  if (material.quote_source) return material.quote_source;
  if (!material.reference_url) return 'Source not stated';
  try {
    return new URL(material.reference_url).hostname.replace(/^www\./, '');
  } catch {
    return 'Source link';
  }
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

  return (
    <div className="space-y-4">
      <section className="surface-card cp-enter overflow-hidden px-5 py-6 sm:px-6" style={{ animationDelay: '0.06s' }}>
        <div className="flex flex-col gap-4 border-b border-slate-900/8 pb-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="cp-subtle-label">Source Library</div>
            <h2 className="cp-heading-xl mt-2">Materials, sources, and route templates</h2>
            <p className="cp-body-copy mt-2 max-w-2xl">
              Move between material sources, process steps, and route templates from one place, with clear domain and application filters.
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

            <div className="mt-5 overflow-hidden rounded-[28px] border border-slate-900/8 bg-white/58 backdrop-blur-xl">
              <div className="border-b border-slate-900/8 bg-slate-50/80 px-5 py-3 text-xs leading-6 text-slate-600">
                Public URLs open directly when available. Historical bulk rows remain visible, but many do not have a stable public permalink.
              </div>
              <div className="grid grid-cols-[minmax(0,1.35fr)_120px_120px_150px_220px_minmax(0,210px)] gap-3 border-b border-slate-900/8 bg-white/46 px-5 py-3 text-[11px] uppercase tracking-[0.18em] text-slate-500">
                <span>Material</span>
                <span>Domain</span>
                <span>Application</span>
                <span>Category</span>
                <span>Quote</span>
                <span>Source & trust</span>
              </div>

              {loading ? (
                <div className="px-5 py-8 text-sm text-slate-500">Loading materials...</div>
              ) : materials.length === 0 ? (
                <div className="px-5 py-8 text-sm text-slate-500">No materials match the current filters.</div>
              ) : (
                <div className="max-h-[62vh] divide-y divide-slate-900/8 overflow-auto">
                  {materials.map((material) => (
                    <div key={material.id} className="grid grid-cols-[minmax(0,1.35fr)_120px_120px_150px_220px_minmax(0,210px)] gap-3 px-5 py-3 text-sm">
                      <div className="min-w-0">
                        <div className="truncate font-semibold text-slate-950">{material.name}</div>
                        <div className="truncate text-xs text-slate-500">{material.symbol || material.formula || 'No symbol'}</div>
                        {material.notes ? (
                          <div className="mt-1 text-xs leading-5 text-slate-500">{material.notes}</div>
                        ) : null}
                      </div>
                      <div>
                        <span className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] ${domainTone(material.catalyst_domain)}`}>
                          {domainLabel(material.catalyst_domain)}
                        </span>
                      </div>
                      <div>
                        <span className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] ${applicationTone(material.application_family)}`}>
                          {applicationLabel(material.application_family)}
                        </span>
                      </div>
                      <div>
                        <span className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] ${categoryTone(material.category)}`}>
                          {material.category || 'Uncategorised'}
                        </span>
                      </div>
                      <div className="min-w-0">
                        <div className="font-mono text-slate-700">{formatRawPrice(material)}</div>
                        <div className="mt-1 truncate text-xs text-slate-500">{formatPack(material)}</div>
                        <div className="mt-1 truncate text-xs text-slate-500">
                          {priceScopeLabel(material.price_scope)} / {pricingBasisLabel(material.pricing_basis)}
                          {material.quote_year ? ` / ${material.quote_year}` : ''}
                        </div>
                      </div>
                      <div className="min-w-0 text-slate-500">
                        {material.reference_url ? (
                          <a
                            href={material.reference_url}
                            target="_blank"
                            rel="noreferrer"
                            className="truncate font-medium text-slate-900 underline decoration-slate-300 underline-offset-4 transition hover:text-sky-700"
                            title={material.reference_url}
                          >
                            {sourceLinkLabel(material)}
                          </a>
                        ) : (
                          <div className="truncate font-medium text-slate-700">{material.quote_source || 'Source not stated'}</div>
                        )}
                        <div className="mt-2">
                          <span className={`inline-flex rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.16em] ${sourceTrustTone(material)}`}>
                            {sourceTrustLabel(material)}
                          </span>
                        </div>
                        {material.reference_url ? (
                          <a
                            href={material.reference_url}
                            target="_blank"
                            rel="noreferrer"
                            className="mt-2 inline-flex text-xs text-sky-700 underline underline-offset-2"
                          >
                            Open source
                          </a>
                        ) : (
                          <div className="mt-2 text-xs leading-5 text-slate-500">
                            {material.price_scope === 'historical_bulk'
                              ? 'Archive-derived bulk row without a stable public product page.'
                              : 'No public source URL stored for this row.'}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}

        {tab === 'steps' && (
          <div className="mt-5 overflow-hidden rounded-[28px] border border-slate-900/8 bg-white/58 backdrop-blur-xl">
            <div className="grid grid-cols-[minmax(0,1.3fr)_120px_120px_120px_minmax(0,1fr)] gap-3 border-b border-slate-900/8 bg-white/46 px-5 py-3 text-[11px] uppercase tracking-[0.18em] text-slate-500">
              <span>Step</span>
              <span className="text-right">Small</span>
              <span className="text-right">Medium</span>
              <span className="text-right">Large</span>
              <span>Note</span>
            </div>

            {loading ? (
              <div className="px-5 py-8 text-sm text-slate-500">Loading step rates...</div>
            ) : (
              <div className="max-h-[62vh] divide-y divide-slate-900/8 overflow-auto">
                {steps.map((step) => (
                  <div key={step.key} className="grid grid-cols-[minmax(0,1.3fr)_120px_120px_120px_minmax(0,1fr)] gap-3 px-5 py-3 text-sm">
                    <div className="font-semibold text-slate-950">{step.name}</div>
                    <div className="text-right font-mono text-slate-700">{step.cost_small != null ? `$${step.cost_small}/hr` : 'N/A'}</div>
                    <div className="text-right font-mono text-slate-700">{step.cost_medium != null ? `$${step.cost_medium}/hr` : 'N/A'}</div>
                    <div className="text-right font-mono text-slate-700">{step.cost_large != null ? `$${step.cost_large}/hr` : 'N/A'}</div>
                    <div className="text-slate-500">{step.note || 'N/A'}</div>
                  </div>
                ))}
              </div>
            )}
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

            <div className="grid gap-4 lg:grid-cols-2">
            {loading ? (
              <div className="text-sm text-slate-500">Loading templates...</div>
            ) : (
              templates.map((template) => (
                <article key={template.id} className="surface-ghost p-5">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="cp-subtle-label">{template.category || 'Template'}</div>
                      <h3 className="cp-heading-lg mt-2">{template.name}</h3>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <span className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] ${domainTone(template.catalyst_domain)}`}>
                        {domainLabel(template.catalyst_domain)}
                      </span>
                      <span className="cp-chip">{template.steps.length} steps</span>
                      {template.application_family ? <span className="cp-chip">{applicationLabel(template.application_family)}</span> : null}
                    </div>
                  </div>

                  <p className="mt-3 text-sm leading-7 text-slate-600">{template.description}</p>

                  {template.manufacturing_mode ? (
                    <div className="mt-3 text-xs text-slate-500">Mode: {template.manufacturing_mode}</div>
                  ) : null}

                  {template.example_catalysts.length > 0 && (
                    <div className="mt-4 flex flex-wrap gap-2">
                      {template.example_catalysts.map((value) => (
                        <span key={value} className="cp-chip">
                          {value}
                        </span>
                      ))}
                    </div>
                  )}

                  <div className="mt-4 flex flex-wrap gap-2">
                    {template.steps.map((step, index) => (
                      <span
                        key={`${template.id}-${step}-${index}`}
                        className="rounded-full border border-slate-200 bg-white/80 px-3 py-1 text-xs text-slate-600"
                      >
                        {step}
                      </span>
                    ))}
                  </div>

                  {template.preprocess?.length ? (
                    <div className="mt-4">
                      <div className="cp-subtle-label">Pre-treatment</div>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {template.preprocess.map((value) => <span key={value} className="cp-chip">{value}</span>)}
                      </div>
                    </div>
                  ) : null}

                  {template.postprocess?.length ? (
                    <div className="mt-4">
                      <div className="cp-subtle-label">Post-treatment</div>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {template.postprocess.map((value) => <span key={value} className="cp-chip">{value}</span>)}
                      </div>
                    </div>
                  ) : null}
                </article>
              ))
            )}
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
