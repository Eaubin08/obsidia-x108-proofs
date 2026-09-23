from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(".").resolve()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

OUT_JSON = ROOT / "docs" / "runtime" / f"OBSIDIA_F31_0_CLEANUP_UNTRACKED_DEBT_INVENTORY_{TS}.json"
OUT_MD = ROOT / "docs" / "runtime" / f"OBSIDIA_F31_0_CLEANUP_UNTRACKED_DEBT_INVENTORY_{TS}.md"


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True, encoding="utf-8", errors="replace").strip()


def git_or_error(cmd: list[str]) -> str:
    try:
        return run(cmd)
    except Exception as exc:
        return f"ERROR: {exc}"


def classify(path: str) -> dict:
    p = path.replace("\\", "/")
    name = Path(p).name

    category = "D_NEEDS_HUMAN_REVIEW"
    action = "REVIEW"
    reason = "No rule matched."

    # Keep external audit from Claude if present.
    if "CLAUDE_FAST_AUDIT" in p:
        category = "A_KEEP_LATER_RUNTIME_EVIDENCE"
        action = "KEEP_OR_COMMIT_IF_USEFUL"
        reason = "External audit evidence from Claude Code."
        return {"path": p, "category": category, "action": action, "reason": reason}

    # Backup files.
    if ".bak" in p or name.endswith(".bak") or "_bak_" in p or ".bak_" in p:
        category = "C_BACKUP_BAK_CAN_IGNORE"
        action = "IGNORE_OR_DELETE_AFTER_CONFIRMATION"
        reason = "Backup artifact; not needed in runtime commit."
        return {"path": p, "category": category, "action": action, "reason": reason}

    # Old F23/F23A4/F23A6 reports and scripts: likely superseded by pushed paliers.
    old_markers = [
        "F23A4_3_SIGMA_REGISTRY_REPAIR",
        "OBSIDIA_F23A4_2_TO_F23A6_2_NIGHT_AUDIT",
        "OBSIDIA_F23_META_AUDIT_RESUME_CHAIN",
        "F23A6_BLOCK_CHECKPOINT",
        "f23_meta_audit_resume_chain",
        "f23a4_2_to_f23a6_2_night_audit",
    ]
    if any(m in p for m in old_markers):
        category = "B_ALREADY_COMMITTED_DUPLICATE_OR_OLD_REPORT"
        action = "ARCHIVE_OR_DELETE_AFTER_CONFIRMATION"
        reason = "Old F23/F23A runtime evidence; current paliers are already pushed."
        return {"path": p, "category": category, "action": action, "reason": reason}

    # Duplicate validation reports produced after commit or superseded.
    duplicate_markers = [
        "OBSIDIA_F29_2_NEO4J_MANUAL_GUARD_REAUDIT_20260529_005956",
        "OBSIDIA_F30_3_WORKFLOW_GOVERNANCE_IMPORT_COMPILE_VALIDATE_20260529_001013",
        "OBSIDIA_F30_3_WORKFLOW_GOVERNANCE_IMPORT_COMPILE_VALIDATE_20260529_002006",
    ]
    if any(m in p for m in duplicate_markers):
        category = "B_ALREADY_COMMITTED_DUPLICATE_OR_OLD_REPORT"
        action = "ARCHIVE_OR_DELETE_AFTER_CONFIRMATION"
        reason = "Duplicate/superseded validation report not included in selected palier commit."
        return {"path": p, "category": category, "action": action, "reason": reason}

    # Runtime docs that do not match known stale patterns.
    if p.startswith("docs/runtime/"):
        category = "D_NEEDS_HUMAN_REVIEW"
        action = "REVIEW_BEFORE_KEEP_OR_DELETE"
        reason = "Runtime evidence under docs/runtime but not matched by stale rules."
        return {"path": p, "category": category, "action": action, "reason": reason}

    return {"path": p, "category": category, "action": action, "reason": reason}


def main():
    status = git_or_error(["git", "status", "-sb"])
    log = git_or_error(["git", "log", "--oneline", "-10"])
    tags = git_or_error(["git", "tag", "--list", "BRODY_F2*"])

    raw = git_or_error(["git", "ls-files", "--others", "--exclude-standard"])
    untracked = [line.strip() for line in raw.splitlines() if line.strip()]

    records = [classify(p) for p in untracked]

    buckets = {}
    for r in records:
        buckets.setdefault(r["category"], []).append(r)

    report = {
        "report_id": f"OBSIDIA_F31_0_CLEANUP_UNTRACKED_DEBT_INVENTORY_{TS}",
        "phase": "F31.0",
        "mode": "INVENTORY_ONLY_NO_DELETE_NO_COMMIT",
        "commit": False,
        "tag": False,
        "delete": False,
        "head": git_or_error(["git", "rev-parse", "--short", "HEAD"]),
        "tag_context": git_or_error(["git", "tag", "--points-at", "HEAD"]),
        "status": status,
        "recent_log": log,
        "brody_tags": tags,
        "untracked_count": len(untracked),
        "bucket_counts": {k: len(v) for k, v in sorted(buckets.items())},
        "records": records,
        "locked_decisions": [
            "F31.0 is inventory-only.",
            "No deletion.",
            "No git clean.",
            "No commit.",
            "No tag.",
            "No runtime patch.",
            "Human review required before deletion or archival.",
        ],
        "next_recommended": "F31.1_CLEANUP_DECISION_APPLY_AFTER_HUMAN_REVIEW",
        "status_label": "F31_0_CLEANUP_UNTRACKED_DEBT_INVENTORY_DONE",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("# OBSIDIA F31.0 — CLEANUP UNTRACKED DEBT INVENTORY")
    lines.append("")
    lines.append("Mode: INVENTORY_ONLY_NO_DELETE_NO_COMMIT")
    lines.append("Commit: NO")
    lines.append("Tag: NO")
    lines.append("Delete: NO")
    lines.append("")
    lines.append(f"HEAD: `{report['head']}`")
    lines.append(f"Tags on HEAD: `{report['tag_context'] or 'NONE'}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Untracked files: {len(untracked)}")
    for cat in ["A_KEEP_LATER_RUNTIME_EVIDENCE", "B_ALREADY_COMMITTED_DUPLICATE_OR_OLD_REPORT", "C_BACKUP_BAK_CAN_IGNORE", "D_NEEDS_HUMAN_REVIEW"]:
        lines.append(f"- {cat}: {len(buckets.get(cat, []))}")
    lines.append("")
    lines.append("## Inventory")
    lines.append("")
    for cat in ["A_KEEP_LATER_RUNTIME_EVIDENCE", "B_ALREADY_COMMITTED_DUPLICATE_OR_OLD_REPORT", "C_BACKUP_BAK_CAN_IGNORE", "D_NEEDS_HUMAN_REVIEW"]:
        lines.append(f"### {cat}")
        lines.append("")
        items = buckets.get(cat, [])
        if not items:
            lines.append("- None.")
        else:
            for r in items:
                lines.append(f"- `{r['path']}`")
                lines.append(f"  - action: `{r['action']}`")
                lines.append(f"  - reason: {r['reason']}")
        lines.append("")
    lines.append("## Next")
    lines.append("")
    lines.append("F31.1_CLEANUP_DECISION_APPLY_AFTER_HUMAN_REVIEW")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append("F31_0_CLEANUP_UNTRACKED_DEBT_INVENTORY_DONE")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("F31_0_CLEANUP_UNTRACKED_DEBT_INVENTORY_DONE")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    print(f"UNTRACKED={len(untracked)}")
    for cat in ["A_KEEP_LATER_RUNTIME_EVIDENCE", "B_ALREADY_COMMITTED_DUPLICATE_OR_OLD_REPORT", "C_BACKUP_BAK_CAN_IGNORE", "D_NEEDS_HUMAN_REVIEW"]:
        print(f"{cat}={len(buckets.get(cat, []))}")
    print("NEXT=F31.1_CLEANUP_DECISION_APPLY_AFTER_HUMAN_REVIEW")


if __name__ == "__main__":
    main()
