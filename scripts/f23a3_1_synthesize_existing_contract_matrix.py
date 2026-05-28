from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
OUT = ROOT / "docs" / "runtime"
OUT.mkdir(parents=True, exist_ok=True)

TS = datetime.now().strftime("%Y%m%d_%H%M%S")

def sh(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, cwd=ROOT, text=True, encoding="utf-8", errors="replace").strip()
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"

latest_json = sorted(
    OUT.glob("OBSIDIA_F23A3_0_EXISTING_RIGHTS_CONTRACTS_FLOW_AUDIT_*.json"),
    key=lambda p: p.stat().st_mtime,
    reverse=True,
)[0]

audit = json.loads(latest_json.read_text(encoding="utf-8"))

PRIORITY_FILES = audit.get("priority_files_found", [])

ACTORS = {
    "KX108": {
        "role": "sole decision authority",
        "files": [
            "apps/obsidia_api/brody_rights_authority_matrix.py",
            "apps/obsidia_api/brody_contracts_packet.py",
            "apps/obsidia_api/routes/x108.py",
            "apps/obsidia_api/routes/brody.py",
        ],
        "terms": [
            "KX108_ONLY",
            "decision_authority",
            "sole_decision_authority",
            "can_authorize_act",
            "x108_mutation",
        ],
    },
    "BRODY": {
        "role": "readonly advisory responder / structure-first narrator",
        "files": [
            "apps/obsidia_api/routes/brody.py",
            "apps/obsidia_api/brody_contracts_packet.py",
            "apps/obsidia_api/brody_rights_authority_matrix.py",
            "apps/obsidia_api/brody_v1_4_12a_final_answer_adapter.py",
            "apps/obsidia_api/brody_true_voice_adapter.py",
        ],
        "terms": [
            "can_decide",
            "can_act",
            "can_write_memory",
            "emits_act",
            "emits_verdict",
            "memory_write",
            "graphiti_write",
            "kernel_mutation",
            "x108_mutation",
            "readonly",
            "advisory",
        ],
    },
    "MEMORY_REFLEX": {
        "role": "candidate/reflex diagnostic layer",
        "files": [
            "apps/obsidia_api/brody_memory_promotion_guard.py",
            "apps/obsidia_api/brody_candidate_memory_adapter.py",
            "apps/obsidia_api/brody_runtime_context_adapter.py",
            "apps/obsidia_api/brody_temporal_context_adapter.py",
        ],
        "terms": [
            "candidate_memory",
            "memory_promotion_guard",
            "memory_write",
            "memory_commit",
            "graphiti_write",
            "readonly",
            "human_review",
            "decision_authority",
        ],
    },
    "AUTOMATION_ORCHESTRATOR": {
        "role": "dry-run / orchestration candidate layer",
        "files": [
            "apps/obsidia_api/brody_automation_orchestrator.py",
            "apps/obsidia_api/brody_full_runtime_orchestrator.py",
            "apps/obsidia_api/routes/worldcalls.py",
            "apps/obsidia_api/routes/periphery_ops.py",
        ],
        "terms": [
            "orchestrator",
            "automation",
            "automation_execute",
            "can_execute",
            "dry_run",
            "human_review",
            "readonly",
            "decision_authority",
            "memory_write",
            "graphiti_write",
            "kernel_mutation",
            "x108_mutation",
        ],
    },
    "GRAPHITI_MEMORY": {
        "role": "readonly memory/context source, write quarantined",
        "files": [
            "apps/obsidia_api/graphiti_v20_readonly_client.py",
            "apps/obsidia_api/brody_memory_promotion_guard.py",
            "apps/obsidia_api/brody_runtime_context_adapter.py",
            "apps/obsidia_api/routes/periphery_ops.py",
        ],
        "terms": [
            "graphiti",
            "readonly",
            "graphiti_write",
            "neo4j_write",
            "MERGE ",
            "CREATE ",
            "SET ",
            "human_review",
        ],
    },
    "OPERATOR_HUMAN": {
        "role": "human review / operator visibility / manual validation",
        "files": [
            "apps/obsidia_api/brody_operator_loop_adapter.py",
            "apps/obsidia_api/brody_operator_view_packet.py",
            "apps/obsidia_api/brody_memory_promotion_guard.py",
            "apps/obsidia_api/routes/runtime_freeze.py",
        ],
        "terms": [
            "operator",
            "human_review",
            "human_review_required",
            "manual",
            "dry_run",
            "can_commit",
            "freeze",
            "promotion_guard",
        ],
    },
}

CONTRACT_FIELDS = [
    "decision_authority",
    "readonly",
    "advisory_only",
    "context_signal_only",
    "can_decide",
    "can_act",
    "can_write_memory",
    "can_execute",
    "emits_act",
    "emits_verdict",
    "memory_write",
    "memory_commit",
    "graphiti_write",
    "neo4j_write",
    "automation_execute",
    "kernel_mutation",
    "x108_mutation",
    "dry_run",
    "human_review",
    "human_review_required",
]

FORBIDDEN_TOKENS = [
    "MERGE ",
    "CREATE ",
    "SET ",
    "DELETE ",
    "DETACH DELETE",
    "session.write_transaction",
    "execute_write",
    "os.system(",
    "git commit",
    "git push",
]

def read_file(rel: str) -> str:
    try:
        return (ROOT / rel).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""

def snippets(rel: str, terms: list[str], limit: int = 40) -> list[dict]:
    text = read_file(rel)
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        low = line.lower()
        for term in terms:
            if term.lower() in low:
                out.append({"path": rel, "line": i, "term": term, "text": line[:420]})
                break
    return out[:limit]

def field_hits(files: list[str], field: str) -> list[dict]:
    out = []
    for f in files:
        out.extend(snippets(f, [field], limit=20))
    return out[:30]

def infer_actor(actor: str, spec: dict) -> dict:
    files = [f for f in spec["files"] if (ROOT / f).exists()]
    evidence = []
    forbidden = []

    for f in files:
        evidence.extend(snippets(f, spec["terms"], limit=40))
        text = read_file(f)
        for tok in FORBIDDEN_TOKENS:
            if tok in text:
                forbidden.append({"path": f, "token": tok})

    fields = {}
    for field in CONTRACT_FIELDS:
        hits = field_hits(files, field)
        if hits:
            fields[field] = {
                "observed": True,
                "evidence": hits[:10],
            }
        else:
            fields[field] = {
                "observed": False,
                "evidence": [],
            }

    return {
        "actor": actor,
        "role": spec["role"],
        "evidence_files": files,
        "field_observations": fields,
        "evidence_hits": evidence[:80],
        "forbidden_write_tokens_found": forbidden,
    }

actors = {actor: infer_actor(actor, spec) for actor, spec in ACTORS.items()}

# Conservative synthesis: only assert high-level rights that are already structurally repeated in the evidence.
SYNTHESIS = {
    "KX108": {
        "may_decide": True,
        "may_authorize_act": True,
        "may_be_mutated_by_brody": False,
        "basis": "KX108_ONLY / decision_authority / x108_mutation boundary evidence",
    },
    "BRODY": {
        "may_read": True,
        "may_structure": True,
        "may_explain": True,
        "may_emit_advisory_packet": True,
        "may_decide": False,
        "may_act": False,
        "may_write_memory": False,
        "may_write_graphiti": False,
        "may_execute_automation": False,
        "basis": "contracts packet + rights matrix + route boundary fields",
    },
    "MEMORY_REFLEX": {
        "may_detect_pattern": True,
        "may_emit_candidate_diagnostic": True,
        "may_commit_memory": False,
        "may_write_graphiti": False,
        "may_decide": False,
        "basis": "candidate memory + promotion guard + readonly context boundaries",
    },
    "AUTOMATION_ORCHESTRATOR": {
        "may_prepare_dry_run": True,
        "may_execute": False,
        "may_schedule": False,
        "may_write_memory": False,
        "may_write_graphiti": False,
        "requires_human_review": True,
        "basis": "orchestrator/dry_run/human_review/boundary evidence",
    },
    "GRAPHITI_MEMORY": {
        "may_provide_context": True,
        "may_be_written_by_f23a": False,
        "write_surfaces": "QUARANTINE_ONLY",
        "may_decide": False,
        "basis": "Graphiti readonly client + write token quarantine findings",
    },
    "OPERATOR_HUMAN": {
        "may_review": True,
        "may_validate_manual_future_phase": True,
        "may_commit_freeze_push": True,
        "automation_still_forbidden_without_explicit_gate": True,
        "basis": "operator view/loop + human_review + freeze route evidence",
    },
}

ALLOWED_FLOWS = [
    {
        "name": "prompt_to_readonly_diagnostic",
        "flow": ["USER_PROMPT", "BRODY", "CONTEXT_READONLY", "MEMORY_REFLEX_DIAGNOSTIC", "FINAL_ANSWER"],
        "writes": False,
        "executes": False,
        "decision_authority": "KX108_ONLY",
    },
    {
        "name": "candidate_memory_to_operator_review",
        "flow": ["CANDIDATE_MEMORY", "PROMOTION_GUARD", "OPERATOR_VIEW", "HUMAN_REVIEW"],
        "writes": False,
        "executes": False,
        "decision_authority": "KX108_ONLY",
    },
    {
        "name": "orchestrator_dry_run_to_operator",
        "flow": ["BRODY", "ORCHESTRATOR_DRY_RUN", "OPERATOR_VIEW", "HUMAN_REVIEW"],
        "writes": False,
        "executes": False,
        "decision_authority": "KX108_ONLY",
    },
]

FORBIDDEN_FLOWS = [
    "BRODY_TO_GRAPHITI_WRITE",
    "BRODY_TO_NEO4J_WRITE",
    "BRODY_TO_MEMORY_COMMIT",
    "BRODY_TO_AUTOMATION_EXECUTE",
    "MEMORY_REFLEX_TO_ACT",
    "MEMORY_REFLEX_TO_DECISION",
    "ORCHESTRATOR_TO_REAL_JOB",
    "ORCHESTRATOR_TO_SCHEDULER",
    "GRAPHITI_TO_DECISION",
    "SCORE_TO_RUNTIME_VERDICT",
]

matrix = {
    "checkpoint": "F23A3_1_SYNTHESIZE_EXISTING_CONTRACT_MATRIX_FROM_DISCOVERED_SOURCES",
    "timestamp": TS,
    "mode": "SYNTHESIS_FROM_EXISTING_SOURCES_NO_PATCH",
    "patch": "NO",
    "commit": "NO",
    "head": sh(["git", "rev-parse", "--short", "HEAD"]),
    "tag": sh(["git", "tag", "--points-at", "HEAD"]),
    "git_status": sh(["git", "status", "-sb"]),
    "source_audit_json": str(latest_json),
    "priority_files_found": PRIORITY_FILES,
    "actors": actors,
    "synthesis": SYNTHESIS,
    "allowed_flows": ALLOWED_FLOWS,
    "forbidden_flows": FORBIDDEN_FLOWS,
    "next": "F23A3_2_VALIDATE_SYNTHESIZED_MATRIX_AGAINST_SOURCE_FIELDS",
}

json_path = OUT / f"OBSIDIA_F23A3_1_EXISTING_CONTRACT_MATRIX_SYNTHESIS_{TS}.json"
md_path = OUT / f"OBSIDIA_F23A3_1_EXISTING_CONTRACT_MATRIX_SYNTHESIS_{TS}.md"

json_path.write_text(json.dumps(matrix, ensure_ascii=False, indent=2), encoding="utf-8")

lines = []
lines.append("# OBSIDIA F23A3.1 — EXISTING CONTRACT MATRIX SYNTHESIS")
lines.append("")
lines.append(f"Date: {TS}")
lines.append("Mode: SYNTHESIS_FROM_EXISTING_SOURCES_NO_PATCH")
lines.append("Patch: NO")
lines.append("Commit: NO")
lines.append("")
lines.append("## Git")
lines.append("")
lines.append(f"- HEAD: {matrix['head']}")
lines.append(f"- TAG: {matrix['tag']}")
lines.append("```text")
lines.append(matrix["git_status"])
lines.append("```")
lines.append("")
lines.append("## Source")
lines.append("")
lines.append(f"- source audit: `{latest_json}`")
lines.append("")
lines.append("## Synthesized rights matrix")
lines.append("")
for actor, rights in SYNTHESIS.items():
    lines.append(f"### {actor}")
    for k, v in rights.items():
        lines.append(f"- {k}: {v}")
    lines.append("")
lines.append("## Actor evidence files")
lines.append("")
for actor, data in actors.items():
    lines.append(f"### {actor}")
    lines.append(f"- role: {data['role']}")
    lines.append("- evidence_files:")
    for f in data["evidence_files"]:
        lines.append(f"  - `{f}`")
    lines.append(f"- forbidden_write_tokens_found: {data['forbidden_write_tokens_found']}")
    lines.append("")
    lines.append("Observed fields:")
    for field, obs in data["field_observations"].items():
        if obs["observed"]:
            lines.append(f"- {field}: observed")
    lines.append("")
    lines.append("Evidence snippets:")
    for h in data["evidence_hits"][:18]:
        lines.append(f"- `{h['path']}:L{h['line']}` [{h['term']}] {h['text']}")
    lines.append("")
lines.append("## Allowed flows")
lines.append("")
for f in ALLOWED_FLOWS:
    lines.append(f"### {f['name']}")
    lines.append(f"- flow: {' → '.join(f['flow'])}")
    lines.append(f"- writes: {f['writes']}")
    lines.append(f"- executes: {f['executes']}")
    lines.append(f"- decision_authority: {f['decision_authority']}")
    lines.append("")
lines.append("## Forbidden flows")
lines.append("")
for f in FORBIDDEN_FLOWS:
    lines.append(f"- {f}")
lines.append("")
lines.append("## Status")
lines.append("")
lines.append("F23A3_1_EXISTING_CONTRACT_MATRIX_SYNTHESIS_DONE")
lines.append("PATCH=NO")
lines.append("COMMIT=NO")
lines.append("NEXT=F23A3_2_VALIDATE_SYNTHESIZED_MATRIX_AGAINST_SOURCE_FIELDS")

md_path.write_text("\n".join(lines), encoding="utf-8")

print("F23A3_1_EXISTING_CONTRACT_MATRIX_SYNTHESIS_DONE")
print(f"HEAD={matrix['head']}")
print(f"TAG={matrix['tag']}")
print(f"REPORT_MD={md_path}")
print(f"REPORT_JSON={json_path}")
print("PATCH=NO")
print("COMMIT=NO")
print("NEXT=F23A3_2_VALIDATE_SYNTHESIZED_MATRIX_AGAINST_SOURCE_FIELDS")
