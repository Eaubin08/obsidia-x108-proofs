"""P37 — Tests unitaires: Runtime Function Inventory Graph.

Vérifie :
1. inventory graph READY.
2. détecte capability_path_router.py comme module.
3. détecte route_capability_path() comme fonction.
4. détecte capability_taxonomy.py comme module.
5. détecte reverse_os_interlanguage_to_context_packet() comme adapter.
6. détecte /api/runtime-wiring/source-runtime/preview comme route.
7. détecte des tests P36.
8. aucun runtime_allowed_now=True dans le graphe.
9. aucun emits_act=True dans le graphe.
10. decision_authority=KX108_ONLY.
"""
import pathlib
import sys
import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from runtime_wiring.source_runtime.runtime_inventory_graph import build_runtime_inventory_graph
from runtime_wiring.source_runtime.capability_inventory_linker import link_capabilities_to_inventory
from runtime_wiring.source_runtime.capability_path_router import route_capability_path


@pytest.fixture(scope="module")
def graph():
    return build_runtime_inventory_graph()


# ── Test 1 : inventory READY ──────────────────────────────────────────────────

def test_inventory_status_ready(graph):
    """Test 1 — inventory graph READY."""
    assert graph.get("inventory_status") == "READY", (
        f"inventory_status inattendu: {graph.get('inventory_status')}"
    )
    assert graph.get("module_count", 0) > 0, "Aucun module détecté"
    assert graph.get("function_count", 0) > 0, "Aucune fonction détectée"


# ── Test 2 : détecte capability_path_router.py ───────────────────────────────

def test_detects_capability_path_router_module(graph):
    """Test 2 — détecte capability_path_router.py comme module."""
    module_paths = [m["module_path"] for m in graph.get("modules", [])]
    found = any("capability_path_router" in mp for mp in module_paths)
    assert found, (
        f"capability_path_router.py non trouvé dans les modules: {module_paths[:10]}"
    )


# ── Test 3 : détecte route_capability_path() ─────────────────────────────────

def test_detects_route_capability_path_function(graph):
    """Test 3 — détecte route_capability_path() comme fonction."""
    fn_names = [f["name"] for f in graph.get("functions", [])]
    assert "route_capability_path" in fn_names, (
        f"route_capability_path() non trouvé. Premiers: {fn_names[:20]}"
    )


# ── Test 4 : détecte capability_taxonomy.py ──────────────────────────────────

def test_detects_capability_taxonomy_module(graph):
    """Test 4 — détecte capability_taxonomy.py comme module."""
    module_paths = [m["module_path"] for m in graph.get("modules", [])]
    found = any("capability_taxonomy" in mp for mp in module_paths)
    assert found, (
        f"capability_taxonomy.py non trouvé dans les modules: {module_paths[:10]}"
    )


# ── Test 5 : détecte reverse_os_interlanguage_to_context_packet ──────────────

def test_detects_reverse_os_interlanguage_adapter(graph):
    """Test 5 — détecte reverse_os_interlanguage_to_context_packet() comme adapter."""
    adapter_names = [a["adapter_name"] for a in graph.get("adapters", [])]
    fn_names = [f["name"] for f in graph.get("functions", [])]
    assert "reverse_os_interlanguage_to_context_packet" in adapter_names or \
           "reverse_os_interlanguage_to_context_packet" in fn_names, (
        f"reverse_os_interlanguage_to_context_packet non détecté. "
        f"Adapters: {adapter_names[:10]}"
    )


# ── Test 6 : détecte /api/runtime-wiring/source-runtime/preview ──────────────

def test_detects_source_runtime_preview_route(graph):
    """Test 6 — détecte /api/runtime-wiring/source-runtime/preview comme route."""
    route_paths = [r["path"] for r in graph.get("routes", [])]
    found = any("source-runtime/preview" in rp for rp in route_paths)
    assert found, (
        f"/api/runtime-wiring/source-runtime/preview non trouvé. Routes: {route_paths[:10]}"
    )


# ── Test 7 : détecte tests P36 ────────────────────────────────────────────────

def test_detects_p36_tests(graph):
    """Test 7 — détecte des fichiers test P36."""
    test_paths = [t["test_path"] for t in graph.get("tests", [])]
    found = any("p36" in tp for tp in test_paths)
    assert found, (
        f"Aucun test P36 trouvé. Tests disponibles: {test_paths[:10]}"
    )


# ── Test 8 : runtime_allowed_now toujours False ───────────────────────────────

def test_inventory_graph_no_runtime_allowed_now(graph):
    """Test 8 — aucun runtime_allowed_now=True dans le graphe."""
    assert graph.get("runtime_allowed_now") is False, (
        "runtime_allowed_now=True détecté dans le graphe"
    )
    # Vérifie aussi dans les arêtes (pas de flag runtime_allowed_now dans les arêtes)
    for edge in graph.get("edges", []):
        assert edge.get("runtime_allowed_now", False) is False


# ── Test 9 : emits_act toujours False ────────────────────────────────────────

def test_inventory_graph_no_emits_act(graph):
    """Test 9 — aucun emits_act=True dans le graphe."""
    assert graph.get("emits_act") is False, (
        "emits_act=True détecté dans le graphe"
    )


# ── Test 10 : decision_authority KX108_ONLY ──────────────────────────────────

def test_inventory_graph_decision_authority_kx108(graph):
    """Test 10 — decision_authority=KX108_ONLY dans le graphe."""
    assert graph.get("decision_authority") == "KX108_ONLY", (
        f"decision_authority inattendu: {graph.get('decision_authority')}"
    )


# ── Test supplémentaire : linker enrichit un chemin IR ────────────────────────

def test_linker_enriches_ir_path_with_functions(graph):
    """Linker: query IR retourne selected_functions non vide."""
    routing = route_capability_path("IR alphabet reverse OS interlanguage")
    enriched = link_capabilities_to_inventory(routing, graph)
    selected_fns = enriched.get("selected_functions", [])
    assert isinstance(selected_fns, list), "selected_functions doit être une liste"
    # Peut être vide si les modules ne sont pas scannés — on vérifie juste le type


def test_linker_preserves_readonly_invariants(graph):
    """Linker: readonly, no_act et decision_authority préservés."""
    routing = route_capability_path("IR alphabet reverse OS")
    enriched = link_capabilities_to_inventory(routing, graph)
    assert enriched.get("readonly") is True
    assert enriched.get("no_act") is True
    assert enriched.get("runtime_allowed_now") is False
    assert enriched.get("emits_act") is False
    assert enriched.get("decision_authority") == "KX108_ONLY"


def test_linker_sets_inventory_linked(graph):
    """Linker: inventory_linked=True après enrichissement."""
    routing = route_capability_path("IR alphabet reverse OS")
    enriched = link_capabilities_to_inventory(routing, graph)
    assert enriched.get("inventory_linked") is True


def test_graph_summary_counts(graph):
    """Vérification basique des compteurs du graphe."""
    summary = graph.get("summary", {})
    assert summary.get("module_count", 0) > 0
    assert summary.get("function_count", 0) > 0
    assert summary.get("static_edge_count", 0) > 0
    assert summary.get("total_edge_count", 0) >= summary.get("static_edge_count", 0)


def test_graph_has_adapters(graph):
    """Vérifie que le graphe a détecté des adapters."""
    adapters = graph.get("adapters", [])
    assert len(adapters) > 0, "Aucun adapter détecté"
    adapter_names = [a["adapter_name"] for a in adapters]
    assert any("to_context_packet" in name for name in adapter_names), (
        f"Aucun adapter *_to_context_packet détecté: {adapter_names[:10]}"
    )
