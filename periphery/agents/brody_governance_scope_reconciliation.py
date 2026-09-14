"""
Readonly validator for the BRODY_GOVERNANCE_ELEMENT_SYSTEM scope reconciliation matrix.

Source: periphery/agents/brody_governance_scope_reconciliation.index.json

ARCHITECTURE: JSON_FIRST_READONLY_DOCUMENTARY_INDEX
AUTHORITY:    NON_SOVEREIGN -- KX108_ONLY decision authority.

No agent is invoked, no model is called, no memory is written.
can_decide=false / can_act=false / emits_act=false / memory_write=false
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

_INDEX_REL_PARTS = (
    "periphery",
    "agents",
    "brody_governance_scope_reconciliation.index.json",
)

_EXPECTED_INDEX_ID = "BRODY_GOVERNANCE_SCOPE_RECONCILIATION_INDEX_V1"
_CENSUS_ID = "BRODY_PRIMARY_POPULATION_CENSUS_V1"

_VALID_SUBWAVES = frozenset({
    "WAVE005_A_BRODY_CORE_GOVERNANCE_AND_TEST",
    "WAVE005_B_BRODY_INTEGRATION_RUNTIME_AND_API_TESTS",
    "WAVE005_C_BRODY_PROTOCOLS_CONNECTORS_AND_SCRIPTS",
    "WAVE005_D_BRODY_MEMORY_INTERFACE_AND_SPECS",
    "WAVE005_E_BRODY_DOCUMENTATION_ARCHITECTURE_AND_REPORTS",
    "WAVE005_F_BRODY_LEGACY_ARCHIVE_TOOLING_AND_REVIEW",
})

_WAVE005_A_INDEXED = frozenset({
    "periphery/brody/__init__.py",
    "periphery/brody/brody_response_contract.py",
    "periphery/brody/brody_runtime_readonly.py",
    "periphery/brody/brody_context_query.py",
    "periphery/brody/brody_language_router.py",
    "periphery/brody/brody_response_sanitizer.py",
    "tests/periphery/test_brody_response_contract.py",
    "tests/periphery/test_brody_runtime_readonly.py",
    "tests/non_sovereignty/test_brody_no_act.py",
    "tests/non_sovereignty/test_brody_no_decision.py",
    "tests/non_sovereignty/test_brody_response_never_emits_verdict.py",
})

_WAVE005_A_CORE_SOURCES = frozenset({
    "periphery/brody/__init__.py",
    "periphery/brody/brody_response_contract.py",
    "periphery/brody/brody_runtime_readonly.py",
    "periphery/brody/brody_context_query.py",
    "periphery/brody/brody_language_router.py",
    "periphery/brody/brody_response_sanitizer.py",
})

_WAVE005_A_GOVERNANCE_TESTS = frozenset({
    "tests/periphery/test_brody_response_contract.py",
    "tests/periphery/test_brody_runtime_readonly.py",
    "tests/non_sovereignty/test_brody_no_act.py",
    "tests/non_sovereignty/test_brody_no_decision.py",
    "tests/non_sovereignty/test_brody_response_never_emits_verdict.py",
})

_CAMPAIGN_METADATA_PATHS = frozenset({
    "periphery/agents/brody_governance_element_system.index.json",
    "periphery/agents/brody_governance_element_system.py",
    "tests/periphery/test_brody_governance_element_system.py",
    "periphery/agents/brody_governance_scope_reconciliation.index.json",
    "periphery/agents/brody_governance_scope_reconciliation.py",
    "tests/periphery/test_brody_governance_scope_reconciliation.py",
})

_SECONDARY_RELATION_PATHS = frozenset({
    "periphery/agents/brody_memory_agent.py",
    "periphery/brody_memory_readonly/brody_agent_readonly_session_test_packet/run_brody_agent_readonly_session_test_packet_v1.ps1",
    "periphery/workflow_governance_readonly/integration/brody_workflow_governance_snapshot_adapter.py",
    "periphery/workflow_governance_readonly/operators/brody_workflow_operator_readonly.py",
})

_FIVE_EXCLUDED_FROM_914 = [
    ".runtime_freezes/F32_BRODY_FULL_RUNTIME_INTEGRATION_READONLY_PACKET_20260529_023206/MANIFEST_SHA256.json",
    ".runtime_freezes/F33_BRODY_RUNTIME_ENTRYPOINT_READONLY_20260529_012937/MANIFEST_SHA256.json",
    ".runtime_freezes/F36_USER_SCENARIO_BRODY_WORKBENCH_CONTROLLED_RESPONSE_20260529_033111/MANIFEST_SHA256.json",
    ".runtime_freezes/F42_BRODY_GPT_V1_FINAL_RELEASE_SEAL_20260529_080000/MANIFEST_SHA256.json",
    ".runtime_freezes/F43_BRODY_V1_FULL_LIVE_SERVER_PORT_MATRIX_AUDIT_20260529_085000/MANIFEST_SHA256.json",
]


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for p in here.parents:
        if (p / ".git").exists():
            return p
    raise RuntimeError("Cannot locate repository root from " + str(here))


def _load_index() -> dict:
    root = _repo_root()
    index_path = root.joinpath(*_INDEX_REL_PARTS)
    with open(index_path, encoding="utf-8") as f:
        raw = json.load(f)
    if raw.get("index_id") != _EXPECTED_INDEX_ID:
        raise ValueError(f"Unexpected index_id: {raw.get('index_id')!r}")
    return raw


def get_index() -> dict:
    """Return a deep copy of the index metadata (no entries)."""
    raw = _load_index()
    return copy.deepcopy({k: v for k, v in raw.items() if k != "entries"})


def get_entries() -> list[dict]:
    """Return all 912 matrix entries (primary + secondary + campaign metadata)."""
    raw = _load_index()
    return copy.deepcopy(raw.get("entries", []))


def get_primary_entries() -> list[dict]:
    """Return only entries where counted_in_brody_primary_census=True (902 entries)."""
    return [e for e in get_entries() if e.get("counted_in_brody_primary_census") is True]


def get_campaign_metadata_entries() -> list[dict]:
    """Return campaign metadata entries (6 entries with brody in name)."""
    return [e for e in get_entries() if e["path"] in _CAMPAIGN_METADATA_PATHS]


def get_secondary_relation_entries() -> list[dict]:
    """Return secondary relation entries (4 entries)."""
    return [e for e in get_entries() if e["path"] in _SECONDARY_RELATION_PATHS]


def get_entries_by_subwave(subwave: str) -> list[dict]:
    """Return primary entries for a given subwave."""
    return [e for e in get_primary_entries() if e.get("assigned_subwave") == subwave]


def get_unresolved_entries() -> list[dict]:
    """Return UNRESOLVED primary entries (0 after reclassification of workflow_governance_readonly)."""
    return [
        e for e in get_primary_entries()
        if e.get("current_relation_status") == "UNRESOLVED"
    ]


def get_wave005a_entries() -> list[dict]:
    """Return all WAVE005_A primary entries."""
    return [
        e for e in get_primary_entries()
        if e.get("assigned_subwave") == "WAVE005_A_BRODY_CORE_GOVERNANCE_AND_TEST"
    ]


def get_wave005a_indexed_entries() -> list[dict]:
    """Return INDEXED WAVE005_A entries (11 functional entries)."""
    return [e for e in get_primary_entries() if e.get("current_relation_status") == "INDEXED"]


def get_double_count_entries() -> list[dict]:
    raw = _load_index()
    return copy.deepcopy(
        raw.get("double_count_status", {}).get("detail", [])
    )


def validate_all_current_paths_exist() -> dict[str, bool]:
    """Check physical existence for primary entries marked current_present=True."""
    root = _repo_root()
    result: dict[str, bool] = {}
    for entry in get_primary_entries():
        if entry.get("current_present", False):
            p = root / entry["path"]
            result[entry["path"]] = p.is_file()
    return result


def get_partition_summary() -> dict[str, int]:
    """Return the PRIMARY partition summary (A-F, primary owners only)."""
    raw = _load_index()
    return copy.deepcopy(raw.get("primary_partition_summary", {}))


def get_five_excluded_from_914() -> list[str]:
    """Return the exact 5 .runtime_freezes paths excluded from the initial scan."""
    return list(_FIVE_EXCLUDED_FROM_914)


def get_unresolved_paths() -> list[str]:
    """Return paths of UNRESOLVED primary entries (0 after reclassification)."""
    return [e["path"] for e in get_unresolved_entries()]


def get_prior_wave_intersections() -> dict:
    """Return Wave001-004 intersection data from index."""
    raw = _load_index()
    return copy.deepcopy(raw.get("prior_wave_intersections", {}))


def summary() -> dict:
    primary = get_primary_entries()
    all_entries = get_entries()
    idx = get_index()
    return {
        "normalized_current_total": len(all_entries),
        "primary_census_total": len(primary),
        "campaign_metadata_total": len(get_campaign_metadata_entries()),
        "secondary_relation_total": len(get_secondary_relation_entries()),
        "initial_scan_914": 914,
        "excluded_from_914": 5,
        "partition": get_partition_summary(),
        "wave005a_indexed": len(get_wave005a_indexed_entries()),
        "wave005a_core_sources": len([e for e in primary if e["path"] in _WAVE005_A_CORE_SOURCES]),
        "wave005a_governance_tests": len([e for e in primary if e["path"] in _WAVE005_A_GOVERNANCE_TESTS]),
        "unresolved": len(get_unresolved_entries()),
        "unresolved_paths": get_unresolved_paths(),
        "double_count_secondary_only": idx.get("double_count_status", {}).get("secondary_relation_only", 0),
        "silent_double_count": 0,
        "prior_wave_primary_owners": get_prior_wave_intersections().get("prior_wave_primary_owners", 0),
        "prior_wave_secondary_intersections": get_prior_wave_intersections().get("prior_wave_secondary_intersections", 0),
        "baseline_reference": 905,
        "baseline_reference_status": "NON_RECONSTRUCTIBLE_AGGREGATE_COUNTER",
        "net_delta_from_baseline": "UNKNOWN",
    }
