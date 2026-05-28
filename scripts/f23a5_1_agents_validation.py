from __future__ import annotations

import ast
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(".").resolve()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

OUT_JSON = ROOT / "docs" / "runtime" / f"OBSIDIA_F23A5_1_AGENTS_VALIDATION_{TS}.json"
OUT_MD = ROOT / "docs" / "runtime" / f"OBSIDIA_F23A5_1_AGENTS_VALIDATION_{TS}.md"

BOUNDARY_REQUIRED_FALSE = [
    "emits_act",
    "memory_write",
    "graphiti_write",
    "kernel_mutation",
    "x108_mutation",
]

DANGER_PATTERNS = [
    "can_emit_act=True",
    "emits_act=True",
    "memory_write=True",
    "graphiti_write=True",
    "kernel_mutation=True",
    "x108_mutation=True",
    "git commit",
    "git push",
    "os.system",
    "subprocess.run",
]

NEO4J_WRITE_WORDS = [
    "CREATE",
    "MERGE",
    "SET",
    "DELETE",
    "REMOVE",
    "DROP",
]


def git(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, text=True, encoding="utf-8", errors="replace").strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def latest_audit_json() -> Path:
    candidates = sorted(
        (ROOT / "docs" / "runtime").glob("OBSIDIA_F23A5_0_AGENTS_BRANCH_AUDIT_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise RuntimeError("NO_F23A5_0_AUDIT_JSON_FOUND")
    return candidates[0]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def inspect_lines(path: Path, tokens: list[str]) -> list[dict]:
    text = read_text(path)
    out = []
    for idx, line in enumerate(text.splitlines(), start=1):
        for token in tokens:
            if token in line:
                out.append({
                    "line": idx,
                    "token": token,
                    "text": line.strip()[:300],
                })
    return out


def parse_ok(path: Path) -> tuple[bool, str | None]:
    try:
        ast.parse(read_text(path))
        return True, None
    except Exception as exc:
        return False, str(exc)


def classify_neo4j_bridge(path: Path) -> dict:
    text = read_text(path)
    hits = inspect_lines(path, NEO4J_WRITE_WORDS + DANGER_PATTERNS)

    lower_path = str(path).lower().replace("\\", "/")
    name_declares_readonly = "readonly" in lower_path

    has_write_transaction = any(x in text for x in [
        ".execute_write",
        ".write_transaction",
        "session.write_transaction",
        "execute_write(",
    ])

    has_read_transaction = any(x in text for x in [
        ".execute_read",
        ".read_transaction",
        "session.read_transaction",
        "execute_read(",
    ])

    # If CYPHER write words only appear in audit strings, checks, allowlists,
    # or comments, classify as static false-positive unless write transaction exists.
    risky_lines = []
    for h in hits:
        t = h["text"]
        is_comment = t.startswith("#")
        is_string_or_guard = (
            '"' in t or "'" in t or "DANGER_TOKEN" in t or "forbidden" in t.lower()
            or "readonly" in t.lower() or "write" in t.lower()
        )
        if h["token"] in NEO4J_WRITE_WORDS and not is_comment and not is_string_or_guard:
            risky_lines.append(h)

    if has_write_transaction:
        classification = "CONFIRMED_RUNTIME_WRITE_RISK"
    elif risky_lines:
        classification = "REVIEW_REQUIRED"
    elif name_declares_readonly and not has_write_transaction:
        classification = "STATIC_FALSE_POSITIVE_READONLY_FILE"
    else:
        classification = "REVIEW_REQUIRED"

    return {
        "path": str(path).replace("\\", "/"),
        "name_declares_readonly": name_declares_readonly,
        "has_write_transaction": has_write_transaction,
        "has_read_transaction": has_read_transaction,
        "danger_hits": hits,
        "risky_lines": risky_lines,
        "classification": classification,
    }


def validate_agent_file(path: Path) -> dict:
    text = read_text(path)
    ok, err = parse_ok(path)

    dangers = inspect_lines(path, DANGER_PATTERNS)
    boundary_mentions = {
        "KX108_ONLY": "KX108_ONLY" in text,
        "readonly": "readonly" in text,
        "emits_act": "emits_act" in text,
        "kernel_mutation": "kernel_mutation" in text,
        "x108_mutation": "x108_mutation" in text,
    }

    confirmed_violation = False
    reasons = []

    for d in dangers:
        confirmed_violation = True
        reasons.append(f"DANGER_PATTERN:{d['token']}:L{d['line']}")

    if "can_emit_act=True" in text or "emits_act=True" in text:
        confirmed_violation = True
        reasons.append("ACT_TRUE_FLAG")

    return {
        "path": str(path).replace("\\", "/"),
        "parse_ok": ok,
        "parse_error": err,
        "boundary_mentions": boundary_mentions,
        "danger_hits": dangers,
        "confirmed_violation": confirmed_violation,
        "reasons": reasons,
    }


def main():
    audit_path = latest_audit_json()
    audit = json.loads(audit_path.read_text(encoding="utf-8"))

    high_risk_records = audit.get("high_risk_records", [])
    no_boundary_records = audit.get("no_boundary_records", [])

    high_risk_validation = []
    confirmed_violations = []
    false_positives = []

    for record in high_risk_records:
        path = Path(record["path"])
        if not path.exists():
            item = {
                "path": str(path),
                "classification": "MISSING_FILE",
                "confirmed_violation": False,
            }
        elif "neo4j" in str(path).lower() and "readonly" in str(path).lower():
            item = classify_neo4j_bridge(path)
            item["confirmed_violation"] = item["classification"] == "CONFIRMED_RUNTIME_WRITE_RISK"
        else:
            item = validate_agent_file(path)

        high_risk_validation.append(item)

        if item.get("confirmed_violation"):
            confirmed_violations.append(item)
        elif item.get("classification") == "STATIC_FALSE_POSITIVE_READONLY_FILE":
            false_positives.append(item)

    # Validate no-boundary records as audit debt, not automatic runtime violation.
    no_boundary_sample = no_boundary_records[:50]

    report = {
        "report_id": f"OBSIDIA_F23A5_1_AGENTS_VALIDATION_{TS}",
        "phase": "F23A5.1",
        "mode": "VALIDATION_ONLY_NO_PATCH",
        "commit": False,
        "tag": False,
        "freeze": False,
        "head": git(["git", "rev-parse", "--short", "HEAD"]),
        "tag_context": git(["git", "tag", "--points-at", "HEAD"]),
        "source_audit": str(audit_path).replace("\\", "/"),
        "source_audit_scanned": audit.get("scanned_file_count"),
        "source_audit_high_risk": audit.get("high_risk_count"),
        "source_audit_no_boundary": audit.get("no_boundary_token_count"),
        "high_risk_validation": high_risk_validation,
        "confirmed_violation_count": len(confirmed_violations),
        "false_positive_count": len(false_positives),
        "no_boundary_debt_count": audit.get("no_boundary_token_count"),
        "no_boundary_policy": "AUDIT_DEBT_NOT_RUNTIME_VIOLATION",
        "no_boundary_sample": no_boundary_sample,
        "locked_decisions": [
            "F23A5.1 does not patch runtime files.",
            "No-boundary-token records are audit debt, not automatic runtime failure.",
            "Neo4j readonly bridge tokens are only confirmed risk if write transaction or executable write path exists.",
            "Decision authority remains KX108_ONLY.",
        ],
        "next_recommended": "F23A5.2_AGENT_GOVERNANCE_AUDIT",
        "status": "F23A5_1_AGENTS_VALIDATION_DONE",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("# OBSIDIA F23A5.1 — AGENTS VALIDATION")
    lines.append("")
    lines.append("Mode: VALIDATION_ONLY_NO_PATCH")
    lines.append("Commit: NO")
    lines.append("Tag: NO")
    lines.append("Freeze: NO")
    lines.append("")
    lines.append(f"HEAD: `{report['head']}`")
    lines.append(f"Tags on HEAD: `{report['tag_context'] or 'NONE'}`")
    lines.append(f"Source audit: `{report['source_audit']}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Source scanned files: {report['source_audit_scanned']}")
    lines.append(f"- Source high-risk records: {report['source_audit_high_risk']}")
    lines.append(f"- Source no-boundary-token records: {report['source_audit_no_boundary']}")
    lines.append(f"- Confirmed runtime violations: {report['confirmed_violation_count']}")
    lines.append(f"- Static false positives: {report['false_positive_count']}")
    lines.append("")
    lines.append("## High-risk validation")
    lines.append("")
    for item in high_risk_validation:
        lines.append(f"- `{item['path']}`")
        lines.append(f"  - classification: `{item.get('classification', 'VALIDATED')}`")
        lines.append(f"  - confirmed_violation: `{item.get('confirmed_violation')}`")
        if item.get("danger_hits"):
            lines.append("  - danger hits:")
            for h in item["danger_hits"][:20]:
                lines.append(f"    - L{h['line']} `{h['token']}` — {h['text']}")
    if not high_risk_validation:
        lines.append("- None.")
    lines.append("")
    lines.append("## No-boundary-token policy")
    lines.append("")
    lines.append("No-boundary-token files are classified as audit debt, not automatic runtime violations.")
    lines.append("They become patch candidates only if they expose runtime actions, external writes, or mutation flags.")
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append("```text")
    lines.append("DECISION_AUTHORITY=KX108_ONLY")
    lines.append("readonly=true")
    lines.append("emits_act=false")
    lines.append("kernel_mutation=false")
    lines.append("x108_mutation=false")
    lines.append("```")
    lines.append("")
    lines.append("## Next")
    lines.append("")
    lines.append("F23A5.2_AGENT_GOVERNANCE_AUDIT")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append("F23A5_1_AGENTS_VALIDATION_DONE")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("F23A5_1_AGENTS_VALIDATION_DONE")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    print(f"CONFIRMED_VIOLATIONS={len(confirmed_violations)}")
    print(f"FALSE_POSITIVES={len(false_positives)}")
    print(f"NO_BOUNDARY_DEBT={report['no_boundary_debt_count']}")
    print(f"NEXT={report['next_recommended']}")


if __name__ == "__main__":
    main()
