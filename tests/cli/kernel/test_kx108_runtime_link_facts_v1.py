"""
The runtime link facts must describe the repository as it actually is.

Presence is read from the filesystem, never claimed by a caller, and no
detected link is ever allowed to raise a validation flag on its own.
"""

from pathlib import Path

from scripts.kernel.kx108_runtime_link_facts_v1 import (
    AGENT_PRE_EXECUTION_CONTEXT_PATH,
    FEEDBACK_CONTEXT_ADAPTER_PATH,
    CANONICAL_DOMAIN_GATE_REACHABILITY,
    GOVERNED_RUNTIME_CYCLE_PATH,
    INTERNAL_E2E_REQUIRED_LINKS,
    REQUIRED_GLOBAL_RUNTIME_LINKS,
    MISSING_RUNTIME_LINK_ADAPTER,
    MISSING_RUNTIME_LINK_AGENT_DECISION_RECORD,
    MISSING_RUNTIME_LINK_WORLD_ACTUATION,
    agent_decision_record_rail_present,
    canonical_agent_context_adapter_present,
    governed_runtime_cycle_present,
    multi_domain_runtime_present,
    runtime_internal_end_to_end_validated,
    runtime_internal_globally_validated,
    missing_runtime_links,
    runtime_link_facts,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]


def test_detected_links_match_the_files_on_disk():
    assert canonical_agent_context_adapter_present() is (
        (_REPO_ROOT / "periphery/context/agent_result_context_adapter.py").is_file()
        and (_REPO_ROOT / "periphery/context/agent_x108_context_flow.py").is_file()
    )
    assert governed_runtime_cycle_present() is (
        (_REPO_ROOT / GOVERNED_RUNTIME_CYCLE_PATH).is_file()
    )


def test_present_adapter_is_no_longer_reported_as_missing():
    assert canonical_agent_context_adapter_present() is True
    assert MISSING_RUNTIME_LINK_ADAPTER not in missing_runtime_links()


def test_agent_decision_record_rail_is_detected_on_disk():
    assert (_REPO_ROOT / AGENT_PRE_EXECUTION_CONTEXT_PATH).is_file()
    assert (_REPO_ROOT / FEEDBACK_CONTEXT_ADAPTER_PATH).is_file()
    assert agent_decision_record_rail_present() is True

    assert MISSING_RUNTIME_LINK_AGENT_DECISION_RECORD not in missing_runtime_links()


def test_world_actuation_stays_missing():
    """It is never fabricated, so it is always reported as missing."""
    assert MISSING_RUNTIME_LINK_WORLD_ACTUATION in missing_runtime_links()


def test_internal_e2e_is_validated_while_the_wider_flag_stays_false():
    """An internal governed runtime is not a globally validated runtime."""
    facts = runtime_link_facts()

    assert runtime_internal_end_to_end_validated() is True
    assert facts["runtime_internal_end_to_end_validated"] is True
    assert len(INTERNAL_E2E_REQUIRED_LINKS) == 14

    assert facts["runtime_end_to_end_validated"] is False
    assert facts["runtime_globally_validated"] is False
    assert facts["world_action_runtime_activated"] is False


def test_governed_cycle_presence_raises_no_wider_flag():
    facts = runtime_link_facts()

    assert facts["governed_runtime_cycle_present"] is True

    assert facts["runtime_end_to_end_validated"] is False
    assert facts["runtime_globally_validated"] is False
    assert facts["runtime_allowed_now"] is False
    assert facts["world_action_runtime_activated"] is False


def test_facts_never_carry_authority():
    facts = runtime_link_facts()

    assert facts["decision_authority"] == "KX108_ONLY"
    assert facts["execution_authority"] is False
    assert facts["memory_write"] is False
    assert facts["kernel_mutation"] is False
    assert facts["emits_act"] is False


def test_multi_domain_runtime_is_detected_with_real_bridges():
    assert multi_domain_runtime_present() is True
    assert runtime_link_facts()["multi_domain_runtime_present"] is True


def test_domain_gate_reachability_is_recorded_honestly():
    """Only bank can BLOCK; ecom can only HOLD. Recorded, not engineered."""
    assert CANONICAL_DOMAIN_GATE_REACHABILITY["bank"] == ("ALLOW", "HOLD", "BLOCK")
    assert CANONICAL_DOMAIN_GATE_REACHABILITY["gps_defense_aviation"] == ("ALLOW", "HOLD")
    assert CANONICAL_DOMAIN_GATE_REACHABILITY["trading"] == ("ALLOW", "HOLD")
    assert CANONICAL_DOMAIN_GATE_REACHABILITY["ecom"] == ("HOLD",)


def test_internal_global_validation_does_not_raise_the_historical_flags():
    facts = runtime_link_facts()

    assert runtime_internal_globally_validated() is True
    assert facts["runtime_internal_globally_validated"] is True
    assert len(REQUIRED_GLOBAL_RUNTIME_LINKS) == 12

    # An internal global runtime is not a globally validated runtime, and is
    # certainly not an actuated world.
    assert facts["runtime_globally_validated"] is False
    assert facts["runtime_end_to_end_validated"] is False
    assert facts["world_action_runtime_activated"] is False
    assert facts["runtime_allowed_now"] is False
