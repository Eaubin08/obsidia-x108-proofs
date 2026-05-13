import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

BOUNDARY = {
    "readonly": True,
    "response_only": True,
    "graphiti_import_dry_run": True,
    "post_human_prep_source": True,
    "dry_run": True,
    "manual_apply_required": True,
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
    "brody_role": "GRAPHITI_IMPORT_DRY_RUN_FROM_POST_HUMAN_PREP_READONLY",
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


def make_plan(candidate: dict, index: int, prev_hash: str):
    text = str(candidate.get("text") or "").strip()
    title = str(candidate.get("title") or "").strip()
    graphiti_candidate_id = str(candidate.get("graphiti_candidate_id") or "").strip()

    if not graphiti_candidate_id:
        seed = json.dumps(candidate, ensure_ascii=False, sort_keys=True)
        graphiti_candidate_id = "BRODY_GRAPHITI_DRYRUN_" + sha256_text(seed)[:24]

    if not title:
        title = graphiti_candidate_id

    if not text:
        text = json.dumps(candidate, ensure_ascii=False, sort_keys=True)

    text_hash = sha256_text(text)

    plan_seed = json.dumps(
        {
            "graphiti_candidate_id": graphiti_candidate_id,
            "source_ref": candidate.get("source_ref"),
            "text_hash": text_hash,
            "prep_event_hash": candidate.get("prep_event_hash"),
        },
        ensure_ascii=False,
        sort_keys=True,
    )

    import_plan_id = "BRODY_GRAPHITI_IMPORT_PLAN_" + sha256_text(plan_seed)[:24]

    params = {
        "id": graphiti_candidate_id,
        "title": title,
        "content": text,
        "summary": text[:1200],
        "source": "BRODY_POST_HUMAN_REVIEW_KEEP_DRY_RUN",
        "source_ref": candidate.get("source_ref"),
        "path": candidate.get("source_ref"),
        "candidate_origin": candidate.get("candidate_origin"),
        "source_stage": candidate.get("source_stage"),
        "source_review_lane": candidate.get("source_review_lane"),
        "source_status_key": candidate.get("source_status_key"),
        "source_next_key": candidate.get("source_next_key"),
        "human_decision": candidate.get("human_decision"),
        "candidate_zone": candidate.get("candidate_zone"),
        "triage_event_hash": candidate.get("triage_event_hash"),
        "prep_event_hash": candidate.get("prep_event_hash"),
        "text_hash": text_hash,
        "tags": candidate.get("tags", []),
        "memory_decision": False,
        "allowed_to_decide": False,
        "emits_act": False,
        "emits_verdict": False,
        "kernel_mutation": False,
        "x108_merge": False,
        "graphiti_index_write": False,
        "memory_intake": False,
        "dry_run": True,
        "manual_apply_required": True,
        "created_at": now_iso(),
    }

    record = {
        "index": index,
        "import_plan_id": import_plan_id,
        "graphiti_candidate_id": graphiti_candidate_id,
        "action": "MERGE_GRAPHITI_MEMORY_DOC_DRY_RUN",
        "target_label": "Doc",
        "cypher_preview": "MERGE (d:Doc {id: $id}) SET d.title = $title, d.content = $content, d.source = $source",
        "params": params,
        "dry_run_status": "PLANNED_NOT_EXECUTED",
        "write_would_target": "NEO4J_GRAPHITI_MEMORY_SURFACE",
        "write_executed": False,
        "created_at": now_iso(),
        **BOUNDARY,
    }

    event_seed = json.dumps(
        {
            "prev": prev_hash,
            "import_plan_id": import_plan_id,
            "graphiti_candidate_id": graphiti_candidate_id,
            "text_hash": text_hash,
        },
        ensure_ascii=False,
        sort_keys=True,
    )

    record["prev_dry_run_event_hash"] = prev_hash
    record["dry_run_event_hash"] = sha256_text(event_seed)

    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    prep_ptr = workspace_root / "CURRENT_BRODY_GRAPHITI_CANDIDATE_PREP_FROM_POST_HUMAN_TRIAGE_READONLY_V1_VALIDATE.txt"
    if not prep_ptr.exists():
        raise RuntimeError(f"MISSING_GRAPHITI_CANDIDATE_PREP_VALIDATE_POINTER={prep_ptr}")

    kv = parse_kv(prep_ptr)

    candidates_jsonl = Path(kv.get("GRAPHITI_CANDIDATES_JSONL", ""))
    prep_summary_json = Path(kv.get("SUMMARY_JSON", ""))

    if not candidates_jsonl.exists():
        raise RuntimeError(f"MISSING_GRAPHITI_CANDIDATES_JSONL={candidates_jsonl}")
    if not prep_summary_json.exists():
        raise RuntimeError(f"MISSING_PREP_SUMMARY_JSON={prep_summary_json}")

    prep_summary = json.loads(prep_summary_json.read_text(encoding="utf-8-sig", errors="ignore"))

    if prep_summary.get("status") != "BRODY_GRAPHITI_CANDIDATE_PREP_FROM_POST_HUMAN_TRIAGE_READONLY_V1_PASS":
        raise RuntimeError(f"BAD_PREP_STATUS={prep_summary.get('status')}")

    if int(prep_summary.get("prepared_candidate_count", -1)) != 29:
        raise RuntimeError(f"BAD_PREPARED_CANDIDATE_COUNT={prep_summary.get('prepared_candidate_count')}")

    candidates = read_jsonl(candidates_jsonl)

    if len(candidates) != 29:
        raise RuntimeError(f"BAD_CANDIDATE_COUNT={len(candidates)}")

    plan = []
    prev = "GENESIS_BRODY_GRAPHITI_IMPORT_DRY_RUN_FROM_POST_HUMAN_PREP_READONLY_V1"

    for idx, candidate in enumerate(candidates, start=1):
        rec = make_plan(candidate, idx, prev)
        prev = rec["dry_run_event_hash"]
        plan.append(rec)

    plan_jsonl = out_dir / "BRODY_GRAPHITI_IMPORT_DRY_RUN_FROM_POST_HUMAN_PREP_PLAN.jsonl"
    plan_json = out_dir / "BRODY_GRAPHITI_IMPORT_DRY_RUN_FROM_POST_HUMAN_PREP_PLAN.json"
    summary_json = out_dir / "BRODY_GRAPHITI_IMPORT_DRY_RUN_FROM_POST_HUMAN_PREP_SUMMARY.json"
    report_md = out_dir / "BRODY_GRAPHITI_IMPORT_DRY_RUN_FROM_POST_HUMAN_PREP_REPORT.md"

    write_jsonl(plan_jsonl, plan)
    plan_json.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = {
        "status": "BRODY_GRAPHITI_IMPORT_DRY_RUN_FROM_POST_HUMAN_PREP_READONLY_V1_PASS",
        "created_at": now_iso(),
        "source_prep_pointer": str(prep_ptr),
        "source_candidates_jsonl": str(candidates_jsonl),
        "source_prep_summary_json": str(prep_summary_json),
        "source_prepared_candidate_count": prep_summary.get("prepared_candidate_count"),
        "candidate_count": len(candidates),
        "import_plan_count": len(plan),
        "write_executed_count": 0,
        "latest_dry_run_event_hash": prev,
        "outputs": {
            "import_plan_jsonl": str(plan_jsonl),
            "import_plan_json": str(plan_json),
            "summary_json": str(summary_json),
            "report_md": str(report_md),
        },
        "next": "BUILD_BRODY_GRAPHITI_REVIEW_GATE_FROM_POST_HUMAN_DRY_RUN_READONLY_V1",
        **BOUNDARY,
    }

    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# BRODY GRAPHITI IMPORT DRY RUN FROM POST HUMAN PREP READONLY V1",
        "",
        f"- status: {summary['status']}",
        f"- candidate_count: {summary['candidate_count']}",
        f"- import_plan_count: {summary['import_plan_count']}",
        f"- write_executed_count: {summary['write_executed_count']}",
        f"- latest_dry_run_event_hash: {summary['latest_dry_run_event_hash']}",
        "",
        "## Boundary",
        "",
        "- Graphiti import dry-run: true",
        "- Dry run: true",
        "- Manual apply required: true",
        "- Graphiti write: false",
        "- Neo4j write executed: false",
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
