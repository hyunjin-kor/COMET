/* eslint-disable react-refresh/only-export-components */
import { useEffect, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';

export type WorkspaceSection = {
  id: string;
  label: string;
  summary: string;
};

export function useWorkspaceSections(sections: WorkspaceSection[], queryKey: string) {
  const [searchParams, setSearchParams] = useSearchParams();
  const sectionIds = useMemo(() => sections.map((section) => section.id), [sections]);
  const rawValue = searchParams.get(queryKey);
  const activeSectionId = rawValue && sectionIds.includes(rawValue) ? rawValue : sections[0]?.id ?? '';
  const activeIndex = Math.max(0, sectionIds.indexOf(activeSectionId));
  const activeSection = sections[activeIndex] ?? sections[0];

  useEffect(() => {
    if (typeof window === 'undefined') return;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [activeSectionId]);

  function setActiveSection(id: string) {
    if (!sectionIds.includes(id)) return;
    const next = new URLSearchParams(searchParams);
    next.set(queryKey, id);
    setSearchParams(next);
  }

  function goPrevious() {
    if (activeIndex <= 0) return;
    setActiveSection(sectionIds[activeIndex - 1]);
  }

  function goNext() {
    if (activeIndex >= sectionIds.length - 1) return;
    setActiveSection(sectionIds[activeIndex + 1]);
  }

  return {
    activeIndex,
    activeSection,
    activeSectionId,
    canGoPrevious: activeIndex > 0,
    canGoNext: activeIndex < sectionIds.length - 1,
    goNext,
    goPrevious,
    setActiveSection,
  };
}

type WorkspaceSectionNavProps = {
  sections: WorkspaceSection[];
  activeSectionId: string;
  activeIndex: number;
  onSelect: (id: string) => void;
  disabledSectionIds?: string[];
};

export function WorkspaceSectionNav({
  sections,
  activeSectionId,
  activeIndex,
  onSelect,
  disabledSectionIds = [],
}: WorkspaceSectionNavProps) {
  const activeSection = sections[activeIndex] ?? sections[0];

  return (
    <section className="surface-card-soft px-4 py-3">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="cp-subtle-label">Workflow</div>
          <div className="mt-2 text-sm font-medium text-slate-700">
            Step {activeIndex + 1} of {sections.length}
          </div>
        </div>
        <div className="text-xs leading-6 text-slate-500">
          {activeSection?.summary}
        </div>
      </div>

      <div className="mt-4 grid gap-2 lg:grid-cols-[repeat(auto-fit,minmax(150px,1fr))]">
        {sections.map((section, index) => {
          const active = section.id === activeSectionId;
          const disabled = !active && disabledSectionIds.includes(section.id);
          return (
            <button
              key={section.id}
              onClick={() => !disabled && onSelect(section.id)}
              disabled={disabled}
              className={`rounded-[16px] border px-3 py-3 text-left transition ${
                active
                  ? 'border-slate-950 bg-white text-slate-950 shadow-[0_6px_16px_rgba(15,23,42,0.06)]'
                  : disabled
                    ? 'cursor-not-allowed border-slate-200/80 bg-slate-50/70 text-slate-300'
                    : 'border-slate-200/90 bg-transparent text-slate-500 hover:border-slate-300 hover:bg-white/72'
              }`}
            >
              <div className="flex items-center gap-2">
                <span
                  className={`inline-flex h-6 min-w-6 items-center justify-center rounded-full px-1.5 text-[10px] font-semibold uppercase tracking-[0.18em] ${
                    active ? 'bg-slate-950 text-white' : 'bg-slate-100 text-slate-500'
                  }`}
                >
                  {String(index + 1).padStart(2, '0')}
                </span>
                <div className="font-semibold">{section.label}</div>
              </div>
              {active ? <div className="mt-2 text-xs leading-5 text-slate-500">{section.summary}</div> : null}
            </button>
          );
        })}
      </div>
    </section>
  );
}

type WorkspaceSectionFooterProps = {
  activeSection: WorkspaceSection;
  activeIndex: number;
  totalSections: number;
  onPrevious: () => void;
  onNext: () => void;
  canGoPrevious: boolean;
  canGoNext: boolean;
};

export function WorkspaceSectionFooter({
  activeSection,
  activeIndex,
  totalSections,
  onPrevious,
  onNext,
  canGoPrevious,
  canGoNext,
}: WorkspaceSectionFooterProps) {
  return (
    <section className="surface-card-soft px-4 py-3">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="cp-subtle-label">Continue</div>
          <div className="mt-2 font-semibold text-slate-950">{activeSection.label}</div>
          <div className="mt-1 text-xs leading-5 text-slate-500">
            Step {activeIndex + 1} of {totalSections}. {activeSection.summary}
          </div>
        </div>

        <div className="flex w-full gap-2 sm:w-auto">
          <button
            onClick={onPrevious}
            disabled={!canGoPrevious}
            className="cp-button-secondary flex-1 px-4 py-2.5 text-sm disabled:opacity-35 sm:flex-none"
          >
            Back
          </button>
          <button
            onClick={onNext}
            disabled={!canGoNext}
            className="cp-button-primary flex-1 px-4 py-2.5 text-sm disabled:opacity-35 sm:flex-none"
          >
            Next
          </button>
        </div>
      </div>
    </section>
  );
}
