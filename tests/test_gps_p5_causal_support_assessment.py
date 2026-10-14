import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "gps" / "p5_causal_support_assessment.py"
SPEC = importlib.util.spec_from_file_location("p5_causal_support_assessment", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

assess = MODULE.assess


def test_p5_recorded_evidence_is_strong_observational_support_not_causal():
    evidence = json.loads(
        (
            ROOT
            / "hackathons"
            / "nativebuilder-gps-defense"
            / "rf_attack_benchmark"
            / "p5_recorded_evidence_input_v0.json"
        ).read_text(encoding="utf-8")
    )

    result = assess(evidence)

    assert result["support_level"] == "STRONG_OBSERVATIONAL_SUPPORT_NOT_CAUSAL"
    assert result["causal_attribution_closed"] is False
    assert result["emits_verdict"] is False
    assert result["decision_authority"] == "KX108_ONLY"

    checks = result["checks"]
    assert checks["detector_truth_free"] is True
    assert checks["detector_anomaly"] is True
    assert checks["official_onset_straddled_by_first_anomaly_transition"] is True
    assert checks["cross_receiver_consistent"] is True
    assert checks["nominal_control_clean"] is True
    assert checks["same_recorded_rf_source_across_receivers"] is True

    assert checks["independent_physical_source_corroboration"] is False
    assert checks["controlled_intervention"] is False
    assert checks["heldout_hostile_validation"] is False

    assert result["metrics"]["cross_receiver_agreement_m"] < 2.0
    assert "NO_INDEPENDENT_PHYSICAL_SOURCE_CORROBORATION" in result["blockers"]
    assert "NO_CONTROLLED_INTERVENTION" in result["blockers"]
    assert "NO_HELDOUT_HOSTILE_VALIDATION" in result["blockers"]

    assert "SPOOFING_CAUSED_THE_OBSERVED_DISPLACEMENT" in result["forbidden_claims"]
