#!/usr/bin/env python3
"""Convert P4 temporal classifier output into claim-bounded GPS domain evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_obj(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def build_temporal_domain_evidence(detection: dict) -> dict:
    classification = str(detection.get("overall_classification", "UNKNOWN")).upper()
    if classification not in {"NOMINAL", "UNKNOWN", "ANOMALY"}:
        classification = "UNKNOWN"

    core = {
        "classification": classification,
        "algorithm_version": str(detection.get("algorithm_version", "UNKNOWN")),
        "status": str(detection.get("status", "UNKNOWN")),
        "truth_or_onset_consumed": bool(detection.get("truth_or_onset_consumed", True)),
        "first_anomaly": detection.get("first_anomaly"),
        "thresholds": detection.get("thresholds", {}),
        "claim_boundary": detection.get(
            "claim_boundary",
            "TRAJECTORY_DISCONTINUITY_ONLY_NO_HOSTILE_OR_CAUSAL_ATTRIBUTION",
        ),
        "input_log_sha256": str(detection.get("input_log_sha256", "")),
        "calibration_log_sha256": str(detection.get("calibration_log_sha256", "")),
    }
    evidence_hash = sha256_obj(core)

    return {
        "artifact": "p4_temporal_integrity_domain_evidence",
        "decision_authority": "KX108_ONLY",
        "emits_verdict": False,
        "temporal_integrity_classification": classification,
        "temporal_integrity_anomaly": classification == "ANOMALY",
        "temporal_integrity_evidence_hash": evidence_hash,
        "temporal_integrity_algorithm_version": core["algorithm_version"],
        "temporal_integrity_status": core["status"],
        "truth_or_onset_consumed": core["truth_or_onset_consumed"],
        "claim_boundary": core["claim_boundary"],
        "evidence": core,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--detection", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    detection = json.loads(args.detection.read_text(encoding="utf-8"))
    result = build_temporal_domain_evidence(detection)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
