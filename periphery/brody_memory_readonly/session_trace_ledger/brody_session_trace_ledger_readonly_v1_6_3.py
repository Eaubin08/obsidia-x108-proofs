import argparse
import json
import hashlib
from pathlib import Path
from datetime import datetime

BOUNDARY = {
    "readonly": True,
    "memory_authority": False,
    "memory_decision": False,
    "allowed_to_decide": False,
    "emits_act": False,
    "kernel_binding": False,
    "x108_merge": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "decision_authority": "KX108_ONLY",
    "scope": "BRODY_SESSION_TRACE_LEDGER_PERIPHERY_ONLY"
}

def read_pointer(path: Path):
    if not path.exists():
        return {}
    out = {}
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out

def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest().upper()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--ledger-root", required=True)
    ap.add_argument("--event", required=True)
    ap.add_argument("--body", default="")
    ap.add_argument("--source", default="")
    ap.add_argument("--tags", default="")
    args = ap.parse_args()

    root = Path(args.root)
    ledger_root = Path(args.ledger_root)
    ledger_root.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    ts = now.strftime("%Y%m%d_%H%M%S")
    iso = now.isoformat()

    world_ptr = read_pointer(root / "_world_intake" / "CURRENT_BRODY_WORLD_SOURCE_INTAKE_READONLY.txt")
    graphiti_ptr = read_pointer(root / "CURRENT_GRAPHITI_READONLY_INDEX.txt")
    clean_ptr = read_pointer(root / "CURRENT_PROJECT_MEMORY_CLEAN_SOURCE_NO_INDEX.txt")

    session_id = f"BRODY_SESSION_TRACE_{ts}"
    run_dir = ledger_root / session_id
    run_dir.mkdir(parents=True, exist_ok=True)

    record = {
        "status": "BRODY_SESSION_TRACE_LEDGER_READONLY_RECORD_PASS",
        "date": ts,
        "iso": iso,
        "event": args.event,
        "body": args.body,
        "body_sha256": sha256_text(args.body),
        "source": args.source,
        "tags": [x.strip() for x in args.tags.split(",") if x.strip()],
        "world_intake_current": world_ptr,
        "graphiti_current": graphiti_ptr,
        "clean_source_current": clean_ptr,
        **BOUNDARY
    }

    record_json = json.dumps(record, ensure_ascii=False, sort_keys=True)
    record["record_sha256"] = sha256_text(record_json)

    json_path = run_dir / "SESSION_TRACE_RECORD.json"
    md_path = run_dir / "SESSION_TRACE_RECORD.md"
    ledger_jsonl = ledger_root / "BRODY_SESSION_TRACE_LEDGER_READONLY.jsonl"

    json_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    md = [
        "# BRODY SESSION TRACE LEDGER READONLY",
        "",
        f"- status: {record['status']}",
        f"- date: {record['date']}",
        f"- event: {record['event']}",
        f"- source: {record['source']}",
        f"- body_sha256: {record['body_sha256']}",
        f"- record_sha256: {record['record_sha256']}",
        "",
        "## Boundary",
        "",
        f"- readonly: {record['readonly']}",
        f"- memory_decision: {record['memory_decision']}",
        f"- decision_authority: {record['decision_authority']}",
        f"- kernel_binding: {record['kernel_binding']}",
        f"- x108_merge: {record['x108_merge']}",
        "",
        "## Body",
        "",
        "```text",
        args.body,
        "```",
        "",
        "## Current world intake",
        "",
        "```json",
        json.dumps(world_ptr, indent=2, ensure_ascii=False),
        "```",
        "",
        "## Current Graphiti",
        "",
        "```json",
        json.dumps(graphiti_ptr, indent=2, ensure_ascii=False),
        "```",
        ""
    ]
    md_path.write_text("\n".join(md), encoding="utf-8")

    with ledger_jsonl.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    current = root / "CURRENT_BRODY_SESSION_TRACE_LEDGER_READONLY.txt"
    current.write_text(
        "\n".join([
            f"CURRENT_BRODY_SESSION_TRACE_LEDGER_READONLY={run_dir}",
            f"RECORD_JSON={json_path}",
            f"RECORD_MD={md_path}",
            f"LEDGER_JSONL={ledger_jsonl}",
            f"STATUS={record['status']}",
            "MEMORY_DECISION=false",
            "DECISION_AUTHORITY=KX108_ONLY",
            "NEXT=WORLD_CONNECTOR_BRIDGE_READONLY"
        ]) + "\n",
        encoding="utf-8"
    )

    print(json.dumps({
        "status": record["status"],
        "run_dir": str(run_dir),
        "record_json": str(json_path),
        "record_md": str(md_path),
        "ledger_jsonl": str(ledger_jsonl),
        "record_sha256": record["record_sha256"],
        **BOUNDARY
    }, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
