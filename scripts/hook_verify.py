"""Claude Code PostToolUse hook — 교안 산출물을 고치면 verify.py를 자동 실행한다.

대상: lessons/, workflows/, prompts/ 아래 파일 중 파일명으로 교시 id를 알 수 있는 것
      (lessons/d1-p3.html, workflows/d1-p3.json, prompts/d1-p4-minwon-app.md → d1-p4)
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


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path") or tool_input.get("path")
    if not file_path:
        return 0
    ids = [l["id"] for l in json.loads((ROOT / "lessons.json").read_text(encoding="utf-8"))["lessons"]]
    lid = lesson_id_for(Path(file_path), ids)
    if not lid:
        return 0
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "verify.py"), lid],
                       capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    if r.returncode != 0:
        sys.stderr.write(f"[hook] {Path(file_path).name} 수정 → verify.py {lid} 실패. 아래를 고치세요.\n")
        sys.stderr.write(r.stdout + r.stderr)
        return 2
    print(f"[hook] verify.py {lid} 통과")
    return 0


if __name__ == "__main__":
    sys.exit(main())
