"""
Tests — CIC Readonly Pack Provider
Tests 1-7 : vérifications fondamentales du provider CIC.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from apps.obsidia_api.cic.cic_readonly_pack_provider import (
    _ZIP_CANONICAL,
    build_cic_readonly_context,
)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest().upper()


# Test 1
def test_zip_exists():
    assert _ZIP_CANONICAL.exists(), f"ZIP introuvable: {_ZIP_CANONICAL}"


# Test 2
def test_zip_sha256_calculable():
    assert _ZIP_CANONICAL.exists()
    sha = _sha256(_ZIP_CANONICAL)
    assert len(sha) == 64
    assert sha == "037E1696A0643683ACC9B48DA209EB25CA0BB06916F0A56D2BB57E78A7C61115"


# Test 3
def test_provider_readonly_true():
    ctx = build_cic_readonly_context()
    assert ctx["readonly"] is True


# Test 4
def test_provider_emits_act_false():
    ctx = build_cic_readonly_context()
    assert ctx["emits_act"] is False


# Test 5
def test_provider_kernel_mutation_false():
    ctx = build_cic_readonly_context()
    assert ctx["kernel_mutation"] is False


# Test 6
def test_provider_x108_binding_false():
    ctx = build_cic_readonly_context()
    assert ctx["x108_binding"] is False


# Test 7
def test_provider_decision_authority_kx108_only():
    ctx = build_cic_readonly_context()
    assert ctx["decision_authority"] == "KX108_ONLY"


# Test 14 (NCP)
def test_no_ncp_activation():
    ctx = build_cic_readonly_context()
    assert ctx["ncp_active"] is False


# Test 15 (scraping)
def test_no_scraping_activation():
    ctx = build_cic_readonly_context()
    assert ctx["scraping_active"] is False


def test_source_status_is_local_freeze_readonly():
    ctx = build_cic_readonly_context()
    assert ctx["source_status"] == "LOCAL_FREEZE_READONLY"


def test_authority_is_none():
    ctx = build_cic_readonly_context()
    assert ctx["authority"] == "NONE"


def test_confirmed_metric_families_not_empty():
    ctx = build_cic_readonly_context()
    assert len(ctx["confirmed_metric_families"]) > 0


def test_zip_sha256_in_context_matches_file():
    ctx = build_cic_readonly_context()
    assert ctx["source_zip_sha256"] == _sha256(_ZIP_CANONICAL)


# ---------------------------------------------------------------------------
# T16-T25 — NCP/Scraping binding (Phase 3)
# ---------------------------------------------------------------------------

# T16
def test_ncp_context_present():
    ctx = build_cic_readonly_context()
    assert "ncp_context" in ctx
    assert isinstance(ctx["ncp_context"], dict)
    assert len(ctx["ncp_context"]) > 0


# T17
def test_ncp_context_active_false():
    ctx = build_cic_readonly_context()
    assert ctx["ncp_context"]["ncp_active"] is False


# T18
def test_ncp_context_authority_none():
    ctx = build_cic_readonly_context()
    assert ctx["ncp_context"]["authority"] == "NONE"


# T19
def test_scraping_context_present():
    ctx = build_cic_readonly_context()
    assert "scraping_context" in ctx
    assert isinstance(ctx["scraping_context"], dict)
    assert len(ctx["scraping_context"]) > 0


# T20
def test_scraping_context_active_false():
    ctx = build_cic_readonly_context()
    assert ctx["scraping_context"]["scraping_active"] is False


# T21
def test_scraping_context_quarantine_policy():
    ctx = build_cic_readonly_context()
    assert ctx["scraping_context"]["quarantine_policy"] == "WEB_SCRAPE_QUARANTINED"


# T22 — régression top-level ncp_active
def test_top_level_ncp_active_still_false():
    ctx = build_cic_readonly_context()
    assert ctx["ncp_active"] is False


# T23 — régression top-level scraping_active
def test_top_level_scraping_active_still_false():
    ctx = build_cic_readonly_context()
    assert ctx["scraping_active"] is False


# T24
def test_ncp_context_no_network():
    ctx = build_cic_readonly_context()
    ncp = ctx["ncp_context"]
    assert ncp["network"] is False
    assert ncp["fetch"] is False
    assert ncp["crawl"] is False


# T25
def test_missing_or_inactive_updated():
    ctx = build_cic_readonly_context()
    moi = ctx["missing_or_inactive"]
    assert "ncp_targeted_fetch:MISSING" not in moi
    assert "scraping:MISSING" not in moi
    assert any("ncp_targeted_fetch:STUB_V0" in s for s in moi)
    assert any("scraping:STUB_V0" in s for s in moi)
