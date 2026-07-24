"""
Tests — CIC Receipt Replay V0
Vérifie que le receipt CIC est readonly, déterministe, et sans champ souverain.
DECISION_AUTHORITY: KX108_ONLY | AUTHORITY: NONE | ACT: NO
"""
from __future__ import annotations

import pytest

from apps.obsidia_api.cic.cic_receipt_pack import build_cic_receipt
from apps.obsidia_api.cic.cic_readonly_pack_provider import build_cic_readonly_context

_SOVEREIGN_KEYS = {"ALLOW", "BLOCK", "HOLD", "decision", "gate", "verdict"}

_SAMPLE_FAMILIES = ["guard_metrics", "timing_metrics", "proof_metrics"]


def _make_receipt():
    return build_cic_receipt(
        domain="test_domain",
        source_zip_sha256="abc123def456",
        confirmed_metric_families=_SAMPLE_FAMILIES,
    )


# Test 1 — receipt_id présent et préfixé
def test_receipt_id_present():
    r = _make_receipt()
    assert "receipt_id" in r
    assert r["receipt_id"].startswith("CIC_RCP_")


# Test 2 — invocation_hash présent (sha256 hex, 64 chars)
def test_invocation_hash_present():
    r = _make_receipt()
    assert "invocation_hash" in r
    assert len(r["invocation_hash"]) == 64


# Test 3 — invocation_hash stable sur deux appels identiques
def test_invocation_hash_deterministic():
    r1 = build_cic_receipt(
        domain="stable_domain",
        source_zip_sha256="fixedsha",
        confirmed_metric_families=["guard_metrics", "proof_metrics"],
    )
    r2 = build_cic_receipt(
        domain="stable_domain",
        source_zip_sha256="fixedsha",
        confirmed_metric_families=["proof_metrics", "guard_metrics"],  # ordre différent
    )
    assert r1["invocation_hash"] == r2["invocation_hash"]


# Test 4 — replay_inputs présent et non vide
def test_replay_inputs_present():
    r = _make_receipt()
    assert "replay_inputs" in r
    assert isinstance(r["replay_inputs"], dict)
    assert len(r["replay_inputs"]) > 0


# Test 5 — replay_inputs ne contient aucun champ souverain
def test_replay_inputs_no_sovereign_keys():
    r = _make_receipt()
    for key in r["replay_inputs"]:
        assert key.upper() not in _SOVEREIGN_KEYS, f"Clé souveraine interdite : {key}"


# Test 6 — flags readonly invariants dans le receipt
def test_receipt_readonly_flags():
    r = _make_receipt()
    assert r["readonly"] is True
    assert r["emits_act"] is False
    assert r["graphiti_write"] is False
    assert r["neo4j_write"] is False
    assert r["kernel_mutation"] is False
    assert r["memory_write"] is False
    assert r["real_action"] is False
    assert r["canonical_write"] is False


# Test 7 — authority et decision_authority
def test_receipt_authority():
    r = _make_receipt()
    assert r["authority"] == "NONE"
    assert r["decision_authority"] == "KX108_ONLY"


# Test 8 — cic_receipt intégré dans build_cic_readonly_context
def test_provider_includes_receipt():
    ctx = build_cic_readonly_context()
    assert "cic_receipt" in ctx
    receipt = ctx["cic_receipt"]
    assert receipt["receipt_id"].startswith("CIC_RCP_")
    assert receipt["authority"] == "NONE"
    assert receipt["decision_authority"] == "KX108_ONLY"
    assert receipt["readonly"] is True
    assert receipt["emits_act"] is False
    assert receipt["kernel_mutation"] is False
