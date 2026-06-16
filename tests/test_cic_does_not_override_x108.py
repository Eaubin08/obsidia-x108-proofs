"""
Tests — CIC ne remplace pas X108
Vérifie qu'aucun composant CIC ne prend l'autorité X108.
"""
from __future__ import annotations

from apps.obsidia_api.brody_cic_context_adapter import build_brody_cic_packet
from apps.obsidia_api.cic.cic_domain_context import build_domain_cic_context
from apps.obsidia_api.cic.cic_readonly_pack_provider import build_cic_readonly_context


def test_provider_authority_is_none():
    ctx = build_cic_readonly_context()
    assert ctx["authority"] == "NONE"
    assert ctx["decision_authority"] == "KX108_ONLY"


def test_brody_adapter_decision_authority_kx108_only():
    packet = build_brody_cic_packet()
    ctx = packet["cic_readonly_context"]
    assert ctx["decision_authority"] == "KX108_ONLY"
    assert ctx["brody_boundary"]["decision_authority"] == "KX108_ONLY"


def test_domain_bank_decision_authority_kx108_only():
    ctx = build_domain_cic_context("bank")
    assert ctx["decision_authority"] == "KX108_ONLY"


def test_domain_trading_decision_authority_kx108_only():
    ctx = build_domain_cic_context("trading")
    assert ctx["decision_authority"] == "KX108_ONLY"


def test_domain_gps_decision_authority_kx108_only():
    ctx = build_domain_cic_context("gps_defense_aviation")
    assert ctx["decision_authority"] == "KX108_ONLY"


def test_provider_forbidden_capabilities_includes_decision_authority():
    ctx = build_cic_readonly_context()
    assert "decision_authority" in ctx["forbidden_capabilities"]
    assert "kernel_mutation" in ctx["forbidden_capabilities"]
    assert "x108_binding" in ctx["forbidden_capabilities"]


def test_cic_does_not_claim_authority_over_x108():
    ctx = build_cic_readonly_context()
    assert ctx["x108_binding"] is False
    assert ctx["authority"] != "X108"
    assert ctx["authority"] != "KX108"
    assert ctx["decision_authority"] == "KX108_ONLY"
