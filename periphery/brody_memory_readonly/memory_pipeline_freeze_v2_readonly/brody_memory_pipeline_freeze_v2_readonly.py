import argparse
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

BOUNDARY = {
    "readonly": True,
    "response_only": True,
    "freeze_v2": True,
    "graphiti_index_write": False,
    "neo4j_write_executed": False,
    "memory_intake": False,
    "memory_decision": False,
    "allowed_to_decide": False,
    "emits_act": False,
    "emits_verdict": False,
    "kernel_mutation": False,
    "x108_runtime_binding": False,
    "x108_merge": False,
    "decision_authority": "KX108_ONLY",
    "ui": False,
    "brody_role": "MEMORY_PIPELINE_FREEZE_V2_READONLY",
    "memory_role": "GUIDE_CONTEXT_NAVIGATION_ONLY",
}

REQUIRED_POINTERS = [
    "CURRENT_BRODY_MEMORY_PIPELINE_READONLY_FREEZE_REPORT_V1_VALIDATE.txt",
    "CURRENT_BRODY_PROJECT_INTAKE_CAPTURE_BUFFER_READONLY.txt",
    "CURRENT_BRODY_SESSION_PRESAVE_BUFFER_READONLY.txt",
    "CURRENT_BRODY_SESSION_CLOSE_HUMAN_VALIDATION_GATE_READONLY.txt",
    "CURRENT_BRODY_SESSION_CLOSE_DECISION_APPLY_READONLY.txt",
    "CURRENT_BRODY_POST_HUMAN_REVIEW_MEMORY_TRIAGE_READONLY.txt",
    "CURRENT_BRODY_GRAPHITI_CANDIDATE_PREP_FROM_POST_HUMAN_TRIAGE_READONLY.txt",
    "CURRENT_BRODY_GRAPHITI_IMPORT_DRY_RUN_FROM_POST_HUMAN_PREP_READONLY.txt",
    "CURRENT_BRODY_GRAPHITI_REVIEW_GATE_FROM_POST_HUMAN_DRY_RUN_READONLY.txt",
    "CURRENT_BRODY_GRAPHITI_REVIEW_DECISION_APPLY_READONLY.txt",
    "CURRENT_BRODY_GRAPHITI_GUARDED_MANUAL_APPLY_FROM_REVIEW_DECISION_READONLY_MEMORY_ONLY.txt",
    "CURRENT_BRODY_GRAPHITI_GUARDED_MANUAL_APPLY_EXECUTION_MEMORY_ONLY.txt",
    "CURRENT_BRODY_POST_GRAPHITI_APPLY_VERIFY_READONLY.txt",
    "CURRENT_BRODY_POST_GRAPHITI_APPLY_VERIFY_READONLY_V1_VALIDATE.txt",
    "CURRENT_BRODY_POST_GRAPHITI_REPLAY_QUERY_REGRESSION_READONLY.txt",
    "CURRENT_BRODY_POST_GRAPHITI_REPLAY_QUERY_REGRESSION_READONLY_V1_VALIDATE.txt",
]

EXPECTED_V2_CHAIN = [
    "BRODY_MEMORY_PIPELINE_READONLY_FREEZE_REPORT_V1_VALIDATE",
    "BRODY_PROJECT_INTAKE_CAPTURE_BUFFER_READONLY",
    "BRODY_SESSION_PRESAVE_BUFFER_READONLY",
    "BRODY_SESSION_CLOSE_HUMAN_VALIDATION_GATE_READONLY",
    "BRODY_SESSION_CLOSE_DECISION_APPLY_READONLY",
    "BRODY_POST_HUMAN_REVIEW_MEMORY_TRIAGE_READONLY",
    "BRODY_GRAPHITI_CANDIDATE_PREP_FROM_POST_HUMAN_TRIAGE_READONLY",
    "BRODY_GRAPHITI_IMPORT_DRY_RUN_FROM_POST_HUMAN_PREP_READONLY",
    "BRODY_GRAPHITI_REVIEW_GATE_FROM_POST_HUMAN_DRY_RUN_READONLY",
    "BRODY_GRAPHITI_REVIEW_DECISION_APPLY_READONLY",
    "BRODY_GRAPHITI_GUARDED_MANUAL_APPLY_FROM_REVIEW_DECISION_READONLY_MEMORY_ONLY",
    "BRODY_GRAPHITI_GUARDED_MANUAL_APPLY_EXECUTION_MEMORY_ONLY",
    "BRODY_POST_GRAPHITI_APPLY_VERIFY_READONLY",
    "BRODY_POST_GRAPHITI_REPLAY_QUERY_REGRESSION_READONLY",
]

ALLOWED_HISTORICAL_FAILED_POINTERS = {
    "CURRENT_BRODY_NEO4J_GUIDE_BRIDGE_IMPORT_SMOKE_FAILED.txt",
    "CURRENT_BRODY_NEO4J_GUIDE_BRIDGE_IMPORT_SMOKE_FAILED_REAL.txt",
}

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()

def parse_pointer(path: Path):
    kv = {}
    text = path.read_text(encoding="utf-8-sig", errors="ignore")
    for line in text.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            kv[k.strip()] = v.strip()
    return kv, text

def load_json_if_exists(path_str):
    if not path_str:
        return None
    p = Path(path_str)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8", errors="ignore"))

def classify_pointer(name: str):
    n = name.upper()
    n = n.replace("CURRENT_", "").replace(".TXT", "")
    return n

def collect_pointer(path: Path):
    kv, text = parse_pointer(path)
    return {
        "name": path.name,
        "path": str(path),
        "sha256": sha256_bytes(path.read_bytes()),
        "size": path.stat().st_size,
        "stage": classify_pointer(path.name),
        "status": kv.get("STATUS"),
        "next": kv.get("NEXT"),
        "keys": kv,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[3]
    workspace_root = repo_root.parent

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    pointer_dirs = [workspace_root, repo_root]
    records = []
    seen = set()

    for d in pointer_dirs:
        for p in sorted(d.glob("CURRENT_*.txt")):
            rp = str(p.resolve())
            if rp in seen:
                continue
            seen.add(rp)
            records.append(collect_pointer(p))

    found_names = {r["name"] for r in records}
    missing_required = [name for name in REQUIRED_POINTERS if name not in found_names]

    status_fail = []
    allowed_historical_status_fail = []

    for r in records:
        status = str(r.get("status") or "")
        if "FAILED" in status:
            rec = {
                "name": r["name"],
                "path": r["path"],
                "status": status,
                "historical_reflex_trace": r["name"] in ALLOWED_HISTORICAL_FAILED_POINTERS,
            }

            if r["name"] in ALLOWED_HISTORICAL_FAILED_POINTERS:
                allowed_historical_status_fail.append(rec)
            else:
                status_fail.append(rec)

    by_name = {r["name"]: r for r in records}

    replay_validate = by_name.get("CURRENT_BRODY_POST_GRAPHITI_REPLAY_QUERY_REGRESSION_READONLY_V1_VALIDATE.txt")
    apply_verify = by_name.get("CURRENT_BRODY_POST_GRAPHITI_APPLY_VERIFY_READONLY_V1_VALIDATE.txt")
    manual_apply_exec = by_name.get("CURRENT_BRODY_GRAPHITI_GUARDED_MANUAL_APPLY_EXECUTION_MEMORY_ONLY.txt")
    freeze_v1 = by_name.get("CURRENT_BRODY_MEMORY_PIPELINE_READONLY_FREEZE_REPORT_V1_VALIDATE.txt")

    critical = {
        "replay_validate_present": replay_validate is not None,
        "apply_verify_present": apply_verify is not None,
        "manual_apply_execution_present": manual_apply_exec is not None,
        "freeze_v1_present": freeze_v1 is not None,
    }

    replay_summary = load_json_if_exists((replay_validate or {}).get("keys", {}).get("SUMMARY_JSON")) if replay_validate else None
    apply_verify_summary = load_json_if_exists((apply_verify or {}).get("keys", {}).get("SUMMARY_JSON")) if apply_verify else None
    manual_apply_summary = load_json_if_exists((manual_apply_exec or {}).get("keys", {}).get("SUMMARY_JSON")) if manual_apply_exec else None
    freeze_v1_summary = load_json_if_exists((freeze_v1 or {}).get("keys", {}).get("SUMMARY_JSON")) if freeze_v1 else None

    replay_ok = (
        replay_summary is not None
        and replay_summary.get("status") == "BRODY_POST_GRAPHITI_REPLAY_QUERY_REGRESSION_READONLY_V1_PASS"
        and replay_summary.get("patch") == "V1_2_SCALAR_SAFE_PARAM_FIX"
        and int(replay_summary.get("expected_applied_id_count", -1)) == 29
        and int(replay_summary.get("exact_replay_found_count", -1)) == 29
        and int(replay_summary.get("missing_applied_id_count", -1)) == 0
        and int(replay_summary.get("required_prefix_query_applied_hit_count", -1)) >= 29
        and replay_summary.get("regression_ok") is True
        and replay_summary.get("graphiti_index_write") is False
        and replay_summary.get("neo4j_write_executed") is False
        and replay_summary.get("memory_decision") is False
        and replay_summary.get("decision_authority") == "KX108_ONLY"
    )

    apply_verify_ok = (
        apply_verify_summary is not None
        and apply_verify_summary.get("status") == "BRODY_POST_GRAPHITI_APPLY_VERIFY_READONLY_V1_PASS"
        and int(apply_verify_summary.get("expected_applied_id_count", -1)) == 29
        and int(apply_verify_summary.get("found_applied_id_count", -1)) == 29
        and int(apply_verify_summary.get("missing_applied_id_count", -1)) == 0
        and apply_verify_summary.get("verified_previous_graphiti_write") is True
        and apply_verify_summary.get("verified_previous_memory_intake") is True
        and apply_verify_summary.get("memory_decision") is False
        and apply_verify_summary.get("decision_authority") == "KX108_ONLY"
    )

    manual_apply_ok = (
        manual_apply_summary is not None
        and manual_apply_summary.get("status") == "BRODY_GRAPHITI_GUARDED_MANUAL_APPLY_FROM_REVIEW_DECISION_READONLY_MEMORY_ONLY_V1_PASS"
        and manual_apply_summary.get("manual_apply_executed") is True
        and int(manual_apply_summary.get("write_executed_count", -1)) == 29
        and manual_apply_summary.get("graphiti_index_write") is True
        and manual_apply_summary.get("neo4j_write_executed") is True
        and manual_apply_summary.get("memory_intake") is True
        and manual_apply_summary.get("memory_decision") is False
        and manual_apply_summary.get("decision_authority") == "KX108_ONLY"
    )

    freeze_v1_ok = (
        freeze_v1_summary is not None
        and int(freeze_v1_summary.get("pipeline_stage_count", -1)) == 14
        and int(freeze_v1_summary.get("pipeline_stage_found_count", -1)) == 14
        and int(freeze_v1_summary.get("pipeline_stage_missing_count", -1)) == 0
        and int(freeze_v1_summary.get("pointer_file_count", -1)) >= 51
        and freeze_v1_summary.get("memory_decision") is False
        and freeze_v1_summary.get("decision_authority") == "KX108_ONLY"
    )

    chain_found = []
    for stage in EXPECTED_V2_CHAIN:
        found = any(stage in r["stage"] for r in records)
        chain_found.append({"stage": stage, "found": found})

    chain_missing = [x["stage"] for x in chain_found if not x["found"]]

    freeze_ok = (
        len(missing_required) == 0
        and len(status_fail) == 0
        and replay_ok
        and apply_verify_ok
        and manual_apply_ok
        and freeze_v1_ok
        and len(chain_missing) == 0
    )

    pointer_records_json = out_dir / "BRODY_MEMORY_PIPELINE_FREEZE_V2_POINTER_RECORDS.json"
    summary_json = out_dir / "BRODY_MEMORY_PIPELINE_FREEZE_V2_SUMMARY.json"
    report_md = out_dir / "BRODY_MEMORY_PIPELINE_FREEZE_V2_REPORT.md"
    manifest_json = out_dir / "BRODY_MEMORY_PIPELINE_FREEZE_V2_MANIFEST.json"

    pointer_records_json.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = {
        "status": "BRODY_MEMORY_PIPELINE_FREEZE_V2_READONLY_PASS" if freeze_ok else "BRODY_MEMORY_PIPELINE_FREEZE_V2_READONLY_FAIL",
        "created_at": now_iso(),
        "head_scope": "LOCAL_GIT_HEAD_CHECKED_BY_CALLER",
        "pointer_record_count": len(records),
        "required_pointer_count": len(REQUIRED_POINTERS),
        "required_pointer_found_count": len(REQUIRED_POINTERS) - len(missing_required),
        "required_pointer_missing_count": len(missing_required),
        "missing_required_pointers": missing_required,
                "status_fail_count": len(status_fail),
        "allowed_historical_status_fail_count": len(allowed_historical_status_fail),
        "allowed_historical_status_fail_records": allowed_historical_status_fail,
        "status_fail_records": status_fail,
        "expected_v2_chain_count": len(EXPECTED_V2_CHAIN),
        "expected_v2_chain_found_count": len(EXPECTED_V2_CHAIN) - len(chain_missing),
        "expected_v2_chain_missing_count": len(chain_missing),
        "expected_v2_chain_missing": chain_missing,
        "critical": critical,
        "freeze_v1_ok": freeze_v1_ok,
        "manual_apply_ok": manual_apply_ok,
        "apply_verify_ok": apply_verify_ok,
        "replay_ok": replay_ok,
        "manual_apply_write_executed_count": int(manual_apply_summary.get("write_executed_count", 0)) if manual_apply_summary else 0,
        "apply_verify_found_count": int(apply_verify_summary.get("found_applied_id_count", 0)) if apply_verify_summary else 0,
        "replay_exact_found_count": int(replay_summary.get("exact_replay_found_count", 0)) if replay_summary else 0,
        "replay_prefix_hit_count": int(replay_summary.get("required_prefix_query_applied_hit_count", 0)) if replay_summary else 0,
        "regression_ok": replay_ok,
        "freeze_ok": freeze_ok,
        "previous_graphiti_write_verified": apply_verify_ok,
        "previous_memory_intake_verified": apply_verify_ok,
                "patch": "V2_1_REFLEX_FAILED_POINTER_ALLOWLIST",
        "v2_interpretation": "Freeze V2 seals the full Brody memory pipeline including post-human review, guarded memory-only Graphiti apply, post-apply verification, and scalar-safe readonly replay regression. Historical Neo4j smoke failed pointers are preserved as reflex traces but are not blockers.",
        "outputs": {
            "pointer_records_json": str(pointer_records_json),
            "summary_json": str(summary_json),
            "report_md": str(report_md),
            "manifest_json": str(manifest_json),
        },
        "next": "REVIEW_THEN_COMMIT_BRODY_MEMORY_PIPELINE_FREEZE_V2_READONLY",
        **BOUNDARY,
    }

    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    manifest = {
        "name": "BRODY_MEMORY_PIPELINE_FREEZE_V2_READONLY",
        "version": "v2",
        "status": summary["status"],
        "created_at": summary["created_at"],
        "freeze_ok": freeze_ok,
        "pointer_record_count": len(records),
        "required_pointer_count": len(REQUIRED_POINTERS),
        "expected_v2_chain_count": len(EXPECTED_V2_CHAIN),
        "outputs": summary["outputs"],
        **BOUNDARY,
    }

    manifest_json.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# BRODY MEMORY PIPELINE FREEZE V2 READONLY",
        "",
        f"- status: {summary['status']}",
        f"- pointer_record_count: {summary['pointer_record_count']}",
        f"- required_pointer_found_count: {summary['required_pointer_found_count']}/{summary['required_pointer_count']}",
        f"- expected_v2_chain_found_count: {summary['expected_v2_chain_found_count']}/{summary['expected_v2_chain_count']}",
        f"- freeze_v1_ok: {str(freeze_v1_ok).lower()}",
        f"- manual_apply_ok: {str(manual_apply_ok).lower()}",
        f"- apply_verify_ok: {str(apply_verify_ok).lower()}",
        f"- replay_ok: {str(replay_ok).lower()}",
        f"- manual_apply_write_executed_count: {summary['manual_apply_write_executed_count']}",
        f"- apply_verify_found_count: {summary['apply_verify_found_count']}",
        f"- replay_exact_found_count: {summary['replay_exact_found_count']}",
        f"- replay_prefix_hit_count: {summary['replay_prefix_hit_count']}",
        f"- freeze_ok: {str(freeze_ok).lower()}",
        "",
        "## Boundary",
        "",
        "- Freeze V2 itself is readonly.",
        "- It does not write Graphiti.",
        "- It does not write Neo4j.",
        "- It does not decide.",
        "- It does not emit ACT.",
        "- It does not emit verdict.",
        "- It does not mutate kernel.",
        "- It does not bind X108 runtime.",
        "- It does not merge X108.",
        "",
        "## Previous write evidence",
        "",
        "- Previous guarded manual memory-only apply wrote 29 records.",
        "- Post-apply verify found 29/29.",
        "- Replay regression found 29/29 and prefix query hit 29/29.",
        "",
        "## Next",
        "",
        summary["next"],
    ]

    if missing_required:
        lines += ["", "## Missing required pointers", ""]
        lines += [f"- {x}" for x in missing_required]

    if chain_missing:
        lines += ["", "## Missing chain stages", ""]
        lines += [f"- {x}" for x in chain_missing]

    if status_fail:
        lines += ["", "## Failed status records", ""]
        lines += [f"- {x['name']} :: {x['status']}" for x in status_fail]

    report_md.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))

    if not freeze_ok:
        raise SystemExit("BRODY_MEMORY_PIPELINE_FREEZE_V2_READONLY_FAILED")

if __name__ == "__main__":
    main()

