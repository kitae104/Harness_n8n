"""verify.py 회귀 테스트 — 규칙 위반 샘플은 FAIL, 오탐 확인 샘플은 PASS가 나오는지 확인한다.

사용법:  python scripts/test_verify.py
verify.py나 glossary·sample-data·data-contract를 고친 뒤 실행한다. 불일치가 있으면 종료코드 1.
샘플은 임시 폴더에 만들고 끝나면 지운다.
"""
import copy
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parent.parent
_tmp = tempfile.TemporaryDirectory()
S = Path(_tmp.name)
tpl = (ROOT/"docs/templates/lesson-lab.html").read_text(encoding="utf-8")
wf = json.loads((ROOT/"workflows/_template.json").read_text(encoding="utf-8"))
ANCHOR = "<p>〔비유 하나로 시작합니다."

def html_with(insert=None, replace=None):
    t = tpl
    if insert: t = t.replace(ANCHOR, insert + "\n    " + ANCHOR, 1)
    if replace: t = t.replace(*replace)
    return t

def cut_summary(t):
    return re.sub(r'\s*<section class="sec" id="summary".*?</section>', "", t, flags=re.S)

def move_summary(t):
    m = re.search(r'\s*<section class="sec" id="summary".*?</section>', t, flags=re.S)
    t = t.replace(m.group(0), "")
    return t.replace('  <section class="sec" id="practice"', m.group(0).strip() + '\n\n  <section class="sec" id="practice"', 1)

def wf_mod(fn):
    w = copy.deepcopy(wf); fn(w); return w

def add_gemini(w):
    w["nodes"] += [
      {"parameters": {"promptType": "define", "text": "=안내문을 써 주세요: {{ $json.body.상세설명 }}", "options": {}},
       "type": "@n8n/n8n-nodes-langchain.chainLlm", "typeVersion": 1.9, "position": [260, 200], "id": "t-ai", "name": "AI 안내문 작성"},
      {"parameters": {"modelName": "models/gemini-2.5-flash", "options": {}},
       "type": "@n8n/n8n-nodes-langchain.lmChatGoogleGemini", "typeVersion": 1, "position": [260, 400], "id": "t-gm", "name": "Google Gemini Chat Model"}]
    w["connections"]["앱에서 받기"]["main"][0].append({"node": "AI 안내문 작성", "type": "main", "index": 0})
    w["connections"]["Google Gemini Chat Model"] = {"ai_languageModel": [[{"node": "AI 안내문 작성", "type": "ai_languageModel", "index": 0}]]}

def cred(w):
    w["nodes"][0]["credentials"] = {"httpHeaderAuth": {"id": "aB3dE5fG7hJ9kL1m", "name": "강사 계정"}}
def badconn(w):
    w["connections"]["앱에서 받기"]["main"][0].append({"node": "없는 노드", "type": "main", "index": 0})
def respmode(w):
    w["nodes"][0]["parameters"]["responseMode"] = "onReceived"
def bottoken(w):
    w["nodes"][1]["parameters"]["responseBody"] = "123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsawA"
def badpath(w):
    w["nodes"][0]["parameters"]["path"] = "minwon2"

# (이름, 종류, 내용, 기대, 확인할 범주/문구, 추가 인자)
cases = [
 ("웹훅 표기(본문)", "html", html_with("<p>웹훅 주소를 복사합니다.</p>"), "FAIL", "금지 표기 '웹훅"),
 ("code.val 안의 '웹훅'", "html", html_with('<p><code class="val">웹훅</code> 버튼을 누릅니다.</p>'), "FAIL", "금지 표기 '웹훅'"),
 ("alt 없는 이미지", "html", html_with('<img src="../assets/css/lesson.css">'), "FAIL", "alt 없는 이미지"),
 ("깨진 링크", "html", html_with('<p><a href="nope.html">다음</a></p>'), "FAIL", "깨진 링크"),
 ("필수 섹션 누락(summary)", "html", cut_summary(tpl), "FAIL", "필수 섹션 data-section=\"summary\""),
 ("섹션 순서 뒤바뀜", "html", move_summary(tpl), "FAIL", "섹션 순서가 어긋남"),
 ("전화번호 010-9876-5432", "html", html_with("<p>연락처: 010-9876-5432</p>"), "FAIL", "010-9876-5432"),
 ("민원인: 이철수", "html", html_with("<p>민원인: 이철수</p>"), "FAIL", "'민원인' 값 '이철수'"),
 ("이름: 박실명", "html", html_with("<p>이름: 박실명</p>"), "FAIL", "'이름' 값 '박실명'"),
 ("<script> 태그", "html", html_with("<script>alert(1)</script>"), "FAIL", "<script> 태그 금지"),
 ("외부 CDN 링크", "html", html_with('', ('<link rel="stylesheet" href="../assets/css/lesson.css">', '<link rel="stylesheet" href="../assets/css/lesson.css">\n<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/x.css">')), "FAIL", "외부 자원 참조 금지"),
 ("주민번호 형태", "html", html_with("<p>900101-1234567</p>"), "FAIL", "주민등록번호"),
 ("실제 이메일", "html", html_with("<p>메일: someone@gmail.com</p>"), "FAIL", "someone@gmail.com"),
 ("todo 교시로 가는 링크", "html", html_with('<p><a href="d2-p4.html">다음 교시</a></p>'), "WARN", "아직 작성 전(todo)"),
 ("서비스 이름: 현장점검 보고 앱", "html", html_with("<p>서비스 이름: 현장점검 보고 앱</p>"), "PASS", None),
 ("시트 이름: 민원대장", "html", html_with("<p>시트 이름: 민원대장</p>"), "PASS", None),
 ("담당자: 민원팀", "html", html_with("<p>담당자: 민원팀</p>"), "PASS", None),
 ("홍길동 / 010-1234-5678 / {본인 이메일}", "html", html_with("<p>이름: 홍길동, 연락처: 010-1234-5678, 받는 사람: {본인 이메일}</p>"), "PASS", None),
 ("표 안의 인명(성명 | 김민원)", "html", html_with("<table><tr><th>성명</th><td>김민원</td></tr></table>"), "PASS", None),
 ("표 안의 인명(성명 | 최실명)", "html", html_with("<table><tr><th>성명</th><td>최실명</td></tr></table>"), "FAIL", "'성명' 옆 칸 '최실명'"),
 ("<code> 안의 /webhook/ 주소", "html", html_with("<p><code>https://example.app.n8n.cloud/webhook/minwon</code></p>"), "PASS", None),
 ("'워크플로우' (워크플로 오탐 방지)", "html", html_with("<p>워크플로우를 저장합니다.</p>"), "PASS", None),
 ("'워크플로' 단독", "html", html_with("<p>워크플로를 저장합니다.</p>"), "FAIL", "금지 표기 '워크플로'"),
 ("풀이 필수 용어에 <dfn> 없음", "html", html_with('<p>이제 Test URL을 복사합니다.</p>'), "FAIL", "'Test URL' 첫 등장에 <dfn>"),
 ("JSON: 견본(정상)", "json", wf, "PASS", None),
 ("JSON: ai_languageModel 연결", "json", wf_mod(add_gemini), "PASS", None),
 ("JSON: 자격 증명 ID 남음", "json", wf_mod(cred), "FAIL", "실제 자격 증명 ID"),
 ("JSON: 없는 노드로 연결", "json", wf_mod(badconn), "FAIL", "도착 노드가 nodes에 없음"),
 ("JSON: responseMode 불일치", "json", wf_mod(respmode), "FAIL", "responseMode"),
 ("JSON: 텔레그램 봇 토큰", "json", wf_mod(bottoken), "FAIL", "텔레그램 봇 토큰"),
 ("JSON: Webhook 경로 ≠ 데이터 약속", "json", wf_mod(badpath), "FAIL", "data-contract"),
 ("JSON: UTF-8 BOM", "jsonbom", wf, "FAIL", "BOM"),
]
rows = []
for i, (name, kind, content, expect, needle) in enumerate(cases, 1):
    if kind == "html":
        p = S / f"s{i:02d}.html"; p.write_text(content, encoding="utf-8")
        args = ["--file", str(p), "--type", "lab", "--base", "lessons"]
    else:
        p = S / f"s{i:02d}.json"
        data = json.dumps(content, ensure_ascii=False, indent=2).encode("utf-8")
        p.write_bytes((b"\xef\xbb\xbf" if kind == "jsonbom" else b"") + data)
        args = ["--file", str(p), "--lesson-id", "d1-p3"]
    r = subprocess.run([sys.executable, str(ROOT/"scripts/verify.py"), *args], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    out = r.stdout
    has_fail = "[FAIL]" in out; has_warn = "[WARN]" in out
    actual = "FAIL" if has_fail else ("WARN" if has_warn else "PASS")
    ok = actual == expect and (needle is None or needle in out)
    reason = ""
    if needle and needle in out:
        reason = next(l for l in out.splitlines() if needle in l).split(": ", 2)[-1][:70]
    elif has_fail or has_warn:
        reason = next(l for l in out.splitlines() if l.startswith(("[FAIL]", "[WARN]")))[:90]
    rows.append((i, name, expect, actual, r.returncode, "O" if ok else "X", reason))
print("| # | 샘플 | 기대 | 실제 | exit | 일치 | 잡아낸 내용 |")
print("|---|---|---|---|---|---|---|")
for row in rows:
    print("| " + " | ".join(str(x).replace("|", "\\|") for x in row) + " |")
bad = sum(1 for r in rows if r[5] == "X")
print(f"\n샘플 {len(rows)}개 — 불일치 {bad}개")
_tmp.cleanup()
sys.exit(1 if bad else 0)
