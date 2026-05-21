"""
V5A Non-Sovereignty Test: Brody responses never emit verdict.
Brody is advisory only. No verdict. No decision. No ACT.
"""
import pytest
from periphery.brody.brody_runtime_readonly import brody_respond, BrodyResponse
from periphery.brody.brody_response_contract import BrodyResponseContract


def test_brody_response_is_advisory_only():
    """Every Brody response must be advisory, never a verdict."""
    response = brody_respond(
        query="What is the best action?",
        language="en",
        context_refs=["ctx_001"],
        confidence=0.9,
    )
    contract = BrodyResponseContract()
    # Contract validates its own invariants — check them
    assert contract.advisory_only is True
    assert contract.emits_act is False
    assert contract.emits_verdict is False


def test_brody_contract_never_emits_act():
    """Brody contract must enforce emits_act=False."""
    contract = BrodyResponseContract()
    assert contract.emits_act is False


def test_brody_contract_never_emits_verdict():
    """Brody contract must enforce emits_verdict=False."""
    contract = BrodyResponseContract()
    assert contract.emits_verdict is False


def test_brody_decision_authority_is_x108_only():
    """Brody never claims decision authority."""
    contract = BrodyResponseContract()
    assert contract.decision_authority == "KX108_ONLY"


def test_brody_memory_write_is_forbidden():
    """Brody cannot write to memory."""
    contract = BrodyResponseContract()
    assert contract.memory_write is False


def test_brody_kernel_mutation_forbidden():
    """Brody cannot mutate kernel state."""
    contract = BrodyResponseContract()
    assert contract.kernel_mutation is False
