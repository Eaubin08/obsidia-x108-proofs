from __future__ import annotations

import pytest

from apps.obsidia_api.brody_semantic_query_router import (
    build_semantic_query,
    build_memory_retrieval_queries,
)


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        (
            "rappelle historique memoire "
            "session precedente contextpacket",
            "contextpacket",
        ),
        (
            "retrouve contextpacket "
            "dans la memoire precedente",
            "contextpacket",
        ),
        (
            "reprends le contexte precedent "
            "sur contextpacket",
            "contextpacket",
        ),
        (
            "retrouve kernel "
            "dans la memoire precedente",
            "kernel",
        ),
        (
            "rappelle le kernel x108 "
            "de la session precedente",
            "kernel",
        ),
        (
            "retrouve nodecontinuum "
            "dans la memoire precedente",
            "nodecontinuum",
        ),
        (
            "rappelle hexaflux "
            "depuis la memoire precedente",
            "hexaflux",
        ),
        (
            "recall previous stored memory "
            "about contextpacket",
            "contextpacket",
        ),
    ],
)
def test_exact_memory_target_is_preserved(
    message,
    expected,
):
    queries = build_memory_retrieval_queries(
        message
    )

    assert queries
    assert queries[0] == expected


def test_canonical_semantic_query_remains_unchanged():
    message = (
        "retrouve contextpacket "
        "dans la memoire precedente"
    )

    semantic = build_semantic_query(
        message
    )

    # Existing semantic routing remains canonical.
    assert (
        semantic["topic"]
        == "MEMORY_QUERY"
    )

    assert (
        semantic["semantic_query"]
        == "Brody mémoire candidate pipeline"
    )

    # Retrieval specificity is a separate channel.
    retrieval = build_memory_retrieval_queries(
        message
    )

    assert retrieval[0] == "contextpacket"


def test_retrieval_builder_is_not_provider_identity():
    queries = build_memory_retrieval_queries(
        "retrouve contextpacket "
        "dans la memoire precedente"
    )

    blob = " ".join(queries).lower()

    assert "graphiti" not in blob
    assert "neo4j" not in blob
    assert "http" not in blob


def test_generic_recall_without_target_does_not_invent_entity():
    queries = build_memory_retrieval_queries(
        "rappelle historique memoire "
        "session precedente"
    )

    assert queries == []
