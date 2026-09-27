"""사이트 목차(index.html)와 인쇄용 교재(print/textbook.html)를 만든다.

사용법:  python scripts/build.py

- index.html: 첫 화면(공책 표지) — 과정 소개, 완성 서비스 흐름 그림, 학교 시간표 모양의 이틀 시간표(없는 교시는 "준비 중"). 스타일은 assets/css/home.css
- instructor-notes.html: 교안 안의 강사 표시(inote)를 교시별로 모은 준비 목록. 표시가 하나도 없으면 만들지 않고 지운다
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


def head(title: str, css_prefix: str, css=None) -> str:
    links = "\n".join(f'<link rel="stylesheet" href="{css_prefix}assets/css/{c}">' for c in (css or CSS))
    return (f'<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f"<title>{html.escape(title)}</title>\n{links}\n</head>\n")


def label(l) -> str:
    if l["period"] is None:
        return "선택"
    return f'{l["day"]}-{l["period"]}'


# ── 첫 화면(index.html) ─────────────────────────────────────
# 과정 소개 문구는 docs/proposal.md 3·5·8·9절을 수강생 눈높이로 옮긴 것이다.
# 첫 화면 그림은 2일차 완성 서비스(workflows/d2-p2.json)의 흐름을 n8n 노드 모양으로 그린 것.

FLOW_OUT = [  # (제목, 설명) — 앱 요청을 받은 n8n이 하는 일
    ("구글 시트", "접수 내용 기록"),
    ("Gmail", "담당자에게 배정 메일"),
    ("구글 캘린더", "처리 마감 등록"),
    ("Gemini", "민원인 안내문 작성"),
    ("텔레그램", "새 민원 알림"),
]


def _node(x, y, w, h, title, sub, kind, ports):
    """n8n 노드처럼 생긴 상자 하나. ports: [(cx, cy)] 연결점."""
    t = html.escape(title)
    s = html.escape(sub)
    ty = y + h / 2 - (4 if sub else -5)
    out = [f'<g class="node {kind}">',
           f'<rect class="box" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>',
           f'<rect class="bar" x="{x + 10}" y="{y + 12}" width="4" height="{h - 24}" rx="2"/>',
           f'<text class="nt" x="{x + 26}" y="{ty}">{t}</text>']
    if sub:
        out.append(f'<text class="ns" x="{x + 26}" y="{ty + 20}">{s}</text>')
    out += [f'<circle class="port" cx="{cx}" cy="{cy}" r="4.5"/>' for cx, cy in ports]
    out.append("</g>")
    return "".join(out)


def flow_svg(tall: bool) -> str:
    """완성 서비스 흐름 그림. tall=True는 좁은 화면(휴대폰)용 세로 배치."""
    wires, nodes = [], []
    if not tall:
        vb, cls = "0 0 820 420", "flow wide"
        nodes.append(_node(4, 158, 220, 104, "민원 접수 앱", "AI Studio로 만든 화면", "n-app", [(224, 210)]))
        nodes.append(_node(290, 176, 170, 68, "Webhook", "앱의 요청 받기", "n-hook", [(290, 210), (460, 210)]))
        wires.append('<path class="w" d="M224,210 L290,210" pathLength="1"/>')
        for i, (t, s) in enumerate(FLOW_OUT):
            y = 6 + i * 82
            cy = y + 31
            nodes.append(_node(540, y, 276, 62, t, s, "n-out", [(540, cy)]))
            wires.append(f'<path class="w" d="M460,210 C502,210 498,{cy} 540,{cy}" pathLength="1"/>')
        back = ('<path class="back" d="M375,244 C375,345 114,350 114,268" marker-end="url(#arr-w)"/>'
                '<text class="bl" x="245" y="352" text-anchor="middle">접수번호·안내문 회신</text>')
    else:
        vb, cls = "0 0 360 636", "flow tall"
        nodes.append(_node(40, 8, 280, 94, "민원 접수 앱", "AI Studio로 만든 화면", "n-app", [(180, 102)]))
        nodes.append(_node(95, 156, 170, 62, "Webhook", "앱의 요청 받기", "n-hook", [(180, 156), (180, 218)]))
        wires.append('<path class="w" d="M180,102 L180,156" pathLength="1"/>')
        for i, (t, s) in enumerate(FLOW_OUT):
            y = 272 + i * 72
            cy = y + 27
            nodes.append(_node(60, y, 280, 54, t, s, "n-out", [(60, cy)]))
            wires.append(f'<path class="w" d="M180,218 C180,252 24,236 24,274 L24,{cy - 14} '
                         f'Q24,{cy} 38,{cy} L60,{cy}" pathLength="1"/>')
        back = ('<path class="back" d="M265,187 C350,187 352,55 326,55" marker-end="url(#arr-t)"/>'
                '<text class="bl" x="318" y="136" text-anchor="end">접수번호 회신</text>')
    mid = "arr-t" if tall else "arr-w"
    defs = (f'<defs><marker id="{mid}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" '
            'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="ah"/></marker></defs>')
    return (f'<svg class="{cls}" viewBox="{vb}" role="img" aria-labelledby="flow-cap">'
            + defs + "".join(wires) + back + "".join(nodes) + "</svg>")


def _split(title: str):
    main, _, sub = title.partition(" — ")
    return main, sub


def _cell(l) -> str:
    """시간표 한 칸. 교안이 있으면 링크, 없으면 "준비 중"."""
    if l is None:
        return "<td></td>"
    main, sub = _split(l["title"])
    inner = f'<b>{html.escape(main)}</b>' + (f'<span class="ps">{html.escape(sub)}</span>' if sub else "")
    if (ROOT / "lessons" / f'{l["id"]}.html').exists():
        return f'<td><a href="lessons/{l["id"]}.html">{inner}</a></td>'
    return f'<td class="todo">{inner}<span class="ps">준비 중</span></td>'


def _opt(l) -> str:
    main, sub = _split(l["title"])
    inner = f'<b>{html.escape(main)}</b>' + (f' {html.escape(sub)}' if sub else "")
    if (ROOT / "lessons" / f'{l["id"]}.html').exists():
        return f'<li><a href="lessons/{l["id"]}.html">{inner}</a></li>'
    return f'<li class="todo">{inner} (준비 중)</li>'


DAY_THEME = {1: "n8n 다지기, 첫 앱, 그리고 연결", 2: "자동화 확장과 나만의 업무 서비스"}
LUNCH_AFTER = 3  # 오전 3교시 뒤 점심


def build_index(lessons, notes_total: int = 0) -> str:
    grid, extra = {}, []
    for l in lessons:
        if l["period"] is None:
            extra.append(_opt(l))
        else:
            grid[(l["day"], l["period"])] = l
    first = next((l for l in lessons if l["period"] == 1 and l["day"] == 1), lessons[0])

    rows = []
    for p in range(1, max(k[1] for k in grid) + 1):
        any_l = grid.get((1, p)) or grid.get((2, p))
        tm = html.escape(any_l["time"].split("~")[0]) if any_l else ""
        rows.append(f'<tr><th scope="row">{p}<small>{tm}</small></th>'
                    f'{_cell(grid.get((1, p)))}{_cell(grid.get((2, p)))}</tr>')
        if p == LUNCH_AFTER:
            rows.append('<tr class="lunch"><td colspan="3">점심시간</td></tr>')
    table = ('<div class="tt-wrap"><table class="timetable"><thead><tr><th scope="col">교시</th>'
             + "".join(f'<th scope="col">{d}일차<span class="ps">{DAY_THEME[d]}</span></th>' for d in (1, 2))
             + "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>")
    opt = (f'<div class="opt"><h3>선택 실습</h3><p>2일차 프로젝트 시간에 원하는 사람만, '
           f'또는 수료 뒤 혼자 해 보는 실습입니다.</p><ul>{"".join(extra)}</ul></div>') if extra else ""

    note = ""
    if notes_total:
        note = ('<div class="inote" data-inote="prep"><b class="inote-tag">강사 준비·확인</b>'
                f'교안 안에 강사가 확인할 표시가 {notes_total}곳 있습니다. '
                '<a href="instructor-notes.html">강사 준비 목록 열기</a> — 준비가 끝나면 '
                '<code>python scripts/strip_inotes.py</code>로 지우고 다시 build 하면 이 안내도 사라집니다.</div>')

    body = f'''<body class="home">
<header class="cover">
  <div class="cover-in">
    <div class="cover-text">
      <h1>{html.escape(COURSE)}</h1>
      <p class="lead">코딩 없이 앱 화면을 만들고, 이미 배운 n8n 자동화에 연결합니다.
      이틀 동안 민원 접수 서비스를 함께 완성하고, 내 업무로 만든 서비스 하나를 더 가지고 돌아갑니다.</p>
      <p class="cta"><a class="btn primary" href="lessons/{first["id"]}.html">1교시부터 시작하기</a>
      <a class="btn" href="#schedule">시간표 보기</a></p>
    </div>
    <dl class="label">
      <dt>과목</dt><dd>화면은 AI가, 일은 n8n이</dd>
      <dt>기간</dt><dd>2일, 14시간(중급)</dd>
      <dt>대상</dt><dd>n8n 기초 과정 수료 공무원</dd>
      <dt>메모</dt><dd class="hand">코딩은 몰라도 됩니다</dd>
    </dl>
  </div>
</header>

<main class="sheet">
  <section class="block" id="about">
    <h2>이 과정은</h2>
    <p class="intro">n8n으로 만든 자동화에는 동료나 민원인이 직접 쓸 수 있는 <b>입구</b>가 없었습니다.
    이 과정에서는 그 입구인 앱 화면을 Google AI Studio에 한국어 문장으로 부탁해 만들고,
    뒤에서 일하는 부분은 이미 익숙한 n8n이 맡도록 둘을 연결합니다.</p>
    <figure class="hero-flow">
      {flow_svg(False)}
      {flow_svg(True)}
      <figcaption id="flow-cap">이틀 뒤 완성하는 민원 접수 서비스입니다. 앱에서 접수하면 n8n이 기록·메일·마감 등록·안내문·알림을 처리하고, 접수번호를 앱 화면에 돌려줍니다.</figcaption>
    </figure>
    <div class="roles">
      <div class="role r-app">
        <h3>화면은 AI가</h3>
        <p class="tool">Google AI Studio Build</p>
        <ul>
          <li>문장으로 민원 접수 입력 화면 만들기</li>
          <li>“버튼을 크게 해 줘”처럼 말로 화면 고치기</li>
          <li>오류 문구를 복사해 AI에게 고쳐 달라고 하기</li>
          <li>처리 상태 조회 화면 추가하기</li>
        </ul>
      </div>
      <div class="role r-n8n">
        <h3>일은 n8n이</h3>
        <p class="tool">n8n 워크플로우</p>
        <ul>
          <li><code>Webhook</code>으로 앱이 보낸 접수 내용 받기</li>
          <li>구글 시트 기록, 담당자 메일, 캘린더 마감 등록</li>
          <li>Gemini로 민원인 안내문 쓰기, 유형별 담당자 나누기</li>
          <li>텔레그램 알림, 접수번호를 앱에 돌려주기</li>
        </ul>
      </div>
    </div>
  </section>

  <section class="block" id="schedule">
    <h2>이틀 시간표</h2>
    <p class="muted">교시를 누르면 그 시간의 웹 교안이 열립니다. 교시마다 50분입니다.</p>
    {table}
    <p class="hand-note">진도가 밀려도 괜찮아요. 교시마다 완성 파일이 있어요.</p>
    {opt}
  </section>

  <section class="block" id="ready">
    <h2>수업 전에 확인하세요</h2>
    <div class="cols3">
      <div>
        <h3>이런 분을 위한 과정입니다</h3>
        <p>「AI를 활용한 나만의 비서 만들기(n8n)」를 수료했거나, 트리거–처리–결과로 이어지는 n8n 워크플로우를 만들어 본 공무원.
        프로그래밍 경험은 없어도 됩니다.</p>
      </div>
      <div>
        <h3>준비물</h3>
        <ul>
          <li>개인 구글 계정</li>
          <li>텔레그램 계정</li>
          <li>기초 과정에서 쓰던 n8n(또는 강사가 안내하는 n8n)</li>
          <li>자동화하고 싶은 내 업무 한 가지</li>
        </ul>
      </div>
      <div>
        <h3>수업은 이렇게 진행합니다</h3>
        <ul>
          <li>교시마다 앞 10분은 왜 필요한지 설명, 나머지는 실습</li>
          <li>진도가 밀려도 교시별 완성 파일을 가져와 따라잡기</li>
          <li>웹 교안과 인쇄 교재를 함께 사용</li>
        </ul>
      </div>
    </div>
    <p class="promise"><b>실습에는 가상 자료만 씁니다.</b> 실제 민원, 공문, 실명, 연락처는 앱이나 n8n에 넣지 않습니다. 교안에 나오는 이름과 연락처도 모두 지어낸 것입니다.</p>
  </section>

  <section class="block" id="outcome">
    <h2>과정을 마치면 가져가는 것</h2>
    <ul class="outcomes">
      <li><h3>민원 접수 서비스</h3><p>앱에서 접수하면 시트에 기록되고, 담당자 메일과 캘린더 마감이 만들어지고, Gemini가 쓴 안내문과 접수번호가 앱에 표시됩니다.</p></li>
      <li><h3>내 업무 자동화 서비스</h3><p>내 부서 업무로 설계서를 쓰고 앱과 워크플로우를 만들어 발표합니다. 예: 현장점검 보고, 교육·행사 신청 접수, 회의록 정리.</p></li>
      <li><h3>설계서와 적용 계획</h3><p>입력–처리–출력 설계서, 개인정보 점검표, 부서에 적용할 때 확인할 항목을 정리해 갑니다.</p></li>
    </ul>
  </section>

  <footer class="foot">
    <p><a href="print/textbook.html">인쇄용 교재 열기</a> — 브라우저에서 “PDF로 인쇄”하면 교시마다 새 쪽에서 시작합니다.</p>
    <p class="muted">사용 도구: Google AI Studio, n8n, Gemini API, 구글 시트·Gmail·구글 캘린더, 텔레그램(모두 무료로 사용)</p>
    {note}
  </footer>
</main>
</body>
</html>
'''
    return head(COURSE, "", ["style.css", "lesson.css", "home.css"]) + body


def collect_notes(lessons):
    """교시별 (lesson, [(표시 id, 종류, 참조, 글)])."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from strip_inotes import find_notes, attr, plain
    out = []
    for l in lessons:
        path = ROOT / "lessons" / f'{l["id"]}.html'
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        items = [(attr(o, "id"), attr(o, "data-inote"), attr(o, "data-ref"), plain(text[s:e]))
                 for s, e, o in find_notes(text)]
        if items:
            out.append((l, items))
    return out


def build_notes(groups) -> str:
    total = sum(len(i) for _, i in groups)
    checks = sum(1 for _, i in groups for x in i if x[1] == "check")
    body = ['<body class="lecture-mode">\n<main class="wrap">\n'
            '<nav class="crumb"><a href="index.html">목차</a> › 강사 준비 목록</nav>'
            '<header class="page-head"><h1>강사 준비 목록</h1>'
            f'<p class="sub">교안 안의 강사 표시 {total}곳(확인 {checks}) — 수강생용 페이지가 아닙니다</p></header>',
            '<div class="note tip"><b>쓰는 법</b><ul>'
            '<li>항목의 [ ] 표시를 누르면 교안의 그 위치(노란 점선 상자)로 갑니다.</li>'
            '<li>확인 결과를 Claude 세션에 알려 주면 교안·fact-check에 반영합니다. 강사 직접 시험 전체 목록은 '
            '<code>docs/instructor-checklist.md</code>, 앱 → n8n 연결 시험은 <a href="docs/instructor-kit/f4-checklist.html">F4 시험 체크리스트</a>.</li>'
            '<li>확인이 끝난 표시만 지우기: <code>python scripts/strip_inotes.py --ref F42</code>, 한 교시만: '
            '<code>--lesson d1-p3</code>, 전부: 옵션 없이 실행. 그다음 <code>python scripts/build.py</code>.</li>'
            '</ul></div>']
    for l, items in groups:
        lis = []
        for nid, kind, ref, txt in items:
            badge = "준비" if kind == "prep" else f"확인 {ref}"
            first, *rest = txt.split("\n")
            extra = "".join(f"<br>{html.escape(r.strip())}" for r in rest if r.strip())
            lis.append(f'<li><a href="lessons/{l["id"]}.html#{nid}"><b>[{html.escape(badge)}]</b></a> '
                       f'{html.escape(first)}{extra}</li>')
        body.append(f'<section class="sec" id="{l["id"]}"><h2 class="sec-title">{label(l)} '
                    f'<a href="lessons/{l["id"]}.html">{html.escape(l["title"])}</a></h2><ul>'
                    + "".join(lis) + "</ul></section>")
    body.append("</main>\n</body>\n</html>\n")
    return head("강사 준비 목록 — " + COURSE, "") + "\n".join(body)


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
    groups = collect_notes(lessons)
    notes_total = sum(len(i) for _, i in groups)
    notes_path = ROOT / "instructor-notes.html"
    if notes_total:
        notes_path.write_text(build_notes(groups), encoding="utf-8", newline="\n")
    elif notes_path.exists():
        notes_path.unlink()
    (ROOT / "index.html").write_text(build_index(lessons, notes_total), encoding="utf-8", newline="\n")
    (ROOT / "print").mkdir(exist_ok=True)
    text, n = build_textbook(lessons)
    (ROOT / "print" / "textbook.html").write_text(text, encoding="utf-8", newline="\n")
    print(f"index.html 생성 — 교시 {len(lessons)}개 중 작성된 {n}개 링크")
    print(f"print/textbook.html 생성 — 교시 {n}개 포함")
    print("instructor-notes.html " + (f"생성 — 강사 표시 {notes_total}곳" if notes_total else "없음(강사 표시 0곳, 파일 지움)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
