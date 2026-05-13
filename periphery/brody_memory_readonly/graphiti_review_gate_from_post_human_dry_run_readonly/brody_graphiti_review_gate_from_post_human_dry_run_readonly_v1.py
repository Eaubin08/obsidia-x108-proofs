import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

BOUNDARY = {
    "readonly": True,
    "response_only": True,
    "graphiti_review_gate": True,
    "post_human_dry_run_source": True,
    "human_review_required": True,
    "dry_run": True,
    "manual_apply_required": True,
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
    "brody_role": "GRAPHITI_REVIEW_GATE_FROM_POST_HUMAN_DRY_RUN_READONLY",
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


def infer_review(plan: dict):
    reasons = []

    if plan.get("action") != "MERGE_GRAPHITI_MEMORY_DOC_DRY_RUN":
        reasons.append("BAD_ACTION")

    if plan.get("write_executed") is not False:
        reasons.append("WRITE_EXECUTED_NOT_FALSE")

    if plan.get("graphiti_index_write") is not False:
        reasons.append("GRAPHITI_INDEX_WRITE_NOT_FALSE")

    if plan.get("neo4j_write_executed") is not False:
        reasons.append("NEO4J_WRITE_EXECUTED_NOT_FALSE")

    if plan.get("memory_intake") is not False:
        reasons.append("MEMORY_INTAKE_NOT_FALSE")

    if plan.get("memory_decision") is not False:
        reasons.append("MEMORY_DECISION_NOT_FALSE")

    params = plan.get("params", {}) or {}

    if params.get("dry_run") is not True:
        reasons.append("PARAM_DRY_RUN_NOT_TRUE")

    if params.get("manual_apply_required") is not True:
        reasons.append("PARAM_MANUAL_APPLY_REQUIRED_NOT_TRUE")

    if not str(plan.get("graphiti_candidate_id") or "").strip():
        reasons.append("MISSING_GRAPHITI_CANDIDATE_ID")

    if not str(params.get("content") or "").strip():
        reasons.append("MISSING_CONTENT")

    if reasons:
        return "REVIEW_IMPORT_PLAN", "TRANSITION", reasons

    return "ACCEPT_IMPORT_CANDIDATE", "KEEP", ["POST_HUMAN_DRY_RUN_PLAN_VALID"]


def make_review_record(plan: dict, index: int, prev_hash: str):
    review, suggested_human_decision, reasons = infer_review(plan)

    record = {
        "index": index,
        "source_import_plan_id": plan.get("import_plan_id"),
        "graphiti_candidate_id": plan.get("graphiti_candidate_id"),
        "source_action": plan.get("action"),
        "source_target_label": plan.get("target_label"),
        "source_dry_run_event_hash": plan.get("dry_run_event_hash"),
        "source_ref": (plan.get("params") or {}).get("source_ref"),
        "title": (plan.get("params") or {}).get("title"),
        "text_preview": str((plan.get("params") or {}).get("content") or "")[:500],
        "review": review,
        "suggested_human_decision": suggested_human_decision,
        "reasons": reasons,
        "review_lane": "KEEP_IMPORT_REVIEW" if review == "ACCEPT_IMPORT_CANDIDATE" else "TRANSITION_IMPORT_REVIEW",
        "human_decision": "PENDING",
        "write_executed": False,
        "created_at": now_iso(),
        **BOUNDARY,
    }

    seed = json.dumps(
        {
            "prev": prev_hash,
            "source_import_plan_id": record["source_import_plan_id"],
            "graphiti_candidate_id": record["graphiti_candidate_id"],
            "review": review,
            "reasons": reasons,
        },
        ensure_ascii=False,
        sort_keys=True,
    )

    record["prev_review_event_hash"] = prev_hash
    record["review_event_hash"] = sha256_text(seed)

    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    dry_ptr = workspace_root / "CURRENT_BRODY_GRAPHITI_IMPORT_DRY_RUN_FROM_POST_HUMAN_PREP_READONLY_V1_VALIDATE.txt"
    if not dry_ptr.exists():
        raise RuntimeError(f"MISSING_DRY_RUN_VALIDATE_POINTER={dry_ptr}")

    kv = parse_kv(dry_ptr)

    import_plan_jsonl = Path(kv.get("IMPORT_PLAN_JSONL", ""))
    dry_summary_json = Path(kv.get("SUMMARY_JSON", ""))

    if not import_plan_jsonl.exists():
        raise RuntimeError(f"MISSING_IMPORT_PLAN_JSONL={import_plan_jsonl}")
    if not dry_summary_json.exists():
        raise RuntimeError(f"MISSING_DRY_RUN_SUMMARY_JSON={dry_summary_json}")

    dry_summary = json.loads(dry_summary_json.read_text(encoding="utf-8-sig", errors="ignore"))

    if dry_summary.get("status") != "BRODY_GRAPHITI_IMPORT_DRY_RUN_FROM_POST_HUMAN_PREP_READONLY_V1_PASS":
        raise RuntimeError(f"BAD_DRY_RUN_STATUS={dry_summary.get('status')}")

    if int(dry_summary.get("import_plan_count", -1)) != 29:
        raise RuntimeError(f"BAD_IMPORT_PLAN_COUNT={dry_summary.get('import_plan_count')}")

    plans = read_jsonl(import_plan_jsonl)

    if len(plans) != 29:
        raise RuntimeError(f"BAD_PLAN_ROWS={len(plans)}")

    records = []
    prev = "GENESIS_BRODY_GRAPHITI_REVIEW_GATE_FROM_POST_HUMAN_DRY_RUN_READONLY_V1"

    for idx, plan in enumerate(plans, start=1):
        rec = make_review_record(plan, idx, prev)
        prev = rec["review_event_hash"]
        records.append(rec)

    accept_count = sum(1 for r in records if r["review"] == "ACCEPT_IMPORT_CANDIDATE")
    transition_count = sum(1 for r in records if r["review"] == "REVIEW_IMPORT_PLAN")
    keep_count = sum(1 for r in records if r["suggested_human_decision"] == "KEEP")
    review_pending_count = sum(1 for r in records if r["human_decision"] == "PENDING")

    review_records_jsonl = out_dir / "BRODY_GRAPHITI_REVIEW_GATE_FROM_POST_HUMAN_DRY_RUN_RECORDS.jsonl"
    review_records_json = out_dir / "BRODY_GRAPHITI_REVIEW_GATE_FROM_POST_HUMAN_DRY_RUN_RECORDS.json"
    checklist_md = out_dir / "BRODY_GRAPHITI_REVIEW_GATE_FROM_POST_HUMAN_DRY_RUN_CHECKLIST.md"
    summary_json = out_dir / "BRODY_GRAPHITI_REVIEW_GATE_FROM_POST_HUMAN_DRY_RUN_SUMMARY.json"
    report_md = out_dir / "BRODY_GRAPHITI_REVIEW_GATE_FROM_POST_HUMAN_DRY_RUN_REPORT.md"

    write_jsonl(review_records_jsonl, records)
    review_records_json.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = {
        "status": "BRODY_GRAPHITI_REVIEW_GATE_FROM_POST_HUMAN_DRY_RUN_READONLY_V1_PASS",
        "created_at": now_iso(),
        "source_dry_run_pointer": str(dry_ptr),
        "source_import_plan_jsonl": str(import_plan_jsonl),
        "source_dry_run_summary_json": str(dry_summary_json),
        "source_import_plan_count": dry_summary.get("import_plan_count"),
        "review_record_count": len(records),
        "accept_import_candidate_count": accept_count,
        "transition_review_count": transition_count,
        "suggested_keep_count": keep_count,
        "human_decision_pending_count": review_pending_count,
        "latest_review_event_hash": prev,
        "outputs": {
            "review_records_jsonl": str(review_records_jsonl),
            "review_records_json": str(review_records_json),
            "checklist_md": str(checklist_md),
            "summary_json": str(summary_json),
            "report_md": str(report_md),
        },
        "next": "HUMAN_REVIEW_THEN_BUILD_BRODY_GRAPHITI_REVIEW_DECISION_APPLY_READONLY_V1",
        **BOUNDARY,
    }

    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    checklist_lines = [
        "# BRODY GRAPHITI REVIEW GATE - POST HUMAN DRY RUN",
        "",
        "Decision codes:",
        "",
        "- KEEP = allow this import candidate to move toward guarded manual apply",
        "- TRANSITION = review later / unclear",
        "- NEANT = reject this import candidate",
        "- REFLEX = alert / weak signal",
        "",
        "Nothing below writes Graphiti.",
        "Nothing below becomes canon memory.",
        "",
    ]

    for r in records:
        checklist_lines += [
            f"## {r['index']}. {r['graphiti_candidate_id']}",
            "",
            f"- review: `{r['review']}`",
            f"- suggested: `{r['suggested_human_decision']}`",
            f"- title: `{r.get('title')}`",
            f"- source_ref: `{r.get('source_ref')}`",
            f"- reasons: `{', '.join(r.get('reasons', []))}`",
            "- question: **KEEP / TRANSITION / NEANT / REFLEX ?**",
            "- decision: `[ ] KEEP  [ ] TRANSITION  [ ] NEANT  [ ] REFLEX`",
            "- reason:",
            "",
        ]

    checklist_md.write_text("\n".join(checklist_lines), encoding="utf-8")

    lines = [
        "# BRODY GRAPHITI REVIEW GATE FROM POST HUMAN DRY RUN READONLY V1",
        "",
        f"- status: {summary['status']}",
        f"- source_import_plan_count: {summary['source_import_plan_count']}",
        f"- review_record_count: {summary['review_record_count']}",
        f"- accept_import_candidate_count: {summary['accept_import_candidate_count']}",
        f"- transition_review_count: {summary['transition_review_count']}",
        f"- human_decision_pending_count: {summary['human_decision_pending_count']}",
        f"- latest_review_event_hash: {summary['latest_review_event_hash']}",
        "",
        "## Boundary",
        "",
        "- Graphiti review gate: true",
        "- Human review required: true",
        "- Dry run: true",
        "- Manual apply required: true",
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
