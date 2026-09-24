# 사실 확인 목록 (fact-check)

교안에 쓰는 도구 기능 서술을 **공식 문서와 대조**한 기록이다. `fact-checker` 에이전트가 갱신한다.
제안서 내용도 사실로 가정하지 않는다. 교안에는 **상태가 `확인`인 항목만** 단정적으로 쓴다.

- 상태: `미확인` → `확인`(근거 URL 있음) / `수정 필요`(제안서·교안과 다름) / `확인 불가`(공식 문서 없음 → 강사가 직접 시험)
- 근거는 공식 문서 URL(ai.google.dev, docs.n8n.io 등)을 우선한다. 블로그·포럼은 보조 근거로만 쓴다.
- UI 표기는 확인한 **날짜와 버전**이 중요하다. n8n과 AI Studio는 화면이 자주 바뀐다.

## Google AI Studio Build 모드

| # | 확인할 서술 | 출처 | 상태 | 근거 | 확인일 | 관련 교시 |
|---|---|---|---|---|---|---|
| F1 | Build 모드는 한글 문장(프롬프트)만으로 웹 앱을 생성·수정한다 | 제안서 2절 | 미확인 | | | d1-p4, d1-p5 |
| F2 | 구글 계정만 있으면 무료로 사용한다(결제 정보 불필요) | 제안서 2절 | 미확인 | | | d1-p4 |
| F3 | 만든 앱은 공유 링크로 바로 열어볼 수 있다. 링크를 받은 사람의 로그인 필요 여부와 사용량이 누구 몫인지 | 제안서 2절 | 미확인 | | | d2-p3 |
| F4 | 앱에서 외부 주소(n8n Webhook) 호출(fetch)이 허용된다 | 제안서 2절 | 미확인 | | | d1-p6 |
| F5 | Gemini API 키는 서버 쪽 비밀값으로 자동 보관되어 코드에 넣을 일이 없다 | 제안서 2절 | 미확인 | | | d2-p3 |
| F6 | Cloud Run 배포에는 결제 계정이 필요하다 | 제안서 2절 | 미확인 | | | d2-p3 |
| F7 | 무료 사용량 한도가 있다(수치와 초과 시 동작) | 제안서 11절 | 미확인 | | | d1-p4 |
| F8 | 오류가 나면 화면에 오류 문구가 표시되고, 이를 붙여넣어 수정 요청할 수 있다(자동 수정 버튼 유무 포함) | 제안서 2절 | 미확인 | | | d1-p5 |
| F9 | 앱 안에서 마이크(브라우저 음성 인식) 권한 요청이 동작한다 | 제안서 1절 | 미확인 | | | opt-voice |
| F10 | 앱에서 파일(PDF) 업로드 후 외부로 전송할 수 있다 | 제안서 9절 | 미확인 | | | opt-pdf |
| F11 | 교육망 예외처리에 필요한 도메인 목록(공유 앱이 열리는 도메인 포함) | 제안서 5절 | 미확인 | | | d1-p1, 운영 |

## n8n Webhook

| # | 확인할 서술 | 출처 | 상태 | 근거 | 확인일 | 관련 교시 |
|---|---|---|---|---|---|---|
| F20 | Webhook 노드에 CORS 옵션 "Allowed Origins (CORS)"가 있고 `*` 또는 앱 주소를 넣는다(정확한 옵션 이름·기본값·JSON 키) | 제안서 2절 | 확인 | 옵션 이름은 **Allowed Origins (CORS)**, 기본값 `*`. 노드의 **Add Option**을 눌러 추가하는 옵션이다. 문서: "Enter a comma-separated list of URLs allowed for cross-origin non-preflight requests. Use `*` (default) to allow all origins." (https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/#node-options). 소스 `packages/core/src/nodes-loader/constants.ts`(displayName 'Allowed Origins (CORS)', name 'allowedOrigins', default '*'). 여러 주소는 쉼표로 구분. 참고: 값이 `*`이면 n8n은 응답 헤더에 요청한 쪽 Origin을 그대로 돌려준다(`webhook-request-handler.ts`). 확인 버전: n8n 2.40.6(stable) | 2026-09-24 | d1-p3, d2-p2 |
| F21 | Test URL은 "테스트 대기" 상태에서만 동작하고, Production URL은 워크플로우를 활성화해야 동작한다 | 제안서 2절 | 수정 필요 | 동작은 맞으나 **'활성화' 대신 'Publish(게시)'** 로 써야 한다. 문서 표: Test URL — "Select **Listen for test event** and trigger a test event from the source.", 대기 "120 seconds", 편집 화면에 데이터 표시 ✅ / Production URL — "Publish the workflow", "Until workflow is unpublished", 편집 화면 표시 ❌ (https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/common-issues/#test-url-versus-production-url). 소스의 오류 힌트: 테스트 모드는 "the webhook only works for one call after you click this button"(`webhook-not-found.error.ts`). **올바른 서술**: "Test URL은 `Listen for test event`(또는 `Execute workflow`)를 누른 뒤 120초 동안, 한 번 호출할 때만 동작한다. Production URL은 워크플로우를 **Publish**해야 동작하고, 실행 기록은 캔버스가 아니라 **Executions** 탭에서 본다." 주의: Production URL 404 오류 힌트 문구는 아직 "You can activate the workflow using the toggle in the top-right of the editor"라고 나온다(2.40.6 소스) — 화면에는 토글이 없으니 Publish로 안내. 주소 차이: Test는 `/webhook-test/…`, Production은 `/webhook/…` | 2026-09-24 | d1-p3, d1-p6 |
| F22 | 최신 n8n의 활성화 UI 표기(Active 토글인지 Publish 버튼인지 등) | glossary ❓ | 수정 필요 | n8n 2.0에서 토글이 사라지고 **Publish** 버튼으로 바뀌었다. "The new workflow publishing system replaces the previous active/inactive toggle. This means that the old \"Activate/Deactivate\" toggles become the new \"Publish/Unpublish\" buttons." (https://docs.n8n.io/changelog/v20-breaking-changes/#saving-and-publishing-workflows). 현재 문서: "To publish your workflow, open your workflow and click **Publish**." 단축키 `Shift`+`p`, 게시 창에서 다시 **Publish** 클릭. 게시 해제는 Publish 옆 드롭다운의 **Unpublish**(https://docs.n8n.io/build/understand-workflows/save-and-publish-workflows/). 저장 버튼 없음(자동 저장, "No manual save button is required"). **올바른 서술**: "캔버스 위쪽의 `Publish` 버튼 → 뜨는 창에서 `Publish`". 기존 교안의 '활성화 스위치 켜기'는 모두 교체. 영향: 전 교시(특히 d1-p3, d1-p6, legacy day1/08.html 문구) | 2026-09-24 | 전 교시 |
| F23 | Respond to Webhook 노드를 쓰려면 Webhook 노드의 응답 방식을 "Respond to Webhook 노드 사용"으로 바꿔야 한다(정확한 UI 표기, JSON `responseMode: responseNode`) | 제안서 2절 | 확인 | Webhook 노드 **Respond** 항목에서 **Using 'Respond to Webhook' Node** 선택(선택지: Immediately / When Last Node Finishes / Using 'Respond to Webhook' Node / Streaming). 문서: "In the Webhook node, set **Respond** to **Using 'Respond to Webhook' node**." (https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.respondtowebhook/#how-to-use-respond-to-webhook). 소스 `Webhook/description.ts`: displayName 'Respond', name 'responseMode', 선택지 이름 "Using 'Respond to Webhook' Node", value 'responseNode', 기본값 'onReceived'(=Immediately). 문서는 node 소문자, 화면(소스)은 Node 대문자 — 교안은 화면 표기 `Using 'Respond to Webhook' Node` 사용. 기본값 Immediately의 응답 본문은 `{"message":"Workflow was started"}` | 2026-09-24 | d1-p3, d1-p7 |
| F24 | 브라우저의 사전 요청(OPTIONS preflight)을 CORS 설정만으로 n8n이 처리하는가, Respond to Webhook 응답에도 CORS 헤더가 붙는가 | 추가 | 확인 | 둘 다 **예**(소스 근거). 문서 문구는 "non-preflight requests"라 오해 소지가 있으나, 소스 https://github.com/n8n-io/n8n/blob/n8n@2.40.6/packages/cli/src/webhooks/webhook-request-handler.ts : 요청에 Origin 헤더가 있으면 워크플로우 실행 **전에** `Access-Control-Allow-Origin`·`Access-Control-Allow-Methods`를 붙이고, `OPTIONS`이면 `Access-Control-Max-Age: 300`과 요청한 헤더를 그대로 `Access-Control-Allow-Headers`에 넣어 **204로 바로 응답**한다(워크플로우는 실행 안 함). 같은 응답 객체로 Respond to Webhook이 나중에 응답하므로 CORS 헤더가 유지된다. 따라서 별도 OPTIONS Webhook이나 Response Headers 수동 설정이 필요 없다. 단, Respond to Webhook의 Response Headers에 `Access-Control-Allow-Origin`을 직접 넣으면 덮어쓸 수 있으니 넣지 않는다. Test URL은 대기 중일 때만 등록돼 있어 preflight도 그때만 성공 → 강사 실제 시험 권장 | 2026-09-24 | d1-p3 |
| F25 | GET Webhook에서 쿼리 값(접수번호)을 표현식으로 꺼내는 방법(`$json.query.…`) | 추가 | 확인 | Webhook 출력은 `{ headers, params, query, body }` 구조(소스 `Webhook.node.ts`: `query: req.query`). 문서(Only Run If 옵션): "Use `$json` to access the request as `{ body, headers, params, query }`" (https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/#node-options). 예: `?no=123` → `{{ $json.query.no }}`. 뒤쪽 노드에서는 `{{ $('Webhook').item.json.query.no }}` 처럼 노드 이름으로 참조 | 2026-09-24 | d2-p2 |
| F26 | POST로 받은 JSON 본문이 `$json.body` 아래에 들어온다 | 추가 | 확인 | 소스: `json: { headers: req.headers, params: req.params, query: req.query, body: req.body }` (https://github.com/n8n-io/n8n/blob/n8n@2.40.6/packages/nodes-base/nodes/Webhook/Webhook.node.ts). 문서 예시도 `{{ $json.body.campaign_id === 'user-research-invite' }}` (https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/#node-options). 예: 본문 `{"name":"홍길동"}` → `{{ $json.body.name }}`. (Raw Body 옵션을 켜면 바이너리로도 들어옴 — 교안에서는 켜지 않음) | 2026-09-24 | d1-p6 |
| F27 | 한 워크플로우에 Webhook 트리거 두 개(POST 접수, GET 조회)를 둘 수 있다 | 추가(D11) | 확인 | 가능. 제약은 "n8n only permits registering one webhook for each path and HTTP method combination" (https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/common-issues/#only-one-webhook-per-path-and-method) — **경로+메서드 조합**만 겹치지 않으면 된다(POST 접수·GET 조회는 경로를 달리 두는 것이 안전). 다른 워크플로우와 겹치면 충돌 메시지가 뜬다. 대안: 노드 하나에서 Settings → **Allow Multiple HTTP Methods**(메서드별 출력 분기). Test 모드에서 두 트리거를 번갈아 시험하는 흐름은 강사 시험 필요 | 2026-09-24 | d2-p2 |
| F49 | (코드 없이 GET 시험) GET Webhook 주소를 브라우저 주소창에 붙여넣으면 워크플로우가 실행되고 응답이 화면에 표시된다 | 추가(d1-p3) | 확인 | 주소창 이동은 GET 요청이다. Webhook 노드는 GET을 지원하고 문서 예시도 `curl --request GET <https://your-n8n.url/webhook/path>` (https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/common-issues/#use-curl-to-trigger-the-webhook-node). 주소창 이동에는 보통 Origin 헤더가 없어 CORS와 무관(소스: Origin 헤더가 있을 때만 CORS 처리). 순서: Test URL은 `Listen for test event` 클릭 후 120초 안에 붙여넣기(캔버스에 데이터 표시) / Production URL은 `Publish` 후. 응답: Respond가 Immediately면 `{"message":"Workflow was started"}`, `Using 'Respond to Webhook' Node`면 그 노드의 JSON이 브라우저에 표시. 쿼리 값은 `…?no=123`처럼 붙여 F25로 확인 가능. Text(HTML) 응답은 1.103.0부터 sandbox iframe으로 감싸짐(https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/#how-n8n-secures-html-responses) | 2026-09-24 | d1-p3 |
| F50 | 주소창으로는 POST를 보낼 수 없다. POST Webhook 주소를 주소창에 붙여넣으면 오류가 난다 | 추가(d1-p3) | 확인 | 주소창은 GET만 보낸다. 소스 https://github.com/n8n-io/n8n/blob/n8n@2.40.6/packages/cli/src/errors/response-errors/webhook-not-found.error.ts : 메서드가 다르면 "This webhook is not registered for GET requests. Did you mean to make a POST request?", 등록 안 된 경로면 "The requested webhook \"…\" is not registered."(Test URL 대기 전·Publish 전에 흔한 오류). 교안 '문제 해결' 칸에 이 두 문구를 그대로 쓸 것 | 2026-09-24 | d1-p3 |
| F51 | (코드 없이 POST 시험) n8n 안의 HTTP Request 노드로 내 Webhook에 POST(JSON 본문)를 보내 시험할 수 있다 | 추가(d1-p3) | 확인 | 문서 절 "Use the HTTP Request node to trigger the Webhook node": Request Method를 Webhook과 같게 고르고 URL 붙여넣기 → Test URL이면 Webhook 쪽을 먼저 실행(대기)시킨 뒤 HTTP Request 노드 실행 (https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/common-issues/#use-the-http-request-node-to-trigger-the-webhook-node). 단 **서버→서버 요청이라 CORS는 시험되지 않는다**(브라우저가 아님). 문서도 '새 워크플로우를 만들어' HTTP Request 노드를 두라고 안내 → 별도 '시험용' 워크플로우 권장 | 2026-09-24 | d1-p3 |
| F52 | 코드 작성 없이 브라우저에서 POST + CORS(preflight 포함)를 시험하는 것이 현실적인가 | 추가(d1-p3) | 확인 불가 — 강사 직접 시험 필요 | 판단: **수강생 실습으로는 비현실적**. ① 주소창은 GET만(F50), ② HTML form 제출은 페이지 이동이라 CORS 검사가 일어나지 않아 CORS 시험이 안 됨(게다가 HTML을 작성해야 함), ③ 개발자 도구 Console의 `fetch(…)` 한 줄은 코드 입력이다, ④ 웹 API 도구 Hoppscotch(hoppscotch.io)의 'Browser' interceptor는 브라우저 fetch를 써서 CORS가 실제로 적용됨(https://docs.hoppscotch.io/documentation/features/interceptor — 제3자 도구, 보조 근거) — 코드는 없지만 외부 사이트라 교육망 차단 가능. **권장**: d1-p3에서는 GET 주소창(F49)과 HTTP Request 노드(F51)로 동작만 확인하고, CORS는 d1-p6에서 AI Studio 앱의 실제 호출로 확인. 강사 시연용으로 Hoppscotch Browser 모드 또는 Console fetch 한 줄을 쓸 수 있음. 시험: 교육망에서 hoppscotch.io 접속 가능 여부, POST JSON 시 preflight 204·응답 헤더 확인 | 2026-09-24 | d1-p3, d1-p6 |
| F53 | Publish 후 워크플로우를 고치면, 다시 Publish해야 Production URL에 반영된다 | 추가(d1-p3) | 확인 | "Publishing makes your workflow live and locks it to a specific version. Production executions will use this published version, not your latest edits." / "All edits remain in draft until you publish." (https://docs.n8n.io/build/understand-workflows/save-and-publish-workflows/). 소스도 Production 웹훅은 `activeVersion`(게시된 버전)의 노드 설정(CORS 포함)을 읽는다(`live-webhooks.ts`). **교안 서술**: "Allowed Origins 등 설정을 바꾼 뒤에는 `Publish`를 다시 눌러야 Production URL에 적용된다" | 2026-09-24 | d1-p3, d1-p6, d2-p2 |
| F54 | 최신 노드 typeVersion: Webhook, Respond to Webhook | 추가 | 확인 | n8n@2.40.6(2026-09-24 stable·Latest 릴리스) 소스: Webhook `version: [1, 1.1, 2, 2.1]`, `defaultVersion: 2.1` (https://github.com/n8n-io/n8n/blob/n8n@2.40.6/packages/nodes-base/nodes/Webhook/Webhook.node.ts) / Respond to Webhook `version: [1, 1.1, 1.2, 1.3, 1.4, 1.5]`, `defaultVersion: 1.5` (https://github.com/n8n-io/n8n/blob/n8n@2.40.6/packages/nodes-base/nodes/RespondToWebhook/RespondToWebhook.node.ts). Webhook 2.1부터 Respond에 'Streaming' 선택지가 붙음. workflows/*.json은 Webhook 2.1, Respond to Webhook 1.5 권장. Cloud 인스턴스의 실제 버전은 강사가 확인 | 2026-09-24 | d1-p3 외 Import 전 교시 |

## n8n 기타

| # | 확인할 서술 | 출처 | 상태 | 근거 | 확인일 | 관련 교시 |
|---|---|---|---|---|---|---|
| F40 | n8n Cloud 무료 체험 기간(일수)과 종료 시 동작 — 수강생 개인 계정과 **강사 시연 계정 모두** Cloud 사용(Q1) | 제안서 2·11절 | 미확인 | | | d1-p1, 운영 |
| F41 | 워크플로우 JSON을 가져오면 자격 증명이 비어 있어 노드마다 다시 골라야 한다(ID 없을 때의 동작) | D7 | 확인 불가 — 강사 직접 시험 필요 | 문서: "Exported workflow JSON files include credential names and IDs." (https://docs.n8n.io/build/manage-workflows/export-and-import/ 경고 상자). '비어 있다'는 단정은 근거 없음. 소스(`useNodeHelpers.ts`, 2.40.6)상 JSON의 자격 증명 참조는 남고, 내 계정에 같은 ID가 있으면 그대로 쓰며, 없으면 이름으로 대조해 노드에 경고를 띄운다(예: "Credentials with name {name} do not exist for {type}." / "Credentials for {type} are not set."). **교안 권장 서술**: "가져온 뒤 경고 표시가 뜬 노드를 열어 Credential 칸에서 내 자격 증명을 고른다". 시험: ① credentials 블록을 지운 JSON, ② 남긴 JSON을 각각 Cloud에 Import → 노드 경고 문구·자동 선택 여부 확인 | 2026-09-24 | 전 교시 Import |
| F42 | Gemini 구성: Basic LLM Chain(`chainLlm`, 교안 이름 'AI 안내문 작성') + `Google Gemini Chat Model`(`lmChatGoogleGemini`) 하위 노드, 자격 증명 'Google Gemini(PaLM) API'(API 키). 최신 버전의 노드 이름·typeVersion·모델 목록(기존 교안은 `models/gemini-2.5-flash`) | Q2 | 미확인 | | | d1-p2, d2-p1, d2-p6, opt-pdf |
| F43 | 기관 설치형(자체 서버) n8n 전환 방법의 공식 안내 문서 | 제안서 2절 | 미확인 | | | d2-p3 |
| F44 | n8n Form(대체 경로)으로 같은 워크플로우를 받을 수 있다 | 제안서 2절 | 미확인 | | | d1-p4 플랜 B |
| F45 | Gemini 캔버스 웹 미리보기에서 외부 주소 호출이 가능하다 | 제안서 2절 | 미확인 | | | d1-p4 플랜 B |
| F46 | 기존 교안의 영문 UI 문구(`Execute workflow`, `Create workflow`, 활성화 스위치, `Form URLs` 등)가 현재 n8n Cloud 화면과 같다 | 기존 교안 capture-guide.md | 수정 필요 | 2.40.6 화면 문구 소스(`packages/frontend/@n8n/i18n/src/locales/en.json`): `Execute workflow` ✅, `Create workflow` ✅, `Listen for test event` ✅, `Stop Listening`, `Test URL`/`Production URL`/`Webhook URLs` ✅, `Form URLs`(Form Trigger) ✅. **활성화 스위치 ❌ → `Publish` 버튼**(F22). 문서 본문은 `Execute Workflow`(대문자)로도 쓰나 화면은 `Execute workflow`. 영향: legacy day1/08.html 등 '활성화 스위치 켜기' 문구 전부 | 2026-09-24 | d1-p2 외 전 교시 |
| F47 | n8n에서 워크플로우 JSON 가져오기(Import) 메뉴 위치와 이름(파일 가져오기, 붙여넣기) | D7 | 확인 | 워크플로우 캔버스 오른쪽 위 **…(점 세 개) 메뉴 → `Import` → `From file`**(또는 `From URL`). 근거: 2.40.6 소스 `ActionsDropdownMenu.vue`·`en.json`("menuActions.import": "Import", "menuActions.importFromFile": "From file", 내보내기는 "Export JSON"). 문서(https://docs.n8n.io/build/manage-workflows/export-and-import/#from-the-editor-ui-menu)는 아직 **Import from File / Import from URL / Download**로 적혀 있어 화면과 다름 → 교안은 화면(소스) 표기 사용, 강사 캡처로 최종 확인. 붙여넣기: JSON을 복사해 캔버스에서 `Ctrl + v`(문서 Copy-Paste 절) | 2026-09-24 | 전 교시 Import |
| F48 | Webhook 노드 CORS 옵션의 JSON 키가 `options.allowedOrigins`이다(verify.py가 이 키로 경고함) | verify.py | 확인 | 노드 로더가 CORS 옵션을 `options` 컬렉션 맨 앞에 끼워 넣는다(`packages/core/src/nodes-loader/directory-loader.ts` applySpecialNodeParameters, name 'allowedOrigins'). 서버는 `webhookNode.parameters.options`에서 읽는다(`live-webhooks.ts`/`test-webhooks.ts` findAccessControlOptions). → JSON: `"parameters": { "options": { "allowedOrigins": "*" } }`. 기본값이 `*`이라 키가 없어도 서버는 요청 Origin을 허용한다 — verify.py 경고는 '명시 권장' 수준이 맞음 | 2026-09-24 | d1-p3, d2-p2 |

## d1-p3 작성 중 추가 (미확인 — 강사 시험 또는 다음 fact-checker 실행)

| # | 확인할 서술 | 출처 | 상태 | 근거 | 확인일 | 관련 교시 |
|---|---|---|---|---|---|---|
| F55 | 노드 추가 검색에서 `Webhook`을 입력하면 트리거 `Webhook` 항목이 나온다(검색 결과 표기) | d1-p3 | 미확인 | | | d1-p3 |
| F56 | Webhook 노드 `HTTP Method` 기본값이 `GET`이고 `Path` 칸에 `hello`를 입력할 수 있다 | d1-p3 | 미확인 | | | d1-p3 |
| F57 | Respond to Webhook의 `Respond With` = `JSON`, `Response Body`에 `{{ }}` 표현식을 섞은 JSON을 쓰면 값이 채워져 응답된다 | d1-p3 | 미확인 | | | d1-p3 |
| F58 | 주소창에 `?이름=홍길동`처럼 한글 쿼리를 붙여도 `$json.query.이름`으로 꺼낼 수 있다 | d1-p3 | 미확인 | | | d1-p3, d2-p2 |
| F59 | 노드 설정 창을 닫고 캔버스로 돌아가는 방법(창 바깥 클릭, `Back to canvas` 등 화면 표기) | d1-p3 리뷰 | 미확인 | | | 전 교시 |
| F60 | Webhook 노드 위쪽에서 `Test URL`/`Production URL`을 고르고 주소를 누르면 복사되는지(화면 구성) | d1-p3 리뷰 | 미확인 | | | d1-p3, d1-p6 |
| F61 | Publish 성공 후 버튼 자리 표시(예: `Published`)의 화면 표기 | d1-p3 리뷰 | 미확인 | | | 전 교시 |
| F62 | 두 워크플로우가 같은 경로·방식의 Webhook을 가질 때 두 번째 Publish가 실패하는지와 오류 문구(Import 복구 시 Unpublish 안내의 근거) | d1-p3 리뷰 | 미확인 | | | 전 교시 Import |
| F63 | Respond to Webhook에서 `Respond With`를 `JSON`으로 바꾸면 `Response Body`에 예시 글이 미리 들어 있는지, Expression 토글이 마우스를 올려야 보이는지 | d1-p3 리뷰 | 미확인 | | | d1-p3 |

## 변경 이력

| 날짜 | 항목 | 변경 | 작성 |
|---|---|---|---|
| 2026-09-24 | 전체 | 목록 최초 작성(0회차 세션) | main |
| 2026-09-24 | F40, F42, F46~F48 | Q1·Q2 결정 반영, 기존 교안 UI 문구·Import·CORS 키 항목 추가 | main |
| 2026-09-24 | F20~F27, F41, F46~F48 확인, F49~F54 신규 | d1-p3 대비 확인(n8n 2.40.6 소스·docs.n8n.io 대조). 확인 13 / 수정 필요 3(F21·F22·F46: 활성화→Publish) / 확인 불가 2(F41·F52). 코드 없는 Webhook 시험 방법 항목 추가 | fact-checker |
| 2026-09-24 | F55~F58 신규, 확인 건수 정정(12→13) | d1-p3 작성 중 나온 UI 표기·한글 쿼리 항목 추가(미확인). D28(주소창 GET), D29(Publish) 반영 | main |
