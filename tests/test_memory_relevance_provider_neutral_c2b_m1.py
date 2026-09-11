"""
C2B-M1 ? memory relevance must be provider-neutral.

Memory activation/relevance is cognitive.
Graphiti availability/admission is a retrieval-provider concern.

DECISION_AUTHORITY = KX108_ONLY.
"""

from apps.obsidia_api.brody_memory_trace_extractor import (
    _compute_memory_relevance_score,
)


def _micro_core():
    return {
        "path_coherence_score": 0.5,
    }


def _balance():
    return {
        "balances": {
            "balance_memoire": {
                "tension": 0.5,
            },
        },
    }


def _point_cloud(
    *,
    graphiti_allowed: bool,
    memory_packet_required: bool,
):
    return {
        "axes": {
            "axis_13_memory": 0.5,
        },
        "graphiti_allowed": graphiti_allowed,
        "memory_packet_required": memory_packet_required,
    }


def test_graphiti_toggle_does_not_change_memory_relevance():
    score_graphiti_off = _compute_memory_relevance_score(
        _micro_core(),
        _balance(),
        _point_cloud(
            graphiti_allowed=False,
            memory_packet_required=True,
        ),
    )

    score_graphiti_on = _compute_memory_relevance_score(
        _micro_core(),
        _balance(),
        _point_cloud(
            graphiti_allowed=True,
            memory_packet_required=True,
        ),
    )

    assert score_graphiti_off == score_graphiti_on


def test_memory_packet_required_changes_memory_relevance():
    score_not_required = _compute_memory_relevance_score(
        _micro_core(),
        _balance(),
        _point_cloud(
            graphiti_allowed=False,
            memory_packet_required=False,
        ),
    )

    score_required = _compute_memory_relevance_score(
        _micro_core(),
        _balance(),
        _point_cloud(
            graphiti_allowed=False,
            memory_packet_required=True,
        ),
    )

    assert score_required > score_not_required
    assert round(score_required - score_not_required, 4) == 0.2


def test_memory_relevance_stays_bounded():
    score = _compute_memory_relevance_score(
        {"path_coherence_score": 1.0},
        {"balances": {"balance_memoire": {"tension": 1.0}}},
        {
            "axes": {"axis_13_memory": 1.0},
            "graphiti_allowed": True,
            "memory_packet_required": True,
        },
    )

    assert 0.0 <= score <= 1.0
    assert score == 1.0
