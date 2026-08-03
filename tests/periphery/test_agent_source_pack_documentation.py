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
    assert d.get("truth_audit") == "WAVE003_EVIDENCE_GATE_V2"
    assert d.get("false_relations_corrected") == 117
    gate = d.get("gate_v2_corrections", {})
    assert gate.get("total_gate_v2") == 512, (
        f"Expected 512 gate_v2 corrections, got {gate.get('total_gate_v2')}"
    )


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
    """04_ARBRES: content docs -> STRUCTURAL_NAMESPACE, __init__.py -> CANONICAL_INDEX.

    GATE_V2: tree_registry.py references pack name only (criterion C). No individual
    file loading (L15: individual MMONDE file SHAs NOT_COMPUTED in V0). 388 content
    documents link to tree_registry.py as DOCUMENT_LINKED_TO_STRUCTURAL_NAMESPACE.
    35 __init__.py namespace anchors link to MANIFEST_SHA256.json as CANONICAL_INDEX.
    """
    arbres = [e for e in _entries() if e["directory_family"] == "04_ARBRES_34_TENSOR_MATRIX"]
    assert len(arbres) == 423, f"Expected 423 ARBRES entries, got {len(arbres)}"
    content = [e for e in arbres if not e["path"].endswith("__init__.py")]
    init = [e for e in arbres if e["path"].endswith("__init__.py")]
    assert len(content) == 388, f"Expected 388 ARBRES content files, got {len(content)}"
    assert len(init) == 35, f"Expected 35 ARBRES __init__.py, got {len(init)}"
    for e in content:
        assert e.get("relation_type") == "DOCUMENT_LINKED_TO_STRUCTURAL_NAMESPACE", (
            f"ARBRES content must be STRUCTURAL_NAMESPACE: {e['path']}"
        )
        assert "cognitive_trees" in (e.get("destination") or ""), (
            f"ARBRES content must link to cognitive_trees: {e['path']}"
        )
        assert e.get("semantic_verdict") == "TRUE_DOCUMENTARY_RELATION"
    for e in init:
        assert e.get("relation_type") == "DOCUMENT_LINKED_TO_CANONICAL_INDEX", (
            f"ARBRES __init__ must be CANONICAL_INDEX: {e['path']}"
        )
        assert e.get("role") == "NAMESPACE_ANCHOR"


def test_w3_041_agents52_proved_structural_relation():
    """10_AGENTS_52: 53 source docs -> REGISTRY_ENTRY (agents_52.registry.json has 52 named entries).
    Remaining 13 (init + structural) -> CANONICAL_INDEX.
    GATE_V2: all semantic_verdicts are TRUE_DOCUMENTARY_RELATION."""
    a52 = [e for e in _entries() if e["directory_family"] == "10_AGENTS_52"]
    assert len(a52) == 66, f"Expected 66 AGENTS52 entries, got {len(a52)}"
    source_docs = [e for e in a52 if e["relation_type"] == "DOCUMENT_LINKED_TO_REGISTRY_ENTRY"]
    assert len(source_docs) == 53, (
        f"Expected 53 AGENTS52 source docs in REGISTRY_ENTRY, got {len(source_docs)}"
    )
    for e in source_docs:
        assert "agents_52.registry.json" in (e.get("destination") or ""), (
            f"Agents52 source doc not linked to agents_52.registry.json: {e['path']}"
        )
        assert e.get("semantic_verdict") == "TRUE_DOCUMENTARY_RELATION"
    canonical = [e for e in a52 if e["relation_type"] == "DOCUMENT_LINKED_TO_CANONICAL_INDEX"]
    assert len(canonical) == 13, (
        f"Expected 13 AGENTS52 structural/namespace entries in CANONICAL_INDEX, got {len(canonical)}"
    )


def test_w3_042_shazam_linked_to_canonical_not_runtime():
    """05_SHAZAM links to MANIFEST_SHA256.json (GATE_V2: shazam.registry.json is an empty stub).

    GATE_V2: shazam.registry.json has 0 entries — no EXACT_REGISTRY_ENTRY possible.
    All shazam files reclassified to DOCUMENT_LINKED_TO_CANONICAL_INDEX.
    Previous claim (shazam_cognitif.py) was FALSE — no MMONDE reference found.
    """
    shazam = [e for e in _entries() if e["directory_family"] == "05_SHAZAM_COGNITIF"]
    assert len(shazam) > 0
    for e in shazam:
        assert e.get("relation_type") == "DOCUMENT_LINKED_TO_CANONICAL_INDEX", (
            f"Shazam must be CANONICAL_INDEX (empty registry): {e['path']}"
        )
        assert e.get("relation_type") != "DOCUMENT_LINKED_TO_RUNTIME_COMPONENT", (
            f"Shazam must not claim false runtime link: {e['path']}"
        )
        assert "MANIFEST_SHA256.json" in (e.get("destination") or ""), (
            f"Shazam not linked to MANIFEST_SHA256.json: {e['path']}"
        )


def test_w3_043_mcp_linked_to_canonical_not_runtime():
    """09_MCP links to MANIFEST_SHA256.json (GATE_V2: mcp_bridge.registry.json is empty stub)."""
    mcp = [e for e in _entries() if e["directory_family"] == "09_MCP_BRIDGE_OBSIDIA_IR"]
    assert len(mcp) > 0
    for e in mcp:
        assert "MANIFEST_SHA256.json" in (e.get("destination") or ""), (
            f"MCP not linked to MANIFEST_SHA256.json: {e['path']}"
        )
        assert e.get("relation_type") != "DOCUMENT_LINKED_TO_RUNTIME_COMPONENT"


def test_w3_044_guards_linked_to_canonical_not_runtime():
    """15_GUARDS links to MANIFEST_SHA256.json (GATE_V2: guards.registry.json is empty stub)."""
    guards = [e for e in _entries() if e["directory_family"] == "15_GUARDS_NON_DECISION"]
    assert len(guards) > 0
    for e in guards:
        assert "MANIFEST_SHA256.json" in (e.get("destination") or ""), (
            f"Guards not linked to MANIFEST_SHA256.json: {e['path']}"
        )
        assert e.get("relation_type") != "DOCUMENT_LINKED_TO_RUNTIME_COMPONENT"


def test_w3_045_registres_json_linked_to_self():
    regs = [e for e in _entries() if e["directory_family"] == "19_REGISTRES_JSON"]
    assert len(regs) >= 10, f"Expected >=10 registry entries, got {len(regs)}"


def test_w3_046_index_family_count():
    idx = [e for e in _entries() if e["directory_family"] == "00_INDEX"]
    assert len(idx) >= 8, f"Expected >=8 index docs, got {len(idx)}"


def test_w3_047_relation_distribution():
    """Verify the GATE_V2 corrected relation distribution.

    GATE_V2 final:
    - DOCUMENT_LINKED_TO_STRUCTURAL_NAMESPACE: 388 (04_ARBRES content -- pack name ref only)
    - DOCUMENT_LINKED_TO_REGISTRY_ENTRY:        53 (10_AGENTS_52 source docs, EXACT entries)
    - DOCUMENT_LINKED_TO_CANONICAL_INDEX:       237 (35 ARBRES init + 86 empty-registry + 3 hist + 113 orig)
    - HISTORICAL_DOCUMENT_LINKED_TO_CURRENT_SOURCE: 2 (extracted_text_all.md + image_34_arbres.png)
    - DOCUMENT_LINKED_TO_RUNTIME_COMPONENT:      0 (all reclassified at gate)
    """
    from collections import Counter
    dist = Counter(e["relation_type"] for e in _entries())
    assert dist["DOCUMENT_LINKED_TO_STRUCTURAL_NAMESPACE"] == 388, (
        f"Expected 388 structural-namespace (04_ARBRES content), got {dist['DOCUMENT_LINKED_TO_STRUCTURAL_NAMESPACE']}"
    )
    assert dist["DOCUMENT_LINKED_TO_REGISTRY_ENTRY"] == 53, (
        f"Expected 53 registry relations (agents52 source docs), got {dist['DOCUMENT_LINKED_TO_REGISTRY_ENTRY']}"
    )
    assert dist["DOCUMENT_LINKED_TO_CANONICAL_INDEX"] == 237, (
        f"Expected 237 canonical index relations, got {dist['DOCUMENT_LINKED_TO_CANONICAL_INDEX']}"
    )
    assert dist["HISTORICAL_DOCUMENT_LINKED_TO_CURRENT_SOURCE"] == 2, (
        f"Expected 2 historical source relations, got {dist['HISTORICAL_DOCUMENT_LINKED_TO_CURRENT_SOURCE']}"
    )
    assert dist.get("DOCUMENT_LINKED_TO_RUNTIME_COMPONENT", 0) == 0, (
        f"No DOCUMENT_LINKED_TO_RUNTIME_COMPONENT must remain after GATE_V2, "
        f"got {dist.get('DOCUMENT_LINKED_TO_RUNTIME_COMPONENT', 0)}"
    )
    assert dist.get("GENERATED_DOCUMENT_LINKED_TO_GENERATOR", 0) == 0, (
        "No GENERATED_DOCUMENT_LINKED_TO_GENERATOR must remain (all corrected)"
    )
    assert dist.get("DOCUMENT_LINKED_TO_TEST", 0) == 0, (
        "No DOCUMENT_LINKED_TO_TEST must remain (corrected -- no proven test link)"
    )


def test_w3_048_semantic_verdicts_all_true():
    """All entries must have TRUE_DOCUMENTARY_RELATION (GATE_V2: TRUE_STRUCTURAL eliminated)."""
    for e in _entries():
        v = e.get("semantic_verdict", "")
        assert v == "TRUE_DOCUMENTARY_RELATION", (
            f"Entry {e['path']} has semantic_verdict={v!r} -- must be TRUE_DOCUMENTARY_RELATION after GATE_V2"
        )


def test_w3_049_no_runtime_component_claims():
    """GATE_V2: zero entries may claim DOCUMENT_LINKED_TO_RUNTIME_COMPONENT.

    04_ARBRES content was reclassified to DOCUMENT_LINKED_TO_STRUCTURAL_NAMESPACE
    (tree_registry.py references pack name only -- criterion C, no individual file loading).
    """
    runtime_entries = [
        e for e in _entries()
        if e.get("relation_type") == "DOCUMENT_LINKED_TO_RUNTIME_COMPONENT"
    ]
    assert len(runtime_entries) == 0, (
        f"GATE_V2: {len(runtime_entries)} entries still claim RUNTIME_COMPONENT -- must be zero: "
        f"{[e['path'] for e in runtime_entries[:3]]}"
    )


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
