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
