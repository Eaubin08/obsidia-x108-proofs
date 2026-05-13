import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path


CONFIRM_TOKEN = "BRODY_MANUAL_GRAPHITI_WRITE_READONLY_MEMORY_ONLY"


BOUNDARY = {
    "readonly": True,
    "response_only": True,
    "memory_role": "GUIDE_CONTEXT_NAVIGATION_ONLY",
    "memory_decision": False,
    "allowed_to_decide": False,
    "emits_act": False,
    "emits_allow_hold_block": False,
    "emits_verdict": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "x108_runtime_binding": False,
    "x108_merge": False,
    "neo4j_role": "LIVE_GRAPH_MEMORY_SURFACE_ONLY",
    "brody_role": "GRAPHITI_IMPORT_APPLY_GUARDED_MANUAL_ONLY",
    "decision_authority": "KX108_ONLY",
    "ui": False,
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()


def clean_text(value, max_chars=2200):
    if value is None:
        return ""
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text[:max_chars]


def read_jsonl(path: Path, limit: int):
    out = []
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
            if len(out) >= limit:
                break
    return out


def get_nested(record):
    for key in ("candidate", "memory_candidate", "record", "payload", "item"):
        value = record.get(key)
        if isinstance(value, dict):
            return value
    return record


def review_gate(record):
    blob = json.dumps(record, ensure_ascii=False).upper()

    for key in (
        "review_gate",
        "review_decision",
        "review_status",
        "gate",
        "decision",
        "action",
        "import_action",
        "candidate_action",
        "status",
    ):
        value = str(record.get(key, "")).upper()
        if "ACCEPT" in value:
            return "ACCEPT"
        if "REJECT" in value:
            return "REJECT"
        if "REVIEW" in value:
            return "REVIEW"

    nested = get_nested(record)
    for key in (
        "review_gate",
        "review_decision",
        "review_status",
        "gate",
        "decision",
        "action",
        "import_action",
        "candidate_action",
        "status",
        "zone",
    ):
        value = str(nested.get(key, "")).upper()
        if "ACCEPT" in value or value == "CRISTAL":
            return "ACCEPT"
        if "REJECT" in value or value == "NEANT":
            return "REJECT"
        if "REVIEW" in value or value == "TRANSITION":
            return "REVIEW"

    if '"ACCEPT' in blob or "ACCEPT_CANDIDATE" in blob:
        return "ACCEPT"
    if '"REJECT' in blob or "REJECT_CANDIDATE" in blob:
        return "REJECT"
    if '"REVIEW' in blob or "REVIEW_CANDIDATE" in blob:
        return "REVIEW"

    return "REVIEW"


def first_value(obj, keys, default=""):
    for key in keys:
        value = obj.get(key)
        if value not in (None, ""):
            return value
    return default


def normalize_tags(value):
    tags = []
    if isinstance(value, list):
        tags = [str(x).strip() for x in value if str(x).strip()]
    elif isinstance(value, str):
        tags = [x.strip() for x in re.split(r"[,;| ]+", value) if x.strip()]

    base = [
        "brody",
        "graphiti",
        "memory_candidate",
        "manual_apply_guarded",
        "readonly_context",
        "x108",
    ]

    merged = []
    for tag in base + tags:
        safe = re.sub(r"\s+", "_", str(tag).strip().lower())
        if safe and safe not in merged:
            merged.append(safe)
    return merged


def build_candidate(record, index):
    nested = get_nested(record)

    title = clean_text(first_value(nested, [
        "title", "memory_title", "candidate_title", "query", "user", "source_title", "name"
    ], default=f"BRODY_MEMORY_CANDIDATE_{index:04d}"), max_chars=180)

    text = clean_text(first_value(nested, [
        "text", "content", "memory_text", "response_md", "excerpt", "summary", "body", "value"
    ], default=json.dumps(nested, ensure_ascii=False)), max_chars=2600)

    source_ref = clean_text(first_value(nested, [
        "source_ref", "source", "path", "source_path", "record_source", "session_id"
    ], default=first_value(record, ["source_ref", "source", "path", "session_id"], default="unknown")), max_chars=500)

    zone = clean_text(first_value(nested, [
        "zone", "triage_zone", "classification", "bucket"
    ], default=first_value(record, ["zone", "triage_zone"], default="UNKNOWN")), max_chars=80)

    candidate_seed = json.dumps({
        "title": title,
        "text": text,
        "source_ref": source_ref,
        "zone": zone,
        "index": index,
    }, ensure_ascii=False, sort_keys=True)

    cid = first_value(nested, [
        "candidate_id", "id", "record_id", "memory_id", "event_id"
    ], default="")
    cid = clean_text(cid, max_chars=160)
    if not cid:
        cid = "BRODY_GRAPHITI_ACCEPTED_" + sha256_text(candidate_seed)[:24]

    tags = normalize_tags(first_value(nested, ["tags"], default=[]))

    return {
        "id": cid,
        "title": title,
        "text": text,
        "source_ref": source_ref,
        "zone": zone,
        "tags": tags,
        "review_gate": review_gate(record),
        "record_hash": sha256_text(json.dumps(record, ensure_ascii=False, sort_keys=True)),
    }


def build_plan(records):
    plan = []
    skipped = []

    for i, record in enumerate(records, start=1):
        gate = review_gate(record)
        candidate = build_candidate(record, i)

        if gate != "ACCEPT":
            skipped.append({
                "index": i,
                "review_gate": gate,
                "record_hash": candidate["record_hash"],
                "reason": "NOT_ACCEPTED_BY_REVIEW_GATE",
            })
            continue

        plan.append({
            "index": i,
            "operation": "MERGE_BRODY_MEMORY_DOC",
            "label": "BrodyMemoryDoc",
            "id": candidate["id"],
            "title": candidate["title"],
            "text": candidate["text"],
            "source_ref": candidate["source_ref"],
            "zone": candidate["zone"],
            "tags": candidate["tags"],
            "review_gate": gate,
            "record_hash": candidate["record_hash"],
            "readonly": True,
            "memory_decision": False,
            "decision_authority": "KX108_ONLY",
            "kernel_mutation": False,
            "x108_merge": False,
        })

    return plan, skipped


def apply_to_neo4j(plan, confirm):
    if confirm != CONFIRM_TOKEN:
        raise RuntimeError("MANUAL_CONFIRM_TOKEN_REQUIRED")

    uri = os.environ.get("NEO4J_URI") or "bolt://localhost:7688"
    user = os.environ.get("NEO4J_USER") or os.environ.get("NEO4J_USERNAME") or "neo4j"
    password = os.environ.get("NEO4J_PASSWORD")
    database = os.environ.get("NEO4J_DATABASE") or "neo4j"

    if not password:
        raise RuntimeError("NEO4J_PASSWORD_NOT_SET")

    from neo4j import GraphDatabase

    cypher = """
    MERGE (d:BrodyMemoryDoc {id: $id})
    SET d.title = $title,
        d.text = $text,
        d.content = $text,
        d.summary = $text,
        d.source = "BRODY_MANUAL_ACCEPTED_MEMORY_CANDIDATE",
        d.source_ref = $source_ref,
        d.path = $source_ref,
        d.zone = $zone,
        d.tags = $tags,
        d.readonly = true,
        d.memory_decision = false,
        d.decision_authority = "KX108_ONLY",
        d.kernel_mutation = false,
        d.x108_merge = false,
        d.graphiti_manual_apply = true,
        d.applied_at = $applied_at,
        d.record_hash = $record_hash
    RETURN d.id AS id
    """

    applied = []
    driver = GraphDatabase.driver(uri, auth=(user, password), connection_timeout=15)
    try:
        with driver.session(database=database) as session:
            for item in plan:
                params = dict(item)
                params["applied_at"] = now_iso()
                result = session.run(cypher, **params).single()
                applied.append(result["id"] if result else item["id"])
    finally:
        driver.close()

    return applied


def write_jsonl(path: Path, rows):
    with path.open("w", encoding="utf-8", errors="ignore") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--review-records-jsonl", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--confirm", default="")
    args = parser.parse_args()

    source = Path(args.review_records_jsonl)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not source.exists():
        raise RuntimeError(f"MISSING_REVIEW_RECORDS_JSONL={source}")

    records = read_jsonl(source, args.limit)
    plan, skipped = build_plan(records)

    applied_ids = []
    if args.apply:
        applied_ids = apply_to_neo4j(plan, args.confirm)

    latest_event_hash = ""
    event_hashes = []
    for row in plan + skipped:
        seed = json.dumps({
            "prev": latest_event_hash,
            "row": row,
            "apply": bool(args.apply),
        }, ensure_ascii=False, sort_keys=True)
        latest_event_hash = sha256_text(seed)
        event_hashes.append(latest_event_hash)

    plan_jsonl = out_dir / "GRAPHITI_APPLY_GUARDED_PLAN.jsonl"
    plan_json = out_dir / "GRAPHITI_APPLY_GUARDED_PLAN.json"
    skipped_jsonl = out_dir / "GRAPHITI_APPLY_GUARDED_SKIPPED.jsonl"
    summary_json = out_dir / "GRAPHITI_APPLY_GUARDED_SUMMARY.json"
    report_md = out_dir / "GRAPHITI_APPLY_GUARDED_REPORT.md"

    write_jsonl(plan_jsonl, plan)
    plan_json.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    write_jsonl(skipped_jsonl, skipped)

    summary = {
        "status": "BRODY_GRAPHITI_IMPORT_APPLY_GUARDED_MANUAL_ONLY_PASS",
        "created_at": now_iso(),
        "source_review_records_jsonl": str(source),
        "record_count": len(records),
        "apply_plan_count": len(plan),
        "skipped_count": len(skipped),
        "applied_count": len(applied_ids),
        "applied_ids": applied_ids,
        "dry_run": not bool(args.apply),
        "manual_apply": bool(args.apply),
        "confirm_required": CONFIRM_TOKEN,
        "latest_event_hash": latest_event_hash,
        "outputs": {
            "plan_jsonl": str(plan_jsonl),
            "plan_json": str(plan_json),
            "skipped_jsonl": str(skipped_jsonl),
            "summary_json": str(summary_json),
            "report_md": str(report_md),
        },
        "graphiti_index_write": bool(args.apply),
        "memory_intake": bool(args.apply),
        **BOUNDARY,
    }

    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# BRODY GRAPHITI IMPORT APPLY — GUARDED MANUAL ONLY",
        "",
        f"- status: {summary['status']}",
        f"- dry_run: {str(summary['dry_run']).lower()}",
        f"- manual_apply: {str(summary['manual_apply']).lower()}",
        f"- record_count: {summary['record_count']}",
        f"- apply_plan_count: {summary['apply_plan_count']}",
        f"- skipped_count: {summary['skipped_count']}",
        f"- applied_count: {summary['applied_count']}",
        f"- latest_event_hash: {summary['latest_event_hash']}",
        "",
        "## Boundary",
        "",
        "- Decision authority: KX108_ONLY",
        "- Kernel mutation: false",
        "- X108 merge: false",
        "- UI: false",
        "",
        "## Manual apply guard",
        "",
        f"Required confirm token: `{CONFIRM_TOKEN}`",
    ]
    report_md.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
