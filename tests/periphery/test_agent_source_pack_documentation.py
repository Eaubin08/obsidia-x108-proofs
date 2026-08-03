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

def test_w3_010b_truth_audit_present():
    d = _load_index()
    assert d.get("truth_audit") == "WAVE003_LAST_MILE_GATE_V3"
    assert d.get("false_relations_corrected") == 117
    gate_v2 = d.get("gate_v2_corrections", {})
    assert gate_v2.get("total_gate_v2") == 512, (
        f"Expected 512 gate_v2 corrections, got {gate_v2.get('total_gate_v2')}"
    )
    gate_v3 = d.get("gate_v3_corrections", {})
    assert gate_v3.get("arbres_to_canonical_index") == 388, (
        f"Expected 388 ARBRES reclassified in gate_v3, got {gate_v3}"
    )
    # Population rebaseline present
    rb = d.get("wave003_population_rebaseline", {})
    assert rb.get("old_estimate_status") == "NON_RECONSTRUCTIBLE_PLANNING_ESTIMATE"
    assert rb.get("current_audited_population") == 680


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
        "NAMESPACE_ANCHOR",
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

def test_w3_040_arbres_34_proved_structural_relation():
    """04_ARBRES: GATE_V3 corrected chain.

    388 content docs -> DOCUMENT_LINKED_TO_CANONICAL_INDEX (dest: Wave003 index).
    The index-level field index_linked_to_structural_namespace carries the
    pack->tree_registry.py relation. No individual ARBRE file is loaded by
    tree_registry.py (criterion C only: pack name string reference).
    35 __init__.py namespace anchors -> NAMESPACE_ANCHOR_LINKED_TO_DOCUMENT_INDEX.
    """
    arbres = [e for e in _entries() if e["directory_family"] == "04_ARBRES_34_TENSOR_MATRIX"]
    assert len(arbres) == 423, f"Expected 423 ARBRES entries, got {len(arbres)}"
    content = [e for e in arbres if not e["path"].endswith("__init__.py")]
    init = [e for e in arbres if e["path"].endswith("__init__.py")]
    assert len(content) == 388, f"Expected 388 ARBRES content files, got {len(content)}"
    assert len(init) == 35, f"Expected 35 ARBRES __init__.py, got {len(init)}"
    wave003_index = "agent_source_pack_documentation.index.json"
    for e in content:
        assert e.get("relation_type") == "DOCUMENT_LINKED_TO_CANONICAL_INDEX", (
            f"ARBRES content must be CANONICAL_INDEX (pointing to Wave003 index): {e['path']}"
        )
        assert wave003_index in (e.get("destination") or ""), (
            f"ARBRES content must link to Wave003 index, not directly to tree_registry.py: {e['path']}"
        )
        # Must NOT claim a direct link to tree_registry.py
        assert "tree_registry" not in (e.get("destination") or ""), (
            f"GATE_V3: no individual ARBRE may claim direct link to tree_registry.py: {e['path']}"
        )
        assert e.get("semantic_verdict") == "TRUE_DOCUMENTARY_RELATION"
    for e in init:
        assert e.get("relation_type") == "NAMESPACE_ANCHOR_LINKED_TO_DOCUMENT_INDEX", (
            f"ARBRES __init__ must be NAMESPACE_ANCHOR_LINKED_TO_DOCUMENT_INDEX: {e['path']}"
        )
        assert e.get("role") == "NAMESPACE_ANCHOR"


def test_w3_041_agents52_proved_structural_relation():
    """10_AGENTS_52: GATE_V3 exact partition of 66 files.

    52 source docs (one per agent) -> DOCUMENT_LINKED_TO_REGISTRY_ENTRY (agents_52.registry.json, 52 entries).
    1 README.md (section index) + 2 structural (registry.json, csv) -> CANONICAL_INDEX.
    11 namespace anchors (__init__.py x10 + source_manifest.json) -> NAMESPACE_ANCHOR_LINKED_TO_DOCUMENT_INDEX.
    Total: 52 exact + 14 others = 66.
    """
    a52 = [e for e in _entries() if e["directory_family"] == "10_AGENTS_52"]
    assert len(a52) == 66, f"Expected 66 AGENTS52 entries, got {len(a52)}"
    source_docs = [e for e in a52 if e["relation_type"] == "DOCUMENT_LINKED_TO_REGISTRY_ENTRY"]
    assert len(source_docs) == 52, (
        f"GATE_V3: Expected exactly 52 AGENTS52 source docs (one-to-one with registry entries), "
        f"got {len(source_docs)}"
    )
    for e in source_docs:
        assert "agents_52.registry.json" in (e.get("destination") or ""), (
            f"Agents52 source doc not linked to agents_52.registry.json: {e['path']}"
        )
        assert e.get("semantic_verdict") == "TRUE_DOCUMENTARY_RELATION"
    # Exactly 14 other files explained
    others = [e for e in a52 if e["relation_type"] != "DOCUMENT_LINKED_TO_REGISTRY_ENTRY"]
    assert len(others) == 14, (
        f"Expected 14 AGENTS52 other files (README + structural + namespace), got {len(others)}"
    )
    # The README.md must be CANONICAL_INDEX, not REGISTRY_ENTRY
    readme = [e for e in a52 if e["path"].endswith("README.md")]
    assert len(readme) == 1
    assert readme[0]["relation_type"] == "DOCUMENT_LINKED_TO_CANONICAL_INDEX", (
        "README.md must be CANONICAL_INDEX (section index, not an agent source doc)"
    )
    assert readme[0]["role"] == "INDEX_DOCUMENT"
    # Check the partition metadata in the index
    d = _load_index()
    partition = d.get("agents52_partition", {})
    assert partition.get("exact_registry_entry_documents") == 52
    assert partition.get("total_other_explained") == 14
    assert partition.get("total_in_wave003") == 66


def test_w3_042_shazam_not_runtime_no_direct_tree_registry():
    """05_SHAZAM: GATE_V3 invariants.

    shazam.registry.json is empty (0 entries) — no EXACT_REGISTRY_ENTRY possible.
    Content files -> CANONICAL_INDEX (in manifest). __init__.py -> NAMESPACE_ANCHOR (not in manifest).
    No entry may claim RUNTIME_COMPONENT or direct link to tree_registry.py.
    """
    shazam = [e for e in _entries() if e["directory_family"] == "05_SHAZAM_COGNITIF"]
    assert len(shazam) > 0
    for e in shazam:
        assert e.get("relation_type") != "DOCUMENT_LINKED_TO_RUNTIME_COMPONENT", (
            f"Shazam must not claim false runtime link: {e['path']}"
        )
        assert e.get("relation_type") != "DOCUMENT_LINKED_TO_STRUCTURAL_NAMESPACE", (
            f"Shazam must not claim structural namespace link: {e['path']}"
        )
        assert "tree_registry" not in (e.get("destination") or ""), (
            f"Shazam must not link to tree_registry.py: {e['path']}"
        )


def test_w3_043_mcp_not_runtime_no_direct_tree_registry():
    """09_MCP: mcp_bridge.registry.json is empty. No runtime, no direct tree_registry link."""
    mcp = [e for e in _entries() if e["directory_family"] == "09_MCP_BRIDGE_OBSIDIA_IR"]
    assert len(mcp) > 0
    for e in mcp:
        assert e.get("relation_type") != "DOCUMENT_LINKED_TO_RUNTIME_COMPONENT"
        assert "tree_registry" not in (e.get("destination") or ""), (
            f"MCP must not link to tree_registry.py: {e['path']}"
        )


def test_w3_044_guards_not_runtime_no_direct_tree_registry():
    """15_GUARDS: guards.registry.json is empty. No runtime, no direct tree_registry link."""
    guards = [e for e in _entries() if e["directory_family"] == "15_GUARDS_NON_DECISION"]
    assert len(guards) > 0
    for e in guards:
        assert e.get("relation_type") != "DOCUMENT_LINKED_TO_RUNTIME_COMPONENT"
        assert "tree_registry" not in (e.get("destination") or ""), (
            f"Guards must not link to tree_registry.py: {e['path']}"
        )


def test_w3_045_registres_json_linked_to_self():
    regs = [e for e in _entries() if e["directory_family"] == "19_REGISTRES_JSON"]
    assert len(regs) >= 10, f"Expected >=10 registry entries, got {len(regs)}"


def test_w3_046_index_family_count():
    idx = [e for e in _entries() if e["directory_family"] == "00_INDEX"]
    assert len(idx) >= 8, f"Expected >=8 index docs, got {len(idx)}"


def test_w3_047_relation_distribution():
    """Verify the GATE_V3 final relation distribution.

    GATE_V3 final (last-mile truth):
    - DOCUMENT_LINKED_TO_CANONICAL_INDEX:       560 (388 ARBRES->index + 101 manifest + 71 others)
    - DOCUMENT_LINKED_TO_REGISTRY_ENTRY:         52 (10_AGENTS_52 source docs, EXACT 1-to-1)
    - NAMESPACE_ANCHOR_LINKED_TO_DOCUMENT_INDEX: 66 (__init__.py + files absent from manifest)
    - HISTORICAL_EXTRACTION_LINKED_TO_SOURCE_INVENTORY: 1 (extracted_text_all.md)
    - HISTORICAL_VISUAL_LINKED_TO_DOCUMENT_OR_INVENTORY: 1 (image_34_arbres.png)
    - DOCUMENT_LINKED_TO_RUNTIME_COMPONENT:      0
    - DOCUMENT_LINKED_TO_STRUCTURAL_NAMESPACE:   0 (carried by index metadata only)
    """
    from collections import Counter
    dist = Counter(e["relation_type"] for e in _entries())
    assert dist["DOCUMENT_LINKED_TO_CANONICAL_INDEX"] == 560, (
        f"Expected 560 canonical-index relations, got {dist['DOCUMENT_LINKED_TO_CANONICAL_INDEX']}"
    )
    assert dist["DOCUMENT_LINKED_TO_REGISTRY_ENTRY"] == 52, (
        f"Expected 52 exact registry-entry relations (agents52 source docs), "
        f"got {dist['DOCUMENT_LINKED_TO_REGISTRY_ENTRY']}"
    )
    assert dist["NAMESPACE_ANCHOR_LINKED_TO_DOCUMENT_INDEX"] == 66, (
        f"Expected 66 namespace anchor relations, got {dist['NAMESPACE_ANCHOR_LINKED_TO_DOCUMENT_INDEX']}"
    )
    assert dist["HISTORICAL_EXTRACTION_LINKED_TO_SOURCE_INVENTORY"] == 1, (
        f"Expected 1 historical extraction relation, got {dist['HISTORICAL_EXTRACTION_LINKED_TO_SOURCE_INVENTORY']}"
    )
    assert dist["HISTORICAL_VISUAL_LINKED_TO_DOCUMENT_OR_INVENTORY"] == 1, (
        f"Expected 1 historical visual relation, got {dist['HISTORICAL_VISUAL_LINKED_TO_DOCUMENT_OR_INVENTORY']}"
    )
    assert dist.get("DOCUMENT_LINKED_TO_RUNTIME_COMPONENT", 0) == 0, (
        f"No DOCUMENT_LINKED_TO_RUNTIME_COMPONENT must remain, "
        f"got {dist.get('DOCUMENT_LINKED_TO_RUNTIME_COMPONENT', 0)}"
    )
    assert dist.get("DOCUMENT_LINKED_TO_STRUCTURAL_NAMESPACE", 0) == 0, (
        "STRUCTURAL_NAMESPACE must be 0 -- relation is at index level only (index_linked_to_structural_namespace)"
    )
    assert dist.get("GENERATED_DOCUMENT_LINKED_TO_GENERATOR", 0) == 0
    assert dist.get("DOCUMENT_LINKED_TO_TEST", 0) == 0
    assert sum(dist.values()) == 680, f"Total must be 680, got {sum(dist.values())}"


def test_w3_048_semantic_verdicts_all_true():
    """All entries must have TRUE_DOCUMENTARY_RELATION (TRUE_STRUCTURAL eliminated at GATE_V2)."""
    for e in _entries():
        v = e.get("semantic_verdict", "")
        assert v == "TRUE_DOCUMENTARY_RELATION", (
            f"Entry {e['path']} has semantic_verdict={v!r} -- must be TRUE_DOCUMENTARY_RELATION"
        )


def test_w3_049_no_runtime_component_claims():
    """GATE_V3: zero entries may claim DOCUMENT_LINKED_TO_RUNTIME_COMPONENT or STRUCTURAL_NAMESPACE.

    The pack->tree_registry.py relation is carried at index level only
    (index_linked_to_structural_namespace field), not repeated on 388 individual documents.
    """
    for rt in ("DOCUMENT_LINKED_TO_RUNTIME_COMPONENT", "DOCUMENT_LINKED_TO_STRUCTURAL_NAMESPACE"):
        bad = [e for e in _entries() if e.get("relation_type") == rt]
        assert len(bad) == 0, (
            f"GATE_V3: {len(bad)} entries claim {rt!r} -- must be zero: "
            f"{[e['path'] for e in bad[:3]]}"
        )
    # Structural namespace carried at index level
    d = _load_index()
    ns = d.get("index_linked_to_structural_namespace", {})
    assert ns.get("namespace") == "MMONDE_OS_TRAD_34_ARBRES"
    assert "tree_registry.py" in ns.get("target", "")
    assert ns.get("criterion") == "C_PACK_NAME_REFERENCE_ONLY"


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


def test_w3_074_no_direct_document_to_tree_registry():
    """GATE_V3: zero individual documents may declare tree_registry.py as destination.

    The pack->tree_registry.py relation is at index level (index_linked_to_structural_namespace).
    No individual MMONDE document claims to be loaded by tree_registry.py at runtime.
    """
    bad = [
        e for e in _entries()
        if "tree_registry" in (e.get("destination") or "")
    ]
    assert len(bad) == 0, (
        f"GATE_V3: {len(bad)} entries claim direct tree_registry.py destination -- "
        f"must be zero (relation is at index level): {[e['path'] for e in bad[:3]]}"
    )


def test_w3_075_no_manifest_absent_links_to_manifest():
    """GATE_V3: files absent from MANIFEST_SHA256.json must not declare MANIFEST as destination."""
    import json as _json
    root = _repo_root()
    with open(root / "periphery" / "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1"
              / "00_INDEX" / "MANIFEST_SHA256.json", encoding="utf-8") as f:
        manifest = _json.load(f)
    pack_prefix = "periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/"
    manifest_paths = set(pack_prefix + e["path"] for e in manifest["files"])
    bad = [
        e for e in _entries()
        if "MANIFEST_SHA256.json" in (e.get("destination") or "")
        and e["path"] not in manifest_paths
    ]
    assert len(bad) == 0, (
        f"GATE_V3: {len(bad)} files absent from MANIFEST yet point to MANIFEST as destination: "
        f"{[e['path'] for e in bad[:5]]}"
    )


def test_w3_076_historical_sources_honest_types():
    """GATE_V3: extracted_text_all.md and image_34_arbres.png use honest historical types."""
    extraction = [e for e in _entries() if e["path"].endswith("extracted_text_all.md")]
    assert len(extraction) == 1
    assert extraction[0]["relation_type"] == "HISTORICAL_EXTRACTION_LINKED_TO_SOURCE_INVENTORY", (
        "extracted_text_all.md must use HISTORICAL_EXTRACTION_LINKED_TO_SOURCE_INVENTORY"
    )
    assert "source_inventory.json" in (extraction[0].get("destination") or ""), (
        "extracted_text_all.md must link to source_inventory.json"
    )
    visual = [e for e in _entries() if e["path"].endswith("image_34_arbres.png")]
    assert len(visual) == 1
    assert visual[0]["relation_type"] == "HISTORICAL_VISUAL_LINKED_TO_DOCUMENT_OR_INVENTORY", (
        "image_34_arbres.png must use HISTORICAL_VISUAL_LINKED_TO_DOCUMENT_OR_INVENTORY"
    )
    assert "source_inventory.json" in (visual[0].get("destination") or ""), (
        "image_34_arbres.png must link to source_inventory.json"
    )


def test_w3_077_no_temporary_helpers_in_git():
    """GATE_V3: helper scripts (_gate_*.py) must not be tracked in git."""
    import subprocess
    result = subprocess.run(
        ["git", "ls-files", "_gate_v2_patch.py", "_gate_v3_patch.py"],
        capture_output=True, text=True,
        cwd=str(_repo_root())
    )
    tracked = result.stdout.strip()
    assert not tracked, (
        f"Temporary helpers must not be in git tracked files: {tracked!r}"
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
