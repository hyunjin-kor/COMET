# COMET 논문 자료

현재 원고는 **COMET: Traceable catalyst manufacturing cost and environmental screening with decision-robustness analysis**다. COMET의 가격 상태·제조 원가·환경 반영률·추천 안정성 분석을 연구의 중심으로 다루며, CatCost 등 선행 방법은 사용한 근거와 공개 방법의 재현 검증에 인용한다.

- [현재 원고](manuscript_2026-09-08.md)
- [현재 Supporting Information](si_2026-09-08.md)
- [예상 리뷰 질문과 답변](reviewer_prep_2026-09-08.md)
- [연구 기여와 선행 방법의 경계](../research-contribution.md)
- [수치 주장과 근거 요약](research-claims-2026-09-08.ko.md)
- [주 분석 결과·입력 해시](submission-2026-09-08/reproduction_manifest_2026-09-08.json)
- [통제 사례](controlled-2026-09-08/README.md)
- [가격·가중치 및 구조적 민감도](robustness-2026-09-08/README.md)

현재 문서를 재생성하고 수치 키·고정 산출물 해시를 확인한다.

```bash
python scripts/build_submission_manuscript.py --date 2026-09-08 --directory docs/paper/submission-2026-09-08 --robustness docs/paper/robustness-2026-09-08
python scripts/build_submission_manuscript.py --date 2026-09-08 --directory docs/paper/submission-2026-09-08 --robustness docs/paper/robustness-2026-09-08 --check
```

이전 날짜의 초안·SI·분석 디렉터리는 과거 실행 기록이다. 그 문구와 입력·수치·그림 해시는 보존하며, 이전 문서를 정확히 렌더링하려면 해당 실행 시점의 생성기 커밋을 사용한다. 현재 설명으로 바꾸기 위해 과거 수치 패키지를 덮어쓰지 않는다.

저자·소속·지원 과제·이해관계와 투고 저널은 실제 당사자의 최종 확인이 남아 있다. 이 자료는 게재·투고 완료를 뜻하지 않는다.
