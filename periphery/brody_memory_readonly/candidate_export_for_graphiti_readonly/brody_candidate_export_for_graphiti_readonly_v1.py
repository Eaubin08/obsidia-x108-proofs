import argparse
import hashlib
import json
import re
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
    "neo4j_role": "LIVE_GRAPH_MEMORY_SURFACE_ONLY",
    "brody_role": "CANDIDATE_EXPORT_FOR_GRAPHITI_READONLY",
    "decision_authority": "KX108_ONLY",
    "graphiti_index_write": False,
    "memory_intake": False,
    "auto_triage": False,
    "candidate_export": True,
    "ui": False,
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def clean_text(value, max_chars=1800):
    if value is None:
        return ""
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text[:max_chars]


def read_jsonl(path: Path):
    records = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        records.append(json.loads(line))
    return records


def pick(record, *keys, default=""):
    for key in keys:
        if key in record and record.get(key) not in (None, ""):
            return record.get(key)
    return default


def detect_zone(record):
    for key in ("zone", "triage_zone", "memory_zone", "classification", "candidate_zone", "triage"):
        value = record.get(key)
        if isinstance(value, str):
            up = value.upper()
            if "CRISTAL" in up:
                return "CRISTAL"
            if "TRANSITION" in up:
                return "TRANSITION"
            if "NEANT" in up or "NÉANT" in up:
                return "NEANT"
            if "REFLEX" in up or "RÉFLEX" in up:
                return "REFLEX"

    raw = json.dumps(record, ensure_ascii=False).upper()
    if "CRISTAL" in raw:
        return "CRISTAL"
    if "TRANSITION" in raw:
        return "TRANSITION"
    if "NEANT" in raw or "NÉANT" in raw:
        return "NEANT"
    if "REFLEX" in raw or "RÉFLEX" in raw:
        return "REFLEX"

    return "UNKNOWN"


def extract_tags(record):
    tags = []
    for key in ("tags", "memory_tags", "axes", "detected_axes"):
        value = record.get(key)
        if isinstance(value, list):
            tags.extend([str(x) for x in value])
        elif isinstance(value, str):
            tags.extend([x.strip() for x in re.split(r"[,|;]", value) if x.strip()])

    zone = detect_zone(record)
    tags.append(zone.lower())
    tags.append("brody")
    tags.append("readonly")
    tags.append("graphiti_candidate")
    tags.append("x108")

    deduped = []
    seen = set()
    for tag in tags:
        norm = re.sub(r"\s+", "_", str(tag).strip().lower())
        if norm and norm not in seen:
            seen.add(norm)
            deduped.append(norm)
    return deduped


def extract_material(record):
    user = pick(record, "user", "query", "input", "prompt", "user_input", default="")
    response = pick(record, "response_md", "response", "output", "assistant", "brody_response", default="")
    memory_query = pick(record, "memory_query", "query_norm", "search_query", default="")
    summary = pick(record, "summary", "reason", "rationale", "triage_reason", default="")
    source_ref = pick(record, "source_ref", "source", "path", "session_id", default="")

    parts = []
    if user:
        parts.append(f"USER={clean_text(user, 600)}")
    if memory_query:
        parts.append(f"MEMORY_QUERY={clean_text(memory_query, 300)}")
    if summary:
        parts.append(f"SUMMARY={clean_text(summary, 900)}")
    if response:
        parts.append(f"RESPONSE={clean_text(response, 1800)}")
    if source_ref:
        parts.append(f"SOURCE_REF={clean_text(source_ref, 600)}")

    if not parts:
        parts.append(clean_text(json.dumps(record, ensure_ascii=False), 1800))

    return "\n".join(parts)


def build_candidate(record, index):
    zone = detect_zone(record)
    material = extract_material(record)
    digest = sha256_text(json.dumps(record, sort_keys=True, ensure_ascii=False))

    if zone == "CRISTAL":
        candidate_type = "MEMORY_CANDIDATE_ONLY_NOT_CANON"
        review_priority = "HIGH"
    elif zone == "TRANSITION":
        candidate_type = "REVIEW_CANDIDATE_ONLY"
        review_priority = "MEDIUM"
    else:
        candidate_type = "NON_EXPORTABLE"
        review_priority = "NONE"

    title_seed = pick(record, "user", "query", "memory_query", "title", default=f"candidate_{index}")
    title = clean_text(title_seed, 120) or f"candidate_{index}"

    return {
        "candidate_id": f"BRODY_GRAPHITI_CANDIDATE_{index:04d}_{digest[:12]}",
        "created_at": now_iso(),
        "zone": zone,
        "candidate_type": candidate_type,
        "review_priority": review_priority,
        "title": title,
        "text": material,
        "tags": extract_tags(record),
        "source": "BRODY_AUTO_TRIAGE_MEMORY_INTAKE_READONLY_V1",
        "source_event_hash": pick(record, "event_hash", "latest_event_hash", "hash", default=digest),
        "source_record_sha256": digest,
        "readonly": True,
        "memory_decision": False,
        "allowed_to_decide": False,
        "emits_act": False,
        "emits_verdict": False,
        "decision_authority": "KX108_ONLY",
        "kernel_mutation": False,
        "x108_runtime_binding": False,
        "x108_merge": False,
        "graphiti_index_write": False,
        "memory_intake": False,
        "canon": False,
        "proof_claim": False,
        "needs_human_review": True,
    }


def export_candidates(triage_records_jsonl: Path, out_dir: Path, max_candidates: int):
    records = read_jsonl(triage_records_jsonl)

    candidates = []
    rejected = []

    for record in records:
        zone = detect_zone(record)
        if zone in ("CRISTAL", "TRANSITION"):
            if len(candidates) < max_candidates:
                candidates.append(build_candidate(record, len(candidates) + 1))
        else:
            rejected.append({
                "zone": zone,
                "source_record_sha256": sha256_text(json.dumps(record, sort_keys=True, ensure_ascii=False)),
                "reason": "NOT_EXPORTABLE_READONLY",
            })

    out_dir.mkdir(parents=True, exist_ok=True)

    candidates_jsonl = out_dir / "GRAPHITI_CANDIDATES_READONLY.jsonl"
    candidates_json = out_dir / "GRAPHITI_CANDIDATES_READONLY.json"
    rejected_jsonl = out_dir / "GRAPHITI_REJECTED_READONLY.jsonl"
    summary_json = out_dir / "GRAPHITI_CANDIDATE_EXPORT_SUMMARY.json"
    report_md = out_dir / "GRAPHITI_CANDIDATE_EXPORT_REPORT.md"

    candidates_jsonl.write_text(
        "\n".join(json.dumps(c, ensure_ascii=False) for c in candidates) + ("\n" if candidates else ""),
        encoding="utf-8"
    )

    candidates_json.write_text(
        json.dumps(candidates, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    rejected_jsonl.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rejected) + ("\n" if rejected else ""),
        encoding="utf-8"
    )

    zone_counts = {"CRISTAL": 0, "TRANSITION": 0, "NEANT": 0, "REFLEX": 0, "UNKNOWN": 0}
    for record in records:
        zone = detect_zone(record)
        zone_counts[zone] = zone_counts.get(zone, 0) + 1

    latest_event_hash = sha256_text(
        json.dumps({
            "records_count": len(records),
            "candidate_count": len(candidates),
            "candidate_hashes": [c["source_record_sha256"] for c in candidates],
            "boundary": BOUNDARY,
        }, sort_keys=True, ensure_ascii=False)
    )

    summary = {
        "status": "BRODY_CANDIDATE_EXPORT_FOR_GRAPHITI_READONLY_PASS",
        "created_at": now_iso(),
        "source_triage_records_jsonl": str(triage_records_jsonl),
        "records_count": len(records),
        "candidate_count": len(candidates),
        "rejected_count": len(rejected),
        "zone_counts": zone_counts,
        "outputs": {
            "candidates_jsonl": str(candidates_jsonl),
            "candidates_json": str(candidates_json),
            "rejected_jsonl": str(rejected_jsonl),
            "summary_json": str(summary_json),
            "report_md": str(report_md),
        },
        "latest_event_hash": latest_event_hash,
        **BOUNDARY,
    }

    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# BRODY CANDIDATE EXPORT FOR GRAPHITI — READONLY",
        "",
        f"- status: {summary['status']}",
        f"- source: {triage_records_jsonl}",
        f"- records_count: {len(records)}",
        f"- candidate_count: {len(candidates)}",
        f"- rejected_count: {len(rejected)}",
        f"- graphiti_index_write: false",
        f"- memory_intake: false",
        f"- decision_authority: KX108_ONLY",
        "",
        "## Candidates",
    ]

    for c in candidates:
        lines += [
            "",
            f"### {c['candidate_id']}",
            f"- zone: {c['zone']}",
            f"- type: {c['candidate_type']}",
            f"- title: {c['title']}",
            f"- tags: {', '.join(c['tags'])}",
            f"- source_record_sha256: {c['source_record_sha256']}",
        ]

    lines += [
        "",
        "## Boundary",
        "",
        "This export produces Graphiti-ready candidate files only.",
        "It does not write to Graphiti.",
        "It does not write to Neo4j.",
        "It does not mutate X108.",
        "It does not decide.",
    ]

    report_md.write_text("\n".join(lines), encoding="utf-8")

    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--triage-records-jsonl", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--max-candidates", type=int, default=200)
    args = parser.parse_args()

    summary = export_candidates(
        Path(args.triage_records_jsonl),
        Path(args.out_dir),
        args.max_candidates,
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
