from apps.obsidia_api.brody_temporal_context_adapter import build_temporal_context_snapshot


def test_temporal_context_explicit_x108_mutation_false():
    snap = build_temporal_context_snapshot()

    assert snap["status"] == "TEMPORAL_CONTEXT_MINIMAL"
    assert snap["layers_available"] == 1
    assert snap["readonly"] is True
    assert snap["decision_authority"] == "KX108_ONLY"
    assert snap["memory_write"] is False
    assert snap["graphiti_write"] is False
    assert snap["neo4j_write"] is False
    assert snap["kernel_mutation"] is False
    assert snap["x108_mutation"] is False
    assert snap["emits_act"] is False
    assert snap["emits_verdict"] is False

    control = snap["control_proof_context"]
    assert control["readonly"] is True
    assert control["decision_authority"] == "KX108_ONLY"
    assert control["memory_write"] is False
    assert control["graphiti_write"] is False
    assert control["neo4j_write"] is False
    assert control["kernel_mutation"] is False
    assert control["x108_mutation"] is False
    assert control["emits_act"] is False
    assert control["emits_verdict"] is False


def test_temporal_context_present_layer_is_bool_safe():
    snap = build_temporal_context_snapshot(memory_chain={"status": "READY", "query_results_count": 2})
    assert snap["layers_available"] >= 2
    assert snap["status"] in {"TEMPORAL_CONTEXT_PARTIAL", "TEMPORAL_CONTEXT_FULL"}
    assert snap["x108_mutation"] is False
