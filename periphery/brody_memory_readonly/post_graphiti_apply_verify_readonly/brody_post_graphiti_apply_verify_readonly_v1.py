import argparse
import json
import os
import hashlib
from datetime import datetime, timezone
from pathlib import Path

BOUNDARY = {
    "readonly": True,
    "response_only": True,
    "post_graphiti_apply_verify": True,
    "graphiti_query_read": True,
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
    "brody_role": "POST_GRAPHITI_APPLY_VERIFY_READONLY",
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

def verify_in_neo4j(ids, uri, user, password, database):
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(uri, auth=(user, password), connection_timeout=10)

    cypher = """
    MATCH (n)
    WHERE any(k IN keys(n)
      WHERE k IN ["id", "name", "candidate_id", "memory_id", "source_id"]
      AND n[k] IN $ids
    )
    RETURN
      coalesce(n.id, n.name, n.candidate_id, n.memory_id, n.source_id) AS matched_id,
      labels(n) AS labels,
      properties(n) AS props
    """

    rows = []
    try:
        with driver.session(database=database) as session:
            result = session.run(cypher, ids=ids)
            for r in result:
                props = dict(r["props"] or {})
                rows.append({
                    "matched_id": r["matched_id"],
                    "labels": list(r["labels"] or []),
                    "source": props.get("source"),
                    "source_ref": props.get("source_ref"),
                    "title": props.get("title"),
                    "record_hash": props.get("record_hash"),
                    "graphiti_manual_apply": props.get("graphiti_manual_apply"),
                    "memory_only": props.get("memory_only"),
                    "kernel_mutation": props.get("kernel_mutation"),
                    "x108_merge": props.get("x108_merge"),
                })
    finally:
        driver.close()

    return rows

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--neo4j-uri", default=os.environ.get("NEO4J_URI") or "bolt://localhost:7688")
    parser.add_argument("--limit", type=int, default=500)
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[3]
    workspace_root = repo_root.parent

    apply_exec_ptr = workspace_root / "CURRENT_BRODY_GRAPHITI_GUARDED_MANUAL_APPLY_EXECUTION_MEMORY_ONLY.txt"
    if not apply_exec_ptr.exists():
        raise RuntimeError(f"MISSING_APPLY_EXECUTION_POINTER={apply_exec_ptr}")

    kv = parse_pointer(apply_exec_ptr)

    summary_json = Path(kv.get("SUMMARY_JSON", ""))
    applied_ids_json = Path(kv.get("APPLIED_IDS_JSON", ""))

    if not summary_json.exists():
        raise RuntimeError(f"MISSING_APPLY_SUMMARY_JSON={summary_json}")
    if not applied_ids_json.exists():
        raise RuntimeError(f"MISSING_APPLIED_IDS_JSON={applied_ids_json}")

    apply_summary = load_json(summary_json)
    applied_ids = load_json(applied_ids_json)

    if isinstance(applied_ids, dict) and "applied_ids" in applied_ids:
        applied_ids = applied_ids["applied_ids"]

    if not isinstance(applied_ids, list):
        raise RuntimeError("APPLIED_IDS_NOT_LIST")

    applied_ids = applied_ids[: args.limit]

    if apply_summary.get("manual_apply_executed") is not True:
        raise RuntimeError("SOURCE_MANUAL_APPLY_NOT_EXECUTED")
    if int(apply_summary.get("write_executed_count", 0)) != len(applied_ids):
        raise RuntimeError("SOURCE_WRITE_COUNT_DOES_NOT_MATCH_APPLIED_IDS")

    password = os.environ.get("NEO4J_PASSWORD")
    user = os.environ.get("NEO4J_USER") or os.environ.get("NEO4J_USERNAME") or "neo4j"
    database = os.environ.get("NEO4J_DATABASE") or "neo4j"

    if not password:
        raise RuntimeError("NEO4J_PASSWORD_NOT_SET")

    rows = verify_in_neo4j(
        ids=applied_ids,
        uri=args.neo4j_uri,
        user=user,
        password=password,
        database=database,
    )

    found_ids = sorted({str(r.get("matched_id")) for r in rows if r.get("matched_id")})
    expected_ids = sorted(set(applied_ids))
    missing_ids = sorted(set(expected_ids) - set(found_ids))

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    verification_records = []
    prev = "GENESIS_BRODY_POST_GRAPHITI_APPLY_VERIFY_READONLY_V1"

    by_id = {}
    for r in rows:
        by_id.setdefault(str(r.get("matched_id")), []).append(r)

    for idx, mid in enumerate(expected_ids, start=1):
        matched_rows = by_id.get(mid, [])
        record = {
            "index": idx,
            "applied_id": mid,
            "found": bool(matched_rows),
            "match_count": len(matched_rows),
            "matches": matched_rows,
            "created_at": now_iso(),
            **BOUNDARY,
        }
        seed = json.dumps({"prev": prev, "record": record}, ensure_ascii=False, sort_keys=True)
        record["prev_event_hash"] = prev
        record["event_hash"] = sha256_text(seed)
        prev = record["event_hash"]
        verification_records.append(record)

    records_jsonl = out_dir / "BRODY_POST_GRAPHITI_APPLY_VERIFY_RECORDS.jsonl"
    records_json = out_dir / "BRODY_POST_GRAPHITI_APPLY_VERIFY_RECORDS.json"
    missing_json = out_dir / "BRODY_POST_GRAPHITI_APPLY_VERIFY_MISSING_IDS.json"
    summary_out = out_dir / "BRODY_POST_GRAPHITI_APPLY_VERIFY_SUMMARY.json"
    report_md = out_dir / "BRODY_POST_GRAPHITI_APPLY_VERIFY_REPORT.md"

    write_jsonl(records_jsonl, verification_records)
    records_json.write_text(json.dumps(verification_records, indent=2, ensure_ascii=False), encoding="utf-8")
    missing_json.write_text(json.dumps(missing_ids, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = {
        "status": "BRODY_POST_GRAPHITI_APPLY_VERIFY_READONLY_V1_PASS" if not missing_ids else "BRODY_POST_GRAPHITI_APPLY_VERIFY_READONLY_V1_FAIL",
        "created_at": now_iso(),
        "neo4j_uri": args.neo4j_uri,
        "source_apply_execution_pointer": str(apply_exec_ptr),
        "source_apply_summary_json": str(summary_json),
        "source_applied_ids_json": str(applied_ids_json),
        "expected_applied_id_count": len(expected_ids),
        "found_applied_id_count": len(found_ids),
        "missing_applied_id_count": len(missing_ids),
        "missing_ids": missing_ids,
        "latest_verify_event_hash": prev,
        "previous_manual_apply_executed": True,
        "previous_write_executed_count": int(apply_summary.get("write_executed_count", 0)),
        "verified_previous_graphiti_write": not bool(missing_ids),
        "verified_previous_memory_intake": not bool(missing_ids),
        "outputs": {
            "records_jsonl": str(records_jsonl),
            "records_json": str(records_json),
            "missing_json": str(missing_json),
            "summary_json": str(summary_out),
            "report_md": str(report_md),
        },
        "next": "BUILD_BRODY_POST_GRAPHITI_REPLAY_QUERY_REGRESSION_READONLY_V1",
        **BOUNDARY,
    }

    summary_out.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# BRODY POST GRAPHITI APPLY VERIFY READONLY V1",
        "",
        f"- status: {summary['status']}",
        f"- expected_applied_id_count: {summary['expected_applied_id_count']}",
        f"- found_applied_id_count: {summary['found_applied_id_count']}",
        f"- missing_applied_id_count: {summary['missing_applied_id_count']}",
        f"- verified_previous_graphiti_write: {str(summary['verified_previous_graphiti_write']).lower()}",
        f"- verified_previous_memory_intake: {str(summary['verified_previous_memory_intake']).lower()}",
        "",
        "## Boundary",
        "",
        "- This verifier reads Graphiti only.",
        "- It does not write Neo4j.",
        "- It does not decide memory.",
        "- It does not mutate X108.",
        "- It verifies the previous guarded manual apply.",
        "",
        "## Next",
        "",
        summary["next"],
    ]

    report_md.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))

    if missing_ids:
        raise SystemExit("POST_GRAPHITI_APPLY_VERIFY_MISSING_IDS")

if __name__ == "__main__":
    main()
