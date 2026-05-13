import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

BOUNDARY = {
    "readonly": True,
    "response_only": True,
    "project_intake_capture": True,
    "auto_presave": True,
    "source_tracking": True,
    "human_validation_required": True,
    "pending_not_canon": True,
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
    "brody_role": "PROJECT_INTAKE_CAPTURE_BUFFER_READONLY",
    "memory_role": "GUIDE_CONTEXT_NAVIGATION_ONLY",
}

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".lake",
    ".elan",
    "bin",
    "obj",
    "dist",
    "build",
}

EXTENSIONS = {
    ".txt",
    ".md",
    ".json",
    ".jsonl",
    ".csv",
    ".ps1",
    ".py",
    ".docx",
    ".pdf",
    ".zip",
    ".lean",
    ".tla",
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def dt_from_ts(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def sha256_file(path: Path, max_bytes: int) -> str:
    h = hashlib.sha256()
    total = 0
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            total += len(chunk)
            if total > max_bytes:
                break
            h.update(chunk)
    return h.hexdigest()


def excluded(path: Path) -> bool:
    parts = set(path.parts)
    return bool(parts & EXCLUDE_DIRS)


def classify_file(path: Path) -> dict:
    name = path.name.upper()
    suffix = path.suffix.lower()

    if name.startswith("CURRENT_"):
        kind = "POINTER"
        priority = "HIGH"
    elif "SUMMARY" in name or "REPORT" in name or "VALIDATE" in name or "AUDIT" in name:
        kind = "AUDIT_OR_REPORT"
        priority = "HIGH"
    elif suffix in {".docx", ".pdf", ".md", ".txt"}:
        kind = "DOCUMENT"
        priority = "MEDIUM"
    elif suffix == ".zip":
        kind = "ARTIFACT_ZIP"
        priority = "MEDIUM"
    elif suffix in {".py", ".ps1", ".lean", ".tla"}:
        kind = "CODE_OR_PROOF"
        priority = "MEDIUM"
    elif suffix in {".json", ".jsonl", ".csv"}:
        kind = "DATA_OR_TRACE"
        priority = "MEDIUM"
    else:
        kind = "OTHER"
        priority = "LOW"

    return {
        "capture_kind": kind,
        "proposed_review_priority": priority,
        "pending_zone": "PENDING_HUMAN_REVIEW",
        "learning_state": "PENDING_NOT_CANON",
        "human_decision": "UNDECIDED",
    }


def iter_files(scan_roots, since_hours: int, limit: int, max_bytes: int):
    cutoff = datetime.now(timezone.utc).timestamp() - (since_hours * 3600)
    seen = {}

    for root in scan_roots:
        root = Path(root)
        if not root.exists():
            continue

        for path in root.rglob("*"):
            if len(seen) >= limit:
                break

            if not path.is_file():
                continue

            if excluded(path):
                continue

            suffix = path.suffix.lower()
            if suffix not in EXTENSIONS:
                continue

            try:
                stat = path.stat()
            except Exception:
                continue

            is_pointer = path.name.upper().startswith("CURRENT_")
            is_recent = stat.st_mtime >= cutoff

            if not is_pointer and not is_recent:
                continue

            if stat.st_size > max_bytes:
                # Still capture metadata but mark it as not fully hashed.
                pass

            seen[str(path)] = path

    return list(seen.values())[:limit]


def make_record(path: Path, index: int, prev_hash: str, max_bytes: int):
    stat = path.stat()
    cls = classify_file(path)

    full_hash = None
    hash_mode = "full"
    if stat.st_size > max_bytes:
        hash_mode = "partial_max_bytes"
    full_hash = sha256_file(path, max_bytes=max_bytes)

    record = {
        "index": index,
        "path": str(path),
        "name": path.name,
        "suffix": path.suffix.lower(),
        "size_bytes": stat.st_size,
        "modified_at": dt_from_ts(stat.st_mtime),
        "sha256": full_hash,
        "hash_mode": hash_mode,
        "created_at": now_iso(),
        **cls,
        **BOUNDARY,
    }

    seed = json.dumps(
        {
            "prev": prev_hash,
            "path": str(path),
            "sha256": full_hash,
            "modified_at": record["modified_at"],
            "size_bytes": stat.st_size,
            "class": cls,
        },
        ensure_ascii=False,
        sort_keys=True,
    )

    record["prev_event_hash"] = prev_hash
    record["event_hash"] = sha256_text(seed)

    return record


def write_jsonl(path: Path, rows):
    with path.open("w", encoding="utf-8", errors="ignore") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--label", default="PROJECT_INTAKE_CAPTURE")
    parser.add_argument("--since-hours", type=int, default=72)
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--max-bytes", type=int, default=25 * 1024 * 1024)
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[3]
    workspace_root = repo_root.parent

    scan_roots = [
        workspace_root,
        repo_root,
        repo_root / "periphery",
        workspace_root / "_local_audits",
    ]

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    files = iter_files(scan_roots, args.since_hours, args.limit, args.max_bytes)

    records = []
    prev = "GENESIS_BRODY_PROJECT_INTAKE_CAPTURE_BUFFER_READONLY_V1"
    for idx, path in enumerate(files, start=1):
        record = make_record(path, idx, prev, args.max_bytes)
        prev = record["event_hash"]
        records.append(record)

    kinds = {}
    priorities = {}
    for r in records:
        kinds[r["capture_kind"]] = kinds.get(r["capture_kind"], 0) + 1
        priorities[r["proposed_review_priority"]] = priorities.get(r["proposed_review_priority"], 0) + 1

    records_jsonl = out_dir / "BRODY_PROJECT_INTAKE_CAPTURE_RECORDS.jsonl"
    records_json = out_dir / "BRODY_PROJECT_INTAKE_CAPTURE_RECORDS.json"
    summary_json = out_dir / "BRODY_PROJECT_INTAKE_CAPTURE_SUMMARY.json"
    report_md = out_dir / "BRODY_PROJECT_INTAKE_CAPTURE_REPORT.md"

    write_jsonl(records_jsonl, records)
    records_json.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = {
        "status": "BRODY_PROJECT_INTAKE_CAPTURE_BUFFER_READONLY_V1_PASS",
        "created_at": now_iso(),
        "label": args.label,
        "workspace_root": str(workspace_root),
        "repo_root": str(repo_root),
        "since_hours": args.since_hours,
        "captured_file_count": len(records),
        "capture_kind_counts": kinds,
        "review_priority_counts": priorities,
        "latest_event_hash": prev,
        "outputs": {
            "records_jsonl": str(records_jsonl),
            "records_json": str(records_json),
            "summary_json": str(summary_json),
            "report_md": str(report_md),
        },
        "next": "BUILD_BRODY_SESSION_PRESAVE_BUFFER_READONLY_V1",
        **BOUNDARY,
    }

    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# BRODY PROJECT INTAKE CAPTURE BUFFER READONLY V1",
        "",
        f"- status: {summary['status']}",
        f"- label: {summary['label']}",
        f"- captured_file_count: {summary['captured_file_count']}",
        f"- since_hours: {summary['since_hours']}",
        f"- latest_event_hash: {summary['latest_event_hash']}",
        "",
        "## Meaning",
        "",
        "This block captures what enters the project field.",
        "It preserves traces and prepares pending review records.",
        "It does not decide what becomes memory.",
        "It does not write Graphiti.",
        "",
        "## Boundary",
        "",
        "- Project intake capture: true",
        "- Auto presave: true",
        "- Source tracking: true",
        "- Human validation required: true",
        "- Pending not canon: true",
        "- Graphiti write: false",
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
