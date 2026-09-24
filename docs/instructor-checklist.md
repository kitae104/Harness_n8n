# 강사 수동 확인 목록 (instructor-check)

verify.py는 **구조만** 검사한다. 실제 n8n·AI Studio에서 동작하는지는 사람이 확인해야 한다.
교시 status가 `instructor-check`이면 아래 공통 항목과 그 교시 항목을 확인한 뒤 `done`으로 바꾼다.
Claude 세션은 이 확인을 대신할 수 없다. 확인 결과를 사용자에게 받아 이 파일과 progress.md에 기록한다.

## 공통 (워크플로우가 있는 교시)

- [ ] n8n Cloud(최신 버전)에서 `workflows/{id}.json`을 Import → 오류 없이 열림
- [ ] 교안 Import 안내에 적힌 노드들만 자격 증명을 다시 골라 연결하면 실행됨(빠진 노드 없음)
- [ ] 자리표시자(`여기에_본인_시트_ID` 등)를 바꾸면 실행됨
- [ ] Webhook이 있으면: `Publish` → Production URL로 브라우저 앱에서 호출 → 응답 수신(CORS 오류 없음)
- [ ] 실행 후 다시 Export한 JSON과 저장소 JSON의 노드 `type`·`typeVersion`이 같음(다르면 저장소 JSON 갱신)
- [ ] 교안의 영문 UI 문구가 현재 화면과 같음

## 공통 (프롬프트가 있는 교시)

- [ ] AI Studio Build 모드에서 `prompts/*.md`의 프롬프트를 그대로 붙여 넣어 3회 생성 → 3회 모두 의도한 화면
- [ ] 생성된 앱이 data-contract의 키 이름으로 전송·표시함
- [ ] 프롬프트 파일의 `## 검증 기록` 표에 날짜·모델·결과를 적음

## 공통 (모든 교시)

- [ ] 캡처 촬영 완료(`python scripts/apply_captures.py --list`에 대기 0개)
- [ ] 캡처에 실제 개인정보·API 키·Webhook 고유 주소가 보이지 않음
- [ ] 50분 안에 끝나는지 강사가 직접 따라 해 봄(느린 수강생 기준 1.5배)

## 교육 1주 전 (전 교시)

- [ ] **n8n Cloud 당시 안정 버전 기준으로 캡처·JSON 최종 확인**(버전 고정이 불가하므로)
- [ ] AI Studio 화면·무료 한도 재확인
- [ ] 교육망 예외 도메인 요청 반영 여부 확인(제안서 5절 목록 + fact-check F11)
- [ ] `python scripts/verify.py --all` 통과, `python scripts/build.py`로 인쇄 교재 재생성

## 교시별 추가 항목

| 교시 | 확인할 것 |
|---|---|
| d1-p3 | 교안 그대로 따라 해 보기: Webhook(GET, `hello`) → Respond to Webhook(JSON, 표현식) → Test URL을 주소창에 `?이름=홍길동` 붙여 호출 → Publish → Production URL 호출. 확인할 표기: 노드 검색 결과(F55), HTTP Method 기본값·Path(F56), Respond With/Response Body/Expression(F57), 한글 쿼리 `이름`(F58), Webhook 노드 위쪽 Test URL/Production URL 선택 위치. 오류 문구 두 개(F50)가 교안과 같은지, Test URL 대기 시간이 2분(120초)인지(F21) |
| d1-p2 | 교안 그대로 Import → 시트(sheets.new, 머리글 6칸)·Gmail·Gemini 연결 → Execute workflow → 표현식·샘플 값 고쳐 보기가 **40분 안에** 끝나는지. `models/gemini-3.8-flash`가 새 API 키 계정 목록에 보이는지(F42), Gemini 자격 증명 저장 흐름(F73), `Use Gateway credits` 표시 여부(F71), 한국어 계정 새 시트 탭 이름 `시트1`(F72), Gmail 안내 문구가 빠지는지(F66) |
| d1-p4 | 템플릿(`prompts/d1-p4-minwon-app.md`)을 붙여 3회 생성 → 3회 모두 칸 5개·종류 목록·접수하기·`WEBHOOK_URL` 생성(F76 한국어 프롬프트). 보내기 버튼 표기, `Apps` 목록 자동 저장(F77), 생성 소요 시간, 수강생 20명 동시 생성 시 한도(F7). 플랜 B(n8n Form / Gemini Canvas, F44·F45) 동작 |
| d1-p5 | 요청 1~3을 차례로 보내 칸 이름·`WEBHOOK_URL`이 유지되는지. 연습 오류 1·2가 만들어지는지/AI가 거절·자가 수정하는지(F84), 오류 글 위치와 복사 가능 여부(F85), 오류 고치기 버튼 표기(F8), 되돌리기 버튼(F77), 대화 패널 위치·Annotation 도구(F82), 요청 10회 전후 한도 화면(F86) |
| d1-p6 | **먼저 `docs/instructor-kit/f4-test.md` 시험(F4)** — 결과표를 Claude 세션에 전달. 그 뒤 교안 그대로 따라 하기 |
| d1-p7 | 교안 그대로 16:30까지 5단계 도달 가능한지. 접수번호 001→002 증가, 동시 접수 시 중복 정도. 시간대 설정 화면(F100), Get Row(s)·Always Output Data·Execute Once(F92~F94), JSON 모드 한 줄 표현식(F102), Cell Format 선택지 표기(F103), 선 위 `+` 끼워 넣기(F104), 새 머리글 불러오기(F97), 한국어 계정 시트의 날짜·접수번호 서식(F101) |
| d2-p2 | 조회용 GET Webhook에 한글 쿼리 키(`접수번호`)가 문제없이 전달됨 |
| d2-p3 | 공유 링크를 다른 계정(로그인 안 한 상태 포함)에서 열었을 때의 동작 |
| opt-voice | 공유 링크에서 마이크 권한 요청이 뜨는지 |
| opt-pdf | 가상 공문 PDF 업로드 → 요약 수신 |

## fact-checker가 넘긴 직접 시험 항목 (1회차, 2026-09-24)

- [ ] F41: 자격 증명 블록을 **뺀** JSON과 **남긴** JSON을 각각 Cloud에 Import → 노드 경고 문구, 자격 증명 자동 선택 여부
- [ ] F24·F52: 실제 앱(또는 Hoppscotch Browser 모드)에서 JSON 본문 POST → preflight 204·CORS 헤더·Respond to Webhook 응답 도착. Allowed Origins를 다른 주소 하나로 바꾸면 막히는지. Test URL(대기 중)·Production URL 모두 → **d1-p6 교안 근거**
- [ ] F52: 교육망에서 hoppscotch.io 접속 가능 여부(플랜 B 후보)
- [ ] F49·F50: Chrome 주소창으로 Webhook 호출 시 응답 표시 모양, 두 번 실행되지 않는지, POST 주소일 때 오류 문구
- [ ] F22·F46·F47: 수강생 Cloud 인스턴스에서 Publish 버튼·확인 창, `…` → `Import` → `From file` 메뉴 캡처, 인스턴스 버전 확인
- [ ] F27: POST 접수·GET 조회 Webhook 두 개를 한 워크플로우에 두고 Test 모드에서 번갈아 시험, Publish 시 충돌 없음 → **d2-p2 근거**
- [ ] F21: 120초 대기·1회 호출이 수업에서 어떻게 느껴지는지, Production 404 안내에 여전히 'toggle' 문구가 나오는지
- [ ] F51: 별도 시험용 워크플로우의 HTTP Request 노드로 JSON POST 해 보기

## fact-checker가 넘긴 직접 시험 항목 (2회차, d1-p2 대비)

- [ ] 새 API 키 계정의 Gemini Chat Model `Model` 목록에 `models/gemini-3.8-flash`·`models/gemini-3.5-flash-lite`가 보이고 실행되는지, `gemini-2.5-flash`는 어떤지
- [ ] 무료 한도에서 수강생 20명이 동시에 실행해도 429 오류가 나지 않는지
- [ ] 한국어 구글 계정으로 새 시트를 만들 때 첫 탭 이름이 `시트1`인지, 머리글 없을 때 `Map Each Column Manually` 화면
- [ ] Import한 JSON(`documentId` mode id, `sheetName` mode name `시트1`)이 그대로 동작하는지
- [ ] `Sign in with Google` 동의 화면(권한 체크박스, 확인되지 않은 앱 경고), 교육망에서 accounts.google.com 팝업이 열리는지
- [ ] 자격 증명 없이 Import한 노드를 열었을 때 칸·버튼 표기(`Credential for …`/`Select Credential`/`Connect to …`) 캡처
- [ ] Gemini 자격 증명 창에 `Use Gateway credits`가 뜨는지, 체험 크레딧 금액과 지원 모델
- [ ] Sheets `From list`/`From List` 대소문자
- [ ] Gmail 메일 끝 n8n 안내 문구가 `appendAttribution:false`로 빠지는지

## fact-checker가 넘긴 직접 시험 항목 (3회차, AI Studio)

- [ ] F4: 미리보기·공유 URL·게시 주소 각각에서 n8n Test URL로 POST → 성공 여부와 `headers.origin` 값 기록. 실패 시 콘솔에서 CSP/CORS 구분, 서버 쪽 호출 요청(F80) 시험 → **d1-p6 근거**
- [ ] F76: 한국어 프롬프트로 생성·수정, 화면 글자 한국어 여부, 음성 입력 한국어
- [ ] F77: 되돌리기/체크포인트 버튼 표기와 동작, 새로고침 후 유지, Apps 목록 자동 저장
- [ ] F8: 일부러 코드를 망가뜨려 오류 화면·자동 수정 버튼 표기 캡처 → **d1-p5 근거**
- [ ] F7: 한 교시 분량(생성 1 + 수정 5~10) 부하, 한도 메시지 문구 캡처(하루 한도는 태평양 시간 자정 초기화)
- [ ] F3: 로그아웃(시크릿 창)으로 공유 URL 열기 — 로그인 필요 여부, 공개 범위 선택지 표기 → **d2-p3 근거**
- [ ] F1·F79: 왼쪽 메뉴 Build 항목, Share·Publish 위치, ZIP 다운로드 버튼 캡처
- [ ] F6: 개인 계정으로 Starter Tier Publish 시험
- [ ] F9·F10: Chrome에서 마이크 음성 인식, PDF 업로드 후 n8n 전송·파일 크기 한도 → **opt 교시 근거**
- [ ] F11: 교육망 PC에서 개발자 도구 Network 탭으로 막히는 주소 수집(초기 목록: aistudio.google.com, ai.studio/*.ai.studio, *.run.app, *.usercontent.goog, accounts.google.com, generativelanguage.googleapis.com, esm.sh, cdn.jsdelivr.net, gemini.google.com, *.app.n8n.cloud)
- [ ] F44·F45: n8n Form 한글 필드 이름, Canvas에서 n8n 호출 가능 여부
- [ ] F2: 기관(학교) 계정에서 AI Studio 차단 여부

## fact-checker가 넘긴 직접 시험 항목 (4회차, d1-p5·d1-p6)

- [ ] F84: "오류를 일부러 만들어 줘(고치지 말고)" 두 요청에 AI가 따르는지·거절하는지·스스로 고치는지
- [ ] F8·F85: 오류 화면(미리보기 오류 글, 대화 패널 버튼 `Fix errors`/`Auto-fix` 등, 오른쪽 아래 화살표) 캡처, 오류 글 마우스 선택·복사 가능 여부, 캡처 이미지 붙여 넣기
- [ ] F77: 되돌리기 버튼 표기·위치, 어느 요청의 버튼을 누르면 무엇이 사라지는지
- [ ] F82: 대화 패널·입력창 위치, 미리보기 탭 이름, Annotation 도구 위치·`Add to chat`
- [ ] F86: 요청 10회 전후 https://aistudio.google.com/rate-limit 에 잡히는지, 한도 초과 화면
- [ ] F87: Edit Fields에 한글 필드를 끌어 놓았을 때 이름 `body['이름']`·값 `{{ $json.body['이름'] }}` 모습 캡처, 이름만 `이름`으로 고친 뒤 출력
- [ ] F88: 교실 브라우저 n8n Cloud에서 워크플로우 간 노드 복사·붙여 넣기, 붙인 `시트에 기록`의 Credential·Document 유지
- [ ] F60·F90: Webhook URL 누르면 복사되는지(`Copied to clipboard`), Test/Production URL 전환 위치, `Execute workflow` 버튼 위치와 기다리는 표시
- [ ] F91: `d1-p6.json`(괄호 표기)을 Import해 앱에서 보낸 다섯 값이 시트에 모두 채워지는지

## 확인 기록

| 날짜 | 교시 | 확인자 | 결과 | 비고 |
|---|---|---|---|---|
