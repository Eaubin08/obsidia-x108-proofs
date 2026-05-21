"""
V5A Non-Sovereignty Test: Context packets never claim authority.
Context is signal only — never decides, never acts.
"""
import pytest
from periphery.context.context_packet_builder_v2 import build_context_packet_v2


def test_context_packet_has_no_decision_authority():
    """Context packets must declare decision_authority=KX108_ONLY."""
    packet = build_context_packet_v2(
        query="Test context only",
        context_items=["item1", "item2"],
    )
    assert packet.decision_authority == "KX108_ONLY"
    assert packet.allowed_to_decide is False
    assert packet.allowed_to_act is False


def test_context_packet_is_readonly():
    """Context packets must be readonly."""
    packet = build_context_packet_v2(query="Test")
    assert packet.readonly is True


def test_context_packet_is_signal_only():
    """Context packets are signal, never authority."""
    packet = build_context_packet_v2(query="Signal test")
    assert packet.context_signal_only is True


def test_context_packet_cannot_decide():
    """No context packet can allow decisions."""
    packet = build_context_packet_v2(query="No decision test")
    assert packet.allowed_to_decide is False


def test_context_packet_cannot_act():
    """No context packet can allow actions."""
    packet = build_context_packet_v2(query="No act test")
    assert packet.allowed_to_act is False


def test_context_packet_forbidden_tokens_detected():
    """Forbidden sovereign tokens (ALLOW, BLOCK, ACT) must be detected."""
    packet = build_context_packet_v2(
        query="Test with token",
        context_items=["This item says ALLOW", "Another says BLOCK"],
    )
    assert "ALLOW" in packet.forbidden_tokens_detected or "BLOCK" in packet.forbidden_tokens_detected


def test_context_packet_memory_write_blocked():
    """Context packets must have memory_write=False."""
    packet = build_context_packet_v2(query="Memory test")
    assert packet.memory_write is False
