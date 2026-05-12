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
    "brody_role": "GRAPHITI_CANDIDATE_REVIEW_GATE_READONLY",
    "ui": False,
}

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
    "graphiti_index_write",
    "memory_intake",
]


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_jsonl(path):
    records = []
    p = Path(path)
    if not p.exists():
        raise RuntimeError(f"MISSING_PLAN_JSONL={path}")

    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        records.append(json.loads(line))

    return records


def flatten_values(obj):
    out = []

    if isinstance(obj, dict):
        for k, v in obj.items():
            out.append(str(k))
            out.extend(flatten_values(v))
    elif isinstance(obj, list):
        for v in obj:
            out.extend(flatten_values(v))
    elif obj is not None:
        out.append(str(obj))

    return out


def find_key_recursive(obj, wanted):
    wanted = wanted.lower()

    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(k).lower() == wanted:
                return v
        for v in obj.values():
            found = find_key_recursive(v, wanted)
            if found is not None:
                return found

    elif isinstance(obj, list):
        for v in obj:
            found = find_key_recursive(v, wanted)
            if found is not None:
                return found

    return None


def first_existing_key(obj, keys):
    for key in keys:
        value = find_key_recursive(obj, key)
        if value is not None:
            return value
    return None


def boundary_violations(record):
    violations = []

    for key in FALSE_KEYS:
        value = find_key_recursive(record, key)
        if value is True:
            violations.append(f"{key}=true")

    authority = find_key_recursive(record, "decision_authority")
    if authority is not None and authority != "KX108_ONLY":
        violations.append(f"decision_authority={authority}")

    return violations


def detect_zone(record):
    raw = first_existing_key(record, [
        "zone",
        "triage_zone",
        "triage_decision",
        "candidate_zone",
        "memory_zone",
        "source_zone",
    ])

    if raw is None:
        text = " ".join(flatten_values(record)).upper()
        if "CRISTAL" in text:
            return "CRISTAL"
        if "TRANSITION" in text:
            return "TRANSITION"
        if "NEANT" in text or "NÉANT" in text:
            return "NEANT"
        return "UNKNOWN"

    return str(raw).strip().upper().replace("É", "E")


def review_candidate(record, index, prev_hash):
    zone = detect_zone(record)
    violations = boundary_violations(record)

    reasons = []

    if violations:
        review = "REJECT_CANDIDATE"
        reasons.append("BOUNDARY_VIOLATION")
        reasons.extend(violations)
    elif zone == "CRISTAL":
        review = "ACCEPT_CANDIDATE"
        reasons.append("CRISTAL_MEMORY_CANDIDATE")
    elif zone == "TRANSITION":
        review = "REVIEW_CANDIDATE"
        reasons.append("TRANSITION_REQUIRES_REVIEW")
    elif zone == "NEANT":
        review = "REJECT_CANDIDATE"
        reasons.append("NEANT_REJECT_CANDIDATE_ONLY_NO_DELETE")
    else:
        review = "REVIEW_CANDIDATE"
        reasons.append("UNKNOWN_ZONE_REQUIRES_REVIEW")

    source_id = first_existing_key(record, ["id", "candidate_id", "event_id", "record_id"])
    title = first_existing_key(record, ["title", "memory_title", "source_title"])
    text = first_existing_key(record, ["text", "content", "excerpt", "summary", "memory_text"])
    tags = first_existing_key(record, ["tags", "memory_tags"])
    source_ref = first_existing_key(record, ["source_ref", "path", "source_path", "ref"])

    out = {
        "index": index,
        "review": review,
        "zone": zone,
        "reasons": reasons,
        "source_id": source_id,
        "title": title,
        "source_ref": source_ref,
        "tags": tags if isinstance(tags, list) else [],
        "text_preview": str(text or "")[:800],
        "graphiti_import_allowed": False,
        "graphiti_index_write": False,
        "memory_intake": False,
        "readonly": True,
        "decision_authority": "KX108_ONLY",
        "memory_decision": False,
        "allowed_to_decide": False,
        "emits_act": False,
        "emits_verdict": False,
        "kernel_mutation": False,
        "x108_runtime_binding": False,
        "x108_merge": False,
        "prev_event_hash": prev_hash,
    }

    canonical = json.dumps(out, sort_keys=True, ensure_ascii=False)
    out["event_hash"] = sha256_text(prev_hash + canonical)

    return out


def write_jsonl(path, rows):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + "\n",
        encoding="utf-8",
    )


def write_report(path, summary, reviews):
    lines = []
    lines.append("# BRODY GRAPHITI CANDIDATE REVIEW GATE — READONLY V1")
    lines.append("")
    lines.append(f"- status: {summary['status']}")
    lines.append(f"- source_plan_jsonl: {summary['source_plan_jsonl']}")
    lines.append(f"- record_count: {summary['record_count']}")
    lines.append(f"- accept_count: {summary['accept_count']}")
    lines.append(f"- review_count: {summary['review_count']}")
    lines.append(f"- reject_count: {summary['reject_count']}")
    lines.append(f"- graphiti_index_write: {str(summary['graphiti_index_write']).lower()}")
    lines.append(f"- memory_intake: {str(summary['memory_intake']).lower()}")
    lines.append(f"- decision_authority: {summary['decision_authority']}")
    lines.append("")
    lines.append("## Reviews")
    lines.append("")

    for r in reviews:
        lines.append(f"### {r['index']}. {r['review']}")
        lines.append(f"- zone: {r['zone']}")
        lines.append(f"- title: {r.get('title')}")
        lines.append(f"- source_ref: {r.get('source_ref')}")
        lines.append(f"- reasons: {', '.join(r.get('reasons') or [])}")
        lines.append(f"- event_hash: {r.get('event_hash')}")
        lines.append("")

    lines.append("## Boundary")
    lines.append("")
    lines.append("This gate reviews candidates only. It does not write to Graphiti, does not intake memory, does not decide, and does not mutate X108.")

    Path(path).write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan-jsonl", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    records = load_jsonl(args.plan_jsonl)

    reviews = []
    prev_hash = "GENESIS_BRODY_GRAPHITI_CANDIDATE_REVIEW_GATE_READONLY_V1"

    for index, record in enumerate(records, start=1):
        reviewed = review_candidate(record, index, prev_hash)
        prev_hash = reviewed["event_hash"]
        reviews.append(reviewed)

    accept_count = sum(1 for r in reviews if r["review"] == "ACCEPT_CANDIDATE")
    review_count = sum(1 for r in reviews if r["review"] == "REVIEW_CANDIDATE")
    reject_count = sum(1 for r in reviews if r["review"] == "REJECT_CANDIDATE")

    reviews_jsonl = out_dir / "REVIEW_GATE_RECORDS.jsonl"
    reviews_json = out_dir / "REVIEW_GATE_RECORDS.json"
    summary_json = out_dir / "REVIEW_GATE_SUMMARY.json"
    report_md = out_dir / "REVIEW_GATE_REPORT.md"

    write_jsonl(reviews_jsonl, reviews)
    reviews_json.write_text(json.dumps(reviews, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = {
        "status": "BRODY_GRAPHITI_CANDIDATE_REVIEW_GATE_READONLY_PASS",
        "created_at": now_iso(),
        "source_plan_jsonl": str(Path(args.plan_jsonl)),
        "record_count": len(records),
        "review_record_count": len(reviews),
        "accept_count": accept_count,
        "review_count": review_count,
        "reject_count": reject_count,
        "latest_event_hash": prev_hash,
        "outputs": {
            "review_records_jsonl": str(reviews_jsonl),
            "review_records_json": str(reviews_json),
            "review_summary_json": str(summary_json),
            "review_report_md": str(report_md),
        },
        **BOUNDARY,
    }

    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_report(report_md, summary, reviews)

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
