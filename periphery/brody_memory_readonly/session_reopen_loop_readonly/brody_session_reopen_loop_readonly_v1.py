import argparse
import json
import os
import hashlib
from datetime import datetime, timezone
from pathlib import Path

BOUNDARY = {
    "readonly": True,
    "response_only": True,
    "session_reopen_loop": True,
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
    "brody_role": "SESSION_REOPEN_LOOP_READONLY",
    "memory_role": "GUIDE_CONTEXT_NAVIGATION_ONLY",
}

REOPEN_QUERIES = [
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
    cypher = """
    MATCH (n)
    WHERE n.id IN $ids OR n.name IN $ids
    RETURN coalesce(n.id, n.name) AS matched_id, labels(n) AS labels, properties(n) AS props
    """
    rows = []
    for r in session.run(cypher, ids=ids):
        props = dict(r["props"] or {})
        rows.append({
            "matched_id": str(r["matched_id"]) if r["matched_id"] is not None else None,
            "labels": list(r["labels"] or []),
            "title": props.get("title"),
            "source": props.get("source"),
            "record_hash": props.get("record_hash"),
            "memory_only": props.get("memory_only"),
            "graphiti_manual_apply": props.get("graphiti_manual_apply"),
            "kernel_mutation": props.get("kernel_mutation"),
            "x108_merge": props.get("x108_merge"),
        })
    return rows

def query_replay(session, q, limit):
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
    for r in session.run(cypher, q=q, limit=limit):
        props = dict(r["props"] or {})
        rows.append({
            "labels": list(r["labels"] or []),
            "id": props.get("id") or props.get("name"),
            "title": props.get("title"),
            "source": props.get("source"),
            "record_hash": props.get("record_hash"),
            "memory_only": props.get("memory_only"),
            "graphiti_manual_apply": props.get("graphiti_manual_apply"),
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

    close_ptr = workspace_root / "CURRENT_BRODY_MEMORY_PIPELINE_V2_CLOSE_REPORT_READONLY_VALIDATE.txt"
    micro_smoke_ptr = workspace_root / "CURRENT_BRODY_MEMORY_READONLY_MICRO_SMOKE_V1_VALIDATE.txt"
    apply_ptr = workspace_root / "CURRENT_BRODY_GRAPHITI_GUARDED_MANUAL_APPLY_EXECUTION_MEMORY_ONLY.txt"

    for p in [close_ptr, micro_smoke_ptr, apply_ptr]:
        if not p.exists():
            raise RuntimeError(f"MISSING_REQUIRED_POINTER={p}")

    close_kv = parse_pointer(close_ptr)
    smoke_kv = parse_pointer(micro_smoke_ptr)
    apply_kv = parse_pointer(apply_ptr)

    close_summary_json = Path(close_kv.get("SUMMARY_JSON", ""))
    smoke_summary_json = Path(smoke_kv.get("SUMMARY_JSON", ""))
    applied_ids_json = Path(apply_kv.get("APPLIED_IDS_JSON", ""))

    for p in [close_summary_json, smoke_summary_json, applied_ids_json]:
        if not p.exists():
            raise RuntimeError(f"MISSING_REQUIRED_SOURCE_JSON={p}")

    close_summary = load_json(close_summary_json)
    smoke_summary = load_json(smoke_summary_json)
    applied_ids = load_json(applied_ids_json)

    if isinstance(applied_ids, dict) and "applied_ids" in applied_ids:
        applied_ids = applied_ids["applied_ids"]

    if not isinstance(applied_ids, list):
        raise RuntimeError("APPLIED_IDS_NOT_LIST")

    expected_ids = sorted(set(str(x) for x in applied_ids))

    if close_summary.get("close_ok") is not True:
        raise RuntimeError("CLOSE_REPORT_NOT_OK")
    if smoke_summary.get("micro_smoke_ok") is not True:
        raise RuntimeError("MICRO_SMOKE_NOT_OK")
    if int(close_summary.get("manual_apply_write_executed_count", 0)) != 29:
        raise RuntimeError("BAD_CLOSE_MANUAL_APPLY_WRITE_COUNT")
    if int(smoke_summary.get("exact_found_count", 0)) != 29:
        raise RuntimeError("BAD_MICRO_SMOKE_EXACT_FOUND_COUNT")
    if len(expected_ids) != 29:
        raise RuntimeError(f"BAD_EXPECTED_IDS_COUNT={len(expected_ids)}")

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
        prev = "GENESIS_BRODY_SESSION_REOPEN_LOOP_READONLY_V1"

        for idx, q in enumerate(REOPEN_QUERIES, start=1):
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

    prefix_record = next((r for r in query_records if r["query"] == "BRODY_GRAPHITI_MEMORY_ONLY"), None)
    prefix_hits = int(prefix_record["applied_hit_count"]) if prefix_record else 0

    reopen_loop_ok = (
        len(expected_ids) == 29
        and len(found_ids) == 29
        and len(missing_ids) == 0
        and prefix_hits >= 29
        and all(r["hit_count"] > 0 for r in query_records)
    )

    context_packet = {
        "packet_type": "BRODY_SESSION_REOPEN_CONTEXT_PACKET_READONLY_V1",
        "created_at": now_iso(),
        "source_close_pointer": str(close_ptr),
        "source_micro_smoke_pointer": str(micro_smoke_ptr),
        "source_apply_pointer": str(apply_ptr),
        "expected_applied_id_count": len(expected_ids),
        "exact_found_count": len(found_ids),
        "missing_applied_id_count": len(missing_ids),
        "required_prefix_query": "BRODY_GRAPHITI_MEMORY_ONLY",
        "required_prefix_query_applied_hit_count": prefix_hits,
        "reopen_loop_ok": reopen_loop_ok,
        "memory_records_preview": exact_rows[:29],
        "query_records_preview": query_records,
        "next": "BUILD_BRODY_MEMORY_SCHEDULER_READONLY_V1",
        **BOUNDARY,
    }

    exact_json = out_dir / "BRODY_SESSION_REOPEN_EXACT_RECORDS.json"
    queries_jsonl = out_dir / "BRODY_SESSION_REOPEN_QUERY_RECORDS.jsonl"
    queries_json = out_dir / "BRODY_SESSION_REOPEN_QUERY_RECORDS.json"
    missing_json = out_dir / "BRODY_SESSION_REOPEN_MISSING_IDS.json"
    context_packet_json = out_dir / "BRODY_SESSION_REOPEN_CONTEXT_PACKET.json"
    prompt_context_md = out_dir / "BRODY_SESSION_REOPEN_PROMPT_CONTEXT.md"
    summary_json = out_dir / "BRODY_SESSION_REOPEN_LOOP_SUMMARY.json"
    report_md = out_dir / "BRODY_SESSION_REOPEN_LOOP_REPORT.md"

    exact_json.write_text(json.dumps(exact_rows, indent=2, ensure_ascii=False), encoding="utf-8")
    write_jsonl(queries_jsonl, query_records)
    queries_json.write_text(json.dumps(query_records, indent=2, ensure_ascii=False), encoding="utf-8")
    missing_json.write_text(json.dumps(missing_ids, indent=2, ensure_ascii=False), encoding="utf-8")
    context_packet_json.write_text(json.dumps(context_packet, indent=2, ensure_ascii=False), encoding="utf-8")

    prompt_lines = [
        "# BRODY SESSION REOPEN PROMPT CONTEXT",
        "",
        "## State",
        "",
        f"- close_ok: {str(close_summary.get('close_ok')).lower()}",
        f"- micro_smoke_ok: {str(smoke_summary.get('micro_smoke_ok')).lower()}",
        f"- expected_applied_id_count: {len(expected_ids)}",
        f"- exact_found_count: {len(found_ids)}",
        f"- missing_applied_id_count: {len(missing_ids)}",
        f"- required_prefix_query_applied_hit_count: {prefix_hits}",
        f"- reopen_loop_ok: {str(reopen_loop_ok).lower()}",
        "",
        "## Boundary",
        "",
        "- Graphiti query read only.",
        "- No Graphiti write.",
        "- No Neo4j write.",
        "- No memory decision.",
        "- No ACT.",
        "- No verdict.",
        "- No kernel mutation.",
        "- No X108 runtime binding.",
        "- No X108 merge.",
        "",
        "## Next",
        "",
        "BUILD_BRODY_MEMORY_SCHEDULER_READONLY_V1",
    ]
    prompt_context_md.write_text("\n".join(prompt_lines), encoding="utf-8")

    summary = {
        "status": "BRODY_SESSION_REOPEN_LOOP_READONLY_V1_PASS" if reopen_loop_ok else "BRODY_SESSION_REOPEN_LOOP_READONLY_V1_FAIL",
        "created_at": now_iso(),
        "neo4j_uri": args.neo4j_uri,
        "source_close_pointer": str(close_ptr),
        "source_close_summary_json": str(close_summary_json),
        "source_micro_smoke_pointer": str(micro_smoke_ptr),
        "source_micro_smoke_summary_json": str(smoke_summary_json),
        "source_apply_pointer": str(apply_ptr),
        "source_applied_ids_json": str(applied_ids_json),
        "expected_applied_id_count": len(expected_ids),
        "exact_found_count": len(found_ids),
        "missing_applied_id_count": len(missing_ids),
        "required_prefix_query": "BRODY_GRAPHITI_MEMORY_ONLY",
        "required_prefix_query_applied_hit_count": prefix_hits,
        "query_count": len(query_records),
        "query_records_pass_count": len([r for r in query_records if r["hit_count"] > 0]),
        "context_packet_record_count": len(exact_rows),
        "close_report_reused": True,
        "micro_smoke_reused": True,
        "reopen_loop_ok": reopen_loop_ok,
        "latest_reopen_event_hash": prev,
        "outputs": {
            "exact_json": str(exact_json),
            "queries_jsonl": str(queries_jsonl),
            "queries_json": str(queries_json),
            "missing_json": str(missing_json),
            "context_packet_json": str(context_packet_json),
            "prompt_context_md": str(prompt_context_md),
            "summary_json": str(summary_json),
            "report_md": str(report_md),
        },
        "next": "BUILD_BRODY_MEMORY_SCHEDULER_READONLY_V1",
        **BOUNDARY,
    }

    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    report_lines = [
        "# BRODY SESSION REOPEN LOOP READONLY V1",
        "",
        f"- status: {summary['status']}",
        f"- expected_applied_id_count: {summary['expected_applied_id_count']}",
        f"- exact_found_count: {summary['exact_found_count']}",
        f"- missing_applied_id_count: {summary['missing_applied_id_count']}",
        f"- required_prefix_query: {summary['required_prefix_query']}",
        f"- required_prefix_query_applied_hit_count: {summary['required_prefix_query_applied_hit_count']}",
        f"- query_count: {summary['query_count']}",
        f"- query_records_pass_count: {summary['query_records_pass_count']}",
        f"- context_packet_record_count: {summary['context_packet_record_count']}",
        f"- reopen_loop_ok: {str(summary['reopen_loop_ok']).lower()}",
        "",
        "## Boundary",
        "",
        "- Graphiti query read: true.",
        "- Graphiti write: false.",
        "- Neo4j write: false.",
        "- Memory intake: false.",
        "- Memory decision: false.",
        "- Emits ACT: false.",
        "- Emits verdict: false.",
        "- Kernel mutation: false.",
        "- X108 runtime binding: false.",
        "- X108 merge: false.",
        "",
        "## Next",
        "",
        summary["next"],
    ]

    report_md.write_text("\n".join(report_lines), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))

    if not reopen_loop_ok:
        raise SystemExit("BRODY_SESSION_REOPEN_LOOP_READONLY_FAILED")

if __name__ == "__main__":
    main()
