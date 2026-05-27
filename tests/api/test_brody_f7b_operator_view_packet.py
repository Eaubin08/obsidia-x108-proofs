from apps.obsidia_api.brody_operator_view_packet import build_operator_view_packet


def _packet(**kwargs):
    return build_operator_view_packet(**kwargs)["operator_view_packet"]


def _ready_inputs():
    return dict(
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
        sigma_packet={
            "version": "SIGMA_CALIBRATION_PACKET_V1",
            "truth_score": 0.82,
            "usable_for_gencoin": True,
        },
        anti_mismatch_packet={
            "version": "ANTI_MISMATCH_SIGNAL_V1",
            "mismatch_score": 0.10,
            "risk_level": "LOW",
        },
        thermodynamics_packet={
            "version": "THERMODYNAMICS_PACKET_V1",
            "stability_state": "STABLE",
            "usable_for_gencoin": True,
        },
        gencoin_shadow_packet={
            "version": "GENCOIN_SHADOW_VALUE_PACKET_V1",
            "usable_shadow_value": True,
        },
        tree_signal_packet={
            "version": "TREE_SIGNAL_PACKET_V1",
            "trees_formal_computation": True,
            "usable_for_gencoin_shadow": True,
        },
        memory_promotion_guard_packet={
            "version": "MEMORY_PROMOTION_GUARD_V1",
            "guard_status": "PROMOTION_CANDIDATE_HUMAN_REVIEW_ONLY",
            "eligible_for_human_review": True,
            "readiness_score": 0.74,
            "write_allowed": False,
            "graphiti_write_allowed": False,
            "neo4j_write_allowed": False,
            "canon_promotion_allowed": False,
            "memory_promotion_allowed": False,
        },
    )


def test_operator_view_packet_exists():
    p = _packet()
    assert p["version"] == "OPERATOR_VIEW_PACKET_V1"


def test_boundary_invariants():
    p = _packet(**_ready_inputs())
    assert p["decision_authority"] == "KX108_ONLY"
    assert p["readonly"] is True
    assert p["advisory_only"] is True
    assert p["context_signal_only"] is True
    assert p["emits_act"] is False
    assert p["emits_verdict"] is False
    assert p["memory_write"] is False
    assert p["graphiti_write"] is False
    assert p["neo4j_write"] is False
    assert p["canon_promotion"] is False
    assert p["memory_promotion"] is False
    assert p["kernel_mutation"] is False
    assert p["x108_mutation"] is False


def test_ready_stack_status():
    p = _packet(**_ready_inputs())
    assert p["system_status"] == "OPERATOR_READY_READONLY"
    assert p["next_safe_action"] == "DISPLAY_TRANSVERSE_STACK"
    assert p["summary"]["all_core_packets_ready"] is True
    assert p["summary"]["safe_boundary_ok"] is True


def test_missing_packets_make_partial_readonly():
    p = _packet()
    assert p["system_status"] == "PARTIAL_READONLY"
    assert "sigma_packet" in p["blocked"]["missing_packets"]
    assert p["summary"]["operator_can_write"] is False
    assert p["summary"]["operator_can_decide"] is False


def test_high_mismatch_attention_required():
    data = _ready_inputs()
    data["anti_mismatch_packet"]["risk_level"] = "HIGH"
    p = _packet(**data)
    assert p["system_status"] == "ATTENTION_REQUIRED"
    assert "ANTI_MISMATCH_HIGH" in p["blocked"]["hard_risks"]


def test_unstable_thermo_attention_required():
    data = _ready_inputs()
    data["thermodynamics_packet"]["stability_state"] = "UNSTABLE"
    p = _packet(**data)
    assert p["system_status"] == "ATTENTION_REQUIRED"
    assert "THERMO_UNSTABLE" in p["blocked"]["hard_risks"]


def test_memory_guard_blocked_attention_required():
    data = _ready_inputs()
    data["memory_promotion_guard_packet"]["guard_status"] = "PROMOTION_BLOCKED_RISK"
    p = _packet(**data)
    assert p["system_status"] == "ATTENTION_REQUIRED"
    assert "MEMORY_PROMOTION_BLOCKED_RISK" in p["blocked"]["hard_risks"]


def test_value_layer_scores_must_stay_null():
    data = _ready_inputs()
    data["value_layer"]["scores"]["cognitive_value"] = 0.5
    p = _packet(**data)
    assert p["system_status"] == "ATTENTION_REQUIRED"
    assert "VALUE_LAYER_SCORES_NOT_NULL" in p["blocked"]["hard_risks"]


def test_final_scoring_unexpected_attention_required():
    data = _ready_inputs()
    data["value_layer"]["final_scoring_enabled"] = True
    p = _packet(**data)
    assert p["system_status"] == "ATTENTION_REQUIRED"
    assert "FINAL_SCORING_ENABLED_UNEXPECTED" in p["blocked"]["hard_risks"]


def test_write_permission_unexpected_attention_required():
    data = _ready_inputs()
    data["memory_promotion_guard_packet"]["write_allowed"] = True
    p = _packet(**data)
    assert p["system_status"] == "ATTENTION_REQUIRED"
    assert "WRITE_PERMISSION_UNEXPECTED" in p["blocked"]["hard_risks"]


def test_evidence_surface_contains_core_fields():
    p = _packet(**_ready_inputs())
    assert p["evidence"]["sigma_truth_score"] == 0.82
    assert p["evidence"]["mismatch_score"] == 0.10
    assert p["evidence"]["stability_state"] == "STABLE"
    assert p["evidence"]["tree_formal_computation"] is True
    assert p["evidence"]["memory_guard_status"] == "PROMOTION_CANDIDATE_HUMAN_REVIEW_ONLY"


def test_operator_view_never_grants_action():
    p = _packet(**_ready_inputs())
    assert p["summary"]["operator_can_view"] is True
    assert p["summary"]["operator_can_write"] is False
    assert p["summary"]["operator_can_decide"] is False
    assert p["emits_act"] is False
    assert p["emits_verdict"] is False
