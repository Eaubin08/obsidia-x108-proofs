"""
Tests — Donnée manquante critique : REVIEW/HOLD/BLOCK seulement, jamais ACT via CIC.
Tests 19, 20, 21 couverts ici.
"""
from __future__ import annotations

from apps.obsidia_api.brody_cic_context_adapter import build_brody_cic_packet
from apps.obsidia_api.cic.cic_domain_context import build_domain_cic_context
from apps.obsidia_api.cic.cic_readonly_pack_provider import (
    _CENTRAL_RULES,
    build_cic_readonly_context,
)

_RULE_SCORE_INVARIANT = "A score cannot authorize what an invariant forbids."
_RULE_PRIORITY = "Invariant > Reversibilite > Score > Projection"
_RULE_MISSING_DATA = (
    "Critical missing data on irreversible action triggers HOLD / BLOCK / REVIEW."
)


# Test 19
def test_score_cannot_authorize_invariant_in_central_rules():
    assert _RULE_SCORE_INVARIANT in _CENTRAL_RULES


def test_score_cannot_authorize_invariant_in_provider():
    ctx = build_cic_readonly_context()
    assert any(_RULE_SCORE_INVARIANT in rule for rule in ctx["central_rules"])


def test_score_cannot_authorize_invariant_in_brody():
    packet = build_brody_cic_packet()
    ctx = packet["cic_readonly_context"]
    assert ctx["score_cannot_authorize_invariant"] == _RULE_SCORE_INVARIANT


# Test 20
def test_invariant_priority_chain_in_central_rules():
    assert _RULE_PRIORITY in _CENTRAL_RULES


def test_invariant_priority_chain_in_provider():
    ctx = build_cic_readonly_context()
    assert any(_RULE_PRIORITY in rule for rule in ctx["central_rules"])


def test_priority_chain_in_brody():
    packet = build_brody_cic_packet()
    ctx = packet["cic_readonly_context"]
    assert ctx["priority_chain"] == _RULE_PRIORITY


def test_priority_chain_in_domain_contexts():
    for domain in ("bank", "trading", "gps_defense_aviation"):
        ctx = build_domain_cic_context(domain)
        assert ctx["invariants_priority"] == _RULE_PRIORITY, f"Manquant dans {domain}"


# Test 21
def test_missing_critical_data_triggers_review_not_act():
    ctx = build_cic_readonly_context()
    assert any(_RULE_MISSING_DATA in rule for rule in ctx["central_rules"])
    assert ctx["emits_act"] is False


def test_missing_data_policy_in_domain_says_review_hold_block():
    for domain in ("bank", "trading", "gps_defense_aviation"):
        ctx = build_domain_cic_context(domain)
        policy = ctx["missing_data_policy"]
        assert "HOLD" in policy or "BLOCK" in policy or "REVIEW" in policy
        # "never ACT" doit être présent (CIC n'émet jamais ACT comme verdict autonome)
        assert "never ACT" in policy, (
            f"La politique manquante-données doit contenir 'never ACT' pour {domain}"
        )


def test_missing_data_never_produces_act_from_cic():
    packet = build_brody_cic_packet()
    ctx = packet["cic_readonly_context"]
    assert ctx["emits_act"] is False
    assert ctx["decision_authority"] == "KX108_ONLY"
    for domain in ("bank", "trading", "gps_defense_aviation"):
        dctx = build_domain_cic_context(domain)
        assert dctx["emits_act"] is False


def test_missing_or_inactive_listed_in_provider():
    ctx = build_cic_readonly_context()
    missing = ctx["missing_or_inactive"]
    assert any("ncp_targeted_fetch" in m for m in missing)
    assert any("scraping" in m for m in missing)
    assert any("kernel_binding" in m for m in missing)
