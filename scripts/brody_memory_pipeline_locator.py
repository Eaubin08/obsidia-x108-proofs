#!/usr/bin/env python3
"""
Brody Memory Pipeline Locator
===============================
Scans _local_audits/ for existing BRODY_GRAPHITI_* pipeline artifacts.
Produces PIPELINE_LOCATOR_REPORT.json and .md.
Read-only — never executes any pipeline.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = REPO_ROOT / "_local_audits"
OUTPUT_DIR = AUDIT_DIR / "BRODY_PERSONAL_SIDECAR_TO_REAL_INTAKE_GATE_V1"

# ── Known pipeline markers ──────────────────────────────────────────────
_PIPELINE_KEYWORDS = [
    "BRODY_GRAPHITI",
    "brody_pipeline_hold",
    "controlled_write",
    "real_import",
    "GRAPHITI_IMPORT_DRY_RUN",
    "ROLLBACK_PLAN",
    "POST_WRITE_VALIDATION",
    "IMPORT_PLAN",
]

_EXPECTED_FILES = [
    "GRAPHITI_IMPORT_DRY_RUN_PLAN.jsonl",
    "ROLLBACK_PLAN.cypher",
    "POST_WRITE_VALIDATION.json",
    "REAL_IMPORT_WRITTEN_*.jsonl",
    "BRODY_GRAPHITI_REAL_IMPORT_CONTROLLED_WRITE_TEST_V1_*.json",
    "CURRENT_*.txt",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def locate_pipeline() -> dict[str, Any]:
    """
    Scan _local_audits/ recursively for pipeline artifacts.
    Returns a structured report.
    """
    result: dict[str, Any] = {
        "timestamp": _now(),
        "source": "brody_memory_pipeline_locator",
        "readonly": True,
        "dry_run": True,
        "pipeline_found": False,
        "historical_write_marker": None,
        "dry_run_review_gate": None,
        "controlled_write_runner": None,
        "post_write_validation": None,
        "rollback_plan": None,
        "artifacts": [],
        "expected_import_count": 0,
        "write_flags": {
            "memory_write": False,
            "graphiti_write": False,
            "neo4j_write": False,
            "memory_intake": False,
            "brody_execute_allowed": False,
            "brody_authorize_allowed": False,
            "decision_authority": "KX108_ONLY",
        },
        "blocked_flags": {
            "MEMORY_INTAKE": True,
            "BRODY_EXECUTE_ALLOWED": True,
            "BRODY_AUTHORIZE_ALLOWED": True,
        },
        "batch_id": None,
        "source_import_plan": None,
        "notes": [],
    }

    if not AUDIT_DIR.exists():
        result["notes"].append("_local_audits/ directory not found")
        return result

    audit_root = AUDIT_DIR.resolve()

    # Walk audit directory
    for root, dirs, files in os.walk(AUDIT_DIR):
        root_path = Path(root)
        for fname in files:
            fpath = root_path / fname
            try:
                rel = str(fpath.relative_to(REPO_ROOT))
            except ValueError:
                rel = str(fpath)
            artifact: dict[str, Any] = {
                "path": str(rel),
                "name": fname,
                "size": fpath.stat().st_size,
            }

            # Detect pipeline markers
            if "GRAPHITI_IMPORT_DRY_RUN_PLAN" in fname and fname.endswith(".jsonl"):
                artifact["type"] = "dry_run_review_gate_plan"
                result["dry_run_review_gate"] = str(rel)
                result["pipeline_found"] = True
                # Count lines as expected import count
                try:
                    lines = fpath.read_text(encoding="utf-8").strip().split("\n")
                    result["expected_import_count"] = len([l for l in lines if l.strip()])
                except Exception:
                    pass

            elif "ROLLBACK_PLAN" in fname and fname.endswith(".cypher"):
                artifact["type"] = "rollback_plan"
                result["rollback_plan"] = str(rel)
                result["pipeline_found"] = True

            elif "POST_WRITE_VALIDATION" in fname and fname.endswith(".json"):
                artifact["type"] = "post_write_validation"
                result["post_write_validation"] = str(rel)
                data = _safe_read_json(fpath)
                if data:
                    result["historical_write_marker"] = data.get("status", "FOUND")

            elif "REAL_IMPORT_WRITTEN" in fname:
                artifact["type"] = "real_import_written"
                result["controlled_write_runner"] = str(rel)
                result["pipeline_found"] = True

            elif "brody_pipeline_hold" in str(rel).lower():
                artifact["type"] = "pipeline_hold_stabilized"
                result["pipeline_found"] = True

            elif "CONTROLLED_WRITE" in fname.upper() or "controlled_write" in fname.lower():
                artifact["type"] = "controlled_write_marker"
                result["controlled_write_runner"] = str(rel)
                result["pipeline_found"] = True

            elif "CURRENT_" in fname and fname.endswith(".txt"):
                artifact["type"] = "current_state_pointer"
                try:
                    content = fpath.read_text(encoding="utf-8")[:500]
                    artifact["preview"] = content
                except Exception:
                    pass

            elif any(kw in fname.upper() for kw in _PIPELINE_KEYWORDS):
                artifact["type"] = "related_pipeline_artifact"
                result["pipeline_found"] = True

            else:
                artifact["type"] = "unclassified"

            result["artifacts"].append(artifact)

    # Determine batch_id from artifacts
    for a in result["artifacts"]:
        for kw in ["batch_id", "BATCH_"]:
            if kw in a.get("name", ""):
                result["batch_id"] = a["name"]
                break
        if result["batch_id"]:
            break

    if not result["pipeline_found"]:
        result["notes"].append(
            "No historical BRODY_GRAPHITI pipeline found. "
            "This is a first-time setup or the pipeline directory was cleaned."
        )

    return result


def write_reports(report: dict[str, Any]) -> tuple[Path, Path]:
    """Write JSON and Markdown reports."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = _now().replace(":", "-")[:19]
    json_path = OUTPUT_DIR / f"PIPELINE_LOCATOR_REPORT_{ts}.json"
    md_path = OUTPUT_DIR / f"PIPELINE_LOCATOR_REPORT_{ts}.md"

    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Pipeline Locator Report",
        f"Generated: {report['timestamp']}",
        "",
        f"## Status",
        f"- Pipeline found: {report['pipeline_found']}",
        f"- Historical write marker: {report['historical_write_marker'] or 'NOT FOUND'}",
        f"- Dry-run review gate: {report['dry_run_review_gate'] or 'NOT FOUND'}",
        f"- Controlled write runner: {report['controlled_write_runner'] or 'NOT FOUND'}",
        f"- Post-write validation: {report['post_write_validation'] or 'NOT FOUND'}",
        f"- Rollback plan: {report['rollback_plan'] or 'NOT FOUND'}",
        f"- Expected import count: {report['expected_import_count']}",
        "",
        "## Write Flags",
    ]
    for k, v in report["write_flags"].items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Blocked Flags")
    for k, v in report["blocked_flags"].items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Artifacts")
    for a in report["artifacts"]:
        lines.append(f"- [{a['type']}] {a['path']} ({a['size']} bytes)")
    lines.append("")
    lines.append("## Notes")
    for n in report["notes"]:
        lines.append(f"- {n}")

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


if __name__ == "__main__":
    report = locate_pipeline()
    json_path, md_path = write_reports(report)
    print(f"JSON: {json_path}")
    print(f"MD:   {md_path}")
    print(f"Pipeline found: {report['pipeline_found']}")
    print(f"Expected import count: {report['expected_import_count']}")
