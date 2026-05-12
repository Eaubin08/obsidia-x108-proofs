import argparse
import hashlib
import json
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
    "decision_authority": "KX108_ONLY",
    "brody_role": "GRAPHITI_CANDIDATE_IMPORT_DRY_RUN_READONLY",
    "ui": False,
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_kv_file(path: Path) -> dict:
    out = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def load_jsonl(path: Path, max_records: int):
    if not path.exists():
        raise RuntimeError(f"MISSING_CANDIDATES_JSONL={path}")

    records = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except Exception as exc:
            raise RuntimeError(f"BAD_JSONL_LINE={exc}") from exc

        if max_records and len(records) >= max_records:
            break

    return records


def stable_record_id(record: dict, idx: int) -> str:
    raw = json.dumps(record, ensure_ascii=False, sort_keys=True)
    base = record.get("candidate_id") or record.get("id") or record.get("event_hash") or f"candidate_{idx}"
    return f"BRODY_GRAPHITI_DRYRUN_{str(base)}_{sha256_text(raw)[:12]}"


def normalize_tags(value):
    if isinstance(value, list):
        return sorted({str(x).strip().lower().replace(" ", "_") for x in value if str(x).strip()})
    if isinstance(value, str):
        parts = [x.strip() for x in value.replace(";", ",").split(",")]
        return sorted({x.lower().replace(" ", "_") for x in parts if x})
    return []


def pick_text(record: dict) -> str:
    for key in ("text", "content", "response_md", "excerpt", "summary", "memory_text", "input", "user"):
        val = record.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return json.dumps(record, ensure_ascii=False, sort_keys=True)


def build_import_plan(records):
    plan = []
    previous_hash = "GENESIS"

    for idx, record in enumerate(records, start=1):
        zone = str(record.get("zone") or record.get("triage_zone") or record.get("classification") or "").upper()
        if zone not in {"CRISTAL", "TRANSITION"}:
            continue

        text = pick_text(record)
        tags = normalize_tags(record.get("tags"))
        tags += ["brody", "readonly", "graphiti_candidate", "memory_candidate", zone.lower()]
        tags = sorted(set(tags))

        item = {
            "rank": len(plan) + 1,
            "dry_run_id": stable_record_id(record, idx),
            "source_zone": zone,
            "graphiti_action": "PLAN_ONLY_NO_WRITE",
            "target_label": "BrodyMemoryCandidate",
            "title": record.get("title") or record.get("query") or record.get("user") or f"Brody candidate {idx}",
            "text_preview": text[:1200],
            "tags": tags,
            "source_event_hash": record.get("event_hash") or record.get("latest_event_hash") or record.get("hash") or "",
            "source_record": record,
            "readonly": True,
            "graphiti_index_write": False,
            "memory_intake": False,
            "decision_authority": "KX108_ONLY",
            "kernel_mutation": False,
            "x108_merge": False,
        }

        item_hash_payload = dict(item)
        item_hash_payload["previous_hash"] = previous_hash
        event_hash = sha256_text(json.dumps(item_hash_payload, ensure_ascii=False, sort_keys=True))
        item["previous_hash"] = previous_hash
        item["event_hash"] = event_hash
        previous_hash = event_hash

        plan.append(item)

    return plan, previous_hash


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def write_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(x, ensure_ascii=False, sort_keys=True) for x in rows) + ("\n" if rows else ""),
        encoding="utf-8"
    )


def build_report(summary, plan):
    lines = []
    lines.append("# BRODY GRAPHITI CANDIDATE IMPORT DRY RUN — READONLY")
    lines.append("")
    lines.append(f"- status: {summary['status']}")
    lines.append(f"- records_count: {summary['records_count']}")
    lines.append(f"- import_plan_count: {summary['import_plan_count']}")
    lines.append(f"- graphiti_index_write: {str(summary['graphiti_index_write']).lower()}")
    lines.append(f"- memory_intake: {str(summary['memory_intake']).lower()}")
    lines.append(f"- decision_authority: {summary['decision_authority']}")
    lines.append("")
    lines.append("## Planned candidates")
    for item in plan:
        lines.append("")
        lines.append(f"### {item['rank']}. {item['title']}")
        lines.append(f"- zone: {item['source_zone']}")
        lines.append(f"- dry_run_id: {item['dry_run_id']}")
        lines.append(f"- event_hash: {item['event_hash']}")
        lines.append(f"- tags: {', '.join(item['tags'])}")
        lines.append("")
        lines.append(item["text_preview"][:500])
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append("This is a dry-run import plan only. No Graphiti write. No memory intake. No kernel mutation. KX108 remains sole decision authority.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates-jsonl", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--max-records", type=int, default=200)
    args = parser.parse_args()

    candidates_jsonl = Path(args.candidates_jsonl)
    out_dir = Path(args.out_dir)

    records = load_jsonl(candidates_jsonl, args.max_records)
    plan, latest_hash = build_import_plan(records)

    plan_jsonl = out_dir / "GRAPHITI_IMPORT_DRY_RUN_PLAN.jsonl"
    plan_json = out_dir / "GRAPHITI_IMPORT_DRY_RUN_PLAN.json"
    summary_json = out_dir / "GRAPHITI_IMPORT_DRY_RUN_SUMMARY.json"
    report_md = out_dir / "GRAPHITI_IMPORT_DRY_RUN_REPORT.md"

    summary = {
        "status": "BRODY_GRAPHITI_CANDIDATE_IMPORT_DRY_RUN_READONLY_PASS",
        "created_at": now_iso(),
        "source_candidates_jsonl": str(candidates_jsonl),
        "records_count": len(records),
        "import_plan_count": len(plan),
        "latest_event_hash": latest_hash,
        "outputs": {
            "plan_jsonl": str(plan_jsonl),
            "plan_json": str(plan_json),
            "summary_json": str(summary_json),
            "report_md": str(report_md),
        },
        **BOUNDARY,
    }

    write_jsonl(plan_jsonl, plan)
    write_json(plan_json, plan)
    write_json(summary_json, summary)
    report_md.write_text(build_report(summary, plan), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
