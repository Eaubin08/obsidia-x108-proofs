import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

BOUNDARY = {
    "readonly": True,
    "response_only": True,
    "graphiti_review_decision_apply": True,
    "human_decision_applied": True,
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
    "brody_role": "GRAPHITI_REVIEW_DECISION_APPLY_READONLY",
    "memory_role": "GUIDE_CONTEXT_NAVIGATION_ONLY",
}

VALID_DECISIONS = {"KEEP", "TRANSITION", "NEANT", "REFLEX"}


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
    with path.open("r", encoding="utf-8-sig", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows):
    with path.open("w", encoding="utf-8", errors="ignore") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def load_decision_file(path: Path) -> dict:
    if not path.exists():
        raise RuntimeError(f"MISSING_DECISION_FILE={path}")

    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8-sig", errors="ignore"))
        if isinstance(data, list):
            rows = data
        else:
            rows = data.get("decisions", [])
    else:
        rows = read_jsonl(path)

    decisions = {}
    for row in rows:
        key = row.get("graphiti_candidate_id") or row.get("source_import_plan_id") or row.get("id")
        decision = str(row.get("decision") or row.get("human_decision") or "").upper().strip()
        if not key:
            continue
        if decision not in VALID_DECISIONS:
            raise RuntimeError(f"BAD_DECISION_FOR_{key}={decision}")
        decisions[str(key)] = decision

    return decisions


def zone_for_decision(decision: str) -> str:
    if decision == "KEEP":
        return "APPROVED_GRAPHITI_IMPORT_CANDIDATE"
    if decision == "TRANSITION":
        return "TRANSITION_GRAPHITI_IMPORT_REVIEW_LATER"
    if decision == "NEANT":
        return "REJECTED_GRAPHITI_IMPORT_CANDIDATE"
    if decision == "REFLEX":
        return "REFLEX_ALERT_IMPORT_TRACE"
    return "UNKNOWN"


def make_decision_record(review: dict, decision: str, index: int, prev_hash: str, mode: str):
    zone = zone_for_decision(decision)

    record = {
        "index": index,
        "mode": mode,
        "source_review_event_hash": review.get("review_event_hash"),
        "source_import_plan_id": review.get("source_import_plan_id"),
        "graphiti_candidate_id": review.get("graphiti_candidate_id"),
        "source_action": review.get("source_action"),
        "source_target_label": review.get("source_target_label"),
        "source_ref": review.get("source_ref"),
        "title": review.get("title"),
        "text_preview": review.get("text_preview"),
        "review": review.get("review"),
        "review_lane": review.get("review_lane"),
        "suggested_human_decision": review.get("suggested_human_decision"),
        "human_decision": decision,
        "post_human_zone": zone,
        "approved_for_guarded_manual_apply": decision == "KEEP",
        "human_decision_applied": True,
        "write_executed": False,
        "created_at": now_iso(),
        **BOUNDARY,
    }

    seed = json.dumps(
        {
            "prev": prev_hash,
            "graphiti_candidate_id": record["graphiti_candidate_id"],
            "source_import_plan_id": record["source_import_plan_id"],
            "decision": decision,
            "zone": zone,
        },
        ensure_ascii=False,
        sort_keys=True,
    )

    record["prev_decision_event_hash"] = prev_hash
    record["decision_event_hash"] = sha256_text(seed)
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--accept-suggested", action="store_true")
    parser.add_argument("--decision-file", default="")
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    gate_ptr = workspace_root / "CURRENT_BRODY_GRAPHITI_REVIEW_GATE_FROM_POST_HUMAN_DRY_RUN_READONLY_V1_VALIDATE.txt"
    if not gate_ptr.exists():
        raise RuntimeError(f"MISSING_REVIEW_GATE_VALIDATE_POINTER={gate_ptr}")

    kv = parse_kv(gate_ptr)

    review_records_jsonl = Path(kv.get("REVIEW_RECORDS_JSONL", ""))
    gate_summary_json = Path(kv.get("SUMMARY_JSON", ""))

    if not review_records_jsonl.exists():
        raise RuntimeError(f"MISSING_REVIEW_RECORDS_JSONL={review_records_jsonl}")
    if not gate_summary_json.exists():
        raise RuntimeError(f"MISSING_GATE_SUMMARY_JSON={gate_summary_json}")

    gate_summary = json.loads(gate_summary_json.read_text(encoding="utf-8-sig", errors="ignore"))

    if gate_summary.get("status") != "BRODY_GRAPHITI_REVIEW_GATE_FROM_POST_HUMAN_DRY_RUN_READONLY_V1_PASS":
        raise RuntimeError(f"BAD_GATE_STATUS={gate_summary.get('status')}")

    if int(gate_summary.get("review_record_count", -1)) != 29:
        raise RuntimeError(f"BAD_GATE_REVIEW_RECORD_COUNT={gate_summary.get('review_record_count')}")

    reviews = read_jsonl(review_records_jsonl)

    if len(reviews) != 29:
        raise RuntimeError(f"BAD_REVIEW_ROWS={len(reviews)}")

    if args.accept_suggested:
        mode = "ACCEPT_SUGGESTED_BY_HUMAN_OPERATOR"
        decision_map = {}
    elif args.decision_file:
        mode = "CUSTOM_HUMAN_DECISION_FILE"
        decision_map = load_decision_file(Path(args.decision_file))
    else:
        raise RuntimeError("HUMAN_DECISION_REQUIRED_USE_ACCEPT_SUGGESTED_OR_DECISION_FILE")

    records = []
    prev = "GENESIS_BRODY_GRAPHITI_REVIEW_DECISION_APPLY_READONLY_V1"

    for idx, review in enumerate(reviews, start=1):
        key1 = str(review.get("graphiti_candidate_id") or "")
        key2 = str(review.get("source_import_plan_id") or "")

        if args.accept_suggested:
            decision = str(review.get("suggested_human_decision") or "").upper().strip()
        else:
            decision = decision_map.get(key1) or decision_map.get(key2) or ""

        if decision not in VALID_DECISIONS:
            raise RuntimeError(f"BAD_OR_MISSING_HUMAN_DECISION_INDEX_{idx}={decision}")

        rec = make_decision_record(review, decision, idx, prev, mode)
        prev = rec["decision_event_hash"]
        records.append(rec)

    keep = [r for r in records if r["human_decision"] == "KEEP"]
    transition = [r for r in records if r["human_decision"] == "TRANSITION"]
    neant = [r for r in records if r["human_decision"] == "NEANT"]
    reflex = [r for r in records if r["human_decision"] == "REFLEX"]

    decisions_jsonl = out_dir / "BRODY_GRAPHITI_REVIEW_DECISIONS_APPLIED.jsonl"
    decisions_json = out_dir / "BRODY_GRAPHITI_REVIEW_DECISIONS_APPLIED.json"
    approved_jsonl = out_dir / "BRODY_GRAPHITI_APPROVED_IMPORT_CANDIDATES.jsonl"
    approved_json = out_dir / "BRODY_GRAPHITI_APPROVED_IMPORT_CANDIDATES.json"
    transition_jsonl = out_dir / "BRODY_GRAPHITI_REVIEW_TRANSITION_RECORDS.jsonl"
    reflex_jsonl = out_dir / "BRODY_GRAPHITI_REVIEW_REFLEX_RECORDS.jsonl"
    neant_jsonl = out_dir / "BRODY_GRAPHITI_REVIEW_NEANT_RECORDS.jsonl"
    summary_json = out_dir / "BRODY_GRAPHITI_REVIEW_DECISION_APPLY_SUMMARY.json"
    report_md = out_dir / "BRODY_GRAPHITI_REVIEW_DECISION_APPLY_REPORT.md"

    write_jsonl(decisions_jsonl, records)
    decisions_json.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")

    write_jsonl(approved_jsonl, keep)
    approved_json.write_text(json.dumps(keep, indent=2, ensure_ascii=False), encoding="utf-8")

    write_jsonl(transition_jsonl, transition)
    write_jsonl(reflex_jsonl, reflex)
    write_jsonl(neant_jsonl, neant)

    summary = {
        "status": "BRODY_GRAPHITI_REVIEW_DECISION_APPLY_READONLY_V1_PASS",
        "created_at": now_iso(),
        "mode": mode,
        "source_review_gate_pointer": str(gate_ptr),
        "source_review_records_jsonl": str(review_records_jsonl),
        "source_gate_summary_json": str(gate_summary_json),
        "input_review_record_count": len(reviews),
        "decision_count": len(records),
        "keep_count": len(keep),
        "transition_count": len(transition),
        "reflex_count": len(reflex),
        "neant_count": len(neant),
        "approved_import_candidate_count": len(keep),
        "latest_decision_event_hash": prev,
        "outputs": {
            "decisions_jsonl": str(decisions_jsonl),
            "decisions_json": str(decisions_json),
            "approved_import_candidates_jsonl": str(approved_jsonl),
            "approved_import_candidates_json": str(approved_json),
            "transition_jsonl": str(transition_jsonl),
            "reflex_jsonl": str(reflex_jsonl),
            "neant_jsonl": str(neant_jsonl),
            "summary_json": str(summary_json),
            "report_md": str(report_md),
        },
        "next": "BUILD_BRODY_GRAPHITI_GUARDED_MANUAL_APPLY_FROM_REVIEW_DECISION_READONLY_MEMORY_ONLY_V1",
        **BOUNDARY,
    }

    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# BRODY GRAPHITI REVIEW DECISION APPLY READONLY V1",
        "",
        f"- status: {summary['status']}",
        f"- mode: {summary['mode']}",
        f"- input_review_record_count: {summary['input_review_record_count']}",
        f"- decision_count: {summary['decision_count']}",
        f"- keep_count: {summary['keep_count']}",
        f"- transition_count: {summary['transition_count']}",
        f"- reflex_count: {summary['reflex_count']}",
        f"- neant_count: {summary['neant_count']}",
        f"- approved_import_candidate_count: {summary['approved_import_candidate_count']}",
        f"- latest_decision_event_hash: {summary['latest_decision_event_hash']}",
        "",
        "## Boundary",
        "",
        "- Human decision applied: true",
        "- Graphiti write: false",
        "- Neo4j write executed: false",
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

    report_md.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
