# 앱에 n8n 주소 넣기

- 사용 교시: d1-p6 (1일차 6교시 앱 ↔ n8n 연동 ①)
- 전제: d1-p4 프롬프트로 만든 앱(코드 맨 위에 빈 `WEBHOOK_URL` 상수가 있음), d1-p5에서 다듬은 화면
- 순서: **Test URL로 먼저 시험 → 성공하면 n8n `Publish` → Production URL로 바꾸기** (D28, D38)
- 보내는 JSON 키는 `docs/data-contract.md`의 한글 키(이름·연락처·이메일·종류·상세설명) 그대로다.

## 복사할 프롬프트

### 1) 시험용 — Test URL 넣기

```text
코드 맨 위 WEBHOOK_URL 값을 "{Test URL}"로 바꿔 줘. 다른 부분은 바꾸지 마.
```

### 2) 실제 사용 — Production URL로 바꾸기 (n8n에서 Publish한 뒤)

```text
코드 맨 위 WEBHOOK_URL 값을 "{Production URL}"로 바꿔 줘. 다른 부분은 바꾸지 마.
```

### 3) 막혔을 때 — 브라우저에서 n8n을 부르지 못할 때만

```text
접수하기를 누르면 "접수하지 못했습니다"가 떠. n8n 주소 호출은 서버 쪽 코드에서 하도록 바꿔 줘. WEBHOOK_URL 값과 보내는 JSON의 키 이름은 바꾸지 마.
```

## 바꿀 자리

- `{Test URL}`: n8n `민원 받기` 노드의 `Test URL`(주소 안에 `webhook-test`가 있음). 따옴표 안에 주소만 붙여 넣는다.
- `{Production URL}`: n8n에서 `Publish`한 뒤 같은 노드의 `Production URL`(주소 안에 `/webhook/`가 있음).
- 중괄호 `{ }`는 지우고 주소만 남긴다. 따옴표 `" "`는 남긴다.

## 예상 결과

- 1) 뒤 n8n에서 `Listen for test event`를 누르고 앱에서 `접수하기`를 누르면, n8n `민원 받기` 노드에 초록 표시가 생기고 출력의 `body`에 다섯 값이 보인다.
- 앱 화면은 접수 완료 화면으로 넘어가지만 접수번호 자리는 비어 있을 수 있다(접수번호는 7교시에 만든다).
- 2) 뒤에는 `Listen for test event`나 `Execute workflow`를 누르지 않아도 언제든 `접수하기`가 동작하고, 구글 시트에 줄이 쌓인다.
- 3)은 fact-check F80 근거. 강사 시험(F4, `docs/instructor-kit/f4-test.md`) 결과에 따라 기본 경로가 될 수도 있다.

## 검증 기록

| 날짜 | 검증자 | 도구·모델 | 결과 |
|---|---|---|---|
