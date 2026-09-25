"""Claude Code PostToolUse hook — 교안 산출물을 고치면 verify.py를 자동 실행한다.

대상(고친 파일 → 다시 검사할 교시):
  1. lessons/, workflows/, prompts/ 아래 파일 중 파일명으로 교시 id를 알 수 있는 것
     (lessons/d1-p3.html, workflows/d1-p3.json, prompts/d1-p4-minwon-app.md → d1-p4)
  2. 어느 교시의 deliverables 또는 workflow.file에 적힌 파일 → 그 파일을 쓰는 모든 교시
     (print/forms/*.html, assets/samples/*, d2-p2.json → d2-p2·d1-p1·opt-voice)
     builds_on으로 이 교시를 잇는 뒤 교시도 함께 검사한다(누적 체인).
  3. 규칙 파일(lessons.json, glossary.md, data-contract.md, sample-data.md) → --all
동작: 검증 실패 시 결과를 stderr로 내보내고 exit 2 → Claude에게 결과가 전달된다.
      대상이 아니거나 통과하면 exit 0(조용히 끝남).
설정: .claude/settings.json 의 hooks.PostToolUse
"""
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
WATCHED = ("lessons", "workflows", "prompts")
RULE_FILES = {"lessons.json", "docs/glossary.md", "docs/data-contract.md", "docs/sample-data.md"}


def lesson_id_for(path: Path, ids: list[str]) -> str | None:
    try:
        rel = path.resolve().relative_to(ROOT)
    except ValueError:
        return None
    if len(rel.parts) != 2 or rel.parts[0] not in WATCHED:
        return None
    stem = rel.stem
    # 가장 긴 id부터 맞춰 본다(opt-pdf-upload-app → opt-pdf)
    for i in sorted(ids, key=len, reverse=True):
        if stem == i or stem.startswith(i + "-"):
            return i
    return None


def targets_for(path: Path, lessons: list[dict]) -> list[str] | str:
    """다시 검사할 교시 id 목록. 규칙 파일이면 '--all'."""
    try:
        rel = path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return []
    if rel in RULE_FILES:
        return "--all"
    ids = [l["id"] for l in lessons]
    found: list[str] = []
    lid = lesson_id_for(path, ids)
    if lid:
        found.append(lid)
    for l in lessons:
        files = [f for group in l.get("deliverables", {}).values() for f in group]
        wf = (l.get("workflow") or {}).get("file")
        if wf:
            files.append(wf)
        if rel in files and l["id"] not in found:
            found.append(l["id"])
    # 누적 체인: 이 교시를 builds_on으로 잇는 뒤 교시
    changed = True
    while changed:
        changed = False
        for l in lessons:
            b = (l.get("workflow") or {}).get("builds_on")
            if b in found and l["id"] not in found:
                found.append(l["id"])
                changed = True
    # 아직 쓰지 않은 교시(todo)는 검사하지 않는다(파일명으로 직접 고른 교시는 예외)
    status = {l["id"]: l.get("status") for l in lessons}
    return [i for i in found if i == lid or status.get(i) != "todo"]


def run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(ROOT / "scripts" / "verify.py"), *args],
                          capture_output=True, text=True, encoding="utf-8", cwd=ROOT)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path") or tool_input.get("path")
    if not file_path:
        return 0
    lessons = json.loads((ROOT / "lessons.json").read_text(encoding="utf-8"))["lessons"]
    targets = targets_for(Path(file_path), lessons)
    if not targets:
        return 0
    runs = [["--all"]] if targets == "--all" else [[t] for t in targets]
    failed = []
    for args in runs:
        r = run(args)
        if r.returncode != 0:
            failed.append((args[0], r.stdout + r.stderr))
    name = Path(file_path).name
    label = "--all" if targets == "--all" else ", ".join(targets)
    if failed:
        sys.stderr.write(f"[hook] {name} 수정 → verify.py {label} 중 실패 {len(failed)}건. 아래를 고치세요.\n")
        for _, out in failed:
            sys.stderr.write(out)
        return 2
    print(f"[hook] verify.py {label} 통과")
    return 0


if __name__ == "__main__":
    sys.exit(main())
