# 구독 계정 운영 절차

이 문서는 구현된 수동 B2B 계약 관리 절차다. 실제 회사 계약·고객·결제 수단·가격은 정하지 않았다. 무료 데이터 원칙을 유지하며, 현재 상업용 데이터 권리 심사가 통과하지 않아 실제 서비스 시작은 차단된다. [계정 구조](hosted-architecture.ko.md)와 [권리 등록부](rights-register-2026-09-07.md)를 먼저 확인한다.

## 구독과 자료 접근

| 서버 판정 | 신규 계산·자료 변경 | 기존 계산 조회·내보내기 | 로그인·비밀번호 변경 |
|---|---|---|---|
| 대기: 계약 미기록 또는 시작 전 | 제한 | 허용 | 허용 |
| 활성: 명시한 시작 시각 이상, 종료 시각 미만 | 허용 | 허용 | 허용 |
| 만료: 종료 시각 이상 | 제한 | 허용 | 허용 |
| 해지: 운영자가 revoked로 기록 | 제한 | 허용 | 허용 |
| 보안상 계정 중지 | 제한 | 제한 | 제한 |

일반 구독 만료로 연구 자료를 삭제하거나 잠그지 않는다. 저장 결과, 관측 항목, 재료·설비 및 시세 조회와 내보내기는 유지한다. 제조법별 가공비 계산과 반응군별 추천 분석은 새로운 연산이므로 활성 구독이 필요하다. 보안상 계정 중지는 별개이며 모든 세션을 취소한다. 실제 계약의 보관·반환 기간은 당사자가 정해야 한다.

활성 계정 수가 좌석 수를 넘지 않도록 서버 DB에서 원자적으로 확인한다. 같은 회사의 계정도 연구 자료를 자동 공유하지 않는다. 계약 갱신은 기존 로그인 세션에 즉시 적용하며, 클라이언트가 보낸 회사 ID나 구독 상태로 권한을 부여하지 않는다.

## 운영자 명령

인터넷 관리자 API 대신 서버의 비공개 터미널에서 `python scripts/manage_hosted.py --help`로 명령을 확인한다. 회사·계정 식별자는 명령 결과의 실제 값을 사용한다. 아래 대문자 값은 설명용 자리표시자이며 실행하거나 실제 계약으로 기록한 값이 아니다.

```text
python scripts/manage_hosted.py --actor OPERATOR_ID initialize
python scripts/manage_hosted.py --actor OPERATOR_ID organization COMPANY_NAME
python scripts/manage_hosted.py --actor OPERATOR_ID subscription --organization ORGANIZATION_ID --status active --starts-at CONTRACT_START_WITH_UTC_OFFSET --ends-at CONTRACT_END_WITH_UTC_OFFSET --seats CONTRACT_SEATS --reason contract_recorded
python scripts/manage_hosted.py --actor OPERATOR_ID account --organization ORGANIZATION_ID --username LOGIN_NAME
python scripts/manage_hosted.py status
python scripts/manage_hosted.py audit --limit 50
python scripts/manage_hosted.py --actor OPERATOR_ID disable-account ACCOUNT_ID
python scripts/manage_hosted.py --actor OPERATOR_ID reset-password ACCOUNT_ID
```

`HOSTED_MODE`, HTTPS `HOSTED_ORIGIN`, 소스 밖 절대 경로인 `HOSTED_STORAGE_DIR`, `ALLOWED_HOSTS`와 검토한 `HOSTED_RIGHTS_MANIFEST`가 필요하다. 실제 운영 시작은 초기화·권리 검증을 통과해야 한다. 기존 C08 회사 테이블은 열을 추가해 보존하고 대기 상태로 전환한다. 기존 항목에 계약 기간을 추정해 넣지 않는다.

운영자 식별자 `--actor`는 모든 관리 변경에 필요하다. 계정 생성·비밀번호 재설정은 대화형 터미널의 숨김 입력으로 두 번 확인한다. 비밀번호를 명령행, 환경 변수, 파일, 로그에 넣는 옵션은 제공하지 않는다. 초기 비밀번호 전달과 본인 확인은 승인된 비공개 절차로 수행해야 하며 이 실행에서는 실제 계정을 발급하지 않았다. 비밀번호 변경·재설정은 기존의 모든 로그인 세션을 취소한다. 사용자의 변경에는 현재 비밀번호가 필요하다.

계약 변경의 사유는 `contract_recorded`, `contract_renewed`, `customer_request`, `security_review`, `correction` 중 선택한다. 좌석을 이미 활성화된 계정 수보다 낮추면 거절하므로 대상 계정을 운영자가 먼저 검토해야 한다. 자동으로 임의의 계정을 중지하지 않는다. 결제 성공을 추정하거나, 이 명령을 결제 증빙으로 취급하지 않는다.

## 감사 기록과 운영 한계

감사 항목은 운영자/계정 식별자, 시각, 동작, 대상과 계약 상태·기간·좌석 변경 전후를 기록한다. 계정 생성·활성화/중지, 로그인/로그아웃, 비밀번호 변경/재설정도 기록한다. 비밀번호·세션 토큰·촉매 조성·계산 본문은 감사 항목에 넣지 않는다. 조회는 최대500항목이다. 이 DB는 OS 관리자가 수정할 수 있으므로 불변 외부 감사 원장이라고 주장하지 않는다.

좌석·기간은 현재 명시적인 수동 계약 정보다. 고객 셀프 가입, 카드 자동 결제, 세금계산서, SSO/MFA, 이메일 기반 비밀번호 복구 및 판매 가격은 포함하지 않았다. 계정 화면, 계산 사용량 제한과 백업 복구 검증은 C10에서 연결한다. 실제 운영 전에는 권리·기관 규정·회사 계약·TLS/프록시·OS 접근 권한·백업 보관 정책을 담당자가 확인해야 한다.
