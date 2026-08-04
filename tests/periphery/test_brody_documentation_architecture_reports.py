"""
Tests Wave005_E : BRODY_DOCUMENTATION_ARCHITECTURE_AND_REPORTS
124 fichiers primaires, 0 blocker, NON_SOVEREIGN.

Nomenclature : WE-NNN (Wave005_E)
"""
import pytest

from periphery.agents.brody_documentation_architecture_reports import (
    get_index,
    get_entries,
    get_blocker_queue,
    get_governance_invariants,
    get_scope_reconciliation,
    get_remaining_population,
    get_entries_by_role,
    get_entries_by_executability,
    get_entries_by_family,
    get_md_artifact_entries,
    get_json_artifact_entries,
    get_txt_artifact_entries,
    get_py_source_entries,
    get_runtime_report_entries,
    get_architecture_spec_entries,
    validate_all_paths_exist,
    is_scope_complete,
    get_covered_slice,
    has_no_executable_tests,
    summary,
)

# ---------------------------------------------------------------------------
# WE-001  Chargement de base
# ---------------------------------------------------------------------------
def test_we_001_index_loads():
    idx = get_index()
    assert idx is not None


def test_we_002_schema_version():
    idx = get_index()
    assert idx["schema_version"] == "1.0"


def test_we_003_index_id():
    idx = get_index()
    assert idx["index_id"] == "BRODY_DOCUMENTATION_ARCHITECTURE_REPORTS_INDEX_V1"


def test_we_004_campaign():
    idx = get_index()
    assert idx["campaign"] == "AGENTS_FILE_WIRING"


# ---------------------------------------------------------------------------
# WE-010  Comptages primaires
# ---------------------------------------------------------------------------
def test_we_010_total_entries_124():
    entries = get_entries()
    assert len(entries) == 124


def test_we_011_primary_files_accounted_124():
    idx = get_index()
    assert idx["primary_files_accounted"] == 124


def test_we_012_no_blockers():
    idx = get_index()
    assert idx["files_with_explicit_blocker"] == 0


def test_we_013_blocker_queue_empty():
    bq = get_blocker_queue()
    assert len(bq) == 0


# ---------------------------------------------------------------------------
# WE-020  Champs obligatoires de chaque entrée
# ---------------------------------------------------------------------------
_REQUIRED_FIELDS = (
    "path", "sha256", "role", "canonicality_status", "relation_type",
    "owner_subsystem", "status", "semantic_verdict", "executability_status",
)

def test_we_020_all_entries_have_required_fields():
    entries = get_entries()
    for e in entries:
        for f in _REQUIRED_FIELDS:
            assert f in e, f"Champ manquant '{f}' dans {e.get('path')}"


def test_we_021_all_sha256_non_empty():
    entries = get_entries()
    for e in entries:
        assert e["sha256"] and len(e["sha256"]) >= 16, f"sha256 vide pour {e['path']}"


def test_we_022_all_paths_unique():
    entries = get_entries()
    paths = [e["path"] for e in entries]
    assert len(paths) == len(set(paths))


# ---------------------------------------------------------------------------
# WE-030  Rôles valides
# ---------------------------------------------------------------------------
_VALID_ROLES = {
    "BRODY_DOC_SOURCE_MODULE",
    "BRODY_DOC_UI_MODULE",
    "BRODY_ARCHITECTURE_SPEC",
    "BRODY_RUNTIME_REPORT",
    "BRODY_DOCUMENTATION_ARTIFACT",
}

def test_we_030_all_roles_valid():
    entries = get_entries()
    for e in entries:
        assert e["role"] in _VALID_ROLES, f"Rôle invalide '{e['role']}' pour {e['path']}"


_VALID_RELATION_TYPES = {
    "DOCUMENT_LINKED_TO_BRODY_RUNTIME",
    "DOCUMENT_REFERENCED_BY_COMPONENT",
    "ARCHITECTURE_SPEC_LINKED_TO_FROZEN_COMPONENT",
    "RUNTIME_REPORT_LINKED_TO_AUDIT_TRAIL",
    "DOCUMENT_LINKED_TO_BRODY_COMPONENT",
}

def test_we_031_all_relation_types_valid():
    entries = get_entries()
    for e in entries:
        assert e["relation_type"] in _VALID_RELATION_TYPES, (
            f"Relation invalide '{e['relation_type']}' pour {e['path']}"
        )


_VALID_EXECUTABILITY = {
    "EXECUTABLE_PASSES",
    "EXECUTABLE_FAILS",
    "EXECUTABLE_INTERMITTENT",
    "NOT_A_TEST",
    "NOT_EXECUTABLE",
}

def test_we_032_all_executability_valid():
    entries = get_entries()
    for e in entries:
        assert e["executability_status"] in _VALID_EXECUTABILITY, (
            f"Executability invalide pour {e['path']}"
        )


def test_we_033_all_status_valid():
    entries = get_entries()
    for e in entries:
        assert e["status"] == "INDEXED", f"status inattendu pour {e['path']}"


def test_we_034_all_semantic_verdicts_valid():
    entries = get_entries()
    for e in entries:
        assert e["semantic_verdict"] == "VALID_DOCUMENTARY_ARTIFACT", (
            f"semantic_verdict inattendu pour {e['path']}"
        )


def test_we_035_all_canonicality_canonical():
    entries = get_entries()
    for e in entries:
        assert e["canonicality_status"] == "CANONICAL", (
            f"canonicality_status inattendu pour {e['path']}"
        )


def test_we_036_all_owner_subsystem():
    entries = get_entries()
    for e in entries:
        assert e["owner_subsystem"] == "BRODY_DOCUMENTATION_ARCHITECTURE_REPORTS", (
            f"owner_subsystem inattendu pour {e['path']}"
        )


# ---------------------------------------------------------------------------
# WE-040  Distribution des types de fichier
# ---------------------------------------------------------------------------
def test_we_040_md_count_97():
    idx = get_index()
    assert idx["file_type_distribution"]["md_artifacts"] == 97


def test_we_041_json_count_15():
    idx = get_index()
    assert idx["file_type_distribution"]["json_artifacts"] == 15


def test_we_042_txt_count_11():
    idx = get_index()
    assert idx["file_type_distribution"]["txt_artifacts"] == 11


def test_we_043_py_count_1():
    idx = get_index()
    assert idx["file_type_distribution"]["py_source_modules"] == 1


def test_we_044_suffix_total_124():
    idx = get_index()
    dist = idx["file_type_distribution"]
    total = sum(dist.values())
    assert total == 124


def test_we_045_md_entries_97():
    md = get_md_artifact_entries()
    assert len(md) == 97


def test_we_046_json_entries_15():
    jj = get_json_artifact_entries()
    assert len(jj) == 15


def test_we_047_txt_entries_11():
    tt = get_txt_artifact_entries()
    assert len(tt) == 11


def test_we_048_py_entries_1():
    py = get_py_source_entries()
    assert len(py) == 1


# ---------------------------------------------------------------------------
# WE-050  Executabilité
# ---------------------------------------------------------------------------
def test_we_050_executability_audit():
    idx = get_index()
    ea = idx["executability_audit"]
    assert ea.get("NOT_EXECUTABLE", 0) == 123
    assert ea.get("NOT_A_TEST", 0) == 1


def test_we_051_no_executable_tests_flag():
    assert has_no_executable_tests() is True


def test_we_052_py_source_not_a_test():
    py = get_py_source_entries()
    for e in py:
        assert e["executability_status"] == "NOT_A_TEST", (
            f".py entry devrait être NOT_A_TEST : {e['path']}"
        )


def test_we_053_non_py_not_executable():
    entries = get_entries()
    for e in entries:
        if not e["path"].endswith(".py"):
            assert e["executability_status"] == "NOT_EXECUTABLE", (
                f"Entrée non-py devrait être NOT_EXECUTABLE : {e['path']}"
            )


# ---------------------------------------------------------------------------
# WE-060  Scope reconciliation
# ---------------------------------------------------------------------------
def test_we_060_scope_complete_false():
    assert is_scope_complete() is False


def test_we_061_covered_slice():
    assert get_covered_slice() == "WAVE005_E_BRODY_DOCUMENTATION_ARCHITECTURE_AND_REPORTS"


def test_we_062_scope_reconciliation_accounted():
    sr = get_scope_reconciliation()
    assert sr["wave005e_accounted"] == 124


def test_we_063_scope_remaining_66():
    sr = get_scope_reconciliation()
    assert sr["remaining_after_wave005e"] == 66
    assert sr["wave005f_registered"] == 66


def test_we_064_scope_active_total_902():
    sr = get_scope_reconciliation()
    assert sr["current_active_total"] == 902


def test_we_065_scope_prior_waves():
    sr = get_scope_reconciliation()
    assert sr["wave005a_processed"] == 11
    assert sr["wave005b_accounted"] == 144
    assert sr["wave005c_accounted"] == 51
    assert sr["wave005d_accounted"] == 506


def test_we_066_remaining_population_wave005f_66():
    rp = get_remaining_population()
    assert rp["WAVE005_F"] == 66
    assert rp["total_remaining"] == 66


# ---------------------------------------------------------------------------
# WE-070  Gouvernance
# ---------------------------------------------------------------------------
def test_we_070_non_sovereign():
    idx = get_index()
    assert idx["authority"] == "NON_SOVEREIGN"
    assert idx["can_decide"] is False
    assert idx["can_act"] is False
    assert idx["emits_act"] is False
    assert idx["memory_write"] is False


def test_we_071_governance_claims():
    gc = get_governance_invariants()
    assert gc["NON_SOVEREIGN"] is True
    assert gc["documentary_index_only"] is True
    assert gc["no_agent_invoked"] is True
    assert gc["no_model_called"] is True
    assert gc["no_memory_written"] is True
    assert gc["no_act_emitted"] is True
    assert gc["brody_authority"] is False


def test_we_072_model_calls_zero():
    idx = get_index()
    assert idx["model_calls"] == 0


def test_we_073_runtime_not_consumed():
    idx = get_index()
    assert idx["runtime_consumed"] is False


# ---------------------------------------------------------------------------
# WE-080  Cohérence fichiers physiques
# ---------------------------------------------------------------------------
def test_we_080_all_paths_exist():
    result = validate_all_paths_exist()
    missing = [p for p, exists in result.items() if not exists]
    assert missing == [], f"Fichiers manquants : {missing}"


# ---------------------------------------------------------------------------
# WE-090  Rôle distribution
# ---------------------------------------------------------------------------
def test_we_090_runtime_report_82():
    rr = get_runtime_report_entries()
    assert len(rr) == 82


def test_we_091_documentation_artifact_35():
    da = get_entries_by_role("BRODY_DOCUMENTATION_ARTIFACT")
    assert len(da) == 35


def test_we_092_architecture_spec_6():
    arch = get_architecture_spec_entries()
    assert len(arch) == 6


def test_we_093_doc_source_module_1():
    src = get_entries_by_role("BRODY_DOC_SOURCE_MODULE")
    assert len(src) == 1


def test_we_094_role_total_sums_to_124():
    entries = get_entries()
    from collections import Counter
    role_dist = Counter(e["role"] for e in entries)
    assert sum(role_dist.values()) == 124


# ---------------------------------------------------------------------------
# WE-100  Summary
# ---------------------------------------------------------------------------
def test_we_100_summary_total():
    s = summary()
    assert s["total"] == 124


def test_we_101_summary_md_count():
    s = summary()
    assert s["md_count"] == 97


def test_we_102_summary_not_executable():
    s = summary()
    assert s["not_executable_count"] == 123
    assert s["not_a_test_count"] == 1
