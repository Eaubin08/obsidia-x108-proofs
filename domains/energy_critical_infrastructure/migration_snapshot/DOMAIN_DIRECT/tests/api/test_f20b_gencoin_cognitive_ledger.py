from apps.obsidia_api.brody_gencoin_cognitive_ledger import (
    build_gencoin_cognitive_ledger_packet,
)


GENCOIN = {
    "version": "GENCOIN_SHADOW_VALUE_PACKET_V1",
    "mode": "SHADOW_READONLY",
    "usable_shadow_value": True,
    "final_scoring_enabled": False,
    "economic_scoring_enabled": False,
    "blockchain_enabled": False,
    "memory_promotion_enabled": False,
    "shadow_scores": {
        "cognitive_value": 0.94,
        "proof_value": 0.89,
        "reuse_value": 0.832,
        "memory_value": 0.795,
        "attention_cost": 0.2,
        "energy_cost": 0.108,
        "stability_value": 0.95,
        "economic_projection": None,
    },
}

THERMO_UNIFIED = {
    "version": "THERMO_COHERENCE_TIME_UNIFIED_PACKET_V1",
    "status": "THERMO_COHERENCE_TIME_UNIFIED_READONLY_PASS",
    "usable_for_gencoin": True,
    "usable_for_value_layer": True,
    "composite_temperature": 0.1326,
}

VALUE_LAYER_NULL = {
    "scores": {
        "cognitive_value": None,
        "proof_value": None,
        "reuse_value": None,
        "memory_value": None,
        "attention_cost": None,
        "energy_cost": None,
        "stability_value": None,
        "economic_projection": None,
    }
}

LEDGER_EMPTY = {
    "status": "LIVE_EMPTY_REGISTRY",
    "source": "LIVE_EMPTY_REGISTRY",
    "total": 0,
    "reason": "NO_REAL_GENCOIN_LEDGER_ENTRY_YET",
}


def test_gencoin_cognitive_ledger_projects_real_shadow_scores():
    p = build_gencoin_cognitive_ledger_packet(
        gencoin_shadow_packet=GENCOIN,
        thermo_unified_packet=THERMO_UNIFIED,
        value_layer=VALUE_LAYER_NULL,
        ledger_status=LEDGER_EMPTY,
        session_id="f20b_test",
        source="REAL_BACKEND",
    )

    assert p["version"] == "GENCOIN_COGNITIVE_LEDGER_PACKET_V1"
    assert p["status"] == "GENCOIN_COGNITIVE_LEDGER_READONLY_PASS"
    assert p["source"] == "BRODY_F20B_GENCOIN_COGNITIVE_LEDGER"
    assert p["mode"] == "READONLY_PROJECTED_LEDGER"

    assert p["ledger_status"] == "LIVE_EMPTY_REGISTRY"
    assert p["ledger_total"] == 0
    assert p["entry_count"] == 1
    assert p["projected_only"] is True
    assert p["persisted"] is False

    e = p["entries"][0]
    assert e["ledger_id"].startswith("COGLEDGER_")
    assert e["usable_shadow_value"] is True
    assert e["thermo_unified_usable_for_gencoin"] is True
    assert e["ledger_projection"]["projected_entry_only"] is True
    assert e["ledger_projection"]["persisted"] is False
    assert e["ledger_projection"]["minted"] is False
    assert e["ledger_projection"]["wallet_touched"] is False
    assert e["ledger_projection"]["blockchain_touched"] is False

    assert e["shadow_scores"]["cognitive_value"] == 0.94
    assert e["shadow_scores"]["proof_value"] == 0.89
    assert e["shadow_scores"]["reuse_value"] == 0.832
    assert e["shadow_scores"]["economic_projection"] is None
    assert isinstance(e["cognitive_ledger_score"], float)
    assert e["cognitive_ledger_score"] > 0.0


def test_gencoin_cognitive_ledger_boundaries_are_strict():
    p = build_gencoin_cognitive_ledger_packet(
        gencoin_shadow_packet=GENCOIN,
        thermo_unified_packet=THERMO_UNIFIED,
        value_layer=VALUE_LAYER_NULL,
        ledger_status=LEDGER_EMPTY,
    )

    assert p["decision_authority"] == "KX108_ONLY"
    assert p["readonly"] is True
    assert p["advisory_only"] is True
    assert p["allowed_to_decide"] is False
    assert p["allowed_to_act"] is False
    assert p["emits_act"] is False
    assert p["emits_verdict"] is False
    assert p["memory_write"] is False
    assert p["graphiti_write"] is False
    assert p["kernel_mutation"] is False
    assert p["x108_mutation"] is False
    assert p["final_scoring_enabled"] is False
    assert p["economic_scoring_enabled"] is False
    assert p["blockchain_enabled"] is False
    assert p["mint_allowed"] is False
    assert p["wallet_enabled"] is False
    assert p["is_real_token"] is False

    e = p["entries"][0]
    assert e["decision_authority"] == "KX108_ONLY"
    assert e["readonly"] is True
    assert e["emits_act"] is False
    assert e["memory_write"] is False
    assert e["blockchain_enabled"] is False
    assert e["mint_allowed"] is False
    assert e["wallet_enabled"] is False
    assert e["is_real_token"] is False


def test_gencoin_cognitive_ledger_no_entry_when_shadow_unusable():
    bad = dict(GENCOIN)
    bad["usable_shadow_value"] = False

    p = build_gencoin_cognitive_ledger_packet(
        gencoin_shadow_packet=bad,
        thermo_unified_packet=THERMO_UNIFIED,
        value_layer=VALUE_LAYER_NULL,
        ledger_status=LEDGER_EMPTY,
    )

    assert p["status"] == "GENCOIN_COGNITIVE_LEDGER_READONLY_PASS"
    assert p["entry_count"] == 0
    assert p["entries"] == []
    assert p["projected_only"] is True
    assert p["persisted"] is False
    assert p["mint_allowed"] is False
    assert p["is_real_token"] is False


def test_brody_route_exposes_gencoin_cognitive_ledger_packet():
    from pathlib import Path

    src = Path("apps/obsidia_api/routes/brody.py").read_text(encoding="utf-8")

    assert "build_gencoin_cognitive_ledger_packet" in src
    assert "_gencoin_cognitive_ledger_packet = safe_call_snapshot(" in src
    assert '"gencoin_cognitive_ledger_packet": _gencoin_cognitive_ledger_packet,' in src
    assert '"gencoin_shadow_packet": _gencoin_shadow_packet,' in src
