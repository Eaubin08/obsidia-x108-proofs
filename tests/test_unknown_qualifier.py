from periphery.language.unknown_qualifier import (
    qualify_unknowns,
)


CURRENT_STATE = {
    "topic": "CURRENT_STATE",
    "semantic_query": "Brody Obsidia etat actuel",
    "primary_query": "brody",
    "fallback_queries": [
        "obsidia",
        "etat",
        "current",
        "status",
    ],
    "is_canonical": True,
    "route": "TOPIC_MATCHED",
}


def test_current_state_false_lexical_unknowns_are_resolved():
    result = qualify_unknowns(
        user_message=(
            "Explique moi le statut actuel de Brody."
        ),
        language="fr",
        lexical_unknowns=[
            "moi",
            "statut",
            "actuel",
            "brody",
        ],
        semantic_query_snapshot=CURRENT_STATE,
    )

    assert result[
        "lexical_unknowns"
    ] == [
        "moi",
        "statut",
        "actuel",
        "brody",
    ]

    assert result[
        "surface_language_unknowns"
    ] == [
        "moi",
    ]

    assert result[
        "semantically_resolved_unknowns"
    ] == [
        "statut",
        "actuel",
        "brody",
    ]

    assert result[
        "unresolved_unknowns"
    ] == []


def test_real_unknown_survives_canonical_semantic_route():
    result = qualify_unknowns(
        user_message=(
            "Explique moi le statut actuel "
            "de Brody et florvaxium."
        ),
        language="fr",
        lexical_unknowns=[
            "moi",
            "statut",
            "actuel",
            "brody",
            "florvaxium",
        ],
        semantic_query_snapshot=CURRENT_STATE,
    )

    assert result[
        "unresolved_unknowns"
    ] == [
        "florvaxium",
    ]

    assert "florvaxium" not in result[
        "semantically_resolved_unknowns"
    ]


def test_fallback_query_does_not_magically_resolve_unknown():
    result = qualify_unknowns(
        user_message="explique le florvaxium",
        language="fr",
        lexical_unknowns=[
            "florvaxium",
        ],
        semantic_query_snapshot={
            "topic": "GENERAL",
            "semantic_query": (
                "explique florvaxium"
            ),
            "primary_query": "explique",
            "fallback_queries": [
                "florvaxium",
            ],
            "is_canonical": False,
            "route": (
                "FALLBACK_WORD_EXTRACTION"
            ),
        },
    )

    # Merely appearing in a fallback extraction
    # is NOT semantic resolution.
    assert result[
        "unresolved_unknowns"
    ] == [
        "florvaxium",
    ]


def test_qualifier_is_non_sovereign_and_provider_free():
    result = qualify_unknowns(
        user_message="florvaxium",
        language="fr",
        lexical_unknowns=[
            "florvaxium",
        ],
        semantic_query_snapshot={},
    )

    assert result["readonly"] is True
    assert result[
        "decision_authority"
    ] == "KX108_ONLY"

    assert result[
        "allowed_to_decide"
    ] is False
    assert result[
        "allowed_to_act"
    ] is False
    assert result["emits_act"] is False
    assert result[
        "emits_verdict"
    ] is False

    assert result[
        "memory_write"
    ] is False
    assert result[
        "canonical_write"
    ] is False
    assert result[
        "kernel_mutation"
    ] is False
    assert result[
        "x108_mutation"
    ] is False

    import inspect
    import periphery.language.unknown_qualifier as mod

    source = inspect.getsource(mod).lower()

    forbidden = (
        "graphiti",
        "neo4j",
        "query_neo4j",
        "hydrate_packet",
        "brody_obsidia_native_memory",
        "brody_native_memory_response_adapter",
    )

    for token in forbidden:
        assert token not in source
