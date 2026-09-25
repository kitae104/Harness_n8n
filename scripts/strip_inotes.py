"""강사 표시(inote)를 보여 주거나 지운다.

강사 표시는 강의 준비 기간에만 쓰는 임시 표시다(수강생용 내용이 아님).
  - <span class="inote" data-inote="check" data-ref="F..">  본문 안 확인 항목
  - <span class="inote" data-inote="prep">                   본문 안 준비 항목
  - <div class="inote" id="inote-{id}-0" data-inote="prep">   교시 맨 위 요약 상자

사용법:
  python scripts/strip_inotes.py --list              # 모든 표시를 교시별로 보여 줌(파일은 그대로)
  python scripts/strip_inotes.py --dry-run           # 지울 개수만 보여 줌
  python scripts/strip_inotes.py                     # 모든 교안에서 지움
  python scripts/strip_inotes.py --lesson d1-p3      # 한 교시만 지움(여러 번 쓸 수 있음)
  python scripts/strip_inotes.py --kind prep         # 준비 표시만 지움(check / prep)
  python scripts/strip_inotes.py --ref F42           # 특정 fact-check 번호 표시만 지움(확인 끝난 항목)

지운 뒤에는 python scripts/verify.py --all 과 python scripts/build.py 를 실행한다.
주의: python3 는 이 PC에서 스토어 껍데기 명령이므로 반드시 python 을 쓴다.
"""
import argparse
import html
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
RE_OPEN = re.compile(r'<(span|div)\b[^>]*\bclass="inote"[^>]*>')
RE_TAG = re.compile(r"<(/?)(span|div)\b[^>]*>")


def find_notes(text: str):
    """(시작, 끝, 여는 태그 문자열) 목록. 같은 태그의 중첩을 세어 짝이 맞는 닫는 태그까지."""
    out = []
    pos = 0
    while True:
        m = RE_OPEN.search(text, pos)
        if not m:
            return out
        tag = m.group(1)
        depth, i = 1, m.end()
        while depth:
            t = RE_TAG.search(text, i)
            if not t:
                raise ValueError(f"닫는 </{tag}>를 찾지 못함: {text[m.start():m.start()+80]}")
            if t.group(2) == tag:
                depth += -1 if t.group(1) else 1
            i = t.end()
        out.append((m.start(), i, m.group(0)))
        pos = i


def attr(open_tag: str, name: str) -> str:
    m = re.search(rf'\b{name}="([^"]*)"', open_tag)
    return m.group(1) if m else ""


def plain(fragment: str) -> str:
    """표시 안의 글만(머리표 '강사 확인 F..' 는 뺌)."""
    t = re.sub(r'<b class="inote-tag">.*?</b>', "", fragment, count=1)
    t = re.sub(r"<li>", "\n    · ", t)
    t = re.sub(r"<[^>]+>", "", t)
    return re.sub(r"[ \t]+", " ", html.unescape(t)).strip()


def selected(open_tag: str, kinds, refs) -> bool:
    if kinds and attr(open_tag, "data-inote") not in kinds:
        return False
    if refs:
        have = set(attr(open_tag, "data-ref").split(","))
        if not have & refs:
            return False
    return True


def strip(text: str, kinds, refs) -> tuple[str, int]:
    notes = [n for n in find_notes(text) if selected(n[2], kinds, refs)]
    for start, end, _ in reversed(notes):
        # 표시 앞에 붙인 공백 한 칸, 또는 상자 한 줄 전체(앞 들여쓰기·뒤 줄바꿈)를 함께 지운다
        line_start = text.rfind("\n", 0, start) + 1
        if text[line_start:start].strip() == "" and text[end:end + 1] == "\n":
            start, end = line_start, end + 1
        elif start > 0 and text[start - 1] == " ":
            start -= 1
        text = text[:start] + text[end:]
    return text, len(notes)


def main() -> int:
    ap = argparse.ArgumentParser(description="강사 표시(inote) 보기·지우기")
    ap.add_argument("--list", action="store_true", help="표시 목록만 보여 줌")
    ap.add_argument("--dry-run", action="store_true", help="지울 개수만 보여 줌")
    ap.add_argument("--lesson", action="append", default=[], help="이 교시만(여러 번 가능)")
    ap.add_argument("--kind", action="append", choices=["check", "prep"], default=[], help="이 종류만")
    ap.add_argument("--ref", action="append", default=[], help="이 fact-check 번호가 붙은 표시만(예: F42)")
    a = ap.parse_args()

    files = sorted((ROOT / "lessons").glob("*.html"))
    if a.lesson:
        files = [f for f in files if f.stem in a.lesson]
    kinds, refs = set(a.kind), set(a.ref)
    total = 0
    for f in files:
        text = f.read_text(encoding="utf-8")
        notes = [n for n in find_notes(text) if selected(n[2], kinds, refs)]
        if not notes:
            continue
        total += len(notes)
        if a.list:
            print(f"\n■ {f.stem} — {len(notes)}곳")
            for s, e, o in notes:
                print(f"  #{attr(o, 'id')} [{attr(o, 'data-inote')}{' ' + attr(o, 'data-ref') if attr(o, 'data-ref') else ''}] "
                      f"{plain(text[s:e])[:300]}")
            continue
        if a.dry_run:
            print(f"{f.stem}: {len(notes)}곳 지울 예정")
            continue
        new, n = strip(text, kinds, refs)
        f.write_text(new, encoding="utf-8", newline="\n")
        print(f"{f.stem}: {n}곳 지움")
    verb = "표시" if a.list else ("지울 예정" if a.dry_run else "지움")
    print(f"\n합계 {total}곳 {verb}")
    if not (a.list or a.dry_run) and total:
        print("다음: python scripts/verify.py --all → python scripts/build.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
