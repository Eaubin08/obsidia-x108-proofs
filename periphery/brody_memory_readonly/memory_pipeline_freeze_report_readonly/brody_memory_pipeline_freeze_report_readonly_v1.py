import argparse
import json
import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path


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
    "graphiti_index_write": False,
    "memory_intake": False,
    "dry_run": True,
    "ui": False,
    "decision_authority": "KX108_ONLY",
    "brody_role": "MEMORY_PIPELINE_FREEZE_REPORT_READONLY",
}


PIPELINE_STAGES = [
    "GRAPHITI_READONLY_INDEX",
    "BRODY_NEO4J_GUIDE_BRIDGE_READONLY",
    "BRODY_CONTEXT_PACKET_QUERY_READONLY",
    "BRODY_CONTEXT_PACKET_CONSUMER_READONLY",
    "BRODY_CONTENT_HYDRATION_READONLY",
    "BRODY_LOCAL_RESPONSE_ENGINE_READONLY",
    "BRODY_TERMINAL_STRUCTURAL_DIALOGUE_READONLY",
    "BRODY_SESSION_MEMORY_LEDGER_READONLY",
    "BRODY_AUTO_TRIAGE_MEMORY_INTAKE_READONLY",
    "BRODY_CANDIDATE_EXPORT_FOR_GRAPHITI_READONLY",
    "BRODY_GRAPHITI_CANDIDATE_IMPORT_DRY_RUN_READONLY",
    "BRODY_GRAPHITI_CANDIDATE_REVIEW_GATE_READONLY",
    "BRODY_GRAPHITI_IMPORT_APPLY_GUARDED_MANUAL_ONLY",
    "BRODY_MEMORY_REPLAY_QUERY_REGRESSION_READONLY",
]


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run_git(x108: Path, args):
    p = subprocess.run(
        ["git", "-C", str(x108)] + args,
        text=True,
        capture_output=True,
        check=True,
    )
    return p.stdout.strip()


def parse_pointer(path: Path):
    data = {}
    if not path.exists():
        return data
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            data[k.strip()] = v.strip()
    return data


def collect_pointer_files(root: Path, x108: Path):
    files = []

    for base in [root, x108]:
        if base.exists():
            files.extend(sorted(base.glob("CURRENT_BRODY*.txt")))
            files.extend(sorted(base.glob("CURRENT_GRAPHITI*.txt")))

    # Keep unique normalized paths.
    seen = set()
    unique = []
    for p in files:
        key = str(p).lower()
        if key not in seen:
            unique.append(p)
            seen.add(key)
    return unique


def classify_stage(stage, pointer_records):
    matches = []
    stage_norm = stage.lower()

    for rec in pointer_records:
        blob = json.dumps(rec, ensure_ascii=False).lower()
        if stage_norm in blob:
            matches.append(rec)

    if matches:
        return {
            "stage": stage,
            "status": "FOUND",
            "pointer_count": len(matches),
            "pointers": [m["path"] for m in matches],
        }

    return {
        "stage": stage,
        "status": "NOT_FOUND_IN_POINTERS",
        "pointer_count": 0,
        "pointers": [],
    }


def build_report(root: Path, x108: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)

    git_status = run_git(x108, ["status", "-sb"])
    git_head = run_git(x108, ["rev-parse", "--short", "HEAD"])
    git_log = run_git(x108, ["log", "-15", "--oneline"])

    pointer_files = collect_pointer_files(root, x108)
    pointer_records = []

    for p in pointer_files:
        parsed = parse_pointer(p)
        pointer_records.append({
            "path": str(p),
            "name": p.name,
            "keys": parsed,
            "sha256": sha256_text(p.read_text(encoding="utf-8", errors="ignore")),
        })

    stages = [classify_stage(stage, pointer_records) for stage in PIPELINE_STAGES]
    found_count = sum(1 for s in stages if s["status"] == "FOUND")

    summary = {
        "status": "BRODY_MEMORY_PIPELINE_FREEZE_REPORT_READONLY_PASS",
        "created_at": now_iso(),
        "root": str(root),
        "x108": str(x108),
        "head": git_head,
        "git_status": git_status,
        "pipeline_stage_count": len(stages),
        "pipeline_stage_found_count": found_count,
        "pipeline_stage_missing_count": len(stages) - found_count,
        "pointer_file_count": len(pointer_records),
        "stages": stages,
        "pointer_records": pointer_records,
        "git_log_15": git_log.splitlines(),
        "outputs": {},
        **BOUNDARY,
    }

    json_path = out_dir / "BRODY_MEMORY_PIPELINE_FREEZE_REPORT_SUMMARY.json"
    records_path = out_dir / "BRODY_MEMORY_PIPELINE_POINTER_RECORDS.json"
    md_path = out_dir / "BRODY_MEMORY_PIPELINE_FREEZE_REPORT.md"

    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    records_path.write_text(json.dumps(pointer_records, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("# BRODY MEMORY PIPELINE — READONLY FREEZE REPORT V1")
    lines.append("")
    lines.append(f"- status: {summary['status']}")
    lines.append(f"- created_at: {summary['created_at']}")
    lines.append(f"- head: {summary['head']}")
    lines.append(f"- git_status: `{summary['git_status']}`")
    lines.append(f"- pipeline_stage_count: {summary['pipeline_stage_count']}")
    lines.append(f"- pipeline_stage_found_count: {summary['pipeline_stage_found_count']}")
    lines.append(f"- pipeline_stage_missing_count: {summary['pipeline_stage_missing_count']}")
    lines.append(f"- pointer_file_count: {summary['pointer_file_count']}")
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    for k, v in BOUNDARY.items():
        lines.append(f"- {k}: {str(v).lower() if isinstance(v, bool) else v}")
    lines.append("")
    lines.append("## Pipeline stages")
    lines.append("")
    for s in stages:
        lines.append(f"### {s['stage']}")
        lines.append(f"- status: {s['status']}")
        lines.append(f"- pointer_count: {s['pointer_count']}")
        for p in s["pointers"]:
            lines.append(f"  - {p}")
        lines.append("")
    lines.append("## Last commits")
    lines.append("")
    for line in summary["git_log_15"]:
        lines.append(f"- `{line}`")

    md_path.write_text("\n".join(lines), encoding="utf-8")

    summary["outputs"] = {
        "summary_json": str(json_path),
        "pointer_records_json": str(records_path),
        "report_md": str(md_path),
    }
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--x108", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    build_report(Path(args.root), Path(args.x108), Path(args.out_dir))


if __name__ == "__main__":
    main()

