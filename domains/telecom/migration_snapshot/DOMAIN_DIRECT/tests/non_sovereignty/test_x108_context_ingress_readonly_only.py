"""
V5A Non-Sovereignty Test: X108 context ingress is strictly read-only.
Validates context packets but never decides, never writes, never emits ACT.
"""
import pytest
from periphery.x108_ingress.x108_context_boundary import check_x108_context_boundary
from periphery.context.context_packet_builder_v2 import build_context_packet_v2


def test_x108_ingress_accepts_valid_packet():
    """Valid context packets must pass the boundary check."""
    packet = build_context_packet_v2(query="Test context")
    result = check_x108_context_boundary(packet.to_dict())
    assert result.passed is True
    assert result.violations == []


def test_x108_ingress_readonly():
    """X108 ingress must be readonly."""
    packet = build_context_packet_v2(query="Readonly test")
    result = check_x108_context_boundary(packet.to_dict())
    assert result.readonly is True
    assert result.decision_authority == "KX108_ONLY"


def test_x108_ingress_rejects_packet_with_authority():
    """Packets claiming decision authority must be rejected."""
    bad_packet = {
        "packet_id": "bad_001",
        "decision_authority": "PERIPHERY_AGENT",
        "allowed_to_decide": True,
    }
    result = check_x108_context_boundary(bad_packet)
    assert result.passed is False
    assert len(result.violations) > 0
    assert "decision_authority" in str(result.violations)


def test_x108_ingress_rejects_packet_allowing_decide():
    """Packets with allowed_to_decide=True must be rejected."""
    bad_packet = {
        "packet_id": "bad_002",
        "decision_authority": "KX108_ONLY",
        "allowed_to_decide": True,
    }
    result = check_x108_context_boundary(bad_packet)
    assert result.passed is False
    assert len(result.violations) > 0


def test_x108_ingress_accepts_multiple_valid_packets():
    """Multiple valid packets must all pass the boundary check."""
    for i in range(3):
        packet = build_context_packet_v2(query=f"Packet {i}")
        result = check_x108_context_boundary(packet.to_dict())
        assert result.passed is True, f"Packet {i} must pass"
