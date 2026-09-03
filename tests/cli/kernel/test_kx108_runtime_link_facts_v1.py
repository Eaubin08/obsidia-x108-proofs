"""
The runtime link facts must describe the repository as it actually is.

Presence is read from the filesystem, never claimed by a caller, and no
detected link is ever allowed to raise a validation flag on its own.
"""

from pathlib import Path

from scripts.kernel.kx108_runtime_link_facts_v1 import (
    GOVERNED_RUNTIME_CYCLE_PATH,
    MISSING_RUNTIME_LINK_ADAPTER,
    MISSING_RUNTIME_LINK_AGENT_DECISION_RECORD,
    MISSING_RUNTIME_LINK_WORLD_ACTUATION,
    canonical_agent_context_adapter_present,
    governed_runtime_cycle_present,
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


def test_agent_decision_record_and_world_actuation_stay_missing():
    """Neither is fabricated, so both are always reported as missing."""
    links = missing_runtime_links()

    assert MISSING_RUNTIME_LINK_AGENT_DECISION_RECORD in links
    assert MISSING_RUNTIME_LINK_WORLD_ACTUATION in links


def test_governed_cycle_presence_raises_no_flag():
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
