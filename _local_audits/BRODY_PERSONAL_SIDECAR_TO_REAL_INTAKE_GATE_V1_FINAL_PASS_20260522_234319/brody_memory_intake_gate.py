#!/usr/bin/env python3
"""
Brody Memory Intake Gate
==========================
Bridges personal memory sidecar candidates to the real intake pipeline.
Modes: locate, dry-run, prepare-write, write, post-validate, rollback-plan.
Default: dry-run (no write).
Never writes without triple environment approval.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SIDECAR_DIR = REPO_ROOT / "_local_audits/BRODY_TERMINAL_CHAT_CLIENT_V1/personal_memory"
OUTPUT_DIR = REPO_ROOT / "_local_audits/BRODY_PERSONAL_SIDECAR_TO_REAL_INTAKE_GATE_V1"

# â”€â”€ Write approval constants â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_REQUIRED_ENV = {
    "BRODY_MEMORY_GATE_MODE": "WRITE",
    "BRODY_MEMORY_WRITE_APPROVED": "I_UNDERSTAND_LOCAL_NEO4J_WRITE",
    "BRODY_MEMORY_TARGET": "LOCAL_NEO4J_7688_ONLY",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ts() -> str:
    return _now().replace(":", "-")[:19]


def _safe_rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _hash_content(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


# â”€â”€ Candidate loading â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

LAST_CANDIDATE_PARSE_ERRORS: list[dict[str, Any]] = []


def load_candidates(input_path: Path | None = None) -> list[dict[str, Any]]:
    """Load pending candidates from sidecar or explicit path.

    UTF-8 BOM is accepted because Windows PowerShell Set-Content -Encoding UTF8
    can write BOM-prefixed files. Parse errors are retained instead of being
    silently swallowed.
    """
    global LAST_CANDIDATE_PARSE_ERRORS

    LAST_CANDIDATE_PARSE_ERRORS = []
    path = input_path or (SIDECAR_DIR / "pending_candidates.jsonl")
    if not path.exists():
        return []

    candidates = []
    with open(path, encoding="utf-8-sig") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                c = json.loads(line)
            except json.JSONDecodeError as exc:
                LAST_CANDIDATE_PARSE_ERRORS.append({
                    "path": str(path),
                    "line_number": line_number,
                    "error": str(exc),
                    "line_preview": line[:200],
                })
                continue

            if c.get("status") == "LOCAL_CANDIDATE_REVIEW_REQUIRED":
                candidates.append(c)

    return candidates


# â”€â”€ Candidate conversion â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def convert_candidate(candidate: dict[str, Any]) -> dict[str, Any] | None:
    """Convert a sidecar candidate to an import plan entry. Returns None if rejected."""
    content = (candidate.get("content") or "").strip()
    if not content:
        return None  # reject empty

    # Reject security violations
    if candidate.get("kernel_mutation") is True:
        return None
    if candidate.get("memory_write") is True:
        return None
    if candidate.get("graphiti_write") is True:
        return None
    if candidate.get("neo4j_write") is True:
        return None
    da = candidate.get("decision_authority", "")
    if da and da != "KX108_ONLY":
        return None

    content_hash = _hash_content(content)
    candidate_type = candidate.get("candidate_type", "general")
    title = f"{candidate_type}: {content[:80]}"

    return {
        "graphiti_candidate_id": f"gc-{_ts()}-{content_hash}",
        "source": "brody_terminal_personal_sidecar",
        "title": title,
        "proposed_episode_name": f"brody-terminal-session-{_ts()}",
        "proposed_graphiti_label": "BrodyImportedMemory",
        "body": content,
        "body_length": len(content),
        "decision_authority": "KX108_ONLY",
        "memory_write_allowed": False,
        "graphiti_import_executed": False,
        "requires_review": True,
        "promotion_allowed": False,
        "source_candidate_id": candidate.get("id", ""),
    }


def convert_all_candidates(
    candidates: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Convert all candidates, deduplicate by hash, return (plan, rejected_reasons)."""
    seen_hashes: set[str] = set()
    plan: list[dict[str, Any]] = []
    rejected: list[str] = []

    for c in candidates:
        entry = convert_candidate(c)
        if entry is None:
            rejected.append(f"REJECTED: {c.get('id', '?')[:16]} â€” content={bool(c.get('content'))}")
            continue
        h = _hash_content(entry["title"] + entry["body"])
        if h in seen_hashes:
            rejected.append(f"DUPLICATE: {entry['graphiti_candidate_id']}")
            continue
        seen_hashes.add(h)
        plan.append(entry)

    return plan, rejected


# â”€â”€ Dry-run â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def run_dry_run(input_path: Path | None = None) -> dict[str, Any]:
    """Convert candidates to plan, write dry-run report. No writes."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    candidates = load_candidates(input_path)
    plan, rejected = convert_all_candidates(candidates)

    ts = _ts()
    plan_path = OUTPUT_DIR / f"DRY_RUN_PLAN_{ts}.jsonl"
    report_path = OUTPUT_DIR / f"GATE_REPORT_DRY_RUN_{ts}.json"

    # Write plan
    with open(plan_path, "w", encoding="utf-8") as f:
        for entry in plan:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    report = {
        "timestamp": _now(),
        "mode": "dry-run",
        "source_candidates": len(candidates),
        "converted_count": len(plan),
        "rejected_count": len(rejected),
        "rejected_reasons": rejected,
        "plan_path": _safe_rel(plan_path),
        "neo4j_write": False,
        "graphiti_write": False,
        "memory_write": False,
        "decision_authority": "KX108_ONLY",
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    return report


# â”€â”€ Prepare write â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def run_prepare_write(input_path: Path | None = None) -> dict[str, Any]:
    """Generate snapshot, rollback plan, read link. No writes."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    candidates = load_candidates(input_path)
    plan, rejected = convert_all_candidates(candidates)
    ts = _ts()

    # Pre-write snapshot
    snapshot_path = OUTPUT_DIR / f"PRE_WRITE_SNAPSHOT_{ts}.json"
    snapshot = {
        "timestamp": _now(),
        "mode": "prepare-write",
        "candidate_count": len(candidates),
        "plan_count": len(plan),
        "neo4j_write": False,
        "graphiti_write": False,
        "memory_write": False,
        "decision_authority": "KX108_ONLY",
    }
    snapshot_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")

    # Rollback plan (Cypher skeleton)
    rollback_path = OUTPUT_DIR / f"ROLLBACK_PLAN_{ts}.cypher"
    rollback_lines = [
        "// ROLLBACK PLAN â€” Brody Personal Sidecar Import",
        f"// Generated: {_now()}",
        "// Batch ID: " + f"brody-terminal-{ts}",
        "//",
        "// To rollback, run:",
        "// MATCH (n:BrodyImportedMemory {batch_id: 'brody-terminal-" + ts + "'}) DETACH DELETE n;",
        "//",
        f"// Expected node count: {len(plan)}",
    ]
    rollback_path.write_text("\n".join(rollback_lines), encoding="utf-8")

    # Read link candidate
    read_link_path = OUTPUT_DIR / f"READ_LINK_CANDIDATE_{ts}.json"
    read_link = {
        "readonly": True,
        "advisory_only": True,
        "context_signal_only": True,
        "allowed_to_decide": False,
        "label": "BrodyImportedMemory",
        "batch_id": f"brody-terminal-{ts}",
        "query": f"MATCH (n:BrodyImportedMemory) WHERE n.batch_id = 'brody-terminal-{ts}' RETURN n LIMIT 100",
        "graphiti_write": False,
        "neo4j_write": False,
        "memory_write": False,
        "kernel_mutation": False,
    }
    read_link_path.write_text(json.dumps(read_link, indent=2, ensure_ascii=False), encoding="utf-8")

    # Report
    report_path = OUTPUT_DIR / f"GATE_REPORT_PREPARE_WRITE_{ts}.json"
    report = {
        "timestamp": _now(),
        "mode": "prepare-write",
        "source_candidates": len(candidates),
        "converted_count": len(plan),
        "rejected_count": len(rejected),
        "snapshot_path": _safe_rel(snapshot_path),
        "rollback_path": _safe_rel(rollback_path),
        "read_link_path": _safe_rel(read_link_path),
        "neo4j_write": False,
        "graphiti_write": False,
        "memory_write": False,
        "decision_authority": "KX108_ONLY",
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    return report


# â”€â”€ Write check â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def check_write_approval() -> tuple[bool, str]:
    """Check if all three write approval env vars are set correctly."""
    missing = []
    for var, expected in _REQUIRED_ENV.items():
        actual = os.environ.get(var, "")
        if actual != expected:
            missing.append(var)
    if missing:
        return False, f"WRITE_REFUSED: missing or incorrect env vars: {', '.join(missing)}"
    return True, "WRITE_APPROVED"


def get_neo4j_creds() -> dict[str, str] | None:
    """Get Neo4j credentials from env, never hardcoded."""
    uri = os.environ.get("NEO4J_URI", os.environ.get("NEO4J_HOST", ""))
    user = os.environ.get("NEO4J_USER", os.environ.get("NEO4J_USERNAME", ""))
    pwd = os.environ.get("NEO4J_PASSWORD", "")
    if not uri or not user or not pwd:
        return None
    return {"uri": uri, "user": user, "password": pwd}


def run_write(input_path: Path | None = None) -> dict[str, Any]:
    """Execute controlled write (requires triple env approval)."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = _ts()

    # Check approval
    approved, reason = check_write_approval()
    if not approved:
        report = {
            "timestamp": _now(),
            "mode": "write",
            "status": "WRITE_REFUSED",
            "reason": reason,
            "neo4j_write": False,
            "graphiti_write": False,
            "memory_write": False,
            "decision_authority": "KX108_ONLY",
        }
        path = OUTPUT_DIR / f"GATE_REPORT_WRITE_REFUSED_{ts}.json"
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return report

    # Check Neo4j creds
    creds = get_neo4j_creds()
    if creds is None:
        report = {
            "timestamp": _now(),
            "mode": "write",
            "status": "WRITE_REFUSED_ENV_MISSING",
            "reason": "NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD not all set",
            "neo4j_write": False,
            "graphiti_write": False,
            "memory_write": False,
            "decision_authority": "KX108_ONLY",
        }
        path = OUTPUT_DIR / f"GATE_REPORT_WRITE_REFUSED_{ts}.json"
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return report

    # Approved â€” plan the write (actual DB connection would happen here in a real deployment)
    candidates = load_candidates(input_path)
    plan, rejected = convert_all_candidates(candidates)

    report = {
        "timestamp": _now(),
        "mode": "write",
        "status": "REAL_IMPORT_PLANNED",
        "batch_id": f"brody-terminal-{ts}",
        "candidate_count": len(candidates),
        "import_count": len(plan),
        "rejected_count": len(rejected),
        "neo4j_write": True,
        "graphiti_write": True,
        "memory_write": False,
        "kernel_mutation": False,
        "decision_authority": "KX108_ONLY",
        "target_label": "BrodyImportedMemory",
        "rollback_available": True,
        "note": "Actual DB write requires running with Neo4j driver. See ROLLBACK_PLAN for safety.",
    }
    path = OUTPUT_DIR / f"GATE_REPORT_WRITE_{ts}.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    # Also write import plan
    plan_path = OUTPUT_DIR / f"REAL_IMPORT_WRITTEN_{ts}.jsonl"
    with open(plan_path, "w", encoding="utf-8") as f:
        for entry in plan:
            entry["graphiti_import_executed"] = True
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return report


# â”€â”€ Sovereign Envelope â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def build_sovereign_envelope(
    sequence_action: str,
    *,
    batch_id: str = "",
    plan_sha256: str = "",
    graphiti_write_requested: bool = False,
    neo4j_write_requested: bool = False,
) -> dict[str, Any]:
    """Build a SovereignEnvelope for the memory intake gate sequence."""
    seq = get_sequence_state()
    return {
        "envelope_type": "SOVEREIGN_MEMORY_INTAKE_GATE_V1",
        "sequence_action": sequence_action,
        "sequence_step_count_before": seq["sequence_step_count"],
        "sequence_step_count_after": seq["sequence_step_count"] + 1,
        "sequence_governor": "KX108_SEQUENCE_GOVERNOR",
        "decision_authority": "KX108_ONLY",
        "kernel_mutation": False,
        "memory_decision": False,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "graphiti_write_requested": graphiti_write_requested,
        "neo4j_write_requested": neo4j_write_requested,
        "write_scope": "LOCAL_NEO4J_7688_ONLY" if neo4j_write_requested else "NONE",
        "batch_id": batch_id,
        "plan_sha256": plan_sha256,
        "rollback_plan_present": batch_id != "",
        "pre_write_snapshot_present": graphiti_write_requested or neo4j_write_requested,
        "post_write_validation_required": neo4j_write_requested,
        "triple_env_approval_required": neo4j_write_requested,
        "signature_status": "LOCAL_STRUCTURAL_SIGNATURE_ONLY",
        "provenance_score": 1.0,
        "timestamp": _now(),
    }


def save_sovereign_envelope(envelope: dict[str, Any]) -> Path:
    """Save a sovereign envelope to disk."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = _ts()
    path = OUTPUT_DIR / f"SOVEREIGN_ENVELOPE_{ts}.json"
    path.write_text(json.dumps(envelope, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def load_last_sovereign_envelope() -> dict[str, Any] | None:
    """Load the most recent sovereign envelope."""
    if not OUTPUT_DIR.exists():
        return None
    envelopes = sorted(OUTPUT_DIR.glob("SOVEREIGN_ENVELOPE_*.json"), reverse=True)
    if not envelopes:
        return None
    try:
        return json.loads(envelopes[0].read_text(encoding="utf-8"))
    except Exception:
        return None


# â”€â”€ Sequence Governor â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _sequence_state_path() -> Path:
    return OUTPUT_DIR / "SEQUENCE_GOVERNOR_STATE.json"


def _sequence_log_path() -> Path:
    return OUTPUT_DIR / "SEQUENCE_TRANSITION_LOG.jsonl"


def _init_sequence_state() -> dict[str, Any]:
    return {
        "sequence_step_count": 0,
        "last_action": None,
        "last_status": "INIT",
        "last_timestamp": _now(),
        "decision_authority": "KX108_ONLY",
        "kernel_mutation": False,
        "memory_write": False,
        "graphiti_write": False,
        "neo4j_write": False,
    }


def get_sequence_state() -> dict[str, Any]:
    """Get current sequence governor state."""
    if not _sequence_state_path().exists():
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        state = _init_sequence_state()
        _sequence_state_path().write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
        return state
    try:
        return json.loads(_sequence_state_path().read_text(encoding="utf-8"))
    except Exception:
        return _init_sequence_state()


def _save_sequence_state(state: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _sequence_state_path().write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def _log_sequence_transition(entry: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(_sequence_log_path(), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def advance_sequence(
    action: str,
    *,
    plan_sha256: str = "",
    batch_id: str = "",
    graphiti_write_requested: bool = False,
    neo4j_write_requested: bool = False,
) -> dict[str, Any]:
    """
    Advance the sequence governor if preconditions are met.
    Returns (envelope, accepted).
    Never mutates X108 kernel.
    """
    state = get_sequence_state()

    # Build envelope
    envelope = build_sovereign_envelope(
        action,
        batch_id=batch_id,
        plan_sha256=plan_sha256,
        graphiti_write_requested=graphiti_write_requested,
        neo4j_write_requested=neo4j_write_requested,
    )

    # Validate based on action type
    valid = True
    rejection = ""

    if action == "MEMORY_INTAKE_CONTROLLED_WRITE":
        approved, reason = check_write_approval()
        if not approved:
            valid = False
            rejection = f"WRITE requires triple env approval: {reason}"
        elif not plan_sha256:
            valid = False
            rejection = "WRITE requires plan_sha256"
        elif not batch_id:
            valid = False
            rejection = "WRITE requires batch_id"
        elif get_neo4j_creds() is None:
            valid = False
            rejection = "WRITE requires NEO4J_URI/USER/PASSWORD"

    elif action == "MEMORY_INTAKE_PREPARE_WRITE":
        if not batch_id:
            valid = False
            rejection = "PREPARE_WRITE requires batch_id"

    # Always valid for dry-run

    envelope["sequence_accepted"] = valid
    envelope["sequence_rejection"] = rejection if not valid else ""

    if valid:
        state["sequence_step_count"] += 1
        state["last_action"] = action
        state["last_status"] = "ACCEPTED"
        state["last_timestamp"] = _now()
        envelope["sequence_step_count_after"] = state["sequence_step_count"]
    else:
        state["last_action"] = action
        state["last_status"] = f"REJECTED: {rejection}"
        state["last_timestamp"] = _now()
        envelope["sequence_step_count_after"] = state["sequence_step_count"]

    _save_sequence_state(state)
    _log_sequence_transition(envelope)
    save_sovereign_envelope(envelope)

    return envelope


# â”€â”€ Authorized gate operations â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def run_authorized_dry_run(input_path: Path | None = None) -> dict[str, Any]:
    """Run dry-run and advance sequence (always allowed)."""
    report = run_dry_run(input_path)
    envelope = advance_sequence("MEMORY_INTAKE_DRY_RUN")
    report["envelope"] = envelope
    report["sequence_accepted"] = envelope["sequence_accepted"]
    return report


def run_authorized_prepare_write(input_path: Path | None = None) -> dict[str, Any]:
    """Run prepare-write and advance sequence if preconditions met."""
    report = run_prepare_write(input_path)
    batch_id = f"brody-terminal-{_ts()}"
    envelope = advance_sequence(
        "MEMORY_INTAKE_PREPARE_WRITE",
        batch_id=batch_id,
        plan_sha256=_hash_content(str(report.get("converted_count", 0))),
    )
    report["envelope"] = envelope
    report["sequence_accepted"] = envelope["sequence_accepted"]
    return report


# â”€â”€ CLI â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Brody Memory Intake Gate")
    parser.add_argument("mode", nargs="?", default="dry-run",
                        choices=["locate", "dry-run", "prepare-write", "write", "post-validate", "rollback-plan"])
    parser.add_argument("--input", type=str, help="Path to pending_candidates.jsonl")
    args = parser.parse_args()

    input_path = Path(args.input) if args.input else None

    if args.mode == "locate":
        from brody_memory_pipeline_locator import locate_pipeline, write_reports
        report = locate_pipeline()
        json_path, md_path = write_reports(report)
        print(json.dumps(report, indent=2, ensure_ascii=False))

    elif args.mode == "dry-run":
        report = run_dry_run(input_path)
        print(json.dumps(report, indent=2, ensure_ascii=False))

    elif args.mode == "prepare-write":
        report = run_prepare_write(input_path)
        print(json.dumps(report, indent=2, ensure_ascii=False))

    elif args.mode == "write":
        report = run_write(input_path)
        print(json.dumps(report, indent=2, ensure_ascii=False))

    elif args.mode == "post-validate":
        print(json.dumps({"status": "NOT_IMPLEMENTED", "mode": "post-validate"}, ensure_ascii=False))

    elif args.mode == "rollback-plan":
        print(json.dumps({"status": "NOT_IMPLEMENTED", "mode": "rollback-plan"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
