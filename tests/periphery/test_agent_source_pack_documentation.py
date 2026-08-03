"""
Wave003 -- AGENT_SOURCE_PACK_DOCUMENTATION semantic wiring tests.

Verifies:
- Population and schema integrity of the Wave003 index
- Every file has a role, owner, and semantic destination
- No artificial routes created
- No new authority, no memory writes, no model calls
- 10_AGENTS_52 entries link to the existing agents52 registry (Wave001)
- Wave001 (agents_obsidia_config_registry) and Wave002 (operational_source_catalog) regressions
"""
from __future__ import annotations

import json
import hashlib
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for p in here.parents:
        if (p / ".git").exists():
            return p
    raise RuntimeError("Cannot locate repo root from " + str(here))


def _load_index() -> dict:
    path = _repo_root() / "periphery" / "agents" / "agent_source_pack_documentation.index.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _entries():
    return _load_index()["entries"]


# ---------------------------------------------------------------------------
# W3_001 -- Schema and metadata
# ---------------------------------------------------------------------------

def test_w3_001_index_exists():
    p = _repo_root() / "periphery" / "agents" / "agent_source_pack_documentation.index.json"
    assert p.is_file(), "agent_source_pack_documentation.index.json must exist"


def test_w3_002_schema_version():
    d = _load_index()
    assert d["schema_version"] == "1.0"


def test_w3_003_index_id():
    d = _load_index()
    assert d["index_id"] == "AGENT_SOURCE_PACK_DOCUMENTATION_INDEX_V1"


def test_w3_004_authority_non_sovereign():
    d = _load_index()
    assert d.get("authority") == "NON_SOVEREIGN"


def test_w3_005_no_decision_flags():
    d = _load_index()
    assert d.get("can_decide") is False
    assert d.get("can_act") is False
    assert d.get("emits_act") is False
    assert d.get("memory_write") is False
    assert d.get("model_calls") == 0


def test_w3_006_runtime_not_consumed():
    d = _load_index()
    assert d.get("runtime_consumed") is False
    assert d.get("catalog_role") == "DOCUMENTARY_INDEX"


def test_w3_007_wave_tag():
    d = _load_index()
    assert d.get("wave") == "AGENTS_FILE_WIRING_WAVE_003"


# ---------------------------------------------------------------------------
# W3_010 -- Population integrity
# ---------------------------------------------------------------------------

def test_w3_010_population_exact():
    d = _load_index()
    assert d["total_files"] == 680, f"Expected 680, got {d['total_files']}"
    assert len(d["entries"]) == 680


def test_w3_011_paths_unique():
    paths = [e["path"] for e in _entries()]
    assert len(paths) == len(set(paths)), "Duplicate paths detected"


def test_w3_012_no_path_escape():
    root_prefix = "periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1"
    for e in _entries():
        assert e["path"].startswith(root_prefix), f"Path escapes root: {e['path']}"


def test_w3_013_no_pycache():
    for e in _entries():
        assert "__pycache__" not in e["path"]


# ---------------------------------------------------------------------------
# W3_020 -- All files have required fields
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = (
    "path", "sha256", "file_extension", "directory_family",
    "role", "canonicality_status", "relation_type", "owner_subsystem", "status",
)


def test_w3_020_all_entries_have_required_fields():
    for e in _entries():
        for field in REQUIRED_FIELDS:
            assert field in e and e[field] is not None, (
                f"Missing field '{field}' in entry: {e['path']}"
            )


def test_w3_021_no_unknown_role():
    valid_roles = {
        "AGENT_SPECIFICATION", "AGENT_SOURCE_DOCUMENT", "AGENT_PROMPT_OR_INSTRUCTION",
        "ARCHITECTURE_DOCUMENT", "PROTOCOL_DOCUMENT", "GOVERNANCE_DOCUMENT",
        "REGISTRY_DOCUMENTATION", "RUNTIME_USAGE_DOCUMENTATION", "TEST_DOCUMENTATION",
        "PROOF_DOCUMENTATION", "DATA_DICTIONARY", "MIGRATION_DOCUMENT",
        "GENERATED_REPORT", "HISTORICAL_SOURCE", "LEGACY_DOCUMENT",
        "ARCHIVE_DOCUMENT", "DUPLICATE_DOCUMENT", "INDEX_DOCUMENT",
        "UNKNOWN_PENDING_REVIEW",
    }
    for e in _entries():
        assert e["role"] in valid_roles, f"Invalid role {e['role']!r} in {e['path']}"


def test_w3_022_no_missing_destination_without_blocker():
    for e in _entries():
        status = e.get("status", "")
        if not status.startswith("BLOCKED"):
            assert e.get("destination") is not None, (
                f"Non-blocked entry has no destination: {e['path']}"
            )


def test_w3_023_all_files_exist_on_disk():
    root = _repo_root()
    missing = []
    for e in _entries():
        if not (root / e["path"]).is_file():
            missing.append(e["path"])
    assert not missing, f"{len(missing)} files missing: {missing[:5]}"


def test_w3_024_sha256_sample_first_20():
    """Verify SHA256 for first 20 entries (full scan would be slow)."""
    root = _repo_root()
    entries = _entries()[:20]
    for e in entries:
        p = root / e["path"]
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        assert h.hexdigest() == e["sha256"], f"SHA256 mismatch: {e['path']}"


# ---------------------------------------------------------------------------
# W3_030 -- Zero blocked (all have destinations)
# ---------------------------------------------------------------------------

def test_w3_030_zero_blocked():
    blocked = [e for e in _entries() if (e.get("status") or "").startswith("BLOCKED")]
    assert len(blocked) == 0, f"{len(blocked)} blocked entries: {[b['path'] for b in blocked[:5]]}"


def test_w3_031_zero_unexplained_unresolved():
    unresolved = [e for e in _entries() if e.get("role") == "UNKNOWN_PENDING_REVIEW"]
    assert len(unresolved) == 0, f"{len(unresolved)} unresolved entries"


# ---------------------------------------------------------------------------
# W3_040 -- Subfamily distributions
# ---------------------------------------------------------------------------

def test_w3_040_arbres_34_family_linked_to_tree_registry():
    arbres = [e for e in _entries() if e["directory_family"] == "04_ARBRES_34_TENSOR_MATRIX"]
    assert len(arbres) > 0
    for e in arbres:
        assert "cognitive_trees" in (e.get("destination") or ""), (
            f"Arbre not linked to cognitive_trees: {e['path']}"
        )


def test_w3_041_agents52_family_linked_to_registry():
    a52 = [e for e in _entries() if e["directory_family"] == "10_AGENTS_52"]
    assert len(a52) > 0
    for e in a52:
        assert "agents_52.registry.json" in (e.get("destination") or ""), (
            f"Agents52 entry not linked to agents_52.registry.json: {e['path']}"
        )


def test_w3_042_shazam_linked_to_shazam_cognitif():
    shazam = [e for e in _entries() if e["directory_family"] == "05_SHAZAM_COGNITIF"]
    assert len(shazam) > 0
    for e in shazam:
        assert "shazam_cognitif" in (e.get("destination") or ""), (
            f"Shazam not linked to shazam_cognitif: {e['path']}"
        )


def test_w3_043_mcp_family_linked_to_mcp():
    mcp = [e for e in _entries() if e["directory_family"] == "09_MCP_BRIDGE_OBSIDIA_IR"]
    assert len(mcp) > 0
    for e in mcp:
        assert "mcp" in (e.get("destination") or ""), (
            f"MCP bridge not linked to mcp: {e['path']}"
        )


def test_w3_044_guards_linked_to_guards():
    guards = [e for e in _entries() if e["directory_family"] == "15_GUARDS_NON_DECISION"]
    assert len(guards) > 0
    for e in guards:
        assert "guards" in (e.get("destination") or ""), (
            f"Guards not linked to guards: {e['path']}"
        )


def test_w3_045_registres_json_linked_to_self():
    regs = [e for e in _entries() if e["directory_family"] == "19_REGISTRES_JSON"]
    assert len(regs) >= 10, f"Expected >=10 registry entries, got {len(regs)}"


def test_w3_046_index_family_count():
    idx = [e for e in _entries() if e["directory_family"] == "00_INDEX"]
    assert len(idx) >= 8, f"Expected >=8 index docs, got {len(idx)}"


# ---------------------------------------------------------------------------
# W3_050 -- No artificial route
# ---------------------------------------------------------------------------

def test_w3_050_no_artificial_api_route_for_wave003():
    """Verify no new API route was created to consume the Wave003 index."""
    routes_file = _repo_root() / "apps" / "obsidia_api" / "routes" / "periphery_ops.py"
    if not routes_file.is_file():
        pytest.skip("periphery_ops.py not found")
    content = routes_file.read_text(encoding="utf-8")
    assert "agent_source_pack" not in content, (
        "An artificial API route references agent_source_pack -- remove it"
    )
    assert "wave003" not in content.lower(), (
        "An artificial API route references wave003 -- remove it"
    )


def test_w3_051_no_artificial_import_for_wave003_index():
    routes_file = _repo_root() / "apps" / "obsidia_api" / "routes" / "periphery_ops.py"
    if not routes_file.is_file():
        pytest.skip("periphery_ops.py not found")
    content = routes_file.read_text(encoding="utf-8")
    assert "agent_source_pack_documentation" not in content, (
        "periphery_ops.py must not import the wave003 index loader"
    )


# ---------------------------------------------------------------------------
# W3_060 -- Validator module integrity
# ---------------------------------------------------------------------------

def test_w3_060_validator_module_exists():
    p = _repo_root() / "periphery" / "agents" / "agent_source_pack_documentation.py"
    assert p.is_file()


def test_w3_061_validator_no_memory_write():
    p = _repo_root() / "periphery" / "agents" / "agent_source_pack_documentation.py"
    src = p.read_text(encoding="utf-8")
    assert "memory_write" not in src.replace("memory_write=False", "").replace("memory_write=false", ""), (
        "Validator must not perform memory writes"
    )


def test_w3_062_validator_no_model_call():
    p = _repo_root() / "periphery" / "agents" / "agent_source_pack_documentation.py"
    src = p.read_text(encoding="utf-8")
    for keyword in ("anthropic", "openai", "requests.post", "httpx.post", "model_call"):
        assert keyword not in src.lower(), f"Validator contains model call keyword: {keyword}"


def test_w3_063_validator_importable():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "agent_source_pack_documentation",
        _repo_root() / "periphery" / "agents" / "agent_source_pack_documentation.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert hasattr(mod, "get_entries")
    assert hasattr(mod, "get_index")
    assert hasattr(mod, "summary")


def test_w3_064_validator_get_entries_returns_680():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "agent_source_pack_documentation",
        _repo_root() / "periphery" / "agents" / "agent_source_pack_documentation.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    entries = mod.get_entries()
    assert len(entries) == 680


# ---------------------------------------------------------------------------
# W3_070 -- Wave001/Wave002 regression
# ---------------------------------------------------------------------------

def test_w3_070_wave001_registry_still_passes():
    """Wave001 agents52 registry remains intact."""
    p = _repo_root() / "periphery" / "agents_obsidia_config_registry.py"
    assert p.is_file(), "Wave001 registry file must not have been removed"


def test_w3_071_wave002_catalog_still_passes():
    """Wave002 operational_source_catalog remains intact."""
    p = _repo_root() / "periphery" / "agents" / "operational_source_catalog.json"
    assert p.is_file(), "Wave002 catalog must not have been removed"
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    assert d.get("entry_count") == 167, "Wave002 entry count must remain 167"


def test_w3_072_wave002_artificial_route_still_absent():
    """Confirm Wave002's artificial route was not re-introduced."""
    routes_file = _repo_root() / "apps" / "obsidia_api" / "routes" / "periphery_ops.py"
    if not routes_file.is_file():
        pytest.skip("periphery_ops.py not found")
    content = routes_file.read_text(encoding="utf-8")
    assert "/governance/operational-catalog" not in content, (
        "Wave002 artificial route /governance/operational-catalog must not be re-introduced"
    )


def test_w3_073_wave002_44_false_relations_remain_downgraded():
    """Wave002 document index must not claim artificial runtime relations."""
    p = _repo_root() / "periphery" / "agents" / "operational_agent_document_index.json"
    if not p.is_file():
        pytest.skip("operational_agent_document_index.json not found")
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    entries = d.get("documents", d.get("entries", []))
    runtime_claimed = [
        e for e in entries
        if e.get("relation_status") == "CONNECTED_PROVED"
        and e.get("link_type") not in (
            "COHERENCE_GROUP_DOCUMENT", "KNOWLEDGE_SEED_AGENT",
            "AGENT_ROLE_SPECIFICATION", "SCAN_OUTPUT_DOCUMENTED",
            "MODULE_SPECIFICATION", "PS1_LINKED_TO_PYTHON",
        )
    ]
    assert len(runtime_claimed) == 0, (
        f"{len(runtime_claimed)} entries still claim false CONNECTED_PROVED relation"
    )
