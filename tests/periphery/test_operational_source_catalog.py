"""
Tests for periphery.agents.operational_source_catalog — Wave 002.

PHASE: PYTHON_OPERATIONAL_AGENT_SYSTEM_WAVE002
AUTHORITY: NON_SOVEREIGN — no agent invoked, no model called, no memory written.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import tempfile
from pathlib import Path

import pytest

from periphery.agents.operational_source_catalog import (
    _EXPECTED_ENTRY_COUNT,
    _MANIFEST_REL,
    _SUPPORTED_SCHEMA,
    _manifest_path,
    _manifest_rel_path,
    get_wave002_provenance,
    load_operational_manifest,
)


# ── Helpers ───────────────────────────────────────────────────────────────────


@contextlib.contextmanager
def _reset_cache():
    """Reset module caches and restore on exit."""
    import periphery.agents.operational_source_catalog as mod
    orig = (mod._CACHE, mod._CACHE_SHA)
    mod._CACHE = None
    mod._CACHE_SHA = ""
    try:
        yield mod
    finally:
        mod._CACHE, mod._CACHE_SHA = orig


@contextlib.contextmanager
def _tampered(tampered: dict):
    """Write tampered manifest to temp file, patch _manifest_path, reset cache."""
    import periphery.agents.operational_source_catalog as mod
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as tmp:
        json.dump(tampered, tmp)
        tmp_path = Path(tmp.name)
    orig_fn = mod._manifest_path
    orig = (mod._CACHE, mod._CACHE_SHA)
    mod._manifest_path = lambda: tmp_path  # type: ignore[assignment]
    mod._CACHE = None
    mod._CACHE_SHA = ""
    try:
        yield mod
    finally:
        mod._manifest_path = orig_fn  # type: ignore[assignment]
        mod._CACHE, mod._CACHE_SHA = orig
        tmp_path.unlink(missing_ok=True)


# ── Positive tests ────────────────────────────────────────────────────────────


def test_w2_001_manifest_file_exists():
    """operational_source_catalog.json exists at the expected path."""
    assert _manifest_path().exists(), f"Manifest missing: {_manifest_rel_path()}"


def test_w2_002_manifest_loads():
    """load_operational_manifest() succeeds without raising."""
    m = load_operational_manifest()
    assert isinstance(m, dict)


def test_w2_003_schema_version():
    """Manifest schema_version matches _SUPPORTED_SCHEMA."""
    m = load_operational_manifest()
    assert m["schema_version"] == _SUPPORTED_SCHEMA


def test_w2_004_entry_count():
    """Manifest contains exactly _EXPECTED_ENTRY_COUNT (167) entries."""
    m = load_operational_manifest()
    assert len(m["entries"]) == _EXPECTED_ENTRY_COUNT == 167


def test_w2_005_authority_non_sovereign():
    """Manifest declares authority=NON_SOVEREIGN."""
    m = load_operational_manifest()
    assert m["authority"] == "NON_SOVEREIGN"


def test_w2_006_readonly_flag():
    """Manifest declares readonly=True."""
    m = load_operational_manifest()
    assert m["readonly"] is True


def test_w2_007_no_execution_flags():
    """Manifest declares can_decide=False, can_act=False, emits_act=False, memory_write=False."""
    m = load_operational_manifest()
    assert m["can_decide"] is False
    assert m["can_act"] is False
    assert m["emits_act"] is False
    assert m["memory_write"] is False


def test_w2_008_paths_unique():
    """All path values in manifest entries are unique."""
    m = load_operational_manifest()
    paths = [e["path"] for e in m["entries"]]
    assert len(paths) == len(set(paths)), "Duplicate paths in manifest"


def test_w2_009_all_files_exist():
    """All 167 files referenced in the manifest exist on disk."""
    m = load_operational_manifest()
    repo = _manifest_path().parent.parent.parent
    missing = [
        e["path"] for e in m["entries"]
        if not (repo / e["path"]).exists()
    ]
    assert missing == [], f"Missing files: {missing}"


def test_w2_010_all_sha256_correct():
    """SHA256 of all 167 files matches the manifest record."""
    m = load_operational_manifest()
    repo = _manifest_path().parent.parent.parent
    mismatched = []
    for entry in m["entries"]:
        p = repo / entry["path"]
        if not p.exists():
            continue
        actual = hashlib.sha256(p.read_bytes()).hexdigest()
        if actual != entry["sha256"]:
            mismatched.append(entry["path"])
    assert mismatched == [], f"SHA256 mismatches: {mismatched}"


def test_w2_011_groups_present():
    """Manifest groups field is non-empty and contains expected categories."""
    m = load_operational_manifest()
    groups = m.get("groups", [])
    assert len(groups) >= 5, f"Expected at least 5 groups, got {len(groups)}"
    assert any("REGROUPEMENTS_COHERENCE" in g for g in groups)
    assert "GROUP_MODULES_A1_A24" in groups
    assert any("CANONIQUES" in g for g in groups)


def test_w2_012_all_entries_have_required_fields():
    """Every manifest entry has path, sha256, file_type, group, relation_type."""
    m = load_operational_manifest()
    required = {"path", "sha256", "file_type", "group", "relation_type"}
    for entry in m["entries"]:
        missing = required - set(entry.keys())
        assert not missing, f"Entry {entry.get('path')!r} missing fields: {missing}"


def test_w2_013_no_path_escape():
    """No entry path escapes the repository root."""
    m = load_operational_manifest()
    repo = _manifest_path().parent.parent.parent.resolve()
    for entry in m["entries"]:
        abs_p = (repo / entry["path"]).resolve()
        assert str(abs_p).startswith(str(repo)), (
            f"Path escape: {entry['path']}"
        )


def test_w2_014_immutable_return():
    """load_operational_manifest() returns a new copy each call; internal cache unchanged."""
    import periphery.agents.operational_source_catalog as mod
    m1 = load_operational_manifest()
    original_count = len(m1["entries"])
    m1["entries"].clear()
    m1["INJECTED"] = True
    assert mod._CACHE is not None
    assert len(mod._CACHE["entries"]) == original_count
    assert "INJECTED" not in mod._CACHE
    m2 = load_operational_manifest()
    assert len(m2["entries"]) == original_count
    assert "INJECTED" not in m2


def test_w2_015_two_calls_return_independent_copies():
    """Two successive calls return independent dict objects."""
    m1 = load_operational_manifest()
    m2 = load_operational_manifest()
    assert m1 is not m2
    assert m1["entries"] is not m2["entries"]


def test_w2_016_cold_start_provenance():
    """get_wave002_provenance() works on cold start (no explicit manifest call)."""
    with _reset_cache():
        prov = get_wave002_provenance()
        assert prov["files_validated"] is True
        assert prov["entry_count"] == 167
        assert prov["authority"] == "NON_SOVEREIGN"
        assert prov["readonly"] is True
        assert prov["can_decide"] is False
        assert prov["can_act"] is False
        assert prov["emits_act"] is False
        assert prov["memory_write"] is False
        assert len(prov["groups"]) >= 5


def test_w2_017_manifest_system_and_wave():
    """Manifest declares system=PYTHON_OPERATIONAL_AGENT_SYSTEM and correct wave."""
    m = load_operational_manifest()
    assert m["system"] == "PYTHON_OPERATIONAL_AGENT_SYSTEM"
    assert m["wave"] == "AGENTS_FILE_WIRING_WAVE_002"


def test_w2_018_modules_a1_a24_all_present():
    """All 24 module spec documents (A01–A24) are in the manifest."""
    m = load_operational_manifest()
    a1_a24 = [e for e in m["entries"] if e["group"] == "GROUP_MODULES_A1_A24"]
    assert len(a1_a24) == 24, f"Expected 24 A01-A24 entries, got {len(a1_a24)}"


def test_w2_019_groupe05_members_present():
    """GROUPE_05 Agents_Infrastructure_Tools entries are catalogued."""
    m = load_operational_manifest()
    g5 = [e for e in m["entries"] if "GROUPE_05" in e["group"]]
    assert len(g5) >= 70, f"Expected ≥70 GROUPE_05 entries, got {len(g5)}"


def test_w2_020_agent_domain_integrator_in_manifest():
    """agent_domain_integrator.py is present in the manifest."""
    m = load_operational_manifest()
    paths = {e["path"] for e in m["entries"]}
    assert "periphery/agents/agent_domain_integrator.py" in paths


def test_w2_021_no_memory_write_in_loader():
    """load_operational_manifest source code contains no memory write calls."""
    import inspect as _inspect
    import periphery.agents.operational_source_catalog as mod
    src = _inspect.getsource(mod.load_operational_manifest)
    for forbidden in ("graphiti", "neo4j", "memory.write", "append_memory"):
        assert forbidden not in src.lower(), (
            f"Memory write {forbidden!r} in load_operational_manifest"
        )


def test_w2_022_no_model_call_in_loader():
    """load_operational_manifest source code contains no LLM/model calls."""
    import inspect as _inspect
    import periphery.agents.operational_source_catalog as mod
    src = _inspect.getsource(mod.load_operational_manifest)
    for forbidden in ("anthropic", "openai", "client.messages", "llm.invoke"):
        assert forbidden not in src.lower(), (
            f"Model call {forbidden!r} in load_operational_manifest"
        )


# ── Negative tests ────────────────────────────────────────────────────────────


def test_w2_023_negative_bad_schema():
    """load_operational_manifest raises ValueError when schema_version is wrong."""
    base = load_operational_manifest()
    bad = json.loads(json.dumps(base))
    bad["schema_version"] = "9.9"
    with _tampered(bad):
        with pytest.raises(ValueError) as exc_info:
            load_operational_manifest()
        assert "UNSUPPORTED_SCHEMA" in str(exc_info.value)


def test_w2_024_negative_wrong_entry_count():
    """load_operational_manifest raises ValueError when entry count is wrong."""
    base = load_operational_manifest()
    bad = json.loads(json.dumps(base))
    bad["entries"] = bad["entries"][:10]
    with _tampered(bad):
        with pytest.raises(ValueError) as exc_info:
            load_operational_manifest()
        assert "ENTRY_COUNT" in str(exc_info.value)


def test_w2_025_negative_missing_file():
    """load_operational_manifest raises ValueError when a referenced file is missing."""
    base = load_operational_manifest()
    bad = json.loads(json.dumps(base))
    bad["entries"][0]["path"] = "periphery/agents/NONEXISTENT_WAVE002_XYZ.md"
    with _tampered(bad):
        with pytest.raises(ValueError) as exc_info:
            load_operational_manifest()
        assert "MISSING_FILES" in str(exc_info.value)


def test_w2_026_negative_sha256_mismatch():
    """load_operational_manifest raises ValueError when a SHA256 is wrong."""
    base = load_operational_manifest()
    bad = json.loads(json.dumps(base))
    bad["entries"][0]["sha256"] = "0" * 64
    with _tampered(bad):
        with pytest.raises(ValueError) as exc_info:
            load_operational_manifest()
        assert "SHA256_MISMATCH" in str(exc_info.value)


def test_w2_027_negative_path_escape():
    """load_operational_manifest raises ValueError when a path escapes the repo root."""
    base = load_operational_manifest()
    bad = json.loads(json.dumps(base))
    bad["entries"][0]["path"] = "../../etc/passwd"
    bad["entries"][0]["sha256"] = "0" * 64
    with _tampered(bad):
        with pytest.raises(ValueError) as exc_info:
            load_operational_manifest()
        assert "PATH_ESCAPE" in str(exc_info.value) or "MISSING" in str(exc_info.value)


def test_w2_028_negative_duplicate_path():
    """load_operational_manifest raises ValueError when paths are duplicated."""
    base = load_operational_manifest()
    bad = json.loads(json.dumps(base))
    bad["entries"][1]["path"] = bad["entries"][0]["path"]
    with _tampered(bad):
        with pytest.raises(ValueError) as exc_info:
            load_operational_manifest()
        assert "DUPLICATE_PATH" in str(exc_info.value)


def test_w2_029_production_consumer_imports_catalog():
    """periphery_ops.py imports get_wave002_provenance from operational_source_catalog."""
    import ast
    from pathlib import Path

    route_path = Path(__file__).resolve().parent.parent.parent / (
        "apps/obsidia_api/routes/periphery_ops.py"
    )
    source = route_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    catalog_imports = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module == "periphery.agents.operational_source_catalog"
    ]
    assert catalog_imports, (
        "periphery_ops.py does not import from periphery.agents.operational_source_catalog"
    )
    imported_names = {alias.name for imp in catalog_imports for alias in imp.names}
    assert "get_wave002_provenance" in imported_names, (
        f"get_wave002_provenance not imported; found: {imported_names}"
    )


def test_w2_030_operational_catalog_endpoint_exists():
    """/governance/operational-catalog endpoint is declared in periphery_ops.py."""
    from pathlib import Path

    route_path = Path(__file__).resolve().parent.parent.parent / (
        "apps/obsidia_api/routes/periphery_ops.py"
    )
    source = route_path.read_text(encoding="utf-8")
    assert '"/governance/operational-catalog"' in source, (
        "Endpoint /governance/operational-catalog not found in periphery_ops.py"
    )
    assert "get_operational_catalog_provenance" in source, (
        "get_operational_catalog_provenance not called in periphery_ops.py"
    )
