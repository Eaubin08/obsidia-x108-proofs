"""RED tranche 1 — negative authority contract and isolation of the future app/knowledge/b8 package
(spec header, §1, §11; Sentinel V0: no app.cognition import)."""
from __future__ import annotations

import ast

from tests.b8.conftest import B8_PACKAGE_DIR

FORBIDDEN_IMPORT_PREFIXES = ("app.cognition", "app.harness", "apps", "periphery", "graphiti", "graphiti_core",
                             "neo4j", "requests", "httpx", "urllib", "socket", "http", "aiohttp", "subprocess")
FORBIDDEN_NAMES = ("binder", "kx108", "executor", "memory_writer", "write_memory", "apply_to_neo4j")


def _sources():
    files = sorted(B8_PACKAGE_DIR.rglob("*.py"))
    assert files, f"missing B8 production package at {B8_PACKAGE_DIR}"
    return {f: f.read_text(encoding="utf-8") for f in files}


def production_imports():
    mods = set()
    for path, src in _sources().items():
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Import):
                mods.update(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                mods.add(node.module)
    return mods


def test_boundary_flags_are_hard_false(b8):
    boundary = b8.BOUNDARY
    assert boundary["memory_write"] is False
    assert boundary["emits_act"] is False
    assert boundary["kernel_mutation"] is False
    assert boundary["decision_authority"] == "KX108_ONLY"
    assert boundary["promotion_authority"] == "B8_CANONICAL_TRANSITION_GATE"
    assert boundary["kx108_knowledge_promotion_role"] == "NONE"
    try:
        boundary["memory_write"] = True
    except TypeError:
        pass
    assert b8.BOUNDARY["memory_write"] is False


def test_package_imports_no_runtime_authority_or_network():
    bad = sorted(m for m in production_imports() if m.split(".")[0] in {p.split(".")[0] for p in FORBIDDEN_IMPORT_PREFIXES}
                 and any(m == p or m.startswith(p + ".") for p in FORBIDDEN_IMPORT_PREFIXES))
    assert bad == []


def test_package_references_no_authority_names():
    for path, src in _sources().items():
        names = {n.id.lower() for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Name)}
        names |= {n.attr.lower() for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Attribute)}
        assert not names & set(FORBIDDEN_NAMES), (path, names & set(FORBIDDEN_NAMES))


def test_package_has_no_dynamic_execution_or_io():
    for path, src in _sources().items():
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id not in {"eval", "exec", "compile", "open", "__import__"}, (path, node.func.id)
