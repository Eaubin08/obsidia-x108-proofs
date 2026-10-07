import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "gps" / "p4_temporal_detection_to_domain_evidence.py"
SPEC = importlib.util.spec_from_file_location("p4_temporal_detection_to_domain_evidence", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

build_temporal_domain_evidence = MODULE.build_temporal_domain_evidence


def test_anomaly_adapter_is_evidence_only_and_claim_bounded():
    detection = {
        "overall_classification": "ANOMALY",
        "algorithm_version": "P4_TEMPORAL_DISCONTINUITY_V0",
        "status": "DEVELOPMENT_POST_HOC_NOT_BLIND",
        "truth_or_onset_consumed": False,
        "first_anomaly": {
            "ecef_step_m": 14639.905,
            "clock_residual_s": 35269.5,
            "receiver_gap_s": 42.0,
        },
        "thresholds": {
            "ecef_step_m": 169.6355,
            "clock_residual_s": 5.0,
            "receiver_gap_s": 10.0,
        },
        "claim_boundary": "TRAJECTORY_DISCONTINUITY_ONLY_NO_HOSTILE_OR_CAUSAL_ATTRIBUTION",
        "input_log_sha256": "1" * 64,
        "calibration_log_sha256": "1" * 64,
    }

    result = build_temporal_domain_evidence(detection)

    assert result["temporal_integrity_classification"] == "ANOMALY"
    assert result["temporal_integrity_anomaly"] is True
    assert result["emits_verdict"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["truth_or_onset_consumed"] is False
    assert len(result["temporal_integrity_evidence_hash"]) == 64
    assert "HOSTILE" in result["claim_boundary"]
