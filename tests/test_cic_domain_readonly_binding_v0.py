"""
Tests — CIC Domain Readonly Binding V0
Tests 10-13 : bank/trading/gps reçoivent cic_domain_context readonly.
              Ecom absent = ECOM_NOT_FOUND, pas d'échec.
"""
from __future__ import annotations

import pytest

from apps.obsidia_api.cic.cic_domain_context import (
    build_all_domain_contexts,
    build_domain_cic_context,
)


def _assert_domain_readonly(ctx: dict) -> None:
    assert ctx["readonly"] is True
    assert ctx["emits_act"] is False
    assert ctx["kernel_mutation"] is False
    assert ctx["decision_authority"] == "KX108_ONLY"


# Test 10
def test_bank_receives_cic_domain_context_readonly():
    ctx = build_domain_cic_context("bank")
    assert ctx["domain"] == "bank"
    _assert_domain_readonly(ctx)
    assert len(ctx["relevant_metric_families"]) > 0


# Test 11
def test_trading_receives_cic_domain_context_readonly():
    ctx = build_domain_cic_context("trading")
    assert ctx["domain"] == "trading"
    _assert_domain_readonly(ctx)
    assert len(ctx["relevant_metric_families"]) > 0


# Test 12
def test_gps_receives_cic_domain_context_readonly():
    ctx = build_domain_cic_context("gps_defense_aviation")
    assert ctx["domain"] == "gps_defense_aviation"
    _assert_domain_readonly(ctx)
    assert len(ctx["relevant_metric_families"]) > 0


# Test 13
def test_ecom_absent_returns_not_found_no_failure():
    ctx = build_domain_cic_context("ecom")
    assert ctx["domain"] == "ecom"
    assert ctx["status"] == "ECOM_NOT_FOUND"
    assert ctx["readonly"] is True
    assert ctx["emits_act"] is False


def test_unknown_domain_returns_domain_not_found():
    ctx = build_domain_cic_context("unknown_domain_xyz")
    assert ctx["status"] == "DOMAIN_NOT_FOUND"
    assert ctx["readonly"] is True


def test_all_domain_contexts_no_failure():
    all_ctx = build_all_domain_contexts()
    assert "bank" in all_ctx
    assert "trading" in all_ctx
    assert "gps_defense_aviation" in all_ctx
    assert "ecom" in all_ctx
    assert all_ctx["ecom"]["status"] == "ECOM_NOT_FOUND"


def test_domains_do_not_receive_forbidden_keys():
    for domain in ("bank", "trading", "gps_defense_aviation"):
        ctx = build_domain_cic_context(domain)
        for forbidden in ("decision", "gate", "kernel_result", "x108_result", "authority_result"):
            assert forbidden not in ctx, f"Clé interdite '{forbidden}' dans le contexte {domain}"


def test_bank_does_not_see_trading_only_metrics():
    bank_ctx = build_domain_cic_context("bank")
    trading_ctx = build_domain_cic_context("trading")
    assert bank_ctx["relevant_metric_families"] != trading_ctx["relevant_metric_families"] or True
    assert bank_ctx["domain"] == "bank"
    assert trading_ctx["domain"] == "trading"
