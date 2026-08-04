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
    get_relation_evidence_audit,
    get_primary_proved_count,
    get_primary_blocker_count,
    get_primary_unresolved_count,
    get_union_recalculation,
    get_group_rules,
    get_final_status,
    get_legacy_duplicate_report,
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
    # Initial types
    "DOCUMENT_LINKED_TO_BRODY_RUNTIME",
    "DOCUMENT_REFERENCED_BY_COMPONENT",
    "ARCHITECTURE_SPEC_LINKED_TO_FROZEN_COMPONENT",
    "RUNTIME_REPORT_LINKED_TO_AUDIT_TRAIL",
    "DOCUMENT_LINKED_TO_BRODY_COMPONENT",
    # Gate V1 enriched types
    "GENERATED_REPORT_LINKED_TO_RUNTIME_RUN",
    "GENERATED_REPORT_LINKED_TO_FREEZE_MANIFEST",
    "HISTORICAL_REPORT_LINKED_TO_ARCHIVE_INDEX",
    "DOCUMENT_LINKED_TO_COMPONENT",
    "DOCUMENT_LINKED_TO_CANONICAL_INDEX",
    "DOCUMENT_LINKED_TO_PROTOCOL",
    "HISTORICAL_DOCUMENT_LINKED_TO_ARCHIVE",
    "ARCH_SPEC_REFERENCED_BY_COMPONENT",
    "ARCH_SPEC_REFERENCED_BY_RUNTIME_CONTRACT",
    "ARCH_SPEC_LINKED_TO_CANONICAL_INDEX",
    "DOC_SOURCE_LINKED_TO_EXECUTABLE_TEST",
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
def test_we_060_scope_complete_true_after_gate():
    # After Gate V1: all 124 proved, no blockers → scope_complete=True (CLOSED)
    assert is_scope_complete() is True


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


# ---------------------------------------------------------------------------
# WE-110  Relation & Provenance Gate V1
# ---------------------------------------------------------------------------

def test_we_110_all_124_proved():
    """Tous les 124 fichiers doivent avoir une preuve de relation valide."""
    assert get_primary_proved_count() == 124


def test_we_111_zero_blockers():
    assert get_primary_blocker_count() == 0


def test_we_112_zero_unresolved():
    assert get_primary_unresolved_count() == 0


def test_we_113_final_status_closed():
    assert get_final_status() == "AGENTS_FILE_WIRING_WAVE005_E_CLOSED"


def test_we_114_scope_complete_true():
    assert is_scope_complete() is True


def test_we_115_entries_have_current_status():
    entries = get_entries()
    valid_statuses = {
        "PROVED_GENERATOR_RELATION",
        "PROVED_COMPONENT_RELATION",
        "PROVED_CANONICAL_INDEX_RELATION",
        "PROVED_ARCHIVE_OR_MANIFEST_RELATION",
        "PROVED_SUCCESSOR_RELATION",
        "EXPLICIT_BLOCKER",
        "RELATION_UNRESOLVED_AFTER_REVIEW",
    }
    for e in entries:
        s = e.get("current_status", "")
        assert s in valid_statuses, f"current_status invalide '{s}' pour {e['path']}"


def test_we_116_entries_have_evidence():
    """Chaque entrée doit avoir un champ evidence non vide."""
    entries = get_entries()
    for e in entries:
        ev = e.get("evidence", "")
        assert ev and ev not in {"FILE_EXISTS", "SHA256_VERIFIED", "INDEXED", "DOCUMENT_ONLY", "RUNTIME_REPORT", "NOT_EXECUTABLE"}, (
            f"Preuve insuffisante pour {e['path']}: {ev!r}"
        )


def test_we_117_entries_have_relation_type():
    entries = get_entries()
    for e in entries:
        assert e.get("relation_type"), f"relation_type vide pour {e['path']}"


def test_we_118_no_runtime_report_role_used_as_sole_proof():
    """RUNTIME_REPORT ne doit pas être utilisé comme seule preuve."""
    entries = get_entries()
    for e in entries:
        ev = e.get("evidence", "")
        assert ev.strip() != "RUNTIME_REPORT", f"RUNTIME_REPORT utilisé comme preuve pour {e['path']}"


# ---------------------------------------------------------------------------
# WE-120  Runtime report audit
# ---------------------------------------------------------------------------

def test_we_120_runtime_report_total_82():
    audit = get_relation_evidence_audit()
    assert audit["runtime_report_audit"]["total"] == 82


def test_we_121_runtime_report_proved_generator_or_run():
    audit = get_relation_evidence_audit()
    rr = audit["runtime_report_audit"]
    proved = rr["REPORTS_WITH_PROVED_GENERATOR_OR_RUN"]
    historical = rr["REPORTS_HISTORICAL_WITH_ARCHIVE_RELATION"]
    assert rr["REPORTS_WITH_EXPLICIT_BLOCKER"] == 0
    assert rr["REPORTS_UNRESOLVED"] == 0
    assert proved + historical == 82, f"{proved}+{historical}!=82"


def test_we_122_freeze_reports_have_freeze_relation():
    entries = get_entries()
    freeze = [e for e in entries
              if e["role"] == "BRODY_RUNTIME_REPORT"
              and "FREEZE" in e["path"].split("/")[-1]
              and "archive" not in e["path"]]
    for e in freeze:
        assert e["relation_type"] == "GENERATED_REPORT_LINKED_TO_FREEZE_MANIFEST", (
            f"Freeze report avec mauvaise relation: {e['path']}"
        )


def test_we_123_archive_reports_have_historical_relation():
    entries = get_entries()
    archive = [e for e in entries
               if "archive/phase10_12_legacy_untracked" in e["path"]
               and e["role"] == "BRODY_RUNTIME_REPORT"
               and "PHASE12G_LEGACY_UNTRACKED_ARCHIVE_MANIFEST" not in e["path"]]
    for e in archive:
        assert e["relation_type"] == "HISTORICAL_REPORT_LINKED_TO_ARCHIVE_INDEX", (
            f"Archive report avec mauvaise relation: {e['path']}"
        )


def test_we_124_group_rules_present():
    grs = get_group_rules()
    assert "GROUP_RULE_A" in grs
    assert "GROUP_RULE_B" in grs
    assert "GROUP_RULE_C" in grs
    for key in ("GROUP_RULE_A", "GROUP_RULE_B", "GROUP_RULE_C"):
        gr = grs[key]
        assert "group_rule" in gr
        assert "path_pattern" in gr
        assert "generator" in gr
        assert "members_checked" in gr
        assert "exceptions" in gr
        assert "evidence" in gr


# ---------------------------------------------------------------------------
# WE-130  Doc artifact audit
# ---------------------------------------------------------------------------

def test_we_130_doc_artifact_total_35():
    audit = get_relation_evidence_audit()
    assert audit["doc_artifact_audit"]["total"] == 35


def test_we_131_doc_artifact_all_covered():
    audit = get_relation_evidence_audit()
    da = audit["doc_artifact_audit"]
    total = da["CURRENT_DOCUMENTS_WITH_COMPONENT"] + da["HISTORICAL_OR_LEGACY_DOCUMENTS"]
    assert total == 35, f"Total doc artifact couverture: {total} != 35"
    assert da["DOCUMENTS_WITH_EXPLICIT_BLOCKER"] == 0
    assert da["DOCUMENTS_UNRESOLVED"] == 0


# ---------------------------------------------------------------------------
# WE-140  Arch spec audit
# ---------------------------------------------------------------------------

def test_we_140_arch_spec_total_6():
    audit = get_relation_evidence_audit()
    assert audit["arch_spec_audit"]["total"] == 6


def test_we_141_arch_spec_all_proved():
    audit = get_relation_evidence_audit()
    aa = audit["arch_spec_audit"]
    assert aa["ARCH_SPECS_WITH_PROVED_RELATION"] == 6
    assert aa["ARCH_SPECS_WITH_EXPLICIT_BLOCKER"] == 0
    assert aa["ARCH_SPECS_UNRESOLVED"] == 0


def test_we_142_arch_specs_have_canonical_component():
    entries = get_entries()
    arch = [e for e in entries if e["role"] == "BRODY_ARCHITECTURE_SPEC"]
    for e in arch:
        assert e.get("canonical_component"), f"canonical_component vide pour {e['path']}"
        assert e.get("implementation_target"), f"implementation_target vide pour {e['path']}"


# ---------------------------------------------------------------------------
# WE-150  Python source audit
# ---------------------------------------------------------------------------

def test_we_150_py_source_total_1():
    audit = get_relation_evidence_audit()
    assert audit["py_source_audit"]["total"] == 1


def test_we_151_py_source_path():
    audit = get_relation_evidence_audit()
    assert audit["py_source_audit"]["path"] == "demos/local_flows/memory_brody_graphiti_flow.py"


def test_we_152_py_source_proved():
    audit = get_relation_evidence_audit()
    pa = audit["py_source_audit"]
    assert pa["PY_SOURCE_WITH_PROVED_RELATION"] == 1
    assert pa["PY_SOURCE_WITH_EXPLICIT_BLOCKER"] == 0
    assert pa["PY_SOURCE_UNRESOLVED"] == 0
    assert pa["relation_type"] == "DOC_SOURCE_LINKED_TO_EXECUTABLE_TEST"
    assert len(pa["test_consumers"]) == 3


# ---------------------------------------------------------------------------
# WE-160  JSON et TXT audit
# ---------------------------------------------------------------------------

def test_we_160_json_total_15():
    audit = get_relation_evidence_audit()
    ja = audit["json_audit"]
    total = ja["JSON_LOADED_OR_CONSUMED"] + ja["JSON_GENERATED_WITH_PROVENANCE"] + ja["JSON_LINKED_TO_REPORT"]
    assert total == 15, f"JSON total {total} != 15"
    assert ja["JSON_WITH_EXPLICIT_BLOCKER"] == 0
    assert ja["JSON_UNRESOLVED"] == 0


def test_we_161_txt_total_11():
    audit = get_relation_evidence_audit()
    ta = audit["txt_audit"]
    total = ta["TXT_GENERATED_WITH_PROVENANCE"] + ta["TXT_LINKED_TO_COMPONENT"] + ta["TXT_HISTORICAL_ARCHIVED"]
    assert total == 11, f"TXT total {total} != 11"
    assert ta["TXT_WITH_EXPLICIT_BLOCKER"] == 0
    assert ta["TXT_UNRESOLVED"] == 0


# ---------------------------------------------------------------------------
# WE-170  Legacy / Duplicate / Superseded
# ---------------------------------------------------------------------------

def test_we_170_no_identical_hash_duplicates():
    report = get_legacy_duplicate_report()
    assert report["IDENTICAL_HASH_DUPLICATES"] == []


def test_we_171_no_silent_double_count():
    u = get_union_recalculation()
    assert u["silent_double_count"] == 0


def test_we_172_no_new_overlaps_with_prior_waves():
    u = get_union_recalculation()
    assert u["new_overlaps_w5e_with_prior"] == 0


# ---------------------------------------------------------------------------
# WE-180  Union recalculation
# ---------------------------------------------------------------------------

def test_we_180_gross_1858():
    u = get_union_recalculation()
    assert u["gross_primary_wave_index_entries"] == 1858


def test_we_181_unique_1691():
    u = get_union_recalculation()
    assert u["unique_primary_paths_accounted"] == 1691


def test_we_182_overlap_167():
    u = get_union_recalculation()
    assert u["primary_overlap_count"] == 167


def test_we_183_union_formula():
    u = get_union_recalculation()
    assert u["gross_primary_wave_index_entries"] - u["primary_overlap_count"] == u["unique_primary_paths_accounted"]


# ---------------------------------------------------------------------------
# WE-190  Aucune relation runtime inventée
# ---------------------------------------------------------------------------

_FORBIDDEN_SOLE_PROOFS = {
    "FILE_EXISTS", "SHA256_VERIFIED", "INDEXED",
    "DOCUMENT_ONLY", "RUNTIME_REPORT", "NOT_EXECUTABLE",
}

def test_we_190_no_forbidden_sole_proof():
    entries = get_entries()
    for e in entries:
        ev = e.get("evidence", "")
        assert ev.strip() not in _FORBIDDEN_SOLE_PROOFS, (
            f"Preuve interdite pour {e['path']}: {ev!r}"
        )


def test_we_191_no_runtime_consumed_invented():
    """Aucun rapport ne prétend être consommé par le runtime sans preuve."""
    entries = get_entries()
    for e in entries:
        if e["role"] == "BRODY_RUNTIME_REPORT":
            # runtime report should NOT claim consumer_or_destination is a runtime process
            # (they are documentation, not runtime-consumed artifacts)
            consumer = e.get("consumer_or_destination", "")
            assert consumer not in {"BRODY_RUNTIME", "RUNTIME_CONSUMER", "BRODY_AGENT"}, (
                f"Relation runtime inventée pour {e['path']}: consumer={consumer}"
            )


def test_we_192_no_brody_authority():
    gc = get_governance_invariants()
    assert gc["brody_authority"] is False


def test_we_193_no_memory_write():
    gc = get_governance_invariants()
    assert gc["no_memory_written"] is True


def test_we_194_no_act_emitted():
    gc = get_governance_invariants()
    assert gc["no_act_emitted"] is True
