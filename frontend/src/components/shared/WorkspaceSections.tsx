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
  onPrevious: () => void;
  onNext: () => void;
  canGoPrevious: boolean;
  canGoNext: boolean;
};

export function WorkspaceSectionNav({
  sections,
  activeSectionId,
  activeIndex,
  onSelect,
  onPrevious,
  onNext,
  canGoPrevious,
  canGoNext,
}: WorkspaceSectionNavProps) {
  return (
    <section className="surface-card-soft px-4 py-4">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div className="cp-subtle-label">Workspace Steps</div>
          <div className="mt-2 text-sm text-slate-600">
            Step {activeIndex + 1} of {sections.length}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onPrevious}
            disabled={!canGoPrevious}
            className="cp-button-secondary px-3 py-2 text-xs disabled:opacity-35"
          >
            Back
          </button>
          <button
            onClick={onNext}
            disabled={!canGoNext}
            className="cp-button-secondary px-3 py-2 text-xs disabled:opacity-35"
          >
            Next
          </button>
        </div>
      </div>

      <div className="mt-4 grid gap-2 lg:grid-cols-[repeat(auto-fit,minmax(180px,1fr))]">
        {sections.map((section, index) => {
          const active = section.id === activeSectionId;
          return (
            <button
              key={section.id}
              onClick={() => onSelect(section.id)}
              className={`rounded-[18px] border px-3 py-3 text-left transition ${
                active
                  ? 'border-slate-950 bg-slate-950 text-white'
                  : 'border-slate-200 bg-white/82 text-slate-700 hover:border-slate-300'
              }`}
            >
              <div className={`text-[11px] font-semibold uppercase tracking-[0.18em] ${active ? 'text-slate-300' : 'text-slate-400'}`}>
                {String(index + 1).padStart(2, '0')}
              </div>
              <div className="mt-2 font-semibold">{section.label}</div>
              <div className={`mt-1 text-xs leading-5 ${active ? 'text-slate-300' : 'text-slate-500'}`}>
                {section.summary}
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}
