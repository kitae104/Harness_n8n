# 교안 작성 가이드

대상은 **프로그래밍 경험이 없는 공무원**(선행 n8n 기초과정 수료)이다. "50대 주무관이 옆에 강사 없이 인쇄본만 보고도 따라올 수 있는가"를 기준으로 쓴다.
검사 가능한 규칙은 `scripts/verify.py`가 확인한다(✅ 표시). 나머지는 `learner-reviewer` 리뷰로 확인한다.
디자인·마크업은 기존 교안(`docs/legacy/PublicFlow/`)의 CSS 관례를 따르고, 섹션 표지는 이 과정의 `data-section` 규칙을 쓴다(D20).

## 1. 교시 한 개의 구성 (50분)

| 순서 | 섹션 | `data-section` | 시간 | 내용 |
|---|---|---|---|---|
| 1 | 학습목표 | `objectives` | — | 제목 바로 아래 3줄 이내. lessons.json의 objectives와 같게 |
| 2 | **개념 블록** | `concept` | 10분 | **왜 이 단계가 필요한가.** 비유 1개 + 그림 또는 표 1개. 조작 설명은 넣지 않는다 |
| 3 | 실습 / 활동 | `practice` / `activity` | 30~35분 | 번호 단계 + 캡처 자리 + 자주 하는 실수 박스 |
| 4 | 자주 하는 실수 | `mistakes` | — | 실습 안에서 해당 단계 바로 뒤에 박스로 둔다(여러 개 가능) |
| 5 | 확인 문제 (선택) | `quiz` | — | 기존 교안의 퀴즈 형식. 정리 앞에 둔다 |
| 6 | 정리 | `summary` | 5분 | 오늘 만든 것 3줄, 다음 교시와의 연결 1줄 |
| 7 | 완성본 가져오기 | `import` | — | 교시 **맨 끝**. 뒤처진 수강생 복구 경로 |

- ✅ 순서는 `objectives → concept → practice|activity → (quiz) → summary → import`. 개념 블록 앞에는 학습목표만 올 수 있다.
- ✅ 개념 블록에는 `data-minutes="10"`을 붙인다.

### type별 필수 섹션 ✅

| type | 필수 | 조건부 필수 |
|---|---|---|
| `lab` (따라 하는 실습) | objectives, concept, practice, mistakes, summary | `workflow`가 있으면 import |
| `activity` (시연·기획·발표) | objectives, concept, activity, summary | `workflow`가 있으면 import. mistakes는 권장 |

## 2. HTML 골격 (계약)

`docs/templates/lesson-lab.html`, `lesson-activity.html`을 복사해서 시작한다.

```html
<body class="lecture-mode">
<main class="wrap" data-lesson-id="d1-p3" data-type="lab">
  <nav class="crumb">…</nav>
  <header class="page-head"><h1>…</h1><p class="sub">…</p></header>
  <section class="sec" id="objectives" data-section="objectives">…</section>
  <section class="sec" id="concept" data-section="concept" data-minutes="10">…</section>
  <section class="sec" id="practice" data-section="practice">
    <ol class="steps">
      <li><span class="step-title">단계 제목</span> 설명 …
        <figure class="capture" id="fig-d1-p3-1">
          <div class="capture-cap">[그림 1-3-1] 그림 제목</div>
          <div class="capture-guide">촬영 안내: 무엇을, 어디를 강조해 찍을지</div>
        </figure>
      </li>
    </ol>
    <div class="note mistake" data-section="mistakes"><b>자주 하는 실수</b> …</div>
  </section>
  <section class="sec" id="summary" data-section="summary">…</section>
  <section class="sec" id="import" data-section="import">…</section>
  <nav class="pager">…</nav>
</main>
```

- ✅ `data-lesson-id`는 파일명, `data-type`은 lessons.json의 type과 같아야 한다.
- ✅ CSS는 `../assets/css/style.css`, `lecture.css`(기존 사이트 그대로), `lesson.css`(이 과정 확장) 세 개를 이 순서로 불러온다.
- ✅ `<script>`와 외부 자원(CDN, 웹폰트, 외부 이미지)을 쓰지 않는다(교육망 차단 대비, 기존 교안 규칙).
- ✅ 내부 링크는 `.html` 확장자까지 쓴다(로컬 `file://`로 열어도 동작하도록). 링크 대상 파일과 `#id`가 실제로 있어야 한다. 아직 작성하지 않은(status `todo`) 교시로 가는 링크는 경고로만 알린다.
- ✅ `TODO` `TBD` `FIXME` `lorem ipsum` 같은 미완성 표시를 남기지 않는다.

### 캡처 (기존 교안 방식 그대로) ✅

- 형식: `<figure class="capture" id="fig-{교시 id}-{번호}">` — **class가 먼저, id가 나중**(캡처 도구가 이 순서로 찾음).
- 캡션: `<div class="capture-cap">[그림 {일차}-{교시}-{번호}] 제목</div>`. 선택 실습은 `[그림 opt-pdf-1]`처럼 쓴다.
- 아직 안 찍은 자리: `<div class="capture-guide">촬영 안내</div>`. 찍은 뒤 `assets/img/fig-….png`로 저장하고 `python scripts/apply_captures.py`를 실행하면 이미지로 바뀐다. `--list`로 남은 촬영 목록을 본다.
- ✅ `lab`의 실습에는 `<ol class="steps">`와 캡처가 1개 이상 있어야 한다. 모든 `<img>`에는 비어 있지 않은 `alt`를 단다.
- 캡처 속 계정 이메일·API 키·Webhook 주소의 고유 부분은 가린다.
- 제안서 그림은 `assets/proposal/`에 있다.

## 3. 문장과 용어

- 존댓말 "~합니다 / ~하세요"로 쓴다. 한 문장에 동작 하나만 넣는다.
- 화면에서 누르거나 입력하는 글자는 **`<code class="val">Test URL</code>`**로 화면 표기 그대로 쓴다(기존 교안 관례).
- ✅ 용어는 `docs/glossary.md`의 표준 표기를 따른다. 금지 변형("웹훅" 등)이 나오면 실패한다. `code.val` 안도 검사한다.
- ✅ glossary에서 `풀이 필수 = Y`인 용어는 **교시마다 본문 첫 등장 때** `<dfn>`으로 감싸고 쉬운 말 풀이를 붙인다. 제목(h1~h4), 목차, 학습목표, 단계 제목(`.step-title`), 그림 캡션은 '첫 등장' 판정에서 빠진다.
  예: `<dfn>Webhook</dfn>(외부 앱이 n8n을 부르는 주소)`
- 주소·JSON·표현식은 class 없는 `<code>`나 `<pre class="code-block">` 안에 넣는다. 이 안은 용어 검사를 하지 않는다.
- "간단히", "쉽게", "당연히"는 쓰지 않는다. 막힌 수강생이 자기 탓이라고 느낀다.

## 4. 실습 단계와 박스

1. 단계마다 번호(`ol.steps > li`)와 `<span class="step-title">`을 둔다. 한 단계 = 화면 하나에서 하는 일.
2. 단계 끝에 **확인 문장**을 둔다: "○○가 보이면 성공입니다."
3. 캡처 자리를 둔다.
4. 실수가 잦은 단계 바로 뒤에 **자주 하는 실수** 박스를 둔다. 형식은 `증상 → 원인 → 해결`이다.

```html
<div class="note mistake" data-section="mistakes">
  <b>자주 하는 실수</b>
  <p><b>증상</b> 앱에서 "Failed to fetch"가 떠요<br>
     <b>원인</b> Test URL을 넣었거나 워크플로우를 활성화하지 않았어요<br>
     <b>해결</b> 활성화한 뒤 Production URL로 바꿔 넣으세요</p>
</div>
```

박스는 기존 `.note`를 쓰고 **첫 `<b>`가 박스 제목**이다. 색만으로 구분하지 않도록 제목 글자를 반드시 단다(흑백 인쇄 대비).

| 박스 | class | 제목 예 |
|---|---|---|
| 개념 | `note concept` | 왜 필요한가 |
| 자주 하는 실수 | `note mistake` | 자주 하는 실수 |
| 도움말 | `note tip` (기존) | 알아 두면 좋아요 |
| 주의·개인정보 | `note warn` (기존) | 개인정보 주의 |
| 막혔을 때 | `note planb` | 접속이 막혔을 때 |

## 5. 실습 데이터 ✅

- `docs/sample-data.md`에 등록된 **가상 이름·연락처·이메일만** 쓴다. 실제 민원 데이터·공문·실명은 금지한다.
- 앱 필드 이름, 시트 열, 응답 키, Webhook 경로는 `docs/data-contract.md`를 따른다.
- 교안 본문의 Gmail 수신 주소는 `{본인 이메일}`, JSON 안은 `본인이메일@example.com`으로 쓴다(glossary "자리표시자").
- 새 가상 인물이 필요하면 sample-data.md에 먼저 추가한다.
- ✅ 이 검사는 교시의 **모든 산출물**(HTML, JSON, 프롬프트, 인쇄용 양식)에 적용된다.

## 6. 완성본 가져오기(Import) 섹션 — 교시 맨 끝 ✅

뒤처진 수강생이 **이 섹션만 보고 교시 끝 상태로 복구**할 수 있어야 한다. 기존 교안 `download` 섹션 방식을 따른다.

1. ✅ 내려받기 링크: `<a class="dl" href="../workflows/{파일}.json" download>워크플로우 내려받기 <span class="dl-name">{파일}.json</span></a>` (lessons.json `workflow.file`과 같아야 함)
2. n8n에서 가져오기(Import) 하는 단계
3. ✅ **자격 증명 다시 연결 단계**(필수, "자격 증명" 문구 검사): 가져온 파일에는 자격 증명이 빠져 있다. **다시 골라야 할 노드 이름을 모두 나열**한다(예: `시트에 기록`, `접수 메일 보내기`, `Google Gemini Chat Model`).
4. 자리표시자 바꾸기: 그 JSON에 들어 있는 `여기에_본인_시트_ID` 같은 자리표시자를 모두 적는다(없으면 verify가 경고). 시트 탭 이름도 다시 고르게 한다.
5. Webhook이 있으면: 활성화한 뒤 **내** Production URL을 앱에 다시 넣는다.
6. 성공 확인 방법

`role = reference`인 교시(d1-p1 시연, opt-voice)는 가리키는 파일이 다른 교시(d2-p2) 것임을 밝힌다.

## 7. 워크플로우 JSON 규칙 ✅

- 파일: `workflows/{교시 id}.json`. UTF-8(**BOM 없음**), n8n에서 내보낸 형식(`nodes`, `connections` 필수).
- **새로 만들 때는 기존 교안 JSON(`docs/legacy/PublicFlow/public/downloads/*.json`)을 바탕으로 변형한다.** 노드 `type`·`typeVersion`·파라미터 형태가 실제 n8n에서 내보낸 것이라 믿을 수 있다. 참고할 파일은 lessons.json `legacy_refs`에 있다.
- **Gemini**: `AI 안내문 작성`(`@n8n/n8n-nodes-langchain.chainLlm`) 노드에 `Google Gemini Chat Model`(`@n8n/n8n-nodes-langchain.lmChatGoogleGemini`)을 `ai_languageModel` 연결로 붙인다(기존 교안과 같음). 자격 증명은 Google Gemini(PaLM) API 키.
- **누적 체인**: `d1-p6 → d1-p7 → d2-p1 → d2-p2`, `d2-p5 → d2-p6`. 뒤 교시 JSON은 앞 교시의 **모든 노드 이름을 포함**한다. `d1-p2`, `d1-p3`, `opt-pdf`는 독립 파일이다.
- ✅ Webhook 경로(`path`)는 `docs/data-contract.md` 표와 같아야 한다.
- ✅ **자격 증명 ID를 남기지 않는다.** `credentials` 키를 아예 빼는 것이 기본(기존 교안 방식)이고, 남기면 `id`는 `""`로 둔다.
- ✅ API 키, 봇 토큰, 실제 이메일, `pinData` 속 실제 데이터를 넣지 않는다. 자리표시자를 쓴다.
- ✅ Respond to Webhook 노드를 쓰면 Webhook 노드의 `responseMode`를 `responseNode`로 둔다.
- 브라우저 앱이 부르는 Webhook에는 Allowed Origins(CORS) 옵션을 설정한다(없으면 verify가 경고).
- 노드 이름은 교안 본문에서 부르는 한글 이름과 똑같이 쓴다(예: `시트에 기록`).
- n8n 없이 만든 JSON은 구조 검사만 통과한 상태다. **강사가 n8n Cloud에 Import해 실행해 봐야** `done`이 된다(`docs/instructor-checklist.md`).

## 8. 프롬프트 템플릿 파일 (`prompts/`)

파일명: `{교시 id}-{내용}.md`. 형식:

```markdown
# 제목
- 사용 교시: d1-p4
## 복사할 프롬프트
(코드 블록 하나 — 수강생이 그대로 복사)
## 바꿀 자리
- {Production URL}: …
## 예상 결과
## 검증 기록
| 날짜 | 검증자 | 도구·모델 | 결과 |
```

- ✅ `## 복사할 프롬프트`와 `## 검증 기록` 제목이 있어야 한다.
- 바꿀 자리는 `{중괄호}`로 표시한다. 실제 Webhook 주소를 템플릿에 넣지 않는다.
- 앱이 보내고 받는 키 이름은 `docs/data-contract.md`와 같게 프롬프트에 명시한다.
- 강사가 AI Studio에서 실제로 돌려 본 뒤에만 검증 기록을 채운다.

## 9. 사실 확인

- AI Studio Build 모드, n8n Webhook(CORS, Test/Production URL, Respond to Webhook), 활성화 UI 같은 기능 서술은 **`docs/fact-check.md`에서 '확인'된 내용만** 단정적으로 쓴다.
- 제안서 내용도 검증 전에는 사실로 가정하지 않는다. 확인되지 않은 채 써야 하면 `<!-- FACT-CHECK: F번호 -->` 주석을 남긴다(verify가 경고로 알려 줌).

## 10. 인쇄

- 웹 교안과 인쇄 교재는 같은 HTML에서 만든다(`python scripts/build.py` → `print/textbook.html` → 브라우저 "PDF로 인쇄").
- 교시마다 새 페이지에서 시작한다. 박스·표·그림은 페이지 중간에서 잘리지 않게 한다(CSS가 처리).
- 색만으로 구분하지 않는다. 박스는 제목 글자와 테두리 모양(이중선·굵은 실선·점선)으로 구분된다.
