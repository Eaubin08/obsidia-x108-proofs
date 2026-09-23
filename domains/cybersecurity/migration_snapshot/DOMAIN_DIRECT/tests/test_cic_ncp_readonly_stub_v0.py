"""
Tests NCP_READONLY_STUB_V0
Vérifie : import, déterminisme, flags interdits false, authority, network, ACT, write.
NCP_ACTIVE=NO | NETWORK=NO | AUTHORITY=NONE | DECISION_AUTHORITY=KX108_ONLY
"""
import pytest

from apps.obsidia_api.cic.cic_ncp_readonly_stub import build_ncp_readonly_stub


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------

def test_import_ok():
    """Le module s'importe et la fonction est appelable."""
    result = build_ncp_readonly_stub()
    assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# Déterminisme
# ---------------------------------------------------------------------------

def test_output_deterministic_same_domain():
    """Deux appels avec le même domaine produisent exactement le même dict."""
    r1 = build_ncp_readonly_stub(domain="test_domain")
    r2 = build_ncp_readonly_stub(domain="test_domain")
    assert r1 == r2


def test_output_deterministic_default_domain():
    """Appel sans argument : déterministe sur deux invocations."""
    r1 = build_ncp_readonly_stub()
    r2 = build_ncp_readonly_stub()
    assert r1 == r2


def test_stub_id_stable():
    """ncp_stub_id est stable entre les appels pour le même domaine."""
    r1 = build_ncp_readonly_stub(domain="cic_readonly_pack")
    r2 = build_ncp_readonly_stub(domain="cic_readonly_pack")
    assert r1["ncp_stub_id"] == r2["ncp_stub_id"]


def test_stub_id_differs_by_domain():
    """ncp_stub_id diffère si le domaine change."""
    r1 = build_ncp_readonly_stub(domain="domain_a")
    r2 = build_ncp_readonly_stub(domain="domain_b")
    assert r1["ncp_stub_id"] != r2["ncp_stub_id"]


# ---------------------------------------------------------------------------
# Authority
# ---------------------------------------------------------------------------

def test_authority_none():
    """authority doit être 'NONE' — NCP n'est pas souverain."""
    result = build_ncp_readonly_stub()
    assert result["authority"] == "NONE"


def test_decision_authority_kx108_only():
    """decision_authority doit être 'KX108_ONLY' — seul X108 décide."""
    result = build_ncp_readonly_stub()
    assert result["decision_authority"] == "KX108_ONLY"


def test_allowed_to_act_false():
    result = build_ncp_readonly_stub()
    assert result["allowed_to_act"] is False


def test_allowed_to_decide_false():
    result = build_ncp_readonly_stub()
    assert result["allowed_to_decide"] is False


# ---------------------------------------------------------------------------
# Réseau — aucun champ réseau actif
# ---------------------------------------------------------------------------

def test_ncp_active_false():
    result = build_ncp_readonly_stub()
    assert result["ncp_active"] is False


def test_network_false():
    result = build_ncp_readonly_stub()
    assert result["network"] is False


def test_fetch_false():
    result = build_ncp_readonly_stub()
    assert result["fetch"] is False


def test_crawl_false():
    result = build_ncp_readonly_stub()
    assert result["crawl"] is False


def test_no_external_data_true():
    result = build_ncp_readonly_stub()
    assert result["no_external_data"] is True


def test_source_local_stub_only():
    result = build_ncp_readonly_stub()
    assert result["source"] == "LOCAL_STUB_ONLY"


# ---------------------------------------------------------------------------
# ACT / verdict souverain
# ---------------------------------------------------------------------------

def test_emits_act_false():
    result = build_ncp_readonly_stub()
    assert result["emits_act"] is False


def test_emits_verdict_false():
    result = build_ncp_readonly_stub()
    assert result["emits_verdict"] is False


def test_no_sovereign_verdict_keys():
    """Aucun champ souverain (ALLOW/BLOCK/HOLD/gate/decision) dans le résultat."""
    result = build_ncp_readonly_stub()
    forbidden = {"ALLOW", "BLOCK", "HOLD", "decision", "gate", "verdict",
                 "authority_result", "computed_path", "path_decision"}
    assert not forbidden.intersection(result.keys())


# ---------------------------------------------------------------------------
# Write / mutation
# ---------------------------------------------------------------------------

def test_graphiti_write_false():
    result = build_ncp_readonly_stub()
    assert result["graphiti_write"] is False


def test_neo4j_write_false():
    result = build_ncp_readonly_stub()
    assert result["neo4j_write"] is False


def test_memory_write_false():
    result = build_ncp_readonly_stub()
    assert result["memory_write"] is False


def test_kernel_mutation_false():
    result = build_ncp_readonly_stub()
    assert result["kernel_mutation"] is False


def test_real_action_false():
    result = build_ncp_readonly_stub()
    assert result["real_action"] is False


# ---------------------------------------------------------------------------
# Readonly / advisory
# ---------------------------------------------------------------------------

def test_readonly_true():
    result = build_ncp_readonly_stub()
    assert result["readonly"] is True


def test_advisory_only_true():
    result = build_ncp_readonly_stub()
    assert result["advisory_only"] is True


def test_context_signal_only_true():
    result = build_ncp_readonly_stub()
    assert result["context_signal_only"] is True


# ---------------------------------------------------------------------------
# Aucun secret dans la sortie
# ---------------------------------------------------------------------------

def test_no_secret_keys():
    """Aucun champ portant une valeur sensible (token, key, password, secret)."""
    result = build_ncp_readonly_stub()
    secret_patterns = {"token", "key", "password", "secret", "api_key", "credential"}
    for k in result:
        assert k.lower() not in secret_patterns, f"Clé suspecte trouvée : {k}"
    for v in result.values():
        if isinstance(v, str):
            assert "bearer" not in v.lower()
            assert "sk-" not in v.lower()


# ---------------------------------------------------------------------------
# Aucun appel réseau monkeypatché (pas d'import socket/urllib/requests)
# ---------------------------------------------------------------------------

def test_no_network_imports_in_stub(monkeypatch):
    """
    Le stub ne doit pas tenter d'appel réseau même si socket est bloqué.
    On bloque socket.getaddrinfo pour s'assurer qu'aucun appel DNS n'est fait.
    """
    import socket

    def _blocked(*args, **kwargs):
        raise RuntimeError("Appel réseau interdit dans NCP readonly stub")

    monkeypatch.setattr(socket, "getaddrinfo", _blocked)
    result = build_ncp_readonly_stub(domain="network_test")
    assert result["network"] is False
