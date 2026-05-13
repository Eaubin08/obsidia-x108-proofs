import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


BOUNDARY_FALSE_KEYS = [
    "memory_decision",
    "allowed_to_decide",
    "emits_act",
    "emits_allow_hold_block",
    "emits_verdict",
    "kernel_mutation",
    "x108_mutation",
    "x108_runtime_binding",
    "x108_merge",
    "graphiti_index_write",
    "memory_intake",
]

DEFAULT_QUERIES = [
    ":who",
    ":boundary",
    ":trace",
    "explique X108 avec la mémoire actuelle",
    "explique les 34 arbres",
    "quel est ton rôle dans X108 proofs",
    "Graphiti",
    "kernel",
    "boundary",
    "trace mémoire",
    "tri mémoire Brody",
]


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_json(stdout):
    text = stdout.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < start:
        raise RuntimeError("NO_JSON_IN_TERMINAL_OUTPUT")
    return json.loads(text[start:end + 1])


def run_terminal_query(terminal_runner, query):
    proc = subprocess.run(
        [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(terminal_runner),
            "-Once",
            query,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if proc.returncode != 0:
        raise RuntimeError(
            "BRODY_TERMINAL_QUERY_FAILED\n"
            + "QUERY=" + query + "\n"
            + "STDOUT=" + proc.stdout + "\n"
            + "STDERR=" + proc.stderr
        )

    payload = extract_json(proc.stdout)
    return {
        "query": query,
        "stdout_sha256": sha256_text(proc.stdout),
        "payload": payload,
    }


def assert_boundary(payload):
    if payload.get("readonly") is not True:
        raise RuntimeError("READONLY_NOT_TRUE")

    if payload.get("decision_authority") != "KX108_ONLY":
        raise RuntimeError("BAD_DECISION_AUTHORITY")

    for key in BOUNDARY_FALSE_KEYS:
        if key in payload and payload.get(key) is not False:
            raise RuntimeError(f"BOUNDARY_FALSE_KEY_FAILED:{key}={payload.get(key)}")

    if payload.get("brody_role") != "TERMINAL_STRUCTURAL_DIALOGUE":
        raise RuntimeError(f"BAD_BRODY_ROLE={payload.get('brody_role')}")

    if payload.get("no_external_model_call") is not True:
        raise RuntimeError("NO_EXTERNAL_MODEL_CALL_NOT_TRUE")

    if payload.get("no_network_call") is not True:
        raise RuntimeError("NO_NETWORK_CALL_NOT_TRUE")


def classify_record(record):
    payload = record["payload"]
    response_md = payload.get("response_md", "") or ""
    query = record["query"]

    has_sources = "- " in response_md and "Sources" in response_md
    has_boundary = "Boundary" in response_md or "BOUNDARY" in response_md
    packet_count = int(payload.get("packet_results_count") or 0)

    return {
        "query": query,
        "memory_query": payload.get("memory_query", ""),
        "packet_results_count": packet_count,
        "has_sources": has_sources,
        "has_boundary": has_boundary,
        "version": payload.get("version"),
        "response_sha256": sha256_text(response_md),
        "stdout_sha256": record["stdout_sha256"],
        "readonly": payload.get("readonly"),
        "decision_authority": payload.get("decision_authority"),
        "brody_role": payload.get("brody_role"),
    }


def write_json(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def write_jsonl(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_report(path, summary, rows):
    lines = []
    lines.append("# BRODY MEMORY REPLAY + QUERY REGRESSION — READONLY")
    lines.append("")
    lines.append(f"- status: {summary['status']}")
    lines.append(f"- created_at: {summary['created_at']}")
    lines.append(f"- query_count: {summary['query_count']}")
    lines.append(f"- source_query_count: {summary['source_query_count']}")
    lines.append(f"- boundary_ok_count: {summary['boundary_ok_count']}")
    lines.append(f"- decision_authority: {summary['decision_authority']}")
    lines.append(f"- graphiti_index_write: {str(summary['graphiti_index_write']).lower()}")
    lines.append(f"- memory_intake: {str(summary['memory_intake']).lower()}")
    lines.append("")
    lines.append("## Queries")
    lines.append("")

    for row in rows:
        lines.append(f"### {row['query']}")
        lines.append(f"- memory_query: {row.get('memory_query')}")
        lines.append(f"- packet_results_count: {row.get('packet_results_count')}")
        lines.append(f"- has_sources: {str(row.get('has_sources')).lower()}")
        lines.append(f"- has_boundary: {str(row.get('has_boundary')).lower()}")
        lines.append(f"- response_sha256: {row.get('response_sha256')}")
        lines.append("")

    lines.append("## Boundary")
    lines.append("")
    lines.append("Replay regression only. No write. No ACT. No verdict. No kernel mutation. KX108 remains sole decision authority.")
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--terminal-runner", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--queries-json")
    args = parser.parse_args()

    terminal_runner = Path(args.terminal_runner)
    if not terminal_runner.exists():
        raise RuntimeError(f"MISSING_TERMINAL_RUNNER={terminal_runner}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.queries_json:
        queries = json.loads(Path(args.queries_json).read_text(encoding="utf-8"))
    else:
        queries = DEFAULT_QUERIES

    raw_records = []
    rows = []

    for q in queries:
        record = run_terminal_query(terminal_runner, q)
        assert_boundary(record["payload"])
        raw_records.append(record)
        rows.append(classify_record(record))

    source_query_count = sum(1 for r in rows if r["packet_results_count"] > 0)
    boundary_ok_count = sum(1 for r in rows if r["has_boundary"] is True)

    summary = {
        "status": "BRODY_MEMORY_REPLAY_QUERY_REGRESSION_READONLY_PASS",
        "created_at": now_iso(),
        "terminal_runner": str(terminal_runner),
        "query_count": len(rows),
        "source_query_count": source_query_count,
        "boundary_ok_count": boundary_ok_count,
        "records_jsonl": str(out_dir / "REPLAY_REGRESSION_RECORDS.jsonl"),
        "records_json": str(out_dir / "REPLAY_REGRESSION_RECORDS.json"),
        "raw_records_json": str(out_dir / "REPLAY_REGRESSION_RAW_RECORDS.json"),
        "report_md": str(out_dir / "REPLAY_REGRESSION_REPORT.md"),
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
        "brody_role": "MEMORY_REPLAY_QUERY_REGRESSION_READONLY",
        "decision_authority": "KX108_ONLY",
        "graphiti_index_write": False,
        "memory_intake": False,
        "dry_run": True,
        "ui": False,
    }

    write_jsonl(out_dir / "REPLAY_REGRESSION_RECORDS.jsonl", rows)
    write_json(out_dir / "REPLAY_REGRESSION_RECORDS.json", rows)
    write_json(out_dir / "REPLAY_REGRESSION_RAW_RECORDS.json", raw_records)
    write_json(out_dir / "REPLAY_REGRESSION_SUMMARY.json", summary)
    write_report(out_dir / "REPLAY_REGRESSION_REPORT.md", summary, rows)

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
