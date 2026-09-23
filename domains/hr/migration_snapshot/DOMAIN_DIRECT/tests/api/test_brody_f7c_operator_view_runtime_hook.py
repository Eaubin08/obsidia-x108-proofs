from pathlib import Path

from apps.obsidia_api.brody_operator_view_packet import build_operator_view_packet


def test_routes_imports_operator_view_packet():
    src = Path("apps/obsidia_api/routes/brody.py").read_text(encoding="utf-8")
    assert "from apps.obsidia_api.brody_operator_view_packet import build_operator_view_packet" in src


def test_routes_builds_operator_view_packet_after_value_layer():
    src = Path("apps/obsidia_api/routes/brody.py").read_text(encoding="utf-8")
    assert "_operator_view_raw = safe_call_snapshot(" in src
    assert '"operator_view_packet"' in src
    assert "_operator_view_packet" in src
    assert "value_layer=value_layer" in src
    assert "sigma_packet=_sigma_packet" in src
    assert "anti_mismatch_packet=_anti_mismatch_packet" in src
    assert "thermodynamics_packet=_thermodynamics_packet" in src
    assert "gencoin_shadow_packet=_gencoin_shadow_packet" in src
    assert "tree_signal_packet=_tree_signal_packet" in src
    assert "memory_promotion_guard_packet=_memory_promotion_guard_packet" in src


def test_routes_exposes_operator_view_packet_payload():
    src = Path("apps/obsidia_api/routes/brody.py").read_text(encoding="utf-8")
    assert '"operator_view_packet": _operator_view_packet' in src


def test_operator_view_runtime_ready_sample():
    out = build_operator_view_packet(
        value_layer={
            "final_scoring_enabled": False,
            "scores": {
                "cognitive_value": None,
                "proof_value": None,
                "reuse_value": None,
                "memory_value": None,
                "attention_cost": None,
                "energy_cost": None,
                "economic_projection": None,
            },
        },
        sigma_packet={"version": "SIGMA_CALIBRATION_PACKET_V1", "truth_score": 0.8, "usable_for_gencoin": True},
        anti_mismatch_packet={"version": "ANTI_MISMATCH_SIGNAL_V1", "mismatch_score": 0.1, "risk_level": "LOW"},
        thermodynamics_packet={"version": "THERMODYNAMICS_PACKET_V1", "stability_state": "STABLE", "usable_for_gencoin": True},
        gencoin_shadow_packet={"version": "GENCOIN_SHADOW_VALUE_PACKET_V1", "usable_shadow_value": True},
        tree_signal_packet={"version": "TREE_SIGNAL_PACKET_V1", "trees_formal_computation": True, "usable_for_gencoin_shadow": True},
        memory_promotion_guard_packet={
            "version": "MEMORY_PROMOTION_GUARD_V1",
            "guard_status": "PROMOTION_CANDIDATE_HUMAN_REVIEW_ONLY",
            "eligible_for_human_review": True,
            "readiness_score": 0.7,
            "write_allowed": False,
            "graphiti_write_allowed": False,
            "neo4j_write_allowed": False,
            "canon_promotion_allowed": False,
            "memory_promotion_allowed": False,
        },
        domain_sigma_envelope={
            "mode": "READONLY_DOMAIN_SIGMA_ENVELOPE",
            "domain": "bank",
            "x108_gate": {"status": "HOLD", "source": "sigma_readonly"},
            "decision_authority": "KX108_ONLY",
            "readonly": True,
            "emits_act": False,
            "advisory_only": True,
        },
    )["operator_view_packet"]

    assert out["version"] == "OPERATOR_VIEW_PACKET_V1"
    assert out["system_status"] == "OPERATOR_READY_READONLY"
    assert out["summary"]["operator_can_view"] is True
    assert out["summary"]["operator_can_write"] is False
    assert out["summary"]["operator_can_decide"] is False
    assert out["emits_act"] is False
    assert out["emits_verdict"] is False
