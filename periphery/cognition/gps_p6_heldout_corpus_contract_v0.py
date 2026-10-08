"""P6 held-out corpus admission contract for GPS trajectory-discontinuity validation.

Admits only evidence that is genuinely held out from P4 development/calibration.
This contract does not certify spoofing, hostility, causality, or aviation safety.
"""
from __future__ import annotations

import hashlib
from typing import Any

from periphery.cognition.gps_p6_confusion_matrix_readiness_v0 import (
    CLAIM_BOUNDARY,
    NEGATIVE_REFERENCE,
    POSITIVE_REFERENCE,
)

CURRENT_DEVELOPMENT_SOURCE_IDS = {
    "FGI_UT_DFMC_L1E1_DEVELOPMENT",
    "CTTC_REAL_RF_NOMINAL_DEVELOPMENT_CONTROL",
}

VALID_REFERENCE_CONDITIONS = {
    POSITIVE_REFERENCE,
    NEGATIVE_REFERENCE,
}


def _is_sha256(value: Any) -> bool:
    text = str(value or "").lower()
    if len(text) != 64:
        return False
    try:
        int(text, 16)
    except ValueError:
        return False
    return True


def admit_heldout_corpus_case_v0(case: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(case, dict):
        raise TypeError("P6_HELDOUT_CASE_OBJECT_REQUIRED")

    case_id = str(case.get("case_id") or "").strip()
    source_id = str(case.get("source_id") or "").strip()
    if not case_id:
        raise ValueError("P6_HELDOUT_CASE_ID_REQUIRED")
    if not source_id:
        raise ValueError("P6_HELDOUT_SOURCE_ID_REQUIRED")

    if case_id in CURRENT_DEVELOPMENT_SOURCE_IDS or source_id in CURRENT_DEVELOPMENT_SOURCE_IDS:
        raise ValueError("P6_DEVELOPMENT_SOURCE_REUSE_FORBIDDEN")

    if str(case.get("dataset_split") or "").upper() != "HELD_OUT":
        raise ValueError("P6_DATASET_SPLIT_MUST_BE_HELD_OUT")

    if case.get("classifier_claim_boundary") != CLAIM_BOUNDARY:
        raise ValueError("P6_CLAIM_BOUNDARY_MISMATCH")

    reference = str(case.get("reference_condition") or "")
    if reference not in VALID_REFERENCE_CONDITIONS:
        raise ValueError("P6_REFERENCE_CONDITION_INVALID")

    if case.get("thresholds_frozen_before_case_admission") is not True:
        raise ValueError("P6_THRESHOLDS_MUST_BE_FROZEN_BEFORE_ADMISSION")

    if case.get("used_for_threshold_selection") is not False:
        raise ValueError("P6_HELDOUT_CASE_USED_FOR_THRESHOLD_SELECTION")

    if case.get("used_for_classifier_development") is not False:
        raise ValueError("P6_HELDOUT_CASE_USED_FOR_DEVELOPMENT")

    if case.get("truth_or_reference_visible_to_classifier") is not False:
        raise ValueError("P6_TRUTH_VISIBILITY_FORBIDDEN")

    if case.get("classifier_output_written_before_reference_unseal") is not True:
        raise ValueError("P6_OUTPUT_MUST_PRECEDE_REFERENCE_UNSEAL")

    if case.get("reference_unsealed_post_classification") is not True:
        raise ValueError("P6_REFERENCE_UNSEAL_REQUIRED")

    if not _is_sha256(case.get("rf_artifact_sha256")):
        raise ValueError("P6_RF_SHA256_REQUIRED")

    if not _is_sha256(case.get("classifier_output_sha256")):
        raise ValueError("P6_CLASSIFIER_OUTPUT_SHA256_REQUIRED")

    if not _is_sha256(case.get("reference_manifest_sha256")):
        raise ValueError("P6_REFERENCE_MANIFEST_SHA256_REQUIRED")

    provenance = case.get("provenance")
    if not isinstance(provenance, dict):
        raise ValueError("P6_PROVENANCE_REQUIRED")

    required_provenance = (
        "provider",
        "dataset_or_capture_name",
        "acquisition_kind",
        "license_or_authorization",
    )
    missing = [k for k in required_provenance if not str(provenance.get(k) or "").strip()]
    if missing:
        raise ValueError("P6_PROVENANCE_INCOMPLETE:" + ",".join(missing))

    independent_from_development = case.get("independent_from_development_corpus")
    if independent_from_development is not True:
        raise ValueError("P6_INDEPENDENCE_FROM_DEVELOPMENT_REQUIRED")

    return {
        "artifact": "gps_p6_heldout_corpus_admission_v0",
        "status": "HELDOUT_CASE_ADMITTED_NOT_CERTIFIED",
        "case_id": case_id,
        "source_id": source_id,
        "dataset_split": "HELD_OUT",
        "reference_condition": reference,
        "claim_boundary": CLAIM_BOUNDARY,
        "rf_artifact_sha256": str(case["rf_artifact_sha256"]).lower(),
        "classifier_output_sha256": str(case["classifier_output_sha256"]).lower(),
        "reference_manifest_sha256": str(case["reference_manifest_sha256"]).lower(),
        "provenance": dict(provenance),
        "thresholds_frozen_before_case_admission": True,
        "truth_or_reference_visible_to_classifier": False,
        "classifier_output_written_before_reference_unseal": True,
        "reference_unsealed_post_classification": True,
        "independent_from_development_corpus": True,
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


def fingerprint_admitted_case_v0(admitted: dict[str, Any]) -> str:
    payload = (
        str(admitted.get("case_id")) + "|" +
        str(admitted.get("source_id")) + "|" +
        str(admitted.get("rf_artifact_sha256")) + "|" +
        str(admitted.get("classifier_output_sha256")) + "|" +
        str(admitted.get("reference_manifest_sha256"))
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
