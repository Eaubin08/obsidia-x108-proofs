import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "gps" / "r6_p4_p5_recorded_evidence_to_brody_smoke.py"

SPEC = importlib.util.spec_from_file_location(
    "r6_p4_p5_recorded_evidence_to_brody_smoke",
    SCRIPT,
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_p4_p5_smoke_contract(monkeypatch):
    monkeypatch.setattr(
        MODULE,
        "run_brody_real_response_pipeline",
        lambda **kwargs: {
            "response_source": "REAL_BRODY_RUNTIME",
            "decision_authority": "KX108_ONLY",
            "emits_act": False,
            "pre_reasoning_snapshot": {
                "reasoning_directive": {
                    "resolution_targets": [],
                },
            },
        },
    )

    def fake_join(**kwargs):
        envelope = kwargs["precomputed_domain_sigma_envelope"]
        return {
            "status": "READY_SHADOW_READONLY",
            "completeness": "COMPLETE",
            "sigma_domain_packet": envelope,
            "sigma_domain_packet_source": "PRECOMPUTED_READONLY",
            "upstream_x108_gate_constraint": "HOLD",
            "decision_ticket_dry_run": {
                "decision": "HOLD",
                "x108_gate_status": "X108_DRY_RUN_UPSTREAM_HOLD",
                "decision_authority": "KX108_ONLY",
                "emits_act": False,
            },
            "decision_authority": "KX108_ONLY",
            "allowed_to_decide": False,
            "allowed_to_act": False,
            "emits_act": False,
            "emits_verdict": False,
        }

    monkeypatch.setattr(MODULE, "run_real_cognitive_join", fake_join)

    report = MODULE.build_report()

    assert report["status"] == "P4_P5_RECORDED_EVIDENCE_TO_BRODY_VERIFIED"
    assert report["verified"] is True
    assert report["p4_classification"] == "ANOMALY"
    assert report["p4_first_anomaly_transition"] == {
        "from_receiver_second": 132,
        "to_receiver_second": 174,
    }
    assert (
        report["p5_support_level"]
        == "STRONG_OBSERVATIONAL_SUPPORT_NOT_CAUSAL"
    )
    assert report["causal_attribution_closed"] is False
    assert report["recorded_x108_gate"] == "HOLD"
    assert report["cognitive_ticket_decision"] == "HOLD"
    assert report["checks"]["spoofing_causal_claim_forbidden"] is True
    assert report["checks"]["brody_pre_reasoning_unblocked"] is True
    assert report["brody_remaining_resolution_targets"] == []
    assert report["checks"]["no_act_or_verdict"] is True
