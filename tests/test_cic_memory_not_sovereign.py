"""
Tests — Memory is not sovereign
Test 18 : vérifie que la règle memory_not_sovereign est présente partout.
"""
from __future__ import annotations

from apps.obsidia_api.brody_cic_context_adapter import build_brody_cic_packet
from apps.obsidia_api.cic.cic_domain_context import build_domain_cic_context
from apps.obsidia_api.cic.cic_readonly_pack_provider import (
    _CENTRAL_RULES,
    build_cic_readonly_context,
)

_EXPECTED = "Memory is not sovereign."


# Test 18
def test_memory_not_sovereign_in_central_rules():
    assert _EXPECTED in _CENTRAL_RULES


def test_memory_not_sovereign_in_provider_context():
    ctx = build_cic_readonly_context()
    assert any(_EXPECTED in rule for rule in ctx["central_rules"])


def test_memory_not_sovereign_in_brody_packet():
    packet = build_brody_cic_packet()
    ctx = packet["cic_readonly_context"]
    assert ctx["memory_not_sovereign"] == _EXPECTED


def test_memory_not_sovereign_in_brody_central_rules():
    packet = build_brody_cic_packet()
    ctx = packet["cic_readonly_context"]
    assert any(_EXPECTED in rule for rule in ctx["central_rules"])


def test_memory_not_sovereign_in_bank_domain():
    ctx = build_domain_cic_context("bank")
    assert any(_EXPECTED in rule for rule in ctx["central_rules"])
    assert _EXPECTED in ctx["memory_policy"]


def test_memory_not_sovereign_in_trading_domain():
    ctx = build_domain_cic_context("trading")
    assert any(_EXPECTED in rule for rule in ctx["central_rules"])
    assert _EXPECTED in ctx["memory_policy"]


def test_memory_not_sovereign_in_gps_domain():
    ctx = build_domain_cic_context("gps_defense_aviation")
    assert any(_EXPECTED in rule for rule in ctx["central_rules"])
    assert _EXPECTED in ctx["memory_policy"]


def test_provider_memory_write_not_in_allowed():
    ctx = build_cic_readonly_context()
    assert "memory_write" in ctx["forbidden_capabilities"]
