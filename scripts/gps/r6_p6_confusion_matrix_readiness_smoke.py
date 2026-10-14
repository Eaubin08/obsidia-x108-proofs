#!/usr/bin/env python3
"""P6 GPS confusion-matrix readiness smoke from current recorded P4/P5 evidence.

This script intentionally does not compute TP/TN/FP/FN from development data.
It converts the current real recorded evidence into bounded readiness cases and
expects P6 to remain fail-closed until a held-out positive and held-out negative
reference corpus exist.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from periphery.cognition.gps_p6_confusion_matrix_readiness_v0 import (
    CLAIM_BOUNDARY,
    NEGATIVE_REFERENCE,
    POSITIVE_REFERENCE,
    assess_p6_readiness_v0,
)

P4_FREEZE = (
    ROOT
    / "hackathons"
    / "nativebuilder-gps-defense"
    / "rf_attack_benchmark"
    / "p4_temporal_classifier_freeze_v0.json"
)
P5_INPUT = (
    ROOT
    / "hackathons"
    / "nativebuilder-gps-defense"
    / "rf_attack_benchmark"
    / "p5_recorded_evidence_input_v0.json"
)


def build_current_cases() -> list[dict[str, Any]]:
    p4 = json.loads(P4_FREEZE.read_text(encoding="utf-8"))
    p5 = json.loads(P5_INPUT.read_text(encoding="utf-8"))

    if p4.get("artifact") != "p4_temporal_classifier_freeze_v0":
        raise ValueError("P6_P4_ARTIFACT_MISMATCH")
    if p4.get("thresholds_may_change_before_blind_validation") is not False:
        raise ValueError("P6_P4_THRESHOLDS_NOT_FROZEN")
    if p4.get("development_status") != "DEVELOPMENT_POST_HOC_NOT_BLIND":
        raise ValueError("P6_P4_DEVELOPMENT_STATUS_MISMATCH")

    dev = p4.get("development_result") or {}
    if dev.get("truth_or_onset_consumed") is not False:
        raise ValueError("P6_P4_TRUTH_LEAK")
    if p5.get("truth_or_onset_consumed") is not False:
        raise ValueError("P6_P5_TRUTH_LEAK")

    hostile_development_case = {
        "case_id": "FGI_UT_DFMC_L1E1_DEVELOPMENT",
        "dataset_split": "DEVELOPMENT",
        "reference_condition": POSITIVE_REFERENCE,
        "classifier_output": str(dev.get("classification") or "").upper(),
        "classifier_claim_boundary": CLAIM_BOUNDARY,
        "truth_or_reference_consumed_by_classifier": False,
        "source_kind": "REAL_RECORDED_RF_FGI",
        "same_recorded_rf_source_across_receivers": (
            p5.get("same_recorded_rf_source_across_receivers") is True
        ),
    }

    nominal_development_control = {
        "case_id": "CTTC_REAL_RF_NOMINAL_DEVELOPMENT_CONTROL",
        "dataset_split": "DEVELOPMENT_CONTROL",
        "reference_condition": NEGATIVE_REFERENCE,
        "classifier_output": str(
            p5.get("nominal_control_classification") or ""
        ).upper(),
        "classifier_claim_boundary": CLAIM_BOUNDARY,
        "truth_or_reference_consumed_by_classifier": False,
        "source_kind": "REAL_RECORDED_RF_CTTC_NOMINAL_CONTROL",
    }

    return [hostile_development_case, nominal_development_control]


def build_report() -> dict[str, Any]:
    cases = build_current_cases()
    readiness = assess_p6_readiness_v0(cases, thresholds_frozen=True)

    expected_blockers = {
        "NO_HELDOUT_POSITIVE_REFERENCE",
        "NO_HELDOUT_NEGATIVE_REFERENCE",
    }
    actual_blockers = set(readiness.get("blockers") or [])

    checks = {
        "current_evidence_not_promoted_to_heldout": (
            readiness.get("heldout_cases") == 0
        ),
        "matrix_remains_blocked": (
            readiness.get("ready_to_compute_matrix") is False
            and readiness.get("status") == "BLOCKED_HELDOUT_CORPUS_INCOMPLETE"
        ),
        "heldout_blockers_exact": actual_blockers == expected_blockers,
        "trajectory_only_claim_boundary": (
            readiness.get("classifier_target") == "TRAJECTORY_DISCONTINUITY"
            and readiness.get("spoofing_classifier") is False
            and readiness.get("causal_attribution") is False
        ),
        "not_certified": readiness.get("certification_status") == "NOT_CERTIFIED",
        "kx108_only": readiness.get("decision_authority") == "KX108_ONLY",
        "no_authority_or_mutation": (
            readiness.get("allowed_to_decide") is False
            and readiness.get("allowed_to_act") is False
            and readiness.get("emits_act") is False
            and readiness.get("emits_verdict") is False
            and readiness.get("memory_write") is False
            and readiness.get("kernel_mutation") is False
            and readiness.get("x108_mutation") is False
        ),
    }

    verified = all(bool(v) for v in checks.values())
    return {
        "artifact": "r6_gps_p6_confusion_matrix_readiness_smoke",
        "status": (
            "P6_READINESS_BLOCKED_AS_EXPECTED"
            if verified
            else "P6_READINESS_BOUNDARY_FAILED"
        ),
        "verified": verified,
        "cases": cases,
        "readiness": readiness,
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    report = build_report()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if report["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
