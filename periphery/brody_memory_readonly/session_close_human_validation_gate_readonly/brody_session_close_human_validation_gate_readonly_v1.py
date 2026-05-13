import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

BOUNDARY = {
    "readonly": True,
    "response_only": True,
    "session_close_gate": True,
    "human_validation_required": True,
    "human_decision_pending": True,
    "canonical_pointer_records": True,
    "uses_project_intake_scan": False,
    "support_pointer_fallback": True,
    "graphiti_index_write": False,
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
    "brody_role": "SESSION_CLOSE_HUMAN_VALIDATION_GATE_READONLY",
    "memory_role": "GUIDE_CONTEXT_NAVIGATION_ONLY",
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def parse_kv(path: Path) -> dict:
    kv = {}
    text = path.read_text(encoding="utf-8-sig", errors="ignore")
    for line in text.splitlines():
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip().lstrip("\ufeff")
        v = v.strip()
        if k:
            kv[k] = v
    return kv


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig", errors="ignore"))


def stage_map_from_summary(summary: dict):
    mapping = {}
    for stage in summary.get("stages", []):
        stage_name = stage.get("stage")
        for p in stage.get("pointers", []) or []:
            mapping[str(p)] = stage_name
    return mapping


def pointer_role(record: dict):
    name = str(record.get("name", "")).upper()
    keys = record.get("keys", {}) or {}
    status = str(keys.get("STATUS", "")).upper()
    next_value = str(keys.get("NEXT", "")).upper()

    if "FAILED" in name or "FAILED" in status:
        return "REFLEX_REVIEW"
    if "VALIDATE" in name or "PASS" in status:
        return "KEEP_EVIDENCE_REVIEW"
    if "REMOTE_CLOSE" in name or "REMOTE_SYNC" in keys:
        return "KEEP_REMOTE_SYNC_REVIEW"
    if "CURRENT_BRODY_MEMORY_PIPELINE" in name or "FREEZE" in name:
        return "KEEP_FREEZE_REVIEW"
    if "GRAPHITI_IMPORT_APPLY" in name:
        return "TRANSITION_APPLY_REVIEW"
    if "NEXT" in keys or next_value:
        return "TRANSITION_NEXT_STEP_REVIEW"
    return "STANDARD_POINTER_REVIEW"


def proposed_decision(record: dict):
    role = pointer_role(record)
    if role == "REFLEX_REVIEW":
        return "REFLEX"
    if role in {"TRANSITION_APPLY_REVIEW", "TRANSITION_NEXT_STEP_REVIEW"}:
        return "TRANSITION"
    return "KEEP"


def infer_support_stage(record: dict):
    name = str(record.get("name", "")).upper()
    keys = record.get("keys", {}) or {}
    status = str(keys.get("STATUS", "")).upper()
    next_value = str(keys.get("NEXT", "")).upper()

    if "FAILED" in name or "FAILED" in status:
        return "SUPPORT_FAILED_TRACE_POINTER"

    if "MEMORY_GUIDE_SCOPE_REALIGN" in name:
        return "SUPPORT_SCOPE_REALIGN_POINTER"

    if "GRAPHITI_READY" in name or "GRAPHITI_TAXONOMY" in name or "TAXONOMY" in name:
        return "SUPPORT_GRAPHITI_TAXONOMY_POINTER"

    if "CURRENT_GRAPHITI" in name:
        return "SUPPORT_GRAPHITI_INDEX_POINTER"

    if "PIPELINE" in name or "FREEZE" in name:
        return "SUPPORT_FREEZE_PIPELINE_POINTER"

    if "BRODY_OBSIDIEN" in name:
        return "SUPPORT_BRODY_OBSIDIEN_POINTER"

    if next_value:
        return "SUPPORT_NEXT_STEP_POINTER"

    return "SUPPORT_POINTER_OUTSIDE_14_STAGE_FREEZE"

def make_queue_record(record: dict, index: int, prev_hash: str, stage_mapping: dict):
    path = record.get("path")
    name = record.get("name")
    keys = record.get("keys", {}) or {}
    stage = stage_mapping.get(path)
    if not stage:
        stage = infer_support_stage(record)

    base = {
        "index": index,
        "canonical_source": "BRODY_MEMORY_PIPELINE_POINTER_RECORDS",
        "source": "PIPELINE_FREEZE_REPORT_POINTER_RECORDS",
        "stage": stage,
        "pointer_path": path,
        "pointer_name": name,
        "pointer_sha256": record.get("sha256"),
        "status_key": keys.get("STATUS"),
        "next_key": keys.get("NEXT"),
        "review_lane": pointer_role(record),
        "suggested_human_decision": proposed_decision(record),
        "human_question": "KEEP / TRANSITION / NEANT / REFLEX ?",
        "human_decision": "PENDING",
        "human_reason": "",
        "pending_zone": "PENDING_HUMAN_REVIEW",
        "learning_state": "PENDING_NOT_CANON",
        "created_at": now_iso(),
        **BOUNDARY,
    }

    seed = json.dumps(
        {
            "prev": prev_hash,
            "canonical_source": base["canonical_source"],
            "stage": stage,
            "path": path,
            "sha256": record.get("sha256"),
            "review_lane": base["review_lane"],
            "suggested_human_decision": base["suggested_human_decision"],
        },
        ensure_ascii=False,
        sort_keys=True,
    )

    base["prev_event_hash"] = prev_hash
    base["event_hash"] = sha256_text(seed)
    return base


def write_jsonl(path: Path, rows):
    with path.open("w", encoding="utf-8", errors="ignore") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    freeze_ptr = workspace_root / "CURRENT_BRODY_MEMORY_PIPELINE_READONLY_FREEZE_REPORT_V1_VALIDATE.txt"
    if not freeze_ptr.exists():
        raise RuntimeError(f"MISSING_FREEZE_VALIDATE_POINTER={freeze_ptr}")

    freeze_kv = parse_kv(freeze_ptr)

    pointer_records_json = Path(freeze_kv.get("POINTER_RECORDS_JSON", ""))
    freeze_summary_json = Path(freeze_kv.get("SUMMARY_JSON", ""))

    if not pointer_records_json.exists():
        raise RuntimeError(f"MISSING_POINTER_RECORDS_JSON={pointer_records_json}")
    if not freeze_summary_json.exists():
        raise RuntimeError(f"MISSING_FREEZE_SUMMARY_JSON={freeze_summary_json}")

    pointer_records = load_json(pointer_records_json)
    freeze_summary = load_json(freeze_summary_json)

    if not isinstance(pointer_records, list):
        raise RuntimeError("POINTER_RECORDS_JSON_NOT_LIST")

    stage_mapping = stage_map_from_summary(freeze_summary)

    queue = []
    prev = "GENESIS_BRODY_SESSION_CLOSE_HUMAN_VALIDATION_GATE_READONLY_V1_3_CANONICAL_POINTER_RECORDS_SUPPORT_FALLBACK"

    for record in pointer_records[: args.limit]:
        row = make_queue_record(record, len(queue) + 1, prev, stage_mapping)
        prev = row["event_hash"]
        queue.append(row)

    lane_counts = {}
    stage_counts = {}
    decision_counts = {}
    unmapped_count = 0

    for row in queue:
        lane_counts[row["review_lane"]] = lane_counts.get(row["review_lane"], 0) + 1
        stage_counts[row["stage"]] = stage_counts.get(row["stage"], 0) + 1
        decision_counts[row["suggested_human_decision"]] = decision_counts.get(row["suggested_human_decision"], 0) + 1
        if row["stage"] == "UNMAPPED_POINTER_RECORD":
            unmapped_count += 1

    queue_jsonl = out_dir / "BRODY_SESSION_CLOSE_HUMAN_VALIDATION_QUEUE.jsonl"
    queue_json = out_dir / "BRODY_SESSION_CLOSE_HUMAN_VALIDATION_QUEUE.json"
    checklist_md = out_dir / "BRODY_SESSION_CLOSE_HUMAN_VALIDATION_CHECKLIST.md"
    summary_json = out_dir / "BRODY_SESSION_CLOSE_HUMAN_VALIDATION_SUMMARY.json"
    report_md = out_dir / "BRODY_SESSION_CLOSE_HUMAN_VALIDATION_REPORT.md"

    write_jsonl(queue_jsonl, queue)
    queue_json.write_text(json.dumps(queue, indent=2, ensure_ascii=False), encoding="utf-8")

    checklist_lines = [
        "# BRODY SESSION CLOSE - HUMAN VALIDATION CHECKLIST",
        "",
        "Source: BRODY_MEMORY_PIPELINE_POINTER_RECORDS",
        "",
        "Decision codes:",
        "",
        "- KEEP = memory candidate / keep as evidence",
        "- TRANSITION = review later / next-step candidate",
        "- NEANT = reject / do not keep",
        "- REFLEX = alert / weak signal / failed trace",
        "",
        "Nothing below is canon until manually validated.",
        "Nothing writes Graphiti from this gate.",
        "",
    ]

    for row in queue:
        checklist_lines += [
            f"## {row['index']}. {row.get('pointer_name')}",
            "",
            f"- stage: `{row.get('stage')}`",
            f"- lane: `{row.get('review_lane')}`",
            f"- suggested: `{row.get('suggested_human_decision')}`",
            f"- status: `{row.get('status_key')}`",
            f"- path: `{row.get('pointer_path')}`",
            f"- question: **{row.get('human_question')}**",
            "- decision: `[ ] KEEP  [ ] TRANSITION  [ ] NEANT  [ ] REFLEX`",
            "- reason:",
            "",
        ]

    checklist_md.write_text("\n".join(checklist_lines), encoding="utf-8")

    summary = {
        "status": "BRODY_SESSION_CLOSE_HUMAN_VALIDATION_GATE_READONLY_V1_PASS",
        "patch": "V1_3_CANONICAL_POINTER_RECORDS_SUPPORT_FALLBACK",
        "created_at": now_iso(),
        "workspace_root": str(workspace_root),
        "freeze_validate_pointer": str(freeze_ptr),
        "pointer_records_json": str(pointer_records_json),
        "freeze_summary_json": str(freeze_summary_json),
        "pipeline_stage_count": freeze_summary.get("pipeline_stage_count"),
        "pipeline_stage_found_count": freeze_summary.get("pipeline_stage_found_count"),
        "pipeline_stage_missing_count": freeze_summary.get("pipeline_stage_missing_count"),
        "canonical_pointer_record_count": len(pointer_records),
        "queue_count": len(queue),
        "lane_counts": lane_counts,
        "stage_counts": stage_counts,
        "suggested_human_decision_counts": decision_counts,
        "unmapped_pointer_count": unmapped_count,
        "latest_event_hash": prev,
        "outputs": {
            "queue_jsonl": str(queue_jsonl),
            "queue_json": str(queue_json),
            "checklist_md": str(checklist_md),
            "summary_json": str(summary_json),
            "report_md": str(report_md),
        },
        "next": "HUMAN_REVIEW_THEN_BUILD_BRODY_SESSION_CLOSE_DECISION_APPLY_READONLY_V1",
        **BOUNDARY,
    }

    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    report_lines = [
        "# BRODY SESSION CLOSE HUMAN VALIDATION GATE READONLY V1",
        "",
        f"- status: {summary['status']}",
        f"- patch: {summary['patch']}",
        f"- canonical_pointer_record_count: {summary['canonical_pointer_record_count']}",
        f"- queue_count: {summary['queue_count']}",
        f"- unmapped_pointer_count: {summary['unmapped_pointer_count']}",
        f"- latest_event_hash: {summary['latest_event_hash']}",
        "",
        "## Boundary",
        "",
        "- Canonical pointer records: true",
        "- Uses project intake scan: false",
        "- Human validation required: true",
        "- Human decision pending: true",
        "- Graphiti write: false",
        "- Memory intake: false",
        "- Memory decision: false",
        "- Emits ACT: false",
        "- Emits verdict: false",
        "- Kernel mutation: false",
        "- X108 runtime binding: false",
        "- X108 merge: false",
        "",
        "## Next",
        "",
        summary["next"],
    ]

    report_md.write_text("\n".join(report_lines), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

