#!/usr/bin/env python3
"""Replay P4 temporal-integrity evidence through the GPS DomainState gate.

This is a local fail-closed governance replay. It does not call or simulate a
hostile classifier, and it does not authorize an action.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from domains.gps.gps_x108_gate import GpsX108Gate


def build_payload(evidence: dict) -> dict:
    return {
        "flow_type": "POSITION_REPORT",
        "flight_id": "FGI-P4-TEMPORAL-EVIDENCE",
        "risk_score": 0.5,
        "confidence_index": 0.9,
        "audit_score": 1.0,
        "freshness_ms": 0,
        "attestation_ready": True,
        "sensor_attested": True,
        "replay_window_detected": False,
        "gps_available": True,
        "inertial_available": True,
        "radio_available": True,
        "trajectory_drift_score": 0.0,
        "source_conflict_score": 0.0,
        "time_skew_score": 0.0,
        "brownout_score": 0.0,
        "ground_speed": 0.0,
        "g_load": 1.0,
        "rollback_possible": True,
        "temporal_integrity_classification": evidence.get(
            "temporal_integrity_classification", "UNKNOWN"
        ),
        "temporal_integrity_evidence_hash": evidence.get(
            "temporal_integrity_evidence_hash", ""
        ),
        "temporal_integrity_algorithm_version": evidence.get(
            "temporal_integrity_algorithm_version", ""
        ),
        "temporal_integrity_status": evidence.get("temporal_integrity_status", ""),
    }


def run(evidence: dict) -> dict:
    payload = build_payload(evidence)
    result = GpsX108Gate().evaluate(payload)
    state = result.get("ir_payload", {}).get("meta", {}).get("domain_state", {})
    return {
        "artifact": "p4_temporal_domain_gate_replay",
        "input_temporal_evidence_hash": evidence.get("temporal_integrity_evidence_hash", ""),
        "decision_authority": "KX108_ONLY",
        "connector_decides": False,
        "temporal_integrity_classification": evidence.get(
            "temporal_integrity_classification", "UNKNOWN"
        ),
        "gate_verdict": result.get("verdict"),
        "gate_source": result.get("source"),
        "reality_authenticity_reasons": state.get("reality_authenticity", {}).get("reasons", []),
        "nuisances": state.get("nuisances", []),
        "domain_state_hash": state.get("domain_state_hash"),
        "receipt": result.get("receipt", {}),
        "claim_boundary": evidence.get(
            "claim_boundary",
            "TRAJECTORY_DISCONTINUITY_ONLY_NO_HOSTILE_OR_CAUSAL_ATTRIBUTION",
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    result = run(evidence)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
