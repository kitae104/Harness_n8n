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
