/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState, type ReactNode } from 'react';

export type Lang = 'en' | 'ko';

const LANG_KEY = 'comet_lang';

// Keyed by the English source string; anything missing falls back to English,
// so partial coverage degrades gracefully. Data content (citations, evidence
// notes, candidate summaries) deliberately stays in its source language.
const KO: Record<string, string> = {
  // Navigation
  'Cost Estimate': '원가 계산',
  'Live Metal Prices': '실시간 금속 시세',
  'Literature Benchmarks': '문헌 벤치마크',
  'Estimate Range': '추정 범위',
  'Capital & OpEx': '설비·운영비',
  'Source Library': '자료 라이브러리',
  'Catalyst cost workspace': '촉매 원가 워크스페이스',
  'Evidence-first catalyst costing': '근거 우선 촉매 원가 산정',
  'Display unit': '표시 단위',
  'Language': '언어',
  'Collapse sidebar': '사이드바 접기',
  'Expand sidebar': '사이드바 펼치기',

  // Wizard chrome
  'Back': '이전',
  'Next': '다음',
  'Step': '단계',
  'of': '/',

  // Calculator sections
  'Catalyst Type': '촉매 유형',
  'Composition': '조성',
  'Preparation Method': '제조법',
  'Result': '결과',
  'Choose thermocatalyst or electrocatalyst.': '열촉매 또는 전기촉매를 선택하세요.',
  'Set recipe rows or the electrode stack.': '조성 또는 전극 스택을 설정하세요.',
  'Set campaign scale and preparation steps.': '생산 규모와 제조 스텝을 설정하세요.',
  'Run the estimate and open the result screen.': '계산을 실행하고 결과 화면을 여세요.',
  'Choose the workflow, define the recipe, set the preparation basis, then run the result.':
    '워크플로를 고르고, 조성을 정의하고, 제조 기준을 설정한 뒤 결과를 실행하세요.',
  'Choose the workflow, build the stack, set the preparation basis, then run the result.':
    '워크플로를 고르고, 전극 스택을 구성하고, 제조 기준을 설정한 뒤 결과를 실행하세요.',
  'Catalyst type': '촉매 유형',
  'Choose the workflow before you edit the recipe.': '조성을 편집하기 전에 워크플로를 선택하세요.',
  'Thermocatalyst': '열촉매',
  'Electrocatalyst': '전기촉매',
  'Selected': '선택됨',
  'Choose': '선택',
  'Use bulk composition, support share, and plant-style preparation steps in one estimate.':
    '벌크 조성, 담체 비율, 플랜트식 제조 스텝을 하나의 계산으로 다룹니다.',
  'Best for supported metal catalysts, mixed oxides, zeolites, and reforming or cracking routes.':
    '담지 금속 촉매, 혼합 산화물, 제올라이트, 개질·크래킹 공정에 적합합니다.',
  'Split the electrode stack into catalyst powder, ionomer, membrane, and substrate.':
    '전극 스택을 촉매 분말, 아이오노머, 멤브레인, 기재로 나눠 계산합니다.',
  'Best for PEMFC, PEMWE, DMFC, and other electrode-preparation workflows.':
    'PEMFC, PEMWE, DMFC 등 전극 제조 워크플로에 적합합니다.',
  'Switching the workflow does not auto-advance.': '워크플로를 바꿔도 자동으로 넘어가지 않습니다.',
  'Define the catalyst recipe.': '촉매 조성을 정의하세요.',
  'Active metals': '활성 금속',
  'Promoters': '조촉매',
  'Support': '담체',
  'Add active metal': '활성 금속 추가',
  'Add promoter': '조촉매 추가',
  'Add support': '담체 추가',
  'No promoters added yet.': '아직 추가된 조촉매가 없습니다.',
  'Remove row': '행 삭제',
  'Choose the preparation basis.': '제조 기준을 선택하세요.',
  'Preparation method': '제조법',
  'Selection mode': '선택 방식',
  'Choose all operations that apply': '해당하는 공정을 모두 선택',
  'This screen builds a full route, not a one-choice wizard.': '이 화면은 단일 선택이 아니라 전체 공정 루트를 구성합니다.',
  'Bucket logic': '그룹 구성',
  'One bucket can hold multiple steps': '한 그룹에 여러 스텝을 담을 수 있습니다',
  'Current route': '현재 루트',
  'Order size': '주문 규모',
  'tons per campaign': '톤/캠페인',
  'Quick-apply a saved route': '저장된 루트 바로 적용',
  'templates': '개 템플릿',
  'One click loads the full step chain for a named preparation method — co-precipitation, sol-gel, impregnation, zeolite synthesis and more. Steps stay editable afterward.':
    '공침, 졸-겔, 함침, 제올라이트 합성 등 이름 있는 제조법의 전체 스텝 체인을 클릭 한 번으로 불러옵니다. 이후에도 자유롭게 수정할 수 있습니다.',
  'Mixing': '혼합',
  'Impregnation': '함침',
  'Reaction': '반응',
  'Drying': '건조',
  'Calcination': '소성',
  'Separation': '분리',
  'Forming': '성형',
  'Size Reduction': '분쇄',
  'Utilities': '유틸리티',
  'Choose all operations that apply within this bucket.': '이 그룹에서 해당하는 공정을 모두 선택하세요.',
  'selected': '선택',
  'Run estimate': '계산 실행',
  'Running estimate': '계산 중',
  'The result screen opens separately and keeps this draft intact.': '결과 화면은 따로 열리며 이 초안은 그대로 유지됩니다.',
  'Calculation failed.': '계산에 실패했습니다.',
  'Saved estimates': '저장된 계산',
  'saved': '개 저장됨',
  'Named cases saved from the result screen. Load restores the composition, steps, and order size into this draft.':
    '결과 화면에서 이름을 붙여 저장한 케이스입니다. 불러오기는 조성·스텝·주문 규모를 이 초안으로 복원합니다.',
  'Load': '불러오기',
  'Delete': '삭제',
  'Working…': '처리 중…',
  'Restore this case into the draft': '이 케이스를 초안으로 복원',
  'Recovery scenario': '회수 시나리오',
  'Recovery off': '회수 미적용',
  'Refresh': '새로고침',
  'Refreshing': '새로고침 중',
  'Price basis': '가격 기준',
  'Status': '상태',
  'Current case': '현재 케이스',
  'Campaign': '캠페인',
  'Steps': '스텝',
  'Latest result': '최근 결과',
  'Open': '열기',
  'Pending': '대기',

  // Result page
  'The estimate, route basis, and evidence in one place — grouped for reading, separate from the editing workspace.':
    '계산 결과, 공정 기준, 근거를 한곳에 모았습니다 — 편집 화면과 분리된 읽기 전용 화면입니다.',
  'Export CSV': 'CSV 내보내기',
  'Back to cost estimate': '원가 계산으로 돌아가기',
  'Save estimate': '계산 저장',
  'Saving…': '저장 중…',
  'Saved ✓': '저장됨 ✓',
  'Retry save': '다시 저장',
  'Estimate name': '계산 이름',
  'Final result': '최종 결과',
  'Estimated selling price': '추정 판매가',
  'Estimated electrode cost': '추정 전극 원가',
  'Cost ledger': '원가 내역',
  'Materials': '원재료',
  'Processing': '가공',
  'Evidence': '근거',
  'Preparation basis': '제조 기준',
  'Environmental': '환경 영향',

  // Benchmarks (Compare)
  'Overview': '개요',
  'Candidates': '후보',
  'Detail': '상세',
  'Choose family and ranking logic.': '반응군과 랭킹 기준을 선택하세요.',
  'Scan the current route stack.': '현재 후보들을 살펴보세요.',
  'Read the selected route deeply.': '선택한 루트를 자세히 읽어보세요.',
  'Screen published routes before you edit the cost case.': '원가 케이스를 편집하기 전에 발표된 공정 루트를 스크리닝하세요.',
  'Benchmark family': '벤치마크 반응군',
  'Ranking profile': '랭킹 프로필',
  'Balanced': '균형',
  'Cost-first': '비용 우선',
  'Evidence-first': '근거 우선',
  'Top route': '1위 루트',
  'Landed catalyst': '실효 촉매 단가',
  'Electrode layer': '전극층',
  'Family bank': '반응군 문헌',
  'Published routes': '발표된 루트',
  'How do these routes compare right now?': '지금 이 루트들은 어떻게 비교될까요?',
  'candidates': '개 후보',
  'Selected reference route': '선택된 참조 루트',
  'Load into cost estimate': '원가 계산으로 불러오기',
  'Evidence anchors': '핵심 근거',
  'Family literature bank': '반응군 문헌 목록',
  'Screening basis': '스크리닝 기준',
  'Reference notes': '참고 노트',
  'Preprocess': '전처리',
  'Synthesis': '합성',
  'Postprocess': '후처리',
  'Route extras': '루트 부대비용',
  'Raw material stack': '원재료 구성',
  'Step-method operations': '스텝법 가공비',
  'Score': '점수',

  // Library
  'Material sources, step rates, and route templates in one place, with the quote basis behind every number.':
    '재료 출처, 스텝 요율, 공정 템플릿을 한곳에 모았습니다 — 모든 숫자에 견적 근거가 붙어 있습니다.',
  'Templates': '템플릿',
  'Search': '검색',
  'Category filter': '분류 필터',
  'All categories': '전체 분류',
  'Catalyst domain': '촉매 도메인',
  'All domains': '전체 도메인',
  'Application': '응용 분야',
  'All applications': '전체 응용',
  'Sort by': '정렬',
  'Filtered rows': '표시된 행',
  'Ready to cost': '계산 가능',
  'Public source links': '공개 출처 링크',
  'Archive-only': '아카이브 전용',
  'Quote': '견적',
  'In calculator': '계산기 적용가',
  'Source type': '출처 유형',
  'Quote year': '견적 연도',

  // Prices
  'Prices': '시세',
  'History': '이력',
  'Choose the metal price to inspect.': '확인할 금속 시세를 선택하세요.',
  'Read source quality, freshness, and trend.': '출처 품질, 최신성, 추세를 확인하세요.',
  'Scan the tracked symbols, then inspect evidence, freshness, and source quality for the selected metal.':
    '추적 중인 금속을 훑어보고, 선택한 금속의 근거·최신성·출처 품질을 확인하세요.',
  'Quote Status': '시세 상태',
  'Tracked symbols': '추적 금속',
  'Live coverage': '실시간 커버리지',
  'Fallback rows': '대체 행',
  'Needs review': '점검 필요',
  'Refresh quotes': '시세 새로고침',
  'Feed Coverage': '피드 커버리지',

  // Uncertainty
  'Current Case': '현재 케이스',
  'Use the same draft that feeds Cost Estimate.': '원가 계산과 같은 초안을 사용합니다.',
  'Run Monte Carlo around the same catalyst case.': '같은 촉매 케이스로 몬테카를로를 실행하세요.',
  'Monte Carlo range around the current Cost Estimate draft. Edit the catalyst case there, then run the range here.':
    '현재 원가 계산 초안을 중심으로 한 몬테카를로 범위입니다. 케이스는 원가 계산에서 편집하고, 범위는 여기서 실행하세요.',
  'Baseline': '기준값',
  'Mean': '평균',
  'Median': '중앙값',
  'Range width': '범위 폭',
  'Std dev': '표준편차',
  'Distribution sketch': '분포 스케치',

  // CapEx
  'Factor purchased equipment into FCI and TCI using Peters & Timmerhaus Lang factors, then optionally layer annual OpEx on top.':
    '구매 장비비를 Peters & Timmerhaus Lang 팩터로 FCI·TCI로 환산하고, 필요하면 연간 운영비까지 얹어 계산합니다.',
  'Lump-sum equipment cost': '장비비 일괄 입력',
  'Equipment list (six-tenths rule)': '장비 목록 (0.6승 법칙)',

  // Calculator - catalyst type section
  'Thermocatalyst keeps bulk composition and support balance together. Electrocatalyst separates catalyst powder, ionomer, membrane, and substrate.':
    '열촉매는 벌크 조성과 담체 균형을 함께 다루고, 전기촉매는 촉매 분말·아이오노머·멤브레인·기재를 분리해서 다룹니다.',
  'Selected:': '선택됨:',
  'Next: Composition →': '다음: 조성 →',

  // Calculator - composition section
  'Build the electrode stack.': '전극 스택을 구성하세요.',
  'Choose the stored material records first, then tune the geometric inputs used for area-based costing.':
    '저장된 재료 레코드를 먼저 고른 뒤, 면적 기준 원가 계산에 쓰이는 기하 입력값을 조정하세요.',
  'Keep active metals and promoters explicit. A single support row auto-balances the recipe, and multiple support rows enable promoted-support formulations up to four total components.':
    '활성 금속과 조촉매는 명시적으로 입력합니다. 담체가 한 행이면 자동으로 잔량을 채우고, 여러 행이면 최대 4성분까지 조촉매화 담체 조성을 만들 수 있습니다.',
  'Promoted support is on. Enter each support wt% explicitly so the total recipe closes at 100 wt%.':
    '복합 담체 모드입니다. 전체 조성이 100 wt%가 되도록 각 담체의 wt%를 직접 입력하세요.',
  'Single-support mode stays auto-balanced. Add a second support to split the support bed explicitly.':
    '단일 담체 모드에서는 잔량이 자동으로 채워집니다. 담체를 나누려면 두 번째 담체를 추가하세요.',
  'Pick live metal feeds or library-backed material identities.': '실시간 금속 시세 또는 라이브러리 기반 재료를 선택하세요.',
  'Optional promoter rows use the same DB-backed thermal material bank.': '조촉매 행도 같은 DB 기반 재료 뱅크를 사용합니다.',
  'At least one active metal is required.': '활성 금속이 최소 한 개 필요합니다.',

  // Calculator - electrode stack panel
  'Electrode stack': '전극 스택',
  'Set the stack first, then price the preparation method.': '스택을 먼저 구성한 뒤 제조법 원가를 계산하세요.',
  'Catalyst powder, ionomer, membrane, and substrate each keep their own source record.':
    '촉매 분말, 아이오노머, 멤브레인, 기재는 각자 출처 레코드를 유지합니다.',
  'Defaults prefer higher-confidence literature or sourced vendor rows when they exist.':
    '기본값은 신뢰도가 높은 문헌 또는 출처가 있는 벤더 행을 우선합니다.',
  'Application family': '응용 분야',
  'Material stack': '재료 스택',
  'Catalyst powder': '촉매 분말',
  'Ionomer': '아이오노머',
  'Membrane': '멤브레인',
  'Substrate / GDL': '기재 / GDL',
  'Electrode geometry': '전극 기하',
  'Active area': '유효 면적',
  'Selected preparation template': '선택된 제조 템플릿',
  'Pre-treatment': '전처리',
  'Synthesis / coating': '합성 / 코팅',
  'Post-treatment': '후처리',
  'Loaded reference baseline': '불러온 참조 기준',

  // Calculator - preparation method section
  'Templates add pretreatment, coating, drying, lamination, and break-in steps. Adjust them if the lab route differs.':
    '템플릿은 전처리, 코팅, 건조, 라미네이션, 브레이크인 스텝을 추가합니다. 실험실 공정과 다르면 수정하세요.',
  'Pick the industrial steps that best approximate the synthesis route, then let campaign size set the scale basis.':
    '합성 공정에 가장 가까운 산업 스텝을 고르면, 캠페인 규모가 스케일 기준을 결정합니다.',
  'Saved thermal and electrochemical templates often stack several operations inside the same bucket.':
    '저장된 열·전기화학 템플릿은 같은 그룹 안에 여러 공정을 함께 담는 경우가 많습니다.',
  'Add or remove operations until the route matches the actual lab or pilot workflow.':
    '실제 실험실 또는 파일럿 워크플로와 일치할 때까지 공정을 추가하거나 제거하세요.',
  'Recovery on': '회수 적용',
  'Optional spent catalyst value proxy': '폐촉매 가치 프록시 (선택)',
  'Use this when the catalyst contains recoverable metal and end-of-life value matters to the screening decision.':
    '촉매에 회수 가능한 금속이 포함되어 있고, 수명 종료 시 가치가 스크리닝 판단에 중요할 때 사용하세요.',
  'Current engine includes support loss, reactor-type loss, refining loss, and recovery cost. Full deactivation and regeneration-cycle modeling is not yet included.':
    '현재 엔진은 담체 손실, 반응기 유형 손실, 정제 손실, 회수 비용을 포함합니다. 비활성화·재생 사이클 모델링은 아직 포함되지 않습니다.',
  'Reactor type': '반응기 유형',
  'Fixed bed': '고정층',
  'Slurry': '슬러리',
  'Bulk density': '벌크 밀도',
  'Screening use': '스크리닝 용도',
  'Best for Pt, Pd, Rh, Ru, Ir, Ni, and Co routes where salvage value changes the commercial basis.':
    '회수 가치가 상업성 판단을 바꾸는 Pt, Pd, Rh, Ru, Ir, Ni, Co 공정에 적합합니다.',

  // Calculator - status rail
  'Loading live feed': '실시간 피드 로딩 중',
  'Live feed unavailable': '실시간 피드 사용 불가',
  'Ready': '준비됨',
  'Recovery': '회수',
  'Family': '반응군',

  // Result page - sections and labels
  'Headline price, scope, and active warnings.': '핵심 가격, 범위, 활성 경고를 봅니다.',
  'Route, cost structure, and campaign basis.': '공정 루트, 비용 구조, 캠페인 기준을 봅니다.',
  'Cradle-to-gate impact per kg of catalyst.': '촉매 kg당 크래들-투-게이트 영향을 봅니다.',
  'Resolved source rows, normalization, and links.': '확정된 출처 행, 정규화, 링크를 봅니다.',
  'Model Scope': '모델 범위',
  'Direct workspace route': '워크스페이스 직접 구성 루트',
  'Separate route logic from raw inputs.': '공정 로직과 원료 입력을 분리해서 봅니다.',
  'This surface is for campaign scale, selected preparation steps, route metadata, and the main cost split.':
    '이 화면은 캠페인 규모, 선택된 제조 스텝, 루트 메타데이터, 주요 비용 분할을 보여줍니다.',
  'Cost Structure': '비용 구조',
  'Materials versus processing': '원재료 대 가공비',
  'Breakdown wheel': '비용 분해 차트',
  'Materials, processing, and selling adjustments.': '원재료, 가공, 판매 조정 항목입니다.',
  'Preparation Steps': '제조 스텝',
  'Reference baseline': '참조 기준',
  'No LCA data attached to this estimate.': '이 계산에는 LCA 데이터가 없습니다.',
  'Re-run the estimate to compute cradle-to-gate impact.': '크래들-투-게이트 영향을 계산하려면 계산을 다시 실행하세요.',
  'Cradle-to-gate impact per kg of catalyst': '촉매 kg당 크래들-투-게이트 영향',
  'Weighted-average over the wt% composition. Manufacturing-step emissions are not included in this version — only embodied material impact.':
    'wt% 조성 가중 평균입니다. 이 버전에는 제조 스텝 배출은 포함되지 않고, 재료 내재 영향만 포함됩니다.',
  'Resolved material sources and normalization': '확정된 재료 출처와 정규화',
  'Each record shows raw quote, pack basis, normalization basis, and public link status when available.':
    '각 레코드는 원 견적, 포장 기준, 정규화 기준, 공개 링크 상태를 보여줍니다.',

  // Library sections
  'Source rows with quote and trust metadata.': '견적·신뢰도 메타데이터가 붙은 출처 행입니다.',
  'Hourly step rates by campaign scale.': '캠페인 규모별 시간당 스텝 요율입니다.',
  'Route templates and processing stages.': '공정 루트 템플릿과 처리 단계입니다.',

  // Uncertainty
  'Run the current case to reveal the price spread.': '현재 케이스를 실행해 가격 분포를 확인하세요.',
  'This result uses the same catalyst draft and preparation route from Cost Estimate.':
    '이 결과는 원가 계산과 동일한 촉매 초안과 제조 루트를 사용합니다.',

  // Compare
  'Public benchmark links in the active family': '현재 반응군의 공개 벤치마크 링크 수',

  // Prices - status strip
  'Refreshing live quotes': '실시간 시세 새로고침 중',
  'Live quotes loaded': '실시간 시세 로드됨',
  'Stored pricing basis': '저장된 가격 기준',
  'Indexed and manual prices are available even before a live refresh.': '실시간 새로고침 전에도 지수·수동 가격을 사용할 수 있습니다.',
  'Refreshing now': '새로고침 중',
  'Metals visible in the desktop feed.': '피드에 표시되는 금속 수입니다.',
  'Freshness or confidence flags worth checking.': '최신성 또는 신뢰도 확인이 필요한 행입니다.',
  'Symbols backed by current live sources.': '현재 실시간 출처가 있는 금속입니다.',

  // Uncertainty - stat tiles
  'Baseline source': '기준값 출처',
  'Current estimate': '현재 계산값',
  'Average simulated value': '시뮬레이션 평균',
  '90% interval': '90% 구간',
  'Average outcome': '평균 결과',
  '50th percentile': '50번째 백분위',

  // Library - filters
  'Search materials, formulas, or symbols': '재료, 화학식, 심볼 검색',
  'Material rows visible under the current filters.': '현재 필터에서 표시되는 재료 행 수입니다.',

  // CapEx - inputs
  'Purchased equipment cost (USD)': '구매 장비비 (USD)',
};

type LangContextValue = {
  lang: Lang;
  toggle: () => void;
  t: (text: string) => string;
};

const LangContext = createContext<LangContextValue | null>(null);

export function LangProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>(() => {
    try {
      const stored = window.localStorage.getItem(LANG_KEY);
      return stored === 'ko' ? 'ko' : 'en';
    } catch {
      return 'en';
    }
  });

  function toggle() {
    setLang((previous) => {
      const next: Lang = previous === 'en' ? 'ko' : 'en';
      try {
        window.localStorage.setItem(LANG_KEY, next);
      } catch {
        // storage unavailable - keep the in-memory choice
      }
      return next;
    });
  }

  const t = (text: string) => (lang === 'ko' ? (KO[text] ?? text) : text);

  return <LangContext.Provider value={{ lang, toggle, t }}>{children}</LangContext.Provider>;
}

export function useLang() {
  const ctx = useContext(LangContext);
  if (!ctx) throw new Error('useLang requires LangProvider');
  return ctx;
}
