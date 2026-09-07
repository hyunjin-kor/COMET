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

좌석·기간은 현재 명시적인 수동 계약 정보다. 고객 셀프 가입, 카드 자동 결제, 세금계산서, SSO/MFA, 이메일 기반 비밀번호 복구 및 판매 가격은 포함하지 않았다. 실제 운영 전에는 권리·기관 규정·회사 계약·TLS/프록시·OS 접근 권한·백업 보관 정책을 담당자가 확인해야 한다.

## 계정 화면과 요청 한도

브라우저 계정 화면에서 구독 상태·이용 종료 시각, 최근200개 저장 계산의 조회/JSON 내보내기, 비밀번호 변경, 로그아웃을 제공한다. 저장 결과는 당시 값을 읽으며 구독 만료 후 새로 계산하지 않는다. 저장된 전체 항목은 API의 검색·조회에서도 접근할 수 있다. 계정별 복구 백업에는 최근200개 제한이 없다.

브라우저 새로고침·계정 변경·로그아웃 때 저장하지 않은 조성과 결과는 지운다. 언어·단위·가격 기준 설정은 보존한다. 다른 탭의 계정 변경/로그아웃도 감지해 연구 화면을 닫는다. 각 요청의 `X-Comet-Account`는 화면의 계정이 쿠키의 서버 계정과 같은지 확인하는 용도이며, 자료 소유자를 선택하는 권한이 아니다. 다르면409로 거절한다. 이미 진행 중인 이전 계정의 응답도 화면에서 폐기한다. 인증 정보는 브라우저 저장소에 넣지 않는다.

초기 단일 작업자 운영 기준은 **계정당 분당60회, 회사당 분당240회**의 계산/쓰기 요청과 **계정당 분당10회**의 추정 범위 요청이다. 추정 범위는 기존 API와 같이 요청당 최대10,000회 표본을 사용한다. 분 단위 고정 구간의 원자적 DB 카운터로 확인하며, 허용된 요청은 본문 검증/계산 실패도 한도에 포함한다. 경계 시각에는 연속한 두 구간의 요청이 몰릴 수 있으므로 부하 평탄화나 용량 보장으로 해석하지 않는다. 서버 프로세스 내 동시 계산/쓰기는2개이고 한도를 넘으면429 및 `Retry-After`를 반환한다. 저장 조회/내보내기는 이 계산 한도에 포함하지 않는다. 여러 작업자를 사용하면 동시 제한은 작업자별로 늘어나므로 검증 없이 작업자 수를 늘리지 않는다. 실제 사용량 가격제나 청구 단위는 정하지 않았다.

hosted 화면의 시세 새로고침은 저장한 시세를 다시 읽는다. 외부 수집·예약 수집은 활성화하지 않는다. 데스크톱 모드는 기존 외부 시세 흐름을 유지한다.

## 백업·복구

`scripts/backup_hosted.py`는 제어 DB와 모든 계정 DB를 SQLite backup API로 복사하고, 각 파일의 SHA-256 및 `PRAGMA quick_check`를 확인한다. 고객 정보가 포함된 비공개 백업이므로 소스·웹 정적 폴더·GitHub에 넣으면 안 된다. 실제 경로는 호스트 관리자가 승인한 소스 밖 절대 경로를 사용한다.

```text
python scripts/backup_hosted.py backup NEW_PRIVATE_BACKUP_DIRECTORY --service-stopped
python scripts/backup_hosted.py verify PRIVATE_BACKUP_DIRECTORY
python scripts/backup_hosted.py restore PRIVATE_BACKUP_DIRECTORY NEW_PRIVATE_RECOVERY_DIRECTORY --service-stopped
```

백업/복구 전에 서비스 작업자와 운영자 쓰기를 모두 중지해야 한다. `--service-stopped`는 운영자의 확인이며 자동으로 프로세스 정지를 검증하거나 DB 여러 개의 동일 시점 스냅샷을 보장하지 않는다. SQLite 파일별 일관성을 여러 DB 간 일관성으로 과장하지 않는다. 실패한 부분 복사본은 지우지 않고 보존하며, 정상 검증된 manifest가 없는 복사본으로 운영하지 않는다.

복구는 **존재하지 않는 새 디렉터리**에만 가능하다. 기존 서비스 DB를 덮어쓰거나 자동으로 설정을 전환하지 않는다. 경로 이탈, 중복 항목, 누락 계정 DB, 해시 불일치를 거절한다. 복구된 모든 로그인 세션을 무효화해 과거 쿠키를 되살리지 않는다. 원본 계정/계약/비밀번호 해시 자체는 백업 시점으로 돌아가므로 실제 전환 전에는 최근 계약·계정 중지·비밀번호 재설정·관측 자료 변경을 대조하고 필요한 복구 이후 변경을 다시 적용해야 한다.

검증된 복구 폴더에서 실제 샘플 조회·내보내기와 회사/계정 접근 경계를 확인한 뒤 운영자가 설정 전환을 결정한다. 복구 보고서는 원본 manifest와 복구 후 DB 해시를 기록한다. 해시는 우발적 손상 탐지이며 서명된 진위 증명은 아니다. 호스트 설정·인증서·번들 데이터는 이 DB 백업에 포함되지 않는다. 접근 권한, 디스크 암호화, 별도 매체, 보관 기간, 정기 복구 훈련의 주기 및 실제 복구 시간 목표는 운영자가 정해야 한다. Windows 디렉터리 mode만으로 ACL을 보장하지 않는다.

로그인의 비밀번호 검사와 세션 발급은 제어 DB의 동일한 쓰기 트랜잭션에서 처리한다. 비밀번호 재설정·계정 중지와 경합할 때 이미 검사를 마친 옛 비밀번호로 새 세션이 뒤늦게 살아나는 것을 막는다. 로그인 중에는 제어 DB의 다른 쓰기가 잠시 대기할 수 있다. 합성 동시 실행 테스트 결과는 [논문 작성 전 감사](../audit/prepublication-run-2026-09-08.md)에 남겼다.
