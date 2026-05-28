from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(".").resolve()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

OUT_JSON = ROOT / "docs" / "runtime" / f"OBSIDIA_F23A5_2_AGENT_GOVERNANCE_AUDIT_{TS}.json"
OUT_MD = ROOT / "docs" / "runtime" / f"OBSIDIA_F23A5_2_AGENT_GOVERNANCE_AUDIT_{TS}.md"

GOVERNANCE_RULES = [
    {
        "id": "AGENT_GOV_01",
        "rule": "Agents are non-sovereign.",
        "required": "No agent may decide ACT/BLOCK/HOLD as runtime authority.",
        "authority": "KX108_ONLY",
    },
    {
        "id": "AGENT_GOV_02",
        "rule": "Agents may emit analysis, signals, risk flags, unknowns, evidence refs.",
        "required": "Signals remain advisory/context only.",
        "authority": "KX108_ONLY",
    },
    {
        "id": "AGENT_GOV_03",
        "rule": "Agents may not mutate kernel or X108.",
        "required": "kernel_mutation=false and x108_mutation=false.",
        "authority": "KX108_ONLY",
    },
    {
        "id": "AGENT_GOV_04",
        "rule": "Memory/Graphiti/Neo4j writes are not allowed from readonly agents.",
        "required": "memory_write=false, graphiti_write=false, neo4j_write=false unless a future explicit write-mode palier exists.",
        "authority": "KX108_ONLY",
    },
    {
        "id": "AGENT_GOV_05",
        "rule": "No-boundary-token files are audit debt, not runtime failure.",
        "required": "Patch only if runtime exposure or mutation path is confirmed.",
        "authority": "AUDIT_POLICY",
    },
    {
        "id": "AGENT_GOV_06",
        "rule": "Neo4j readonly bridge with CREATE/MERGE/SET remains review-required.",
        "required": "Do not patch until executable write path is confirmed or bridge is activated in runtime.",
        "authority": "AUDIT_POLICY",
    },
]


def git(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, text=True, encoding="utf-8", errors="replace").strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def latest(pattern: str) -> Path:
    files = sorted((ROOT / "docs" / "runtime").glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise RuntimeError(f"MISSING_REPORT:{pattern}")
    return files[0]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    f23a5_0 = latest("OBSIDIA_F23A5_0_AGENTS_BRANCH_AUDIT_*.json")
    f23a5_1 = latest("OBSIDIA_F23A5_1_AGENTS_VALIDATION_*.json")

    audit0 = load_json(f23a5_0)
    audit1 = load_json(f23a5_1)

    confirmed = int(audit1.get("confirmed_violation_count", 0))
    high_risk = int(audit0.get("high_risk_count", 0))
    no_boundary = int(audit0.get("no_boundary_token_count", 0))

    governance_status = "PASS_WITH_AUDIT_DEBT" if confirmed == 0 else "BLOCKED_CONFIRMED_VIOLATION"

    open_debts = []
    if no_boundary:
        open_debts.append({
            "id": "DEBT_BOUNDARY_TOKENS",
            "count": no_boundary,
            "status": "OPEN_AUDIT_DEBT",
            "patch_now": False,
            "reason": "No-boundary-token files are not confirmed runtime violations.",
        })

    if high_risk:
        open_debts.append({
            "id": "DEBT_NEO4J_READONLY_REVIEW",
            "count": high_risk,
            "status": "REVIEW_REQUIRED",
            "patch_now": False,
            "reason": "No confirmed runtime write violation in F23A5.1.",
        })

    report = {
        "report_id": f"OBSIDIA_F23A5_2_AGENT_GOVERNANCE_AUDIT_{TS}",
        "phase": "F23A5.2",
        "mode": "GOVERNANCE_AUDIT_NO_RUNTIME_PATCH",
        "commit": False,
        "tag": False,
        "freeze": False,
        "head": git(["git", "rev-parse", "--short", "HEAD"]),
        "tag_context": git(["git", "tag", "--points-at", "HEAD"]),
        "source_reports": {
            "f23a5_0": str(f23a5_0).replace("\\", "/"),
            "f23a5_1": str(f23a5_1).replace("\\", "/"),
        },
        "inputs": {
            "scanned_files": audit0.get("scanned_file_count"),
            "high_risk_records": high_risk,
            "confirmed_violations": confirmed,
            "no_boundary_debt": no_boundary,
        },
        "governance_status": governance_status,
        "governance_rules": GOVERNANCE_RULES,
        "open_debts": open_debts,
        "locked_decisions": [
            "No runtime patch in F23A5.2.",
            "No agent governance violation confirmed.",
            "No-boundary-token files remain audit debt.",
            "Neo4j readonly bridge remains review-required, not patched.",
            "Decision authority remains KX108_ONLY.",
        ],
        "next_recommended": "F23A5.3_F23A5_BLOCK_CHECKPOINT",
        "status": "F23A5_2_AGENT_GOVERNANCE_AUDIT_DONE",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("# OBSIDIA F23A5.2 — AGENT GOVERNANCE AUDIT")
    lines.append("")
    lines.append("Mode: GOVERNANCE_AUDIT_NO_RUNTIME_PATCH")
    lines.append("Commit: NO")
    lines.append("Tag: NO")
    lines.append("Freeze: NO")
    lines.append("")
    lines.append(f"HEAD: `{report['head']}`")
    lines.append(f"Tags on HEAD: `{report['tag_context'] or 'NONE'}`")
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append(f"- F23A5.0 source: `{report['source_reports']['f23a5_0']}`")
    lines.append(f"- F23A5.1 source: `{report['source_reports']['f23a5_1']}`")
    lines.append(f"- Scanned files: {audit0.get('scanned_file_count')}")
    lines.append(f"- High-risk records: {high_risk}")
    lines.append(f"- Confirmed violations: {confirmed}")
    lines.append(f"- No-boundary debt: {no_boundary}")
    lines.append("")
    lines.append("## Governance status")
    lines.append("")
    lines.append(f"`{governance_status}`")
    lines.append("")
    lines.append("## Governance rules")
    lines.append("")
    for rule in GOVERNANCE_RULES:
        lines.append(f"### {rule['id']}")
        lines.append(f"- Rule: {rule['rule']}")
        lines.append(f"- Required: {rule['required']}")
        lines.append(f"- Authority: {rule['authority']}")
        lines.append("")
    lines.append("## Open debts")
    lines.append("")
    if open_debts:
        for debt in open_debts:
            lines.append(f"- `{debt['id']}` — count={debt['count']} — status={debt['status']} — patch_now={debt['patch_now']}")
            lines.append(f"  - Reason: {debt['reason']}")
    else:
        lines.append("- None.")
    lines.append("")
    lines.append("## Locked decisions")
    lines.append("")
    for d in report["locked_decisions"]:
        lines.append(f"- {d}")
    lines.append("")
    lines.append("## Next")
    lines.append("")
    lines.append("F23A5.3_F23A5_BLOCK_CHECKPOINT")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append("F23A5_2_AGENT_GOVERNANCE_AUDIT_DONE")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("F23A5_2_AGENT_GOVERNANCE_AUDIT_DONE")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    print(f"GOVERNANCE_STATUS={governance_status}")
    print(f"CONFIRMED_VIOLATIONS={confirmed}")
    print(f"OPEN_DEBTS={len(open_debts)}")
    print("NEXT=F23A5.3_F23A5_BLOCK_CHECKPOINT")


if __name__ == "__main__":
    main()
