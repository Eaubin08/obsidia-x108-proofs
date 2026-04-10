#!/usr/bin/env python3
import sys
import json
from pathlib import Path
from typing import Any, Dict, Optional

VALID_PREFIXES = ("audit:", "merkle:", "seal:", "tla:", "tla_vars:", "rfc3161:", "sigma:")

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

def ref_is_resolvable(ref: str) -> bool:
    if ref.startswith(VALID_PREFIXES):
        return True
    return Path(ref).exists()

def validate(audit_entry: Dict[str, Any], envelope: Dict[str, Any]) -> list[str]:
    errors: list[str] = []

    # IDs
    if not envelope.get("decision_id"):
        errors.append("envelope decision_id missing")
    if not envelope.get("trace_id"):
        errors.append("envelope trace_id missing")

    if audit_entry.get("decision_id") != envelope.get("decision_id"):
        errors.append("audit/envelope decision_id mismatch")
    if audit_entry.get("trace_id") != envelope.get("trace_id"):
        errors.append("audit/envelope trace_id mismatch")

    # Audit chain
    if "hash" not in audit_entry:
        errors.append("audit hash missing")
    if "prev_hash" not in audit_entry:
        errors.append("audit prev_hash missing")

    # Evidence refs
    evidence_refs = envelope.get("evidence_refs", [])
    if not isinstance(evidence_refs, list):
        errors.append("evidence_refs invalid")
    else:
        if len(evidence_refs) == 0:
            errors.append("evidence_refs empty")

        has_audit = any(str(x).startswith("audit:") for x in evidence_refs)
        if not has_audit:
            errors.append("missing audit ref in evidence_refs")

        for ref in evidence_refs:
            if not isinstance(ref, str):
                errors.append("non-string evidence_ref")
                continue
            if not ref_is_resolvable(ref):
                errors.append(f"unresolved evidence_ref: {ref}")

    # Attestation coherence
    att = envelope.get("attestation")
    if att is not None:
        if not isinstance(att, dict):
            errors.append("attestation invalid")
        else:
            status = att.get("status")
            if status is not None and status not in ["verified", "incomplete", "failed", "ok"]:
                errors.append("attestation status invalid")

    # Sigma coherence
    sigma = envelope.get("sigma")
    if sigma is not None and not isinstance(sigma, dict):
        errors.append("sigma invalid")

    return errors

def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: verify_provenance.py <audit_log.jsonl> <envelope.json>", file=sys.stderr)
        sys.exit(1)

    audit_log_path = Path(sys.argv[1])
    envelope_path = Path(sys.argv[2])

    if not audit_log_path.exists():
        print(json.dumps({"status": "failed", "error": "audit log not found"}))
        sys.exit(1)

    if not envelope_path.exists():
        print(json.dumps({"status": "failed", "error": "envelope not found"}))
        sys.exit(1)

    envelope = load_json(envelope_path)
    decision_id = envelope.get("decision_id")
    if not decision_id:
        print(json.dumps({"status": "failed", "error": "envelope decision_id missing"}))
        sys.exit(1)

    audit_entry = load_audit_entry(audit_log_path, decision_id)
    if not audit_entry:
        print(json.dumps({"status": "failed", "error": f"decision {decision_id} not found in audit log"}))
        sys.exit(1)

    errors = validate(audit_entry, envelope)

    print(json.dumps({
        "status": "ok" if not errors else "failed",
        "decision_id": decision_id,
        "errors": errors,
        "provenance": {
            "decision_id": envelope.get("decision_id"),
            "trace_id": envelope.get("trace_id"),
            "evidence_refs": envelope.get("evidence_refs", []),
            "audit_hash": audit_entry.get("hash"),
            "audit_prev_hash": audit_entry.get("prev_hash"),
        }
    }, indent=2))

    if errors:
        sys.exit(1)

if __name__ == "__main__":
    main()
