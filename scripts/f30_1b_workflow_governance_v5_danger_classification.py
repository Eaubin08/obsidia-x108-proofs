from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(".").resolve()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

zip_path = Path(sys.argv[1]).resolve()

OUT_JSON = ROOT / "docs" / "runtime" / f"OBSIDIA_F30_1B_WORKFLOW_GOVERNANCE_V5_DANGER_CLASSIFICATION_{TS}.json"
OUT_MD = ROOT / "docs" / "runtime" / f"OBSIDIA_F30_1B_WORKFLOW_GOVERNANCE_V5_DANGER_CLASSIFICATION_{TS}.md"

DANGER_TOKENS = [
    "session.write_transaction",
    "execute_write",
    "git commit",
    "git push",
    "os.system(",
    "subprocess.run",
    "runtime_execute=True",
    "emits_act=True",
    "can_emit_act=True",
    "kernel_mutation=True",
    "x108_mutation=True",
    "memory_write=True",
    "graphiti_write=True",
    "neo4j_write=True",
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


def latest_f30_1() -> Path | None:
    files = sorted(
        (ROOT / "docs" / "runtime").glob("OBSIDIA_F30_1_WORKFLOW_GOVERNANCE_V5_AUDIT_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return files[0] if files else None


def classify_hit(lines: list[str], idx: int, token: str) -> dict:
    # idx is 0-based
    line = lines[idx]
    before = "\n".join(lines[max(0, idx - 20):idx + 1])

    if "QUARANTINE_PATTERNS" in before:
        return {
            "token": token,
            "line_number": idx + 1,
            "line": line.strip(),
            "classification": "FALSE_POSITIVE_QUARANTINE_PATTERN_LITERAL",
            "confirmed_violation": False,
            "reason": "Danger token is stored as a string inside QUARANTINE_PATTERNS, not executed.",
        }

    if line.strip().startswith('"') or line.strip().startswith("'"):
        return {
            "token": token,
            "line_number": idx + 1,
            "line": line.strip(),
            "classification": "STRING_LITERAL_REVIEW_REQUIRED",
            "confirmed_violation": False,
            "reason": "Danger token appears as a string literal. Review required, but not executable by itself.",
        }

    return {
        "token": token,
        "line_number": idx + 1,
        "line": line.strip(),
        "classification": "EXECUTION_CONTEXT_REVIEW_REQUIRED",
        "confirmed_violation": True,
        "reason": "Danger token appears outside recognized quarantine literal context.",
    }


def main():
    f30_1_report = latest_f30_1()
    f30_1_data = {}
    if f30_1_report:
        f30_1_data = json.loads(f30_1_report.read_text(encoding="utf-8"))

    target_normalized = "src/obsidia_workflow_governance/repo_aware/obsidia_x108_repo_map.py"

    with zipfile.ZipFile(zip_path) as zf:
        all_names = [n for n in zf.namelist() if not n.endswith("/")]
        name_by_norm = {strip_root(n): n for n in all_names}

        if target_normalized not in name_by_norm:
            raise SystemExit(f"DANGER_TARGET_NOT_FOUND:{target_normalized}")

        zip_name = name_by_norm[target_normalized]
        text = zf.read(zip_name).decode("utf-8-sig", errors="replace")
        lines = text.splitlines()

        hits = []
        for i, line in enumerate(lines):
            for token in DANGER_TOKENS:
                if token in line:
                    hits.append(classify_hit(lines, i, token))

    confirmed = [h for h in hits if h["confirmed_violation"]]
    false_positive = [h for h in hits if not h["confirmed_violation"]]

    copy_gate = "ALLOW_COPY_WITH_REVIEW_NOTE" if not confirmed else "BLOCK_COPY_CONFIRMED_VIOLATION"

    report = {
        "report_id": f"OBSIDIA_F30_1B_WORKFLOW_GOVERNANCE_V5_DANGER_CLASSIFICATION_{TS}",
        "phase": "F30.1B",
        "mode": "DANGER_CLASSIFICATION_ONLY_NO_PATCH",
        "commit": False,
        "tag": False,
        "freeze": False,
        "head": git(["git", "rev-parse", "--short", "HEAD"]),
        "tag_context": git(["git", "tag", "--points-at", "HEAD"]),
        "zip_path": str(zip_path),
        "source_f30_1_report": str(f30_1_report) if f30_1_report else None,
        "target_file": target_normalized,
        "hit_count": len(hits),
        "false_positive_count": len(false_positive),
        "confirmed_violation_count": len(confirmed),
        "copy_gate": copy_gate,
        "hits": hits,
        "decision": {
            "copy_now": False,
            "runtime_patch_now": False,
            "next_if_clean": "F30.2_COPY_V5_READONLY_MODULE",
            "next_if_blocked": "F30.1C_SANITIZE_OR_EXCLUDE_DANGER_FILE",
        },
        "locked_decisions": [
            "F30.1B is classification-only.",
            "No runtime patch.",
            "No ZIP copy in F30.1B.",
            "Danger tokens inside QUARANTINE_PATTERNS are not executable behavior.",
            "Decision authority remains KX108_ONLY.",
        ],
        "status": "F30_1B_WORKFLOW_GOVERNANCE_V5_DANGER_CLASSIFICATION_DONE",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines_md = []
    lines_md.append("# OBSIDIA F30.1B — WORKFLOW GOVERNANCE V5 DANGER CLASSIFICATION")
    lines_md.append("")
    lines_md.append("Mode: DANGER_CLASSIFICATION_ONLY_NO_PATCH")
    lines_md.append("Commit: NO")
    lines_md.append("Tag: NO")
    lines_md.append("Freeze: NO")
    lines_md.append("")
    lines_md.append(f"HEAD: `{report['head']}`")
    lines_md.append(f"ZIP: `{zip_path}`")
    lines_md.append(f"Target: `{target_normalized}`")
    lines_md.append("")
    lines_md.append("## Summary")
    lines_md.append("")
    lines_md.append(f"- Hits: {len(hits)}")
    lines_md.append(f"- False positives: {len(false_positive)}")
    lines_md.append(f"- Confirmed violations: {len(confirmed)}")
    lines_md.append(f"- Copy gate: `{copy_gate}`")
    lines_md.append("")
    lines_md.append("## Classified hits")
    lines_md.append("")
    for h in hits:
        lines_md.append(f"- L{h['line_number']} `{h['token']}` — `{h['classification']}`")
        lines_md.append(f"  - confirmed_violation: {h['confirmed_violation']}")
        lines_md.append(f"  - reason: {h['reason']}")
        lines_md.append(f"  - line: `{h['line']}`")
    lines_md.append("")
    lines_md.append("## Next")
    lines_md.append("")
    if confirmed:
        lines_md.append("F30.1C_SANITIZE_OR_EXCLUDE_DANGER_FILE")
    else:
        lines_md.append("F30.2_COPY_V5_READONLY_MODULE")
    lines_md.append("")
    lines_md.append("## Boundary")
    lines_md.append("")
    lines_md.append("```text")
    lines_md.append("DECISION_AUTHORITY=KX108_ONLY")
    lines_md.append("readonly=true")
    lines_md.append("runtime_execute=false")
    lines_md.append("emits_act=false")
    lines_md.append("kernel_mutation=false")
    lines_md.append("x108_mutation=false")
    lines_md.append("```")
    lines_md.append("")
    lines_md.append("## Status")
    lines_md.append("")
    lines_md.append("F30_1B_WORKFLOW_GOVERNANCE_V5_DANGER_CLASSIFICATION_DONE")
    lines_md.append("")

    OUT_MD.write_text("\n".join(lines_md), encoding="utf-8")

    print("F30_1B_WORKFLOW_GOVERNANCE_V5_DANGER_CLASSIFICATION_DONE")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    print(f"HITS={len(hits)}")
    print(f"FALSE_POSITIVE={len(false_positive)}")
    print(f"CONFIRMED_VIOLATIONS={len(confirmed)}")
    print(f"COPY_GATE={copy_gate}")
    print(f"NEXT={report['decision']['next_if_clean'] if not confirmed else report['decision']['next_if_blocked']}")


if __name__ == "__main__":
    main()
