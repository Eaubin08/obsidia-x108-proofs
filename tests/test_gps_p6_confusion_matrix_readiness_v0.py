from __future__ import annotations

import pytest

from periphery.cognition.gps_p6_confusion_matrix_readiness_v0 import (
    CLAIM_BOUNDARY,
    NEGATIVE_REFERENCE,
    POSITIVE_REFERENCE,
    assess_p6_readiness_v0,
    compute_p6_confusion_matrix_v0,
)


def _case(
    case_id: str,
    *,
    split: str,
    reference: str,
    output: str,
):
    return {
        "case_id": case_id,
        "dataset_split": split,
        "reference_condition": reference,
        "classifier_output": output,
        "classifier_claim_boundary": CLAIM_BOUNDARY,
        "truth_or_reference_consumed_by_classifier": False,
    }


def test_current_development_evidence_cannot_be_promoted_to_p6_matrix():
    cases = [
        _case(
            "fgi-development",
            split="DEVELOPMENT",
            reference=POSITIVE_REFERENCE,
            output="ANOMALY",
        ),
        _case(
            "cttc-development-control",
            split="DEVELOPMENT_CONTROL",
            reference=NEGATIVE_REFERENCE,
            output="NOMINAL",
        ),
    ]

    result = assess_p6_readiness_v0(cases, thresholds_frozen=True)

    assert result["status"] == "BLOCKED_HELDOUT_CORPUS_INCOMPLETE"
    assert result["ready_to_compute_matrix"] is False
    assert set(result["blockers"]) == {
        "NO_HELDOUT_POSITIVE_REFERENCE",
        "NO_HELDOUT_NEGATIVE_REFERENCE",
    }
    assert result["spoofing_classifier"] is False
    assert result["causal_attribution"] is False
    assert result["decision_authority"] == "KX108_ONLY"


def test_truth_leak_is_rejected():
    case = _case(
        "leaky",
        split="HELD_OUT",
        reference=POSITIVE_REFERENCE,
        output="ANOMALY",
    )
    case["truth_or_reference_consumed_by_classifier"] = True

    with pytest.raises(ValueError, match="P6_TRUTH_LEAK_FORBIDDEN"):
        assess_p6_readiness_v0([case], thresholds_frozen=True)


def test_claim_promotion_to_spoofing_boundary_is_rejected():
    case = _case(
        "bad-boundary",
        split="HELD_OUT",
        reference=POSITIVE_REFERENCE,
        output="ANOMALY",
    )
    case["classifier_claim_boundary"] = "SPOOFING_DETECTOR"

    with pytest.raises(ValueError, match="P6_CLAIM_BOUNDARY_MISMATCH"):
        assess_p6_readiness_v0([case], thresholds_frozen=True)


def test_unfrozen_thresholds_are_rejected():
    case = _case(
        "heldout-positive",
        split="HELD_OUT",
        reference=POSITIVE_REFERENCE,
        output="ANOMALY",
    )

    with pytest.raises(ValueError, match="P6_REQUIRES_FROZEN_P4_THRESHOLDS"):
        assess_p6_readiness_v0([case], thresholds_frozen=False)


def test_minimal_heldout_matrix_is_computable_but_not_certified():
    cases = [
        _case(
            "hp1",
            split="HELD_OUT",
            reference=POSITIVE_REFERENCE,
            output="ANOMALY",
        ),
        _case(
            "hp2",
            split="HELD_OUT",
            reference=POSITIVE_REFERENCE,
            output="NOMINAL",
        ),
        _case(
            "hn1",
            split="HELD_OUT",
            reference=NEGATIVE_REFERENCE,
            output="NOMINAL",
        ),
        _case(
            "hn2",
            split="HELD_OUT",
            reference=NEGATIVE_REFERENCE,
            output="ANOMALY",
        ),
        _case(
            "hu1",
            split="HELD_OUT",
            reference=NEGATIVE_REFERENCE,
            output="UNKNOWN",
        ),
    ]

    readiness = assess_p6_readiness_v0(cases, thresholds_frozen=True)
    assert readiness["ready_to_compute_matrix"] is True

    matrix = compute_p6_confusion_matrix_v0(
        cases,
        thresholds_frozen=True,
    )
    assert matrix["matrix"] == {"TP": 1, "TN": 1, "FP": 1, "FN": 1}
    assert matrix["unknown_count"] == 1
    assert matrix["evaluated_count"] == 4
    assert matrix["coverage"] == pytest.approx(0.8)
    assert matrix["certification_status"] == "NOT_CERTIFIED"
    assert matrix["decision_authority"] == "KX108_ONLY"


def test_matrix_fails_closed_without_both_heldout_classes():
    cases = [
        _case(
            "only-positive",
            split="HELD_OUT",
            reference=POSITIVE_REFERENCE,
            output="ANOMALY",
        )
    ]

    with pytest.raises(ValueError, match="P6_MATRIX_NOT_READY"):
        compute_p6_confusion_matrix_v0(
            cases,
            thresholds_frozen=True,
        )
