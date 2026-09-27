# CLAUDE.md — 교안 제작 하네스 지도

「AI 앱과 n8n으로 만드는 나만의 업무 자동화 서비스」 2일(14시간) 중급 과정의 **공무원용 교안**을 여러 세션에 걸쳐 만든다.
대상: 프로그래밍 경험 없는 공무원(선행 n8n 기초과정 수료). 핵심: "화면은 AI(Google AI Studio)가, 일은 n8n이".
산출물: 교시별 웹 교안(HTML), 인쇄용 교재, 교시별 완성 워크플로우 JSON, AI Studio 프롬프트 템플릿, 설계서 양식.

## 폴더

```
CLAUDE.md          이 지도            progress.md     세션 기록(매 세션 추가)
lessons.json       교시 명세·상태·작성 순서(authoring_order)
index.html         사이트 목차(build.py 생성)   instructor-notes.html  강사 준비 목록(build.py 생성, 임시)
lessons/           교시 교안 {id}.html          workflows/   완성본 JSON {id}.json
prompts/           AI Studio 프롬프트 {id}-*.md  print/       인쇄 교재·양식(forms/)
assets/css/        style(n8n 캔버스 디자인, D49)·lecture·lesson·home.css   assets/img/  캡처 fig-*.png
assets/proposal/   제안서 그림 PNG      assets/samples/  실습용 가상 자료(가상 공문 등)
docs/
  proposal.md        제안서(명세 원본 — PDF 대신 이것을 읽음)
  decisions.md       결정 기록(제안서보다 우선)
  writing-guide.md   작성 규칙 ★        glossary.md     용어 표기·자리표시자
  data-contract.md   앱·n8n·시트 이름 약속   sample-data.md  허용 가상 데이터
  fact-check.md      기능 서술 검증 상태   instructor-checklist.md  강사 수동 확인
  templates/         교안 HTML 템플릿      reviews/        learner-reviewer 결과
  instructor-kit/    강사 직접 시험 키트(F4 등)
  legacy/PublicFlow/ 기존 교안(참조 전용, 수정 금지)
scripts/  verify.py(검증) test_verify.py(검증기 회귀 테스트) build.py(목차·인쇄·강사 준비 목록) apply_captures.py(캡처 삽입)
          strip_inotes.py(강사 표시 보기·지우기) hook_verify.py
.claude/  settings.json(hook) agents/learner-reviewer.md, agents/fact-checker.md
```

## 세션 시작 절차

1. `progress.md`의 **마지막 기록**을 읽는다(다음 할 일, 미해결 문제).
2. `lessons.json`에서 이번 교시를 고른다: `authoring_order` 순서에서 status가 `todo`·`drafting`·`review`인 첫 교시(사용자가 지정하면 그것). 모두 `instructor-check` 이상이면 아래 "강사 확인 단계"를 따른다.
3. `docs/decisions.md` → 그 교시의 명세(objectives, acceptance_criteria, workflow, deliverables, source_refs, legacy_refs)를 읽는다.
4. `docs/writing-guide.md`, 그리고 필요에 따라 `data-contract.md`, `glossary.md`, `fact-check.md`의 관련 항목을 읽는다.
5. 모호한 점은 **추측하지 말고 사용자에게 개별 질문**한다. 답은 `docs/decisions.md`에 기록한다.

## 규칙

- **한 세션에 한 교시만** 작업한다(사용자가 여러 교시·전체 점검을 지시하면 예외). 다른 교시 파일은 고치지 않는다(링크·체인 수정이 꼭 필요하면 사용자에게 먼저 묻는다).
- **완료 조건은 검증 스크립트 통과다.** `python scripts/verify.py {id}`가 FAIL 0이어야 status를 올릴 수 있다.
  - hook: 교시 산출물(`lessons/`·`workflows/`·`prompts/`·deliverables에 적힌 파일)을 고치면 그 파일을 쓰는 교시와 체인 뒤 교시가, 규칙 파일(lessons.json·glossary·data-contract·sample-data)을 고치면 전 교시가 자동 검증된다.
- 시작은 `docs/templates/lesson-lab.html` 또는 `lesson-activity.html` 복사. 새 JSON은 `legacy_refs`의 기존 JSON을 바탕으로 변형한다.
- AI Studio·n8n 기능 서술은 `docs/fact-check.md`에서 `확인`된 것만 단정한다. 아니면 fact-checker를 돌리거나 그 자리에 **강사 확인 표시**(`span.inote`, writing-guide 9-1)를 단다.
- 강사가 확인·준비할 곳은 모두 강사 표시로 남긴다(모아 보기 `instructor-notes.html`). 준비가 끝나면 `python scripts/strip_inotes.py`로 지운다.
- 실습 데이터는 `docs/sample-data.md`의 가상 이름·연락처만 쓴다. 실제 민원·공문·실명 금지.
- 용어는 `docs/glossary.md` 표기("웹훅" 금지 → `Webhook`). 화면 글자는 `<code class="val">`.
- 명령은 `python`으로 실행한다(`python3`는 이 PC에서 동작하지 않음).
- `docs/legacy/`는 수정하지 않는다.

## 세션 종료 절차

1. `python scripts/verify.py {id}` → FAIL 0 (status `drafting`→`review` 조건)
2. `learner-reviewer` 에이전트로 리뷰 → `docs/reviews/{id}-learner.md`의 "막힘" 항목을 모두 반영
3. 기능 서술이 새로 생겼으면 `fact-checker` 에이전트 실행 → 수정 필요 항목 반영
4. 강사 수동 확인이 남았으면 status `instructor-check`, 모두 끝났으면 `done` (`docs/instructor-checklist.md`)
5. `python scripts/build.py`로 목차·인쇄 교재 갱신
6. `progress.md`에 기록 추가(한 일 / 검증 결과 / 다음 할 일 / 미해결 문제)
7. 커밋(한 교시 = 한 커밋 이상). push는 사용자가 요청할 때만.

## 강사 확인 단계 (status `instructor-check`)

1. 사용자가 강사 시험 결과(예: `docs/instructor-kit/f4-test.md` 결과표, 체크리스트 항목, 캡처)를 주면 `docs/fact-check.md`에 반영(fact-checker)
2. 결과에 맞게 교안을 고치고 해당 강사 표시를 지운다(`python scripts/strip_inotes.py --ref F번호`) → verify FAIL 0
3. `instructor-checklist.md`의 그 교시 항목을 모두 체크하면 status `done`, 확인 기록 표에 날짜·결과 기록

## 자주 쓰는 명령

```bash
python scripts/verify.py d1-p3          # 교시 검증
python scripts/verify.py --all          # todo가 아닌 전 교시
python scripts/test_verify.py           # verify.py·규칙 파일을 고친 뒤 회귀 테스트
python scripts/build.py                 # index.html, print/textbook.html 생성
python scripts/apply_captures.py --list # 남은 캡처 목록
```
