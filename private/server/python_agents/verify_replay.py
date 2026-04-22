#!/usr/bin/env python3
import sys
import json
from pathlib import Path
from typing import Any, Dict, Optional

def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def load_audit_entry(log_path: Path, decision_id: str) -> Optional[Dict[str, Any]]:
    if not log_path.exists():
        return None

    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except Exception:
            continue
        if entry.get("decision_id") == decision_id:
            return entry
    return None

def validate(audit_entry: Dict[str, Any], envelope: Dict[str, Any], trace: Dict[str, Any]) -> list[str]:
    errors: list[str] = []

    # IDs
    if audit_entry.get("decision_id") != envelope.get("decision_id"):
        errors.append("audit/envelope decision_id mismatch")
    if audit_entry.get("trace_id") != envelope.get("trace_id"):
        errors.append("audit/envelope trace_id mismatch")
    if trace.get("decision_id") != envelope.get("decision_id"):
        errors.append("trace/envelope decision_id mismatch")
    if trace.get("trace_id") != envelope.get("trace_id"):
        errors.append("trace/envelope trace_id mismatch")

    # Verdicts
    if trace.get("kernel_verdict") != envelope.get("kernel_verdict"):
        errors.append("trace/envelope kernel_verdict mismatch")
    if trace.get("consensus_verdict") != envelope.get("consensus_verdict"):
        errors.append("trace/envelope consensus_verdict mismatch")

    # Audit times
    created_at = audit_entry.get("created_at")
    kernel_at = audit_entry.get("kernel_at")
    consensus_at = audit_entry.get("consensus_at")

    if created_at is None:
        errors.append("audit created_at missing")
    if kernel_at is None:
        errors.append("audit kernel_at missing")
    if consensus_at is None:
        errors.append("audit consensus_at missing")

    if isinstance(created_at, (int, float)) and isinstance(kernel_at, (int, float)) and kernel_at < created_at:
        errors.append("audit kernel_at < created_at")

    if isinstance(kernel_at, (int, float)) and isinstance(consensus_at, (int, float)) and consensus_at < kernel_at:
        errors.append("audit consensus_at < kernel_at")

    # Evidence refs
    evidence_refs = envelope.get("evidence_refs", [])
    if not isinstance(evidence_refs, list):
        errors.append("envelope evidence_refs invalid")
    else:
        if not any(str(x).startswith("audit:") for x in evidence_refs):
            errors.append("audit reference missing from evidence_refs")

    return errors

def main() -> None:
    if len(sys.argv) < 4:
        print("Usage: verify_replay.py <audit_log.jsonl> <envelope.json> <trace_tla.json>", file=sys.stderr)
        sys.exit(1)

    audit_log_path = Path(sys.argv[1])
    envelope_path = Path(sys.argv[2])
    trace_path = Path(sys.argv[3])

    if not audit_log_path.exists():
        print(json.dumps({"status": "failed", "error": "audit log not found"}))
        sys.exit(1)
    if not envelope_path.exists():
        print(json.dumps({"status": "failed", "error": "envelope not found"}))
        sys.exit(1)
    if not trace_path.exists():
        print(json.dumps({"status": "failed", "error": "trace not found"}))
        sys.exit(1)

    envelope = load_json(envelope_path)
    trace = load_json(trace_path)
    decision_id = envelope.get("decision_id")

    if not decision_id:
        print(json.dumps({"status": "failed", "error": "envelope decision_id missing"}))
        sys.exit(1)

    audit_entry = load_audit_entry(audit_log_path, decision_id)
    if not audit_entry:
        print(json.dumps({"status": "failed", "error": f"decision {decision_id} not found in audit log"}))
        sys.exit(1)

    errors = validate(audit_entry, envelope, trace)

    print(json.dumps({
        "status": "ok" if not errors else "failed",
        "decision_id": decision_id,
        "errors": errors,
        "audit_entry_found": True,
        "envelope_loaded": True,
        "trace_loaded": True,
    }, indent=2))

    if errors:
        sys.exit(1)

if __name__ == "__main__":
    main()
