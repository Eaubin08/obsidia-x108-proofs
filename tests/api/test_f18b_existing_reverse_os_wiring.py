from apps.obsidia_api.brody_existing_reverse_os_bridge import (
    build_existing_reverse_flow,
    build_existing_ir_candidate,
    build_existing_reverse_os_projection,
)


MSG = "write Graphiti memory + canon -> DOMAIN_RACCORD_WRITE_BOUNDARY"


def test_existing_reverse_flow_is_non_decision_kx108_only():
    flow = build_existing_reverse_flow(
        user_message=MSG,
        intent="action_request",
        semantic_query_snapshot={"topic": "MEMORY", "semantic_query": "Graphiti memory canon"},
        authority_snapshot={"request_type": "ACTION_REQUEST"},
    )

    assert flow["agent_name"] == "BRODY_REVERSE_OS_SSR_REAL_BRIDGE"
    assert flow["reason_code"] == "RC_X108_REQUIRED"
    assert flow["verdict"] == "NO_DECISION_X108_REQUIRED"
    assert flow["non_decision"] is True
    assert flow["decision_authority"] == "KX108_ONLY"
    assert isinstance(flow["tree_vector"], dict)
    assert len(flow["tree_vector"]) == 34


def test_existing_ir_candidate_has_real_entities_constraints_and_boundary():
    flow = build_existing_reverse_flow(
        user_message=MSG,
        intent="action_request",
        semantic_query_snapshot={"topic": "MEMORY"},
        authority_snapshot={"request_type": "ACTION_REQUEST"},
    )

    ir = build_existing_ir_candidate(
        user_message=MSG,
        intent="action_request",
        semantic_query_snapshot={"topic": "MEMORY"},
        authority_snapshot={"request_type": "ACTION_REQUEST"},
        reverse_flow=flow,
    )

    assert ir["status"] == "IR_CANDIDATE_EXISTING_REVERSE_OS_BRIDGE_PASS"
    assert ir["source"] == "BRODY_EXISTING_REVERSE_OS_IR_BRIDGE_V1"
    assert ir["ir_kind"] == "OBSIDIA_IR_CANDIDATE_READONLY"
    assert ir["entities"]
    assert ir["constraints"]
    assert any(e["entity"] == "GRAPHITI" for e in ir["entities"])
    assert any(e["entity"] == "CANON" for e in ir["entities"])
    assert any(c["constraint"] == "Decision = KX108" for c in ir["constraints"])
    assert ir["non_decision"] is True
    assert ir["executable"] is False
    assert ir["allowed_to_decide"] is False
    assert ir["allowed_to_act"] is False
    assert ir["emits_act"] is False
    assert ir["emits_verdict"] is False
    assert ir["memory_write"] is False
    assert "graphiti_write" not in ir
    assert ir["kernel_mutation"] is False
    assert ir["x108_mutation"] is False
    assert ir["decision_authority"] == "KX108_ONLY"


def test_existing_reverse_os_projection_reuses_repo_reverse_os():
    out = build_existing_reverse_os_projection(
        user_message=MSG,
        intent="action_request",
        semantic_query_snapshot={"topic": "MEMORY", "semantic_query": "Graphiti memory canon"},
        authority_snapshot={"request_type": "ACTION_REQUEST"},
    )

    assert out["status"] == "EXISTING_REVERSE_OS_READONLY_BRIDGE_PASS"
    assert out["source"] == "BRODY_EXISTING_REVERSE_OS_BRIDGE_V1"
    assert out["projection"]["non_decision"] is True
    assert out["projection"]["verdict_existant"] == "NO_DECISION_X108_REQUIRED"

    tr = out["translation_trace"]
    ir = out["ir_candidate"]

    assert tr["source"] == "BRODY_EXISTING_REVERSE_OS_BRIDGE_V1"
    assert tr["os_trad_status"] == "READONLY_PASS"
    assert tr["alphabet_units_count"] > 0
    assert len(tr["alphabet_units"]) > 0
    assert tr["os_reverse_projection"]["non_decision"] is True

    assert ir["status"] == "IR_CANDIDATE_EXISTING_REVERSE_OS_BRIDGE_PASS"
    assert len(ir["entities"]) > 0
    assert len(ir["constraints"]) > 0

    assert out["readonly"] is True
    assert out["emits_act"] is False
    assert out["emits_verdict"] is False
    assert out["memory_write"] is False
    assert "graphiti_write" not in out
    assert out["kernel_mutation"] is False
    assert out["x108_mutation"] is False
    assert out["decision_authority"] == "KX108_ONLY"


def test_brody_route_uses_existing_reverse_os_bridge():
    from pathlib import Path

    src = Path("apps/obsidia_api/routes/brody.py").read_text(encoding="utf-8")

    assert "build_existing_reverse_os_projection" in src
    assert "existing_reverse_os_bridge" in src
    assert '"alphabet_units": []' not in src
    assert '"os_reverse_projection": {"readonly": True, "advisory_only": True}' not in src
