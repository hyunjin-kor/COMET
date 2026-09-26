# 투고 준비 브리핑 — 2026-09-09

교수님 보고용 요약이다. 결정이 필요한 항목은 마지막 표에 모았다. 이 문서는 게재·투고 완료를 뜻하지 않는다.

## 한 줄 결론

COMET 소프트웨어 논문은 **Journal of Chemical Information and Modeling (JCIM)의 Application Note**로 투고할 것을 제안한다. SCIE Q1(IF 6.4, 2026 JCR 기준 제3자 집계)이며, 소프트웨어 자체를 심사하는 트랙이라 현재 원고 수준으로 통과 가능성이 가장 높다. 원고 초안은 [application-note-2026-09-09.md](application-note-2026-09-09.md), 커버레터 초안은 [cover-letter-jcim-2026-09-09.md](cover-letter-jcim-2026-09-09.md)에 있다.

## 왜 이 저널인가

| 검토 항목 | 확인 결과 |
|---|---|
| SCIE 조건 | 앞서 검토한 Digital Discovery와 ACS Engineering Au는 ESCI로 확인돼 제외. JCIM, ACS Sustainable Chem. & Eng., Green Chemistry가 SCIE Q1 후보 |
| 같은 유형의 게재 선례 | JCIM Application Note: AutoDock Vina 1.2.0 (2021, 피인용 7,000 이상), NEXTorch (2021, 화학공학 최적화 도구), AI4Green (2023), ProcessOptimizer (2025). 모두 소프트웨어가 본체인 6~8쪽 논문 |
| Application Note 요건 (ACS 공식 안내) | 초록·본문·그림 합계 5,000단어 이내, 그림 1개 이상, 제목에 소프트웨어 이름, 학술·상업 용도 모두 평가 또는 구매 가능, 가능하면 OS 무관, 심사자 익명 테스트 가능 |
| 현재 원고의 적합성 | 4,494 word-equivalent (초록 171 + 본문 2,523 + 그림 3개 1,800), 제목에 COMET 명시, 수치 49개가 동결 분석 파일에 연결됨 |
| 대안 | ACS Sustainable Chem. & Eng. (IF 7.6, Q1)은 일반 Article로 가능하나 "새 촉매 결론"을 요구받을 가능성이 커서, 암모니아 성능 자료를 결합한 뒤가 적기. Computers & Chemical Engineering (Q2)은 안전망 |

## 지금까지 확보한 것

- 소프트웨어: Windows 설치본, 브라우저 모드, 한/영 UI, GitHub 공개, Zenodo DOI, 자동 테스트 907개, CI에서 Windows 패키지 빌드·검사.
- 방법 검증: CatCost Table 6.2 세 사례를 발표 입력값 그대로 재현 (Pt/C 센트 일치, Ni/Al₂O₃ −6.65%, FCC +1.16%).
- 연구 분석: 30개 반응군·116개 후보의 가중치·가격 상태·후보 제거·점수 교란 민감도. 재현 명령과 입력 해시가 저장소에 있음.
- 독립 검토(2026-09-09): 코드와 원고 수식 대조, 참고문헌 Crossref 10건 확인, 발견한 불일치 10건 수정.
- 긴 원고(`manuscript_2026-09-08.md`, 본문 약 3,800단어, SI 12개 표)는 연구 기록으로 보존한다. Application Note는 그 요약판이다.

## 정직하게 남겨 둔 한계

- 산업 실측 원가와의 오차(MAPE)는 미산정이다. 조건이 맞는 공개 관측이 없기 때문이며, 0% 오차가 아니다.
- 라이브러리 후보의 성능·제조 준비도 점수는 저자가 부여한 선별 점수이지 측정값이 아니다.
- 환경 영향은 부분 산정이다 (평균 재료 반영률 62.79%, 116개 중 47개가 50% 미만).
- 외부 연구자 사용성 평가는 아직 없다.

## 교수님께서 정해 주셔야 할 것

| 항목 | 내용 | 필요한 이유 |
|---|---|---|
| 저자·소속·교신저자 | 이름, 순서, 소속, 연락처 | 원고와 커버레터의 빈칸 |
| 연구비·감사문 | 지원 과제와 기여 | Acknowledgments |
| 이해관계 | 회사와의 관계, 지분, 향후 구독 사업 | Competing interests 문구 |
| 상업 라이선스 문의처 | "commercial licenses are available on request from [ ]"에 들어갈 주체와 조건 | JCIM은 상업 용도도 평가 또는 구매가 가능해야 함. PolyForm NC라 이 문장이 필요 |
| 심사용 버전 | v1.4.0을 공개 릴리스로 태그할지, v1.3.24로 심사받을지 | 심사자가 직접 설치·실행함 |
| 데이터 권리 | 라이브러리에 남은 CatCost 워크북 유래 항목의 재배포 범위 | 공개 릴리스와 상업 사용 전 확인 필요 |
| 투고 시점 | Application Note를 먼저 낼지, 암모니아 LCOH 논문과 순서를 맞출지 | 두 논문이 서로 인용하는 구조 |

## 일정 추정

원고 확정 1~2주, 심사용 버전 정리 며칠, 투고 후 첫 결정까지 수 주에서 두세 달. JCIM의 공식 평균 심사 기간은 확인하지 못했다. 데스크 반려 위험은 범위 판정(원가·의사결정 도구가 JCIM 주류인 분자 모델링과 거리가 있음)이며, 커버레터에서 NEXTorch·AI4Green을 범위 선례로 든다.

## 확인 근거

- ACS JCIM 저자 안내: `researcher-resources.acs.org/publish/author_guidelines?coden=jcisd8` (2026-09-09, HTTP 200)
- 저널 색인·IF: journalsearches.com (제3자 집계). JCR 프로필의 Edition·JIF·분위로 최종 확인 필요
- 선례 서지: Crossref API로 확인. DOI는 커버레터와 [저널 검토 기록](journal-targets-2026-09-07.md)에 있음
