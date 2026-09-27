# 글꼴

| 파일 | 내용 |
|---|---|
| `nanum-pen-subset.woff` | 나눔손글씨 펜(Nanum Pen Script). `hand-text.txt`의 글자만 남긴 부분 글꼴(약 18KB) |
| `OFL-NanumPenScript.txt` | 글꼴 라이선스(SIL Open Font License 1.1) |
| `hand-text.txt` | 손글씨로 보이는 글자 목록 |

교육망에서 외부 웹폰트가 막힐 수 있어 글꼴을 사이트 안에 둔다(writing-guide: 외부 자원 금지).
손글씨는 짧은 표시에만 쓴다: CSS의 `참고`·`10분`·`촬영 예정`, 교안의 `자주 하는 실수` 제목, 첫 화면의 이름표·점심시간·시간표 아래 한 줄.

## 손글씨 글자를 새로 쓸 때

`hand-text.txt`에 글자를 더하고 다시 만든다. 원본 TTF는 저장소에 두지 않는다
(출처: https://github.com/google/fonts/tree/main/ofl/nanumpenscript).

```bash
python -m fontTools.subset NanumPenScript-Regular.ttf --text-file=assets/fonts/hand-text.txt --flavor=woff --output-file=assets/fonts/nanum-pen-subset.woff
```

목록에 없는 글자는 손글씨 대신 기본 글꼴로 보인다(깨지지는 않음).
