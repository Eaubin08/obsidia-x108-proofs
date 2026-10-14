import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "gps" / "r6_p6_confusion_matrix_readiness_smoke.py"

SPEC = importlib.util.spec_from_file_location(
    "r6_p6_confusion_matrix_readiness_smoke",
    SCRIPT,
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_current_real_evidence_remains_blocked_from_p6_matrix():
    report = MODULE.build_report()

    assert report["verified"] is True
    assert report["status"] == "P6_READINESS_BLOCKED_AS_EXPECTED"

    readiness = report["readiness"]
    assert readiness["ready_to_compute_matrix"] is False
    assert readiness["heldout_cases"] == 0
    assert set(readiness["blockers"]) == {
        "NO_HELDOUT_POSITIVE_REFERENCE",
        "NO_HELDOUT_NEGATIVE_REFERENCE",
    }
    assert readiness["classifier_target"] == "TRAJECTORY_DISCONTINUITY"
    assert readiness["spoofing_classifier"] is False
    assert readiness["causal_attribution"] is False
    assert readiness["certification_status"] == "NOT_CERTIFIED"
    assert readiness["decision_authority"] == "KX108_ONLY"


def test_real_evidence_cases_are_development_only():
    cases = MODULE.build_current_cases()

    assert len(cases) == 2
    by_id = {case["case_id"]: case for case in cases}

    hostile = by_id["FGI_UT_DFMC_L1E1_DEVELOPMENT"]
    nominal = by_id["CTTC_REAL_RF_NOMINAL_DEVELOPMENT_CONTROL"]

    assert hostile["dataset_split"] == "DEVELOPMENT"
    assert hostile["classifier_output"] == "ANOMALY"
    assert hostile["truth_or_reference_consumed_by_classifier"] is False

    assert nominal["dataset_split"] == "DEVELOPMENT_CONTROL"
    assert nominal["classifier_output"] == "NOMINAL"
    assert nominal["truth_or_reference_consumed_by_classifier"] is False
