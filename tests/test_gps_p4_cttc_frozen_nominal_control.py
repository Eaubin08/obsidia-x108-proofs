import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CLASSIFIER_PATH = ROOT / "scripts" / "gps" / "p4_temporal_discontinuity_classifier.py"
SPEC_C = importlib.util.spec_from_file_location("p4_temporal_discontinuity_classifier", CLASSIFIER_PATH)
MOD_C = importlib.util.module_from_spec(SPEC_C)
assert SPEC_C and SPEC_C.loader
sys.modules[SPEC_C.name] = MOD_C
SPEC_C.loader.exec_module(MOD_C)

VALIDATOR_PATH = ROOT / "scripts" / "gps" / "p4_validate_frozen_temporal_classifier.py"
SPEC_V = importlib.util.spec_from_file_location("p4_validate_frozen_temporal_classifier", VALIDATOR_PATH)
MOD_V = importlib.util.module_from_spec(SPEC_V)
assert SPEC_V and SPEC_V.loader
sys.modules[SPEC_V.name] = MOD_V
SPEC_V.loader.exec_module(MOD_V)

detect = MOD_C.detect
calibration_from_freeze = MOD_V.calibration_from_freeze


def test_cttc_real_nominal_is_nominal_under_frozen_p4_classifier():
    freeze = json.loads(
        (
            ROOT
            / "hackathons"
            / "nativebuilder-gps-defense"
            / "rf_attack_benchmark"
            / "p4_temporal_classifier_freeze_v0.json"
        ).read_text(encoding="utf-8")
    )
    log = (
        ROOT
        / "hackathons"
        / "nativebuilder-gps-defense"
        / "runs"
        / "iq_cttc_2013_04_04"
        / "gnss_sdr_run_stdout_modern.log"
    )

    result = detect(log, calibration_from_freeze(freeze))

    assert result["overall_classification"] == "NOMINAL"
    assert result["first_anomaly"] is None
    assert result["position_count"] == 149
    assert result["transition_count"] == 148
    assert result["max_observed"]["ecef_step_m"] < freeze["thresholds"]["ecef_step_m"]
    assert result["max_observed"]["clock_residual_s"] < freeze["thresholds"]["clock_residual_s"]
    assert result["max_observed"]["receiver_gap_s"] < freeze["thresholds"]["receiver_gap_s"]
