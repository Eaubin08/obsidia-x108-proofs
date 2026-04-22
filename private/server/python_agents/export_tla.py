#!/usr/bin/env python3
import sys
import json
from pathlib import Path
from typing import Any, Dict

def build_trace(envelope: Dict[str, Any]) -> Dict[str, Any]:
    x108 = envelope.get("x108") or {}
    timestamps = envelope.get("timestamps") or {}
    sigma = envelope.get("sigma") or {}
    attestation = envelope.get("attestation") or {}
    rfc3161 = envelope.get("rfc3161") or {}

    return {
        "trace_version": "obsidia.tla.export.v1",
        "decision_id": envelope.get("decision_id"),
        "trace_id": envelope.get("trace_id"),
        "ticket_id": envelope.get("ticket_id"),

        "domain": envelope.get("domain"),
        "mode": envelope.get("mode"),

        "kernel_verdict": envelope.get("kernel_verdict"),
        "consensus_verdict": envelope.get("consensus_verdict"),
        "x108_gate": envelope.get("x108_gate"),

        "x108": {
            "elapsed": x108.get("elapsed"),
            "tau": x108.get("tau"),
            "irr": x108.get("irr"),
        },

        "timestamps": {
            "created_at": timestamps.get("created_at"),
            "kernel_at": timestamps.get("kernel_at"),
            "consensus_at": timestamps.get("consensus_at"),
            "sigma_at": timestamps.get("sigma_at"),
            "attestation_at": timestamps.get("attestation_at"),
            "rfc3161_at": timestamps.get("rfc3161_at"),
        },

        "evidence_refs": envelope.get("evidence_refs", []),
        "reason_count": len(envelope.get("reasons") or []),
        "theorem_ref_count": len(envelope.get("theorem_refs") or []),

        "sigma": {
            "status": sigma.get("status"),
            "stability": sigma.get("stability"),
            "alert_count": len(sigma.get("alerts") or []),
            "confidence": sigma.get("confidence"),
        },

        "attestation": {
            "status": attestation.get("status"),
            "verified": attestation.get("verified"),
            "merkle_root": attestation.get("merkle_root"),
            "seal": attestation.get("seal"),
        },

        "rfc3161": {
            "status": rfc3161.get("status"),
            "verified": rfc3161.get("verified"),
            "artifact_path": rfc3161.get("artifact_path"),
        },

        "tla_targets": ["X108.tla", "ObsidiaDistX108A12.tla"],
    }

def build_vars(trace: Dict[str, Any]) -> Dict[str, Any]:
    x108 = trace.get("x108") or {}
    sigma = trace.get("sigma") or {}
    attestation = trace.get("attestation") or {}

    base_decision = trace.get("kernel_verdict")
    final_decision = trace.get("consensus_verdict") or base_decision

    return {
        "decisionId": trace.get("decision_id"),
        "traceId": trace.get("trace_id"),
        "domain": trace.get("domain"),
        "mode": trace.get("mode"),

        "elapsed": x108.get("elapsed"),
        "tau": x108.get("tau"),
        "irr": x108.get("irr"),

        "baseDecision": base_decision,
        "decision": final_decision,

        "sigmaStatus": sigma.get("status"),
        "attestationStatus": attestation.get("status"),
    }

def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: export_tla.py <input_envelope.json> <output_trace.json>", file=sys.stderr)
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_trace_path = Path(sys.argv[2])

    if not input_path.exists():
        print(json.dumps({"status": "failed", "error": f"input not found: {input_path}"}))
        sys.exit(1)

    envelope = json.loads(input_path.read_text(encoding="utf-8"))
    trace = build_trace(envelope)
    vars_tla = build_vars(trace)

    output_trace_path.write_text(json.dumps(trace, indent=2), encoding="utf-8")
    vars_path = output_trace_path.with_name(output_trace_path.stem + "_vars.json")
    vars_path.write_text(json.dumps(vars_tla, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": "ok",
        "trace_output": str(output_trace_path),
        "vars_output": str(vars_path),
        "trace_version": trace["trace_version"],
        "tla_targets": trace["tla_targets"],
    }))

if __name__ == "__main__":
    main()
