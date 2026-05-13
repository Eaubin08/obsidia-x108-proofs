import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

CONFIRM_TOKEN = "BRODY_GRAPHITI_MANUAL_APPLY_REVIEW_DECISION_MEMORY_ONLY"

BOUNDARY_BASE = {
    "response_only": True,
    "guarded_manual_apply": True,
    "manual_apply_only": True,
    "memory_only": True,
    "requires_human_confirm_token": True,
    "memory_decision": False,
    "allowed_to_decide": False,
    "emits_act": False,
    "emits_verdict": False,
    "kernel_mutation": False,
    "x108_runtime_binding": False,
    "x108_merge": False,
    "decision_authority": "KX108_ONLY",
    "ui": False,
    "brody_role": "GRAPHITI_GUARDED_MANUAL_APPLY_FROM_REVIEW_DECISION_READONLY_MEMORY_ONLY",
    "memory_role": "GUIDE_CONTEXT_NAVIGATION_ONLY",
}

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()

def read_jsonl(path: Path):
    rows = []
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows

def write_jsonl(path: Path, rows):
    with path.open("w", encoding="utf-8", errors="ignore") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

def parse_pointer(path: Path):
    kv = {}
    with path.open("r", encoding="utf-8-sig", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or "=" not in line:
                continue
            k, v = line.split("=", 1)
            kv[k.strip()] = v.strip()
    return kv

def first_value(obj, keys, default=None):
    if not isinstance(obj, dict):
        return default
    for key in keys:
        if key in obj and obj[key] not in (None, ""):
            return obj[key]
    for value in obj.values():
        if isinstance(value, dict):
            found = first_value(value, keys, None)
            if found not in (None, ""):
                return found
    return default

def normalize_text(value, max_chars=12000):
    if value is None:
        return ""
    text = str(value).replace("\x00", " ").strip()
    while "  " in text:
        text = text.replace("  ", " ")
    if len(text) > max_chars:
        text = text[:max_chars] + "..."
    return text

def build_plan_row(record, index, prev_hash):
    raw_seed = json.dumps(record, ensure_ascii=False, sort_keys=True)

    source_id = normalize_text(
        first_value(record, ["source_id", "candidate_id", "id", "record_id"], ""),
        max_chars=180,
    )

    title = normalize_text(
        first_value(record, ["title", "name", "pointer_name", "status_key"], f"BRODY_MEMORY_CANDIDATE_{index:04d}"),
        max_chars=240,
    )

    text = normalize_text(
        first_value(record, ["text", "content", "summary", "text_preview", "body", "path", "pointer_path"], raw_seed),
        max_chars=12000,
    )

    source_ref = normalize_text(
        first_value(record, ["source_ref", "path", "pointer_path", "source_path"], ""),
        max_chars=1200,
    )

    if not source_id:
        source_id = "BRODY_GRAPHITI_REVIEW_APPROVED_" + sha256_text(raw_seed)[:24]

    stable_id = "BRODY_GRAPHITI_MEMORY_ONLY_" + sha256_text(source_id + "|" + title + "|" + text)[:32]

    tags = first_value(record, ["tags"], [])
    if not isinstance(tags, list):
        tags = [str(tags)]

    tags = sorted(set([str(t).strip() for t in tags if str(t).strip()] + [
        "brody",
        "graphiti",
        "manual_apply",
        "memory_only",
        "post_human_review",
        "x108_readonly",
    ]))

    row = {
        "index": index,
        "graphiti_memory_id": stable_id,
        "source_id": source_id,
        "title": title,
        "text": text,
        "source_ref": source_ref,
        "tags": tags,
        "approved_for_manual_apply": True,
        "manual_confirm_required": CONFIRM_TOKEN,
        "record_hash": sha256_text(raw_seed),
        "created_at": now_iso(),
        "source_record": record,
        **BOUNDARY_BASE,
        "readonly": True,
        "graphiti_index_write": False,
        "neo4j_write_executed": False,
        "memory_intake": False,
    }

    seed = json.dumps(
        {
            "prev": prev_hash,
            "graphiti_memory_id": stable_id,
            "record_hash": row["record_hash"],
            "title": title,
            "source_ref": source_ref,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    row["prev_event_hash"] = prev_hash
    row["event_hash"] = sha256_text(seed)
    return row

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
    MERGE (d:Document {id: $id})
    SET
        d.title = $title,
        d.content = $text,
        d.summary = $text,
        d.source = "BRODY_GRAPHITI_REVIEW_DECISION_MANUAL_APPLY_MEMORY_ONLY",
        d.source_ref = $source_ref,
        d.path = $source_ref,
        d.tags = $tags,
        d.readonly_context = true,
        d.memory_only = true,
        d.memory_decision = false,
        d.allowed_to_decide = false,
        d.emits_act = false,
        d.emits_verdict = false,
        d.kernel_mutation = false,
        d.x108_runtime_binding = false,
        d.x108_merge = false,
        d.graphiti_manual_apply = true,
        d.graphiti_index_write = true,
        d.memory_intake = true,
        d.applied_at = $applied_at,
        d.record_hash = $record_hash
    RETURN d.id AS id
    """

    applied = []
    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        with driver.session(database=database) as session:
            for row in plan:
                result = session.run(
                    cypher,
                    id=row["graphiti_memory_id"],
                    title=row["title"],
                    text=row["text"],
                    source_ref=row["source_ref"],
                    tags=row["tags"],
                    applied_at=now_iso(),
                    record_hash=row["record_hash"],
                )
                rec = result.single()
                if rec:
                    applied.append(rec["id"])
    finally:
        driver.close()

    return applied

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--approved-import-candidates-jsonl", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--confirm", default="")
    args = parser.parse_args()

    source = Path(args.approved_import_candidates_jsonl)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    records = read_jsonl(source)[: args.limit]

    plan = []
    prev = "GENESIS_BRODY_GRAPHITI_GUARDED_MANUAL_APPLY_FROM_REVIEW_DECISION_MEMORY_ONLY_V1"
    for idx, record in enumerate(records, start=1):
        row = build_plan_row(record, idx, prev)
        prev = row["event_hash"]
        plan.append(row)

    applied_ids = []
    if args.apply:
        applied_ids = apply_to_neo4j(plan, args.confirm)

    dry_run = not bool(args.apply)
    graphiti_write = bool(args.apply)
    write_count = len(applied_ids)

    plan_jsonl = out_dir / "BRODY_GRAPHITI_GUARDED_MANUAL_APPLY_PLAN.jsonl"
    plan_json = out_dir / "BRODY_GRAPHITI_GUARDED_MANUAL_APPLY_PLAN.json"
    applied_json = out_dir / "BRODY_GRAPHITI_GUARDED_MANUAL_APPLY_APPLIED_IDS.json"
    summary_json = out_dir / "BRODY_GRAPHITI_GUARDED_MANUAL_APPLY_SUMMARY.json"
    report_md = out_dir / "BRODY_GRAPHITI_GUARDED_MANUAL_APPLY_REPORT.md"

    write_jsonl(plan_jsonl, plan)
    plan_json.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    applied_json.write_text(json.dumps(applied_ids, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = {
        "status": "BRODY_GRAPHITI_GUARDED_MANUAL_APPLY_FROM_REVIEW_DECISION_READONLY_MEMORY_ONLY_V1_PASS",
        "created_at": now_iso(),
        "source_approved_import_candidates_jsonl": str(source),
        "approved_candidate_count": len(records),
        "manual_apply_plan_count": len(plan),
        "manual_apply_executed": bool(args.apply),
        "write_executed_count": write_count,
        "applied_ids": applied_ids,
        "dry_run": dry_run,
        "manual_apply_required": True,
        "confirm_required": CONFIRM_TOKEN,
        "latest_apply_event_hash": prev,
        "outputs": {
            "manual_apply_plan_jsonl": str(plan_jsonl),
            "manual_apply_plan_json": str(plan_json),
            "applied_ids_json": str(applied_json),
            "summary_json": str(summary_json),
            "report_md": str(report_md),
        },
        "next": "IF_MANUAL_APPLY_EXECUTED_THEN_BUILD_BRODY_POST_GRAPHITI_APPLY_VERIFY_READONLY_V1",
        **BOUNDARY_BASE,
        "readonly": dry_run,
        "graphiti_index_write": graphiti_write,
        "neo4j_write_executed": graphiti_write,
        "memory_intake": graphiti_write,
    }

    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# BRODY GRAPHITI GUARDED MANUAL APPLY FROM REVIEW DECISION",
        "",
        f"- status: {summary['status']}",
        f"- dry_run: {str(summary['dry_run']).lower()}",
        f"- manual_apply_executed: {str(summary['manual_apply_executed']).lower()}",
        f"- approved_candidate_count: {summary['approved_candidate_count']}",
        f"- manual_apply_plan_count: {summary['manual_apply_plan_count']}",
        f"- write_executed_count: {summary['write_executed_count']}",
        "",
        "## Boundary",
        "",
        "- Memory only: true",
        "- Requires human confirm token: true",
        "- Graphiti write: true only if --apply and valid token",
        "- Neo4j write executed: true only if --apply and valid token",
        "- Kernel mutation: false",
        "- X108 runtime binding: false",
        "- X108 merge: false",
        "- Emits ACT: false",
        "- Emits verdict: false",
        "",
        "## Confirm token",
        "",
        f"`{CONFIRM_TOKEN}`",
    ]
    report_md.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
