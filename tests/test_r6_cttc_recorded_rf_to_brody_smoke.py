import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "gps" / "r6_cttc_recorded_rf_to_brody_smoke.py"

SPEC = importlib.util.spec_from_file_location(
    "r6_cttc_recorded_rf_to_brody_smoke",
    SCRIPT,
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_recorded_rf_smoke_contract(monkeypatch):
    monkeypatch.setattr(
        MODULE,
        "run_brody_real_response_pipeline",
        lambda **kwargs: {
            "response_source": "REAL_BRODY_RUNTIME",
            "response_md": "readonly",
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
            "sigma_domain_packet_sha256": "a" * 64,
            "components": {
                "W3_BRODY": "READY:REAL_RUNTIME_ADAPTER",
            },
            "kx108_admission": "DRY_RUN",
            "upstream_x108_gate_constraint": envelope["x108_gate"],
            "decision_ticket_dry_run": {
                "decision": "HOLD",
                "x108_gate_status": "X108_DRY_RUN_UPSTREAM_HOLD",
                "dry_run": True,
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

    report = MODULE.build_report(MODULE.DEFAULT_ARTIFACT)

    assert report["status"] == "RECORDED_REAL_RF_TO_BRODY_VERIFIED"
    assert report["verified"] is True
    assert report["source_proof_level"] == "RECORDED_REAL_RF"
    assert report["recorded_x108_gate"] == "HOLD"
    assert report["recorded_market_verdict"] == "RECALC_TRAJECTORY"
    assert report["checks"]["evidence_envelope_preserved_exactly"] is True
    assert report["checks"]["sigma_envelope_hash_present"] is True
    assert report["checks"]["no_decision_promotion"] is True
    assert report["checks"]["recorded_gate_preserved_in_cognitive_ticket"] is True
    assert report["checks"]["brody_pre_reasoning_unblocked"] is True
    assert report["brody_remaining_resolution_targets"] == []
    assert report["cognitive_ticket_decision"] == "HOLD"
