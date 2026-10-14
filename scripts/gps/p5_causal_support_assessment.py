#!/usr/bin/env python3
"""Deterministic P5 causal-support assessment for recorded GNSS evidence.

This tool scores evidential support only. It cannot emit an operational verdict
and cannot promote observational evidence into causal spoofing attribution.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def assess(evidence: dict[str, Any]) -> dict[str, Any]:
    detector_truth_free = evidence.get("truth_or_onset_consumed") is False
    detector_anomaly = evidence.get("detector_classification") == "ANOMALY"

    transition = evidence.get("first_anomaly_transition") or {}
    start = transition.get("from_receiver_second")
    end = transition.get("to_receiver_second")
    onset = evidence.get("official_onset_s")
    onset_straddled = (
        isinstance(start, (int, float))
        and isinstance(end, (int, float))
        and isinstance(onset, (int, float))
        and start <= onset <= end
    )

    a = evidence.get("gnss_sdr_ecef_delta_m")
    b = evidence.get("gsrx_ecef_delta_m")
    cross_receiver_agreement_m = None
    cross_receiver_relative_error = None
    cross_receiver_consistent = False
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        cross_receiver_agreement_m = abs(float(a) - float(b))
        denom = max(abs(float(a)), abs(float(b)), 1e-12)
        cross_receiver_relative_error = cross_receiver_agreement_m / denom
        cross_receiver_consistent = cross_receiver_relative_error <= 0.001

    nominal_clean = evidence.get("nominal_control_classification") == "NOMINAL"
    same_recording = evidence.get("same_recorded_rf_source_across_receivers") is True

    independent_physical_source = (
        evidence.get("independent_physical_source_corroboration") is True
    )
    controlled_intervention = evidence.get("controlled_intervention") is True
    heldout_hostile = evidence.get("heldout_hostile_validation") is True

    observational_support = all(
        [
            detector_truth_free,
            detector_anomaly,
            onset_straddled,
            cross_receiver_consistent,
            nominal_clean,
            same_recording,
        ]
    )

    causal_closed = all(
        [
            observational_support,
            independent_physical_source,
            controlled_intervention,
            heldout_hostile,
        ]
    )

    blockers: list[str] = []
    if not independent_physical_source:
        blockers.append("NO_INDEPENDENT_PHYSICAL_SOURCE_CORROBORATION")
    if not controlled_intervention:
        blockers.append("NO_CONTROLLED_INTERVENTION")
    if not heldout_hostile:
        blockers.append("NO_HELDOUT_HOSTILE_VALIDATION")

    if causal_closed:
        support_level = "CAUSAL_ATTRIBUTION_CLOSED"
    elif observational_support:
        support_level = "STRONG_OBSERVATIONAL_SUPPORT_NOT_CAUSAL"
    else:
        support_level = "INSUFFICIENT_OBSERVATIONAL_SUPPORT"

    return {
        "artifact": "gps_p5_causal_support_assessment",
        "decision_authority": "KX108_ONLY",
        "emits_verdict": False,
        "support_level": support_level,
        "causal_attribution_closed": causal_closed,
        "checks": {
            "detector_truth_free": detector_truth_free,
            "detector_anomaly": detector_anomaly,
            "official_onset_straddled_by_first_anomaly_transition": onset_straddled,
            "cross_receiver_consistent": cross_receiver_consistent,
            "nominal_control_clean": nominal_clean,
            "same_recorded_rf_source_across_receivers": same_recording,
            "independent_physical_source_corroboration": independent_physical_source,
            "controlled_intervention": controlled_intervention,
            "heldout_hostile_validation": heldout_hostile,
        },
        "metrics": {
            "cross_receiver_agreement_m": cross_receiver_agreement_m,
            "cross_receiver_relative_error": cross_receiver_relative_error,
        },
        "blockers": blockers,
        "allowed_claim": (
            "Recorded FGI evidence shows a truth-free temporal anomaly aligned with the "
            "official event boundary, independently reproduced by two receiver implementations, "
            "with a clean real nominal control."
            if observational_support
            else "Evidence does not yet satisfy the P5 observational-support contract."
        ),
        "forbidden_claims": [
            "SPOOFING_CAUSED_THE_OBSERVED_DISPLACEMENT",
            "GENERAL_SPOOFING_DETECTOR_VALIDATED",
            "SPOOFING_RESISTANCE_PROVEN",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    result = assess(evidence)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
