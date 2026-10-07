import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "gps" / "p4_temporal_domain_gate_replay.py"
SPEC = importlib.util.spec_from_file_location("p4_temporal_domain_gate_replay", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

run = MODULE.run


def test_temporal_anomaly_replay_fail_closes_without_spoofing_claim():
    evidence = {
        "temporal_integrity_classification": "ANOMALY",
        "temporal_integrity_evidence_hash": "e" * 64,
        "temporal_integrity_algorithm_version": "P4_TEMPORAL_DISCONTINUITY_V0",
        "temporal_integrity_status": "DEVELOPMENT_POST_HOC_NOT_BLIND",
        "claim_boundary": "TRAJECTORY_DISCONTINUITY_ONLY_NO_HOSTILE_OR_CAUSAL_ATTRIBUTION",
    }

    result = run(evidence)

    assert result["gate_verdict"] == "HOLD"
    assert result["gate_source"] == "REALITY_AUTHENTICITY_GATE_FAIL_CLOSED"
    assert "TEMPORAL_INTEGRITY_ANOMALY" in result["reality_authenticity_reasons"]
    assert "GPS_SPOOFING" not in result["nuisances"]
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["connector_decides"] is False
    assert result["receipt"]["connector_decides"] is False
