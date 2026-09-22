from apps.obsidia_api.brody_pre_reasoning_adapter import (
    build_brody_pre_reasoning_snapshot,
)


def test_brody_pre_reasoning_adapter_unknown():
    result = build_brody_pre_reasoning_snapshot(
        user_message="explique le florvaxium",
        language="fr",
        intent="pure_response",
        authority_snapshot={
            "request_type": "PURE_RESPONSE",
        },
    )

    assert result["status"] == "BRODY_PRE_REASONING_PASS"

    assert result["semantic_query_snapshot"]
    assert result["reverse_os_projection"]

    calibration = result["pre_reasoning_calibration"]

    assert calibration["stage_order"] == [
        "C265",
        "C266",
        "C273",
        "C274",
    ]

    assert calibration["unknowns"] == [
        "florvaxium",
    ]

    assert calibration["symbolic_alignment"] == "PARTIAL"

    assert calibration["reasoning_readiness"] == (
        "CALIBRATED_WITH_UNCERTAINTY"
    )

    assert result["readonly"] is True
    assert result["decision_authority"] == "KX108_ONLY"

    assert result["allowed_to_decide"] is False
    assert result["allowed_to_act"] is False
    assert result["emits_act"] is False
    assert result["emits_verdict"] is False

    assert result["memory_write"] is False
    assert result["canonical_write"] is False
    assert result["kernel_mutation"] is False
    assert result["x108_mutation"] is False


def test_brody_pre_reasoning_adapter_known_x108():
    result = build_brody_pre_reasoning_snapshot(
        user_message="explique x108",
        language="fr",
        intent="pure_response",
        authority_snapshot={
            "request_type": "PURE_RESPONSE",
        },
    )

    calibration = result["pre_reasoning_calibration"]

    assert calibration["unknowns"] == []
    assert "x108" in calibration["known_concept_ids"]

    assert calibration["symbolic_alignment"] == "ALIGNED"
    assert calibration["divergences"] == []
    assert calibration["reasoning_readiness"] == "CALIBRATED"


def test_brody_pre_reasoning_adapter_has_no_memory_provider_dependency():
    import inspect
    import apps.obsidia_api.brody_pre_reasoning_adapter as mod

    source = inspect.getsource(mod).lower()

    forbidden = (
        "brody_obsidia_native_memory",
        "brody_native_memory_response_adapter",
        "brody_memory_response_chain_adapter",
        "graphiti_v20_readonly_client",
        "neo4j_brody_guide_bridge",
        "hydrate_packet",
        "query_neo4j",
        "bolt://",
        "localhost:7688",
        "localhost:8011",
    )

    for token in forbidden:
        assert token not in source
