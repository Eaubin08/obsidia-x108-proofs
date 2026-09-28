from __future__ import annotations

from openjarvis.server.routes import (
    _server_agent_model_allowlist,
)


class GovernedAgent:
    server_model_allowlist = (
        "obsidia-governed",
    )


class OrdinaryAgent:
    pass


def test_governed_agent_exposes_only_synthetic_model():
    assert (
        _server_agent_model_allowlist(
            GovernedAgent()
        )
        == (
            "obsidia-governed",
        )
    )


def test_normal_agent_keeps_default_model_discovery():
    assert (
        _server_agent_model_allowlist(
            OrdinaryAgent()
        )
        == ()
    )


def test_model_allowlist_is_deduplicated_and_cleaned():
    class Agent:
        server_model_allowlist = (
            " obsidia-governed ",
            "obsidia-governed",
            "",
        )

    assert (
        _server_agent_model_allowlist(
            Agent()
        )
        == (
            "obsidia-governed",
        )
    )
