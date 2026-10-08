from __future__ import annotations

import pytest

from periphery.cognition.gps_p6_confusion_matrix_readiness_v0 import (
    CLAIM_BOUNDARY,
    NEGATIVE_REFERENCE,
    POSITIVE_REFERENCE,
)
from periphery.cognition.gps_p6_heldout_corpus_contract_v0 import (
    admit_heldout_corpus_case_v0,
    fingerprint_admitted_case_v0,
)


H = "a" * 64


def _case(reference=POSITIVE_REFERENCE):
    return {
        "case_id": "HELDOUT_CASE_001",
        "source_id": "NEW_INDEPENDENT_CAPTURE_001",
        "dataset_split": "HELD_OUT",
        "classifier_claim_boundary": CLAIM_BOUNDARY,
        "reference_condition": reference,
        "thresholds_frozen_before_case_admission": True,
        "used_for_threshold_selection": False,
        "used_for_classifier_development": False,
        "truth_or_reference_visible_to_classifier": False,
        "classifier_output_written_before_reference_unseal": True,
        "reference_unsealed_post_classification": True,
        "rf_artifact_sha256": H,
        "classifier_output_sha256": "b" * 64,
        "reference_manifest_sha256": "c" * 64,
        "independent_from_development_corpus": True,
        "provenance": {
            "provider": "example-provider",
            "dataset_or_capture_name": "capture-001",
            "acquisition_kind": "RECORDED_RF",
            "license_or_authorization": "AUTHORIZED_TEST_USE",
        },
    }


def test_valid_positive_heldout_case_is_admitted():
    out = admit_heldout_corpus_case_v0(_case())
    assert out["status"] == "HELDOUT_CASE_ADMITTED_NOT_CERTIFIED"
    assert out["reference_condition"] == POSITIVE_REFERENCE
    assert out["decision_authority"] == "KX108_ONLY"
    assert out["allowed_to_act"] is False


def test_valid_negative_heldout_case_is_admitted():
    out = admit_heldout_corpus_case_v0(_case(NEGATIVE_REFERENCE))
    assert out["reference_condition"] == NEGATIVE_REFERENCE


def test_current_fgi_development_case_cannot_be_recycled_as_heldout():
    case = _case()
    case["case_id"] = "FGI_UT_DFMC_L1E1_DEVELOPMENT"
    with pytest.raises(ValueError, match="P6_DEVELOPMENT_SOURCE_REUSE_FORBIDDEN"):
        admit_heldout_corpus_case_v0(case)


def test_current_cttc_control_cannot_be_recycled_as_heldout():
    case = _case(NEGATIVE_REFERENCE)
    case["source_id"] = "CTTC_REAL_RF_NOMINAL_DEVELOPMENT_CONTROL"
    with pytest.raises(ValueError, match="P6_DEVELOPMENT_SOURCE_REUSE_FORBIDDEN"):
        admit_heldout_corpus_case_v0(case)


def test_truth_visibility_is_rejected():
    case = _case()
    case["truth_or_reference_visible_to_classifier"] = True
    with pytest.raises(ValueError, match="P6_TRUTH_VISIBILITY_FORBIDDEN"):
        admit_heldout_corpus_case_v0(case)


def test_threshold_tuning_with_heldout_case_is_rejected():
    case = _case()
    case["used_for_threshold_selection"] = True
    with pytest.raises(ValueError, match="P6_HELDOUT_CASE_USED_FOR_THRESHOLD_SELECTION"):
        admit_heldout_corpus_case_v0(case)


def test_classifier_development_reuse_is_rejected():
    case = _case()
    case["used_for_classifier_development"] = True
    with pytest.raises(ValueError, match="P6_HELDOUT_CASE_USED_FOR_DEVELOPMENT"):
        admit_heldout_corpus_case_v0(case)


def test_unsealed_reference_before_output_is_rejected():
    case = _case()
    case["classifier_output_written_before_reference_unseal"] = False
    with pytest.raises(ValueError, match="P6_OUTPUT_MUST_PRECEDE_REFERENCE_UNSEAL"):
        admit_heldout_corpus_case_v0(case)


def test_bad_hash_is_rejected():
    case = _case()
    case["rf_artifact_sha256"] = "bad"
    with pytest.raises(ValueError, match="P6_RF_SHA256_REQUIRED"):
        admit_heldout_corpus_case_v0(case)


def test_provenance_is_required():
    case = _case()
    case["provenance"]["provider"] = ""
    with pytest.raises(ValueError, match="P6_PROVENANCE_INCOMPLETE"):
        admit_heldout_corpus_case_v0(case)


def test_development_independence_is_required():
    case = _case()
    case["independent_from_development_corpus"] = False
    with pytest.raises(ValueError, match="P6_INDEPENDENCE_FROM_DEVELOPMENT_REQUIRED"):
        admit_heldout_corpus_case_v0(case)


def test_fingerprint_is_deterministic():
    admitted = admit_heldout_corpus_case_v0(_case())
    assert fingerprint_admitted_case_v0(admitted) == fingerprint_admitted_case_v0(admitted)
    assert len(fingerprint_admitted_case_v0(admitted)) == 64
