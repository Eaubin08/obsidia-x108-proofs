import argparse
import json
import os
import hashlib
from datetime import datetime, timezone
from pathlib import Path

BOUNDARY = {
    "readonly": True,
    "response_only": True,
    "post_graphiti_replay_query_regression": True,
    "scalar_safe_replay": True,
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
    "brody_role": "POST_GRAPHITI_REPLAY_QUERY_REGRESSION_READONLY",
    "memory_role": "GUIDE_CONTEXT_NAVIGATION_ONLY",
}

REPLAY_QUERIES = [
    "BRODY_GRAPHITI_MEMORY_ONLY",
    "BRODY",
    "GRAPHITI",
    "MEMORY",
    "READONLY",
    "KEEP",
    "PIPELINE",
    "FREEZE",
]

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

def neo4j_session(uri, user, password, database):
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(uri, auth=(user, password), connection_timeout=10)
    session = driver.session(database=database)
    return driver, session

def exact_id_replay(session, ids):
    # Scalar-safe: avoid any(keys(n)) + toString(n[k]) because Graphiti nodes may contain array properties.
    cypher = """
    MATCH (n)
    WHERE n.id IN $ids OR n.name IN $ids
    RETURN coalesce(n.id, n.name) AS matched_id, labels(n) AS labels, properties(n) AS props
    """
    rows = []
    for r in session.run(cypher, ids=ids):
        rows.append({
            "matched_id": str(r["matched_id"]) if r["matched_id"] is not None else None,
            "labels": list(r["labels"] or []),
            "props": dict(r["props"] or {}),
        })
    return rows

def query_replay(session, query, limit):
    # Scalar-safe: query only scalar fields created/expected by this memory-only apply.
    cypher = """
    MATCH (n)
    WHERE
      (n.id IS NOT NULL AND toLower(toString(n.id)) CONTAINS toLower($q))
      OR (n.name IS NOT NULL AND toLower(toString(n.name)) CONTAINS toLower($q))
      OR (n.title IS NOT NULL AND toLower(toString(n.title)) CONTAINS toLower($q))
      OR (n.source IS NOT NULL AND toLower(toString(n.source)) CONTAINS toLower($q))
      OR (n.record_hash IS NOT NULL AND toLower(toString(n.record_hash)) CONTAINS toLower($q))
    RETURN labels(n) AS labels, properties(n) AS props
    LIMIT $limit
    """
    rows = []
    for r in session.run(cypher, q=query, limit=limit):
        props = dict(r["props"] or {})
        rows.append({
            "labels": list(r["labels"] or []),
            "id": props.get("id") or props.get("name"),
            "title": props.get("title"),
            "source": props.get("source"),
            "record_hash": props.get("record_hash"),
            "graphiti_manual_apply": props.get("graphiti_manual_apply"),
            "memory_only": props.get("memory_only"),
            "kernel_mutation": props.get("kernel_mutation"),
            "x108_merge": props.get("x108_merge"),
        })
    return rows

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--neo4j-uri", default=os.environ.get("NEO4J_URI") or "bolt://localhost:7688")
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[3]
    workspace_root = repo_root.parent

    verify_ptr = workspace_root / "CURRENT_BRODY_POST_GRAPHITI_APPLY_VERIFY_READONLY_V1_VALIDATE.txt"
    apply_ptr = workspace_root / "CURRENT_BRODY_GRAPHITI_GUARDED_MANUAL_APPLY_EXECUTION_MEMORY_ONLY.txt"

    if not verify_ptr.exists():
        raise RuntimeError(f"MISSING_VERIFY_POINTER={verify_ptr}")
    if not apply_ptr.exists():
        raise RuntimeError(f"MISSING_APPLY_EXECUTION_POINTER={apply_ptr}")

    verify_kv = parse_pointer(verify_ptr)
    apply_kv = parse_pointer(apply_ptr)

    verify_summary_json = Path(verify_kv.get("SUMMARY_JSON", ""))
    applied_ids_json = Path(apply_kv.get("APPLIED_IDS_JSON", ""))

    if not verify_summary_json.exists():
        raise RuntimeError(f"MISSING_VERIFY_SUMMARY_JSON={verify_summary_json}")
    if not applied_ids_json.exists():
        raise RuntimeError(f"MISSING_APPLIED_IDS_JSON={applied_ids_json}")

    verify_summary = load_json(verify_summary_json)
    applied_ids = load_json(applied_ids_json)

    if isinstance(applied_ids, dict) and "applied_ids" in applied_ids:
        applied_ids = applied_ids["applied_ids"]

    if not isinstance(applied_ids, list):
        raise RuntimeError("APPLIED_IDS_NOT_LIST")

    expected_ids = sorted(set(str(x) for x in applied_ids))

    if verify_summary.get("verified_previous_graphiti_write") is not True:
        raise RuntimeError("PREVIOUS_GRAPHITI_WRITE_NOT_VERIFIED")

    if int(verify_summary.get("found_applied_id_count", 0)) != len(expected_ids):
        raise RuntimeError("VERIFY_FOUND_COUNT_DOES_NOT_MATCH_APPLIED_IDS")

    password = os.environ.get("NEO4J_PASSWORD")
    user = os.environ.get("NEO4J_USER") or os.environ.get("NEO4J_USERNAME") or "neo4j"
    database = os.environ.get("NEO4J_DATABASE") or "neo4j"

    if not password:
        raise RuntimeError("NEO4J_PASSWORD_NOT_SET")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    driver, session = neo4j_session(args.neo4j_uri, user, password, database)

    try:
        exact_rows = exact_id_replay(session, expected_ids)

        found_ids = sorted(set(str(r.get("matched_id")) for r in exact_rows if r.get("matched_id")))
        missing_ids = sorted(set(expected_ids) - set(found_ids))

        query_records = []
        prev = "GENESIS_BRODY_POST_GRAPHITI_REPLAY_QUERY_REGRESSION_READONLY_V1_1_SCALAR_SAFE"

        for idx, q in enumerate(REPLAY_QUERIES, start=1):
            hits = query_replay(session, q, args.limit)
            applied_hits = []
            for h in hits:
                hay = json.dumps(h, ensure_ascii=False, sort_keys=True)
                if any(mid in hay for mid in expected_ids):
                    applied_hits.append(h)

            record = {
                "index": idx,
                "query": q,
                "hit_count": len(hits),
                "applied_hit_count": len(applied_hits),
                "hits_preview": hits[:10],
                "created_at": now_iso(),
                **BOUNDARY,
            }
            seed = json.dumps({"prev": prev, "record": record}, ensure_ascii=False, sort_keys=True)
            record["prev_event_hash"] = prev
            record["event_hash"] = sha256_text(seed)
            prev = record["event_hash"]
            query_records.append(record)

    finally:
        session.close()
        driver.close()

    required_prefix = next((r for r in query_records if r["query"] == "BRODY_GRAPHITI_MEMORY_ONLY"), None)
    required_prefix_ok = required_prefix is not None and required_prefix["applied_hit_count"] >= len(expected_ids)

    regression_ok = (
        len(expected_ids) == 29
        and len(found_ids) == 29
        and len(missing_ids) == 0
        and required_prefix_ok
    )

    exact_json = out_dir / "BRODY_POST_GRAPHITI_REPLAY_EXACT_ID_RECORDS.json"
    queries_jsonl = out_dir / "BRODY_POST_GRAPHITI_REPLAY_QUERY_RECORDS.jsonl"
    queries_json = out_dir / "BRODY_POST_GRAPHITI_REPLAY_QUERY_RECORDS.json"
    missing_json = out_dir / "BRODY_POST_GRAPHITI_REPLAY_MISSING_IDS.json"
    summary_json = out_dir / "BRODY_POST_GRAPHITI_REPLAY_QUERY_REGRESSION_SUMMARY.json"
    report_md = out_dir / "BRODY_POST_GRAPHITI_REPLAY_QUERY_REGRESSION_REPORT.md"

    exact_json.write_text(json.dumps(exact_rows, indent=2, ensure_ascii=False), encoding="utf-8")
    write_jsonl(queries_jsonl, query_records)
    queries_json.write_text(json.dumps(query_records, indent=2, ensure_ascii=False), encoding="utf-8")
    missing_json.write_text(json.dumps(missing_ids, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = {
        "status": "BRODY_POST_GRAPHITI_REPLAY_QUERY_REGRESSION_READONLY_V1_PASS" if regression_ok else "BRODY_POST_GRAPHITI_REPLAY_QUERY_REGRESSION_READONLY_V1_FAIL",
        "patch": "V1_2_SCALAR_SAFE_PARAM_FIX",
        "created_at": now_iso(),
        "neo4j_uri": args.neo4j_uri,
        "source_verify_pointer": str(verify_ptr),
        "source_verify_summary_json": str(verify_summary_json),
        "source_apply_pointer": str(apply_ptr),
        "source_applied_ids_json": str(applied_ids_json),
        "expected_applied_id_count": len(expected_ids),
        "exact_replay_found_count": len(found_ids),
        "missing_applied_id_count": len(missing_ids),
        "required_prefix_query": "BRODY_GRAPHITI_MEMORY_ONLY",
        "required_prefix_query_applied_hit_count": required_prefix["applied_hit_count"] if required_prefix else 0,
        "query_count": len(query_records),
        "query_records_pass_count": len([r for r in query_records if r["hit_count"] > 0]),
        "latest_replay_event_hash": prev,
        "post_graphiti_replay_query_regression": True,
        "scalar_safe_replay": True,
        "exact_id_replay": True,
        "query_replay": True,
        "regression_ok": regression_ok,
        "outputs": {
            "exact_json": str(exact_json),
            "queries_jsonl": str(queries_jsonl),
            "queries_json": str(queries_json),
            "missing_json": str(missing_json),
            "summary_json": str(summary_json),
            "report_md": str(report_md),
        },
        "next": "BUILD_BRODY_MEMORY_PIPELINE_FREEZE_V2",
        **BOUNDARY,
    }

    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# BRODY POST GRAPHITI REPLAY QUERY REGRESSION READONLY V1",
        "",
        f"- status: {summary['status']}",
        f"- patch: {summary['patch']}",
        f"- expected_applied_id_count: {summary['expected_applied_id_count']}",
        f"- exact_replay_found_count: {summary['exact_replay_found_count']}",
        f"- missing_applied_id_count: {summary['missing_applied_id_count']}",
        f"- required_prefix_query: {summary['required_prefix_query']}",
        f"- required_prefix_query_applied_hit_count: {summary['required_prefix_query_applied_hit_count']}",
        f"- query_count: {summary['query_count']}",
        f"- regression_ok: {str(summary['regression_ok']).lower()}",
        "",
        "## Boundary",
        "",
        "- Reads Graphiti only.",
        "- Writes Graphiti: false.",
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

    if not regression_ok:
        raise SystemExit("POST_GRAPHITI_REPLAY_QUERY_REGRESSION_FAILED")

if __name__ == "__main__":
    main()

