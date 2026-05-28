from __future__ import annotations

import json
import re
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(".").resolve()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

zip_path = Path(sys.argv[1]).resolve()
if not zip_path.exists():
    raise SystemExit(f"ZIP_NOT_FOUND:{zip_path}")

OUT_JSON = ROOT / "docs" / "runtime" / f"OBSIDIA_F30_1_WORKFLOW_GOVERNANCE_V5_AUDIT_{TS}.json"
OUT_MD = ROOT / "docs" / "runtime" / f"OBSIDIA_F30_1_WORKFLOW_GOVERNANCE_V5_AUDIT_{TS}.md"

EXPECTED_FILES = [
    "src/obsidia_workflow_governance/agents/agent_01_sop_extractor.py",
    "src/obsidia_workflow_governance/agents/agent_02_risk_analyzer.py",
    "src/obsidia_workflow_governance/agents/agent_03_compliance_mapper.py",
    "src/obsidia_workflow_governance/agents/agent_04_evidence_builder.py",
    "src/obsidia_workflow_governance/agents/agent_05_contradiction_replayer.py",
    "src/obsidia_workflow_governance/agents/agent_06_readonly_aggregator.py",
    "src/obsidia_workflow_governance/agents/orchestrator_readonly.py",
    "src/obsidia_workflow_governance/models.py",
    "src/obsidia_workflow_governance/boundary.py",
    "src/obsidia_workflow_governance/primitives/workflow_graph_readonly.py",
    "src/obsidia_workflow_governance/primitives/critical_action_detector.py",
    "src/obsidia_workflow_governance/primitives/workflow_replay_audit.py",
    "src/obsidia_workflow_governance/primitives/x108_workflow_gateway_readonly.py",
    "src/obsidia_workflow_governance/integration/brody_workflow_governance_snapshot_adapter.py",
    "src/obsidia_workflow_governance/integration/periphery_ops_route_contract.py",
    "src/obsidia_workflow_governance/integration/rightpanel_workbench_contract.py",
    "docs/REPO_AWARE_INTEGRATION_GUIDE_V5.md",
    "contracts/REPO_ALIGNMENT_CONTRACT_V5.json",
    "install/WINDOWS_POWERSHELL_APPLY_PLAN_V5.ps1",
]

BOUNDARY_TOKENS = [
    "KX108_ONLY",
    "readonly",
    "READONLY",
    "emits_act",
    "can_emit_act",
    "kernel_mutation",
    "x108_mutation",
    "memory_write",
    "graphiti_write",
    "neo4j_write",
]

DANGER_TOKENS = [
    "emits_act=True",
    "can_emit_act=True",
    "kernel_mutation=True",
    "x108_mutation=True",
    "memory_write=True",
    "graphiti_write=True",
    "neo4j_write=True",
    "runtime_execute=True",
    "subprocess.run",
    "os.system",
    "git push",
    "git commit",
    "execute_write",
    "write_transaction",
    "session.write_transaction",
]

CANONICAL_TARGET = "periphery/workflow_governance_readonly"


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


def read_zip_text(zf: zipfile.ZipFile, name: str) -> str:
    return zf.read(name).decode("utf-8-sig", errors="replace")


def line_hits(text: str, tokens: list[str]) -> list[dict]:
    hits = []
    for idx, line in enumerate(text.splitlines(), start=1):
        for token in tokens:
            if token in line:
                hits.append({
                    "line": idx,
                    "token": token,
                    "text": line.strip()[:260],
                })
    return hits


def main():
    with zipfile.ZipFile(zip_path) as zf:
        all_names = [n for n in zf.namelist() if not n.endswith("/")]
        normalized = {strip_root(n): n for n in all_names}

        py_files = [n for n in all_names if n.endswith(".py")]
        docs = [n for n in all_names if "/docs/" in n or n.endswith(".md")]
        contracts = [n for n in all_names if "/contracts/" in n and n.endswith(".json")]
        tests = [n for n in all_names if "/tests/" in n and n.endswith(".py")]
        freeze = [n for n in all_names if "/freeze/" in n]

        expected_found = []
        expected_missing = []
        for rel in EXPECTED_FILES:
            if rel in normalized:
                expected_found.append(rel)
            else:
                expected_missing.append(rel)

        records = []
        danger_records = []
        boundary_records = []

        for name in py_files:
            text = read_zip_text(zf, name)
            boundary_hits = line_hits(text, BOUNDARY_TOKENS)
            danger_hits = line_hits(text, DANGER_TOKENS)

            rec = {
                "zip_path": name,
                "normalized_path": strip_root(name),
                "line_count": len(text.splitlines()),
                "boundary_hits": boundary_hits[:30],
                "danger_hits": danger_hits[:30],
            }
            records.append(rec)

            if boundary_hits:
                boundary_records.append(rec)
            if danger_hits:
                danger_records.append(rec)

        repo_target_exists = (ROOT / CANONICAL_TARGET).exists()
        old_minimal_target_exists = (ROOT / "periphery" / "workflows").exists()

        integration_decision = {
            "selected_source": "OBSIDIA_WORKFLOW_GOVERNANCE_PRIMITIVE_V5",
            "canonical_target": CANONICAL_TARGET,
            "copy_now": False,
            "runtime_patch_now": False,
            "reason": "F30.1 is audit-only. F30.2 should copy selected V5 readonly module into canonical target after this audit.",
        }

        report = {
            "report_id": f"OBSIDIA_F30_1_WORKFLOW_GOVERNANCE_V5_AUDIT_{TS}",
            "phase": "F30.1",
            "mode": "ZIP_AUDIT_ONLY_NO_PATCH",
            "commit": False,
            "tag": False,
            "freeze": False,
            "head": git(["git", "rev-parse", "--short", "HEAD"]),
            "tag_context": git(["git", "tag", "--points-at", "HEAD"]),
            "zip_path": str(zip_path),
            "zip_file_count": len(all_names),
            "python_file_count": len(py_files),
            "docs_count": len(docs),
            "contracts_count": len(contracts),
            "tests_count": len(tests),
            "freeze_file_count": len(freeze),
            "expected_files_count": len(EXPECTED_FILES),
            "expected_found_count": len(expected_found),
            "expected_missing_count": len(expected_missing),
            "expected_found": expected_found,
            "expected_missing": expected_missing,
            "boundary_record_count": len(boundary_records),
            "danger_record_count": len(danger_records),
            "danger_records": danger_records,
            "records_sample": records[:40],
            "repo_target_exists": repo_target_exists,
            "old_minimal_target_exists": old_minimal_target_exists,
            "integration_decision": integration_decision,
            "selected_next": "F30.2_COPY_V5_READONLY_MODULE",
            "locked_decisions": [
                "F30.1 is audit-only.",
                "Do not run V5 install script directly.",
                "Do not patch runtime routes in F30.1.",
                "Do not merge into X108.",
                "Do not write Graphiti/Neo4j/memory.",
                "Canonical target is periphery/workflow_governance_readonly.",
                "Decision authority remains KX108_ONLY.",
            ],
            "status": "F30_1_WORKFLOW_GOVERNANCE_V5_AUDIT_DONE",
        }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("# OBSIDIA F30.1 — WORKFLOW GOVERNANCE V5 AUDIT")
    lines.append("")
    lines.append("Mode: ZIP_AUDIT_ONLY_NO_PATCH")
    lines.append("Commit: NO")
    lines.append("Tag: NO")
    lines.append("Freeze: NO")
    lines.append("")
    lines.append(f"HEAD: `{report['head']}`")
    lines.append(f"Tags on HEAD: `{report['tag_context'] or 'NONE'}`")
    lines.append(f"ZIP: `{zip_path}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- ZIP files: {len(all_names)}")
    lines.append(f"- Python files: {len(py_files)}")
    lines.append(f"- Docs: {len(docs)}")
    lines.append(f"- Contracts: {len(contracts)}")
    lines.append(f"- Tests: {len(tests)}")
    lines.append(f"- Freeze files: {len(freeze)}")
    lines.append(f"- Expected found: {len(expected_found)}/{len(EXPECTED_FILES)}")
    lines.append(f"- Expected missing: {len(expected_missing)}")
    lines.append(f"- Boundary records: {len(boundary_records)}")
    lines.append(f"- Danger records: {len(danger_records)}")
    lines.append("")
    lines.append("## Expected missing")
    lines.append("")
    if expected_missing:
        for item in expected_missing:
            lines.append(f"- `{item}`")
    else:
        lines.append("- None.")
    lines.append("")
    lines.append("## Danger records")
    lines.append("")
    if danger_records:
        for r in danger_records:
            lines.append(f"- `{r['normalized_path']}`")
            for h in r["danger_hits"][:12]:
                lines.append(f"  - L{h['line']} `{h['token']}` — {h['text']}")
    else:
        lines.append("- None.")
    lines.append("")
    lines.append("## Integration decision")
    lines.append("")
    lines.append("```text")
    lines.append("selected_source=OBSIDIA_WORKFLOW_GOVERNANCE_PRIMITIVE_V5")
    lines.append(f"canonical_target={CANONICAL_TARGET}")
    lines.append("copy_now=false")
    lines.append("runtime_patch_now=false")
    lines.append("next=F30.2_COPY_V5_READONLY_MODULE")
    lines.append("```")
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
    lines.append("F30_1_WORKFLOW_GOVERNANCE_V5_AUDIT_DONE")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("F30_1_WORKFLOW_GOVERNANCE_V5_AUDIT_DONE")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    print(f"ZIP_FILES={len(all_names)}")
    print(f"PY_FILES={len(py_files)}")
    print(f"EXPECTED_FOUND={len(expected_found)}")
    print(f"EXPECTED_MISSING={len(expected_missing)}")
    print(f"DANGER={len(danger_records)}")
    print(f"CANONICAL_TARGET={CANONICAL_TARGET}")
    print("NEXT=F30.2_COPY_V5_READONLY_MODULE")


if __name__ == "__main__":
    main()
