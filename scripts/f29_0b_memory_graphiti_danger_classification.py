from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(".").resolve()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

OUT_JSON = ROOT / "docs" / "runtime" / f"OBSIDIA_F29_0B_MEMORY_GRAPHITI_DANGER_CLASSIFICATION_{TS}.json"
OUT_MD = ROOT / "docs" / "runtime" / f"OBSIDIA_F29_0B_MEMORY_GRAPHITI_DANGER_CLASSIFICATION_{TS}.md"

DANGER_TOKENS = [
    "write_transaction",
    "execute_write",
    "session.write_transaction",
    "CREATE ",
    "MERGE ",
    "DELETE ",
    "SET ",
    "memory_write=True",
    "graphiti_write=True",
    "neo4j_write=True",
    "kernel_mutation=True",
    "x108_mutation=True",
    "emits_act=True",
    "runtime_execute=True",
]


def git(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, text=True, encoding="utf-8", errors="replace").strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def latest_f29_0() -> Path:
    files = sorted(
        (ROOT / "docs" / "runtime").glob("OBSIDIA_F29_0_MEMORY_GRAPHITI_RECONCILIATION_AUDIT_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not files:
        raise SystemExit("F29_0_REPORT_NOT_FOUND")
    return files[0]


def context_for(path: Path, line_number: int) -> dict:
    if not path.exists():
        return {
            "exists": False,
            "context_before": [],
            "context_after": [],
            "line": "",
        }

    lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    idx = max(0, line_number - 1)

    return {
        "exists": True,
        "line": lines[idx].strip() if idx < len(lines) else "",
        "context_before": [l.strip() for l in lines[max(0, idx - 12):idx]],
        "context_after": [l.strip() for l in lines[idx + 1:idx + 13]],
    }


def classify(path_rel: str, token: str, line: str, before: list[str], after: list[str]) -> dict:
    low_path = path_rel.lower()
    joined = "\n".join(before + [line] + after).lower()

    manual_indicators = [
        "manual",
        "guarded",
        "review_decision",
        "apply_from_review",
        "operator",
        "human",
    ]

    readonly_indicators = [
        "readonly",
        "kx108_only",
        "memory_write",
        "graphiti_write",
        "neo4j_write",
        "candidate_only",
        "allowed_to_decide",
    ]

    # Cypher keywords inside literal strings or generated query blocks.
    if token.strip() in {"CREATE", "MERGE", "DELETE", "SET"} or token in {"CREATE ", "MERGE ", "DELETE ", "SET "}:
        if any(x in low_path for x in manual_indicators) or any(x in joined for x in manual_indicators):
            return {
                "classification": "MANUAL_GUARDED_WRITE_SURFACE_PRESENT",
                "confirmed_runtime_violation": False,
                "confirmed_write_capability": True,
                "reason": "A write-capable Cypher/manual apply surface exists, but it appears scoped to guarded/manual review flow rather than automatic runtime.",
            }

        return {
            "classification": "GRAPH_WRITE_SURFACE_REVIEW_REQUIRED",
            "confirmed_runtime_violation": True,
            "confirmed_write_capability": True,
            "reason": "Graph write token appears without enough manual/guarded context.",
        }

    if "true" in line and any(t in token for t in ["memory_write", "graphiti_write", "neo4j_write", "kernel_mutation", "x108_mutation", "emits_act", "runtime_execute"]):
        return {
            "classification": "BOUNDARY_TRUE_FLAG_REVIEW_REQUIRED",
            "confirmed_runtime_violation": True,
            "confirmed_write_capability": True,
            "reason": "A boundary-critical flag appears true.",
        }

    if any(x in joined for x in readonly_indicators):
        return {
            "classification": "READONLY_BOUNDARY_REFERENCE",
            "confirmed_runtime_violation": False,
            "confirmed_write_capability": False,
            "reason": "Danger token appears near readonly/boundary metadata rather than a confirmed runtime write path.",
        }

    return {
        "classification": "REVIEW_REQUIRED",
        "confirmed_runtime_violation": False,
        "confirmed_write_capability": False,
        "reason": "Could not prove runtime violation from local context alone.",
    }


def main():
    f29_path = latest_f29_0()
    f29 = json.loads(f29_path.read_text(encoding="utf-8"))

    raw_records = f29.get("danger_records", [])
    classified = []

    for record in raw_records:
        path_rel = record.get("path", "")
        repo_path = ROOT / path_rel

        for hit in record.get("danger_hits", []):
            token = hit.get("token", "")
            line_number = int(hit.get("line", 0) or 0)

            ctx = context_for(repo_path, line_number)
            c = classify(
                path_rel=path_rel,
                token=token,
                line=ctx["line"] or hit.get("text", ""),
                before=ctx["context_before"],
                after=ctx["context_after"],
            )

            classified.append({
                "path": path_rel,
                "line_number": line_number,
                "token": token,
                "line": ctx["line"] or hit.get("text", ""),
                "exists": ctx["exists"],
                **c,
            })

    confirmed_runtime = [x for x in classified if x["confirmed_runtime_violation"]]
    write_capable = [x for x in classified if x["confirmed_write_capability"]]

    if confirmed_runtime:
        next_step = "F29.1_QUARANTINE_OR_GUARD_GRAPHITI_WRITE_SURFACES"
        gate = "BLOCK_PATCH_UNTIL_REVIEW"
    elif write_capable:
        next_step = "F29.1_DOCUMENT_MANUAL_WRITE_SURFACES_AND_NO_RUNTIME_BINDING"
        gate = "ALLOW_NO_RUNTIME_PATCH_WITH_REVIEW_NOTE"
    else:
        next_step = "F29.1_CHECKPOINT_AUDIT_ONLY"
        gate = "ALLOW_CHECKPOINT"

    report = {
        "report_id": f"OBSIDIA_F29_0B_MEMORY_GRAPHITI_DANGER_CLASSIFICATION_{TS}",
        "phase": "F29.0B",
        "mode": "DANGER_CLASSIFICATION_ONLY_NO_PATCH",
        "commit": False,
        "tag": False,
        "freeze": False,
        "head": git(["git", "rev-parse", "--short", "HEAD"]),
        "tag_context": git(["git", "tag", "--points-at", "HEAD"]),
        "source_f29_0_report": str(f29_path),
        "raw_danger_record_count": len(raw_records),
        "classified_hit_count": len(classified),
        "confirmed_runtime_violation_count": len(confirmed_runtime),
        "write_capability_present_count": len(write_capable),
        "gate": gate,
        "classified_hits": classified,
        "boundary_expected": {
            "decision_authority": "KX108_ONLY",
            "readonly": True,
            "memory_write": False,
            "graphiti_write": False,
            "neo4j_write": False,
            "emits_act": False,
            "runtime_execute": False,
            "kernel_mutation": False,
            "x108_mutation": False,
        },
        "locked_decisions": [
            "F29.0B is classification-only.",
            "No runtime patch.",
            "No Graphiti/Neo4j write.",
            "No memory write.",
            "Manual guarded write surfaces must not be bound to runtime.",
            "Graphiti/memory remain readonly context sidecars.",
            "Decision authority remains KX108_ONLY.",
        ],
        "next_recommended": next_step,
        "status": "F29_0B_MEMORY_GRAPHITI_DANGER_CLASSIFICATION_DONE",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("# OBSIDIA F29.0B — MEMORY / GRAPHITI DANGER CLASSIFICATION")
    lines.append("")
    lines.append("Mode: DANGER_CLASSIFICATION_ONLY_NO_PATCH")
    lines.append("Commit: NO")
    lines.append("Tag: NO")
    lines.append("Freeze: NO")
    lines.append("")
    lines.append(f"HEAD: `{report['head']}`")
    lines.append(f"Source F29.0 report: `{f29_path}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Raw danger records: {len(raw_records)}")
    lines.append(f"- Classified hits: {len(classified)}")
    lines.append(f"- Confirmed runtime violations: {len(confirmed_runtime)}")
    lines.append(f"- Write-capable manual surfaces: {len(write_capable)}")
    lines.append(f"- Gate: `{gate}`")
    lines.append("")
    lines.append("## Classified hits")
    lines.append("")
    for item in classified:
        lines.append(f"- `{item['path']}` L{item['line_number']} `{item['token']}`")
        lines.append(f"  - classification: `{item['classification']}`")
        lines.append(f"  - confirmed_runtime_violation: {item['confirmed_runtime_violation']}")
        lines.append(f"  - confirmed_write_capability: {item['confirmed_write_capability']}")
        lines.append(f"  - reason: {item['reason']}")
        lines.append(f"  - line: `{item['line']}`")
    lines.append("")
    lines.append("## Next")
    lines.append("")
    lines.append(next_step)
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append("```text")
    lines.append("DECISION_AUTHORITY=KX108_ONLY")
    lines.append("readonly=true")
    lines.append("memory_write=false")
    lines.append("graphiti_write=false")
    lines.append("neo4j_write=false")
    lines.append("emits_act=false")
    lines.append("runtime_execute=false")
    lines.append("kernel_mutation=false")
    lines.append("x108_mutation=false")
    lines.append("```")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append("F29_0B_MEMORY_GRAPHITI_DANGER_CLASSIFICATION_DONE")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("F29_0B_MEMORY_GRAPHITI_DANGER_CLASSIFICATION_DONE")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    print(f"RAW_DANGER_RECORDS={len(raw_records)}")
    print(f"CLASSIFIED_HITS={len(classified)}")
    print(f"CONFIRMED_RUNTIME_VIOLATIONS={len(confirmed_runtime)}")
    print(f"WRITE_CAPABILITY_PRESENT={len(write_capable)}")
    print(f"GATE={gate}")
    print(f"NEXT={next_step}")


if __name__ == "__main__":
    main()
