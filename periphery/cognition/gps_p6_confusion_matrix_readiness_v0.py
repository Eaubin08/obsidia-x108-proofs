"""P6 GPS confusion-matrix readiness contract.

This module evaluates only the frozen P4 temporal trajectory-discontinuity
classifier. It does not classify spoofing, hostility, or causality.

Decision authority remains KX108_ONLY.
"""
from __future__ import annotations

from typing import Any

CLAIM_BOUNDARY = (
    "TRAJECTORY_DISCONTINUITY_CLASSIFIER_ONLY_NO_SPOOFING_OR_CAUSAL_ATTRIBUTION"
)
POSITIVE_REFERENCE = "TRAJECTORY_DISCONTINUITY_PRESENT"
NEGATIVE_REFERENCE = "TRAJECTORY_DISCONTINUITY_ABSENT"
VALID_OUTPUTS = {"ANOMALY", "NOMINAL", "UNKNOWN"}
VALID_REFERENCES = {POSITIVE_REFERENCE, NEGATIVE_REFERENCE}


def _validate_case(case: dict[str, Any]) -> None:
    if not isinstance(case, dict):
        raise TypeError("P6_CASE_OBJECT_REQUIRED")
    if not str(case.get("case_id") or "").strip():
        raise ValueError("P6_CASE_ID_REQUIRED")
    if case.get("classifier_claim_boundary") != CLAIM_BOUNDARY:
        raise ValueError("P6_CLAIM_BOUNDARY_MISMATCH")
    if case.get("truth_or_reference_consumed_by_classifier") is not False:
        raise ValueError("P6_TRUTH_LEAK_FORBIDDEN")

    reference = str(case.get("reference_condition") or "")
    output = str(case.get("classifier_output") or "").upper()
    if reference not in VALID_REFERENCES:
        raise ValueError("P6_REFERENCE_CONDITION_INVALID")
    if output not in VALID_OUTPUTS:
        raise ValueError("P6_CLASSIFIER_OUTPUT_INVALID")


def assess_p6_readiness_v0(
    cases: list[dict[str, Any]],
    *,
    thresholds_frozen: bool,
) -> dict[str, Any]:
    if thresholds_frozen is not True:
        raise ValueError("P6_REQUIRES_FROZEN_P4_THRESHOLDS")

    for case in cases:
        _validate_case(case)

    heldout = [
        case
        for case in cases
        if str(case.get("dataset_split") or "").upper() == "HELD_OUT"
    ]
    heldout_positive = [
        case for case in heldout
        if case["reference_condition"] == POSITIVE_REFERENCE
    ]
    heldout_negative = [
        case for case in heldout
        if case["reference_condition"] == NEGATIVE_REFERENCE
    ]

    blockers: list[str] = []
    if not heldout_positive:
        blockers.append("NO_HELDOUT_POSITIVE_REFERENCE")
    if not heldout_negative:
        blockers.append("NO_HELDOUT_NEGATIVE_REFERENCE")

    ready = not blockers
    return {
        "artifact": "gps_p6_confusion_matrix_readiness_v0",
        "status": (
            "READY_TO_COMPUTE_HELDOUT_MATRIX_NOT_CERTIFIED"
            if ready
            else "BLOCKED_HELDOUT_CORPUS_INCOMPLETE"
        ),
        "ready_to_compute_matrix": ready,
        "claim_boundary": CLAIM_BOUNDARY,
        "classifier_target": "TRAJECTORY_DISCONTINUITY",
        "spoofing_classifier": False,
        "causal_attribution": False,
        "thresholds_frozen": True,
        "total_cases": len(cases),
        "heldout_cases": len(heldout),
        "heldout_positive_cases": len(heldout_positive),
        "heldout_negative_cases": len(heldout_negative),
        "blockers": blockers,
        "certification_status": "NOT_CERTIFIED",
        "certification_blockers": [
            "NO_INDEPENDENT_PHYSICAL_SOURCE_CORROBORATION",
            "NO_CONTROLLED_INTERVENTION",
        ],
        "decision_authority": "KX108_ONLY",
        "readonly": True,
        "advisory_only": True,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
        "emits_verdict": False,
        "memory_write": False,
        "kernel_mutation": False,
        "x108_mutation": False,
    }


def compute_p6_confusion_matrix_v0(
    cases: list[dict[str, Any]],
    *,
    thresholds_frozen: bool,
) -> dict[str, Any]:
    readiness = assess_p6_readiness_v0(
        cases,
        thresholds_frozen=thresholds_frozen,
    )
    if readiness["ready_to_compute_matrix"] is not True:
        raise ValueError("P6_MATRIX_NOT_READY")

    heldout = [
        case
        for case in cases
        if str(case.get("dataset_split") or "").upper() == "HELD_OUT"
    ]

    tp = tn = fp = fn = unknown = 0
    for case in heldout:
        reference_positive = case["reference_condition"] == POSITIVE_REFERENCE
        output = str(case["classifier_output"]).upper()

        if output == "UNKNOWN":
            unknown += 1
        elif reference_positive and output == "ANOMALY":
            tp += 1
        elif reference_positive and output == "NOMINAL":
            fn += 1
        elif (not reference_positive) and output == "ANOMALY":
            fp += 1
        elif (not reference_positive) and output == "NOMINAL":
            tn += 1

    evaluated = tp + tn + fp + fn
    return {
        "artifact": "gps_p6_confusion_matrix_v0",
        "status": "HELDOUT_MATRIX_COMPUTED_NOT_CERTIFIED",
        "claim_boundary": CLAIM_BOUNDARY,
        "matrix": {"TP": tp, "TN": tn, "FP": fp, "FN": fn},
        "unknown_count": unknown,
        "evaluated_count": evaluated,
        "heldout_case_count": len(heldout),
        "coverage": (
            evaluated / len(heldout)
            if heldout else 0.0
        ),
        "certification_status": "NOT_CERTIFIED",
        "decision_authority": "KX108_ONLY",
        "readonly": True,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
        "emits_verdict": False,
        "memory_write": False,
        "kernel_mutation": False,
        "x108_mutation": False,
    }
