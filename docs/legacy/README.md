# 기존 교안 (참조 전용)

「AI를 활용한 나만의 비서 만들기(n8n)」 1·2기 교안. 이 과정(중급)의 선행 과정이며 디자인·JSON·도구의 기준이다.

- 원본 저장소: https://github.com/kitae104/PublicFlow (커밋 `de82744a4092c5189cf3ec42d5b8a297361b8b06`, 2026-09-24 복사)
- 배포 사이트: https://kitae-n8n.vercel.app
- 복사 범위: README, docs/*.md, tools/*.py, public/**/*.html, public/assets/*.css, public/downloads/*.json, vercel.json
- **제외**: 캡처 PNG(public/assets/img/), datas/(기관 공문 PDF) — 필요하면 원본 저장소에서 본다
- 이 폴더는 **수정하지 않는다.** 원본이 바뀌면 다시 복사하고 위 커밋 해시를 갱신한다.

## 이 과정에서 가져다 쓴 것

| 기존 | 이 과정 |
|---|---|
| public/assets/style.css, lecture.css | assets/css/ 에 그대로 복사(디자인 기준) |
| tools/apply_captures.py | scripts/apply_captures.py (경로만 변경) |
| tools/check_site.py 의 검사 | scripts/verify.py 에 흡수(외부 자원·script 금지, BOM, 금지 토큰) |
| public/downloads/*.json | 새 워크플로우 JSON을 만들 때 노드 정의의 기준 |

## 표기 대응 — 헷갈리기 쉬움

| 기존 교안 | 뜻 | 이 과정 |
|---|---|---|
| 01~08강 (day1/01.html …) | 1일차 강의 8개 | d1-p2 복습의 바탕 |
| P1~P4 (day2/p1.html …) | 2일차 **프로젝트** 4개 | 새 과정의 `d2-p1`(2일차 **1교시**)과 다름 |
| P1 공문서 요약 서비스 | 프로젝트 | opt-pdf의 바탕 |
| 08강 민원 입력 폼(Form Trigger) | 1일차 완성본 | d1-p6에서 Form Trigger를 Webhook으로 바꿈 |
| 자격증명 | Credential | 자격 증명(띄어 씀) |

교시별로 참고할 파일은 `lessons.json`의 `legacy_refs`에 있다.
