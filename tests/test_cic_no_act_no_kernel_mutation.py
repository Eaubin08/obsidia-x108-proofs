"""
Tests — Pas d'ACT, pas de mutation kernel via CIC
Tests 4, 5 étendus + vérifications NCP/scraping/world_connection.
"""
from __future__ import annotations

from apps.obsidia_api.brody_cic_context_adapter import build_brody_cic_packet
from apps.obsidia_api.cic.cic_domain_context import (
    build_all_domain_contexts,
    build_domain_cic_context,
)
from apps.obsidia_api.cic.cic_readonly_pack_provider import build_cic_readonly_context


def test_provider_emits_act_false():
    ctx = build_cic_readonly_context()
    assert ctx["emits_act"] is False


def test_provider_kernel_mutation_false():
    ctx = build_cic_readonly_context()
    assert ctx["kernel_mutation"] is False


def test_provider_ncp_active_false():
    ctx = build_cic_readonly_context()
    assert ctx["ncp_active"] is False


def test_provider_scraping_active_false():
    ctx = build_cic_readonly_context()
    assert ctx["scraping_active"] is False


def test_brody_packet_emits_act_false():
    packet = build_brody_cic_packet()
    ctx = packet["cic_readonly_context"]
    assert ctx["emits_act"] is False
    assert ctx["kernel_mutation"] is False
    assert ctx["ncp_active"] is False
    assert ctx["scraping_active"] is False


def test_all_domain_contexts_no_act_no_kernel():
    all_ctx = build_all_domain_contexts()
    for domain, ctx in all_ctx.items():
        if ctx.get("status") in ("ECOM_NOT_FOUND", "DOMAIN_NOT_FOUND"):
            assert ctx["emits_act"] is False
            assert ctx["kernel_mutation"] is False
        else:
            assert ctx["emits_act"] is False, f"domaine {domain}: emits_act doit être False"
            assert ctx["kernel_mutation"] is False, f"domaine {domain}: kernel_mutation doit être False"


def test_forbidden_capabilities_include_act_and_kernel():
    ctx = build_cic_readonly_context()
    forbidden = ctx["forbidden_capabilities"]
    assert "act" in forbidden
    assert "kernel_mutation" in forbidden
    assert "ncp_activation" in forbidden
    assert "scraping_activation" in forbidden
    assert "world_connection_activation" in forbidden


def test_brody_boundary_cannot_emit_act():
    packet = build_brody_cic_packet()
    boundary = packet["cic_readonly_context"]["brody_boundary"]
    assert boundary["can_emit_act"] is False
    assert boundary["can_mutate_kernel"] is False
