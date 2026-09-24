# 결정 기록

제안서만으로는 모호했던 부분에 대한 결정이다. 교안을 쓸 때 제안서보다 이 파일을 우선한다.
새 결정이 생기면 아래에 번호를 이어 붙인다. 결정을 뒤집을 때는 지우지 말고 ~~취소선~~과 날짜를 남긴다.

## 확정 (2026-09-24, 0회차 세션)

| # | 주제 | 결정 |
|---|---|---|
| D1 | 선택 실습 | `opt-pdf`(PDF 공문 요약 앱), `opt-voice`(음성 입력 민원 접수) 두 항목으로 나눈다 |
| D2 | 섹션 순서 | 학습목표(3줄 이내) → 개념 블록(10분) → 실습/활동 → 정리 → 완성본 가져오기. 자주 하는 실수는 실습 안에 둔다 |
| D3 | 교시 type | lessons.json에 `type`(lab/activity) 필드를 둔다. verify.py가 type별로 다른 필수 섹션을 검사한다. activity: d1-p1, d2-p4, d2-p5, d2-p6, d2-p7 |
| D4 | JSON 누적 | 교시 JSON은 교시 끝 시점의 **전체** 워크플로우다. 체인은 `d1-p6 → d1-p7 → d2-p1 → d2-p2`. `d1-p3`은 독립 연습용, `d1-p2`는 독립 복습용 |
| D5 | 시연 파일 | d1-p1 시연은 최종 완성본 `workflows/d2-p2.json`을 쓴다 |
| D6 | 프로젝트 예시 | d2-p5·d2-p6은 설계서 예시 "현장점검 보고 앱"을 예시 완성본으로 둔다(`d2-p5` 기본형 → `d2-p6` 확장형) |
| D7 | 자격 증명 | JSON에 실제 자격 증명 ID를 남기지 않는다(verify 검사). 모든 Import 안내에 "자격 증명 다시 연결" 단계를 필수로 넣는다 |
| D8 | 강사 서버 | ~~강사 시연 n8n 서버는 `https://kitae104.work`로 가정한다~~ → **폐기(2026-09-24)**: 강사 시연도 n8n Cloud 사용(Q1) |
| D9 | Webhook 경로 | 수강생마다 자기 n8n을 쓰므로 Webhook 경로 충돌은 고려하지 않는다 |
| D10 | 용어 | n8n·AI Studio 화면 표기는 영문 UI 그대로. "웹훅"은 예외 없이 금지한다. 첫 등장 때 "외부 앱이 n8n을 부르는 주소" 같은 쉬운 말로 풀이한다 |
| D11 | 상태 조회 | d2-p2의 처리 상태 조회는 조회용 GET Webhook(접수번호 → 시트 검색 → Respond to Webhook)으로 만든다. 이 Webhook의 CORS 설정도 d2-p2 체크리스트에 넣는다 |
| D12 | 접수번호 | `YYYY-MMDD-NNN`(예 `2026-0922-017`, 제안서 그림 1과 같음) |
| D13 | 웹 교안 디자인 | 기존 kitae-n8n 사이트(https://kitae-n8n.vercel.app)에 맞춘다 → 기존 `style.css`·`lecture.css`를 그대로 복사해 쓰고, 이 과정 부품은 `lesson.css`에 추가 |
| D14 | 인쇄 | `scripts/build.py`로 전 교시를 합친 `print/textbook.html`을 만들고, 브라우저 "PDF로 인쇄"로 출력한다. 교시별 페이지 나눔, 흑백 인쇄 대비(색으로만 구분 금지) |
| D15 | 제안서 그림 | PNG는 사용자가 `assets/proposal/`에 넣는다 |
| D16 | 플랜 B | AI Studio 차단 대비 플랜 B(n8n Form 또는 Gemini 캔버스)는 d1-p4에 부록 박스로 둔다 |
| D17 | 3일 확대안 | 범위에서 제외한다 |
| D18 | 개인정보 검사 | 허용 목록 방식(`docs/sample-data.md`). 홍길동, 010-1234-5678, 김기태(강사명)는 허용한다. 인명 검사는 인명 필드(성명·신청자·민원인·담당자·**이름**)로 한정하되, `이름` 앞에 서비스·파일·노드·시트·워크플로우·앱이 붙으면 제외한다(오탐 방지로 탭·폴더·문서도 제외 추가). Gmail 수신 주소는 `{본인 이메일}` 자리표시를 허용한다 |

## 확정 (2026-09-24, 0회차 세션 — 추가 답변)

| # | 주제 | 결정 |
|---|---|---|
| D19 | hook 범위 | `lessons/`에 더해 `workflows/`, `prompts/` 수정 시에도 verify.py 자동 실행 |
| D20 | HTML 규칙 | 섹션 표지는 이 과정의 `data-section` 규칙을 유지하고, CSS·캡처 방식(`figure.capture`, `apply_captures.py`)·UI 라벨(`code.val`)·박스(`.note`)는 기존 교안 관례를 따른다 |
| D21 | 배포 | 이 저장소를 **별도 사이트**로 배포한다(기존 사이트와는 링크로 연결). 루트 `index.html`은 `scripts/build.py`가 생성. 링크는 `.html`까지 쓴다 |
| D22 | 수강생·강사 n8n (Q1) | 수강생은 **n8n Cloud 무료 체험(개인 계정)**, 강사 시연도 n8n Cloud. 버전 고정이 불가하므로 최신 버전 기준으로 쓰고 **교육 1주 전 당시 안정 버전 기준으로 캡처·JSON 최종 확인** |
| D23 | Gemini (Q2) | 기존 교안과 같은 구성: `AI 안내문 작성`(Basic LLM Chain) + `Google Gemini Chat Model` 하위 노드. 자격 증명은 Gemini API 키(Google Gemini(PaLM) API) |
| D24 | 기존 교안 (Q3·Q4) | 원본 https://github.com/kitae104/PublicFlow (사이트 https://kitae-n8n.vercel.app). 텍스트 자료만 `docs/legacy/PublicFlow/`에 복사(캡처 PNG·기관 공문 PDF 제외) |
| D25 | 데이터 약속 | 앱 필드·시트 열·응답 키·Webhook 경로는 `docs/data-contract.md`로 관리한다. 초안은 기존 교안 폼 필드(이름·연락처·이메일·종류(생활/음식물/대형)·상세설명)를 이어받고, 해당 교시 세션에서 확정한다 |
| D26 | 작업 상태 | `todo → drafting → review → instructor-check → done`. JSON Import 실행·프롬프트 시험·캡처는 강사 수동 확인(`docs/instructor-checklist.md`) 후에만 done |
| D28 | d1-p3 호출 시험 (1회차) | 코드 없이 POST+CORS를 시험할 수 없으므로(fact-check F52) d1-p3은 **GET Webhook을 브라우저 주소창으로 호출**해 응답을 확인한다. Allowed Origins(CORS)는 체크리스트 1번으로 **설정만** 하고 개념을 설명하며, 실제 CORS 확인은 **d1-p6에서 AI Studio 앱으로** 한다. 경로 `hello`(GET) |
| D29 | 활성화 → Publish (1회차) | n8n 2.0부터 활성화 토글이 `Publish` 버튼으로 바뀜(F22). glossary 표준 표기를 `Publish`로 바꾸고 "활성화"를 금지 표기로 둔다. 설정을 바꾸면 다시 Publish(F53) |
| D30 | Gemini 모델 (2회차) | 기존 교안의 `models/gemini-2.5-flash`는 신규 사용자에게 제한됨(F42). 교안·JSON은 `models/gemini-3.8-flash`(대안 `models/gemini-3.5-flash-lite`), Google Gemini Chat Model typeVersion 1.1. Cloud 화면에 `Use Gateway credits`가 보이면 `Use my own credential`을 고른다(D23 유지) |
| D31 | Gmail 안내 문구 (2회차) | Gmail 노드는 `options.appendAttribution: false`로 n8n 안내 문구를 끈다(F66) |
| D32 | d1-p2 설계 (2회차) | 50분 복습은 **모두 같은 완성본(d1-p2.json)을 Import**해 자격 증명 연결 → 실행 → 표현식·샘플 값 고쳐 보기로 진행(수준 차이 흡수). 캘린더는 d2-p1에서 다루므로 제외. 샘플 민원은 가상 데이터(홍길동·010-1234-5678)로 교체 |
| D33 | AI Studio 계정 (3회차) | AI Studio는 **만 18세 이상 나이 확인된 개인 구글 계정** 기준(F2). 기관(Workspace) 계정은 막힐 수 있음 → 준비물 안내(d1-p1)에 반영 |
| D34 | 앱 주소 자리 (3회차) | d1-p4 프롬프트에서 코드 맨 위에 빈 `WEBHOOK_URL` 상수를 미리 만든다. d1-p6에서는 그 자리에 Production URL을 넣으라는 짧은 요청만 한다. 보내는 JSON 키는 data-contract의 한글 키 |
| D35 | CORS 값 (3회차) | 앱이 n8n을 부르는 origin은 공식 문서로 확인되지 않음(F4) → 수업에서는 Allowed Origins `*` 유지. 좁히려면 n8n 실행 기록의 `headers.origin` 값을 쓴다(d2-p3). 브라우저 호출이 막히면 "n8n 호출을 서버 쪽 코드에서 하도록 바꿔줘"(F80) |
| D36 | 이름이 겹치는 버튼 (3회차) | AI Studio에도 `Publish`(앱 게시)가 있다. n8n `Publish`와 혼동되므로 d1 교시에서는 AI Studio Publish를 언급하지 않고, d2-p3에서 구분해 다룬다 |
| D37 | d1-p5 오류 연습 (4회차) | 오류 연습은 AI에게 "일부러 오류를 만들어 줘(고치지 말고)"라고 요청해 만든다. AI가 거절·자가 수정하면 교안 속 연습용 오류 문구로 복사·붙여 넣기 동작만 연습(보내지 않음). AI Studio 화면 세부(F8·F77·F82·F84~F86)는 문서에 없어 조건부 문장 + FACT-CHECK로 쓴다 |
| D38 | F4 시험 방식 (4회차) | Chrome 확장이 연결되지 않아 Claude가 직접 시험할 수 없음 → 강사용 시험 키트(`docs/instructor-kit/f4-test.md`, `f4-test-workflow.json`)로 강사가 시험. d1-p6은 "Test URL로 먼저 시험 → 성공하면 Production URL" 순서로 쓰고, 브라우저 호출이 막힐 때의 우회(서버 쪽 호출 요청, F80)를 교안에 둔다. F4 결과를 받으면 확정 |
| D39 | 연동 ① 구조 (4회차) | d1-p6 워크플로우는 `민원 받기`(Webhook POST `minwon`) → `민원 정리`(Edit Fields, body 값 꺼내기) → `시트에 기록`(d1-p2 노드 복사). 시트는 d1-p2의 `민원대장 연습`/`시트1`을 이어 쓰고 날짜 열은 기존 교안의 `등록일`. 접수번호·처리상태 열은 d1-p7에서 추가. d1-p6에는 Respond to Webhook이 없으므로 앱의 접수번호 자리는 비어 보인다(7교시에서 채움) |
| D40 | 시간대 (5회차) | n8n `$now`의 기본 시간대가 미국이라(F100) 모든 워크플로우 JSON에 `settings.timezone: Asia/Seoul`. d1-p2·d1-p6 JSON에 소급 적용(교안 문장 변화 없음). 처음부터 만드는 워크플로우는 d1-p7 첫 단계에서 시간대 설정. verify.py가 검사 |
| D41 | 접수번호 순번 (5회차) | `오늘 접수 조회`(Get Row(s), 필터 없음, Always Output Data) → `접수번호 만들기`(Edit Fields JSON 모드, Execute Once)에서 "접수번호가 오늘 날짜로 시작하는 줄 수 + 1". 날짜 형식 차이·빈 항목 문제 회피(F93·F101). 시트 기록은 Cell Format RAW로 접수번호가 날짜로 바뀌지 않게. 동시 접수 시 번호 중복 가능 — 수업에서는 안내만 |
| D27 | 작성 순서 | 시간표 순서가 아닌 `lessons.json`의 `authoring_order`를 따른다(d1-p1·opt-voice가 d2-p2.json을 참조하므로) |

## 미결정

교안 작성 중 새로 생기는 모호한 점은 **추측하지 않고 그 교시 세션에서 사용자에게 개별 질문**한 뒤 여기에 기록한다.

| # | 주제 | 상태 | 영향 교시 |
|---|---|---|---|
| Q5 | 담당자 배정을 If 두 갈래(기존 교안: 생활 / 그 외)로 할지 세 갈래로 할지 | d2-p2 세션에서 질문 | d2-p2 |
| Q6 | 현장점검 앱의 사진 전송 포함 여부 | d2-p6 세션에서 질문 | d2-p5, d2-p6 |
| Q7 | 조회 쿼리 키를 한글(`접수번호`)로 둘지 | d2-p2 세션에서 강사 시험 결과로 결정 | d2-p2 |
