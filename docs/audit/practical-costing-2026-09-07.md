# Practical costing update — 2026-09-07

User authorization: “다음 개선 사항들 다 진행해”. Same branch `autonomous/2026-09-06`, same [PR112](https://github.com/hyunjin-kor/COMET/pull/112), no merge/release.

## Verified starting point

Clean `ff6155e1b56d1e400438fbcb5a4f40dea06e605e`. Prior completed run: local **710 passed / 459.11 s**, final-head CI **710 passed / 594.59 s**, frontend passed; Windows build + smoke **197.81 s**. These are previous-run results, not a new test run. Table 6.2: Pt/C 27.3695 USD/lb (27.37 rounded); Ni/Al2O3 19.2206 (−6.65%); FCC at 67 short ton/day 2.4380 (+1.16%). Evidence: `validation-submission-2026-09-07.md` and its check JSON.

## Tasks

| ID | 상태 | 커밋 | 근거 명령 출력 요약 | 메모 |
|---|---|---|---|---|
| P01 | 진행 | — | 검증 전 | 계산 범위 표시와 확인된 결과 문구·가격 줄바꿈 수정 |
| P02 | 대기 | — | 검증 전 | 실제 생산 속도 및 생산 기간 근거 |
| P03 | 대기 | — | 검증 전 | 전구체 함량·순도·수율 및 소모재 투입량 |
| P04 | 대기 | — | 검증 전 | 저장한 추정의 동일 조건 비교 |
| P05 | 대기 | — | 검증 전 | 로컬 구매 근거와 실제 비용 관측 |
| P06 | 대기 | — | 검증 전 | 전체 검증·화면·로그·동일 PR 최종화 |

## Conservative assumptions

- Optional effective production rate is expressed in **short ton/day**, consistent with the existing engine. Production duration includes the existing cleaning allowance and is derived, avoiding conflicting independent duration inputs.
- Recipe mode requires explicit purchased-precursor price and retained-component fraction, purity, and retention yield. The same component cannot also apply a precursor markup. Solvent/wash additions are net purchased consumables per kg of finished catalyst; no automatic recovery credit or invented default consumption.
- New production/recipe inputs apply to thermal manufacture. Electrode manufacturing scenarios retain their published area-based boundary.
- Purchase evidence is user supplied local metadata, not an independently verified source. Actual observations only produce an error when matching requirements are satisfied; unmatched records remain visible with reasons.
- No paid data, new factors, or new processing rates; old frozen paper outputs preserved.

## Verification and numerical effects

Pending implementation.
