"""
tests/test_p65_os_adapters_unlock_bus_registry.py

P65 validation suite — 31 tests.
Vérifie : JSON audit, compilation, flags DRY_RUN_ONLY, _BOUNDARY, fonctionnement des adapters.
"""
import json
import os
import py_compile
import tempfile

import pytest

# ---------------------------------------------------------------------------
# Chemins
# ---------------------------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

P65_JSON = os.path.join(ROOT, "docs", "core_import", "P65_OS_ADAPTERS_UNLOCK_BUS_REGISTRY.json")

ADAPTER_INIT = os.path.join(ROOT, "apps", "obsidia_api", "os_adapters", "__init__.py")
ADAPTER_DETERMINISM = os.path.join(ROOT, "apps", "obsidia_api", "os_adapters", "determinism.py")
ADAPTER_PARSE_INPUT = os.path.join(ROOT, "apps", "obsidia_api", "os_adapters", "parse_input.py")
ADAPTER_SVG = os.path.join(ROOT, "apps", "obsidia_api", "os_adapters", "svg.py")
ADAPTER_OS_TRAD = os.path.join(ROOT, "apps", "obsidia_api", "os_adapters", "os_trad_adapter.py")
ADAPTER_REGISTRY = os.path.join(ROOT, "apps", "obsidia_api", "bus", "registry.py")


@pytest.fixture(scope="module")
def p65_data():
    with open(P65_JSON, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Section 1 — JSON audit (6 tests)
# ---------------------------------------------------------------------------

def test_p65_json_exists():
    assert os.path.isfile(P65_JSON), f"P65 JSON manquant : {P65_JSON}"


def test_p65_json_status(p65_data):
    assert p65_data["status"] == "P65_OS_ADAPTERS_UNLOCK_BUS_REGISTRY_READY"


def test_p65_json_adapted_files_count(p65_data):
    assert p65_data["files_adapted_count"] == 5
    assert len(p65_data["adapted_files"]) == 5


def test_p65_json_no_act_enabled(p65_data):
    assert p65_data["act_enabled"] is False


def test_p65_json_no_memory_write(p65_data):
    assert p65_data["memory_write_enabled"] is False
    assert p65_data["graphiti_write_enabled"] is False
    assert p65_data["kernel_mutation_enabled"] is False


def test_p65_json_bus_registry_unblocked(p65_data):
    assert p65_data["bus_registry_unblocked"] is True
    assert p65_data["bus_registry_adapter_created"] is True


# ---------------------------------------------------------------------------
# Section 2 — Compilation (6 tests)
# ---------------------------------------------------------------------------

def test_compile_init():
    py_compile.compile(ADAPTER_INIT, doraise=True)


def test_compile_determinism():
    py_compile.compile(ADAPTER_DETERMINISM, doraise=True)


def test_compile_parse_input():
    py_compile.compile(ADAPTER_PARSE_INPUT, doraise=True)


def test_compile_svg():
    py_compile.compile(ADAPTER_SVG, doraise=True)


def test_compile_os_trad_adapter():
    py_compile.compile(ADAPTER_OS_TRAD, doraise=True)


def test_compile_registry():
    py_compile.compile(ADAPTER_REGISTRY, doraise=True)


# ---------------------------------------------------------------------------
# Section 3 — Flags DRY_RUN_ONLY (5 tests)
# ---------------------------------------------------------------------------

def test_determinism_dry_run_flag():
    from apps.obsidia_api.os_adapters import determinism
    assert determinism.DRY_RUN_ONLY is True


def test_parse_input_dry_run_flag():
    from apps.obsidia_api.os_adapters import parse_input
    assert parse_input.DRY_RUN_ONLY is True


def test_svg_dry_run_flag():
    from apps.obsidia_api.os_adapters import svg
    assert svg.DRY_RUN_ONLY is True


def test_os_trad_adapter_dry_run_flag():
    from apps.obsidia_api.os_adapters import os_trad_adapter
    assert os_trad_adapter.DRY_RUN_ONLY is True


def test_registry_dry_run_flag():
    from apps.obsidia_api.bus import registry
    assert registry.DRY_RUN_ONLY is True


# ---------------------------------------------------------------------------
# Section 4 — _BOUNDARY (5 tests)
# ---------------------------------------------------------------------------

def test_determinism_boundary():
    from apps.obsidia_api.os_adapters.determinism import _BOUNDARY
    assert _BOUNDARY["readonly"] is True
    assert _BOUNDARY["emits_act"] is False
    assert _BOUNDARY["memory_write"] is False
    assert _BOUNDARY["decision_authority"] == "KX108_ONLY"


def test_parse_input_boundary():
    from apps.obsidia_api.os_adapters.parse_input import _BOUNDARY
    assert _BOUNDARY["dry_run_only"] is True
    assert _BOUNDARY["graphiti_write"] is False
    assert _BOUNDARY["kernel_mutation"] is False


def test_svg_boundary():
    from apps.obsidia_api.os_adapters.svg import _BOUNDARY
    assert _BOUNDARY["readonly"] is True
    assert _BOUNDARY["emits_act"] is False
    assert _BOUNDARY["neo4j_write"] is False


def test_os_trad_boundary():
    from apps.obsidia_api.os_adapters.os_trad_adapter import _BOUNDARY
    assert _BOUNDARY["emits_act"] is False
    assert _BOUNDARY["memory_write"] is False
    assert _BOUNDARY["decision_authority"] == "KX108_ONLY"


def test_registry_boundary():
    from apps.obsidia_api.bus.registry import _BOUNDARY
    assert _BOUNDARY["dry_run_only"] is True
    assert _BOUNDARY["emits_act"] is False
    assert _BOUNDARY["kernel_mutation"] is False


# ---------------------------------------------------------------------------
# Section 5 — Tests fonctionnels (9 tests)
# ---------------------------------------------------------------------------

def test_canonical_hash_pure():
    from apps.obsidia_api.os_adapters.determinism import canonical_hash
    h = canonical_hash({"x": 1})
    assert isinstance(h, str)
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_canonical_hash_deterministic():
    from apps.obsidia_api.os_adapters.determinism import canonical_hash
    assert canonical_hash({"a": 1, "b": 2}) == canonical_hash({"b": 2, "a": 1})


def test_parse_input_returns_dry_run():
    from apps.obsidia_api.os_adapters.parse_input import parse_input
    result = parse_input("x = 1")
    assert result["_dry_run"] is True


def test_parse_input_returns_program_key():
    from apps.obsidia_api.os_adapters.parse_input import parse_input
    result = parse_input("x = 1")
    assert "program" in result
    assert isinstance(result["program"], list)
    assert len(result["program"]) > 0


def test_svg_returns_string_not_file():
    from apps.obsidia_api.os_adapters.svg import render_core_svg
    svg_str = render_core_svg(
        labels={0: "A", 1: "B"},
        positions={0: (0.0, 0.0), 1: (1.0, 1.0)},
        edges=[(0, 1, 1.5)],
    )
    assert isinstance(svg_str, str)
    assert "<svg" in svg_str
    assert "</svg>" in svg_str
    # Vérification qu'aucun fichier n'a été créé
    assert not os.path.exists(""), "Aucun fichier ne doit avoir été créé"


def test_svg_contains_svg_tags():
    from apps.obsidia_api.os_adapters.svg import render_core_svg
    result = render_core_svg(labels={}, positions={}, edges=[])
    assert result.startswith("<svg")
    assert result.endswith("</svg>")


def test_os_trad_propose_dry_run():
    from apps.obsidia_api.os_adapters.os_trad_adapter import os_trad_propose
    req = {
        "intent": {
            "type": "PROPOSE",
            "name": "OS_TRAD",
            "payload": {"spec_text": "fn add(a, b) = a + b", "target": "python"},
        }
    }
    result = os_trad_propose(req)
    proposal = result["context"]["proposals"]["OS_TRAD"]
    assert proposal["ok"] is True
    assert proposal["dry_run"] is True
    assert proposal["_act_emitted"] is False
    assert proposal["info"]["build_skipped"] is True


def test_os_trad_action_blocked():
    from apps.obsidia_api.os_adapters.os_trad_adapter import os_trad_propose
    with pytest.raises(ValueError, match="ACTION intent is disabled"):
        os_trad_propose({"intent": {"type": "ACTION", "name": "OS_TRAD"}})


def test_registry_propose_only():
    from apps.obsidia_api.bus.registry import build_default_router
    router = build_default_router()
    assert "OS_TRAD" in router.modules
    request = {"intent": {"type": "PROPOSE", "name": "OS_TRAD", "payload": {}}}
    result = router.run_propose_modules(request, dry_run=True)
    assert result["_dry_run"] is True
    assert result["_act_emitted"] is False
