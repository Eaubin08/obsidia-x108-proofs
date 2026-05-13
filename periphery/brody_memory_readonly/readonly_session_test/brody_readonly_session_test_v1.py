import argparse
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

BOUNDARY = {
    "readonly": True,
    "response_only": True,
    "readonly_session_test": True,
    "file_read_only": True,
    "graphiti_query_read": False,
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
    "brody_role": "READONLY_SESSION_TEST",
    "memory_role": "GUIDE_CONTEXT_NAVIGATION_ONLY",
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

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))

def nonempty_file(path: Path):
    return path.exists() and path.is_file() and path.stat().st_size > 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[3]
    workspace_root = repo_root.parent

    scheduler_ptr = workspace_root / "CURRENT_BRODY_MEMORY_SCHEDULER_READONLY_V1_VALIDATE.txt"
    reopen_ptr = workspace_root / "CURRENT_BRODY_SESSION_REOPEN_LOOP_READONLY_V1_VALIDATE.txt"
    micro_ptr = workspace_root / "CURRENT_BRODY_MEMORY_READONLY_MICRO_SMOKE_V1_VALIDATE.txt"
    close_ptr = workspace_root / "CURRENT_BRODY_MEMORY_PIPELINE_V2_CLOSE_REPORT_READONLY_VALIDATE.txt"

    required_ptrs = [scheduler_ptr, reopen_ptr, micro_ptr, close_ptr]
    missing_ptrs = [str(p) for p in required_ptrs if not p.exists()]
    if missing_ptrs:
        raise RuntimeError(f"MISSING_REQUIRED_POINTERS={missing_ptrs}")

    scheduler_kv = parse_pointer(scheduler_ptr)
    reopen_kv = parse_pointer(reopen_ptr)
    micro_kv = parse_pointer(micro_ptr)
    close_kv = parse_pointer(close_ptr)

    scheduler_summary_json = Path(scheduler_kv.get("SUMMARY_JSON", ""))
    scheduler_plan_json = Path(scheduler_kv.get("SCHEDULE_JSON", ""))
    scheduler_prompt_md = Path(scheduler_kv.get("NEXT_SESSION_PROMPT_MD", ""))

    reopen_summary_json = Path(reopen_kv.get("SUMMARY_JSON", ""))
    context_packet_json = Path(reopen_kv.get("CONTEXT_PACKET_JSON", ""))
    prompt_context_md = Path(reopen_kv.get("PROMPT_CONTEXT_MD", ""))

    micro_summary_json = Path(micro_kv.get("SUMMARY_JSON", ""))
    close_summary_json = Path(close_kv.get("SUMMARY_JSON", ""))

    required_files = [
        scheduler_summary_json,
        scheduler_plan_json,
        scheduler_prompt_md,
        reopen_summary_json,
        context_packet_json,
        prompt_context_md,
        micro_summary_json,
        close_summary_json,
    ]

    missing_files = [str(p) for p in required_files if not nonempty_file(p)]
    if missing_files:
        raise RuntimeError(f"MISSING_OR_EMPTY_REQUIRED_FILES={missing_files}")

    scheduler_summary = load_json(scheduler_summary_json)
    scheduler_plan = load_json(scheduler_plan_json)
    reopen_summary = load_json(reopen_summary_json)
    micro_summary = load_json(micro_summary_json)
    close_summary = load_json(close_summary_json)

    scheduler_prompt_text = scheduler_prompt_md.read_text(encoding="utf-8", errors="ignore")
    prompt_context_text = prompt_context_md.read_text(encoding="utf-8", errors="ignore")

    checks = []

    def add_check(name, passed, detail):
        checks.append({
            "name": name,
            "passed": bool(passed),
            "detail": detail,
            "created_at": now_iso(),
            **BOUNDARY,
        })

    add_check(
        "scheduler_summary_pass",
        scheduler_summary.get("status") == "BRODY_MEMORY_SCHEDULER_READONLY_V1_PASS",
        scheduler_summary.get("status"),
    )
    add_check(
        "scheduler_ok",
        scheduler_summary.get("scheduler_ok") is True,
        scheduler_summary.get("scheduler_ok"),
    )
    add_check(
        "scheduler_plan_count_6",
        isinstance(scheduler_plan, list) and len(scheduler_plan) == 6,
        len(scheduler_plan) if isinstance(scheduler_plan, list) else "NOT_LIST",
    )
    add_check(
        "scheduler_no_auto_execution",
        scheduler_summary.get("automatic_execution") is False and scheduler_summary.get("cron_registered") is False,
        {
            "automatic_execution": scheduler_summary.get("automatic_execution"),
            "cron_registered": scheduler_summary.get("cron_registered"),
        },
    )
    add_check(
        "scheduler_human_trigger_required",
        scheduler_summary.get("requires_human_trigger") is True,
        scheduler_summary.get("requires_human_trigger"),
    )
    add_check(
        "reopen_loop_pass",
        reopen_summary.get("status") == "BRODY_SESSION_REOPEN_LOOP_READONLY_V1_PASS",
        reopen_summary.get("status"),
    )
    add_check(
        "context_packet_count_29",
        int(reopen_summary.get("context_packet_record_count", 0)) >= 29,
        reopen_summary.get("context_packet_record_count"),
    )
    add_check(
        "micro_smoke_pass",
        micro_summary.get("status") == "BRODY_MEMORY_READONLY_MICRO_SMOKE_V1_PASS",
        micro_summary.get("status"),
    )
    add_check(
        "close_report_pass",
        close_summary.get("status") == "BRODY_MEMORY_PIPELINE_V2_CLOSE_REPORT_READONLY_PASS",
        close_summary.get("status"),
    )
    add_check(
        "prompt_context_nonempty",
        len(prompt_context_text.strip()) > 0,
        len(prompt_context_text.strip()),
    )
    add_check(
        "scheduler_prompt_boundary_contains_kx108",
        "DECISION_AUTHORITY=KX108_ONLY" in scheduler_prompt_text,
        "DECISION_AUTHORITY=KX108_ONLY",
    )
    add_check(
        "scheduler_prompt_blocks_memory_decision",
        "MEMORY_DECISION=false" in scheduler_prompt_text,
        "MEMORY_DECISION=false",
    )

    prev = "GENESIS_BRODY_READONLY_SESSION_TEST_V1"
    for idx, check in enumerate(checks, start=1):
        check["index"] = idx
        seed = json.dumps({"prev": prev, "check": check}, ensure_ascii=False, sort_keys=True)
        check["prev_event_hash"] = prev
        check["event_hash"] = sha256_text(seed)
        prev = check["event_hash"]

    failed = [c for c in checks if not c["passed"]]
    session_test_ok = len(failed) == 0

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    checks_json = out_dir / "BRODY_READONLY_SESSION_TEST_CHECKS.json"
    session_plan_json = out_dir / "BRODY_READONLY_SESSION_TEST_PLAN.json"
    session_prompt_md = out_dir / "BRODY_READONLY_SESSION_TEST_PROMPT.md"
    summary_json = out_dir / "BRODY_READONLY_SESSION_TEST_SUMMARY.json"
    report_md = out_dir / "BRODY_READONLY_SESSION_TEST_REPORT.md"

    session_plan = {
        "session_test_plan": [
            "READ scheduler validation pointer",
            "READ scheduler next session prompt",
            "READ session reopen context packet",
            "ASSERT memory remains non-decision",
            "ASSERT X108 remains sole decision authority",
            "ALLOW human to start next Brody readonly session",
        ],
        "inputs": {
            "scheduler_pointer": str(scheduler_ptr),
            "reopen_pointer": str(reopen_ptr),
            "micro_smoke_pointer": str(micro_ptr),
            "close_pointer": str(close_ptr),
        },
        **BOUNDARY,
    }

    checks_json.write_text(json.dumps(checks, indent=2, ensure_ascii=False), encoding="utf-8")
    session_plan_json.write_text(json.dumps(session_plan, indent=2, ensure_ascii=False), encoding="utf-8")

    session_prompt_lines = [
        "# BRODY READONLY SESSION TEST PROMPT",
        "",
        "Session can reopen from existing readonly memory artifacts.",
        "",
        "Use:",
        f"- Scheduler prompt: `{scheduler_prompt_md}`",
        f"- Reopen prompt context: `{prompt_context_md}`",
        f"- Context packet: `{context_packet_json}`",
        "",
        "Boundary:",
        "- MEMORY_DECISION=false",
        "- ALLOWED_TO_DECIDE=false",
        "- EMITS_ACT=false",
        "- EMITS_VERDICT=false",
        "- DECISION_AUTHORITY=KX108_ONLY",
        "- KERNEL_MUTATION=false",
        "- X108_RUNTIME_BINDING=false",
        "- X108_MERGE=false",
        "- GRAPHITI_INDEX_WRITE=false",
        "- NEO4J_WRITE_EXECUTED=false",
        "- MEMORY_INTAKE=false",
        "",
        "Next:",
        "COMMIT_BRODY_READONLY_SESSION_TEST_V1_THEN_DECIDE_BRODY_AGENT_TEST_OR_SCHEDULER_V2",
    ]
    session_prompt_md.write_text("\n".join(session_prompt_lines), encoding="utf-8")

    summary = {
        "status": "BRODY_READONLY_SESSION_TEST_V1_PASS" if session_test_ok else "BRODY_READONLY_SESSION_TEST_V1_FAIL",
        "created_at": now_iso(),
        "check_count": len(checks),
        "passed_check_count": len([c for c in checks if c["passed"]]),
        "failed_check_count": len(failed),
        "failed_checks": failed,
        "scheduler_status": scheduler_summary.get("status"),
        "reopen_status": reopen_summary.get("status"),
        "micro_smoke_status": micro_summary.get("status"),
        "close_status": close_summary.get("status"),
        "schedule_record_count": scheduler_summary.get("schedule_record_count"),
        "context_packet_record_count": reopen_summary.get("context_packet_record_count"),
        "session_test_ok": session_test_ok,
        "latest_session_test_event_hash": prev,
        "outputs": {
            "checks_json": str(checks_json),
            "session_plan_json": str(session_plan_json),
            "session_prompt_md": str(session_prompt_md),
            "summary_json": str(summary_json),
            "report_md": str(report_md),
        },
        "next": "COMMIT_BRODY_READONLY_SESSION_TEST_V1_THEN_DECIDE_BRODY_AGENT_TEST_OR_SCHEDULER_V2",
        **BOUNDARY,
    }

    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# BRODY READONLY SESSION TEST V1",
        "",
        f"- status: {summary['status']}",
        f"- check_count: {summary['check_count']}",
        f"- passed_check_count: {summary['passed_check_count']}",
        f"- failed_check_count: {summary['failed_check_count']}",
        f"- schedule_record_count: {summary['schedule_record_count']}",
        f"- context_packet_record_count: {summary['context_packet_record_count']}",
        f"- session_test_ok: {str(summary['session_test_ok']).lower()}",
        "",
        "## Boundary",
        "",
        "- File read only: true.",
        "- Graphiti query read: false.",
        "- Graphiti write: false.",
        "- Neo4j write: false.",
        "- Memory intake: false.",
        "- Memory decision: false.",
        "- X108 mutation: false.",
        "- Kernel mutation: false.",
        "",
        "## Next",
        "",
        summary["next"],
    ]

    report_md.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))

    if not session_test_ok:
        raise SystemExit("BRODY_READONLY_SESSION_TEST_FAILED")

if __name__ == "__main__":
    main()
