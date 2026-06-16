"""
Tests — Projection is not prediction
Test 17 : vérifie que la règle projection_not_prediction est présente partout.
"""
from __future__ import annotations

from apps.obsidia_api.brody_cic_context_adapter import build_brody_cic_packet
from apps.obsidia_api.cic.cic_domain_context import build_domain_cic_context
from apps.obsidia_api.cic.cic_readonly_pack_provider import (
    _CENTRAL_RULES,
    build_cic_readonly_context,
)

_EXPECTED = "Projection is not prediction."


# Test 17
def test_projection_not_prediction_in_central_rules():
    assert _EXPECTED in _CENTRAL_RULES


def test_projection_not_prediction_in_provider_context():
    ctx = build_cic_readonly_context()
    assert any(_EXPECTED in rule for rule in ctx["central_rules"])


def test_projection_not_prediction_in_brody_packet():
    packet = build_brody_cic_packet()
    ctx = packet["cic_readonly_context"]
    assert ctx["projection_not_prediction"] == _EXPECTED


def test_projection_not_prediction_in_brody_central_rules():
    packet = build_brody_cic_packet()
    ctx = packet["cic_readonly_context"]
    assert any(_EXPECTED in rule for rule in ctx["central_rules"])


def test_projection_not_prediction_in_bank_domain():
    ctx = build_domain_cic_context("bank")
    assert any(_EXPECTED in rule for rule in ctx["central_rules"])


def test_projection_not_prediction_in_trading_domain():
    ctx = build_domain_cic_context("trading")
    assert any(_EXPECTED in rule for rule in ctx["central_rules"])


def test_projection_not_prediction_in_gps_domain():
    ctx = build_domain_cic_context("gps_defense_aviation")
    assert any(_EXPECTED in rule for rule in ctx["central_rules"])


def test_projection_policy_in_domain_context():
    for domain in ("bank", "trading", "gps_defense_aviation"):
        ctx = build_domain_cic_context(domain)
        assert _EXPECTED in ctx["projection_policy"], f"Manquant dans {domain}"
