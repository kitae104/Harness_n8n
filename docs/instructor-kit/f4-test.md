# 강사 시험 F4 — AI Studio 앱에서 n8n Webhook으로 POST가 되는가 (약 10~15분)

d1-p6(앱 ↔ n8n 연동 ①) 교안의 근거가 되는 시험이다. 결과를 아래 "기록" 표에 적어 Claude 세션에 알려 주면 d1-p6의 FACT-CHECK 주석을 정리하고 교안을 확정한다.

준비물: d1-p4에서 만든 민원 접수 앱(빈 `WEBHOOK_URL` 상수가 있는 것), n8n Cloud 계정, 이 폴더의 `f4-test-workflow.json`.

## 절차

### A. n8n 준비 (3분)
1. n8n에서 `Create workflow` → `…` → `Import` → `From file` → `f4-test-workflow.json`.
2. `앱에서 받기` 노드를 열어 `Test URL`을 복사하고 `Listen for test event`를 누른다(2분 대기).

### B. 앱에 주소 넣기 (3분)
3. AI Studio에서 d1-p4 앱을 열고 대화 입력창에 보낸다:
   `코드 맨 위 WEBHOOK_URL 값을 "(복사한 Test URL)"로 바꿔 줘. 다른 부분은 바꾸지 마.`
4. 미리보기에서 가상 값(홍길동 / 010-1234-5678 / minwon@example.com / 생활 / 시험)으로 `접수하기`.

### C. 결과 기록
5. 앱 화면에 `TEST-001`과 "시험 성공 — 받은 이름: 홍길동 / origin: …"이 보이면 **성공**. origin 값을 적는다.
6. 실패하면(접수하지 못했습니다 등) 브라우저 `F12` → `Console` 탭의 빨간 글을 그대로 복사해 적는다. `CORS`, `Content Security Policy`, `blocked` 중 어떤 말이 있는지 본다.
7. n8n `Executions`(또는 캔버스 실행 결과)에서 `앱에서 받기` 출력의 `headers.origin`, `body` 모양을 캡처한다.

### D. 추가 확인 (각 2분, 가능한 만큼)
8. **Production URL**: n8n에서 `Publish` → `Production URL`로 3~5를 반복.
9. **CORS가 실제로 걸리는지**: `Allowed Origins (CORS)`를 `https://example.com`으로 바꾸고 다시 `Publish` → 접수하기가 **실패**하는지(실패해야 정상). 끝나면 `*`로 되돌리고 `Publish`.
10. **공유 링크**: 앱 오른쪽 위 `Share`로 링크를 만들어 시크릿 창에서 열고 접수하기(F3·F4).
11. **막혔을 때의 우회**: 6에서 실패했다면 대화 입력창에 `n8n 주소 호출은 서버 쪽 코드에서 하도록 바꿔 줘. 다른 부분은 바꾸지 마.`를 보내고 4~5를 다시 한다(F80).

## 기록

| # | 상황 | 결과(성공/실패) | origin 값 또는 오류 문구 | 비고 |
|---|---|---|---|---|
| 5 | 미리보기 → Test URL | | | |
| 8 | 미리보기 → Production URL | | | |
| 9 | Allowed Origins = example.com (실패해야 정상) | | | |
| 10 | 공유 링크(시크릿 창) → Production URL | | | |
| 11 | 서버 쪽 호출로 바꾼 뒤 | | | |

## 결과에 따라 d1-p6이 달라지는 부분

| 결과 | d1-p6 교안 |
|---|---|
| 5·8 성공 | 현재 초안 그대로(브라우저에서 바로 호출). origin 값은 d2-p3 "허락 명단 좁히기"에 사용 |
| 5 실패 + 11 성공 | d1-p6 기본 경로를 "서버 쪽 호출 요청"으로 바꾸고, CORS 설명은 개념으로만 남김 |
| 5·11 모두 실패 | d1-p6 플랜 B(n8n Form)로 전환 검토 — Claude 세션에 알려 주기 |
