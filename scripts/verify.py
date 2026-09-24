"""교안 검증 스크립트 — 교시 하나의 산출물을 검사해 PASS/FAIL/WARN 목록을 출력한다.

사용법:
  python scripts/verify.py d1-p3                교시 id의 모든 산출물 검사
  python scripts/verify.py --all                status가 todo가 아닌 모든 교시 검사
  python scripts/verify.py --file PATH [--type lab|activity] [--lesson-id ID] [--base DIR]
                                                파일 하나만 검사(템플릿·샘플 점검용)
                                                .html → 교안 검사(--type 필수)
                                                .json → 워크플로우 검사
                                                .md   → 프롬프트 검사

규칙 원본: docs/writing-guide.md, docs/glossary.md, docs/sample-data.md, docs/data-contract.md
FAIL이 하나라도 있으면 종료코드 1.
주의: python3 는 이 PC에서 스토어 껍데기 명령이므로 반드시 python 으로 실행한다.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
LESSONS_JSON = ROOT / "lessons.json"
GLOSSARY_MD = ROOT / "docs" / "glossary.md"
SAMPLE_MD = ROOT / "docs" / "sample-data.md"
CONTRACT_MD = ROOT / "docs" / "data-contract.md"

REQUIRED_SECTIONS = {
    "lab": ["objectives", "concept", "practice", "mistakes", "summary"],
    "activity": ["objectives", "concept", "activity", "summary"],
}
REQUIRED_CSS = ["style.css", "lecture.css", "lesson.css"]
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
BLOCK_TAGS = {"p", "div", "li", "ol", "ul", "section", "h1", "h2", "h3", "h4", "h5", "h6", "table", "tr",
              "td", "th", "figure", "figcaption", "header", "nav", "main", "aside", "dl", "dt", "dd", "br", "pre",
              "blockquote", "details", "summary"}

NAME_FIELDS = ["성명", "신청자", "민원인", "담당자", "이름"]
NAME_PREFIX_EXCLUDE = ["서비스", "파일", "노드", "시트", "워크플로우", "앱",
                       "탭", "폴더", "문서"]  # 뒤 세 개는 "시트 탭 이름:" 같은 오탐 방지용 추가
DEPT_SUFFIXES = ("팀", "과", "실", "국", "부", "센터", "반")
NON_NAME_WORDS = {"없음", "미정", "배정", "본인", "전원", "필수", "선택", "입력", "텍스트", "예시", "자동", "공란",
                  # 필드·열 이름 자체(필드 대응표에서 "이름 | 이름"처럼 쓰임)
                  "이름", "성명", "신청자", "민원인", "담당자", "연락처", "이메일", "종류", "상세설명", "등록일"}
SURNAMES = set("김이박최정강조윤장임한오서신권황안송류전홍고문양손배백허유남심노하곽성차주우구민진지엄채원천방공현함변염여추도소석선설마길연위표명기반왕금옥육인맹제모탁국어은편용예경봉사부")
ALLOWED_DOMAINS = ("example.com", "example.org", "example.net")
FORBIDDEN_TOKENS = ["TODO", "TBD", "FIXME"]

RE_MOBILE = re.compile(r"(?<!\d)01[016789]-?\d{3,4}-?\d{4}(?!\d)")
RE_LANDLINE = re.compile(r"(?<![\d-])0(?:2|[3-6]\d)-\d{3,4}-\d{4}(?!\d)")
RE_RRN = re.compile(r"(?<!\d)\d{6}-[1-4]\d{6}(?!\d)")
RE_EMAIL = re.compile(r"[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
RE_SECRETS = [
    (re.compile(r"AIza[0-9A-Za-z_\-]{35}"), "Google API 키"),
    (re.compile(r"(?<!\d)\d{8,10}:[A-Za-z0-9_\-]{35}(?!\w)"), "텔레그램 봇 토큰"),
    (re.compile(r"ya29\.[0-9A-Za-z_\-]{20,}"), "Google OAuth 토큰"),
]
RE_FIGURE_TAG = re.compile(r"<figure\b[^>]*>", re.IGNORECASE)
RE_PLACEHOLDER_JSON = re.compile(r"여기에_본인_[0-9A-Za-z가-힣_]+|본인이메일@example\.com")


# ─────────────────────────────── 결과 모음 ───────────────────────────────
class Report:
    def __init__(self, title: str):
        self.title = title
        self.items: list[tuple[str, str, str]] = []  # (level, category, msg)
        self.categories: list[str] = []

    def cat(self, name: str):
        if name not in self.categories:
            self.categories.append(name)

    def fail(self, cat, msg):
        self.cat(cat)
        self.items.append(("FAIL", cat, msg))

    def warn(self, cat, msg):
        self.cat(cat)
        self.items.append(("WARN", cat, msg))

    def info(self, cat, msg):
        self.cat(cat)
        self.items.append(("INFO", cat, msg))

    @property
    def fails(self):
        return [i for i in self.items if i[0] == "FAIL"]

    def print(self):
        print(f"== {self.title} ==")
        failed_cats = {c for lvl, c, _ in self.items if lvl == "FAIL"}
        for c in self.categories:
            if c not in failed_cats:
                print(f"[PASS] {c}")
        for lvl in ("FAIL", "WARN", "INFO"):
            for l, c, m in self.items:
                if l == lvl:
                    print(f"[{l}] {c}: {m}")
        n_fail = len(self.fails)
        n_warn = sum(1 for i in self.items if i[0] == "WARN")
        n_pass = len([c for c in self.categories if c not in failed_cats])
        print(f"결과: {'FAIL' if n_fail else 'PASS'} — 통과 {n_pass}개 항목 / 실패 {n_fail}건 / 경고 {n_warn}건\n")


# ─────────────────────────────── 규칙 파일 읽기 ───────────────────────────────
def md_section(text: str, heading: str) -> str:
    m = re.search(rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def md_table_rows(section: str) -> list[list[str]]:
    rows = []
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("|") or re.match(r"^\|\s*-", line):
            continue
        rows.append([c.strip() for c in line.strip("|").split("|")])
    return rows[1:] if rows else []  # 머리글 제외


def load_glossary():
    text = GLOSSARY_MD.read_text(encoding="utf-8")
    terms = []  # dict(standard, forbidden[], explain_required)
    for row in md_table_rows(md_section(text, "표기 기준")):
        if len(row) < 4:
            continue
        std = re.findall(r"`([^`]+)`", row[0])
        if not std:
            continue
        terms.append({
            "standard": std[0],
            "forbidden": re.findall(r"`([^`]+)`", row[1]),
            "explain": row[3].strip().upper().startswith("Y"),
        })
    return terms


def load_sample_data():
    text = SAMPLE_MD.read_text(encoding="utf-8")
    first_col = lambda h: {r[0] for r in md_table_rows(md_section(text, h)) if r and r[0]}
    return {
        "names": first_col("허용 인명"),
        "phones": {p.replace(" ", "") for p in first_col("허용 전화번호")},
        "emails": first_col("허용 이메일"),
    }


def load_contract_paths() -> dict[str, set[tuple[str, str]]]:
    """교시 id → {(경로, 방식)}. data-contract.md의 'Webhook 경로' 표."""
    if not CONTRACT_MD.exists():
        return {}
    text = CONTRACT_MD.read_text(encoding="utf-8")
    out: dict[str, set[tuple[str, str]]] = {}
    for row in md_table_rows(md_section(text, "Webhook 경로")):
        if len(row) >= 3:
            paths = re.findall(r"`([^`]+)`", row[1])
            method = row[2].strip().upper() or "GET"
            for p in paths:
                out.setdefault(row[0], set()).add((p, method))
    return out


def load_lessons():
    data = json.loads(LESSONS_JSON.read_text(encoding="utf-8"))
    return {l["id"]: l for l in data["lessons"]}


# ─────────────────────────────── 간단한 HTML 트리 ───────────────────────────────
class Node:
    def __init__(self, tag, attrs, parent):
        self.tag = tag
        self.attrs = dict(attrs)
        self.parent = parent
        self.children: list = []  # Node 또는 str

    @property
    def classes(self):
        return (self.attrs.get("class") or "").split()

    def iter(self):
        yield self
        for c in self.children:
            if isinstance(c, Node):
                yield from c.iter()

    def text(self):
        out = []
        for c in self.children:
            out.append(c if isinstance(c, str) else c.text())
        return "".join(out)

    def ancestors(self):
        n = self.parent
        while n is not None:
            yield n
            n = n.parent


class TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", [], None)
        self.cur = self.root
        self.comments: list[str] = []

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.cur)
        self.cur.children.append(node)
        if tag not in VOID_TAGS:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        n = self.cur
        while n is not None and n.tag != tag:
            n = n.parent
        if n is not None and n.parent is not None:
            self.cur = n.parent

    def handle_data(self, data):
        self.cur.children.append(data)

    def handle_comment(self, data):
        self.comments.append(data)


def parse_html(text):
    b = TreeBuilder()
    b.feed(text)
    b.close()
    return b.root, b.comments


def is_skipped_for_terms(node: Node) -> bool:
    """용어 검사에서 제외하는 요소: pre, kbd, script, style, class 없는 code."""
    if node.tag in ("pre", "kbd", "script", "style", "title"):
        return True
    if node.tag == "code" and "val" not in node.classes:
        return True
    return False


def collect_text(root: Node, skip, exclude_prose=None):
    """(전체 텍스트, dfn 구간 목록, 본문 구간 mask)를 만든다.

    skip(node) → 이 요소와 자손 텍스트를 버림
    exclude_prose(node) → 텍스트는 포함하되 '첫 등장' 판정 대상(prose)에서는 뺌
    """
    parts: list[str] = []
    dfn_spans: list[tuple[int, int]] = []
    prose_mask: list[tuple[int, int]] = []
    pos = 0

    def walk(n: Node, in_excl: bool):
        nonlocal pos
        for c in n.children:
            if isinstance(c, str):
                parts.append(c)
                if not in_excl:
                    prose_mask.append((pos, pos + len(c)))
                pos += len(c)
            else:
                if skip(c):
                    continue
                excl = in_excl or bool(exclude_prose and exclude_prose(c))
                if c.tag in BLOCK_TAGS:
                    parts.append("\n")
                    pos += 1
                start = pos
                walk(c, excl)
                if c.tag == "dfn":
                    dfn_spans.append((start, pos))
                if c.tag in BLOCK_TAGS:
                    parts.append("\n")
                    pos += 1

    walk(root, False)
    return "".join(parts), dfn_spans, prose_mask


def term_regex(term: str) -> re.Pattern:
    pat = re.escape(term)
    if re.match(r"[A-Za-z]", term):
        pat = r"(?<![A-Za-z])" + pat
    if re.search(r"[A-Za-z]$", term):
        pat = pat + r"(?![A-Za-z])"
    return re.compile(pat)


# ─────────────────────────────── 공통 검사 ───────────────────────────────
def check_terms(rep: Report, text: str, terms, where: str):
    cat = "용어 표기(glossary)"
    rep.cat(cat)
    # 이메일·URL 안의 글자(예: gmail.com, /webhook/)는 표기 검사 대상이 아니므로 같은 길이의 공백으로 가림
    text = re.sub(r"https?://\S+|[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}", lambda m: " " * len(m.group(0)), text)
    covering = []
    for t in terms:
        for m in term_regex(t["standard"].replace(" ❓", "").strip()).finditer(text):
            covering.append((m.start(), m.end()))
    for t in terms:
        for v in t["forbidden"]:
            for m in term_regex(v).finditer(text):
                if any(s <= m.start() and m.end() <= e and (e - s) > (m.end() - m.start()) for s, e in covering):
                    continue
                ctx = text[max(0, m.start() - 12): m.end() + 12].replace("\n", " ")
                rep.fail(cat, f"{where}: 금지 표기 '{v}' → '{t['standard']}' 사용 (…{ctx}…)")


def check_explanations(rep: Report, text: str, dfn_spans, prose_mask, terms, where: str):
    cat = "용어 풀이(<dfn>)"
    rep.cat(cat)
    for t in terms:
        if not t["explain"]:
            continue
        std = t["standard"].replace("❓", "").strip()
        rx = term_regex(std)
        first = None
        for m in rx.finditer(text):
            if any(s <= m.start() < e for s, e in prose_mask):
                first = m
                break
        if not first:
            continue
        in_dfn = [(s, e) for s, e in dfn_spans if s <= first.start() and first.end() <= e]
        if not in_dfn:
            has_any = any(rx.search(text[s:e]) for s, e in dfn_spans)
            hint = " (뒤쪽에 <dfn>이 있지만 첫 등장이 아님)" if has_any else ""
            rep.fail(cat, f"{where}: '{std}' 첫 등장에 <dfn> 풀이 없음{hint}")


def valid_name_value(value: str, names: set[str]) -> bool:
    """True면 문제없음."""
    v = value.strip().strip("'\"`.,;·)")
    if not v or v.startswith("{") or "{{" in v or v.startswith("=") or v.startswith("$"):
        return True
    if any(v.startswith(n) for n in names):
        return True
    m = re.match(r"^[가-힣]{2,4}", v)
    if not m:
        return True  # 한글 인명 형태가 아님(영문 라벨·설명 등)
    token = m.group(0)
    if token in NON_NAME_WORDS or token.endswith(DEPT_SUFFIXES):
        return True
    if token[0] not in SURNAMES:
        return True
    return False


RE_NAME_FIELD = re.compile(
    r"(?P<field>" + "|".join(NAME_FIELDS) + r")\s*[:：|]\s*(?P<val>[^\s,|<>()\[\]]+)"
)


def name_field_excluded(field: str, before: str) -> bool:
    if field != "이름":
        return False
    b = before.replace(" ", "")
    return any(b.endswith(p) for p in NAME_PREFIX_EXCLUDE)


def check_privacy_text(rep: Report, text: str, sample, where: str):
    cat = "개인정보"
    rep.cat(cat)
    for m in RE_MOBILE.finditer(text):
        raw = m.group(0)
        norm = re.sub(r"^(01\d)-?(\d{3,4})-?(\d{4})$", r"\1-\2-\3", raw)
        if norm in sample["phones"] or re.fullmatch(r"010-0000-\d{4}", norm):
            continue
        rep.fail(cat, f"{where}: 허용 목록에 없는 전화번호 {raw}")
    for m in RE_LANDLINE.finditer(text):
        rep.fail(cat, f"{where}: 일반전화 번호 {m.group(0)}(가상 번호만 허용)")
    for m in RE_RRN.finditer(text):
        rep.fail(cat, f"{where}: 주민등록번호 형태 {m.group(0)}")
    for m in RE_EMAIL.finditer(text):
        addr = m.group(0)
        domain = addr.rsplit("@", 1)[1].lower()
        if domain in ALLOWED_DOMAINS or addr in sample["emails"]:
            continue
        rep.fail(cat, f"{where}: 허용되지 않은 이메일 {addr}(example.com 또는 {{본인 이메일}} 사용)")
    for m in RE_NAME_FIELD.finditer(text):
        field, val = m.group("field"), m.group("val")
        line_start = text.rfind("\n", 0, m.start("field")) + 1
        before = text[line_start:m.start("field")]
        if name_field_excluded(field, before):
            continue
        if not valid_name_value(val, sample["names"]):
            rep.fail(cat, f"{where}: 인명 필드 '{field}' 값 '{val}'이 허용 인명 목록(docs/sample-data.md)에 없음")


def check_privacy_tables(rep: Report, root: Node, sample, where: str):
    """HTML 표: 인명 머리글 옆 칸(행 방향)과 인명 머리글 아래 열(열 방향) 값을 검사."""
    cat = "개인정보"
    for table in (n for n in root.iter() if n.tag == "table"):
        grid = [[c for c in r.children if isinstance(c, Node) and c.tag in ("th", "td")]
                for r in table.iter() if r.tag == "tr"]
        header_row = bool(grid and grid[0] and all(c.tag == "th" for c in grid[0]))
        col_fields = {i: c.text().strip() for i, c in enumerate(grid[0])
                      if c.text().strip() in NAME_FIELDS} if header_row else {}
        for ri, cells in enumerate(grid):
            if header_row and ri == 0:
                continue
            for ci, c in enumerate(cells):
                label = c.text().strip()
                if label in NAME_FIELDS and ci + 1 < len(cells):
                    val = cells[ci + 1].text().strip()
                    if not valid_name_value(val, sample["names"]):
                        rep.fail(cat, f"{where}: 표의 '{label}' 옆 칸 '{val}'이 허용 인명 목록에 없음")
                if ci in col_fields:
                    val = label
                    if not valid_name_value(val, sample["names"]):
                        rep.fail(cat, f"{where}: 표의 '{col_fields[ci]}' 열 값 '{val}'이 허용 인명 목록에 없음")


def check_secrets(rep: Report, text: str, where: str):
    cat = "비밀값"
    rep.cat(cat)
    for rx, label in RE_SECRETS:
        for m in rx.finditer(text):
            rep.fail(cat, f"{where}: {label}로 보이는 문자열 {m.group(0)[:12]}…")


def check_tokens(rep: Report, text: str, where: str):
    cat = "미완성 표시"
    rep.cat(cat)
    for tok in FORBIDDEN_TOKENS:
        if re.search(rf"(?<![A-Za-z]){tok}(?![A-Za-z])", text):
            rep.fail(cat, f"{where}: '{tok}' 표시가 남아 있음")
    if "lorem ipsum" in text.lower():
        rep.fail(cat, f"{where}: 'lorem ipsum' 표시가 남아 있음")


def rel(p: Path) -> str:
    try:
        return p.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return p.as_posix()


# ─────────────────────────────── HTML 교안 검사 ───────────────────────────────
def check_html(rep: Report, path: Path, ltype: str, lesson: dict | None, lessons: dict, terms, sample,
               base: Path | None = None):
    where = rel(path)
    base = base or path.parent  # 링크 기준 폴더(템플릿은 lessons/ 기준으로 검사)
    raw = path.read_text(encoding="utf-8")
    root, comments = parse_html(raw)
    lesson_id = lesson["id"] if lesson else None

    # ── 기본 구조
    cat = "HTML 구조"
    rep.cat(cat)
    mains = [n for n in root.iter() if "data-lesson-id" in n.attrs]
    if not mains:
        rep.fail(cat, f"{where}: data-lesson-id 가 있는 <main>이 없음")
        main = root
        file_id = None
    else:
        main = mains[0]
        file_id = main.attrs.get("data-lesson-id")
        if lesson_id and file_id != lesson_id:
            rep.fail(cat, f"{where}: data-lesson-id='{file_id}' ≠ '{lesson_id}'")
        if main.attrs.get("data-type") != ltype:
            rep.fail(cat, f"{where}: data-type='{main.attrs.get('data-type')}' ≠ lessons.json type '{ltype}'")
    html_el = next((n for n in root.iter() if n.tag == "html"), None)
    if not html_el or html_el.attrs.get("lang") != "ko":
        rep.fail(cat, f"{where}: <html lang=\"ko\"> 가 아님")
    css = [n.attrs.get("href", "") for n in root.iter() if n.tag == "link" and n.attrs.get("rel") == "stylesheet"]
    css_names = [c.rsplit("/", 1)[-1] for c in css]
    if [c for c in css_names if c in REQUIRED_CSS] != REQUIRED_CSS:
        rep.fail(cat, f"{where}: CSS는 {', '.join(REQUIRED_CSS)} 순서로 불러와야 함(현재: {', '.join(css_names) or '없음'})")

    # ── 섹션
    cat = "필수 섹션"
    rep.cat(cat)
    secs = [(i, n) for i, n in enumerate(root.iter()) if "data-section" in n.attrs]
    first = {}
    for i, n in secs:
        first.setdefault(n.attrs["data-section"], (i, n))
    required = list(REQUIRED_SECTIONS[ltype])
    need_import = bool(lesson and lesson.get("workflow")) or "import" in first
    if need_import:
        required.append("import")
    for s in required:
        if s not in first:
            rep.fail(cat, f"{where}: 필수 섹션 data-section=\"{s}\" 없음 (type={ltype})")
    order = ["objectives", "concept", "practice" if ltype == "lab" else "activity", "quiz", "summary", "import"]
    present = [(first[s][0], s) for s in order if s in first]
    expected = [s for s in order if s in first]
    actual = [s for _, s in sorted(present)]
    if actual != expected:
        rep.fail(cat, f"{where}: 섹션 순서가 어긋남 — 기대 {' → '.join(expected)}, 실제 {' → '.join(actual)}")
    if "concept" in first and first["concept"][1].attrs.get("data-minutes") != "10":
        rep.fail(cat, f"{where}: 개념 블록(concept)에 data-minutes=\"10\" 없음")
    if "mistakes" in first and "concept" in first and first["mistakes"][0] < first["concept"][0]:
        rep.fail(cat, f"{where}: 자주 하는 실수 박스가 개념 블록보다 앞에 있음")
    for _, n in secs:
        if n.attrs["data-section"] == "mistakes" and not n.text().strip().startswith("자주 하는 실수"):
            rep.fail(cat, f"{where}: 자주 하는 실수 박스의 제목(첫 <b>)이 '자주 하는 실수'가 아님")

    # ── 캡처·이미지
    cat = "캡처·이미지"
    rep.cat(cat)
    for tag in RE_FIGURE_TAG.findall(raw):
        m = re.fullmatch(r'<figure class="capture" id="fig-([a-z0-9][a-z0-9-]*)">', tag)
        if not m:
            rep.fail(cat, f"{where}: figure 형식 오류(class가 먼저, id='fig-…') → {tag}")
        elif file_id and not m.group(1).startswith(file_id + "-"):
            rep.fail(cat, f"{where}: 캡처 id는 'fig-{file_id}-번호' 형식이어야 함 → {tag}")
    for n in root.iter():
        if n.tag == "img" and not (n.attrs.get("alt") or "").strip():
            rep.fail(cat, f"{where}: alt 없는 이미지 src='{n.attrs.get('src')}'")
    if ltype == "lab" and "practice" in first:
        prac = first["practice"][1]
        if not any(n.tag == "ol" and "steps" in n.classes for n in prac.iter()):
            rep.fail(cat, f"{where}: 실습(practice)에 <ol class=\"steps\"> 번호 단계가 없음")
        if not any(n.tag == "figure" and "capture" in n.classes for n in prac.iter()):
            rep.fail(cat, f"{where}: 실습(practice)에 캡처 자리(figure.capture)가 없음")
    pending = sum(1 for n in root.iter() if n.tag == "figure" and "capture" in n.classes
                  and not any(c.tag == "img" for c in n.iter()))
    if pending:
        rep.info(cat, f"{where}: 아직 촬영하지 않은 캡처 {pending}개 (python scripts/apply_captures.py --list)")

    # ── 외부 자원
    cat = "외부 자원·스크립트"
    rep.cat(cat)
    for n in root.iter():
        if n.tag == "script":
            rep.fail(cat, f"{where}: <script> 태그 금지(교육망·기존 교안 규칙)")
        if n.tag in ("link", "img", "iframe", "source", "script", "video", "audio"):
            for a in ("href", "src"):
                v = n.attrs.get(a) or ""
                if re.match(r"^(?:https?:)?//", v, re.I):
                    rep.fail(cat, f"{where}: 외부 자원 참조 금지 <{n.tag} {a}=\"{v}\">")

    # ── 링크
    cat = "내부 링크"
    rep.cat(cat)
    ids = {n.attrs["id"] for n in root.iter() if "id" in n.attrs}
    todo_html = {(ROOT / "lessons" / f"{i}.html").resolve(): l for i, l in lessons.items() if l.get("status") == "todo"}
    for n in root.iter():
        for a in ("href", "src"):
            v = n.attrs.get(a)
            if not v or n.tag not in ("a", "img", "link", "source", "iframe"):
                continue
            if v.startswith(("mailto:", "tel:", "data:", "javascript:")) or urlparse(v).scheme or v.startswith("//"):
                continue
            target, _, frag = v.partition("#")
            if not target:
                if frag and frag not in ids:
                    rep.fail(cat, f"{where}: 같은 문서 안에 id='{frag}' 없음 (href='{v}')")
                continue
            resolved = (base / unquote(target.split("?", 1)[0])).resolve()
            if not resolved.exists():
                if resolved in todo_html:
                    rep.warn(cat, f"{where}: 아직 작성 전(todo) 교시로 가는 링크 '{v}'")
                else:
                    rep.fail(cat, f"{where}: 깨진 링크 '{v}'")
                continue
            if frag and resolved.suffix == ".html":
                troot, _ = parse_html(resolved.read_text(encoding="utf-8"))
                if frag not in {x.attrs["id"] for x in troot.iter() if "id" in x.attrs}:
                    rep.fail(cat, f"{where}: '{target}'에 id='{frag}' 없음")
            if not target.endswith((".html", ".json", ".css", ".png", ".jpg", ".jpeg", ".webp", ".svg", ".md", ".pdf")) and not resolved.is_dir():
                rep.warn(cat, f"{where}: 확장자 없는 링크 '{v}' — .html까지 쓰기")

    # ── Import 안내
    if "import" in first:
        cat = "Import 안내"
        rep.cat(cat)
        imp = first["import"][1]
        imp_text = imp.text()
        if "자격 증명" not in imp_text:
            rep.fail(cat, f"{where}: Import 섹션에 '자격 증명 다시 연결' 단계가 없음")
        wf = (lesson or {}).get("workflow") or {}
        links = [(base / unquote(n.attrs.get("href", ""))).resolve() for n in imp.iter() if n.tag == "a" and n.attrs.get("href")]
        if wf.get("file"):
            want = (ROOT / wf["file"]).resolve()
            if want not in links:
                rep.fail(cat, f"{where}: Import 섹션에 '{wf['file']}' 내려받기 링크가 없음")
            if want.exists():
                try:
                    wtext = want.read_text(encoding="utf-8-sig")
                    for ph in sorted(set(RE_PLACEHOLDER_JSON.findall(wtext))):
                        if ph not in imp_text:
                            rep.warn(cat, f"{where}: JSON 자리표시자 '{ph}'를 바꾸라는 안내가 Import 섹션에 없음")
                except OSError:
                    pass
        elif not any(n.tag == "a" and "dl" in n.classes for n in imp.iter()):
            rep.fail(cat, f"{where}: Import 섹션에 내려받기 링크(a.dl)가 없음")

    # ── 용어·풀이
    body = next((n for n in root.iter() if n.tag == "body"), root)
    text_all, _, _ = collect_text(body, is_skipped_for_terms)
    title = next((n for n in root.iter() if n.tag == "title"), None)
    check_terms(rep, text_all + ("\n" + title.text() if title else ""), terms, where)

    def exclude_prose(n: Node):
        # 제목·목차·학습목표·단계 제목·그림 캡션은 '첫 등장' 판정에서 뺀다(본문 첫 등장에 풀이를 붙임)
        return (n.tag in ("h1", "h2", "h3", "h4", "nav", "header")
                or n.attrs.get("data-section") == "objectives"
                or bool({"step-title", "capture-cap", "dl"} & set(n.classes)))

    text_p, dfns, mask = collect_text(body, is_skipped_for_terms, exclude_prose)
    check_explanations(rep, text_p, dfns, mask, terms, where)

    # ── 개인정보·비밀값·미완성
    full_text, _, _ = collect_text(root, lambda n: n.tag in ("script", "style"))
    attr_text = "\n".join(v for n in root.iter() for v in n.attrs.values() if v)
    check_privacy_text(rep, full_text + "\n" + attr_text + "\n" + "\n".join(comments), sample, where)
    check_privacy_tables(rep, root, sample, where)
    check_secrets(rep, raw, where)
    check_tokens(rep, full_text + "\n" + "\n".join(comments), where)

    fc = [c for c in comments if "FACT-CHECK" in c]
    if fc:
        rep.warn("사실 확인", f"{where}: 확인되지 않은 서술 {len(fc)}곳(<!-- FACT-CHECK -->) — docs/fact-check.md 확인 필요")


# ─────────────────────────────── 워크플로우 JSON 검사 ───────────────────────────────
def iter_json_strings(obj, key=None):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from iter_json_strings(v, k)
    elif isinstance(obj, list):
        for v in obj:
            yield from iter_json_strings(v, key)
    elif isinstance(obj, str):
        yield key, obj


def load_workflow(rep: Report, path: Path, cat: str):
    where = rel(path)
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        rep.fail(cat, f"{where}: UTF-8 BOM이 붙어 있음(n8n Import 오류 원인)")
        raw = raw[3:]
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        rep.fail(cat, f"{where}: JSON 파싱 실패 — {e}")
        return None


def check_workflow(rep: Report, path: Path, lesson: dict | None, lessons: dict, contract: dict, sample):
    where = rel(path)
    cat = "워크플로우 JSON"
    rep.cat(cat)
    wf = load_workflow(rep, path, cat)
    if wf is None:
        return
    if not isinstance(wf, dict) or not isinstance(wf.get("nodes"), list) or not isinstance(wf.get("connections"), dict):
        rep.fail(cat, f"{where}: 최상위에 nodes(목록)와 connections(객체)가 있어야 함")
        return
    nodes = wf["nodes"]
    if not nodes:
        rep.fail(cat, f"{where}: 노드가 하나도 없음")
    names = []
    for i, n in enumerate(nodes):
        label = n.get("name", f"#{i}") if isinstance(n, dict) else f"#{i}"
        if not isinstance(n, dict):
            rep.fail(cat, f"{where}: 노드 {label}가 객체가 아님")
            continue
        if not isinstance(n.get("name"), str) or not n["name"]:
            rep.fail(cat, f"{where}: 노드 {label}에 name 없음")
        if not isinstance(n.get("type"), str) or not n["type"]:
            rep.fail(cat, f"{where}: 노드 '{label}'에 type 없음")
        if not isinstance(n.get("typeVersion"), (int, float)):
            rep.fail(cat, f"{where}: 노드 '{label}'에 typeVersion(숫자) 없음")
        pos = n.get("position")
        if not (isinstance(pos, list) and len(pos) == 2 and all(isinstance(x, (int, float)) for x in pos)):
            rep.fail(cat, f"{where}: 노드 '{label}'의 position이 [x, y] 형식이 아님")
        if not isinstance(n.get("parameters"), dict):
            rep.fail(cat, f"{where}: 노드 '{label}'에 parameters(객체) 없음")
        names.append(n.get("name"))
    dup = {x for x in names if names.count(x) > 1}
    if dup:
        rep.fail(cat, f"{where}: 노드 이름 중복 {sorted(dup)}")
    nameset = set(names)
    by_name = {n.get("name"): n for n in nodes if isinstance(n, dict)}

    # 연결
    edges: dict[str, list[str]] = {}
    for src, types in wf["connections"].items():
        if src not in nameset:
            rep.fail(cat, f"{where}: connections의 출발 노드 '{src}'가 nodes에 없음")
        if not isinstance(types, dict):
            rep.fail(cat, f"{where}: connections['{src}'] 형식 오류")
            continue
        for ctype, outputs in types.items():
            if not isinstance(outputs, list):
                rep.fail(cat, f"{where}: connections['{src}']['{ctype}']가 목록이 아님")
                continue
            for out in outputs:
                for link in out or []:
                    if not isinstance(link, dict) or "node" not in link:
                        rep.fail(cat, f"{where}: connections['{src}']['{ctype}']에 잘못된 연결")
                        continue
                    if link["node"] not in nameset:
                        rep.fail(cat, f"{where}: '{src}' → '{link['node']}' 연결의 도착 노드가 nodes에 없음")
                    if not isinstance(link.get("index", 0), int):
                        rep.fail(cat, f"{where}: '{src}' → '{link['node']}' 연결의 index가 정수가 아님")
                    if ctype == "main":
                        edges.setdefault(src, []).append(link["node"])

    types = {n.get("name"): (n.get("type") or "") for n in nodes if isinstance(n, dict)}
    triggers = [nm for nm, t in types.items() if "trigger" in t.lower() or t.endswith(".webhook")]
    if not triggers:
        rep.fail(cat, f"{where}: 트리거 노드가 없음")

    # Webhook ↔ Respond to Webhook
    webhooks = [nm for nm, t in types.items() if t.endswith(".webhook")]
    responders = {nm for nm, t in types.items() if t.endswith(".respondToWebhook")}
    for wh in webhooks:
        seen, stack = set(), [wh]
        while stack:
            cur = stack.pop()
            for nx in edges.get(cur, []):
                if nx not in seen:
                    seen.add(nx)
                    stack.append(nx)
        params = by_name[wh].get("parameters", {}) or {}
        if seen & responders and params.get("responseMode") != "responseNode":
            rep.fail(cat, f"{where}: Webhook '{wh}' 뒤에 Respond to Webhook이 있는데 responseMode가 'responseNode'가 아님")
        if not (params.get("options") or {}).get("allowedOrigins"):
            rep.warn(cat, f"{where}: Webhook '{wh}'에 Allowed Origins(CORS) 옵션이 명시되어 있지 않음(기본값 *이지만 교안과 맞게 명시 권장, fact-check F20)")

    # 데이터 약속: Webhook 경로
    lid = lesson["id"] if lesson else None
    if lid and lid in contract:
        cat2 = "데이터 약속(경로)"
        rep.cat(cat2)
        actual = set()
        for w in webhooks:
            prm = by_name[w].get("parameters", {}) or {}
            actual.add((prm.get("path") or "(없음)", (prm.get("httpMethod") or "GET").upper()))  # 기본 방식 GET
        if actual != contract[lid]:
            fmt = lambda s: sorted(f"{m} {p}" for p, m in s)
            rep.fail(cat2, f"{where}: Webhook 경로·방식 {fmt(actual)} ≠ data-contract {fmt(contract[lid])}")

    # 시간대: $now를 쓰면 워크플로우 시간대를 서울로 고정해야 함(기본은 인스턴스 시간대 또는 America/New_York, fact-check F100)
    if "$now" in json.dumps(wf, ensure_ascii=False):
        cat_tz = "시간대"
        rep.cat(cat_tz)
        tz = (wf.get("settings") or {}).get("timezone")
        if tz != "Asia/Seoul":
            rep.fail(cat_tz, f"{where}: $now를 쓰는데 settings.timezone이 'Asia/Seoul'이 아님(현재 {tz!r}) — 오전에는 날짜가 하루 전으로 찍힘")

    # 자격 증명
    cat3 = "자격 증명"
    rep.cat(cat3)
    for n in nodes:
        creds = n.get("credentials") if isinstance(n, dict) else None
        if isinstance(creds, dict):
            for ctype, c in creds.items():
                if isinstance(c, dict) and str(c.get("id", "")).strip():
                    rep.fail(cat3, f"{where}: 노드 '{n.get('name')}'에 실제 자격 증명 ID가 남아 있음({ctype}.id='{c['id']}') — id를 지우거나 비울 것")
    if wf.get("pinData"):
        rep.warn(cat3, f"{where}: pinData(고정 실행 데이터)가 들어 있음 — 실제 데이터가 아닌지 확인")

    # 누적 체인
    if lesson and (lesson.get("workflow") or {}).get("builds_on"):
        prev_id = lesson["workflow"]["builds_on"]
        prev = lessons.get(prev_id, {})
        prev_file = ROOT / ((prev.get("workflow") or {}).get("file") or f"workflows/{prev_id}.json")
        cat4 = "누적 체인"
        rep.cat(cat4)
        if not prev_file.exists():
            rep.warn(cat4, f"{where}: 앞 교시 {prev_id}의 JSON이 없어 체인 검사를 건너뜀")
        else:
            pwf = load_workflow(Report("tmp"), prev_file, cat4) or {}
            pnames = {n.get("name") for n in pwf.get("nodes", []) if isinstance(n, dict)}
            missing = sorted(pnames - nameset)
            if missing:
                rep.fail(cat4, f"{where}: 앞 교시 {prev_id}의 노드가 빠짐 {missing}")

    # 개인정보·비밀값·미완성
    all_strings = []
    for key, s in iter_json_strings(wf):
        all_strings.append(s)
        if key in NAME_FIELDS and not valid_name_value(s, sample["names"]):
            rep.fail("개인정보", f"{where}: JSON 키 '{key}'의 값 '{s}'이 허용 인명 목록에 없음")
    blob = "\n".join(all_strings)
    check_privacy_text(rep, blob, sample, where)
    check_secrets(rep, path.read_text(encoding="utf-8-sig"), where)
    check_tokens(rep, blob, where)


# ─────────────────────────────── 프롬프트·기타 파일 ───────────────────────────────
def check_prompt(rep: Report, path: Path, sample):
    where = rel(path)
    cat = "프롬프트 형식"
    rep.cat(cat)
    text = path.read_text(encoding="utf-8")
    for h in ("## 복사할 프롬프트", "## 검증 기록"):
        if not re.search(rf"^{re.escape(h)}\s*$", text, re.M):
            rep.fail(cat, f"{where}: '{h}' 제목이 없음")
    check_privacy_text(rep, text, sample, where)
    check_secrets(rep, text, where)
    check_tokens(rep, text, where)
    if re.search(r"https?://[^\s)]*/webhook(-test)?/", text):
        rep.fail(cat, f"{where}: 실제 Webhook 주소가 들어 있음 — {{Production URL}} 자리표시자로 바꿀 것")


def check_other(rep: Report, path: Path, sample, terms, lessons):
    if path.suffix == ".html":
        where = rel(path)
        raw = path.read_text(encoding="utf-8")
        root, comments = parse_html(raw)
        full_text, _, _ = collect_text(root, lambda n: n.tag in ("script", "style"))
        check_privacy_text(rep, full_text, sample, where)
        check_privacy_tables(rep, root, sample, where)
        check_secrets(rep, raw, where)
        check_tokens(rep, full_text, where)
        body = next((n for n in root.iter() if n.tag == "body"), root)
        check_terms(rep, collect_text(body, is_skipped_for_terms)[0], terms, where)
    else:
        text = path.read_text(encoding="utf-8", errors="replace")
        check_privacy_text(rep, text, sample, rel(path))
        check_secrets(rep, text, rel(path))


# ─────────────────────────────── 실행 ───────────────────────────────
def verify_lesson(lesson_id: str, lessons, terms, sample, contract) -> Report:
    lesson = lessons[lesson_id]
    rep = Report(f"verify {lesson_id} ({lesson['type']}) — {lesson['title']}")
    d = lesson["deliverables"]
    cat = "산출물"
    rep.cat(cat)
    for kind in ("html", "json", "prompts", "other"):
        for f in d.get(kind, []):
            if not (ROOT / f).exists():
                rep.fail(cat, f"{f} 없음")
    wf = lesson.get("workflow")
    if wf and wf.get("role") == "reference" and not (ROOT / wf["file"]).exists():
        owner = next((i for i, l in lessons.items() if (l.get("workflow") or {}).get("file") == wf["file"]
                      and l["workflow"].get("role") == "own"), "?")
        rep.fail(cat, f"참조하는 {wf['file']} 없음 — 참조 교시 {owner}를 먼저 완료할 것(lessons.json authoring_order)")

    for f in d.get("html", []):
        p = ROOT / f
        if p.exists():
            check_html(rep, p, lesson["type"], lesson, lessons, terms, sample)
    for f in d.get("json", []):
        p = ROOT / f
        if p.exists():
            check_workflow(rep, p, lesson, lessons, contract, sample)
    for f in d.get("prompts", []):
        p = ROOT / f
        if p.exists():
            check_prompt(rep, p, sample)
    for f in d.get("other", []):
        p = ROOT / f
        if p.exists():
            check_other(rep, p, sample, terms, lessons)
    return rep


def main() -> int:
    ap = argparse.ArgumentParser(description="교안 검증")
    ap.add_argument("lesson_id", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--file")
    ap.add_argument("--type", choices=["lab", "activity"])
    ap.add_argument("--lesson-id", dest="as_lesson")
    ap.add_argument("--base", help="HTML 링크를 해석할 기준 폴더(예: lessons — 템플릿 점검용)")
    a = ap.parse_args()

    lessons = load_lessons()
    terms = load_glossary()
    sample = load_sample_data()
    contract = load_contract_paths()

    reports = []
    if a.file:
        p = Path(a.file)
        if not p.is_absolute():
            p = (Path.cwd() / p)
        if not p.exists():
            print(f"파일 없음: {p}")
            return 1
        lesson = lessons.get(a.as_lesson) if a.as_lesson else None
        rep = Report(f"verify --file {p.name}")
        if p.suffix == ".html":
            ltype = a.type or (lesson or {}).get("type")
            if not ltype:
                print("--file 로 HTML을 검사할 때는 --type lab|activity 가 필요합니다")
                return 1
            check_html(rep, p, ltype, lesson, lessons, terms, sample,
                       base=(ROOT / a.base) if a.base else None)
        elif p.suffix == ".json":
            check_workflow(rep, p, lesson, lessons, contract, sample)
        elif p.suffix == ".md":
            check_prompt(rep, p, sample)
        else:
            check_other(rep, p, sample, terms, lessons)
        reports.append(rep)
    elif a.all:
        ids = [i for i, l in lessons.items() if l.get("status") != "todo"]
        if not ids:
            print("검사할 교시가 없습니다(모든 교시가 todo).")
            return 0
        reports = [verify_lesson(i, lessons, terms, sample, contract) for i in ids]
    elif a.lesson_id:
        if a.lesson_id not in lessons:
            print(f"lessons.json에 없는 교시 id: {a.lesson_id}")
            print("가능한 id:", ", ".join(lessons))
            return 1
        reports = [verify_lesson(a.lesson_id, lessons, terms, sample, contract)]
    else:
        ap.print_help()
        return 1

    for r in reports:
        r.print()
    return 1 if any(r.fails for r in reports) else 0


if __name__ == "__main__":
    sys.exit(main())
