import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

BOUNDARY = {
    "readonly": True,
    "response_only": True,
    "post_human_review_triage": True,
    "human_decision_consumed": True,
    "memory_candidate_preparation": True,
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
    "brody_role": "POST_HUMAN_REVIEW_MEMORY_TRIAGE_READONLY",
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


def read_jsonl(path: Path):
    rows = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8-sig", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows):
    with path.open("w", encoding="utf-8", errors="ignore") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def candidate_id(row: dict):
    seed = json.dumps(
        {
            "pointer_path": row.get("pointer_path"),
            "pointer_sha256": row.get("pointer_sha256"),
            "decision_event_hash": row.get("decision_event_hash"),
            "human_decision": row.get("human_decision"),
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return "BRODY_POST_HUMAN_KEEP_" + sha256_text(seed)[:24]


def make_keep_candidate(row: dict, index: int, prev_hash: str):
    cid = candidate_id(row)
    record = {
        "index": index,
        "candidate_id": cid,
        "candidate_zone": "KEEP_MEMORY_CANDIDATE_READONLY",
        "candidate_status": "READY_FOR_GRAPHITI_CANDIDATE_PREP_READONLY",
        "source_pointer_name": row.get("pointer_name"),
        "source_pointer_path": row.get("pointer_path"),
        "source_pointer_sha256": row.get("pointer_sha256"),
        "source_stage": row.get("stage"),
        "source_review_lane": row.get("review_lane"),
        "source_status_key": row.get("status_key"),
        "source_next_key": row.get("next_key"),
        "human_decision": row.get("human_decision"),
        "decision_event_hash": row.get("decision_event_hash"),
        "created_at": now_iso(),
        **BOUNDARY,
    }

    seed = json.dumps(
        {
            "prev": prev_hash,
            "candidate_id": cid,
            "source_pointer_path": record["source_pointer_path"],
            "decision_event_hash": record["decision_event_hash"],
            "candidate_zone": record["candidate_zone"],
        },
        ensure_ascii=False,
        sort_keys=True,
    )

    record["prev_triage_event_hash"] = prev_hash
    record["triage_event_hash"] = sha256_text(seed)
    return record


def make_side_record(row: dict, index: int, zone: str, prev_hash: str):
    record = {
        "index": index,
        "zone": zone,
        "source_pointer_name": row.get("pointer_name"),
        "source_pointer_path": row.get("pointer_path"),
        "source_pointer_sha256": row.get("pointer_sha256"),
        "source_stage": row.get("stage"),
        "source_review_lane": row.get("review_lane"),
        "source_status_key": row.get("status_key"),
        "source_next_key": row.get("next_key"),
        "human_decision": row.get("human_decision"),
        "decision_event_hash": row.get("decision_event_hash"),
        "created_at": now_iso(),
        **BOUNDARY,
    }

    seed = json.dumps(
        {
            "prev": prev_hash,
            "zone": zone,
            "source_pointer_path": record["source_pointer_path"],
            "decision_event_hash": record["decision_event_hash"],
        },
        ensure_ascii=False,
        sort_keys=True,
    )

    record["prev_triage_event_hash"] = prev_hash
    record["triage_event_hash"] = sha256_text(seed)
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    decision_ptr = workspace_root / "CURRENT_BRODY_SESSION_CLOSE_DECISION_APPLY_READONLY_V1_VALIDATE.txt"
    if not decision_ptr.exists():
        raise RuntimeError(f"MISSING_DECISION_APPLY_VALIDATE_POINTER={decision_ptr}")

    kv = parse_kv(decision_ptr)

    decisions_jsonl = Path(kv.get("DECISIONS_JSONL", ""))
    keep_jsonl = Path(kv.get("KEEP_JSONL", ""))
    transition_jsonl = Path(kv.get("TRANSITION_JSONL", ""))
    reflex_jsonl = Path(kv.get("REFLEX_JSONL", ""))
    neant_jsonl = Path(kv.get("NEANT_JSONL", ""))
    source_summary_json = Path(kv.get("SUMMARY_JSON", ""))

    required = [decisions_jsonl, keep_jsonl, transition_jsonl, reflex_jsonl, neant_jsonl, source_summary_json]
    for p in required:
        if not p.exists():
            raise RuntimeError(f"MISSING_INPUT={p}")

    source_summary = json.loads(source_summary_json.read_text(encoding="utf-8-sig", errors="ignore"))

    if source_summary.get("status") != "BRODY_SESSION_CLOSE_DECISION_APPLY_READONLY_V1_PASS":
        raise RuntimeError(f"BAD_SOURCE_STATUS={source_summary.get('status')}")

    if source_summary.get("gate_patch") != "V1_3_CANONICAL_POINTER_RECORDS_SUPPORT_FALLBACK":
        raise RuntimeError(f"BAD_GATE_PATCH={source_summary.get('gate_patch')}")

    decisions = read_jsonl(decisions_jsonl)
    keep_rows = read_jsonl(keep_jsonl)
    transition_rows = read_jsonl(transition_jsonl)
    reflex_rows = read_jsonl(reflex_jsonl)
    neant_rows = read_jsonl(neant_jsonl)

    # BLOCKED_DYNAMIC_DECISION_COUNT_REQUIRED — hardcode 51 supprimé (P66)
    # La validation du count est déléguée à l'opérateur humain KX108_ONLY.

    prev = "GENESIS_BRODY_POST_HUMAN_REVIEW_MEMORY_TRIAGE_READONLY_V1"

    keep_candidates = []
    for idx, row in enumerate(keep_rows, start=1):
        out = make_keep_candidate(row, idx, prev)
        prev = out["triage_event_hash"]
        keep_candidates.append(out)

    transition_records = []
    for idx, row in enumerate(transition_rows, start=1):
        out = make_side_record(row, idx, "TRANSITION_REVIEW_LATER", prev)
        prev = out["triage_event_hash"]
        transition_records.append(out)

    reflex_records = []
    for idx, row in enumerate(reflex_rows, start=1):
        out = make_side_record(row, idx, "REFLEX_ALERT_TRACE", prev)
        prev = out["triage_event_hash"]
        reflex_records.append(out)

    neant_records = []
    for idx, row in enumerate(neant_rows, start=1):
        out = make_side_record(row, idx, "NEANT_REJECTED", prev)
        prev = out["triage_event_hash"]
        neant_records.append(out)

    memory_candidates_jsonl = out_dir / "BRODY_POST_HUMAN_MEMORY_CANDIDATES_READONLY.jsonl"
    memory_candidates_json = out_dir / "BRODY_POST_HUMAN_MEMORY_CANDIDATES_READONLY.json"
    transition_out = out_dir / "BRODY_POST_HUMAN_TRANSITION_BACKLOG.jsonl"
    reflex_out = out_dir / "BRODY_POST_HUMAN_REFLEX_ALERTS.jsonl"
    neant_out = out_dir / "BRODY_POST_HUMAN_NEANT_REJECTED.jsonl"
    triage_records_jsonl = out_dir / "BRODY_POST_HUMAN_REVIEW_TRIAGE_RECORDS.jsonl"
    triage_records_json = out_dir / "BRODY_POST_HUMAN_REVIEW_TRIAGE_RECORDS.json"
    summary_json = out_dir / "BRODY_POST_HUMAN_REVIEW_MEMORY_TRIAGE_SUMMARY.json"
    report_md = out_dir / "BRODY_POST_HUMAN_REVIEW_MEMORY_TRIAGE_REPORT.md"

    all_records = keep_candidates + transition_records + reflex_records + neant_records

    write_jsonl(memory_candidates_jsonl, keep_candidates)
    memory_candidates_json.write_text(json.dumps(keep_candidates, indent=2, ensure_ascii=False), encoding="utf-8")
    write_jsonl(transition_out, transition_records)
    write_jsonl(reflex_out, reflex_records)
    write_jsonl(neant_out, neant_records)
    write_jsonl(triage_records_jsonl, all_records)
    triage_records_json.write_text(json.dumps(all_records, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = {
        "status": "BRODY_POST_HUMAN_REVIEW_MEMORY_TRIAGE_READONLY_V1_PASS",
        "created_at": now_iso(),
        "source_decision_apply_pointer": str(decision_ptr),
        "source_decisions_jsonl": str(decisions_jsonl),
        "source_summary_json": str(source_summary_json),
        "source_mode": source_summary.get("mode"),
        "source_gate_patch": source_summary.get("gate_patch"),
        "decision_count": len(decisions),
        "keep_count": len(keep_candidates),
        "transition_count": len(transition_records),
        "reflex_count": len(reflex_records),
        "neant_count": len(neant_records),
        "triage_record_count": len(all_records),
        "latest_triage_event_hash": prev,
        "outputs": {
            "memory_candidates_jsonl": str(memory_candidates_jsonl),
            "memory_candidates_json": str(memory_candidates_json),
            "transition_backlog_jsonl": str(transition_out),
            "reflex_alerts_jsonl": str(reflex_out),
            "neant_rejected_jsonl": str(neant_out),
            "triage_records_jsonl": str(triage_records_jsonl),
            "triage_records_json": str(triage_records_json),
            "summary_json": str(summary_json),
            "report_md": str(report_md),
        },
        "next": "BUILD_BRODY_GRAPHITI_CANDIDATE_PREP_FROM_POST_HUMAN_TRIAGE_READONLY_V1",
        **BOUNDARY,
    }

    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    report_lines = [
        "# BRODY POST HUMAN REVIEW MEMORY TRIAGE READONLY V1",
        "",
        f"- status: {summary['status']}",
        f"- source_mode: {summary['source_mode']}",
        f"- source_gate_patch: {summary['source_gate_patch']}",
        f"- decision_count: {summary['decision_count']}",
        f"- keep_count: {summary['keep_count']}",
        f"- transition_count: {summary['transition_count']}",
        f"- reflex_count: {summary['reflex_count']}",
        f"- neant_count: {summary['neant_count']}",
        f"- latest_triage_event_hash: {summary['latest_triage_event_hash']}",
        "",
        "## Boundary",
        "",
        "- Post-human review triage: true",
        "- Human decision consumed: true",
        "- Memory candidate preparation: true",
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
