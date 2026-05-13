import argparse
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

BOUNDARY = {
    "readonly": True,
    "response_only": True,
    "memory_scheduler": True,
    "scheduler_registers_background_task": False,
    "automatic_execution": False,
    "cron_registered": False,
    "requires_human_trigger": True,
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
    "brody_role": "MEMORY_SCHEDULER_READONLY",
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

def write_jsonl(path: Path, rows):
    with path.open("w", encoding="utf-8", errors="ignore") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

def assert_bool(obj, key, expected):
    if obj.get(key) is not expected:
        raise RuntimeError(f"BAD_{key.upper()}={obj.get(key)}")

def assert_int(obj, key, expected):
    if int(obj.get(key, -1)) != expected:
        raise RuntimeError(f"BAD_{key.upper()}={obj.get(key)}")

def make_schedule_records(close_summary, smoke_summary, reopen_summary, freeze_summary):
    records = [
        {
            "id": "BRODY_SCHEDULER_STEP_01_SESSION_START_READ_CONTEXT",
            "trigger": "MANUAL_SESSION_START",
            "purpose": "Open latest Brody memory context packet before new work session.",
            "source": "BRODY_SESSION_REOPEN_LOOP_READONLY_V1",
            "required_pointer": "CURRENT_BRODY_SESSION_REOPEN_LOOP_READONLY_V1_VALIDATE.txt",
            "required_status": "BRODY_SESSION_REOPEN_LOOP_READONLY_V1_PASS",
            "action_allowed": "READ_CONTEXT_PACKET_ONLY",
            "writes": False,
        },
        {
            "id": "BRODY_SCHEDULER_STEP_02_PRE_SESSION_MICRO_SMOKE",
            "trigger": "MANUAL_BEFORE_MEMORY_WORK",
            "purpose": "Verify memory-only records are still readable before depending on them.",
            "source": "BRODY_MEMORY_READONLY_MICRO_SMOKE_V1",
            "required_pointer": "CURRENT_BRODY_MEMORY_READONLY_MICRO_SMOKE_V1_VALIDATE.txt",
            "required_status": "BRODY_MEMORY_READONLY_MICRO_SMOKE_V1_PASS",
            "action_allowed": "READONLY_SMOKE_ONLY",
            "writes": False,
        },
        {
            "id": "BRODY_SCHEDULER_STEP_03_SESSION_REOPEN_LOOP",
            "trigger": "MANUAL_NEW_SESSION_REOPEN",
            "purpose": "Regenerate prompt context and context packet from frozen memory-only records.",
            "source": "BRODY_SESSION_REOPEN_LOOP_READONLY_V1",
            "required_pointer": "CURRENT_BRODY_SESSION_REOPEN_LOOP_READONLY_V1_VALIDATE.txt",
            "required_status": "BRODY_SESSION_REOPEN_LOOP_READONLY_V1_PASS",
            "action_allowed": "READONLY_REOPEN_ONLY",
            "writes": False,
        },
        {
            "id": "BRODY_SCHEDULER_STEP_04_AFTER_MEMORY_APPLY_VERIFY",
            "trigger": "ONLY_IF_MANUAL_MEMORY_ONLY_APPLY_EXECUTED",
            "purpose": "If a guarded manual memory-only apply happens, verify applied IDs before any close report.",
            "source": "BRODY_POST_GRAPHITI_APPLY_VERIFY_READONLY_V1",
            "required_pointer": "CURRENT_BRODY_POST_GRAPHITI_APPLY_VERIFY_READONLY_V1_VALIDATE.txt",
            "required_status": "BRODY_POST_GRAPHITI_APPLY_VERIFY_READONLY_V1_PASS",
            "action_allowed": "READONLY_VERIFY_ONLY",
            "writes": False,
        },
        {
            "id": "BRODY_SCHEDULER_STEP_05_REPLAY_REGRESSION",
            "trigger": "AFTER_APPLY_VERIFY_OR_BEFORE_FREEZE",
            "purpose": "Replay exact IDs and query retrieval to prove records are retrievable, not only present.",
            "source": "BRODY_POST_GRAPHITI_REPLAY_QUERY_REGRESSION_READONLY_V1",
            "required_pointer": "CURRENT_BRODY_POST_GRAPHITI_REPLAY_QUERY_REGRESSION_READONLY_V1_VALIDATE.txt",
            "required_status": "BRODY_POST_GRAPHITI_REPLAY_QUERY_REGRESSION_READONLY_V1_PASS",
            "action_allowed": "READONLY_REPLAY_ONLY",
            "writes": False,
        },
        {
            "id": "BRODY_SCHEDULER_STEP_06_CLOSE_OR_FREEZE",
            "trigger": "MANUAL_AFTER_PIPELINE_CHANGE",
            "purpose": "Close the Brody memory pipeline after validated readonly replay and freeze checks.",
            "source": "BRODY_MEMORY_PIPELINE_V2_CLOSE_REPORT_READONLY",
            "required_pointer": "CURRENT_BRODY_MEMORY_PIPELINE_V2_CLOSE_REPORT_READONLY_VALIDATE.txt",
            "required_status": "BRODY_MEMORY_PIPELINE_V2_CLOSE_REPORT_READONLY_PASS",
            "action_allowed": "READONLY_CLOSE_REPORT_ONLY",
            "writes": False,
        },
    ]

    prev = "GENESIS_BRODY_MEMORY_SCHEDULER_READONLY_V1"

    for idx, record in enumerate(records, start=1):
        record["index"] = idx
        record["created_at"] = now_iso()
        record["human_trigger_required"] = True
        record["automatic_execution"] = False
        record["cron_registered"] = False
        record["graphiti_index_write"] = False
        record["neo4j_write_executed"] = False
        record["memory_intake"] = False
        record["memory_decision"] = False
        record["allowed_to_decide"] = False
        record["emits_act"] = False
        record["emits_verdict"] = False
        record["decision_authority"] = "KX108_ONLY"
        record["kernel_mutation"] = False
        record["x108_runtime_binding"] = False
        record["x108_merge"] = False

        seed = json.dumps({"prev": prev, "record": record}, ensure_ascii=False, sort_keys=True)
        record["prev_event_hash"] = prev
        record["event_hash"] = sha256_text(seed)
        prev = record["event_hash"]

    return records, prev

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[3]
    workspace_root = repo_root.parent

    close_ptr = workspace_root / "CURRENT_BRODY_MEMORY_PIPELINE_V2_CLOSE_REPORT_READONLY_VALIDATE.txt"
    smoke_ptr = workspace_root / "CURRENT_BRODY_MEMORY_READONLY_MICRO_SMOKE_V1_VALIDATE.txt"
    reopen_ptr = workspace_root / "CURRENT_BRODY_SESSION_REOPEN_LOOP_READONLY_V1_VALIDATE.txt"
    freeze_ptr = workspace_root / "CURRENT_BRODY_MEMORY_PIPELINE_FREEZE_V2_READONLY_VALIDATE.txt"

    required_ptrs = [close_ptr, smoke_ptr, reopen_ptr, freeze_ptr]

    missing_ptrs = [str(p) for p in required_ptrs if not p.exists()]
    if missing_ptrs:
        raise RuntimeError(f"MISSING_REQUIRED_POINTERS={missing_ptrs}")

    close_kv = parse_pointer(close_ptr)
    smoke_kv = parse_pointer(smoke_ptr)
    reopen_kv = parse_pointer(reopen_ptr)
    freeze_kv = parse_pointer(freeze_ptr)

    close_summary_json = Path(close_kv.get("SUMMARY_JSON", ""))
    smoke_summary_json = Path(smoke_kv.get("SUMMARY_JSON", ""))
    reopen_summary_json = Path(reopen_kv.get("SUMMARY_JSON", ""))
    freeze_summary_json = Path(freeze_kv.get("SUMMARY_JSON", ""))

    required_jsons = [close_summary_json, smoke_summary_json, reopen_summary_json, freeze_summary_json]
    missing_jsons = [str(p) for p in required_jsons if not p.exists()]
    if missing_jsons:
        raise RuntimeError(f"MISSING_REQUIRED_SUMMARIES={missing_jsons}")

    close_summary = load_json(close_summary_json)
    smoke_summary = load_json(smoke_summary_json)
    reopen_summary = load_json(reopen_summary_json)
    freeze_summary = load_json(freeze_summary_json)

    if close_summary.get("status") != "BRODY_MEMORY_PIPELINE_V2_CLOSE_REPORT_READONLY_PASS":
        raise RuntimeError(f"BAD_CLOSE_STATUS={close_summary.get('status')}")
    if smoke_summary.get("status") != "BRODY_MEMORY_READONLY_MICRO_SMOKE_V1_PASS":
        raise RuntimeError(f"BAD_SMOKE_STATUS={smoke_summary.get('status')}")
    if reopen_summary.get("status") != "BRODY_SESSION_REOPEN_LOOP_READONLY_V1_PASS":
        raise RuntimeError(f"BAD_REOPEN_STATUS={reopen_summary.get('status')}")
    if freeze_summary.get("status") != "BRODY_MEMORY_PIPELINE_FREEZE_V2_READONLY_PASS":
        raise RuntimeError(f"BAD_FREEZE_STATUS={freeze_summary.get('status')}")

    assert_bool(close_summary, "close_ok", True)
    assert_bool(smoke_summary, "micro_smoke_ok", True)
    assert_bool(reopen_summary, "reopen_loop_ok", True)
    assert_bool(freeze_summary, "freeze_ok", True)

    assert_int(close_summary, "manual_apply_write_executed_count", 29)
    assert_int(smoke_summary, "exact_found_count", 29)
    assert_int(reopen_summary, "exact_found_count", 29)
    assert_int(freeze_summary, "manual_apply_write_executed_count", 29)

    schedule_records, latest_hash = make_schedule_records(
        close_summary,
        smoke_summary,
        reopen_summary,
        freeze_summary,
    )

    scheduler_ok = (
        len(schedule_records) == 6
        and close_summary.get("close_ok") is True
        and smoke_summary.get("micro_smoke_ok") is True
        and reopen_summary.get("reopen_loop_ok") is True
        and freeze_summary.get("freeze_ok") is True
    )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    schedule_jsonl = out_dir / "BRODY_MEMORY_SCHEDULER_PLAN_READONLY.jsonl"
    schedule_json = out_dir / "BRODY_MEMORY_SCHEDULER_PLAN_READONLY.json"
    prompt_md = out_dir / "BRODY_MEMORY_SCHEDULER_NEXT_SESSION_PROMPT.md"
    summary_json = out_dir / "BRODY_MEMORY_SCHEDULER_READONLY_SUMMARY.json"
    report_md = out_dir / "BRODY_MEMORY_SCHEDULER_READONLY_REPORT.md"

    write_jsonl(schedule_jsonl, schedule_records)
    schedule_json.write_text(json.dumps(schedule_records, indent=2, ensure_ascii=False), encoding="utf-8")

    prompt_lines = [
        "# BRODY MEMORY SCHEDULER — NEXT SESSION PROMPT",
        "",
        "Use this as readonly session reopen protocol.",
        "",
        "1. Load `CURRENT_BRODY_SESSION_REOPEN_LOOP_READONLY_V1_VALIDATE.txt`.",
        "2. Read `BRODY_SESSION_REOPEN_PROMPT_CONTEXT.md`.",
        "3. Run micro smoke if memory context is needed.",
        "4. Do not write Graphiti unless guarded manual apply token is explicitly used.",
        "5. Do not mutate X108.",
        "6. Do not let memory decide.",
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
    ]
    prompt_md.write_text("\n".join(prompt_lines), encoding="utf-8")

    summary = {
        "status": "BRODY_MEMORY_SCHEDULER_READONLY_V1_PASS" if scheduler_ok else "BRODY_MEMORY_SCHEDULER_READONLY_V1_FAIL",
        "created_at": now_iso(),
        "source_close_pointer": str(close_ptr),
        "source_close_summary_json": str(close_summary_json),
        "source_micro_smoke_pointer": str(smoke_ptr),
        "source_micro_smoke_summary_json": str(smoke_summary_json),
        "source_session_reopen_pointer": str(reopen_ptr),
        "source_session_reopen_summary_json": str(reopen_summary_json),
        "source_freeze_v2_pointer": str(freeze_ptr),
        "source_freeze_v2_summary_json": str(freeze_summary_json),
        "schedule_record_count": len(schedule_records),
        "close_report_ok": close_summary.get("close_ok"),
        "micro_smoke_ok": smoke_summary.get("micro_smoke_ok"),
        "session_reopen_ok": reopen_summary.get("reopen_loop_ok"),
        "freeze_v2_ok": freeze_summary.get("freeze_ok"),
        "manual_apply_write_executed_count": int(close_summary.get("manual_apply_write_executed_count", 0)),
        "micro_smoke_exact_found_count": int(smoke_summary.get("exact_found_count", 0)),
        "session_reopen_context_packet_record_count": int(reopen_summary.get("context_packet_record_count", 0)),
        "scheduler_ok": scheduler_ok,
        "latest_scheduler_event_hash": latest_hash,
        "outputs": {
            "schedule_jsonl": str(schedule_jsonl),
            "schedule_json": str(schedule_json),
            "prompt_md": str(prompt_md),
            "summary_json": str(summary_json),
            "report_md": str(report_md),
        },
        "next": "COMMIT_BRODY_MEMORY_SCHEDULER_READONLY_V1_THEN_RUN_BRODY_READONLY_SESSION_TEST",
        **BOUNDARY,
    }

    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# BRODY MEMORY SCHEDULER READONLY V1",
        "",
        f"- status: {summary['status']}",
        f"- schedule_record_count: {summary['schedule_record_count']}",
        f"- close_report_ok: {str(summary['close_report_ok']).lower()}",
        f"- micro_smoke_ok: {str(summary['micro_smoke_ok']).lower()}",
        f"- session_reopen_ok: {str(summary['session_reopen_ok']).lower()}",
        f"- freeze_v2_ok: {str(summary['freeze_v2_ok']).lower()}",
        f"- manual_apply_write_executed_count: {summary['manual_apply_write_executed_count']}",
        f"- session_reopen_context_packet_record_count: {summary['session_reopen_context_packet_record_count']}",
        f"- scheduler_ok: {str(summary['scheduler_ok']).lower()}",
        "",
        "## Boundary",
        "",
        "- No background task registered.",
        "- No cron registered.",
        "- No automatic execution.",
        "- Human trigger required.",
        "- Graphiti write: false.",
        "- Neo4j write: false.",
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

    if not scheduler_ok:
        raise SystemExit("BRODY_MEMORY_SCHEDULER_READONLY_FAILED")

if __name__ == "__main__":
    main()
