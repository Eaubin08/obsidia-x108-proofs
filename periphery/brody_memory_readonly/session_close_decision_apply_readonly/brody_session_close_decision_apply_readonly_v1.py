import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

BOUNDARY = {
    "readonly": True,
    "response_only": True,
    "session_close_decision_apply": True,
    "human_decision_applied": True,
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
    "brody_role": "SESSION_CLOSE_DECISION_APPLY_READONLY",
    "memory_role": "GUIDE_CONTEXT_NAVIGATION_ONLY",
}

VALID_DECISIONS = {"KEEP", "TRANSITION", "NEANT", "REFLEX"}


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
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows):
    with path.open("w", encoding="utf-8", errors="ignore") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def apply_decision(row: dict, mode: str, index: int, prev_hash: str):
    suggested = str(row.get("suggested_human_decision", "")).upper().strip()

    if mode == "accept_suggested":
        decision = suggested
        source = "ACCEPT_SUGGESTED_BY_HUMAN_OPERATOR"
    else:
        raise RuntimeError(f"UNSUPPORTED_MODE={mode}")

    if decision not in VALID_DECISIONS:
        raise RuntimeError(f"BAD_DECISION={decision}")

    out = dict(row)
    out["index"] = index
    out["human_decision"] = decision
    out["human_decision_source"] = source
    out["human_decision_applied_at"] = now_iso()
    out["human_decision_applied"] = True

    if decision == "KEEP":
        out["post_human_zone"] = "KEEP_MEMORY_CANDIDATE"
        out["next_action"] = "PREPARE_MEMORY_CANDIDATE_READONLY"
    elif decision == "TRANSITION":
        out["post_human_zone"] = "TRANSITION_REVIEW_LATER"
        out["next_action"] = "HOLD_FOR_LATER_REVIEW"
    elif decision == "REFLEX":
        out["post_human_zone"] = "REFLEX_ALERT_TRACE"
        out["next_action"] = "KEEP_AS_ALERT_TRACE_ONLY"
    else:
        out["post_human_zone"] = "NEANT_REJECTED"
        out["next_action"] = "DO_NOT_KEEP"

    out.update(BOUNDARY)

    seed = json.dumps(
        {
            "prev": prev_hash,
            "pointer_path": out.get("pointer_path"),
            "pointer_sha256": out.get("pointer_sha256"),
            "source_event_hash": out.get("event_hash"),
            "human_decision": decision,
            "post_human_zone": out["post_human_zone"],
        },
        ensure_ascii=False,
        sort_keys=True,
    )

    out["prev_decision_event_hash"] = prev_hash
    out["decision_event_hash"] = sha256_text(seed)

    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--accept-suggested", action="store_true")
    args = parser.parse_args()

    if not args.accept_suggested:
        raise RuntimeError("HUMAN_ACCEPT_SUGGESTED_REQUIRED_FOR_V1")

    workspace_root = Path(args.workspace_root)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    gate_ptr = workspace_root / "CURRENT_BRODY_SESSION_CLOSE_HUMAN_VALIDATION_GATE_READONLY_V1_VALIDATE.txt"
    if not gate_ptr.exists():
        raise RuntimeError(f"MISSING_HUMAN_GATE_VALIDATE_POINTER={gate_ptr}")

    gate_kv = parse_kv(gate_ptr)

    queue_jsonl = Path(gate_kv.get("QUEUE_JSONL", ""))
    gate_summary_json = Path(gate_kv.get("SUMMARY_JSON", ""))

    if not queue_jsonl.exists():
        raise RuntimeError(f"MISSING_QUEUE_JSONL={queue_jsonl}")
    if not gate_summary_json.exists():
        raise RuntimeError(f"MISSING_GATE_SUMMARY_JSON={gate_summary_json}")

    gate_summary = json.loads(gate_summary_json.read_text(encoding="utf-8-sig", errors="ignore"))
    queue = read_jsonl(queue_jsonl)

    if gate_summary.get("patch") != "V1_3_CANONICAL_POINTER_RECORDS_SUPPORT_FALLBACK":
        raise RuntimeError(f"BAD_GATE_PATCH={gate_summary.get('patch')}")

    if int(gate_summary.get("queue_count", -1)) != len(queue):
        raise RuntimeError("QUEUE_COUNT_MISMATCH")

    decisions = []
    prev = "GENESIS_BRODY_SESSION_CLOSE_DECISION_APPLY_READONLY_V1"

    for idx, row in enumerate(queue, start=1):
        applied = apply_decision(row, "accept_suggested", idx, prev)
        prev = applied["decision_event_hash"]
        decisions.append(applied)

    counts = {}
    zones = {}
    for row in decisions:
        d = row["human_decision"]
        z = row["post_human_zone"]
        counts[d] = counts.get(d, 0) + 1
        zones[z] = zones.get(z, 0) + 1

    decisions_jsonl = out_dir / "BRODY_SESSION_CLOSE_DECISIONS_APPLIED.jsonl"
    decisions_json = out_dir / "BRODY_SESSION_CLOSE_DECISIONS_APPLIED.json"
    keep_jsonl = out_dir / "BRODY_SESSION_CLOSE_KEEP_CANDIDATES.jsonl"
    transition_jsonl = out_dir / "BRODY_SESSION_CLOSE_TRANSITION_RECORDS.jsonl"
    reflex_jsonl = out_dir / "BRODY_SESSION_CLOSE_REFLEX_RECORDS.jsonl"
    neant_jsonl = out_dir / "BRODY_SESSION_CLOSE_NEANT_RECORDS.jsonl"
    summary_json = out_dir / "BRODY_SESSION_CLOSE_DECISION_APPLY_SUMMARY.json"
    report_md = out_dir / "BRODY_SESSION_CLOSE_DECISION_APPLY_REPORT.md"

    write_jsonl(decisions_jsonl, decisions)
    decisions_json.write_text(json.dumps(decisions, indent=2, ensure_ascii=False), encoding="utf-8")

    write_jsonl(keep_jsonl, [r for r in decisions if r["human_decision"] == "KEEP"])
    write_jsonl(transition_jsonl, [r for r in decisions if r["human_decision"] == "TRANSITION"])
    write_jsonl(reflex_jsonl, [r for r in decisions if r["human_decision"] == "REFLEX"])
    write_jsonl(neant_jsonl, [r for r in decisions if r["human_decision"] == "NEANT"])

    summary = {
        "status": "BRODY_SESSION_CLOSE_DECISION_APPLY_READONLY_V1_PASS",
        "created_at": now_iso(),
        "mode": "ACCEPT_SUGGESTED_BY_HUMAN_OPERATOR",
        "source_gate_pointer": str(gate_ptr),
        "source_queue_jsonl": str(queue_jsonl),
        "source_gate_summary_json": str(gate_summary_json),
        "gate_patch": gate_summary.get("patch"),
        "input_queue_count": len(queue),
        "decision_count": len(decisions),
        "decision_counts": counts,
        "post_human_zone_counts": zones,
        "latest_decision_event_hash": prev,
        "outputs": {
            "decisions_jsonl": str(decisions_jsonl),
            "decisions_json": str(decisions_json),
            "keep_jsonl": str(keep_jsonl),
            "transition_jsonl": str(transition_jsonl),
            "reflex_jsonl": str(reflex_jsonl),
            "neant_jsonl": str(neant_jsonl),
            "summary_json": str(summary_json),
            "report_md": str(report_md),
        },
        "next": "BUILD_BRODY_POST_HUMAN_REVIEW_MEMORY_TRIAGE_READONLY_V1",
        **BOUNDARY,
    }

    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    report_lines = [
        "# BRODY SESSION CLOSE DECISION APPLY READONLY V1",
        "",
        f"- status: {summary['status']}",
        f"- mode: {summary['mode']}",
        f"- input_queue_count: {summary['input_queue_count']}",
        f"- decision_count: {summary['decision_count']}",
        f"- decision_counts: {summary['decision_counts']}",
        f"- latest_decision_event_hash: {summary['latest_decision_event_hash']}",
        "",
        "## Boundary",
        "",
        "- Human decision applied: true",
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

    report_md.write_text("\n".join(report_lines), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
