"""
Test: Brody Final Answer — Freeze-Sourced Live Cases
=======================================================
Tests the 5 live cases from the spec with freeze_metrics_snapshot wired.
Each case asserts: no template fallbacks, freeze metrics used, boundary intact.
"""
import pytest
from apps.obsidia_api.brody_freeze_metrics_snapshot import build_freeze_metrics_snapshot
from apps.obsidia_api.brody_v1_4_12a_final_answer_adapter import (
    run_brody_v1_4_12a_final_answer,
)


@pytest.fixture(scope="module")
def freeze_snap():
    """Module-level freeze snapshot for all tests."""
    return build_freeze_metrics_snapshot()


# ── Case 1: "je trouve que tes réponses sont encore trop protocolaires" ──────

def test_case1_protocolaire_complaint_no_template(freeze_snap):
    """Should NOT return 'Signal reçu...' or 'Développe ta demande'."""
    result = run_brody_v1_4_12a_final_answer(
        user_message="je trouve que tes réponses sont encore trop protocolaires",
        language="fr",
        freeze_metrics_snapshot=freeze_snap,
    )
    final = result["final_answer"]
    assert "Signal reçu" not in final, "Must not use template 'Signal reçu'"
    assert "Développe ta demande" not in final, "Must not use template 'Développe ta demande'"
    assert "Je lis le contexte actuel" not in final, "Must not use template 'Je lis le contexte actuel'"
    # Should contain diagnostic about the problem
    assert any(kw in final.lower() for kw in ["template", "protocolaire", "diagnostic", "freeze", "source"]), \
        "Response should address the protocolaire/template complaint"
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["emits_act"] is False


def test_case1_uses_freeze_metrics(freeze_snap):
    """Response should reference structured_response or freeze_metrics."""
    result = run_brody_v1_4_12a_final_answer(
        user_message="je trouve que tes réponses sont encore trop protocolaires",
        language="fr",
        freeze_metrics_snapshot=freeze_snap,
    )
    final = result["final_answer"]
    freeze_snap_present = (
        "structured_response" in final.lower()
        or "freeze_metrics" in final.lower()
        or "CURRENT_BRODY" in final
    )
    assert freeze_snap_present, (
        "Response should mention structured_response_snapshot or freeze_metrics_snapshot"
    )


# ── Case 2: "reprends le point précédent" (after case 1) ─────────────────────

def test_case2_reprendre_point_precedent_no_fallback(freeze_snap):
    """Should not fallback to template after followup."""
    # Simulate a session by passing context through the response
    result = run_brody_v1_4_12a_final_answer(
        user_message="reprends le point précédent avec plus de structure",
        language="fr",
        response_md="RÉPONSE PRÉCÉDENTE: Diagnostic protocolaire. Correction en cours.",
        freeze_metrics_snapshot=freeze_snap,
    )
    final = result["final_answer"]
    assert len(final) > 40, "Response should not be empty or minimal"
    # Should not be a generic fallback
    assert "Signal reçu" not in final
    assert "Développe ta demande" not in final
    assert result["emits_act"] is False


# ── Case 3: "qu'est-ce que tu dois utiliser pour mieux répondre ?" ───────────

def test_case3_better_response_sources(freeze_snap):
    """Should list ContextPacket chain, response_md, freeze_metrics_snapshot."""
    result = run_brody_v1_4_12a_final_answer(
        user_message="qu'est-ce que tu dois utiliser pour mieux répondre ?",
        language="fr",
        freeze_metrics_snapshot=freeze_snap,
    )
    final = result["final_answer"]
    # Should mention ContextPacket chain
    assert any(kw in final.lower() for kw in [
        "contextpacket", "query", "consumer", "engine", "chaîne"
    ]), "Should mention ContextPacket chain"
    # Should mention structured response or freeze metrics
    assert any(kw in final.lower() for kw in [
        "structured_response", "response_md", "freeze_metrics", "snapshot"
    ]), "Should mention structured_response_snapshot or freeze_metrics_snapshot"
    # No fallback
    assert "Signal reçu" not in final
    assert "Développe ta demande" not in final
    assert result["emits_act"] is False


# ── Case 4: "explique operator loop, command gate, receipt et handoff" ───────

def test_case4_operator_loop_explanation(freeze_snap):
    """Should explain operator loop components from freeze metrics."""
    result = run_brody_v1_4_12a_final_answer(
        user_message="explique operator loop, command gate, receipt et handoff",
        language="fr",
        freeze_metrics_snapshot=freeze_snap,
    )
    final = result["final_answer"]
    # Must mention operator loop specifics
    keywords = ["command gate", "receipt", "handoff", "operator", "opérateur", "boucle"]
    assert any(kw in final.lower() for kw in keywords), \
        "Should mention operator loop components"
    # Should cite PASS status or freeze data
    assert any(kw in final for kw in ["V1_PASS", "PASS", "brody_execute_allowed", "human_operator"]), \
        "Should cite freeze-sourced operator loop status"
    assert result["emits_act"] is False


# ── Case 5: "montre-moi ce que tu peux retenir sans écrire réellement" ───────

def test_case5_memory_retention(freeze_snap):
    """Should show memory pipeline components with write flags disabled."""
    result = run_brody_v1_4_12a_final_answer(
        user_message="montre-moi ce que tu peux retenir sans écrire réellement",
        language="fr",
        freeze_metrics_snapshot=freeze_snap,
    )
    final = result["final_answer"]
    # Must mention memory pipeline components
    memory_keywords = ["session", "presave", "triage", "ledger", "buffer", "candidate", "retenir", "mémoire"]
    assert any(kw in final.lower() for kw in memory_keywords), \
        "Should mention memory pipeline components"
    # Must confirm writes are disabled
    assert any(kw in final.lower() for kw in ["false", "désactivé", "disable", "jamais", "never", "écrire", "write"]), \
        "Should mention writes are disabled"
    assert "graphiti_write" in final.lower() or "graphiti" in final.lower()
    assert "neo4j_write" in final.lower() or "neo4j" in final.lower()
    assert result["emits_act"] is False
    assert result["memory_write"] is False


# ── Anti-invention tests ─────────────────────────────────────────────────────

def test_anti_invention_no_invented_counts(freeze_snap):
    """Freeze-sourced responses must not invent Graphiti/Neo4j counts."""
    snap = freeze_snap
    nf = snap.get("not_found_in_freeze_sources", {})
    result = run_brody_v1_4_12a_final_answer(
        user_message="combien de nodes Graphiti ?",
        language="fr",
        freeze_metrics_snapshot=freeze_snap,
    )
    final = result["final_answer"]
    # If NOT_FOUND, response should not claim specific numbers
    if "graphiti_v20_nodes" in nf:
        # Should not contain specific invented counts for NOT_FOUND metrics
        import re
        numbers = re.findall(r'\b\d{3,5}\b', final)
        for n in numbers:
            # Numbers like 167, 477, 3267 are invented if not in freeze
            if n in ("167", "477", "3267"):
                pytest.fail(f"Response contains invented Graphiti/Neo4j count: {n}")


def test_boundary_invariants_preserved(freeze_snap):
    """All responses must preserve boundary invariants regardless of freeze state."""
    for msg in [
        "test",
        "explique le système",
        "que peux-tu faire ?",
    ]:
        result = run_brody_v1_4_12a_final_answer(
            user_message=msg,
            language="fr",
            freeze_metrics_snapshot=freeze_snap,
        )
        assert result["decision_authority"] == "KX108_ONLY", f"Boundary violated for: {msg}"
        assert result["emits_act"] is False, f"emits_act violated for: {msg}"
        assert result["emits_verdict"] is False, f"emits_verdict violated for: {msg}"
        assert result["memory_write"] is False, f"memory_write violated for: {msg}"
        assert result["kernel_mutation"] is False, f"kernel_mutation violated for: {msg}"
