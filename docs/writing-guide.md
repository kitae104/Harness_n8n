# 교안 작성 가이드

대상은 **프로그래밍 경험이 없는 공무원**(선행 n8n 기초과정 수료)이다. "50대 주무관이 옆에 강사 없이 인쇄본만 보고도 따라올 수 있는가"를 기준으로 쓴다.
검사 가능한 규칙은 `scripts/verify.py`가 확인한다(✅ 표시). 나머지는 `learner-reviewer` 리뷰로 확인한다.

## 1. 교시 한 개의 구성 (50분)

| 순서 | 섹션 | `data-section` | 시간 | 내용 |
|---|---|---|---|---|
| 1 | 학습목표 | `objectives` | — | 제목 바로 아래 3줄 이내. lessons.json의 objectives와 같게 |
| 2 | **개념 블록** | `concept` | 10분 | **왜 이 단계가 필요한가.** 비유 1개 + 그림 또는 표 1개. 조작 설명은 넣지 않는다 |
| 3 | 실습 / 활동 | `practice` / `activity` | 30~35분 | 번호 단계 + 캡처 자리 + 자주 하는 실수 박스 |
| 4 | 자주 하는 실수 | `mistakes` | — | 실습 안의 해당 단계 바로 뒤에 박스로 둔다(여러 개 가능) |
| 5 | 정리 | `summary` | 5분 | 오늘 만든 것 3줄, 다음 교시와의 연결 1줄 |
| 6 | 완성본 가져오기 | `import` | — | 교시 **맨 끝**. 뒤처진 수강생 복구 경로 |

- ✅ 모든 교시는 개념 블록으로 **시작**한다. 학습목표 박스만 그 앞에 둘 수 있다. 순서는 `objectives → concept → practice|activity → summary → import`.
- ✅ 개념 블록에는 `data-minutes="10"`을 붙인다.

### type별 필수 섹션 ✅

| type | 필수 | 조건부 필수 |
|---|---|---|
| `lab` (따라 하는 실습) | objectives, concept, practice, mistakes, summary | `workflow`가 있으면 import |
| `activity` (시연·기획·발표) | objectives, concept, activity, summary | `workflow`가 있으면 import. mistakes는 권장 |

## 2. HTML 골격 (계약)

`docs/templates/lesson-lab.html`, `lesson-activity.html`을 복사해서 시작한다. verify.py는 아래 표지를 본다.

```html
<main class="lesson" data-lesson-id="d1-p3" data-type="lab">
  <section data-section="objectives">…</section>
  <section data-section="concept" data-minutes="10">…</section>
  <section data-section="practice">
    <ol class="steps">
      <li>…
        <figure class="capture"><div class="capture-slot" data-capture="d1-p3-01">캡처 자리: 무엇을 찍을지</div>
          <figcaption>그림 설명</figcaption></figure>
      </li>
    </ol>
    <aside class="box box-mistake" data-section="mistakes">…</aside>
  </section>
  <section data-section="summary">…</section>
  <section data-section="import">…</section>
</main>
```

- ✅ `data-lesson-id`는 파일명, `data-type`은 lessons.json의 type과 같아야 한다.
- ✅ `lab`의 실습에는 `<ol class="steps">`와 캡처 자리(`.capture`)가 1개 이상 있어야 한다.
- ✅ 모든 `<img>`에는 비어 있지 않은 `alt`를 단다. 캡처를 아직 못 찍었으면 `<div class="capture-slot">`에 무엇을 찍을지 적어 둔다(verify가 남은 개수를 알려 줌).
- ✅ 내부 링크(`href`, `src`)는 실제 파일·`#id`를 가리켜야 한다.
- 외부 CDN·웹폰트를 쓰지 않는다(교육망 차단 대비). CSS는 `../assets/css/lesson.css` 하나만 쓴다.
- 이미지는 `assets/img/{교시 id}/`에 둔다. 제안서 그림은 `assets/proposal/`에 있다.

## 3. 문장과 용어

- 존댓말 "~합니다 / ~하세요"로 쓴다. 한 문장에 동작 하나만 넣는다.
- 화면에서 누를 이름은 `<b class="ui">Test URL</b>`처럼 화면 표기 그대로 굵게 쓴다.
- ✅ 용어는 `docs/glossary.md`의 표준 표기를 따른다. 금지 변형("웹훅" 등)이 나오면 실패한다.
- ✅ glossary에서 `풀이 필수 = Y`인 용어는 **교시마다 첫 등장 때** `<dfn>`으로 감싸고 쉬운 말 풀이를 붙인다.
  예: `<dfn>Webhook</dfn>(외부 앱이 n8n을 부르는 주소)`
- 주소·JSON·표현식은 `<code>`나 `<pre>` 안에 넣는다. 이 안은 용어 검사를 하지 않는다.
- "간단히", "쉽게", "당연히"는 쓰지 않는다. 막힌 수강생은 자기 탓이라고 느낀다.

## 4. 실습 단계 쓰는 법

1. 단계마다 번호를 붙인다. 한 단계 = 화면 하나에서 하는 일.
2. 단계 끝에 **확인 문장**을 둔다: "○○가 보이면 성공입니다."
3. 캡처 자리를 둔다. 무엇을, 어느 부분을 강조해 찍을지 적는다.
4. 실수가 잦은 단계 바로 뒤에 **자주 하는 실수** 박스를 둔다. 형식은 `증상 → 원인 → 해결`이다.

```html
<aside class="box box-mistake" data-section="mistakes">
  <p class="box-title">자주 하는 실수</p>
  <dl><dt>증상</dt><dd>앱에서 "Failed to fetch"가 떠요</dd>
      <dt>원인</dt><dd>Test URL을 넣었거나 워크플로우를 활성화하지 않았어요</dd>
      <dt>해결</dt><dd>활성화 후 Production URL로 바꿔 넣으세요</dd></dl>
</aside>
```

박스 종류는 `box-concept`(개념), `box-mistake`(자주 하는 실수), `box-tip`(도움말), `box-warn`(개인정보·보안 주의), `box-planb`(막혔을 때)다.
색만으로 구분하지 않도록 **모든 박스에 `box-title` 글자 제목**을 단다(흑백 인쇄 대비).

## 5. 실습 데이터 ✅

- `docs/sample-data.md`에 등록된 **가상 이름·연락처·이메일만** 쓴다. 실제 민원 데이터·공문·실명은 금지한다.
- Gmail 수신 주소는 `{본인 이메일}` 자리표시로 쓴다.
- 새 가상 인물이 필요하면 sample-data.md에 먼저 추가한다.
- 캡처 속 계정 이메일·API 키·Webhook 주소의 고유 부분은 가린다.

## 6. 완성본 가져오기(Import) 섹션 — 교시 맨 끝 ✅

뒤처진 수강생이 **이 섹션만 보고 교시 끝 상태로 복구**할 수 있어야 한다. 반드시 넣을 것:

1. 완성본 파일 링크: `<a href="../workflows/{파일}.json" download>` (lessons.json `workflow.file`과 같아야 함 ✅)
2. n8n에서 가져오기(Import) 하는 단계
3. **자격 증명 다시 연결 단계**(필수 ✅, "자격 증명" 문구 검사): 가져온 파일에는 강사의 자격 증명이 빠져 있으므로 구글 시트·Gmail·Gemini·텔레그램 노드마다 **내 자격 증명**을 다시 고른다.
4. 구글 시트 문서·시트 이름을 내 것으로 바꾸는 단계(해당 시)
5. Webhook이 있으면: 활성화 → **내** Production URL을 앱에 다시 넣는 단계
6. 성공 확인 방법

`role = reference`인 교시(예: d1-p1 시연)는 가리키는 파일이 다른 교시 것임을 밝힌다.

## 7. 워크플로우 JSON 규칙 ✅

- 파일: `workflows/{교시 id}.json`. n8n에서 내보내기(Download)한 형식 그대로 둔다(`nodes`, `connections` 필수).
- **누적 체인**: `d1-p6 → d1-p7 → d2-p1 → d2-p2`, `d2-p5 → d2-p6`. 뒤 교시 JSON은 앞 교시의 **모든 노드를 포함**한다(verify가 노드 이름으로 확인).
  `d1-p2`, `d1-p3`, `opt-pdf`는 독립 파일이다. `d1-p1`, `opt-voice`는 `d2-p2.json`을 참조한다.
- **자격 증명 ID를 남기지 않는다.** 노드의 `credentials`에서 `id`는 지우거나 `""`로 둔다. `name`은 남겨도 된다.
- API 키, 봇 토큰, 실제 이메일, `pinData` 속 실제 데이터를 넣지 않는다.
- Respond to Webhook 노드를 쓰면 Webhook 노드의 응답 방식(`responseMode`)을 `responseNode`로 둔다.
- 브라우저 앱이 부르는 Webhook에는 Allowed Origins(CORS) 옵션을 설정한다(verify는 없으면 경고).
- 노드 이름은 교안 본문에서 부르는 이름과 똑같이 쓴다.

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
- 강사가 AI Studio에서 실제로 돌려 본 뒤에만 검증 기록을 채운다.

## 9. 사실 확인

- AI Studio Build 모드, n8n Webhook(CORS, Test/Production URL, Respond to Webhook), 활성화 UI 같은 기능 서술은 **`docs/fact-check.md`에서 '확인'된 내용만** 쓴다.
- 제안서 내용도 검증 전에는 사실로 가정하지 않는다. 확인되지 않은 채 써야 하면 `<!-- FACT-CHECK: 항목번호 -->` 주석을 남긴다(verify가 경고로 알려 줌).

## 10. 인쇄

- 웹 교안과 인쇄 교재는 같은 HTML에서 만든다(`python scripts/build.py`).
- 교시마다 새 페이지에서 시작한다. 박스·표는 페이지 중간에서 잘리지 않게 한다(CSS가 처리).
- 색만으로 구분하지 않는다. 박스는 글자 제목과 테두리 모양(실선·이중선·점선)으로 구분한다.
