from __future__ import annotations

import json
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(".").resolve()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
ZIP = Path(sys.argv[1]).resolve()

SRC_PREFIX = "src/obsidia_workflow_governance/"
TARGET = ROOT / "periphery" / "workflow_governance_readonly"

OUT_JSON = ROOT / "docs" / "runtime" / f"OBSIDIA_F30_2_COPY_V5_READONLY_MODULE_{TS}.json"
OUT_MD = ROOT / "docs" / "runtime" / f"OBSIDIA_F30_2_COPY_V5_READONLY_MODULE_{TS}.md"

DANGER_TOKENS = [
    "emits_act=True",
    "can_emit_act=True",
    "kernel_mutation=True",
    "x108_mutation=True",
    "memory_write=True",
    "graphiti_write=True",
    "neo4j_write=True",
    "runtime_execute=True",
    "session.write_transaction",
    "execute_write",
    "git commit",
    "git push",
    "os.system(",
    "subprocess.run",
]


def git(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, text=True, encoding="utf-8", errors="replace").strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def strip_root(name: str) -> str:
    parts = name.split("/", 1)
    if len(parts) == 2 and parts[0].startswith("OBSIDIA_WORKFLOW_GOVERNANCE_PRIMITIVE"):
        return parts[1]
    return name


def rewrite_imports(text: str) -> str:
    return (
        text
        .replace("from obsidia_workflow_governance", "from periphery.workflow_governance_readonly")
        .replace("import obsidia_workflow_governance", "import periphery.workflow_governance_readonly")
    )


def classify_danger(path: Path, line: str, before: str, token: str) -> dict:
    if "QUARANTINE_PATTERNS" in before:
        return {
            "path": str(path).replace("\\", "/"),
            "token": token,
            "classification": "FALSE_POSITIVE_QUARANTINE_PATTERN_LITERAL",
            "confirmed_violation": False,
            "line": line.strip(),
        }

    if line.strip().startswith('"') or line.strip().startswith("'"):
        return {
            "path": str(path).replace("\\", "/"),
            "token": token,
            "classification": "STRING_LITERAL_REVIEW_REQUIRED",
            "confirmed_violation": False,
            "line": line.strip(),
        }

    return {
        "path": str(path).replace("\\", "/"),
        "token": token,
        "classification": "EXECUTION_CONTEXT_REVIEW_REQUIRED",
        "confirmed_violation": True,
        "line": line.strip(),
    }


def scan_target() -> tuple[list[dict], list[dict]]:
    hits = []
    confirmed = []

    for path in sorted(TARGET.rglob("*.py")):
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        lines = text.splitlines()
        for idx, line in enumerate(lines):
            before = "\n".join(lines[max(0, idx - 20): idx + 1])
            for token in DANGER_TOKENS:
                if token in line:
                    h = classify_danger(path.relative_to(ROOT), line, before, token)
                    h["line_number"] = idx + 1
                    hits.append(h)
                    if h["confirmed_violation"]:
                        confirmed.append(h)

    return hits, confirmed


def main():
    if not ZIP.exists():
        raise SystemExit(f"ZIP_NOT_FOUND:{ZIP}")

    if TARGET.exists():
        shutil.rmtree(TARGET)
    TARGET.mkdir(parents=True, exist_ok=True)

    copied = []

    with zipfile.ZipFile(ZIP) as zf:
        names = [n for n in zf.namelist() if not n.endswith("/")]

        for zip_name in names:
            normalized = strip_root(zip_name)
            if not normalized.startswith(SRC_PREFIX):
                continue

            rel = normalized.removeprefix(SRC_PREFIX)
            target_path = TARGET / rel
            target_path.parent.mkdir(parents=True, exist_ok=True)

            raw = zf.read(zip_name)

            if target_path.suffix in {".py", ".md", ".json", ".txt"}:
                text = raw.decode("utf-8-sig", errors="replace")
                if target_path.suffix == ".py":
                    text = rewrite_imports(text)
                lines = [line.rstrip(" \t\r") for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
                text = "\n".join(lines)
                if not text.endswith("\n"):
                    text += "\n"
                target_path.write_text(text, encoding="utf-8", newline="\n")
            else:
                target_path.write_bytes(raw)

            copied.append(str(target_path.relative_to(ROOT)).replace("\\", "/"))

    danger_hits, confirmed = scan_target()

    py_files = sorted(str(p.relative_to(ROOT)).replace("\\", "/") for p in TARGET.rglob("*.py"))

    report = {
        "report_id": f"OBSIDIA_F30_2_COPY_V5_READONLY_MODULE_{TS}",
        "phase": "F30.2",
        "mode": "COPY_V5_READONLY_MODULE_NO_RUNTIME_PATCH",
        "commit": False,
        "tag": False,
        "freeze": False,
        "head": git(["git", "rev-parse", "--short", "HEAD"]),
        "tag_context": git(["git", "tag", "--points-at", "HEAD"]),
        "zip": str(ZIP),
        "source_prefix": SRC_PREFIX,
        "target": str(TARGET.relative_to(ROOT)).replace("\\", "/"),
        "copied_count": len(copied),
        "python_file_count": len(py_files),
        "danger_hit_count": len(danger_hits),
        "confirmed_violation_count": len(confirmed),
        "danger_hits": danger_hits,
        "confirmed_violations": confirmed,
        "copied_files_sample": copied[:80],
        "boundary": {
            "decision_authority": "KX108_ONLY",
            "readonly": True,
            "advisory_only": True,
            "context_signal_only": True,
            "emits_act": False,
            "runtime_execute": False,
            "kernel_mutation": False,
            "x108_mutation": False,
        },
        "locked_decisions": [
            "F30.2 copies V5 into isolated readonly target only.",
            "No runtime route patch in F30.2.",
            "No X108 binding.",
            "No Graphiti/Neo4j write.",
            "No memory write.",
            "Danger tokens inside QUARANTINE_PATTERNS remain false positives.",
            "Decision authority remains KX108_ONLY.",
        ],
        "next_recommended": "F30.3_WORKFLOW_GOVERNANCE_IMPORT_COMPILE_VALIDATE",
        "status": "F30_2_COPY_V5_READONLY_MODULE_DONE",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("# OBSIDIA F30.2 — COPY V5 READONLY MODULE")
    lines.append("")
    lines.append("Mode: COPY_V5_READONLY_MODULE_NO_RUNTIME_PATCH")
    lines.append("Commit: NO")
    lines.append("Tag: NO")
    lines.append("Freeze: NO")
    lines.append("")
    lines.append(f"HEAD: `{report['head']}`")
    lines.append(f"ZIP: `{ZIP}`")
    lines.append(f"Target: `{report['target']}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Copied files: {len(copied)}")
    lines.append(f"- Python files: {len(py_files)}")
    lines.append(f"- Danger hits: {len(danger_hits)}")
    lines.append(f"- Confirmed violations: {len(confirmed)}")
    lines.append("")
    lines.append("## Confirmed violations")
    lines.append("")
    if confirmed:
        for h in confirmed:
            lines.append(f"- `{h['path']}` L{h['line_number']} `{h['token']}` — {h['classification']}")
    else:
        lines.append("- None.")
    lines.append("")
    lines.append("## Next")
    lines.append("")
    lines.append("F30.3_WORKFLOW_GOVERNANCE_IMPORT_COMPILE_VALIDATE")
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append("```text")
    lines.append("DECISION_AUTHORITY=KX108_ONLY")
    lines.append("readonly=true")
    lines.append("advisory_only=true")
    lines.append("context_signal_only=true")
    lines.append("emits_act=false")
    lines.append("runtime_execute=false")
    lines.append("kernel_mutation=false")
    lines.append("x108_mutation=false")
    lines.append("```")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append("F30_2_COPY_V5_READONLY_MODULE_DONE")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("F30_2_COPY_V5_READONLY_MODULE_DONE")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    print(f"TARGET={report['target']}")
    print(f"COPIED={len(copied)}")
    print(f"PY_FILES={len(py_files)}")
    print(f"DANGER_HITS={len(danger_hits)}")
    print(f"CONFIRMED_VIOLATIONS={len(confirmed)}")
    print(f"NEXT={report['next_recommended']}")

    if confirmed:
        raise SystemExit("CONFIRMED_VIOLATIONS_AFTER_COPY")


if __name__ == "__main__":
    main()
