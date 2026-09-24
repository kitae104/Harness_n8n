# 진행 기록 (progress)

세션마다 **맨 아래에** 기록을 하나씩 추가한다. 이전 기록은 고치지 않는다(잘못된 내용은 다음 기록에서 바로잡음).
다음 세션은 마지막 기록의 "다음 할 일"과 "미해결 문제"부터 읽는다.

## 기록 양식

```markdown
## N회차 — YYYY-MM-DD — {교시 id} {교시 제목}

### 한 일
- …

### 검증 결과
- verify.py {id}: PASS/FAIL (실패 n / 경고 n) — 남은 경고 요약
- learner-reviewer: 막힘 n / 헷갈림 n / 사소 n → 반영 n
- fact-checker: 확인 n / 수정 필요 n / 확인 불가 n
- status: todo → …
- 커밋: {해시}

### 다음 할 일
- …

### 미해결 문제
- … (사용자 질문 필요, 강사 수동 확인 대기 등)
```

---

## 0회차 — 2026-09-24 — 하네스 구축(교안 작성 없음)

### 한 일
- 제안서 PDF → `docs/proposal.md` 변환(표 복원, 오탈자 교정)
- `lessons.json`: 14교시 + 선택 실습 2개(opt-pdf, opt-voice), type(lab/activity), workflow 체인, authoring_order, legacy_refs
- 규칙 문서: `writing-guide.md`, `glossary.md`, `sample-data.md`, `data-contract.md`, `decisions.md`(D1~D27), `fact-check.md`(F1~F48 모두 미확인), `instructor-checklist.md`
- 기존 교안(kitae104/PublicFlow `de82744`) 텍스트 자료를 `docs/legacy/PublicFlow/`에 복사, CSS·캡처 도구 이식
- 도구: `verify.py`, `test_verify.py`, `build.py`, `apply_captures.py`, `hook_verify.py` + `.claude/settings.json`(PostToolUse hook)
- 서브에이전트: `learner-reviewer`, `fact-checker`
- 교안 템플릿 2개(lab/activity), `workflows/_template.json` 견본

### 검증 결과
- 템플릿: `verify.py --file docs/templates/lesson-lab.html --type lab --base lessons` PASS, activity 템플릿 PASS, `_template.json` PASS
- `test_verify.py`: 샘플 32개(규칙 위반 → FAIL 22, 오탐 확인 → PASS 9, 작성 전 링크 → WARN 1) 기대 결과와 모두 일치
- hook: 세션 중 추가한 설정이 **바로 적용됨** — `lessons/`에 임시 파일을 Write하자 verify 결과가 자동 전달됨(임시 파일 삭제함)
- `verify.py d1-p1`: 산출물 없음 + 참조 JSON(d2-p2) 없음으로 FAIL(정상)
- `build.py`: index.html, print/textbook.html 생성(교시 0개)

### 다음 할 일
1. `fact-checker` 1차 실행: 첫 교시(d1-p3)와 공통 항목(F20~F27, F46~F48) 먼저
2. `authoring_order` 첫 교시 **d1-p3**(Webhook 이해와 실습) 작성
3. 제안서 그림 PNG가 `assets/proposal/`에 들어오면 교안에서 참조
4. **교육 1주 전: n8n Cloud 당시 안정 버전 기준으로 캡처·JSON 최종 확인**(D22, instructor-checklist)

### 미해결 문제
- 제안서 그림 PNG(그림 0·1·2·7) 전달 대기 → `assets/proposal/`
- decisions.md Q5~Q7(담당자 분기 방식, 현장점검 사진, 조회 쿼리 키)은 해당 교시 세션에서 사용자에게 질문
- 표기 차이: 기존 교안은 "자격증명", 이 과정은 "자격 증명"(glossary). 기존 교안 문장을 가져올 때 verify가 잡아냄
- Webhook CORS 옵션 JSON 키(`options.allowedOrigins`)와 Import 메뉴 위치는 미확인(F47, F48)

## 1회차 — 2026-09-24 — d1-p3 Webhook 이해와 실습

### 한 일
- fact-checker 1차 실행(n8n 2.40.6 소스·docs.n8n.io 대조): F20~F27·F41·F46~F48 확인, F49~F54 신규. **활성화 토글 → `Publish` 버튼(n8n 2.0~)** 등 3건 수정 필요 판정
- D29: glossary 표준 표기 `활성화` → `Publish`로 변경(금지 표기로 전환), 템플릿·가이드·명세·체크리스트 반영
- D28(사용자 결정): d1-p3은 **GET Webhook을 주소창으로 호출**, CORS는 설정만 하고 실제 확인은 d1-p6 앱에서. data-contract `hello`를 GET으로 확정, d1-p3 objectives·acceptance 수정, d1-p6 acceptance에 CORS 실제 확인 추가
- verify.py: data-contract의 HTTP 방식(GET/POST)까지 비교하도록 보강(회귀 샘플 33번 추가)
- 산출물: `workflows/d1-p3.json`(Webhook 2.1 GET hello → Respond to Webhook 1.5, CORS *), `lessons/d1-p3.html`(개념 표·10단계 실습·체크리스트·퀴즈 3·Import)
- learner-reviewer 리뷰(`docs/reviews/d1-p3-learner.md`): 막힘 2 / 헷갈림 11 / 사소 5 → **18건 모두 반영**(6단계 분리, Response Body 지우기, 2분 제한 대비 순서, 이름 철자 실수 박스, Import 전 Unpublish 안내 등)
- data-contract에 d1-p6 결정용 메모 추가: 기존 교안 부챗살 구조·`$json.body` 풀기 노드·`등록일` 열 이름
- fact-checker가 넘긴 강사 직접 시험 8건을 instructor-checklist로 이동

### 검증 결과
- verify.py d1-p3: PASS (실패 0 / 경고 3 — 작성 전 교시 링크 2, FACT-CHECK 7곳: F55~F57, F59~F62)
- test_verify.py: 33개 불일치 0
- learner-reviewer: 막힘 2 / 헷갈림 11 / 사소 5 → 반영 18
- fact-checker: 확인 13 / 수정 필요 3 / 확인 불가 2
- status: todo → **instructor-check**
- 커밋: (이 기록과 같은 커밋)

### 다음 할 일
1. **강사 확인(d1-p3)**: `docs/instructor-checklist.md`의 d1-p3 행과 "fact-checker가 넘긴 직접 시험 항목" — 특히 F55~F63 화면 표기. 결과를 받으면 FACT-CHECK 주석 제거 → status `done`
2. 다음 교시: `authoring_order`상 **d1-p2**(n8n 핵심 복습). 시작 전 fact-checker로 F42(Gemini 구성·typeVersion)·F46 확인
3. 교육 1주 전: n8n Cloud 당시 안정 버전 기준 캡처·JSON 최종 확인

### 미해결 문제
- **`.claude/agents/`의 learner-reviewer·fact-checker는 이번 세션에서 에이전트 종류로 등록되지 않았음**(세션 중 추가한 정의는 재시작 후 로드되는 것으로 보임). 이번에는 범용 에이전트에 정의 파일을 읽혀 대신 실행함 → **재시작 후 `learner-reviewer`/`fact-checker` 이름으로 호출되는지 확인**
- 제안서 그림 PNG 전달 대기(`assets/proposal/`)
- F41(Import 시 자격 증명 처리)은 문서 근거 없음 → 강사 시험 필요. 그전까지 Import 안내는 "경고 표시가 뜬 노드를 열어 내 자격 증명 선택"으로 씀
- 기존 교안(legacy) day1/08.html의 "활성화 스위치" 서술은 현재 화면과 다름(참조 시 주의, legacy는 수정하지 않음)

## 2회차 — 2026-09-24 — d1-p2 n8n 핵심 복습 (1회차와 같은 세션, 사용자 요청으로 이어서 진행)

### 한 일
- fact-checker 2차: F42 갱신, F64~F72 신규. **`gemini-2.5-flash`는 신규 사용자 제한 → `models/gemini-3.8-flash`**(D30), Gmail `appendAttribution:false`(D31), Cloud의 `Use Gateway credits` 대신 `Use my own credential`
- 설계(D32): 모두 같은 완성본을 Import → 자격 증명 연결 → 실행 → 표현식·샘플 값 고쳐 보기. 캘린더는 d2-p1로 미룸
- 산출물: `workflows/d1-p2.json`(기존 day1-06 기반, 노드 6개, 가상 데이터로 교체, Gemini Chat Model 1.1), `lessons/d1-p2.html`(개념 표 2개, 실습 11단계 — 10단계까지 필수, 빨간 노드 대처 박스, 퀴즈 2, Import)
- learner-reviewer: 막힘 2(시트 계정 ≠ 연결 계정, 빨간 노드 대처 없음) / 헷갈림 13 / 사소 5 → **20건 모두 반영**. 느린 수강생 41분 어림 → 표현식·샘플 바꾸기를 한 번의 실행으로 합치고 "10단계까지 필수" 명시
- fact-check F73~F75 신규(미확인), instructor-checklist에 d1-p2 행과 강사 시험 9건 추가

### 검증 결과
- verify.py d1-p2: PASS (실패 0 / 경고 2 — 작성 전 d1-p1 링크, FACT-CHECK 5곳: F59, F72~F75)
- verify.py --all: d1-p2·d1-p3 모두 PASS / test_verify.py 33개 불일치 0
- learner-reviewer: 막힘 2 / 헷갈림 13 / 사소 5 → 반영 20
- fact-checker: 확인 7 / 수정 필요 2(F42 모델, F70 화면 표기) / 확인 불가 1(F72)
- status: todo → **instructor-check**
- 커밋: (이 기록과 같은 커밋)

### 다음 할 일
1. **강사 확인(d1-p2, d1-p3)**: instructor-checklist의 교시별 행 + fact-checker 직접 시험 항목. 특히 새 API 키에서 `models/gemini-3.8-flash` 목록·실행, 20명 동시 실행 한도(429)
2. 다음 교시: `authoring_order`상 **d1-p4**(AI 앱 빌더 첫 체험). AI Studio Build 모드 항목(F1~F11)이 모두 미확인이므로 **fact-checker로 F1~F11부터** 확인
3. 교육 1주 전: n8n Cloud 당시 안정 버전 기준 캡처·JSON 최종 확인

### 미해결 문제
- 1회차 미해결(에이전트 등록 확인, 제안서 그림 PNG, F41)은 그대로
- 한 세션에 두 교시를 진행함(사용자 요청). 컨텍스트가 길어졌으므로 d1-p4는 새 세션을 권장

## 3회차 — 2026-09-24 — d1-p4 AI 앱 빌더 첫 체험 (같은 세션, 사용자 요청으로 이어서 진행)

### 한 일
- fact-checker 3차(AI Studio, F1~F11·F44·F45, F76~F80 신규): 확인 7 / 수정 필요 3 / 확인 불가 8
  - F2 **만 18세 이상 나이 확인된 개인 계정**(D33), F3 공유 앱의 Gemini 사용량은 만든 사람 몫, F6 AI Studio 버튼은 `Publish`(n8n과 이름이 겹침 → D36)
  - 앱이 n8n을 부르는 origin은 문서 없음 → CORS `*` 유지, 막히면 서버 쪽 호출 요청(D35, F80)
- 산출물: `prompts/d1-p4-minwon-app.md`(화면·눌렀을 때·넣지 말 것 3부 구성, 빈 `WEBHOOK_URL` 상수 미리 생성 — D34, data-contract 한글 키), `lessons/d1-p4.html`(개념: 주문서 비유, 실습 6단계, 플랜 B, 퀴즈 2). 워크플로우 없음 → Import 섹션 없음(규칙상 정상)
- learner-reviewer: 막힘 3(보내기 버튼·Enter, 생성 실패 복구 없음, Apps 목록에서 앱 못 찾음) / 헷갈림 10 / 사소 5 → **18건 모두 반영**. 이메일을 data-contract대로 선택 입력으로 변경(프롬프트 파일·교안 동시)
- fact-check F81~F83 신규(미확인), decisions D33~D36, instructor-checklist에 d1-p4 행과 AI Studio 강사 시험 12건

### 검증 결과
- verify.py d1-p4: PASS (실패 0 / 경고 2 — 작성 전 d1-p5 링크, FACT-CHECK 9곳: F7·F8·F45·F76·F77·F81~F83)
- verify.py --all: d1-p2·d1-p3·d1-p4 PASS / test_verify.py 33개 불일치 0
- status: todo → **instructor-check**
- 커밋: (이 기록과 같은 커밋)

### 다음 할 일
1. **강사 확인 최우선: F4(앱 → n8n POST 성공 여부·origin)** — d1-p6 교안의 근거. 이어서 F8(오류 화면·자동 수정 버튼) — d1-p5의 근거
2. 다음 교시: **d1-p5**(첫 앱 다듬기 — 화면 수정 요청·오류 대처 루틴). F8·F77·F81·F82가 미확인이라 강사 캡처를 받으면 더 정확해짐
3. d1-p1 작성 시 준비물 안내에 "만 18세 이상 개인 구글 계정"(D33) 반영

### 미해결 문제
- AI Studio 화면 표기 상당수(F4·F7·F8·F76·F77·F81~F83)가 공식 문서에 없음 → 강사 캡처 전까지 FACT-CHECK 주석 유지
- 1·2회차 미해결 그대로(에이전트 등록 확인, 제안서 그림 PNG, F41)

## 4회차 — 2026-09-25 — d1-p5 첫 앱 다듬기 · d1-p6 앱 ↔ n8n 연동 ① (새 세션, 사용자 지시로 두 교시 연속)

### 한 일
- 재시작 후 `fact-checker`·`learner-reviewer` 에이전트가 정식 등록됨을 확인하고 사용(1회차 미해결 해소)
- **d1-p5**: `prompts/d1-p5-edit-requests.md`(요청 1~3, 나쁜 예/좋은 예), `prompts/d1-p5-error-routine.md`(오류 신고 문장, 연습 오류 1·2, 되돌리기·복구 문장), `lessons/d1-p5.html`(A 화면 수정 6단계 / B 오류 루틴 5단계, 2회 반복)
  - fact-checker: 확인 0 / 확인 불가 6(F8·F77·F82·F84~F86) → 조건부 문장 + FACT-CHECK(D37)
  - learner-reviewer: 막힘 5(오류 글·신고 문장 **복사 순서**, Code 탭 뒤 복귀, 흰 화면 오류, 되돌리기 버튼, 끝내 안 고쳐질 때) / 헷갈림 12 / 사소 8 → 25건 반영. 루틴을 "신고 문장 먼저 → 오류 글 끼워 넣기"로 바꿈, 요청 2·되돌리기를 선택으로
- **F4 시험**: Chrome 확장 미연결로 Claude가 직접 시험 불가 → 강사용 키트 `docs/instructor-kit/f4-test.md` + `f4-test-workflow.json`(D38)
- **d1-p6**: 구조 확정(D39) — `민원 받기`(Webhook POST minwon) → `민원 정리`(Edit Fields) → `시트에 기록`(d1-p2 노드 복사), 시트는 `민원대장 연습`/`시트1`, 날짜 열 `등록일`. data-contract 갱신. `workflows/d1-p6.json`, `prompts/d1-p6-connect-webhook.md`, `lessons/d1-p6.html`(10단계 + 연결 점검표)
  - fact-checker: F87 **수정 필요** — 한글 필드를 끌어 놓으면 이름이 `body['이름']`이 됨 → "이름 칸만 고치기"를 필수 단계로, JSON 값도 괄호 표기로. F89 노드 이름 바꾸기는 설정 창 맨 위 이름 한 번 누르기. F88 노드 복사 확인
  - learner-reviewer: 막힘 3(주소·문장 **복사 순서**, 끌어올 값 없음, Import 시트 목록) / 헷갈림 17 / 사소 8 → 28건 반영. 시간 기준(15:35), "성공 여부는 n8n 쪽으로 판단" 추가
- verify.py: 필드 대응표의 "이름 | 이름" 오탐 수정(NON_NAME_WORDS에 필드 이름 추가), 회귀 샘플 34개

### 검증 결과
- verify.py --all: d1-p2~d1-p6 모두 PASS(실패 0) / test_verify.py 34개 불일치 0
- status: d1-p5, d1-p6 → **instructor-check**
- 커밋: (이 기록과 같은 커밋)

### 다음 할 일
1. **강사: `docs/instructor-kit/f4-test.md` 시험** → 결과표 전달 시 d1-p6의 FACT-CHECK F4 정리(결과에 따라 기본 경로를 "서버 쪽 호출"로 바꿀 수 있음)
2. 다음 교시: **d1-p7**(연동 ① 완성 — 접수번호 생성·Respond to Webhook·1일차 정리). 접수번호 NNN 순번 생성 방식 결정 필요
3. d1-p4 교안의 "왼쪽 아래 입력창" 표기는 F82 미확인 — 강사 캡처 후 d1-p4·d1-p5·d1-p6 표기 통일

### 미해결 문제
- AI Studio 화면 세부(F4·F8·F77·F82·F84~F86)와 n8n UI 일부(F60·F87·F90·F91)는 강사 시험 대기
- 제안서 그림 PNG 전달 대기, F41 그대로
