import importlib.util
import json
import sys
from pathlib import Path

import pytest

from periphery.cognition.gps_defense_p4_p5_evidence_v0 import (
    build_p4_p5_brody_sigma_envelope_v0,
)


ROOT = Path(__file__).resolve().parents[1]
P4 = (
    ROOT
    / "hackathons"
    / "nativebuilder-gps-defense"
    / "rf_attack_benchmark"
    / "p4_temporal_classifier_freeze_v0.json"
)
P5 = (
    ROOT
    / "hackathons"
    / "nativebuilder-gps-defense"
    / "rf_attack_benchmark"
    / "p5_recorded_evidence_input_v0.json"
)
P5_MODULE = ROOT / "scripts" / "gps" / "p5_causal_support_assessment.py"


def _load_inputs():
    p4 = json.loads(P4.read_text(encoding="utf-8"))
    p5_input = json.loads(P5.read_text(encoding="utf-8"))

    spec = importlib.util.spec_from_file_location(
        "p5_causal_support_assessment_test",
        P5_MODULE,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return p4, module.assess(p5_input)


def test_p4_p5_real_recorded_evidence_builds_claim_bounded_hold_envelope():
    p4, p5 = _load_inputs()
    envelope = build_p4_p5_brody_sigma_envelope_v0(
        p4_freeze=p4,
        p5_assessment=p5,
    )

    assert envelope["domain"] == "gps_defense_aviation"
    assert envelope["p4_classification"] == "ANOMALY"
    assert envelope["p4_first_anomaly_transition"] == {
        "from_receiver_second": 132,
        "to_receiver_second": 174,
    }
    assert envelope["p4_violation_count"] == 3
    assert envelope["p4_truth_or_onset_consumed"] is False
    assert envelope["x108_gate"] == "HOLD"
    assert "TEMPORAL_INTEGRITY_ANOMALY" in envelope["gate_reason_codes"]

    assert (
        envelope["p5_support_level"]
        == "STRONG_OBSERVATIONAL_SUPPORT_NOT_CAUSAL"
    )
    assert envelope["causal_attribution_closed"] is False
    assert (
        "NO_INDEPENDENT_PHYSICAL_SOURCE_CORROBORATION"
        in envelope["unknowns"]
    )
    assert "NO_CONTROLLED_INTERVENTION" in envelope["unknowns"]
    assert "NO_HELDOUT_HOSTILE_VALIDATION" in envelope["unknowns"]
    assert (
        "SPOOFING_CAUSED_THE_OBSERVED_DISPLACEMENT"
        in envelope["forbidden_claims"]
    )

    assert envelope["readonly"] is True
    assert envelope["allowed_to_decide"] is False
    assert envelope["allowed_to_act"] is False
    assert envelope["emits_act"] is False
    assert envelope["emits_verdict"] is False
    assert envelope["decision_authority"] == "KX108_ONLY"


def test_p4_truth_leak_is_rejected():
    p4, p5 = _load_inputs()
    p4["development_result"]["truth_or_onset_consumed"] = True

    with pytest.raises(ValueError, match="P4_TRUTH_OR_ONSET_LEAK"):
        build_p4_p5_brody_sigma_envelope_v0(
            p4_freeze=p4,
            p5_assessment=p5,
        )


def test_p4_unfrozen_thresholds_are_rejected():
    p4, p5 = _load_inputs()
    p4["thresholds_may_change_before_blind_validation"] = True

    with pytest.raises(
        ValueError,
        match="P4_FROZEN_THRESHOLD_BOUNDARY_VIOLATED",
    ):
        build_p4_p5_brody_sigma_envelope_v0(
            p4_freeze=p4,
            p5_assessment=p5,
        )


def test_p5_causal_promotion_is_rejected():
    p4, p5 = _load_inputs()
    p5["causal_attribution_closed"] = True

    with pytest.raises(
        ValueError,
        match="P5_CAUSAL_ATTRIBUTION_MUST_REMAIN_OPEN",
    ):
        build_p4_p5_brody_sigma_envelope_v0(
            p4_freeze=p4,
            p5_assessment=p5,
        )


def test_p5_missing_causal_blocker_is_rejected():
    p4, p5 = _load_inputs()
    p5["blockers"] = [
        "NO_CONTROLLED_INTERVENTION",
        "NO_HELDOUT_HOSTILE_VALIDATION",
    ]

    with pytest.raises(
        ValueError,
        match="P5_REQUIRED_CAUSAL_BLOCKERS_MISSING",
    ):
        build_p4_p5_brody_sigma_envelope_v0(
            p4_freeze=p4,
            p5_assessment=p5,
        )


def test_p4_temporal_anomaly_does_not_become_spoofing_nuisance():
    p4, p5 = _load_inputs()
    envelope = build_p4_p5_brody_sigma_envelope_v0(
        p4_freeze=p4,
        p5_assessment=p5,
    )

    assert envelope["x108_gate"] == "HOLD"
    assert envelope["gate_reason_codes"] == [
        "TEMPORAL_INTEGRITY_ANOMALY"
    ]
    assert "GPS_SPOOFING" not in envelope["risk_flags"]
    assert (
        envelope["p4_claim_boundary"]
        == "TRAJECTORY_DISCONTINUITY_ONLY_NO_HOSTILE_OR_CAUSAL_ATTRIBUTION"
    )
