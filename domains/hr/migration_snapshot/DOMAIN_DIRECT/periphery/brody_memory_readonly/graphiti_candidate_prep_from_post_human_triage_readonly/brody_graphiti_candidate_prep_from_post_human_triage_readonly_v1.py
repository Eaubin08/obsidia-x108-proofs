import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

BOUNDARY = {
    "readonly": True,
    "response_only": True,
    "graphiti_candidate_prep": True,
    "post_human_keep_only": True,
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
    "brody_role": "GRAPHITI_CANDIDATE_PREP_FROM_POST_HUMAN_TRIAGE_READONLY",
    "memory_role": "GUIDE_CONTEXT_NAVIGATION_ONLY",
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


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


def read_jsonl(path: Path):
    rows = []
    with path.open("r", encoding="utf-8-sig", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows):
    with path.open("w", encoding="utf-8", errors="ignore") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def safe_read_excerpt(path_value, max_chars=4000):
    if not path_value:
        return ""
    path = Path(str(path_value))
    if not path.exists() or not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8-sig", errors="ignore")[:max_chars]
    except Exception:
        return ""


def clean_title(value):
    text = str(value or "").strip()
    if not text:
        return "BRODY_MEMORY_CANDIDATE"
    return text[:160]


def make_graphiti_candidate(row: dict, index: int, prev_hash: str):
    source_path = row.get("source_pointer_path")
    source_name = row.get("source_pointer_name") or Path(str(source_path)).name
    source_text = safe_read_excerpt(source_path)

    seed = json.dumps(
        {
            "source_pointer_path": source_path,
            "source_pointer_sha256": row.get("source_pointer_sha256"),
            "triage_event_hash": row.get("triage_event_hash"),
            "candidate_id": row.get("candidate_id"),
        },
        ensure_ascii=False,
        sort_keys=True,
    )

    gid = "BRODY_GRAPHITI_POST_HUMAN_" + sha256_text(seed)[:24]

    title = clean_title(source_name)
    text = source_text.strip()
    if not text:
        text = json.dumps(
            {
                "source_pointer_name": source_name,
                "source_pointer_path": source_path,
                "source_stage": row.get("source_stage"),
                "source_status_key": row.get("source_status_key"),
                "source_next_key": row.get("source_next_key"),
                "candidate_id": row.get("candidate_id"),
            },
            ensure_ascii=False,
            sort_keys=True,
        )

    record = {
        "index": index,
        "graphiti_candidate_id": gid,
        "source_candidate_id": row.get("candidate_id"),
        "title": title,
        "text": text,
        "text_preview": text[:500],
        "source_ref": source_path,
        "source_pointer_name": source_name,
        "source_pointer_sha256": row.get("source_pointer_sha256"),
        "source_stage": row.get("source_stage"),
        "source_review_lane": row.get("source_review_lane"),
        "source_status_key": row.get("source_status_key"),
        "source_next_key": row.get("source_next_key"),
        "human_decision": row.get("human_decision"),
        "candidate_zone": row.get("candidate_zone"),
        "triage_event_hash": row.get("triage_event_hash"),
        "import_status": "PREPARED_FOR_DRY_RUN_ONLY",
        "candidate_origin": "POST_HUMAN_REVIEW_KEEP",
        "tags": [
            "brody",
            "post_human_review",
            "graphiti_candidate",
            "memory_candidate",
            "readonly",
            "x108",
        ],
        "created_at": now_iso(),
        **BOUNDARY,
    }

    event_seed = json.dumps(
        {
            "prev": prev_hash,
            "graphiti_candidate_id": gid,
            "source_ref": source_path,
            "text_hash": sha256_text(text),
        },
        ensure_ascii=False,
        sort_keys=True,
    )

    record["prev_prep_event_hash"] = prev_hash
    record["prep_event_hash"] = sha256_text(event_seed)

    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    triage_ptr = workspace_root / "CURRENT_BRODY_POST_HUMAN_REVIEW_MEMORY_TRIAGE_READONLY_V1_VALIDATE.txt"
    if not triage_ptr.exists():
        raise RuntimeError(f"MISSING_POST_HUMAN_TRIAGE_VALIDATE_POINTER={triage_ptr}")

    kv = parse_kv(triage_ptr)

    memory_candidates_jsonl = Path(kv.get("MEMORY_CANDIDATES_JSONL", ""))
    triage_summary_json = Path(kv.get("SUMMARY_JSON", ""))

    if not memory_candidates_jsonl.exists():
        raise RuntimeError(f"MISSING_MEMORY_CANDIDATES_JSONL={memory_candidates_jsonl}")
    if not triage_summary_json.exists():
        raise RuntimeError(f"MISSING_TRIAGE_SUMMARY_JSON={triage_summary_json}")

    triage_summary = json.loads(triage_summary_json.read_text(encoding="utf-8-sig", errors="ignore"))

    if triage_summary.get("status") != "BRODY_POST_HUMAN_REVIEW_MEMORY_TRIAGE_READONLY_V1_PASS":
        raise RuntimeError(f"BAD_TRIAGE_STATUS={triage_summary.get('status')}")

    if int(triage_summary.get("keep_count", -1)) != 29:
        raise RuntimeError(f"BAD_KEEP_COUNT={triage_summary.get('keep_count')}")

    keep_rows = read_jsonl(memory_candidates_jsonl)

    if len(keep_rows) != 29:
        raise RuntimeError(f"BAD_KEEP_ROWS={len(keep_rows)}")

    prepared = []
    prev = "GENESIS_BRODY_GRAPHITI_CANDIDATE_PREP_FROM_POST_HUMAN_TRIAGE_READONLY_V1"

    for idx, row in enumerate(keep_rows, start=1):
        rec = make_graphiti_candidate(row, idx, prev)
        prev = rec["prep_event_hash"]
        prepared.append(rec)

    candidates_jsonl = out_dir / "BRODY_GRAPHITI_CANDIDATES_FROM_POST_HUMAN_TRIAGE_READONLY.jsonl"
    candidates_json = out_dir / "BRODY_GRAPHITI_CANDIDATES_FROM_POST_HUMAN_TRIAGE_READONLY.json"
    summary_json = out_dir / "BRODY_GRAPHITI_CANDIDATE_PREP_FROM_POST_HUMAN_TRIAGE_SUMMARY.json"
    report_md = out_dir / "BRODY_GRAPHITI_CANDIDATE_PREP_FROM_POST_HUMAN_TRIAGE_REPORT.md"

    write_jsonl(candidates_jsonl, prepared)
    candidates_json.write_text(json.dumps(prepared, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = {
        "status": "BRODY_GRAPHITI_CANDIDATE_PREP_FROM_POST_HUMAN_TRIAGE_READONLY_V1_PASS",
        "created_at": now_iso(),
        "source_triage_pointer": str(triage_ptr),
        "source_memory_candidates_jsonl": str(memory_candidates_jsonl),
        "source_triage_summary_json": str(triage_summary_json),
        "source_keep_count": triage_summary.get("keep_count"),
        "prepared_candidate_count": len(prepared),
        "latest_prep_event_hash": prev,
        "outputs": {
            "graphiti_candidates_jsonl": str(candidates_jsonl),
            "graphiti_candidates_json": str(candidates_json),
            "summary_json": str(summary_json),
            "report_md": str(report_md),
        },
        "next": "BUILD_BRODY_GRAPHITI_IMPORT_DRY_RUN_FROM_POST_HUMAN_PREP_READONLY_V1",
        **BOUNDARY,
    }

    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# BRODY GRAPHITI CANDIDATE PREP FROM POST HUMAN TRIAGE READONLY V1",
        "",
        f"- status: {summary['status']}",
        f"- source_keep_count: {summary['source_keep_count']}",
        f"- prepared_candidate_count: {summary['prepared_candidate_count']}",
        f"- latest_prep_event_hash: {summary['latest_prep_event_hash']}",
        "",
        "## Boundary",
        "",
        "- Graphiti candidate prep: true",
        "- Post-human KEEP only: true",
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
