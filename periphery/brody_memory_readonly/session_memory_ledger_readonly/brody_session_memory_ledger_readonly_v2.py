import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


FALSE_KEYS = [
    "memory_decision",
    "allowed_to_decide",
    "emits_act",
    "emits_allow_hold_block",
    "emits_verdict",
    "kernel_mutation",
    "x108_mutation",
    "x108_runtime_binding",
    "x108_merge",
]

TRUE_KEYS = [
    "readonly",
    "response_only",
    "no_external_model_call",
    "no_network_call",
]

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
    "brody_role": "SESSION_MEMORY_LEDGER_READONLY",
    "decision_authority": "KX108_ONLY",
    "ui": False,
    "auto_triage": False,
    "graphiti_index_write": False,
    "memory_intake": False,
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256((value or "").encode("utf-8")).hexdigest()


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def load_json_from_raw(path: Path):
    raw = path.read_text(encoding="utf-8", errors="ignore").strip()
    try:
        return json.loads(raw)
    except Exception:
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            return json.loads(raw[start:end + 1])
        raise RuntimeError("BRODY_RESPONSE_JSON_PARSE_FAILED")


def validate_brody_response(resp: dict):
    for key in TRUE_KEYS:
        if resp.get(key) is not True:
            raise RuntimeError(f"BOUNDARY_TRUE_KEY_FAILED:{key}={resp.get(key)}")

    for key in FALSE_KEYS:
        if resp.get(key) is not False:
            raise RuntimeError(f"BOUNDARY_FALSE_KEY_FAILED:{key}={resp.get(key)}")

    if resp.get("decision_authority") != "KX108_ONLY":
        raise RuntimeError(f"BAD_DECISION_AUTHORITY={resp.get('decision_authority')}")

    if resp.get("real_llm_connected") is not False:
        raise RuntimeError("REAL_LLM_CONNECTED_MUST_BE_FALSE")

    if resp.get("model_provider_bound") is not False:
        raise RuntimeError("MODEL_PROVIDER_BOUND_MUST_BE_FALSE")


def load_index(session_dir: Path):
    index_path = session_dir / "SESSION_INDEX.json"
    if index_path.exists():
        return json.loads(index_path.read_text(encoding="utf-8"))
    return {
        "status": "BRODY_SESSION_MEMORY_LEDGER_READONLY_V2_INDEX",
        "session_id": None,
        "created_at": now_iso(),
        "record_count": 0,
        "latest_event_hash": "GENESIS",
        "records": [],
        **BOUNDARY,
    }


def write_md_record(path: Path, record: dict):
    lines = []
    lines.append("# BRODY SESSION MEMORY LEDGER RECORD — READONLY V2")
    lines.append("")
    lines.append(f"- status: {record['status']}")
    lines.append(f"- session_id: {record['session_id']}")
    lines.append(f"- sequence: {record['sequence']}")
    lines.append(f"- created_at: {record['created_at']}")
    lines.append(f"- memory_query: {record.get('memory_query')}")
    lines.append(f"- packet_results_count: {record.get('packet_results_count')}")
    lines.append(f"- event_hash: {record['event_hash']}")
    lines.append(f"- previous_event_hash: {record['previous_event_hash']}")
    lines.append("")
    lines.append("## User input")
    lines.append("")
    lines.append(record.get("user_input", ""))
    lines.append("")
    lines.append("## Brody response")
    lines.append("")
    lines.append(record.get("response_md", ""))
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    for key, value in BOUNDARY.items():
        lines.append(f"- {key}: {value}")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_record(user_input: str, response: dict, session_dir: Path, session_id: str):
    validate_brody_response(response)

    session_dir.mkdir(parents=True, exist_ok=True)
    records_dir = session_dir / "records"
    records_dir.mkdir(parents=True, exist_ok=True)

    index = load_index(session_dir)
    if not index.get("session_id"):
        index["session_id"] = session_id

    sequence = int(index.get("record_count", 0)) + 1
    previous_hash = index.get("latest_event_hash", "GENESIS")

    response_md = response.get("response_md", "")
    response_canon = canonical_json(response)

    base_record = {
        "status": "BRODY_SESSION_MEMORY_LEDGER_READONLY_V2_RECORD",
        "created_at": now_iso(),
        "session_id": session_id,
        "sequence": sequence,
        "user_input": user_input,
        "user_input_sha256": sha256_text(user_input),
        "memory_query": response.get("memory_query", ""),
        "packet_results_count": response.get("packet_results_count", 0),
        "response_md": response_md,
        "response_md_sha256": sha256_text(response_md),
        "response_json_sha256": sha256_text(response_canon),
        "previous_event_hash": previous_hash,
        "triage_status": "NOT_APPLIED_NEXT_PALIER",
        "memory_intake_status": "TRACE_ONLY_NOT_INDEXED",
        "graphiti_index_write": False,
        "auto_triage": False,
        **BOUNDARY,
    }

    event_hash = sha256_text(previous_hash + canonical_json(base_record))
    record = dict(base_record)
    record["event_hash"] = event_hash

    stem = f"{sequence:04d}_{event_hash[:12]}"
    record_json = records_dir / f"{stem}.json"
    record_md = records_dir / f"{stem}.md"

    record_json.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    write_md_record(record_md, record)

    jsonl_path = session_dir / "SESSION_LEDGER.jsonl"
    with jsonl_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    index["record_count"] = sequence
    index["updated_at"] = now_iso()
    index["latest_event_hash"] = event_hash
    index["records"].append({
        "sequence": sequence,
        "event_hash": event_hash,
        "record_json": str(record_json),
        "record_md": str(record_md),
        "user_input_sha256": record["user_input_sha256"],
        "response_md_sha256": record["response_md_sha256"],
        "memory_query": record["memory_query"],
        "packet_results_count": record["packet_results_count"],
    })

    index_path = session_dir / "SESSION_INDEX.json"
    index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "status": "BRODY_SESSION_MEMORY_LEDGER_READONLY_V2_PASS",
        "created_at": now_iso(),
        "session_id": session_id,
        "session_dir": str(session_dir),
        "sequence": sequence,
        "event_hash": event_hash,
        "previous_event_hash": previous_hash,
        "record_json": str(record_json),
        "record_md": str(record_md),
        "session_index": str(index_path),
        "session_ledger_jsonl": str(jsonl_path),
        "memory_query": record["memory_query"],
        "packet_results_count": record["packet_results_count"],
        **BOUNDARY,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", required=True)
    parser.add_argument("--response-raw", required=True)
    parser.add_argument("--session-dir", required=True)
    parser.add_argument("--session-id", required=True)
    args = parser.parse_args()

    response = load_json_from_raw(Path(args.response_raw))
    result = build_record(
        user_input=args.user,
        response=response,
        session_dir=Path(args.session_dir),
        session_id=args.session_id,
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
