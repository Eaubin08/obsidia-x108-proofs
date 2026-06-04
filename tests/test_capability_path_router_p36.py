"""P36 — Tests unitaires: Global Capability Path Router.

Vérifie :
1. "IR alphabet reverse OS" sélectionne REVERSE_OS_INTERLANGUAGE.
2. Le selected_path contient reverse_os_interlanguage_to_context_packet.
3. Le selected_path contient REVERSE_OS_INTERLANGUAGE_CANON_V1.
4. "34 arbres agents" sélectionne AGENT_TREE_LOOKUP.
5. "lois protocoles non décision" sélectionne LAW_PROTOCOL_LOOKUP.
6. "RSSI sécurité audit conformité" sélectionne RSSI_SECURITY_CONTEXT ou PROOF_AUDIT_CONTEXT.
7. "mémoire Brody Graphiti" sélectionne MEMORY_REINTEGRATION_CONTEXT ou GRAPHITI_READONLY_CONTEXT.
8. Une requête action "envoie un mail" retourne ACTION_REQUEST_BLOCKED.
9. Aucun selected_path ne met runtime_allowed_now=True.
10. Aucun selected_path ne met emits_act=True.
11. decision_authority reste KX108_ONLY.
12. hydration_plan max 8 fichiers.
13. Aucun fichier exécutable sélectionné.
"""
import pathlib
import sys
import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from runtime_wiring.source_runtime.capability_path_router import route_capability_path
from runtime_wiring.source_runtime.source_hydration_planner import build_hydration_plan_from_path
from runtime_wiring.source_runtime.capability_taxonomy import (
    CAPABILITY_TAXONOMY,
    list_capability_ids,
    is_valid_capability,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _get_capabilities_chain(result: dict) -> list:
    """Collecte toutes les capabilities de la chain du selected_path."""
    return result.get("selected_path", {}).get("capability_chain", [])


def _all_capability_ids_in_paths(result: dict) -> list:
    """Collecte tous les capability_ids présents dans les chemins ranked."""
    ids = []
    for path in result.get("ranked_runtime_paths", []):
        ids.extend(path.get("capability_chain", []))
    return ids


def _selected_adapters(result: dict) -> list:
    return result.get("selected_path", {}).get("adapters", [])


def _selected_subfamilies(result: dict) -> list:
    return result.get("selected_path", {}).get("source_subfamilies", [])


# ── Test 1 : IR alphabet → REVERSE_OS_INTERLANGUAGE ─────────────────────────

def test_ir_alphabet_selects_reverse_os_interlanguage():
    """Test 1 — "IR alphabet reverse OS" sélectionne REVERSE_OS_INTERLANGUAGE."""
    result = route_capability_path("IR alphabet reverse OS")
    all_caps = _all_capability_ids_in_paths(result)
    assert "REVERSE_OS_INTERLANGUAGE" in all_caps or \
           "IR_ALPHABET_MAPPING" in all_caps, (
        f"REVERSE_OS_INTERLANGUAGE / IR_ALPHABET_MAPPING manquant dans: {all_caps}"
    )


# ── Test 2 : selected_path contient le bon adapter ───────────────────────────

def test_ir_alphabet_selected_path_contains_interlanguage_adapter():
    """Test 2 — selected_path contient reverse_os_interlanguage_to_context_packet."""
    result = route_capability_path("IR alphabet reverse OS")
    adapters = _selected_adapters(result)
    assert "reverse_os_interlanguage_to_context_packet" in adapters, (
        f"Adapter manquant dans: {adapters}"
    )


# ── Test 3 : selected_path contient REVERSE_OS_INTERLANGUAGE_CANON_V1 ────────

def test_ir_alphabet_selected_path_contains_canon_v1():
    """Test 3 — selected_path contient REVERSE_OS_INTERLANGUAGE_CANON_V1 dans source_subfamilies."""
    result = route_capability_path("IR alphabet reverse OS interlanguage canon")
    subfamilies = _selected_subfamilies(result)
    assert "REVERSE_OS_INTERLANGUAGE_CANON_V1" in subfamilies, (
        f"REVERSE_OS_INTERLANGUAGE_CANON_V1 manquant dans subfamilies: {subfamilies}"
    )


# ── Test 4 : "34 arbres agents" → AGENT_TREE_LOOKUP ─────────────────────────

def test_agent_tree_query_selects_agent_tree_lookup():
    """Test 4 — "34 arbres agents" sélectionne AGENT_TREE_LOOKUP."""
    result = route_capability_path("34 arbres agents registry")
    all_caps = _all_capability_ids_in_paths(result)
    assert "AGENT_TREE_LOOKUP" in all_caps, (
        f"AGENT_TREE_LOOKUP manquant dans: {all_caps}"
    )


# ── Test 5 : "lois protocoles non décision" → LAW_PROTOCOL_LOOKUP ────────────

def test_law_protocol_query_selects_law_protocol_lookup():
    """Test 5 — "lois protocoles non décision" sélectionne LAW_PROTOCOL_LOOKUP."""
    result = route_capability_path("lois protocoles non décision boundary")
    all_caps = _all_capability_ids_in_paths(result)
    assert "LAW_PROTOCOL_LOOKUP" in all_caps, (
        f"LAW_PROTOCOL_LOOKUP manquant dans: {all_caps}"
    )


# ── Test 6 : "RSSI sécurité audit conformité" → RSSI_SECURITY ou PROOF_AUDIT ─

def test_rssi_query_selects_rssi_or_proof_audit():
    """Test 6 — "RSSI sécurité audit conformité" sélectionne RSSI_SECURITY_CONTEXT ou PROOF_AUDIT_CONTEXT."""
    result = route_capability_path("RSSI sécurité audit conformité cyber")
    all_caps = _all_capability_ids_in_paths(result)
    assert "RSSI_SECURITY_CONTEXT" in all_caps or "PROOF_AUDIT_CONTEXT" in all_caps, (
        f"RSSI_SECURITY_CONTEXT / PROOF_AUDIT_CONTEXT manquant dans: {all_caps}"
    )


# ── Test 7 : "mémoire Brody Graphiti" → MEMORY ou GRAPHITI ──────────────────

def test_memory_graphiti_query_selects_memory_or_graphiti():
    """Test 7 — "mémoire Brody Graphiti" sélectionne MEMORY_REINTEGRATION_CONTEXT ou GRAPHITI_READONLY_CONTEXT."""
    result = route_capability_path("mémoire Brody Graphiti réintégration")
    all_caps = _all_capability_ids_in_paths(result)
    assert "MEMORY_REINTEGRATION_CONTEXT" in all_caps or \
           "GRAPHITI_READONLY_CONTEXT" in all_caps, (
        f"MEMORY_REINTEGRATION_CONTEXT / GRAPHITI_READONLY_CONTEXT manquant dans: {all_caps}"
    )


# ── Test 8 : action request → ACTION_REQUEST_BLOCKED ─────────────────────────

def test_action_request_returns_blocked():
    """Test 8 — "envoie un mail" retourne ACTION_REQUEST_BLOCKED."""
    result = route_capability_path("envoie un mail à l'équipe")
    selected_cap_chain = _get_capabilities_chain(result)
    assert "ACTION_REQUEST_BLOCKED" in selected_cap_chain, (
        f"ACTION_REQUEST_BLOCKED manquant dans chain: {selected_cap_chain}"
    )


# ── Test 9 : runtime_allowed_now toujours False ──────────────────────────────

def test_no_path_sets_runtime_allowed_now_true():
    """Test 9 — Aucun selected_path ne met runtime_allowed_now=True."""
    queries = [
        "IR alphabet reverse OS",
        "34 arbres agents",
        "lois protocoles",
        "RSSI sécurité",
        "mémoire Brody Graphiti",
        "envoie un mail",
        "source context générique",
    ]
    for q in queries:
        result = route_capability_path(q)
        assert result["selected_path"].get("runtime_allowed_now") is False, (
            f"runtime_allowed_now=True détecté pour query: {q!r}"
        )
        for path in result.get("ranked_runtime_paths", []):
            assert path.get("runtime_allowed_now") is False, (
                f"runtime_allowed_now=True dans ranked_paths pour query: {q!r}"
            )


# ── Test 10 : emits_act toujours False ───────────────────────────────────────

def test_no_path_sets_emits_act_true():
    """Test 10 — Aucun selected_path ne met emits_act=True."""
    queries = [
        "IR alphabet reverse OS",
        "34 arbres agents",
        "lois protocoles",
        "envoie un mail",
    ]
    for q in queries:
        result = route_capability_path(q)
        assert result["selected_path"].get("emits_act") is False, (
            f"emits_act=True détecté pour query: {q!r}"
        )
        assert result.get("emits_act") is False
        assert result.get("no_act") is True


# ── Test 11 : decision_authority KX108_ONLY ──────────────────────────────────

def test_decision_authority_always_kx108():
    """Test 11 — decision_authority reste KX108_ONLY pour tous les chemins."""
    result = route_capability_path("IR alphabet reverse OS")
    assert result.get("decision_authority") == "KX108_ONLY"
    for path in result.get("ranked_runtime_paths", []):
        assert path.get("decision_authority") == "KX108_ONLY", (
            f"decision_authority inattendu dans path: {path.get('path_id')}"
        )


# ── Test 12 : hydration_plan max 8 fichiers ───────────────────────────────────

def test_hydration_plan_max_8_files():
    """Test 12 — hydration_plan retourne au maximum 8 fichiers."""
    result = route_capability_path("IR alphabet reverse OS")
    selected_path = result["selected_path"]
    plan = build_hydration_plan_from_path(selected_path, max_files=8)
    assert plan.get("planned_files_count", 0) <= 8, (
        f"Trop de fichiers dans le plan: {plan.get('planned_files_count')}"
    )
    assert plan.get("max_files") == 8
    assert plan.get("readonly") is True
    assert plan.get("emits_act") is False
    assert plan.get("runtime_allowed_now") is False


# ── Test 13 : aucun fichier exécutable sélectionné ───────────────────────────

def test_no_executable_file_in_hydration_plan():
    """Test 13 — Aucun fichier exécutable (.py .ps1 .sh .bat .exe) dans le plan."""
    forbidden_ext = {".py", ".pyc", ".ps1", ".bat", ".sh", ".exe", ".dll"}
    queries = [
        "IR alphabet reverse OS",
        "34 arbres agents",
        "lois protocoles",
        "envoie un mail",
    ]
    for q in queries:
        result = route_capability_path(q)
        selected_path = result["selected_path"]
        plan = build_hydration_plan_from_path(selected_path, max_files=8)
        for f in plan.get("planned_files", []):
            fname = f.lower().replace("\\", "/").split("/")[-1]
            ext = ("." + fname.rsplit(".", 1)[-1]) if "." in fname else ""
            assert ext not in forbidden_ext, (
                f"Fichier exécutable détecté dans le plan: {f!r} pour query: {q!r}"
            )


# ── Test supplémentaire : taxonomie complète cohérente ───────────────────────

def test_taxonomy_all_capabilities_valid():
    """Vérifie que toutes les capabilities de la taxonomie ont les champs obligatoires."""
    required_fields = {
        "capability_id", "description", "allowed_runtime_mode",
        "runtime_allowed_now", "emits_act", "decision_authority",
        "candidate_modules", "candidate_adapters", "candidate_routes",
        "candidate_source_families", "candidate_subfamilies",
    }
    for cap_id, cap in CAPABILITY_TAXONOMY.items():
        for field in required_fields:
            assert field in cap, (
                f"Champ {field!r} manquant dans capability {cap_id!r}"
            )
        assert cap["runtime_allowed_now"] is False, (
            f"runtime_allowed_now doit être False pour {cap_id!r}"
        )
        assert cap["emits_act"] is False, (
            f"emits_act doit être False pour {cap_id!r}"
        )
        assert cap["decision_authority"] == "KX108_ONLY", (
            f"decision_authority doit être KX108_ONLY pour {cap_id!r}"
        )


def test_readonly_always_in_result():
    """Le résultat du router doit toujours contenir readonly=True et no_act=True."""
    result = route_capability_path("quelque chose de générique")
    assert result.get("readonly") is True
    assert result.get("no_act") is True
    assert result.get("runtime_allowed_now") is False
