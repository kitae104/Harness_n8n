# -*- coding: utf-8 -*-
"""신규과정 제안서 양식에 맞춘 제안서 PDF 만들기.

실행: python references/제안서_만들기.py
결과: references/제안서.html, references/제안서.pdf
그림: references/제안서_그림/ (화면 캡처), 나머지 그림(앱 화면·워크플로우·구성도)은 이 파일이 SVG로 그림
"""
import os
import subprocess
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_HTML = os.path.join(HERE, "제안서.html")
OUT_PDF = os.path.join(HERE, "제안서.pdf")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# ─────────────────────────────────────────────
# SVG 부품: n8n 노드
# ─────────────────────────────────────────────
KINDS = {
    "webhook": ("Webhook", "#ff6d5a"),
    "form": ("n8n Form Trigger", "#ff6d5a"),
    "set": ("Edit Fields", "#3b82f6"),
    "sheets": ("Google Sheets", "#0f9d58"),
    "gmail": ("Gmail", "#ea4335"),
    "cal": ("Google Calendar", "#4285f4"),
    "ai": ("Basic LLM Chain", "#7c3aed"),
    "model": ("Gemini Chat Model", "#7c3aed"),
    "if": ("If", "#f59e0b"),
    "tg": ("Telegram", "#229ed9"),
    "resp": ("Respond to Webhook", "#64748b"),
    "extract": ("Extract From File", "#0ea5e9"),
}


class Flow:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.nodes = {}
        self.parts = []
        self.edges = []

    def node(self, key, x, y, name, kind, w=112, h=44):
        self.nodes[key] = (x, y, w, h)
        t, c = KINDS[kind]
        if kind == "model":
            h = 28
            self.nodes[key] = (x, y, w, h)
            self.parts.append(
                f'<g transform="translate({x},{y})"><rect class="nd sub" width="{w}" height="{h}" rx="14"/>'
                f'<circle cx="14" cy="14" r="5" fill="{c}"/>'
                f'<text x="25" y="18" class="ns2">{escape(name)}</text></g>')
            return
        self.parts.append(
            f'<g transform="translate({x},{y})"><rect class="nd" width="{w}" height="{h}" rx="7"/>'
            f'<rect width="6" height="{h}" rx="3" fill="{c}"/>'
            f'<text x="13" y="19" class="nt">{escape(name)}</text>'
            f'<text x="13" y="34" class="ns">{t}</text></g>')

    def edge(self, a, b, label=None):
        ax, ay, aw, ah = self.nodes[a]
        bx, by, bw, bh = self.nodes[b]
        x1, y1 = ax + aw, ay + ah / 2
        x2, y2 = bx, by + bh / 2
        dx = max(18, (x2 - x1) / 2)
        self.edges.append(
            f'<path class="ln" d="M{x1},{y1} C{x1 + dx},{y1} {x2 - dx},{y2} {x2 - 3},{y2}" marker-end="url(#ar)"/>')
        if label:
            self.edges.append(f'<text x="{x1 + 6}" y="{(y1 + y2) / 2 + (-3 if y2 < y1 else 10)}" class="lb">{label}</text>')

    def sub(self, chain, model):
        ax, ay, aw, ah = self.nodes[chain]
        bx, by, bw, bh = self.nodes[model]
        cx = ax + aw / 2
        self.edges.append(f'<path class="ln dash" d="M{cx},{ay + ah} L{cx},{by}"/>')

    def text(self, x, y, s, cls="cap2"):
        self.parts.append(f'<text x="{x}" y="{y}" class="{cls}">{s}</text>')

    def raw(self, s):
        self.parts.append(s)

    def svg(self):
        return (f'<svg viewBox="0 0 {self.w} {self.h}" xmlns="http://www.w3.org/2000/svg" class="wf">'
                '<defs><marker id="ar" viewBox="0 0 8 8" refX="6" refY="4" markerWidth="7" markerHeight="7" orient="auto">'
                '<path d="M0,0 L8,4 L0,8 z" fill="#8a93a3"/></marker>'
                '<pattern id="dots" width="14" height="14" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#d5d9e0"/></pattern></defs>'
                f'<rect width="{self.w}" height="{self.h}" fill="#f7f8fa"/><rect width="{self.w}" height="{self.h}" fill="url(#dots)"/>'
                + "".join(self.edges) + "".join(self.parts) + "</svg>")


# ─────────────────────────────────────────────
# SVG 부품: 휴대폰 앱 화면
# ─────────────────────────────────────────────
PW, PH = 172, 336


class Phone:
    def __init__(self, x, y, title, sub=None, color="#1a73e8"):
        self.x, self.y = x, y
        self.cy = 76 if sub else 60
        self.p = [f'<rect x="0" y="0" width="{PW}" height="{PH}" rx="20" fill="#fff" stroke="#23262d" stroke-width="4"/>',
                  f'<path d="M4,20 a16,16 0 0 1 16,-16 h{PW - 40} a16,16 0 0 1 16,16 v{(66 if sub else 50) - 20} h-{PW - 8} z" fill="{color}"/>',
                  f'<text x="14" y="36" class="ph-t">{escape(title)}</text>']
        if sub:
            for i, line in enumerate(sub if isinstance(sub, list) else [sub]):
                self.p.append(f'<text x="14" y="{52 + i * 11}" class="ph-s">{escape(line)}</text>')

    def field(self, label, value, h=24, select=False, lines=None):
        y = self.cy
        self.p.append(f'<text x="14" y="{y + 8}" class="ph-l">{escape(label)}</text>')
        self.p.append(f'<rect x="12" y="{y + 12}" width="{PW - 24}" height="{h}" rx="5" fill="#f8fafc" stroke="#cbd5e1"/>')
        vals = lines or [value]
        for i, v in enumerate(vals):
            self.p.append(f'<text x="19" y="{y + 28 + i * 12}" class="ph-v">{escape(v)}</text>')
        if select:
            self.p.append(f'<path d="M{PW - 28},{y + 22} l5,5 l5,-5" fill="none" stroke="#64748b" stroke-width="1.5"/>')
        self.cy = y + 12 + h + 7

    def button(self, label, color="#1a73e8", outline=False, icon=None):
        y = self.cy + 2
        if outline:
            self.p.append(f'<rect x="12" y="{y}" width="{PW - 24}" height="28" rx="6" fill="#fff" stroke="{color}" stroke-width="1.5"/>')
            fill = color
        else:
            self.p.append(f'<rect x="12" y="{y}" width="{PW - 24}" height="28" rx="6" fill="{color}"/>')
            fill = "#fff"
        tx = PW / 2
        if icon == "mic":
            self.p.append(f'<g transform="translate({tx - 52},{y + 7})" fill="none" stroke="{fill}" stroke-width="1.6">'
                          '<rect x="3" y="0" width="6" height="10" rx="3" fill="' + fill + '"/><path d="M0,7 a6,6 0 0 0 12,0 M6,13 v2"/></g>')
            tx += 8
        self.p.append(f'<text x="{tx}" y="{y + 18}" text-anchor="middle" class="ph-b" fill="{fill}">{escape(label)}</text>')
        self.cy = y + 28 + 8

    def box(self, lines, fill="#ecfdf3", stroke="#86efac", title=None, big=None, tcolor="#15803d"):
        y = self.cy
        h = 10 + (14 if title else 0) + (26 if big else 0) + 13 * len(lines) + 4
        self.p.append(f'<rect x="12" y="{y}" width="{PW - 24}" height="{h}" rx="7" fill="{fill}" stroke="{stroke}"/>')
        cy = y + 16
        if title:
            self.p.append(f'<text x="{PW / 2 if big else 20}" y="{cy}" {"text-anchor=middle" if big else ""} class="ph-bt" fill="{tcolor}">{escape(title)}</text>')
            cy += 14
        if big:
            self.p.append(f'<text x="{PW / 2}" y="{cy + 12}" text-anchor="middle" class="ph-big" fill="{tcolor}">{escape(big)}</text>')
            cy += 26
        for ln in lines:
            anchor = f'x="{PW / 2}" text-anchor="middle"' if big else 'x="20"'
            self.p.append(f'<text {anchor} y="{cy}" class="ph-v">{escape(ln)}</text>')
            cy += 13
        self.cy = y + h + 8

    def table(self, rows):
        y = self.cy
        for i, (k, v) in enumerate(rows):
            yy = y + i * 22
            self.p.append(f'<rect x="12" y="{yy}" width="{PW - 24}" height="22" fill="{"#f1f5f9" if i % 2 == 0 else "#fff"}" stroke="#e2e8f0"/>')
            self.p.append(f'<text x="18" y="{yy + 15}" class="ph-l">{escape(k)}</text>')
            self.p.append(f'<text x="74" y="{yy + 15}" class="ph-v">{escape(v)}</text>')
        self.cy = y + len(rows) * 22 + 8

    def tabs(self, a, b, active=1):
        y = self.cy
        for i, t in enumerate([a, b]):
            x = 12 + i * (PW - 24) / 2
            on = i == active
            self.p.append(f'<rect x="{x}" y="{y}" width="{(PW - 24) / 2}" height="22" rx="4" fill="{"#1a73e8" if on else "#eef2f7"}"/>')
            self.p.append(f'<text x="{x + (PW - 24) / 4}" y="{y + 15}" text-anchor="middle" class="ph-l" fill="{"#fff" if on else "#475569"}">{escape(t)}</text>')
        self.cy = y + 30

    def note(self, s, color="#64748b"):
        self.p.append(f'<text x="{PW / 2}" y="{self.cy + 8}" text-anchor="middle" class="ph-s2" fill="{color}">{escape(s)}</text>')
        self.cy += 16

    def svg(self):
        return f'<g transform="translate({self.x},{self.y})">' + "".join(self.p) + "</g>"


def screens(phones, w, h, captions=(), arrows=()):
    body = "".join(p.svg() for p in phones)
    for (x, y) in arrows:
        body += f'<path d="M{x},{y} h16" stroke="#1a73e8" stroke-width="3" marker-end="url(#ar2)"/>'
    for (x, y, s) in captions:
        body += f'<text x="{x}" y="{y}" text-anchor="middle" class="cap2">{escape(s)}</text>'
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" class="scr">'
            '<defs><marker id="ar2" viewBox="0 0 8 8" refX="5" refY="4" markerWidth="5" markerHeight="5" orient="auto">'
            '<path d="M0,0 L8,4 L0,8 z" fill="#1a73e8"/></marker></defs>'
            f'<rect width="{w}" height="{h}" rx="8" fill="#f3f5f8"/>' + body + "</svg>")


# ─────────────────────────────────────────────
# 그림들
# ─────────────────────────────────────────────
def fig_legacy_flow():
    f = Flow(480, 300)
    f.node("form", 10, 128, "민원 입력 폼", "form", w=120)
    f.node("sheet", 190, 6, "시트에 기록", "sheets", w=120)
    f.node("mail", 190, 56, "접수 메일 보내기", "gmail", w=120)
    f.node("cal", 190, 106, "처리 마감 일정", "cal", w=120)
    f.node("ai", 190, 156, "AI 안내문 작성", "ai", w=120)
    f.node("gm", 190, 206, "Gemini Chat Model", "model", w=120)
    f.node("if", 190, 246, "생활인가?", "if", w=120)
    f.node("m1", 355, 206, "생활 담당자", "gmail", w=115)
    f.node("m2", 355, 256, "일반 담당자", "gmail", w=115)
    for k in ["sheet", "mail", "cal", "ai", "if"]:
        f.edge("form", k)
    f.sub("ai", "gm")
    f.edge("if", "m1", "true")
    f.edge("if", "m2", "false")
    f.text(10, 20, "기초과정 완성 워크플로우", "cap3")
    f.text(10, 36, "(1일차 8강)", "cap2")
    return f.svg()


def fig_minwon_flow():
    f = Flow(1000, 470)
    f.text(10, 22, "① 민원 접수 — 앱이 POST …/webhook/minwon 호출", "cap3")
    f.node("wh", 10, 128, "민원 받기", "webhook")
    f.node("set", 140, 128, "민원 정리", "set")
    f.node("today", 270, 128, "오늘 접수 조회", "sheets")
    f.node("no", 400, 128, "접수번호 만들기", "set")
    f.node("rec", 530, 128, "시트에 기록", "sheets")
    f.node("ai", 690, 8, "AI 안내문 작성", "ai", w=124)
    f.node("gm", 690, 62, "Gemini Chat Model", "model", w=124)
    f.node("if", 690, 112, "생활인가?", "if", w=124)
    f.node("cal", 690, 180, "처리 마감 일정", "cal", w=124)
    f.node("tg", 690, 240, "텔레그램 알림", "tg", w=124)
    f.node("resp", 860, 8, "앱에 답하기", "resp", w=130)
    f.node("m1", 860, 88, "담당자 메일", "gmail", w=130)
    f.node("m2", 860, 146, "일반 담당자 메일", "gmail", w=130)
    for a, b in [("wh", "set"), ("set", "today"), ("today", "no"), ("no", "rec")]:
        f.edge(a, b)
    for b in ["ai", "if", "cal", "tg"]:
        f.edge("rec", b)
    f.sub("ai", "gm")
    f.edge("ai", "resp")
    f.edge("if", "m1", "true")
    f.edge("if", "m2", "false")
    f.text(862, 68, "→ 앱 화면에 표시", "cap2")
    f.raw('<line x1="10" y1="305" x2="990" y2="305" stroke="#c7ccd4" stroke-dasharray="5 4"/>')
    f.text(10, 330, "② 처리 상태 조회 — 앱이 GET …/webhook/minwon-status?no=접수번호 호출", "cap3")
    f.node("st", 10, 375, "상태 조회", "webhook")
    f.node("find", 140, 375, "접수번호로 찾기", "sheets")
    f.node("ok", 270, 375, "찾았나?", "if")
    f.node("r1", 430, 342, "조회 결과 답하기", "resp", w=130)
    f.node("r2", 430, 408, "없음 답하기", "resp", w=130)
    f.edge("st", "find")
    f.edge("find", "ok")
    f.edge("ok", "r1", "true")
    f.edge("ok", "r2", "false")
    f.text(600, 368, "찾으면: 접수번호·처리상태·담당자·처리마감", "cap2")
    f.text(600, 386, "없으면: {찾음: false, 오류: \"접수번호를 찾을 수 없습니다\"}", "cap2")
    f.text(600, 414, "담당자 = 종류가 생활이면 정담당, 그 외 강처리", "cap2")
    f.text(600, 432, "처리마감 = 등록일 + 3일", "cap2")
    return f.svg()


def fig_field_flow():
    f = Flow(1000, 236)
    f.node("wh", 10, 96, "점검 받기", "webhook", w=100)
    f.node("set", 125, 96, "점검 정리", "set", w=100)
    f.node("today", 240, 96, "오늘 접수 조회", "sheets", w=104)
    f.node("no", 359, 96, "접수번호 만들기", "set", w=104)
    f.node("rec", 478, 96, "시트에 기록", "sheets", w=100)
    f.node("resp", 620, 10, "앱에 답하기", "resp", w=116)
    f.node("if", 620, 96, "보수필요인가?", "if", w=116)
    f.node("tg", 620, 182, "텔레그램 알림", "tg", w=116)
    f.node("ai", 772, 96, "AI 조치 요약", "ai", w=104)
    f.node("gm", 772, 152, "Gemini Chat Model", "model", w=110)
    f.node("mail", 900, 96, "팀장 메일", "gmail", w=92)
    for a, b in [("wh", "set"), ("set", "today"), ("today", "no"), ("no", "rec"), ("ai", "mail")]:
        f.edge(a, b)
    for b in ["resp", "if", "tg"]:
        f.edge("rec", b)
    f.edge("if", "ai", "true")
    f.sub("ai", "gm")
    f.text(10, 22, "현장점검 보고 — 앱이 POST …/webhook/field-check 호출", "cap3")
    f.text(742, 30, "접수번호·메시지 → 앱 화면", "cap2")
    f.text(742, 206, "텔레그램 부서방에 점검 알림", "cap2")
    return f.svg()


def fig_pdf_flow():
    f = Flow(700, 196)
    f.node("wh", 10, 76, "공문 받기", "webhook", w=110)
    f.node("ex", 150, 76, "글자 뽑기", "extract", w=118)
    f.node("ai", 300, 76, "AI 공문 요약", "ai", w=118)
    f.node("gm", 300, 132, "Gemini Chat Model", "model", w=118)
    f.node("resp", 470, 8, "앱에 답하기", "resp", w=120)
    f.node("mail", 470, 76, "요약 메일", "gmail", w=120)
    f.node("tg", 470, 144, "텔레그램 알림", "tg", w=120)
    f.edge("wh", "ex")
    f.edge("ex", "ai")
    f.sub("ai", "gm")
    for b in ["resp", "mail", "tg"]:
        f.edge("ai", b)
    f.text(10, 22, "PDF 공문 요약 — 파일(file)을 POST", "cap3")
    return f.svg()


def fig_minwon_screens():
    p1 = Phone(14, 14, "민원 접수", "아래 내용을 적고 접수하기를 누르세요.")
    p1.field("이름", "홍길동")
    p1.field("연락처", "010-1234-5678")
    p1.field("이메일", "minwon@example.com")
    p1.field("종류", "생활", select=True)
    p1.field("상세설명", "", h=34, lines=["보도블록이 깨져 있습니다."])
    p1.button("접수하기")

    p2 = Phone(222, 14, "접수 완료", "n8n이 보낸 답을 보여 줍니다", color="#0f9d58")
    p2.box(["접수되었습니다"], title="접수번호", big="2026-0922-001")
    p2.box(["홍길동 님, 생활 민원이", "정상적으로 접수되었습니다.", "담당자가 확인한 뒤", "처리 결과를 알려 드리겠습니다."],
           fill="#fffbeb", stroke="#fcd34d", title="AI 안내문 (Gemini)", tcolor="#b45309")
    p2.button("새 민원 접수", outline=True)

    p3 = Phone(430, 14, "처리 상태 조회", "접수번호로 진행 상황을 봅니다")
    p3.tabs("민원 접수", "처리 상태 조회")
    p3.field("접수번호", "2026-0922-001")
    p3.button("조회하기")
    p3.table([("접수번호", "2026-0922-001"), ("처리상태", "접수"), ("담당자", "정담당"), ("처리마감", "2026-09-25")])
    return screens([p1, p2, p3], 616, 372, arrows=[(191, 180), (399, 180)],
                   captions=[(100, 366, "① 입력 화면"), (308, 366, "② 접수 완료(n8n 회신)"), (516, 366, "③ 처리 상태 조회")])


def fig_field_screens():
    p1 = Phone(14, 14, "현장점검 보고", "시설과 점검 담당자용", color="#0e7490")
    p1.field("점검장소", "OO동 체육공원")
    p1.field("점검결과", "보수필요", select=True)
    p1.field("특이사항", "", h=34, lines=["벤치 1개 파손"])
    p1.field("점검자", "오점검")
    p1.button("보고하기", color="#0e7490")

    p2 = Phone(222, 14, "보고 완료", "n8n이 보낸 답을 보여 줍니다", color="#0f9d58")
    p2.box(["점검 보고가 접수되었습니다"], title="접수번호", big="2026-0922-003")
    p2.box(["보수필요 → Gemini가 조치 요약을", "써서 팀장에게 메일로 보냈고,", "부서 텔레그램에 알렸습니다."],
           fill="#f8fafc", stroke="#cbd5e1", title="뒤에서 n8n이 한 일", tcolor="#334155")
    p2.button("새로 입력", outline=True, color="#0e7490")
    return screens([p1, p2], 408, 372, arrows=[(191, 180)],
                   captions=[(100, 366, "① 현장에서 입력"), (308, 366, "② 접수번호 회신")])


def fig_option_screens():
    p1 = Phone(14, 14, "공문 요약", ["PDF 공문을 올리면 핵심을", "5줄로 요약해 드립니다."], color="#7c3aed")
    p1.field("PDF 파일", "gongmun-sample.pdf")
    p1.button("요약하기", color="#7c3aed")
    p1.box(["· 주민 디지털 역량 교육 협조", "· 동별 4회(회당 2시간) 운영", "· 강사·교재는 구청이 지원",
            "· 동별 15명 내외 모집", "· 10.10.까지 참여 인원 회신"],
           fill="#f5f3ff", stroke="#c4b5fd", title="요약", tcolor="#6d28d9")
    p1.note("같은 요약이 메일·텔레그램으로도 갑니다")

    p2 = Phone(222, 14, "민원 접수", "음성 입력 버튼을 더한 화면")
    p2.field("이름", "홍길동")
    p2.field("종류", "생활", select=True)
    p2.field("상세설명", "", h=34, lines=["공원 가로등이 꺼져 있어요"])
    p2.button("음성으로 입력", outline=True, icon="mic")
    p2.note("듣는 중… (크롬·엣지, 한국어)", color="#dc2626")
    p2.button("접수하기")
    return screens([p1, p2], 408, 372,
                   captions=[(100, 366, "선택 ① PDF 공문 요약 앱"), (308, 366, "선택 ② 음성 입력 민원 접수")])


def fig_architecture():
    s = ['<svg viewBox="0 0 1000 330" xmlns="http://www.w3.org/2000/svg" class="wf">',
         '<defs><marker id="ar3" viewBox="0 0 8 8" refX="6" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#475569"/></marker></defs>',
         '<rect width="1000" height="330" fill="#fff"/>',
         '<text x="500" y="24" text-anchor="middle" class="h3s">"화면은 AI가, 일은 n8n이" — 앱 + 자동화 연동 서비스 구성</text>']
    # 사람
    s.append('<circle cx="60" cy="140" r="16" fill="#334155"/><path d="M30,190 a30,26 0 0 1 60,0 z" fill="#334155"/>')
    s.append('<text x="60" y="212" text-anchor="middle" class="nt">공무원·민원인</text><text x="60" y="227" text-anchor="middle" class="ns">브라우저·휴대폰</text>')
    s.append('<path d="M100,160 H150" stroke="#475569" stroke-width="2" marker-end="url(#ar3)"/>')
    # 앱
    s.append('<rect x="155" y="50" width="220" height="250" rx="12" fill="#eef4ff" stroke="#1a73e8" stroke-width="2"/>')
    s.append('<text x="265" y="76" text-anchor="middle" class="h3s" fill="#1a73e8">① 앱 (Google AI Studio Build)</text>')
    s.append('<text x="265" y="96" text-anchor="middle" class="ns">한국어 문장(프롬프트)으로 생성 · 코드 작성 없음</text>')
    for i, t in enumerate(["민원 접수 화면", "접수번호·AI 안내문 표시", "처리 상태 조회 화면", "(선택) 공문 PDF 올리기", "(선택) 음성으로 입력"]):
        s.append(f'<rect x="175" y="{110 + i * 32}" width="180" height="26" rx="6" fill="#fff" stroke="#bfd4fb"/>'
                 f'<text x="187" y="{127 + i * 32}" class="nt2">{t}</text>')
    s.append('<text x="265" y="290" text-anchor="middle" class="ns">공유 링크(Share)로 동료에게 배포</text>')
    # 화살표
    s.append('<path d="M380,140 H470" stroke="#1a73e8" stroke-width="2.5" marker-end="url(#ar3)"/>')
    s.append('<text x="425" y="130" text-anchor="middle" class="ns">Webhook</text><text x="425" y="118" text-anchor="middle" class="ns">POST·GET</text>')
    s.append('<path d="M470,200 H380" stroke="#ff6d5a" stroke-width="2.5" marker-end="url(#ar3)"/>')
    s.append('<text x="425" y="220" text-anchor="middle" class="ns">접수번호·안내문</text><text x="425" y="233" text-anchor="middle" class="ns">조회 결과 회신</text>')
    # n8n
    s.append('<rect x="475" y="50" width="270" height="250" rx="12" fill="#fff4f1" stroke="#ff6d5a" stroke-width="2"/>')
    s.append('<text x="610" y="76" text-anchor="middle" class="h3s" fill="#e0492f">② n8n 워크플로우 (뒷단 처리)</text>')
    s.append('<text x="610" y="96" text-anchor="middle" class="ns">기초과정에서 배운 노드를 그대로 재사용</text>')
    boxes = [("Webhook", "앱 요청 받기"), ("Edit Fields", "값 정리·접수번호"), ("If", "종류별 담당자"),
             ("Basic LLM Chain", "Gemini 안내문·요약"), ("Respond to Webhook", "앱에 답하기"), ("Google Sheets", "기록·조회")]
    for i, (a, b) in enumerate(boxes):
        x = 490 + (i % 2) * 128
        y = 110 + (i // 2) * 58
        s.append(f'<rect x="{x}" y="{y}" width="118" height="46" rx="7" fill="#fff" stroke="#f6b3a6"/>'
                 f'<text x="{x + 59}" y="{y + 20}" text-anchor="middle" class="nt2">{a}</text>'
                 f'<text x="{x + 59}" y="{y + 36}" text-anchor="middle" class="ns">{b}</text>')
    s.append('<text x="610" y="290" text-anchor="middle" class="ns">Test URL로 시험 → Publish → Production URL</text>')
    # 외부 서비스
    svc = [("Google Sheets", "민원대장 기록", "#0f9d58"), ("Gmail", "담당자 메일", "#ea4335"),
           ("Google Calendar", "처리 마감 등록", "#4285f4"), ("Gemini API", "안내문·요약 작성", "#7c3aed"),
           ("Telegram", "부서 알림", "#229ed9")]
    for i, (a, b, c) in enumerate(svc):
        y = 52 + i * 50
        s.append(f'<path d="M745,175 C780,175 780,{y + 20} 810,{y + 20}" fill="none" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar3)"/>')
        s.append(f'<rect x="815" y="{y}" width="170" height="40" rx="7" fill="#fff" stroke="{c}" stroke-width="1.5"/>'
                 f'<rect x="815" y="{y}" width="6" height="40" rx="3" fill="{c}"/>'
                 f'<text x="830" y="{y + 17}" class="nt2">{a}</text><text x="830" y="{y + 32}" class="ns">{b}</text>')
    s.append('<text x="900" y="316" text-anchor="middle" class="ns">③ 외부 서비스(무료 사용 범위)</text>')
    s.append('</svg>')
    return "".join(s)


def fig_design_sheet():
    rows = [("서비스 이름", "현장점검 보고 앱"), ("누가 쓰나", "시설과 점검 담당자 6명"),
            ("입력(앱 화면)", "점검장소, 점검결과(양호/보수필요), 특이사항, 점검자"),
            ("처리(n8n)", "시트 기록 → \"보수필요\"면 Gemini가 조치 요약 작성 → 팀장 메일"),
            ("출력(알림·회신)", "텔레그램 부서방 알림, 앱에 접수번호 표시"),
            ("자동화 전 → 후", "수기 보고서 작성 30분 → 현장에서 2분 입력")]
    tr = "".join(f"<tr><th>{escape(a)}</th><td>{escape(b)}</td></tr>" for a, b in rows)
    return ('<div class="sheet"><div class="sheet-h">나만의 업무 서비스 설계서 <span>(2일차 4교시, 작성 예)</span></div>'
            f'<table class="ds">{tr}</table>'
            '<div class="sheet-f">스스로 점검: 입력 칸 5개 이하 · 배운 노드로 가능 · 가상 데이터만 · 전후 효과 한 문장</div></div>')


# ─────────────────────────────────────────────
# 본문
# ─────────────────────────────────────────────
TITLE = "AI 앱과 n8n으로 만드는 나만의 업무 자동화 서비스"

TIMETABLE = [
    ("1교시", "09:00~09:50",
     ("입과 안내 및 과정 소개", ["완성 서비스 시연(앱 접수 → 시트·메일·캘린더·AI 안내문·텔레그램 → 접수번호 회신)",
                         "\"화면은 AI가, 일은 n8n이\" 역할 분담, 가상 데이터 원칙", "준비물 점검, 사전조사한 \"자동화 희망 업무\" 공유"]),
     ("앱 ↔ n8n 연동 ②", ["담당자 메일(Gmail) 발송", "구글 캘린더에 처리 마감 등록", "Gemini 민원인 안내문 생성 → 앱 화면에 표시"])),
    ("2교시", "10:00~10:50",
     ("n8n 핵심 복습 실습", ["트리거–처리–결과 구조, 표현식 {{ }}", "구글 시트 기록, Gmail 발송, Gemini 안내문",
                        "완성본 가져오기(Import)·자격 증명 연결로 수준 맞추기"]),
     ("연동 ② 완성", ["If 조건 분기(민원 종류별 담당자 배정)", "처리 상태 조회: 조회용 Webhook + 앱 조회 화면", "텔레그램 접수 알림"])),
    ("3교시", "11:00~11:50",
     ("Webhook 이해와 실습", ["앱과 자동화가 대화하는 방법(외부 앱이 n8n을 부르는 주소)", "Test URL → Publish → Production URL 순서",
                          "Respond to Webhook으로 답 돌려주기, 브라우저 호출 테스트", "Allowed Origins(CORS) 설정"]),
     ("앱 배포·공유·보안", ["AI Studio 공유 링크 만들고 옆 사람과 서로 접수 시험", "비밀값(API 키) 관리, 앱 코드 점검",
                       "실행 기록에 남는 개인정보 확인, 개인정보·보안 점검표", "기관 설치형 n8n 전환 안내"])),
    ("4교시", "13:00~13:50",
     ("AI 앱 빌더 첫 체험", ["Google AI Studio Build 화면 구성", "문장(프롬프트)으로 앱 만드는 원리", "프롬프트 템플릿으로 민원 접수 화면 생성"]),
     ("프로젝트 기획", ["부서별 시나리오 확정(개인 또는 2~3인 팀)", "입력–처리–출력 설계서 작성, 강사 검토", "설계서를 AI Studio 프롬프트로 옮기기"])),
    ("5교시", "14:00~14:50",
     ("첫 앱 다듬기", ["화면 수정 요청하기(구체적인 문장으로)", "오류 대처 루틴(오류 문구 복사 → AI에 붙여 넣고 수정 요청) 반복 연습"]),
     ("프로젝트 제작 ①", ["프롬프트 템플릿을 고쳐 내 앱 화면 생성", "완성 워크플로우 파일을 변형해 내 워크플로우 구성"])),
    ("6교시", "15:00~15:50",
     ("앱 ↔ n8n 연동 ①", ["앱에 Webhook 주소 넣기", "접수 데이터 전송 → 구글 시트 기록 확인", "연결 점검표로 주소·CORS 문제 해결"]),
     ("프로젝트 제작 ②", ["앱–n8n 연동, 처음부터 끝까지 테스트", "점검 순서표로 오류 원인 좁히기", "(선택 실습) PDF 공문 요약·음성 입력 기능"])),
    ("7교시", "16:00~16:50",
     ("연동 ① 완성", ["접수번호 생성·시트 기록", "접수번호 회신(Respond to Webhook) → 앱 화면에 표시", "1일차 정리"]),
     ("발표·피드백 및 적용 로드맵", ["내 서비스 뽐내기(팀별 5분)", "부서 적용 로드맵(점검 → 협의 → 시범 → 보완 → 운영)", "수료 설문"])),
]


def cell(item):
    t, subs = item
    return f'<div class="tt-t">◦{escape(t)}</div>' + "".join(f'<div class="tt-s">- {escape(s)}</div>' for s in subs)


def timetable():
    rows = []
    for i, (p, tm, d1, d2) in enumerate(TIMETABLE):
        rows.append(f'<tr><th class="tt-p">{p}<br><span>({tm})</span></th><td>{cell(d1)}</td><td>{cell(d2)}</td></tr>')
        if i == 2:
            rows.append('<tr class="lunch"><th>점심</th><td colspan="2">12:00~13:00</td></tr>')
    return ('<table class="f tt"><colgroup><col style="width:15%"><col style="width:42.5%"><col style="width:42.5%"></colgroup>'
            '<tr class="tt-h"><th>구 분</th><th>1일차<div class="tt-d">n8n 다지기 + 첫 앱 + 연결</div></th>'
            '<th>2일차<div class="tt-d">자동화 확장 + 내 업무 서비스</div><div class="red">(유료계정 불필요 — 모두 무료 사용 범위)</div></th></tr>'
            + "".join(rows) + "</table>")


def img(name, cls="shot"):
    return f'<img class="{cls}" src="제안서_그림/{name}">'


CSS = r"""
@page { size: A4; margin: 15mm 15mm 14mm 15mm; }
* { box-sizing: border-box; }
body { font-family: 'Malgun Gothic', 'Noto Sans KR', sans-serif; font-size: 9.6pt; color: #111; line-height: 1.5; margin: 0; }
.bar { display: flex; height: 5px; margin: 4px 0 0 0; }
.bar i { display: block; height: 5px; } .bar i:nth-child(1){width:34px;background:#1e88e5} .bar i:nth-child(2){width:72px;background:#1a3a8a} .bar i:nth-child(3){width:78px;background:#7cb342}
.titlebox { border: 1.3px solid #222; padding: 9px 10px; text-align: center; font-size: 16.5pt; line-height: 1.4; font-weight: 800; letter-spacing: -0.3px; }
.titlebox .q { font-weight: 700; }
.subt { text-align: center; font-size: 9.5pt; color: #333; margin-top: 5px; }
h2 { color: #1f2a6b; font-size: 13.5pt; margin: 17px 0 7px; font-weight: 800; letter-spacing: -0.2px; }
h3 { font-size: 10.5pt; margin: 12px 0 5px; }
table.f { width: 100%; border-collapse: collapse; border-top: 2px solid #222; border-bottom: 1.5px solid #222; }
table.f th, table.f td { border: 1px dotted #8c96a3; padding: 5px 8px; vertical-align: middle; }
table.f tr > :first-child { border-left: none; } table.f tr > :last-child { border-right: none; }
table.f th { background: #e8eef7; font-weight: 700; text-align: center; white-space: nowrap; }
td.c { text-align: center; }
.red { color: #d32f2f; font-weight: 700; font-size: 8.8pt; }
.small { font-size: 8.6pt; color: #333; }
ul.dot { margin: 0; padding-left: 0; list-style: none; } ul.dot li::before { content: "◦ "; }
table.edu { width: 100%; border-collapse: collapse; break-inside: avoid; page-break-inside: avoid; }
tr.edu-row { break-inside: avoid; page-break-inside: avoid; }
table.edu th, table.edu td { border: 1px dotted #8c96a3; padding: 5px 7px; }
table.edu tr > :first-child { border-left: none; } table.edu tr > :last-child { border-right: none; }
table.edu tr:first-child > * { border-top: none; } table.edu tr:last-child > * { border-bottom: none; }
table.edu th { background: #f2f4f7; }
table.edu td.n { text-align: center; width: 7.5%; }
table.edu .it { padding-left: 1em; text-indent: -0.7em; }
td.edu-wrap { padding: 0 !important; }
table.tt { font-size: 9pt; }
table.tt tr.tt-h th { background: #d9d9d9; font-size: 11pt; padding: 7px; }
.tt-d { font-size: 8.8pt; font-weight: 600; color: #333; }
th.tt-p { background: #f2f2f2 !important; font-weight: 500 !important; }
th.tt-p span { font-size: 8.3pt; }
table.tt td { vertical-align: top; padding: 7px 9px; }
.tt-t { font-weight: 800; color: #0d2a8a; }
.tt-s { padding-left: 0.9em; text-indent: -0.6em; color: #1a2b5f; }
tr.lunch th, tr.lunch td { background: #fafafa; font-size: 8.3pt; color: #666; padding: 2px 8px; text-align: center; }
.pb { page-break-before: always; }
.avoid { page-break-inside: avoid; }
.outbox { border: 1.5px dotted #555; padding: 12px 14px 6px; }
.out h3 { margin: 4px 0 4px; font-size: 10.5pt; }
.out p.desc { margin: 0 0 6px; font-size: 9pt; }
table.ba { width: 100%; border-collapse: collapse; margin-bottom: 14px; }
table.ba > tbody > tr > th { font-size: 11pt; font-weight: 600; text-decoration: underline; text-underline-offset: 3px; padding: 4px; border: 1px solid #333; background: #fff; }
table.ba > tbody > tr > td { border: 1px solid #333; padding: 6px; vertical-align: middle; text-align: center; }
.cap { font-size: 8.4pt; color: #333; text-align: center; margin-top: 3px; }
svg.wf, svg.scr { width: 100%; height: auto; display: block; }
img.shot { width: 100%; display: block; border: 1px solid #cfd5dd; }
.row3 { display: flex; gap: 8px; } .row3 > div { flex: 1; }
.row2 { display: flex; gap: 10px; align-items: flex-start; } .row2 > div { flex: 1; }
.nd { fill: #fff; stroke: #b8bfca; stroke-width: 1.2; } .nd.sub { stroke-dasharray: 3 2; }
.nt { font-size: 11.5px; font-weight: 700; fill: #1f2937; } .nt2 { font-size: 11.5px; font-weight: 700; fill: #1f2937; }
.ns { font-size: 9.5px; fill: #6b7280; } .ns2 { font-size: 9.5px; fill: #5b21b6; }
.ln { fill: none; stroke: #8a93a3; stroke-width: 1.5; } .ln.dash { stroke-dasharray: 4 3; }
.lb { font-size: 9px; fill: #64748b; } .cap2 { font-size: 10px; fill: #475569; } .cap3 { font-size: 11.5px; font-weight: 800; fill: #1f2a6b; }
.h3s { font-size: 14px; font-weight: 800; fill: #1f2937; }
.ph-t { font-size: 14px; font-weight: 800; fill: #fff; } .ph-s { font-size: 8.4px; fill: #e8f0fe; }
.ph-l { font-size: 9px; font-weight: 700; fill: #334155; } .ph-v { font-size: 9.3px; fill: #111827; }
.ph-b { font-size: 11px; font-weight: 800; } .ph-bt { font-size: 9.5px; font-weight: 800; } .ph-big { font-size: 17px; font-weight: 800; }
.ph-s2 { font-size: 8.4px; }
.sheet { border: 1px solid #b9c2cf; background: #fff; text-align: left; font-size: 8.6pt; }
.sheet-h { background: #1f2a6b; color: #fff; font-weight: 800; padding: 6px 9px; font-size: 9.5pt; } .sheet-h span { font-weight: 400; font-size: 8.3pt; }
table.ds { width: 100%; border-collapse: collapse; }
table.ds th, table.ds td { border-bottom: 1px solid #dde3ea; padding: 5px 7px; vertical-align: top; }
table.ds th { background: #f1f5f9; width: 30%; text-align: left; white-space: nowrap; }
.sheet-f { font-size: 7.8pt; color: #475569; padding: 5px 8px; background: #f8fafc; }
table.plan th { width: 22%; } table.plan td { font-size: 9pt; }
.note { font-size: 8.4pt; color: #444; margin-top: 4px; }
p.lead { margin: 3px 0; }
ul.b { margin: 3px 0 6px; padding-left: 1.2em; } ul.b li { margin: 2px 0; }
"""


def build():
    edu_rows = [
        ("1일차", ["입과 안내·완성 서비스 시연, 자동화 희망 업무 공유 (1)",
                 "n8n 핵심 복습: 트리거–처리–결과, 표현식, 구글 시트·Gmail·Gemini (1)",
                 "Webhook 이해와 실습: Test/Production URL, Publish, Respond to Webhook, CORS (1)",
                 "AI 앱 빌더 첫 체험: Google AI Studio Build로 민원 접수 화면 만들기, 화면 수정 요청·오류 대처 루틴 (2)",
                 "앱 ↔ n8n 연동 ①: 접수 → 시트 기록 → 접수번호 회신·앱 화면 표시 (2)"], "7", "2", "5", "-"),
        ("2일차", ["앱 ↔ n8n 연동 ②: 담당자 메일·캘린더 처리 마감·Gemini 안내문, 민원 종류별 담당자 분기, 처리 상태 조회 화면, 텔레그램 알림 (2)",
                 "앱 배포·공유·보안: 공유 링크, 비밀값(API 키) 관리, 개인정보·보안 점검표, 기관 설치형 n8n 안내 (1)",
                 "나만의 업무 서비스 프로젝트: 설계서 작성 → 앱·워크플로우 제작(완성 파일 변형) → 연동·테스트 (3)",
                 "발표·피드백 및 부서 적용 로드맵 (1)"], "7", "1", "5", "1"),
        ("선택", ["파일·음성 다루기(선택 실습): PDF 공문 업로드 요약 앱, 음성 입력 민원 접수 — 2일차 6교시 중 희망자 진행, 웹 교안·완성 파일로 수료 후 자율학습"],
         "-", "", "○", ""),
    ]
    edu = ('<table class="edu"><colgroup><col style="width:10%"><col><col style="width:7.5%"><col style="width:7.5%"><col style="width:7.5%"><col style="width:7.5%"></colgroup>'
           '<tr><th rowspan="2">구분</th><th rowspan="2">주요교육내용</th><th colspan="4">교육시간 및 방법</th></tr>'
           '<tr><th>계</th><th>강의</th><th>참여</th><th>기타</th></tr>'
           '<tr><td></td><td class="small" style="text-align:right">합계</td><td class="n"><b>14</b></td><td class="n"><b>3</b></td><td class="n"><b>10</b></td><td class="n"><b>1</b></td></tr>')
    for g, items, a, b, c, d in edu_rows:
        lis = "".join(f'<div class="it">- {escape(x)}</div>' for x in items)
        edu += f'<tr><td class="n" style="width:10%">{g}</td><td>{lis}</td><td class="n">{a}</td><td class="n">{b}</td><td class="n">{c}</td><td class="n">{d}</td></tr>'
    edu += '</table>'

    html = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{TITLE} 과정 세부계획(안)</title><style>{CSS}</style></head><body>

<div class="bar"><i></i><i></i><i></i></div>
<div class="titlebox"><span class="q">「</span>{TITLE}<span class="q">」</span><br>과정 세부계획(안)</div>
<div class="subt">코딩 없이 앱 화면을 만들고 n8n 자동화에 연결하기 — 「AI를 활용한 나만의 비서 만들기(n8n)」 심화(중급) 과정</div>

<h2>□ 과정개요</h2>
<table class="f">
<colgroup><col style="width:13%"><col style="width:52%"><col style="width:13%"><col style="width:22%"></colgroup>
<tr><th>교육목표</th><td colspan="3">Google AI Studio(무료 AI 앱 빌더)로 업무용 앱 화면을 만들고 n8n 자동화와 Webhook으로 연동하여, 접수→기록→알림→회신·조회로 이어지는 <b>나만의 업무 자동화 서비스를 직접 구축·공유하는 능력 향상</b></td></tr>
<tr><th>교육대상</th><td>「AI를 활용한 나만의 비서 만들기(n8n)」 수료자 또는 n8n 워크플로우(트리거–처리–결과)를 만들어 본 국가직·지방직 공무원(민원 접수·신청 접수·현장 보고 등 반복 행정업무 담당자)<br><span class="small">※ 프로그래밍 경험 불필요</span></td>
<th>교육기간</th><td class="c">2일(14시간)<br>중급</td></tr>
</table>

<h2>□ 강사정보</h2>
<table class="f">
<colgroup><col style="width:13%"><col style="width:18%"><col></colgroup>
<tr><th>성명</th><th>소속(직위)</th><th>주요 경력</th></tr>
<tr><td class="c">김기태</td><td class="c">인하공업전문대학<br>(조교수)</td><td><ul class="dot">
<li>「AI를 활용한 나만의 비서 만들기(n8n)」 1·2기 강의(2025~2026)</li>
<li>중앙공무원 정보화 교육, 중등교사 AI 연수 교육</li>
<li>한국인공지능교육학회 이사</li></ul></td></tr>
<tr><td class="c">(성명)</td><td class="c">(소속)<br>(보조강사)</td><td><ul class="dot">
<li>n8n·Google AI Studio 실습 지도</li>
<li>수강생 계정·권한 문제(구글 로그인, Gemini API 키) 및 오류 해결 전담</li>
<li>교시별 완성 파일 가져오기 지원 등 진도 보조</li></ul></td></tr>
</table>

<h2>□ 과정운영개요</h2>
<table class="f">
<colgroup><col style="width:13%"><col style="width:52%"><col style="width:13%"><col style="width:22%"></colgroup>
<tr><th>과정개요</th><td colspan="3">AI 앱 화면(Google AI Studio)과 n8n 자동화를 Webhook으로 연결하는 업무 서비스 구축 프로세스를 이해하고, 민원 접수·처리 상태 조회·현장점검 보고 등 반복 행정업무를 앱과 자동화로 바꾸는 방법 및 부서 업무 적용사례 습득</td></tr>
<tr><th>과정분류</th><td>업무자동화</td><th>난이도</th><td class="c">중</td></tr>
<tr><th>기초지식</th><td colspan="3">선수과목 「AI를 활용한 나만의 비서 만들기(n8n)」 수료 또는 동등 수준(트리거–처리–결과 워크플로우 구성, 구글 시트·Gmail 노드와 표현식 {{{{ }}}} 사용 경험) ※ 프로그래밍 경험 불필요</td></tr>
<tr><th>교재/사용SW</th><td colspan="3">「AI 앱과 n8n으로 만드는 나만의 업무 자동화 서비스」(자체파일: 웹 교안 + 인쇄 교재, 교시별 완성 워크플로우 JSON 9종, AI Studio 프롬프트 템플릿 11종, 설계서·점검표·로드맵 양식 3종) / Google AI Studio(Build), n8n Cloud, Gemini API, Google Sheets·Gmail·Google Calendar, Telegram(모두 무료 사용 범위)
<div class="red" style="margin-top:4px">※ 교육망 예외처리 요청: aistudio.google.com, ai.studio, *.usercontent.goog(AI Studio 앱 미리보기), accounts.google.com, docs·mail·calendar.google.com, generativelanguage.googleapis.com, *.n8n.cloud, esm.sh·cdn.jsdelivr.net, web.telegram.org·api.telegram.org, harness-n8n.vercel.app(웹 교안) — 교육 1주 전 교육장 PC 접속 사전 점검</div>
<div class="small" style="margin-top:3px">※ 수강생 사전 준비: 만 18세 이상 나이 확인된 개인 구글 계정(기관 계정은 AI Studio 사용이 막힐 수 있음), n8n Cloud 무료 체험 계정(교육 중 만료되지 않도록 개설 시점 안내), Gemini API 키, 텔레그램 계정</div></td></tr>
<tr class="edu-row"><th>교육내용</th><td colspan="3" class="edu-wrap">{edu}</td></tr>
</table>

<h2 class="pb">□ 시간표</h2>
{timetable()}
<div class="note">※ 각 교시는 50분 수업 + 10분 휴식. 교시마다 앞 10분은 개념 설명(왜 이 단계가 필요한가), 나머지는 실습이며, 교시 끝 "완성본 가져오기"로 뒤처진 수강생도 다음 교시를 함께 시작합니다.</div>

<h2 class="pb">□ 과정완료 후 산출물</h2>
<div class="outbox out">

<div class="avoid">
<h3>1. 민원 접수 서비스(AI 앱 + n8n) 실습 결과물</h3>
<p class="desc">앱에서 민원을 접수하면 구글 시트에 접수번호와 함께 기록되고, 민원 종류별 담당자 메일·구글 캘린더 처리 마감·텔레그램 알림이 이어지며, Gemini가 쓴 안내문과 접수번호가 앱 화면에 표시됩니다. 접수번호로 처리 상태를 조회하는 화면까지 만듭니다.</p>
<table class="ba"><colgroup><col style="width:42%"><col></colgroup>
<tr><th>실습 전</th><th>실습 후</th></tr>
<tr><td>{fig_legacy_flow()}<div class="cap">기초과정 결과: n8n 기본 폼으로 접수<br>(전용 앱 화면·접수번호·상태 조회 없음)</div></td>
<td>{fig_minwon_screens()}<div class="cap">AI Studio로 만든 민원 접수 앱(화면 예시 — 생성할 때마다 색·배치는 조금씩 다름)</div></td></tr>
<tr><td colspan="2">{fig_minwon_flow()}<div class="cap">앱 뒤에서 일하는 n8n 워크플로우(과정 최종 완성본, 노드 18개) — 접수와 상태 조회 두 입구</div></td></tr>
</table>
</div>

<div class="avoid">
<h3>2. 나만의 업무 자동화 서비스 프로젝트 결과물 — 예: 현장점검 보고 앱</h3>
<p class="desc">수강생(팀)이 자기 업무로 입력–처리–출력 설계서를 쓰고, 민원 접수 완성 파일을 고쳐 서비스를 완성해 발표합니다. 다른 주제 예: 교육·행사 신청 접수, 회의록 정리, 부서 지침 Q&amp;A.</p>
<table class="ba"><colgroup><col style="width:42%"><col></colgroup>
<tr><th>실습 전</th><th>실습 후</th></tr>
<tr><td>{fig_design_sheet()}<div class="cap">2일차 4교시에 쓴 한 장 설계서</div></td>
<td>{fig_field_screens()}<div class="cap">설계서대로 만든 현장점검 보고 앱</div></td></tr>
<tr><td colspan="2">{fig_field_flow()}<div class="cap">현장점검 보고 워크플로우 — 민원 접수 완성본의 앞부분을 그대로 고쳐 쓰고, "보수필요"일 때만 AI 요약·팀장 메일을 더함</div></td></tr>
</table>
</div>

<div class="avoid">
<h3>3. (선택 실습) 공문 요약·음성 접수 앱 결과물</h3>
<p class="desc">PDF 공문을 앱에 올리면 n8n이 글자를 뽑아 Gemini로 요약하고 앱 화면·메일·텔레그램으로 전달합니다. 민원 접수 앱에 "음성으로 입력" 버튼을 더하면 말한 내용이 글자로 바뀌어 같은 워크플로우로 접수됩니다.</p>
<table class="ba"><colgroup><col style="width:34%"><col></colgroup>
<tr><th>실습 전</th><th>실습 후</th></tr>
<tr><td>{img("gongmun.png")}<div class="cap">실습용 가상 공문(PDF로 저장해 사용)</div></td>
<td>{fig_option_screens()}<div class="cap">공문 요약 앱과 음성 입력 버튼을 더한 민원 접수 앱</div>
<div style="margin-top:6px">{fig_pdf_flow()}</div><div class="cap">공문 요약 워크플로우</div></td></tr>
</table>
</div>

<div class="avoid">
<h3>4. 서비스 설계·적용 문서</h3>
<p class="desc">교육 뒤 부서에서 실제 적용을 준비할 때 그대로 쓰는 양식 세 가지를 작성해 가져갑니다.</p>
<div class="row3" style="margin-bottom:10px">
<div>{img("form-design.png")}<div class="cap">입력–처리–출력 설계서</div></div>
<div>{img("form-security.png")}<div class="cap">실제 적용 전 개인정보·보안 점검표</div></div>
<div>{img("form-roadmap.png")}<div class="cap">부서 적용 로드맵(점검→협의→시범→보완→운영)</div></div>
</div>
</div>
</div>

<h2 class="pb">□ 과정운영계획</h2>
<h3>1. 개요</h3>
<ul class="b">
<li>선행 과정(「AI를 활용한 나만의 비서 만들기(n8n)」 1·2기)에서 공무원들이 n8n으로 민원 접수·기록·알림 자동화를 경험하였으나, 수료 설문에서 <b>현업도움 문항이 가장 낮았고(2.04)</b>, 수준별(초급→중급) 과정, 교육시간 확대, 실무 적용 사례, 앱 제작까지 이어지는 과정을 요청함</li>
<li>자동화 워크플로우만으로는 동료·민원인이 직접 쓸 수 있는 "입구(화면)"가 없어 부서 단위 확산이 어려움. 무료 AI 앱 빌더(Google AI Studio)는 프로그래밍 없이 문장만으로 앱 화면을 만들 수 있어, 비개발자도 "앱 + 자동화" 형태의 완성된 서비스를 구축할 수 있음</li>
<li>본 과정은 AI 앱 빌더로 업무용 화면을 만들고 n8n 자동화와 연동하여, 접수부터 기록·알림·회신·조회까지 이어지는 서비스를 수강생이 직접 완성하는 실습 중심 심화 과정임</li>
<li>입과 전 사전조사로 모은 수강생의 실제 업무를 프로젝트 주제로 삼아, 교육 종료 시 설계서·서비스·적용 로드맵을 가지고 돌아가는 것을 목표로 함</li>
</ul>
<div class="avoid" style="margin:8px 0 4px">{fig_architecture()}<div class="cap">그림. 전체 서비스 구성 — 수강생은 ①을 문장으로 만들고, ②는 이미 배운 워크플로우에 Webhook만 더해 연결</div></div>

<h3>2. 특징</h3>
<ul class="b">
<li><b>"화면은 AI가, 일은 n8n이"</b>: 수강생은 코드를 쓰지 않고 한국어 문장으로 앱 화면을 만들며, 기록·발송·AI 생성은 선행 과정에서 배운 n8n 노드로 처리</li>
<li><b>교시별 웹 교안 16개와 인쇄 교재</b>: 교시마다 학습목표 → 개념 설명(10분) → 따라하기 → 확인 문제 → 정리 순서이며, 단계마다 성공 조건·자주 하는 실수·막혔을 때 대처를 안내</li>
<li><b>누적형 완성 파일</b>: 교시 끝 상태의 워크플로우 JSON을 제공하여 진도가 밀린 수강생도 가져오기(Import)로 즉시 따라잡음(1일차 6교시 → 7교시 → 2일차 1교시 → 2교시로 이어지는 하나의 서비스)</li>
<li><b>검증된 프롬프트 템플릿 11종</b>과 "오류 문구 복사 → AI에 수정 요청" 루틴으로 결과 편차를 줄임</li>
<li><b>2일차 오후 4시간 프로젝트</b>(기획 1 + 제작 2 + 발표 1): 예시 완성본(현장점검 보고 앱)을 고쳐 쓰는 방식으로 현업 적용성 강화</li>
<li><b>안전한 적용 준비</b>: 실습은 가상 데이터만 사용하고, 공유·비밀값·개인정보 점검표와 부서 적용 로드맵까지 다룸. 무료 도구만 사용(유료 계정 불필요), 보조강사 1명 배치</li>
</ul>
<div class="row2 avoid" style="margin:6px 0 4px">
<div>{img("web-home.png")}<div class="cap">웹 교안 첫 화면(harness-n8n.vercel.app)</div></div>
<div>{img("web-lesson.png")}<div class="cap">교시 교안 예(1일차 6교시) — 단계마다 성공 조건 표시</div></div>
</div>

<h3>3. 세부학습내용</h3>
<table class="f plan avoid">
<tr><th>교과목</th><th>세부 교육내용</th></tr>
<tr><th>n8n 핵심 복습 및<br>Webhook 이해</th><td>◦ 트리거–처리–결과 구조와 표현식 복습, 구글 시트·Gmail·Gemini 노드 재점검(완성본 가져오기) ◦ Webhook 개념(외부 앱이 n8n을 부르는 주소) 이해 ◦ Webhook·Respond to Webhook 노드, Test/Production URL과 Publish, Allowed Origins(CORS) 설정 실습</td></tr>
<tr><th>AI 앱 빌더 활용</th><td>◦ Google AI Studio Build 화면 구성과 문장으로 앱 만드는 원리 ◦ 프롬프트 템플릿으로 민원 접수 화면 생성·수정 ◦ 오류 대처 루틴(오류 문구 복사 → 수정 요청) 반복 연습</td></tr>
<tr><th>앱–자동화 연동<br>서비스 구축</th><td>◦ 앱 입력 → Webhook → 구글 시트 기록 → 접수번호 회신·앱 화면 표시 ◦ 담당자 메일·캘린더 처리 마감·Gemini 안내문 ◦ If 조건 분기로 민원 종류별 담당자 배정, 텔레그램 알림, 접수번호로 처리 상태 조회 화면</td></tr>
<tr><th>배포·보안·운영</th><td>◦ 공유 링크 생성과 동료 상호 시험 ◦ API 키 등 비밀값 관리(AI Studio Secrets·n8n 자격 증명), 앱 코드 점검 ◦ 실행 기록에 남는 개인정보 확인, 개인정보·보안 점검표, 기관 설치형 n8n 전환 안내</td></tr>
<tr><th>나만의 업무 자동화<br>서비스 프로젝트</th><td>◦ 사전조사 기반 부서별 시나리오 확정과 입력–처리–출력 설계서 작성 ◦ 설계서를 프롬프트로 옮겨 앱 생성 → 완성 파일 변형으로 워크플로우 구성 → 연동·테스트·오류 수정 ◦ 발표·상호 피드백, 부서 적용 로드맵 작성</td></tr>
<tr><th>파일·음성 기능 확장<br>(선택 실습)</th><td>◦ PDF 공문 업로드 → 글자 추출 → Gemini 요약 → 앱·메일·텔레그램 전송 ◦ 음성 입력 민원 접수(브라우저 음성 인식) ◦ 웹 교안·완성 파일로 수료 후 자율학습</td></tr>
</table>
</body></html>"""
    with open(OUT_HTML, "w", encoding="utf-8") as fp:
        fp.write(html)
    print("HTML:", OUT_HTML)


def to_pdf():
    url = "file:///" + OUT_HTML.replace("\\", "/")
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={OUT_PDF}", url], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("PDF:", OUT_PDF)


if __name__ == "__main__":
    build()
    to_pdf()
