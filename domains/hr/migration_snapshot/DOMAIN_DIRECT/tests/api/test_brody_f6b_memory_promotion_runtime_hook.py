from pathlib import Path

from apps.obsidia_api.brody_memory_promotion_guard import build_memory_promotion_guard_packet


def test_f6b_routes_imports_memory_guard():
    src = Path("apps/obsidia_api/routes/brody.py").read_text(encoding="utf-8")
    assert "build_memory_promotion_guard_packet" in src
    assert "from apps.obsidia_api.brody_memory_promotion_guard import build_memory_promotion_guard_packet" in src


def test_f6b_routes_builds_memory_guard_packet():
    src = Path("apps/obsidia_api/routes/brody.py").read_text(encoding="utf-8")
    assert "_memory_guard_raw = safe_call_snapshot(" in src
    assert '"memory_promotion_guard_packet"' in src
    assert "_memory_promotion_guard_packet" in src
    assert "sigma_packet=_sigma_packet" in src
    assert "anti_mismatch_packet=_anti_mismatch_packet" in src
    assert "thermodynamics_packet=_thermodynamics_packet" in src
    assert "gencoin_shadow_packet=_gencoin_shadow_packet" in src
    assert "tree_signal_packet=_tree_signal_packet" in src


def test_f6b_routes_exposes_memory_guard_payload():
    src = Path("apps/obsidia_api/routes/brody.py").read_text(encoding="utf-8")
    assert '"memory_promotion_guard_packet": _memory_promotion_guard_packet' in src


def test_memory_guard_runtime_packet_never_writes():
    packet = build_memory_promotion_guard_packet(
        request_text="ecris en memoire et canonise ce bloc",
        sigma_packet={"truth_score": 0.9, "usable_for_gencoin": True},
        anti_mismatch_packet={"mismatch_score": 0.1, "risk_level": "LOW"},
        thermodynamics_packet={"stability_state": "STABLE", "usable_for_gencoin": True},
        gencoin_shadow_packet={
            "usable_shadow_value": True,
            "shadow_scores": {
                "cognitive_value": 0.9,
                "proof_value": 0.9,
                "memory_value": 0.9,
                "stability_value": 0.9,
            },
        },
        tree_signal_packet={
            "trees_formal_computation": True,
            "can_decide": False,
            "can_emit_act": False,
        },
    )["memory_promotion_guard_packet"]

    assert packet["guard_status"] == "PROMOTION_BLOCKED_RISK"
    assert packet["write_allowed"] is False
    assert packet["graphiti_write_allowed"] is False
    assert packet["neo4j_write_allowed"] is False
    assert packet["canon_promotion_allowed"] is False
    assert packet["memory_promotion_allowed"] is False
    assert packet["memory_write"] is False
    assert packet["kernel_mutation"] is False
    assert packet["x108_mutation"] is False


def test_memory_guard_human_review_is_not_permission():
    packet = build_memory_promotion_guard_packet(
        request_text="analyse sans ecriture memoire",
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
            "trees_formal_computation": True,
            "can_decide": False,
            "can_emit_act": False,
        },
    )["memory_promotion_guard_packet"]

    assert packet["eligible_for_human_review"] is True
    assert packet["guard_status"] == "PROMOTION_CANDIDATE_HUMAN_REVIEW_ONLY"
    assert packet["promotion_enabled"] is False
    assert packet["write_allowed"] is False
    assert packet["memory_promotion_allowed"] is False
