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
| d1-p4 | 플랜 B(n8n Form / Gemini 캔버스) 경로가 실제로 동작 |
| d1-p7 | 같은 날 여러 건 접수 시 접수번호 순번(NNN)이 겹치지 않음 |
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

## 확인 기록

| 날짜 | 교시 | 확인자 | 결과 | 비고 |
|---|---|---|---|---|
