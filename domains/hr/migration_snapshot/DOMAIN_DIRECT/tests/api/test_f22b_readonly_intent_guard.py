"""F22B — Readonly Runtime State Intent Guard tests.

Unit tests: pure function calls against the guard and the patched helpers.
Live smoke tests: POST /api/brody/chat on ports 8000 and 8012.

All tests are READ_ONLY. No write, no memory, no kernel/x108 mutation.
"""
import json
import urllib.request

import pytest

from apps.obsidia_api.brody_readonly_intent_guard import (
    detect_readonly_runtime_state_intent,
    _fold,
    _has_explicit_write,
    _has_readonly_signal,
)
from apps.obsidia_api.brody_domain_raccord_adapter import has_memory_write_request
from apps.obsidia_api.routes.os_trad_ir_reverse import _risk_flags

# ── canonical F22B test prompt ───────────────────────────────────────────────

_READONLY_PROMPT = (
    "Décris ton état système actuel en lecture seule : "
    "modules actifs, mémoire, Graphiti, IR, Reverse OS, Thermo, Gencoin, "
    "Dashboard runtime. Ne propose aucune action."
)

# ── Unit tests ───────────────────────────────────────────────────────────────


def test_decris_does_not_match_ecris_write():
    """'decris' must NOT trigger has_memory_write_request (false positive F22A)."""
    assert has_memory_write_request("Décris ton état système") is False
    assert has_memory_write_request("decris les modules actifs") is False
    assert has_memory_write_request("décrire le runtime") is False


def test_actifs_does_not_match_act_action():
    """'actifs' and 'action' (negated) must NOT produce action_request risk flag."""
    flags = _risk_flags(_READONLY_PROMPT)
    assert "action_request" not in flags, f"Unexpected action_request in: {flags}"


def test_runtime_state_readonly_intent_detected():
    """Full canonical prompt must return RUNTIME_STATE_READONLY_INTENT_PASS."""
    result = detect_readonly_runtime_state_intent(_READONLY_PROMPT)
    assert result["status"] == "RUNTIME_STATE_READONLY_INTENT_PASS"
    assert result["intent"] == "RUNTIME_STATE_READONLY"
    assert result["write_boundary_required"] is False
    assert result["ir_op"] == "READ"
    assert result["ir_target"] == "STATE(runtime_status)"
    assert "RUNTIME_STATE_READONLY" in result["domains"]
    assert result["risk_flags"] == []
    assert result["contradictions"] == []
    assert result["readonly"] is True
    assert result["decision_authority"] == "KX108_ONLY"


def test_graphiti_mention_readonly_not_graphiti_write():
    """Mentioning 'Graphiti' in a readonly query must NOT trigger write boundary."""
    prompts = [
        "Décris l'état de Graphiti en lecture seule.",
        "Explique le statut Graphiti actuel.",
        "Describe Graphiti readonly state.",
    ]
    for p in prompts:
        assert has_memory_write_request(p) is False, f"False write trigger for: {p!r}"
        result = detect_readonly_runtime_state_intent(p)
        assert result["write_boundary_required"] is False, f"write_boundary true for: {p!r}"


def test_memory_mention_readonly_not_memory_write():
    """Mentioning 'mémoire' in a readonly query must NOT trigger write boundary."""
    prompts = [
        "Décris la mémoire candidate actuelle.",
        "Explique l'état de la mémoire en lecture seule.",
        "Describe memory state readonly.",
    ]
    for p in prompts:
        assert has_memory_write_request(p) is False, f"False write trigger for: {p!r}"


def test_freeze_dashboard_mention_not_freeze_promotion():
    """'dashboard runtime' and 'freeze' in a description must not add MEMORY_WRITE_CANON_FREEZE.

    Guard passes for readonly descriptions → build_domain_raccord_snapshot suppresses
    MEMORY_WRITE_CANON_FREEZE even though 'freeze' appears in write_terms.
    The guard is the correct layer to check, not has_memory_write_request directly.
    """
    from apps.obsidia_api.brody_domain_raccord_adapter import build_domain_raccord_snapshot

    prompts = [
        "Décris le dashboard runtime et le freeze dashboard.",
        "Explique l'état du freeze dashboard en lecture seule.",
    ]
    for p in prompts:
        result = detect_readonly_runtime_state_intent(p)
        assert result["status"] == "RUNTIME_STATE_READONLY_INTENT_PASS", f"Guard missed: {p!r}"
        snap = build_domain_raccord_snapshot(p)
        assert snap["write_boundary_required"] is False, f"write_boundary_required True for: {p!r}"
        assert "MEMORY_WRITE_CANON_FREEZE" not in snap["domains"], (
            f"MEMORY_WRITE_CANON_FREEZE in domains for: {p!r} — got {snap['domains']}"
        )


def test_explicit_write_memory_still_triggers_boundary():
    """Explicit 'écris en mémoire' MUST still trigger has_memory_write_request."""
    assert has_memory_write_request("écris en mémoire ce résultat") is True
    assert has_memory_write_request("write memory with this data") is True
    assert has_memory_write_request("écris ce bloc en mémoire graphiti") is True


def test_explicit_graphiti_write_still_triggers_boundary():
    """Explicit graphiti write markers MUST still trigger has_memory_write_request."""
    # "write graphiti" is a direct early_write_boundary_marker
    assert has_memory_write_request("write graphiti node") is True
    assert has_memory_write_request("write graphiti") is True
    assert has_memory_write_request("graphiti memory update") is True  # "graphiti memory" marker


def test_explicit_canon_promotion_still_triggers_boundary():
    """Explicit canon/canonise markers MUST still trigger write boundary."""
    # "canonise" is a direct early_write_boundary_marker
    assert has_memory_write_request("canonise ce bloc en mémoire") is True
    assert has_memory_write_request("canoniser ce freeze") is True
    assert has_memory_write_request("memory_write_canon_freeze request") is True
    # Guard must also return NEGATIVE for explicit write instructions
    result = detect_readonly_runtime_state_intent("canonise ce freeze en mémoire")
    assert result["status"] == "NO_RUNTIME_STATE_READONLY_INTENT"


def test_8000_8012_parity_runtime_state_intent():
    """Live smoke: canonical prompt on 8000 must have readonly_intent_guard_packet PASS."""
    data = json.dumps({
        "message": _READONLY_PROMPT,
        "language": "fr",
        "session_id": "f22b_readonly_intent_guard_test",
    }).encode("utf-8")

    for port in [8000, 8012]:
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/brody/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            pytest.skip(f"Port {port} not reachable: {exc}")

        guard = payload.get("readonly_intent_guard_packet", {})
        assert guard.get("status") == "RUNTIME_STATE_READONLY_INTENT_PASS", (
            f"Port {port}: guard status wrong: {guard}"
        )
        assert guard.get("write_boundary_required") is False, (
            f"Port {port}: write_boundary_required is True"
        )

        # Boundary invariants must remain intact
        assert payload["decision_authority"] == "KX108_ONLY"
        assert payload["readonly"] is True
        assert payload["emits_act"] is False
        assert payload["memory_write"] is False
        assert payload["graphiti_write"] is False
        assert payload["kernel_mutation"] is False
        assert payload["x108_mutation"] is False

        # domain_raccord must NOT have MEMORY_WRITE_CANON_FREEZE
        tvs = payload.get("true_voice_snapshot", {})
        dr = tvs.get("domain_raccord_snapshot", {})
        assert "MEMORY_WRITE_CANON_FREEZE" not in dr.get("domains", []), (
            f"Port {port}: MEMORY_WRITE_CANON_FREEZE still in domains: {dr.get('domains')}"
        )
        assert dr.get("write_boundary_required") is False, (
            f"Port {port}: domain_raccord write_boundary_required is True"
        )
        assert "RUNTIME_STATE_READONLY" in dr.get("domains", []), (
            f"Port {port}: RUNTIME_STATE_READONLY not in domains: {dr.get('domains')}"
        )
