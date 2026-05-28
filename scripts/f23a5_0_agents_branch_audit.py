from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(".").resolve()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

OUT_JSON = ROOT / "docs" / "runtime" / f"OBSIDIA_F23A5_0_AGENTS_BRANCH_AUDIT_{TS}.json"
OUT_MD = ROOT / "docs" / "runtime" / f"OBSIDIA_F23A5_0_AGENTS_BRANCH_AUDIT_{TS}.md"

SCAN_ROOTS = [
    "periphery",
    "sigma",
    "apps/obsidia_api",
]

EXCLUDE_PARTS = {
    "__pycache__",
    ".pytest_cache",
    ".git",
    ".venv",
    "node_modules",
}

BOUNDARY_TOKENS = [
    "KX108_ONLY",
    "decision_authority",
    "readonly",
    "emits_act",
    "kernel_mutation",
    "x108_mutation",
    "memory_write",
    "graphiti_write",
    "neo4j_write",
]

DANGER_TOKENS = [
    "git commit",
    "git push",
    "subprocess.run",
    "os.system",
    "requests.post",
    "MERGE ",
    "CREATE ",
    "DELETE ",
    "SET ",
    "emits_act=True",
    "can_emit_act=True",
    "kernel_mutation=True",
    "x108_mutation=True",
]

AGENT_HINTS = [
    "agent",
    "Agent",
    "operator",
    "Operator",
    "orchestrator",
    "Orchestrator",
    "bridge",
    "Bridge",
]


def git(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, text=True, encoding="utf-8", errors="replace").strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def should_scan(path: Path) -> bool:
    if path.suffix != ".py":
        return False
    parts = set(path.parts)
    if parts & EXCLUDE_PARTS:
        return False
    text_name = str(path).replace("\\", "/")
    return any(root in text_name for root in SCAN_ROOTS) and any(h in path.name or h in text_name for h in AGENT_HINTS)


def extract_python_symbols(text: str) -> dict:
    try:
        tree = ast.parse(text)
    except Exception as exc:
        return {
            "parse_ok": False,
            "parse_error": str(exc),
            "classes": [],
            "functions": [],
        }

    classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    functions = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]

    return {
        "parse_ok": True,
        "parse_error": None,
        "classes": classes,
        "functions": functions,
    }


def classify_file(path: Path, text: str, symbols: dict) -> dict:
    boundary_hits = sorted({tok for tok in BOUNDARY_TOKENS if tok in text})
    danger_hits = sorted({tok for tok in DANGER_TOKENS if tok in text})

    lower = text.lower()
    role = "UNKNOWN"

    if "build_" in text and "_agents" in text:
        role = "SIGMA_DOMAIN_AGENT_BUILDER"
    elif "orchestrator" in lower:
        role = "ORCHESTRATOR"
    elif "operator" in lower:
        role = "OPERATOR"
    elif "bridge" in lower:
        role = "BRIDGE"
    elif "registry" in lower:
        role = "REGISTRY"
    elif "agent" in lower:
        role = "AGENT"
    elif "adapter" in lower:
        role = "ADAPTER"

    sovereign_risk = False
    risk_reasons = []

    for token in danger_hits:
        if token in {"git commit", "git push", "os.system", "subprocess.run", "MERGE ", "CREATE ", "DELETE ", "SET "}:
            sovereign_risk = True
            risk_reasons.append(f"DANGER_TOKEN:{token}")

    if "can_emit_act=True" in text or "emits_act=True" in text:
        sovereign_risk = True
        risk_reasons.append("ACT_EMISSION_FLAG_TRUE")

    if "kernel_mutation=True" in text or "x108_mutation=True" in text:
        sovereign_risk = True
        risk_reasons.append("MUTATION_FLAG_TRUE")

    boundary_score = len(boundary_hits)
    if boundary_score == 0:
        risk_reasons.append("NO_BOUNDARY_TOKEN_VISIBLE")

    return {
        "path": str(path).replace("\\", "/"),
        "role": role,
        "parse_ok": symbols["parse_ok"],
        "classes": symbols["classes"][:30],
        "functions": symbols["functions"][:40],
        "boundary_hits": boundary_hits,
        "danger_hits": danger_hits,
        "sovereign_risk": sovereign_risk,
        "risk_reasons": risk_reasons,
    }


def main():
    files = []
    for root in SCAN_ROOTS:
        root_path = ROOT / root
        if root_path.exists():
            files.extend([p for p in root_path.rglob("*.py") if should_scan(p)])

    files = sorted(set(files), key=lambda p: str(p).lower())

    records = []
    for path in files:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        symbols = extract_python_symbols(text)
        records.append(classify_file(path, text, symbols))

    high_risk = [r for r in records if r["sovereign_risk"]]
    no_boundary = [r for r in records if not r["boundary_hits"]]

    role_counts = {}
    for r in records:
        role_counts[r["role"]] = role_counts.get(r["role"], 0) + 1

    report = {
        "report_id": f"OBSIDIA_F23A5_0_AGENTS_BRANCH_AUDIT_{TS}",
        "phase": "F23A5.0",
        "mode": "AUDIT_ONLY_NO_PATCH",
        "commit": False,
        "tag": False,
        "freeze": False,
        "head": git(["git", "rev-parse", "--short", "HEAD"]),
        "tag_context": git(["git", "tag", "--points-at", "HEAD"]),
        "scanned_file_count": len(records),
        "role_counts": role_counts,
        "high_risk_count": len(high_risk),
        "no_boundary_token_count": len(no_boundary),
        "boundary_expected": {
            "decision_authority": "KX108_ONLY",
            "readonly": True,
            "emits_act": False,
            "kernel_mutation": False,
            "x108_mutation": False,
        },
        "records": records,
        "high_risk_records": high_risk,
        "no_boundary_records": no_boundary[:50],
        "locked_decisions": [
            "No agent may emit ACT.",
            "No agent may mutate kernel or X108.",
            "Agents are analysis/context/projection only.",
            "Decision authority remains KX108_ONLY.",
            "F23A5.0 does not patch runtime files.",
        ],
        "next_recommended": "F23A5.1_AGENTS_VALIDATION",
        "status": "F23A5_0_AGENTS_BRANCH_AUDIT_DONE",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("# OBSIDIA F23A5.0 — AGENTS BRANCH AUDIT")
    lines.append("")
    lines.append("Mode: AUDIT_ONLY_NO_PATCH")
    lines.append("Commit: NO")
    lines.append("Tag: NO")
    lines.append("Freeze: NO")
    lines.append("")
    lines.append(f"HEAD: `{report['head']}`")
    lines.append(f"Tags on HEAD: `{report['tag_context'] or 'NONE'}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Scanned files: {len(records)}")
    lines.append(f"- High-risk records: {len(high_risk)}")
    lines.append(f"- No-boundary-token records: {len(no_boundary)}")
    lines.append("")
    lines.append("## Role counts")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(role_counts, indent=2, ensure_ascii=False))
    lines.append("```")
    lines.append("")
    lines.append("## Boundary expected")
    lines.append("")
    lines.append("```text")
    lines.append("DECISION_AUTHORITY=KX108_ONLY")
    lines.append("readonly=true")
    lines.append("emits_act=false")
    lines.append("kernel_mutation=false")
    lines.append("x108_mutation=false")
    lines.append("```")
    lines.append("")
    lines.append("## High-risk records")
    lines.append("")
    if high_risk:
        for r in high_risk:
            lines.append(f"- `{r['path']}` — {', '.join(r['risk_reasons'])}")
    else:
        lines.append("- None detected by static scan.")
    lines.append("")
    lines.append("## Files without visible boundary tokens")
    lines.append("")
    for r in no_boundary[:50]:
        lines.append(f"- `{r['path']}` — role={r['role']}")
    if len(no_boundary) > 50:
        lines.append(f"- ... truncated {len(no_boundary) - 50} more")
    lines.append("")
    lines.append("## Next")
    lines.append("")
    lines.append("F23A5.1_AGENTS_VALIDATION")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append("F23A5_0_AGENTS_BRANCH_AUDIT_DONE")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("F23A5_0_AGENTS_BRANCH_AUDIT_DONE")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    print(f"SCANNED={len(records)}")
    print(f"HIGH_RISK={len(high_risk)}")
    print(f"NO_BOUNDARY={len(no_boundary)}")
    print(f"NEXT={report['next_recommended']}")


if __name__ == "__main__":
    main()
