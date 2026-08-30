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
  'Set the formulation or the electrode stack.': '조성 또는 전극 스택을 설정하세요.',
  'Set campaign scale and preparation steps.': '생산 규모와 제조 단계를 설정하세요.',
  'Run the estimate and open the result screen.': '계산을 실행하고 결과 화면을 여세요.',
  'Choose the catalyst class, define the formulation, set the preparation basis, then run the estimate.':
    '촉매 유형을 고르고, 조성을 정의하고, 제조 기준을 설정한 뒤 계산을 실행하세요.',
  'Choose the catalyst class, build the electrode stack, set the preparation basis, then run the estimate.':
    '촉매 유형을 고르고, 전극 스택을 구성하고, 제조 기준을 설정한 뒤 계산을 실행하세요.',
  'Catalyst type': '촉매 유형',
  'Choose the catalyst class before you build the formulation.': '조성을 구성하기 전에 촉매 유형을 먼저 선택하세요.',
  'Thermocatalyst': '열촉매',
  'Electrocatalyst': '전기촉매',
  'Selected': '선택됨',
  'Choose': '선택',
  'Use bulk composition, support share, and plant-style preparation steps in one estimate.':
    '벌크 조성, 담체 비율, 플랜트식 제조 공정을 하나의 계산으로 다룹니다.',
  'Best for supported metal catalysts, mixed oxides, zeolites, and reforming or cracking routes.':
    '담지 금속 촉매, 혼합 산화물, 제올라이트, 개질·크래킹 공정에 적합합니다.',
  'Split the electrode stack into catalyst powder, ionomer, membrane, and substrate.':
    '전극 스택을 촉매 분말, 아이오노머, 멤브레인, 기재로 나눠 계산합니다.',
  'Best for PEMFC, PEMWE, DMFC, and other electrode fabrication routes.':
    'PEMFC, PEMWE, DMFC 등 전극 제조 공정에 적합합니다.',
  'Switching the catalyst class does not advance to the next step.': '촉매 유형을 바꿔도 다음 단계로 자동 이동하지 않습니다.',
  'Define the catalyst formulation.': '촉매 조성을 정의하세요.',
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
  'Route building': '루트 구성',
  'Select every unit operation that applies': '해당하는 단위 공정을 모두 선택하세요',
  'You are assembling the full preparation route, not choosing a single option.': '단일 선택이 아니라 전체 제조 루트를 구성하는 화면입니다.',
  'Operation groups': '공정 그룹',
  'One group can hold several unit operations': '한 그룹에 여러 단위 공정이 들어갈 수 있습니다',
  'Current route': '현재 루트',
  'Campaign size': '캠페인 규모',
  'tons per campaign': '톤/캠페인',
  'Start from a standard method': '표준 제조법에서 시작',
  'methods': '개 제조법',
  'Loads the full unit-operation sequence for a named preparation method — co-precipitation, sol-gel, impregnation, zeolite synthesis and more. Operations stay editable afterward.':
    '공침, 졸-겔, 함침, 제올라이트 합성 등 이름 있는 제조법의 단위 공정 순서를 그대로 불러옵니다. 이후에도 자유롭게 수정할 수 있습니다.',
  'Mixing': '혼합',
  'Impregnation': '함침',
  'Reaction': '반응',
  'Drying': '건조',
  'Calcination': '소성',
  'Separation': '분리',
  'Forming': '성형',
  'Size Reduction': '분쇄',
  'Utilities': '유틸리티',
  'Select every operation your route uses in this group.': '이 그룹에서 루트에 쓰이는 공정을 모두 선택하세요.',
  'selected': '선택',
  'Run estimate': '계산 실행',
  'Running estimate': '계산 중',
  'The result screen opens separately and keeps this draft intact.': '결과 화면은 따로 열리며 이 초안은 그대로 유지됩니다.',
  'Calculation failed.': '계산에 실패했습니다.',
  'Saved estimates': '저장된 계산',
  'saved': '개 저장됨',
  'Named cases saved from the result screen. Load restores the composition, unit operations, and campaign size into this draft.':
    '결과 화면에서 이름을 붙여 저장한 케이스입니다. 불러오기는 조성·단위 공정·캠페인 규모를 이 초안으로 복원합니다.',
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
  'Steps': '단위 공정',
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
  'Cost build-up': '원가 내역',
  'Materials': '원재료',
  'Processing': '가공',
  'Evidence': '근거',
  'Preparation basis': '제조 기준',
  'Environmental': '환경 영향',

  // Benchmarks (Compare)
  'Overview': '개요',
  'Candidates': '후보',
  'Detail': '상세',
  'Choose family and ranking logic.': '반응군과 순위 기준을 선택하세요.',
  'Scan the current route stack.': '현재 후보들을 살펴보세요.',
  'Read the selected route deeply.': '선택한 루트를 자세히 읽어보세요.',
  'Screen published routes before you edit the cost case.': '원가 케이스를 편집하기 전에 발표된 공정 루트를 스크리닝하세요.',
  'Reaction family': '반응군',
  'Ranking profile': '순위 기준',
  'Balanced': '균형',
  'Cost-first': '비용 우선',
  'Evidence-first': '근거 우선',
  'Top route': '1위 루트',
  'Landed catalyst': '실효 촉매 단가',
  'Electrode layer': '전극층',
  'Literature bank': '반응군 문헌',
  'Published routes': '발표된 루트',
  'How do these routes compare right now?': '지금 이 루트들은 어떻게 비교될까요?',
  'candidates': '개 후보',
  'Selected reference route': '선택된 참조 루트',
  'Load into cost estimate': '원가 계산으로 불러오기',
  'Key evidence': '핵심 근거',
  'Family literature bank': '반응군 문헌 목록',
  'Screening basis': '스크리닝 기준',
  'Reference notes': '참고 노트',
  'Preprocess': '전처리',
  'Synthesis': '합성',
  'Postprocess': '후처리',
  'Route extras': '루트 부대비용',
  'Raw material stack': '원재료 구성',
  'Step-method operations': '스텝법(Step Method) 가공비',
  'Score': '점수',

  // Library
  'Material sources, step rates, and route templates in one place, with the quote basis behind every number.':
    '재료 출처, 단위 공정 요율, 제조법 템플릿을 한곳에 모았습니다 — 모든 숫자에 견적 근거가 붙어 있습니다.',
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
  'Scan the tracked metals, then inspect the evidence, quote age, and source quality for the selected metal.':
    '추적 중인 금속을 훑어보고, 선택한 금속의 근거·시세 경과·출처 품질을 확인하세요.',
  'Quote Status': '시세 상태',
  'Tracked metals': '추적 금속',
  'Live coverage': '실시간 커버리지',
  'Indexed & manual quotes': '지수·수동 시세',
  'Needs review': '점검 필요',
  'Refresh quotes': '시세 새로고침',
  'Price Coverage': '시세 커버리지',
  'Quote age': '시세 경과',

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
  'Simulated distribution': '시뮬레이션 분포',

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
  'Keep active metals and promoters explicit. A single support row auto-balances the formulation, and multiple support rows enable promoted-support formulations up to four total components.':
    '활성 금속과 조촉매는 명시적으로 입력합니다. 담체가 한 행이면 자동으로 잔량을 채우고, 여러 행이면 최대 4성분까지 조촉매화 담체 조성을 만들 수 있습니다.',
  'Promoted support is on. Enter each support wt% explicitly so the total formulation closes at 100 wt%.':
    '복합 담체 모드입니다. 전체 조성이 100 wt%가 되도록 각 담체의 wt%를 직접 입력하세요.',
  'Single-support mode stays auto-balanced. Add a second support to split the support bed explicitly.':
    '단일 담체 모드에서는 잔량이 자동으로 채워집니다. 담체를 나누려면 두 번째 담체를 추가하세요.',
  'Pick exchange-quoted metals or library-backed materials.': '시세 연동 금속 또는 라이브러리 기반 재료를 선택하세요.',
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
    '템플릿은 전처리, 코팅, 건조, 라미네이션, 브레이크인 단계를 추가합니다. 실험실 공정과 다르면 수정하세요.',
  'Pick the industrial steps that best approximate the synthesis route, then let campaign size set the scale basis.':
    '합성 경로에 가장 가까운 산업 단위 공정을 고르면, 캠페인 규모가 스케일 기준을 결정합니다.',
  'Saved thermal and electrochemical routes often include several operations from the same group.':
    '저장된 열·전기화학 루트는 같은 그룹의 공정을 여러 개 포함하는 경우가 많습니다.',
  'Add or remove operations until the route matches the actual lab or pilot procedure.':
    '실제 실험실 또는 파일럿 절차와 일치할 때까지 공정을 추가하거나 제거하세요.',
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
  'Loading live prices': '실시간 시세 불러오는 중',
  'Live prices unavailable': '실시간 시세 사용 불가',
  'Ready': '준비됨',
  'Recovery': '회수',

  // Result page - sections and labels
  'Headline price, scope, and active warnings.': '핵심 가격, 범위, 활성 경고를 봅니다.',
  'Route, cost structure, and campaign basis.': '공정 루트, 비용 구조, 캠페인 기준을 봅니다.',
  'Cradle-to-gate impact per kg of catalyst.': '촉매 kg당 크래들-투-게이트 영향을 봅니다.',
  'Resolved source rows, normalization, and links.': '확정된 출처 행, 정규화, 링크를 봅니다.',
  'Model Scope': '모델 범위',
  'Direct workspace route': '워크스페이스 직접 구성 루트',
  'Separate route logic from raw inputs.': '공정 로직과 원료 입력을 분리해서 봅니다.',
  'This surface is for campaign scale, selected preparation steps, route metadata, and the main cost split.':
    '이 화면은 캠페인 규모, 선택된 제조 단계, 루트 정보, 주요 비용 분할을 보여줍니다.',
  'Cost Structure': '비용 구조',
  'Materials versus processing': '원재료 대 가공비',
  'Cost breakdown': '원가 구성',
  'Materials, processing, and selling adjustments.': '원재료, 가공, 판매 조정 항목입니다.',
  'Preparation Steps': '제조 단계',
  'Reference baseline': '참조 기준',
  'No LCA data attached to this estimate.': '이 계산에는 LCA 데이터가 없습니다.',
  'Re-run the estimate to compute cradle-to-gate impact.': '크래들-투-게이트 영향을 계산하려면 계산을 다시 실행하세요.',
  'Cradle-to-gate impact per kg of catalyst': '촉매 kg당 크래들-투-게이트 영향',
  'Weighted-average over the wt% composition. Manufacturing-step emissions are not included in this version — only embodied material impact.':
    'wt% 조성 가중 평균입니다. 이 버전에는 제조 공정 배출은 포함되지 않고, 재료 내재 영향만 포함됩니다.',
  'Resolved material sources and normalization': '확정된 재료 출처와 정규화',
  'Each record shows raw quote, pack basis, normalization basis, and public link status when available.':
    '각 레코드는 원 견적, 포장 기준, 정규화 기준, 공개 링크 상태를 보여줍니다.',

  // Library sections
  'Source rows with quote and trust metadata.': '견적·신뢰도 메타데이터가 붙은 출처 행입니다.',
  'Hourly step rates by campaign scale.': '생산 규모별 단위 공정 시간당 요율입니다.',
  'Route templates and processing stages.': '공정 루트 템플릿과 처리 단계입니다.',

  // Uncertainty
  'Run the current case to reveal the price spread.': '현재 케이스를 실행해 가격 분포를 확인하세요.',
  'This result uses the same catalyst draft and preparation route from Cost Estimate.':
    '이 결과는 원가 계산과 동일한 촉매 초안과 제조 루트를 사용합니다.',

  // Compare
  'Public benchmark links in the active reaction family': '현재 반응군의 공개 벤치마크 링크 수',

  // Prices - status strip
  'Refreshing live quotes': '실시간 시세 새로고침 중',
  'Live quotes loaded': '실시간 시세 로드됨',
  'Stored pricing basis': '저장된 가격 기준',
  'Indexed and manual prices are available even before a live refresh.': '실시간 새로고침 전에도 지수·수동 가격을 사용할 수 있습니다.',
  'Refreshing now': '새로고침 중',
  'Metals with a stored price basis.': '가격 기준이 저장된 금속 수입니다.',
  'Stale quotes or low-confidence sources worth checking.': '오래된 시세이거나 신뢰도가 낮은 출처입니다.',
  'Metals backed by current live sources.': '현재 실시간 출처가 있는 금속입니다.',

  // Uncertainty - stat tiles
  'Baseline source': '기준값 출처',
  'Current estimate': '현재 계산값',
  'Average simulated value': '시뮬레이션 평균',
  '90% interval': '90% 구간',
  'Average outcome': '평균 결과',
  '50th percentile': '50번째 백분위',

  // Library - filters
  'Search by material, formula, or element': '재료명, 화학식, 원소로 검색',
  'Material rows visible under the current filters.': '현재 필터에서 표시되는 재료 행 수입니다.',

  // CapEx - inputs
  'Purchased equipment cost (USD)': '구매 장비비 (USD)',

  // Layout
  'Desktop Window': '데스크톱 창',

  // Unit operations (frontend step labels)
  'Dry Blender': '건식 블렌더',
  'Slurry Mixer': '슬러리 믹서',
  'Ionomer Ink Homogenization': '아이오노머 잉크 균질화',
  'Ultrasonic Dispersion': '초음파 분산',
  'Incipient Wetness': '초기습윤 함침',
  'CCM Coating Pass': 'CCM 코팅',
  'Simple Reactor': '단순 반응기',
  'Multistep Reactor': '다단 반응기',
  'Membrane Pretreatment': '멤브레인 전처리',
  'Substrate Pretreatment': '기재 전처리',
  'Ion-Exchange Conversion': '이온교환 전환',
  'Electrochemical Break-In': '전기화학 브레이크인',
  'Crystallizer': '결정화기',
  'Vacuum Tray Dryer': '진공 트레이 건조기',
  'Rotary Dryer 40-100 C': '회전식 건조기 40-100 C',
  'Rotary Dryer 100-300 C': '회전식 건조기 100-300 C',
  'Electrode Drying <100 C': '전극 건조 <100 C',
  'Spray Dryer': '분무 건조기',
  'Batch Kiln': '배치 소성로',
  'Continuous Kiln Direct': '연속 소성로(직접 가열)',
  'Continuous Kiln Indirect': '연속 소성로(간접 가열)',
  'Belt Vacuum Filter': '벨트 진공 여과기',
  'Plate and Frame Filter': '판틀형 여과기',
  'Rotary Vacuum Filter': '회전식 진공 여과기',
  'Extruder with Feeder': '압출기(피더 포함)',
  'Hot Press Lamination': '열간 프레스 라미네이션',
  'Ball Forming': '구형 성형',
  'Mill': '분쇄기',
  'Flare': '플레어',
  'NOx Scrubber': 'NOx 스크러버',

  // Scale labels
  'Small': '소형',
  'Medium': '중형',
  'Large': '대형',
  'small': '소형',
  'medium': '중형',
  'large': '대형',

  // Calculator - additional
  'Manual overrides': '수동 가격 입력',
  'Materials priced by hand instead of a tracked source.': '추적 출처 대신 직접 입력한 가격의 재료 수입니다.',
  'Optional spent catalyst value proxy for recovery-sensitive screening.': '회수 민감 스크리닝용 폐촉매 가치 프록시 (선택).',
  'No result for this catalyst class yet. Run the estimate once to populate this summary.':
    '이 촉매 유형의 결과가 아직 없습니다. 계산을 한 번 실행하면 요약이 채워집니다.',
  'Preparation steps': '제조 단계',
  'Add at least one active metal before continuing.': '계속하기 전에 활성 금속을 최소 한 개 추가하세요.',
  'Add at least one support before continuing.': '계속하기 전에 담체를 최소 한 개 추가하세요.',
  'Active metals and promoters must stay below 100 wt% so support remains positive.': '담체가 남도록 활성 금속과 조촉매 합계는 100 wt% 미만이어야 합니다.',
  'Enter a valid non-zero loading for the active portion of the formulation.': '조성의 활성 성분에 0이 아닌 유효한 담지량을 입력하세요.',
  'Select catalyst powder, ionomer, membrane, substrate / GDL, and a preparation template before continuing.':
    '계속하기 전에 촉매 분말, 아이오노머, 멤브레인, 기재/GDL, 제조 템플릿을 선택하세요.',
  'Select a preparation template': '제조 템플릿을 선택하세요',
  'Manual step selection': '수동 공정 선택',
  'Recovery proxy on': '회수 프록시 적용',
  'Recovery proxy off': '회수 프록시 미적용',
  'Indexed and manual rows stay usable before the next live refresh.': '다음 실시간 갱신 전에도 지수·수동 시세를 사용할 수 있습니다.',
  'Waiting for the local backend to publish live quotes.': '로컬 백엔드가 실시간 시세를 게시할 때까지 기다리는 중입니다.',
  'Choose at least one unit operation': '단위 공정을 최소 한 개 선택하세요',
  'Total components:': '전체 성분:',
  'Select active metal or precursor': '활성 금속 또는 전구체 선택',
  'Select promoter material': '조촉매 재료 선택',
  'Select support': '담체 선택',
  'Auto share': '자동 잔량',
  'Select a support record.': '담체 레코드를 선택하세요.',
  'Live': '실시간',
  'Indexed': '지수',
  'Manual': '수동',
  'Current case basis': '현재 케이스 기준',
  'Ready to run': '실행 준비 완료',
  'Campaign basis': '캠페인 기준',
  'Select a library record to lock pricing.': '라이브러리 레코드를 선택하면 가격이 고정됩니다.',
  'Choose a catalyst powder': '촉매 분말을 선택하세요',
  'Choose an ionomer': '아이오노머를 선택하세요',
  'Choose a membrane': '멤브레인을 선택하세요',
  'Choose a substrate or GDL': '기재 또는 GDL을 선택하세요',
  'Open source': '출처 열기',

  // Result - overview and rails
  'Mode': '모드',
  'Manual selection': '수동 선택',
  'No step labels stored': '저장된 공정 단계 없음',
  'Public route links stored': '공개 루트 링크 저장됨',
  'No route link stored': '저장된 루트 링크 없음',
  'Public links': '공개 링크',
  'Latest quote year': '최신 견적 연도',
  'Route references': '루트 참고문헌',
  'Margin': '마진',
  'General and administrative overhead': '일반관리비',
  'Selling, administrative, and R&D uplift': '판매·관리·연구개발 가산',
  'Overhead (G&A)': '간접비 (G&A)',
  'Sales, admin & R&D (S&ARD)': '판매·관리·연구개발비 (S&ARD)',
  'Reference-loaded': '참조 루트 적용됨',
  'Selling margin basis': '판매 마진 기준',
  'Price sources': '가격 출처',
  'Resolved rows with a public URL.': '공개 URL이 있는 확정 행 수입니다.',
  'Electrode Stack': '전극 스택',
  'Area-based electrocatalyst layer model': '면적 기준 전극층 모델',
  'Catalyst powder, ionomer, membrane, and substrate are costed on an active-area basis and displayed alongside the powder estimate.':
    '촉매 분말, 아이오노머, 멤브레인, 기재를 유효 면적 기준으로 원가 계산해 분말 기준 결과와 함께 보여줍니다.',
  'Per modeled layer': '모델링된 층 기준',
  'Catalyst loading': '촉매 담지량',
  'Dry catalyst loading': '건조 촉매 담지량',
  'Electrode total': '전극 합계',
  'For selected active area': '선택한 유효 면적 기준',
  'Cost per area': '면적당 원가',
  'Manufacturing line cost': '제조 라인 비용',
  'Spent catalyst value was included in the net-cost basis.': '폐촉매 가치가 순원가 기준에 포함되었습니다.',
  'This is an end-of-life recovery proxy. It is useful for early screening, but it does not yet model deactivation kinetics or regeneration frequency.':
    '수명 종료 시점 회수 프록시입니다. 초기 스크리닝에는 유용하지만 비활성화 속도나 재생 주기는 아직 모델링하지 않습니다.',
  'Gross metal value': '총 금속 가치',
  'Recovery cost': '회수 비용',
  'Reclaimed value': '회수 후 가치',
  'Loss basis': '손실 기준',
  'Use loss / refining loss': '사용 손실 / 정제 손실',
  'Named active inputs': '지정된 활성 성분 수',
  'Active-phase loading': '활성상 담지량',
  'Current support basis': '현재 담체 기준',
  'Selected preparation steps': '선택된 제조 단계',
  'Included': '포함됨',
  'Overhead + margin': '간접비 + 마진',
  'Template-driven route metadata is attached to this estimate.': '템플릿 기반 루트 정보가 이 계산에 첨부되어 있습니다.',
  'No saved result yet': '저장된 결과가 아직 없습니다',
  'Run an estimate from the cost estimate workspace first. The result then stays available for focused review.':
    '먼저 원가 계산 화면에서 계산을 실행하세요. 결과는 이 화면에서 계속 확인할 수 있습니다.',

  // Result - environmental
  'kg CO2-eq per kg of finished catalyst (IPCC GWP100a).': '완성 촉매 kg당 kg CO2-eq (IPCC GWP100a).',
  'Cumulative energy demand': '누적 에너지 수요',
  'Total primary energy per kg of finished catalyst.': '완성 촉매 kg당 총 1차 에너지.',
  'Composition coverage': '조성 커버리지',
  'Every component has a verified factor.': '모든 성분에 검증된 계수가 있습니다.',
  'Data source': '데이터 출처',
  'LCA notes': 'LCA 참고사항',
  'Component': '성분',
  'Role': '역할',
  'Reference': '참고문헌',
  'Open the source paper': '원문 논문 열기',

  // Result - sources
  'Resolved rows': '확정 행',
  'Material source rows used during estimate resolution.': '계산 시 사용된 재료 출처 행 수입니다.',
  'Rows that open a public source page.': '공개 출처 페이지가 열리는 행 수입니다.',
  'Historical rows without a stable public URL.': '안정적인 공개 URL이 없는 과거 행입니다.',
  'Per catalyst': '촉매 기준',
  'Loaded into catalyst': '촉매 내 담지 비율',
  'Unit price': '단가',
  'Share': '비중',
  'Of material cost stack': '재료비 중 비중',
  'Total material cost': '총 재료비',
  'CatCost-style step basis with backend escalation and selling adjustments applied in the calculation engine.':
    'CatCost 방식 스텝법 기준이며, 물가 보정과 판매 조정은 계산 엔진에서 적용됩니다.',
  'Source Records': '출처 기록',
  'Public literature source': '공개 문헌 출처',
  'Direct vendor source': '벤더 직접 출처',
  'Public source linked': '공개 출처 연결됨',
  'No public permalink': '공개 고정 링크 없음',
  'Link not stored': '저장된 링크 없음',
  'No quote year stored': '저장된 견적 연도 없음',
  'No resolved source rows — this estimate ran on manual price entries. Pick library materials in the cost estimate workspace to populate per-row provenance.':
    '확정된 출처 행이 없습니다 — 이 계산은 수동 가격 입력으로 실행되었습니다. 원가 계산 화면에서 라이브러리 재료를 선택하면 행별 출처가 채워집니다.',
  'in calculator': '계산기 적용가',
  'Pack Basis': '포장 기준',
  'Normalization': '정규화',
  'Pricing Basis': '가격 책정 기준',

  // Benchmarks - additional
  'Updated': '갱신',
  'Economics, evidence, route, and performance': '경제성·근거·공정·성능 종합',
  'Bias toward lowest current catalyst cost': '현재 촉매 원가가 낮은 쪽 우선',
  'Reward stronger source transparency and route reproducibility': '출처 투명성과 공정 재현성이 높은 쪽 우선',
  'Profiles change weighting only. Candidate records and source links stay fixed.': '기준은 가중치만 바꿉니다. 후보 기록과 출처 링크는 그대로 유지됩니다.',
  'Direct links supporting the selected route.': '선택한 루트를 뒷받침하는 직접 링크 수입니다.',
  'Higher-level references visible across the reaction family.': '반응군 전체에서 참조되는 상위 문헌 수입니다.',
  'How this route is framed in the benchmark set.': '이 루트가 벤치마크에서 다뤄지는 기준입니다.',
  'Current weighting logic for ranking.': '현재 순위 가중치 기준입니다.',
  'QA + activation + route overhead': '품질관리·활성화·루트 간접비',
  'Literature architecture proxy': '문헌 구조 프록시',
  'Engineering proxy': '공학적 프록시',
  'Market plus vendor anchor': '시장가 + 벤더가 기준',
  'Vendor stack anchor': '벤더 스택 기준',
  'Literature low-loading plus vendor stack': '문헌 저담지 + 벤더 스택',
  'Ru-based cost pressure relief': 'Ru 기반 원가 부담 완화',

  // Prices - metals and groups
  'Platinum Group Metals': '백금족 금속',
  'Precious Metals': '귀금속',
  'Industrial Metals': '산업용 금속',
  'Platinum': '백금',
  'Palladium': '팔라듐',
  'Rhodium': '로듐',
  'Ruthenium': '루테늄',
  'Iridium': '이리듐',
  'Gold': '금',
  'Silver': '은',
  'Nickel': '니켈',
  'Cobalt': '코발트',
  'Copper': '구리',
  'Aluminum': '알루미늄',
  'Molybdenum': '몰리브데넘',
  'Tungsten': '텅스텐',
  'Iron': '철',
  'Exchange-linked quote': '거래소 연동 시세',
  'Screen-scraped quote': '화면 수집 시세',
  'Supplier board': '공급사 고시가',
  'Indexed reference': '지수 참조',

  // Prices - inspector rails
  'Selected Quote': '선택된 시세',
  'Selected Metal': '선택된 금속',
  'Open trend view': '추세 보기',
  'Source Basis': '출처 기준',
  'Inspect trust before you read the number.': '숫자를 읽기 전에 신뢰도를 확인하세요.',
  'Acquisition': '수집 방식',
  'Confidence': '신뢰도',
  'Refresh target': '갱신 목표',
  'Expected refresh horizon for this source type.': '이 출처 유형의 예상 갱신 주기입니다.',
  'Trend Evidence': '추세 근거',
  'Period high': '기간 최고',
  'Period low': '기간 최저',
  'Direction': '방향',
  'Stored metal price series': '저장된 금속 가격 시계열',
  'Source Audit': '출처 감사',
  'Evidence tier': '근거 등급',
  'Transparency': '투명성',
  'Current': '현재',
  'Maximum observed value': '관측된 최고값',
  'Evidence Surface': '근거 요약',
  'Choose a metal to inspect its history.': '이력을 확인할 금속을 선택하세요.',
  'Age not stored': '경과 시간 미기재',
  'Indexed reference aligned with CatCost-style library pricing': 'CatCost 방식 라이브러리 가격과 정렬된 지수 참조',
  'Manual price input': '수동 가격 입력값',

  // Uncertainty - additional
  'No valid Cost Estimate draft is ready.': '유효한 원가 계산 초안이 없습니다.',
  'Build the catalyst case first, then come back here to quantify the price range around that same case.':
    '먼저 촉매 케이스를 구성한 뒤, 여기서 같은 케이스의 가격 범위를 정량화하세요.',
  'Open Cost Estimate': '원가 계산 열기',
  'Electrocatalyst stack': '전기촉매 스택',
  'Thermocatalyst formulation': '열촉매 조성',
  'No unit operations selected': '선택된 단위 공정 없음',
  'Campaign scale': '캠페인 규모',
  'Simulation count': '시뮬레이션 횟수',
  'Catalyst powder band': '촉매 분말 변동 폭',
  'Active metal band': '활성 금속 변동 폭',
  'Promoter band': '조촉매 변동 폭',
  'Support band': '담체 변동 폭',
  'Ionomer / membrane / GDL band': '아이오노머/멤브레인/GDL 변동 폭',
  'Campaign size band': '캠페인 규모 변동 폭',
  'Current Cost Estimate draft': '현재 원가 계산 초안',
  'No separate metal-only form is used here anymore.': '별도의 금속 전용 입력 양식은 더 이상 사용하지 않습니다.',
  'What moves': '변동 요소',
  'Catalyst + adjunct prices': '촉매 + 부자재 가격',
  'Active, promoter, and support prices': '활성 금속·조촉매·담체 가격',
  'The same case is re-run under sampled price and scale perturbations.': '같은 케이스를 가격·규모 섭동 샘플로 반복 계산합니다.',
  'Interpretation': '해석',
  'Estimate spread, not a new formulation': '새 조성이 아니라 추정 분포입니다',
  'Use this to read cost confidence around the existing route.': '기존 루트의 원가 신뢰 구간을 읽는 용도입니다.',
  'Running estimate range': '범위 계산 중',
  'Run estimate range': '범위 계산 실행',
  'Edit in Cost Estimate': '원가 계산에서 편집',
  'Case': '케이스',
  'P95 minus P5': 'P95 − P5',
  'Distribution spread': '분포 산포',
  'Percentile-weighted price spread': '백분위 기반 가격 분포',

  // Library - additional
  'Both': '공통',
  'General': '일반',
  'Fuel Cell': '연료전지',
  'Electrolyzer': '수전해',
  'Name (A-Z)': '이름순 (A-Z)',
  'Quote year (newest)': '견적 연도 (최신순)',
  'Quote year (oldest)': '견적 연도 (오래된순)',
  'In-calculator $/kg (high-low)': '계산기 단가 $/kg (높은순)',
  'In-calculator $/kg (low-high)': '계산기 단가 $/kg (낮은순)',
  'In-calculator $/lb (high-low)': '계산기 단가 $/lb (높은순)',
  'In-calculator $/lb (low-high)': '계산기 단가 $/lb (낮은순)',
  'Every visible row plugs into the calculator.': '표시된 모든 행을 계산기에서 사용할 수 있습니다.',
  'Rows that open a source page directly.': '출처 페이지가 바로 열리는 행 수입니다.',
  'Older bulk quotes without a stable public URL.': '안정적인 공개 URL이 없는 과거 벌크 견적입니다.',
  'Browse only': '열람 전용',
  'Public commodity source': '공개 상품 시세 출처',
  'Vendor product page': '벤더 제품 페이지',
  'Public link': '공개 링크',
  'Archive only (no public link)': '아카이브 전용 (공개 링크 없음)',
  'No link stored': '저장된 링크 없음',
  'Bulk commodity': '벌크 상품가',
  'Vendor pack price': '벤더 포장 단가',
  'Historical archive': '과거 아카이브',
  'This row can be picked in the calculator.': '이 행은 계산기에서 선택할 수 있습니다.',
  'Area-priced electrocatalyst row. Used in the electrode stack model, not the thermal mass-based calculator.':
    '면적 단가 전기촉매 행입니다. 질량 기준 열촉매 계산이 아니라 전극 스택 모델에서 사용됩니다.',
  'Volume-priced ionomer / dispersion row without density. Used directly in the electrode stack model.':
    '밀도 정보가 없는 부피 단가 아이오노머/분산액 행입니다. 전극 스택 모델에서 직접 사용됩니다.',
  'Reference row only. Price unit is not yet mapped to the calculator.': '참고용 행입니다. 가격 단위가 아직 계산기에 매핑되지 않았습니다.',
  'Source Detail': '출처 상세',
  'Choose a material row': '재료 행을 선택하세요',
  'Normalized to a per-mass basis for the cost engine.': '계산 엔진용 질량 기준으로 정규화된 값입니다.',
  'Source not stated': '출처 미기재',
  'Public URL available.': '공개 URL이 있습니다.',
  'Public URL not stored.': '공개 URL이 저장되어 있지 않습니다.',
  'Choose a row from the record list to inspect its source basis here.': '목록에서 행을 선택하면 출처 근거를 여기서 확인할 수 있습니다.',
  'Year unknown': '연도 미상',
  'Public URLs open directly when available. Historical bulk rows remain visible, but many do not have a stable public permalink.':
    '공개 URL은 가능하면 바로 열립니다. 과거 벌크 행도 계속 표시되지만, 안정적인 공개 링크가 없는 경우가 많습니다.',

  // CapEx - additional
  'Already-summed value of all purchased equipment. Use this when you have a vendor quote or a high-level scaling already done.':
    '이미 합산된 구매 장비비 총액입니다. 벤더 견적이 있거나 상위 수준 스케일링을 마쳤을 때 사용하세요.',
  'Each equipment line is scaled as Cost = base cost × (target size / base size)^exponent. Exponent 0.6 (six-tenths rule) is the usual default.':
    '각 장비 라인은 비용 = 기준 비용 × (목표 규모/기준 규모)^지수로 스케일링됩니다. 지수 0.6(0.6승 법칙)이 일반적인 기본값입니다.',
  'Live preview total:': '실시간 미리보기 합계:',
  'Name': '이름',
  'Base cost ($)': '기준 비용 ($)',
  'Base cost': '기준 비용',
  'Base size': '기준 규모',
  'Target size': '목표 규모',
  'Exponent': '지수',
  'Qty': '수량',
  'Scaled unit': '스케일 단가',
  'Line total': '라인 합계',
  'Remove': '제거',
  '+ Add equipment line': '+ 장비 라인 추가',
  'Layer annual OpEx on top': '연간 운영비 추가 계산',
  'Direct labor ($/yr)': '직접 인건비 ($/yr)',
  'Raw materials ($/yr)': '원재료비 ($/yr)',
  'Utilities ($/yr)': '유틸리티비 ($/yr)',
  'Calculating...': '계산 중...',
  'Calculate CapEx + OpEx': 'CapEx + OpEx 계산',
  'Calculate CapEx': 'CapEx 계산',
  'Total Capital Investment': '총 자본 투자비 (TCI)',
  'CatCost Ch.7 factored estimate': 'CatCost 7장 팩터 추정',
  'Purchased equipment': '구매 장비비',
  'Sum of equipment-line scaling, before factor expansion.': '팩터 적용 전 장비 라인 스케일링 합계입니다.',
  'Fixed Capital Investment': '고정 자본 투자비 (FCI)',
  'Working capital': '운전자본',
  'Equipment scaling audit': '장비 스케일링 검증',
  'Direct capital': '직접 자본비',
  'Inside the battery limits': '배터리 리밋 내부 항목',
  'Installation': '설치비',
  'Instrumentation & controls': '계장·제어',
  'Piping': '배관',
  'Electrical': '전기',
  'Buildings': '건물',
  'Yard improvements': '부지 정비',
  'Service facilities': '지원 설비',
  'Land': '부지',
  'Direct subtotal': '직접비 소계',
  'Sum of direct capital lines': '직접 자본비 항목 합계',
  'Indirect capital': '간접 자본비',
  'Engineering, contractor, contingency': '엔지니어링·시공·예비비',
  'Engineering & supervision': '엔지니어링·감리',
  'Construction': '건설비',
  'Legal': '법무비',
  "Contractor's fee": '시공사 수수료',
  'Contingency': '예비비',
  'Indirect subtotal': '간접비 소계',
  'Sum of indirect capital lines': '간접 자본비 항목 합계',
  'Carried separate from FCI': 'FCI와 별도로 계상',
  'FCI + working capital': 'FCI + 운전자본',
  'Annual OpEx': '연간 운영비',
  'Layered on top of CapEx using your direct-labor / raw-material / utilities inputs and CatCost Ch.7 factors.':
    '입력한 직접 인건비·원재료비·유틸리티비와 CatCost 7장 팩터로 CapEx 위에 얹어 계산했습니다.',
  'Direct operating': '직접 운영비',
  'Raw materials': '원재료',
  'Direct labor': '직접 인건비',
  'Supervisory & clerical': '감독·사무',
  'Laboratory': '실험실',
  'Maintenance & repair': '유지보수',
  'Operating supplies': '운전 소모품',
  'Fixed operating': '고정 운영비',
  'Local taxes': '지방세',
  'Insurance': '보험',
  'Rent': '임차료',
  'Plant overhead': '공장 간접비',
  'Fixed subtotal': '고정비 소계',
  'General expenses': '일반 경비',
  'Administration': '관리비',
  'Distribution & marketing': '유통·마케팅',
  'R&D': '연구개발',
  'G&A subtotal': '일반관리비 소계',
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
