import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

BOUNDARY = {
    "readonly": True,
    "response_only": True,
    "presave_buffer": True,
    "manual_validation_required": True,
    "graphiti_index_write": False,
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
    "brody_role": "SESSION_PRESAVE_BUFFER_READONLY",
    "memory_role": "GUIDE_CONTEXT_NAVIGATION_ONLY",
}


POINTER_NAMES = [
    "CURRENT_BRODY_PROJECT_INTAKE_CAPTURE_BUFFER_READONLY.txt",
    "CURRENT_BRODY_TERMINAL_STRUCTURAL_DIALOGUE_READONLY_VALIDATE.txt",
    "CURRENT_BRODY_SESSION_MEMORY_LEDGER_READONLY_V2_VALIDATE.txt",
    "CURRENT_BRODY_AUTO_TRIAGE_MEMORY_INTAKE_READONLY_V1_VALIDATE.txt",
    "CURRENT_BRODY_CANDIDATE_EXPORT_FOR_GRAPHITI_READONLY_V1_VALIDATE.txt",
    "CURRENT_BRODY_GRAPHITI_CANDIDATE_IMPORT_DRY_RUN_READONLY_V1_VALIDATE.txt",
    "CURRENT_BRODY_GRAPHITI_CANDIDATE_REVIEW_GATE_READONLY_V1_VALIDATE.txt",
    "CURRENT_BRODY_GRAPHITI_IMPORT_APPLY_GUARDED_MANUAL_ONLY_V1_VALIDATE.txt",
    "CURRENT_BRODY_MEMORY_REPLAY_QUERY_REGRESSION_READONLY_V1_VALIDATE.txt",
    "CURRENT_BRODY_MEMORY_PIPELINE_READONLY_FREEZE_REPORT_V1_VALIDATE.txt",
    "CURRENT_BRODY_MEMORY_PIPELINE_FREEZE_REPORT_READONLY.txt",
    "CURRENT_BRODY_SESSION_MEMORY_LEDGER_READONLY.txt",
    "CURRENT_BRODY_AUTO_TRIAGE_MEMORY_INTAKE_READONLY.txt",
    "CURRENT_BRODY_CANDIDATE_EXPORT_FOR_GRAPHITI_READONLY.txt",
    "CURRENT_BRODY_GRAPHITI_CANDIDATE_REVIEW_GATE_READONLY.txt",
    "CURRENT_BRODY_GRAPHITI_IMPORT_APPLY_GUARDED_MANUAL_ONLY.txt",
    "CURRENT_BRODY_MEMORY_REPLAY_QUERY_REGRESSION_READONLY.txt",
]


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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


def maybe_path(value: str):
    if not value:
        return None
    try:
        p = Path(value)
        if p.exists():
            return str(p)
    except Exception:
        return None
    return None


def collect_pointer_files(workspace_root: Path, repo_root: Path, limit: int):
    found = {}

    for base in [workspace_root, repo_root]:
        for name in POINTER_NAMES:
            p = base / name
            if p.exists():
                found[str(p)] = p

    for base in [workspace_root, repo_root]:
        for p in sorted(base.glob("CURRENT_BRODY_*.txt")):
            found[str(p)] = p
            if len(found) >= limit:
                break

    return list(found.values())[:limit]


def build_record(path: Path, index: int, prev_hash: str):
    kv = parse_kv(path)
    refs = []
    for v in kv.values():
        mp = maybe_path(v)
        if mp:
            refs.append(mp)

    body = {
        "index": index,
        "pointer_path": str(path),
        "pointer_name": path.name,
        "sha256": sha256_file(path),
        "key_count": len(kv),
        "keys": kv,
        "referenced_existing_path_count": len(refs),
        "referenced_existing_paths": refs,
        "created_at": now_iso(),
        **BOUNDARY,
    }

    seed = json.dumps(
        {
            "prev": prev_hash,
            "pointer_path": str(path),
            "sha256": body["sha256"],
            "keys": kv,
        },
        ensure_ascii=False,
        sort_keys=True,
    )

    body["prev_event_hash"] = prev_hash
    body["event_hash"] = sha256_text(seed)
    return body


def write_jsonl(path: Path, rows):
    with path.open("w", encoding="utf-8", errors="ignore") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--label", default="MANUAL_PRESAVE")
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[3]
    workspace_root = repo_root.parent

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    pointers = collect_pointer_files(workspace_root, repo_root, args.limit)

    records = []
    prev = "GENESIS_BRODY_SESSION_PRESAVE_BUFFER_READONLY_V1"
    for idx, p in enumerate(pointers, start=1):
        record = build_record(p, idx, prev)
        prev = record["event_hash"]
        records.append(record)

    records_jsonl = out_dir / "BRODY_SESSION_PRESAVE_BUFFER_RECORDS.jsonl"
    records_json = out_dir / "BRODY_SESSION_PRESAVE_BUFFER_RECORDS.json"
    summary_json = out_dir / "BRODY_SESSION_PRESAVE_BUFFER_SUMMARY.json"
    report_md = out_dir / "BRODY_SESSION_PRESAVE_BUFFER_REPORT.md"

    write_jsonl(records_jsonl, records)
    records_json.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = {
        "status": "BRODY_SESSION_PRESAVE_BUFFER_READONLY_V1_PASS",
        "created_at": now_iso(),
        "label": args.label,
        "workspace_root": str(workspace_root),
        "repo_root": str(repo_root),
        "pointer_file_count": len(records),
        "latest_event_hash": prev,
        "outputs": {
            "records_jsonl": str(records_jsonl),
            "records_json": str(records_json),
            "summary_json": str(summary_json),
            "report_md": str(report_md),
        },
        "next": "BUILD_BRODY_SESSION_CLOSE_HUMAN_VALIDATION_GATE_READONLY_V1",
        **BOUNDARY,
    }

    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# BRODY SESSION PRESAVE BUFFER READONLY V1",
        "",
        f"- status: {summary['status']}",
        f"- label: {summary['label']}",
        f"- pointer_file_count: {summary['pointer_file_count']}",
        f"- latest_event_hash: {summary['latest_event_hash']}",
        "",
        "## Boundary",
        "",
        "- Graphiti write: false",
        "- Memory intake: false",
        "- Memory decision: false",
        "- Emits ACT: false",
        "- Emits verdict: false",
        "- Kernel mutation: false",
        "- X108 runtime binding: false",
        "- X108 merge: false",
        "- Manual validation required: true",
        "",
        "## Role",
        "",
        "This block creates a local presave buffer for session memory review.",
        "It does not write to Graphiti and does not canonize memory.",
        "",
        f"Next: {summary['next']}",
    ]

    report_md.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

