"""사이트 목차(index.html)와 인쇄용 교재(print/textbook.html)를 만든다.

사용법:  python scripts/build.py

- index.html: lessons.json 순서대로 목차. 아직 없는 교시는 링크 없이 "준비 중"으로 표시
- print/textbook.html: 존재하는 교시 HTML의 <main>을 시간표 순서로 이어 붙인 인쇄용 한 파일.
  브라우저로 열어 "PDF로 인쇄"하면 교시마다 새 페이지에서 시작한다(lesson.css의 @media print).
주의: python3 는 이 PC에서 스토어 껍데기 명령이므로 반드시 python 을 쓴다.
"""
import html
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "lessons.json").read_text(encoding="utf-8"))
COURSE = DATA["course"]["title"]
CSS = ["style.css", "lecture.css", "lesson.css"]

RE_MAIN = re.compile(r"<main\b[^>]*>.*?</main>", re.S)
RE_REL_ATTR = re.compile(r'(href|src)="(?!https?:|//|#|mailto:|tel:|data:|\.\./)([^"]+)"')


def head(title: str, css_prefix: str) -> str:
    links = "\n".join(f'<link rel="stylesheet" href="{css_prefix}assets/css/{c}">' for c in CSS)
    return (f'<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f"<title>{html.escape(title)}</title>\n{links}\n</head>\n")


def label(l) -> str:
    if l["period"] is None:
        return "선택"
    return f'{l["day"]}-{l["period"]}'


def build_index(lessons) -> str:
    rows = {1: [], 2: []}
    for l in lessons:
        path = ROOT / "lessons" / f'{l["id"]}.html'
        title = html.escape(l["title"])
        time = html.escape(l["time"].split("(")[0])
        if path.exists():
            item = (f'<li><a href="lessons/{l["id"]}.html"><span class="n">{label(l)}</span> '
                    f'{title} <span class="d">{time}</span></a></li>')
        else:
            item = f'<li><span class="toc-todo"><span class="n">{label(l)}</span> {title} (준비 중)</span></li>'
        rows[l["day"]].append(item)
    body = [f'<body class="lecture-mode">\n<main class="wrap">\n'
            f'<header class="page-head"><h1>{html.escape(COURSE)}</h1>'
            f'<p class="sub">2일(14시간) 중급 과정 — 화면은 AI가, 일은 n8n이</p></header>']
    for day in (1, 2):
        body.append(f'<section class="sec" id="day{day}"><h2 class="sec-title">{day}일차</h2>'
                    f'<ol class="toc">\n' + "\n".join(rows[day]) + "\n</ol></section>")
    body.append('<section class="sec" id="print"><h2 class="sec-title">인쇄용 교재</h2>'
                '<p><a href="print/textbook.html">인쇄용 교재 열기</a> — 브라우저에서 "PDF로 인쇄"하세요.</p></section>')
    body.append("</main>\n</body>\n</html>\n")
    return head(COURSE, "") + "\n".join(body)


def build_textbook(lessons):
    mains, toc = [], []
    for l in lessons:
        path = ROOT / "lessons" / f'{l["id"]}.html'
        if not path.exists():
            continue
        m = RE_MAIN.search(path.read_text(encoding="utf-8"))
        if not m:
            print(f"경고: {path.name}에 <main>이 없어 건너뜀")
            continue
        # lessons/ 기준 상대 경로를 print/ 기준으로 바꿈(같은 깊이이므로 ../로 시작하는 것은 그대로)
        block = RE_REL_ATTR.sub(lambda mm: f'{mm.group(1)}="../lessons/{mm.group(2)}"', m.group(0))
        mains.append(block)
        toc.append(f'<li>{label(l)} {html.escape(l["title"])}</li>')
    cover = (f'<section class="textbook-cover"><h1>{html.escape(COURSE)}</h1>'
             f'<p>2일(14시간) 중급 과정 · 인쇄용 교재</p></section>')
    toc_html = '<section class="textbook-toc"><h2>차례</h2><ol>' + "".join(toc) + "</ol></section>"
    body = '<body class="lecture-mode">\n' + cover + "\n" + toc_html + "\n" + "\n".join(mains) + "\n</body>\n</html>\n"
    return head(COURSE + " — 인쇄용 교재", "../") + body, len(mains)


def main() -> int:
    lessons = DATA["lessons"]
    (ROOT / "index.html").write_text(build_index(lessons), encoding="utf-8", newline="\n")
    (ROOT / "print").mkdir(exist_ok=True)
    text, n = build_textbook(lessons)
    (ROOT / "print" / "textbook.html").write_text(text, encoding="utf-8", newline="\n")
    print(f"index.html 생성 — 교시 {len(lessons)}개 중 작성된 {n}개 링크")
    print(f"print/textbook.html 생성 — 교시 {n}개 포함")
    return 0


if __name__ == "__main__":
    sys.exit(main())
