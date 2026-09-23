from apps.obsidia_api.brody_memory_promotion_guard import build_memory_promotion_guard_packet


def _pkt(**kwargs):
    return build_memory_promotion_guard_packet(**kwargs)["memory_promotion_guard_packet"]


def _good_inputs():
    return dict(
        request_text="analyse ce contexte sans ecriture memoire",
        sigma_packet={"truth_score": 0.82, "usable_for_gencoin": True},
        anti_mismatch_packet={"mismatch_score": 0.10, "risk_level": "LOW"},
        thermodynamics_packet={"stability_state": "STABLE", "usable_for_gencoin": True},
        gencoin_shadow_packet={
            "usable_shadow_value": True,
            "shadow_scores": {
                "cognitive_value": 0.80,
                "proof_value": 0.70,
                "memory_value": 0.65,
                "stability_value": 0.75,
            },
        },
        tree_signal_packet={
            "version": "TREE_SIGNAL_PACKET_V1",
            "trees_formal_computation": True,
            "can_decide": False,
            "can_emit_act": False,
        },
        memory_chain={"material_quality": "USABLE_MATERIAL"},
    )


def test_guard_packet_exists():
    assert _pkt()["version"] == "MEMORY_PROMOTION_GUARD_V1"


def test_boundary_invariants():
    p = _pkt(**_good_inputs())
    assert p["decision_authority"] == "KX108_ONLY"
    assert p["readonly"] is True
    assert p["advisory_only"] is True
    assert p["emits_act"] is False
    assert p["emits_verdict"] is False
    assert p["memory_write"] is False
    assert p["graphiti_write"] is False
    assert p["neo4j_write"] is False
    assert p["canon_promotion"] is False
    assert p["memory_promotion"] is False
    assert p["kernel_mutation"] is False
    assert p["x108_mutation"] is False


def test_candidate_ready_but_no_write_permission():
    p = _pkt(**_good_inputs())
    assert p["eligible_for_human_review"] is True
    assert p["guard_status"] == "PROMOTION_CANDIDATE_HUMAN_REVIEW_ONLY"
    assert p["promotion_enabled"] is False
    assert p["write_allowed"] is False
    assert p["graphiti_write_allowed"] is False
    assert p["neo4j_write_allowed"] is False
    assert p["canon_promotion_allowed"] is False
    assert p["memory_promotion_allowed"] is False


def test_write_intent_blocks_candidate():
    data = _good_inputs()
    data["request_text"] = "ecris en memoire et canonise ce bloc"
    p = _pkt(**data)
    assert p["eligible_for_human_review"] is False
    assert p["guard_status"] == "PROMOTION_BLOCKED_RISK"
    assert p["risk"]["write_intent_detected"] is True


def test_high_mismatch_blocks_candidate():
    data = _good_inputs()
    data["anti_mismatch_packet"] = {"mismatch_score": 0.80, "risk_level": "HIGH"}
    p = _pkt(**data)
    assert p["eligible_for_human_review"] is False
    assert p["guard_status"] == "PROMOTION_BLOCKED_RISK"


def test_unstable_thermo_blocks_candidate():
    data = _good_inputs()
    data["thermodynamics_packet"] = {"stability_state": "UNSTABLE", "usable_for_gencoin": False}
    p = _pkt(**data)
    assert p["eligible_for_human_review"] is False
    assert p["guard_status"] == "PROMOTION_BLOCKED_RISK"


def test_tree_authority_violation_blocks_candidate():
    data = _good_inputs()
    data["tree_signal_packet"]["can_decide"] = True
    p = _pkt(**data)
    assert p["eligible_for_human_review"] is False
    assert p["guard_status"] == "PROMOTION_BLOCKED_RISK"


def test_missing_inputs_not_eligible():
    p = _pkt()
    assert p["eligible_for_human_review"] is False
    assert p["guard_status"] == "PROMOTION_NOT_ELIGIBLE"


def test_readiness_score_bounded_or_none():
    p = _pkt(**_good_inputs())
    assert p["readiness_score"] is not None
    assert 0.0 <= p["readiness_score"] <= 1.0


def test_human_review_is_not_permission():
    p = _pkt(**_good_inputs())
    assert p["eligible_for_human_review"] is True
    assert p["write_allowed"] is False
    assert p["memory_promotion_allowed"] is False
