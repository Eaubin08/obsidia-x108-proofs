import argparse
import json
import os
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime, timezone

BOUNDARY = {
    "readonly": True,
    "response_only": True,
    "close_report": True,
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
    "brody_role": "MEMORY_PIPELINE_V2_CLOSE_REPORT_READONLY",
    "memory_role": "GUIDE_CONTEXT_NAVIGATION_ONLY",
}

REQUIRED_POINTERS = [
    "CURRENT_BRODY_MEMORY_PIPELINE_FREEZE_V2_READONLY_VALIDATE.txt",
    "CURRENT_BRODY_POST_GRAPHITI_REPLAY_QUERY_REGRESSION_READONLY_V1_VALIDATE.txt",
    "CURRENT_BRODY_POST_GRAPHITI_APPLY_VERIFY_READONLY_V1_VALIDATE.txt",
    "CURRENT_BRODY_GRAPHITI_GUARDED_MANUAL_APPLY_EXECUTION_MEMORY_ONLY.txt",
    "CURRENT_BRODY_GRAPHITI_GUARDED_MANUAL_APPLY_FROM_REVIEW_DECISION_READONLY_MEMORY_ONLY.txt",
    "CURRENT_BRODY_GRAPHITI_REVIEW_DECISION_APPLY_READONLY_V1_VALIDATE.txt",
    "CURRENT_BRODY_GRAPHITI_REVIEW_GATE_FROM_POST_HUMAN_DRY_RUN_READONLY_V1_VALIDATE.txt",
    "CURRENT_BRODY_GRAPHITI_IMPORT_DRY_RUN_FROM_POST_HUMAN_PREP_READONLY_V1_VALIDATE.txt",
    "CURRENT_BRODY_GRAPHITI_CANDIDATE_PREP_FROM_POST_HUMAN_TRIAGE_READONLY_V1_VALIDATE.txt",
    "CURRENT_BRODY_POST_HUMAN_REVIEW_MEMORY_TRIAGE_READONLY_V1_VALIDATE.txt",
    "CURRENT_BRODY_SESSION_CLOSE_DECISION_APPLY_READONLY_V1_VALIDATE.txt",
    "CURRENT_BRODY_SESSION_CLOSE_HUMAN_VALIDATION_GATE_READONLY_V1_VALIDATE.txt",
    "CURRENT_BRODY_MEMORY_PIPELINE_READONLY_FREEZE_REPORT_V1_VALIDATE.txt",
]

EXPECTED_PASS = {
    "CURRENT_BRODY_MEMORY_PIPELINE_FREEZE_V2_READONLY_VALIDATE.txt": "BRODY_MEMORY_PIPELINE_FREEZE_V2_READONLY_VALIDATE_PASS",
    "CURRENT_BRODY_POST_GRAPHITI_REPLAY_QUERY_REGRESSION_READONLY_V1_VALIDATE.txt": "BRODY_POST_GRAPHITI_REPLAY_QUERY_REGRESSION_READONLY_V1_VALIDATE_PASS",
    "CURRENT_BRODY_POST_GRAPHITI_APPLY_VERIFY_READONLY_V1_VALIDATE.txt": "BRODY_POST_GRAPHITI_APPLY_VERIFY_READONLY_V1_VALIDATE_PASS",
    "CURRENT_BRODY_GRAPHITI_GUARDED_MANUAL_APPLY_EXECUTION_MEMORY_ONLY.txt": "BRODY_GRAPHITI_GUARDED_MANUAL_APPLY_EXECUTION_MEMORY_ONLY_PASS",
    "CURRENT_BRODY_GRAPHITI_REVIEW_DECISION_APPLY_READONLY_V1_VALIDATE.txt": "BRODY_GRAPHITI_REVIEW_DECISION_APPLY_READONLY_V1_VALIDATE_PASS",
    "CURRENT_BRODY_GRAPHITI_REVIEW_GATE_FROM_POST_HUMAN_DRY_RUN_READONLY_V1_VALIDATE.txt": "BRODY_GRAPHITI_REVIEW_GATE_FROM_POST_HUMAN_DRY_RUN_READONLY_V1_VALIDATE_PASS",
    "CURRENT_BRODY_GRAPHITI_IMPORT_DRY_RUN_FROM_POST_HUMAN_PREP_READONLY_V1_VALIDATE.txt": "BRODY_GRAPHITI_IMPORT_DRY_RUN_FROM_POST_HUMAN_PREP_READONLY_V1_VALIDATE_PASS",
    "CURRENT_BRODY_GRAPHITI_CANDIDATE_PREP_FROM_POST_HUMAN_TRIAGE_READONLY_V1_VALIDATE.txt": "BRODY_GRAPHITI_CANDIDATE_PREP_FROM_POST_HUMAN_TRIAGE_READONLY_V1_VALIDATE_PASS",
    "CURRENT_BRODY_POST_HUMAN_REVIEW_MEMORY_TRIAGE_READONLY_V1_VALIDATE.txt": "BRODY_POST_HUMAN_REVIEW_MEMORY_TRIAGE_READONLY_V1_VALIDATE_PASS",
    "CURRENT_BRODY_SESSION_CLOSE_DECISION_APPLY_READONLY_V1_VALIDATE.txt": "BRODY_SESSION_CLOSE_DECISION_APPLY_READONLY_V1_VALIDATE_PASS",
    "CURRENT_BRODY_SESSION_CLOSE_HUMAN_VALIDATION_GATE_READONLY_V1_VALIDATE.txt": "BRODY_SESSION_CLOSE_HUMAN_VALIDATION_GATE_READONLY_V1_VALIDATE_PASS",
    "CURRENT_BRODY_MEMORY_PIPELINE_READONLY_FREEZE_REPORT_V1_VALIDATE.txt": "BRODY_MEMORY_PIPELINE_READONLY_FREEZE_REPORT_V1_VALIDATE_PASS",
}

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()

def parse_pointer(path: Path):
    kv = {}
    for line in path.read_text(encoding="utf-8-sig", errors="ignore").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            kv[k.strip()] = v.strip()
    return kv

def load_json_if_present(path):
    p = Path(path)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8", errors="ignore"))

def git_short_head(repo_root: Path):
    return subprocess.check_output(
        ["git", "-C", str(repo_root), "rev-parse", "--short", "HEAD"],
        text=True,
        encoding="utf-8",
        errors="ignore"
    ).strip()

def git_status_short(repo_root: Path):
    return subprocess.check_output(
        ["git", "-C", str(repo_root), "status", "--short"],
        text=True,
        encoding="utf-8",
        errors="ignore"
    ).strip()

def resolve_pointer_path(workspace_root: Path, repo_root: Path, name: str):
    candidates = [
        workspace_root / name,
        repo_root / name,
    ]
    for p in candidates:
        if p.exists():
            return p
    return workspace_root / name

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[3]
    workspace_root = repo_root.parent
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    head = git_short_head(repo_root)
    status_short = git_status_short(repo_root)

    pointer_records = []
    missing = []
    bad_status = []
    loaded_summaries = {}

    for name in REQUIRED_POINTERS:
        path = resolve_pointer_path(workspace_root, repo_root, name)
        if not path.exists():
            missing.append(str(path))
            continue

        kv = parse_pointer(path)
        status = kv.get("STATUS", "")
        expected = EXPECTED_PASS.get(name)

        if expected and status != expected:
            bad_status.append({
                "name": name,
                "path": str(path),
                "status": status,
                "expected": expected,
            })

        summary_json = kv.get("SUMMARY_JSON")
        summary = load_json_if_present(summary_json) if summary_json else None
        if summary is not None:
            loaded_summaries[name] = summary

        pointer_records.append({
            "name": name,
            "path": str(path),
            "status": status,
            "expected_status": expected,
            "summary_json": summary_json,
            "keys": kv,
            "sha256": sha256_text(path.read_text(encoding="utf-8-sig", errors="ignore")),
        })

    freeze_v2 = loaded_summaries.get("CURRENT_BRODY_MEMORY_PIPELINE_FREEZE_V2_READONLY_VALIDATE.txt", {})
    replay = loaded_summaries.get("CURRENT_BRODY_POST_GRAPHITI_REPLAY_QUERY_REGRESSION_READONLY_V1_VALIDATE.txt", {})
    verify = loaded_summaries.get("CURRENT_BRODY_POST_GRAPHITI_APPLY_VERIFY_READONLY_V1_VALIDATE.txt", {})
    apply_exec = loaded_summaries.get("CURRENT_BRODY_GRAPHITI_GUARDED_MANUAL_APPLY_EXECUTION_MEMORY_ONLY.txt", {})

    close_ok = (
        len(missing) == 0
        and len(bad_status) == 0
        and freeze_v2.get("status") == "BRODY_MEMORY_PIPELINE_FREEZE_V2_READONLY_PASS"
        and freeze_v2.get("freeze_ok") is True
        and int(freeze_v2.get("status_fail_count", -1)) == 0
        and int(freeze_v2.get("allowed_historical_status_fail_count", -1)) == 2
        and int(freeze_v2.get("manual_apply_write_executed_count", -1)) == 29
        and int(freeze_v2.get("apply_verify_found_count", -1)) == 29
        and int(freeze_v2.get("replay_exact_found_count", -1)) == 29
        and int(freeze_v2.get("replay_prefix_hit_count", -1)) >= 29
        and replay.get("regression_ok") is True
        and int(replay.get("exact_replay_found_count", -1)) == 29
        and int(replay.get("required_prefix_query_applied_hit_count", -1)) >= 29
        and verify.get("verified_previous_graphiti_write") is True
        and verify.get("verified_previous_memory_intake") is True
        and int(verify.get("found_applied_id_count", -1)) == 29
        and apply_exec.get("manual_apply_executed") is True
        and int(apply_exec.get("write_executed_count", -1)) == 29
    )

    pointer_records_json = out_dir / "BRODY_MEMORY_PIPELINE_V2_CLOSE_POINTER_RECORDS.json"
    summary_json = out_dir / "BRODY_MEMORY_PIPELINE_V2_CLOSE_SUMMARY.json"
    report_md = out_dir / "BRODY_MEMORY_PIPELINE_V2_CLOSE_REPORT.md"

    pointer_records_json.write_text(json.dumps(pointer_records, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = {
        "status": "BRODY_MEMORY_PIPELINE_V2_CLOSE_REPORT_READONLY_PASS" if close_ok else "BRODY_MEMORY_PIPELINE_V2_CLOSE_REPORT_READONLY_FAIL",
        "created_at": now_iso(),
        "head": head,
        "git_status_clean": status_short == "",
        "git_status_short": status_short,
        "required_pointer_count": len(REQUIRED_POINTERS),
        "required_pointer_found_count": len(pointer_records),
        "required_pointer_missing_count": len(missing),
        "missing_required_pointers": missing,
        "bad_status_count": len(bad_status),
        "bad_status_records": bad_status,
        "freeze_v2_status": freeze_v2.get("status"),
        "freeze_v2_patch": freeze_v2.get("patch"),
        "freeze_ok": freeze_v2.get("freeze_ok"),
        "status_fail_count": freeze_v2.get("status_fail_count"),
        "allowed_historical_status_fail_count": freeze_v2.get("allowed_historical_status_fail_count"),
        "manual_apply_write_executed_count": freeze_v2.get("manual_apply_write_executed_count"),
        "apply_verify_found_count": freeze_v2.get("apply_verify_found_count"),
        "replay_exact_found_count": freeze_v2.get("replay_exact_found_count"),
        "replay_prefix_hit_count": freeze_v2.get("replay_prefix_hit_count"),
        "replay_regression_ok": replay.get("regression_ok"),
        "replay_query_count": replay.get("query_count"),
        "replay_query_records_pass_count": replay.get("query_records_pass_count"),
        "previous_graphiti_write_verified": verify.get("verified_previous_graphiti_write"),
        "previous_memory_intake_verified": verify.get("verified_previous_memory_intake"),
        "manual_apply_executed": apply_exec.get("manual_apply_executed"),
        "manual_apply_write_count": apply_exec.get("write_executed_count"),
        "close_ok": close_ok,
        "interpretation": "Brody memory pipeline V2 is closed: post-human review, guarded manual memory-only Graphiti apply, post-apply verification, and scalar-safe readonly replay are validated.",
        "outputs": {
            "pointer_records_json": str(pointer_records_json),
            "summary_json": str(summary_json),
            "report_md": str(report_md),
        },
        "next": "MICRO_SMOKE_BRODY_MEMORY_READONLY_THEN_BUILD_SESSION_REOPEN_LOOP",
        **BOUNDARY,
    }

    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# BRODY MEMORY PIPELINE V2 CLOSE REPORT READONLY",
        "",
        f"- status: {summary['status']}",
        f"- head: {head}",
        f"- git_status_clean: {str(summary['git_status_clean']).lower()}",
        f"- required_pointer_found_count: {summary['required_pointer_found_count']}/{summary['required_pointer_count']}",
        f"- required_pointer_missing_count: {summary['required_pointer_missing_count']}",
        f"- bad_status_count: {summary['bad_status_count']}",
        f"- freeze_v2_status: {summary['freeze_v2_status']}",
        f"- freeze_v2_patch: {summary['freeze_v2_patch']}",
        f"- freeze_ok: {str(summary['freeze_ok']).lower()}",
        f"- status_fail_count: {summary['status_fail_count']}",
        f"- allowed_historical_status_fail_count: {summary['allowed_historical_status_fail_count']}",
        f"- manual_apply_write_executed_count: {summary['manual_apply_write_executed_count']}",
        f"- apply_verify_found_count: {summary['apply_verify_found_count']}",
        f"- replay_exact_found_count: {summary['replay_exact_found_count']}",
        f"- replay_prefix_hit_count: {summary['replay_prefix_hit_count']}",
        f"- replay_regression_ok: {str(summary['replay_regression_ok']).lower()}",
        f"- close_ok: {str(close_ok).lower()}",
        "",
        "## Boundary",
        "",
        "- readonly: true",
        "- graphiti_index_write: false",
        "- neo4j_write_executed: false",
        "- memory_intake: false",
        "- memory_decision: false",
        "- allowed_to_decide: false",
        "- emits_act: false",
        "- emits_verdict: false",
        "- kernel_mutation: false",
        "- x108_runtime_binding: false",
        "- x108_merge: false",
        "- decision_authority: KX108_ONLY",
        "",
        "## Interpretation",
        "",
        summary["interpretation"],
        "",
        "## Next",
        "",
        summary["next"],
    ]

    if missing:
        lines += ["", "## Missing pointers", ""]
        lines += [f"- {x}" for x in missing]

    if bad_status:
        lines += ["", "## Bad status records", ""]
        lines += [f"- {x['name']} :: {x['status']} expected {x['expected']}" for x in bad_status]

    report_md.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))

    if not close_ok:
        raise SystemExit("BRODY_MEMORY_PIPELINE_V2_CLOSE_REPORT_READONLY_FAILED")

if __name__ == "__main__":
    main()

