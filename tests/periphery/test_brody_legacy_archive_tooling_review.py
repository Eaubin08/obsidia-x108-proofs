"""
Tests for BRODY_LEGACY_ARCHIVE_TOOLING_AND_REVIEW Wave005_F documentary index.

Coverage: WF-001 to WF-160
NON_SOVEREIGN: can_decide=false, can_act=false, emits_act=false, memory_write=false.
"""
import pytest
from periphery.agents.brody_legacy_archive_tooling_review import (
    get_index,
    get_entries,
    get_entries_by_role,
    get_entries_by_executability,
    get_entries_by_relation_type,
    get_md_artifact_entries,
    get_json_artifact_entries,
    get_txt_artifact_entries,
    get_py_source_entries,
    get_tsx_entries,
    get_ts_entries,
    get_freeze_report_entries,
    get_freeze_foundation_doc_entries,
    get_freeze_manifest_entries,
    get_freeze_recovery_artifact_entries,
    get_tooling_module_entries,
    get_ui_component_entries,
    get_ui_fallback_module_entries,
    get_legacy_test_entries,
    get_ui_test_entries,
    get_blocker_queue,
    get_governance_invariants,
    get_scope_reconciliation,
    get_remaining_population,
    is_scope_complete,
    get_covered_slice,
    has_executable_tests,
    get_relation_evidence_audit,
    get_primary_proved_count,
    get_primary_blocker_count,
    get_primary_unresolved_count,
    get_union_recalculation,
    get_group_rules,
    get_final_status,
    summary,
    _VALID_ROLES,
    _VALID_RELATION_TYPES,
    _VALID_EXECUTABILITY,
    _FORBIDDEN_SOLE_PROOFS,
)


# ---------------------------------------------------------------------------
# WF-001 to WF-010: Index identity and schema
# ---------------------------------------------------------------------------

def test_wf001_index_id():
    idx = get_index()
    assert idx["index_id"] == "BRODY_LEGACY_ARCHIVE_TOOLING_REVIEW_INDEX_V1"


def test_wf002_schema_version():
    idx = get_index()
    assert idx["schema_version"] == "1.0"


def test_wf003_covered_slice():
    assert get_covered_slice() == "WAVE005_F_BRODY_LEGACY_ARCHIVE_TOOLING_AND_REVIEW"


def test_wf004_campaign():
    idx = get_index()
    assert idx["campaign"] == "AGENTS_FILE_WIRING"


def test_wf005_authority_non_sovereign():
    idx = get_index()
    assert idx["authority"] == "NON_SOVEREIGN"


def test_wf006_can_decide_false():
    idx = get_index()
    assert idx["can_decide"] is False


def test_wf007_can_act_false():
    idx = get_index()
    assert idx["can_act"] is False


def test_wf008_emits_act_false():
    idx = get_index()
    assert idx["emits_act"] is False


def test_wf009_memory_write_false():
    idx = get_index()
    assert idx["memory_write"] is False


def test_wf010_final_status_indexed():
    assert get_final_status() == "AGENTS_FILE_WIRING_WAVE005_F_INDEXED"


# ---------------------------------------------------------------------------
# WF-011 to WF-020: Total counts
# ---------------------------------------------------------------------------

def test_wf011_total_entries_66():
    assert len(get_entries()) == 66


def test_wf012_no_duplicate_paths():
    paths = [e["path"] for e in get_entries()]
    assert len(paths) == len(set(paths))


def test_wf013_md_count_45():
    assert len(get_md_artifact_entries()) == 45


def test_wf014_json_count_8():
    assert len(get_json_artifact_entries()) == 8


def test_wf015_txt_count_7():
    assert len(get_txt_artifact_entries()) == 7


def test_wf016_py_count_4():
    assert len(get_py_source_entries()) == 4


def test_wf017_tsx_count_1():
    assert len(get_tsx_entries()) == 1


def test_wf018_ts_count_1():
    assert len(get_ts_entries()) == 1


def test_wf019_primary_proved_66():
    assert get_primary_proved_count() == 66


def test_wf020_primary_blocker_0():
    assert get_primary_blocker_count() == 0


# ---------------------------------------------------------------------------
# WF-021 to WF-030: Role distribution
# ---------------------------------------------------------------------------

def test_wf021_freeze_report_count_42():
    assert len(get_freeze_report_entries()) == 42


def test_wf022_freeze_foundation_doc_count_3():
    assert len(get_freeze_foundation_doc_entries()) == 3


def test_wf023_freeze_manifest_count_8():
    assert len(get_freeze_manifest_entries()) == 8


def test_wf024_freeze_recovery_artifact_count_7():
    assert len(get_freeze_recovery_artifact_entries()) == 7


def test_wf025_tooling_module_count_2():
    assert len(get_tooling_module_entries()) == 2


def test_wf026_ui_component_count_1():
    assert len(get_ui_component_entries()) == 1


def test_wf027_ui_fallback_module_count_1():
    assert len(get_ui_fallback_module_entries()) == 1


def test_wf028_legacy_test_count_1():
    assert len(get_legacy_test_entries()) == 1


def test_wf029_ui_test_count_1():
    assert len(get_ui_test_entries()) == 1


def test_wf030_role_total_sums_to_66():
    s = summary()
    total = sum(v for k, v in s["by_role"].items())
    assert total == 66


# ---------------------------------------------------------------------------
# WF-031 to WF-040: Valid roles and relation types in validator sets
# ---------------------------------------------------------------------------

def test_wf031_valid_roles_set():
    expected = {
        "BRODY_FREEZE_REPORT", "BRODY_FREEZE_FOUNDATION_DOC", "BRODY_FREEZE_MANIFEST",
        "BRODY_FREEZE_RECOVERY_ARTIFACT", "BRODY_TOOLING_MODULE", "BRODY_UI_COMPONENT",
        "BRODY_UI_FALLBACK_MODULE", "BRODY_LEGACY_TEST", "BRODY_UI_TEST",
    }
    assert expected <= _VALID_ROLES


def test_wf032_valid_relation_types_set():
    expected = {
        "FREEZE_REPORT_LINKED_TO_ARCHIVE_INDEX",
        "FREEZE_FOUNDATION_DOC_LINKED_TO_CANONICAL_SPEC",
        "FREEZE_MANIFEST_LINKED_TO_FOUNDATION_DOC",
        "FREEZE_MANIFEST_LINKED_TO_ARCHIVE_INDEX",
        "FREEZE_RECOVERY_ARTIFACT_LINKED_TO_VALIDATION_RUN",
        "TOOLING_MODULE_LINKED_TO_RUNTIME_API",
        "UI_COMPONENT_LINKED_TO_WORKBENCH_APP",
        "UI_FALLBACK_MODULE_LINKED_TO_RUNTIME_API",
        "LEGACY_TEST_LINKED_TO_BRODY_API",
        "UI_TEST_LINKED_TO_UI_COMPONENT",
    }
    assert expected <= _VALID_RELATION_TYPES


def test_wf033_all_entries_have_valid_role():
    for e in get_entries():
        assert e["role"] in _VALID_ROLES, f"Invalid role in {e['path']}: {e['role']}"


def test_wf034_all_entries_have_valid_relation_type():
    for e in get_entries():
        assert e["relation_type"] in _VALID_RELATION_TYPES, f"Invalid relation in {e['path']}: {e['relation_type']}"


def test_wf035_all_entries_have_valid_executability():
    for e in get_entries():
        assert e["executability_status"] in _VALID_EXECUTABILITY, f"Invalid exec in {e['path']}"


def test_wf036_forbidden_sole_proofs_defined():
    assert "FILE_EXISTS" in _FORBIDDEN_SOLE_PROOFS
    assert "SHA256_VERIFIED" in _FORBIDDEN_SOLE_PROOFS
    assert "INDEXED" in _FORBIDDEN_SOLE_PROOFS


def test_wf037_no_entry_has_forbidden_sole_evidence():
    for e in get_entries():
        ev = e.get("evidence", "")
        assert ev not in _FORBIDDEN_SOLE_PROOFS, f"Forbidden sole proof in {e['path']}: {ev!r}"


def test_wf038_all_entries_have_sha256():
    for e in get_entries():
        sha = e.get("sha256", "")
        assert len(sha) == 64, f"Invalid SHA256 length in {e['path']}"
        assert sha.isalnum(), f"Non-hex SHA256 in {e['path']}"


def test_wf039_all_entries_canonical():
    for e in get_entries():
        assert e.get("canonicality_status") == "CANONICAL", f"Non-canonical: {e['path']}"


def test_wf040_all_entries_confirmed():
    for e in get_entries():
        assert e.get("semantic_verdict") == "CONFIRMED", f"Not confirmed: {e['path']}"


# ---------------------------------------------------------------------------
# WF-041 to WF-050: Executability distribution
# ---------------------------------------------------------------------------

def test_wf041_not_executable_count_62():
    assert len(get_entries_by_executability("NOT_EXECUTABLE")) == 62


def test_wf042_not_a_test_count_2():
    assert len(get_entries_by_executability("NOT_A_TEST")) == 2


def test_wf043_executable_passes_count_2():
    assert len(get_entries_by_executability("EXECUTABLE_PASSES")) == 2


def test_wf044_has_executable_tests_true():
    assert has_executable_tests() is True


def test_wf045_scope_complete_false():
    assert is_scope_complete() is False


def test_wf046_blocker_queue_empty():
    assert get_blocker_queue() == []


def test_wf047_primary_unresolved_0():
    assert get_primary_unresolved_count() == 0


def test_wf048_not_a_test_paths():
    entries = get_entries_by_executability("NOT_A_TEST")
    paths = {e["path"] for e in entries}
    assert "apps/obsidia-workbench/audit_brody.py" in paths
    assert "tools/brody_chat.py" in paths


def test_wf049_executable_passes_paths():
    entries = get_entries_by_executability("EXECUTABLE_PASSES")
    paths = {e["path"] for e in entries}
    assert "tests/legacy_root/brody_api/test_conscience.py" in paths
    assert "tests/ui/test_chatview_brody_terminal_view.py" in paths


def test_wf050_md_files_not_executable():
    for e in get_md_artifact_entries():
        assert e["executability_status"] == "NOT_EXECUTABLE", f"MD file should be NOT_EXECUTABLE: {e['path']}"


# ---------------------------------------------------------------------------
# WF-051 to WF-060: Governance invariants
# ---------------------------------------------------------------------------

def test_wf051_no_model_calls():
    inv = get_governance_invariants()
    assert inv.get("no_model_calls") is True


def test_wf052_no_runtime_consumed():
    inv = get_governance_invariants()
    assert inv.get("no_runtime_consumed") is True


def test_wf053_no_brody_authority():
    inv = get_governance_invariants()
    assert inv.get("no_brody_authority") is True


def test_wf054_no_memory_write():
    inv = get_governance_invariants()
    assert inv.get("no_memory_write") is True


def test_wf055_no_emits_act():
    inv = get_governance_invariants()
    assert inv.get("no_emits_act") is True


def test_wf056_scope_reconciliation_files_66():
    sr = get_scope_reconciliation()
    assert sr.get("files_in_scope") == 66
    assert sr.get("files_accounted") == 66
    assert sr.get("files_remaining") == 0


def test_wf057_scope_reconciliation_subwave():
    sr = get_scope_reconciliation()
    assert sr.get("assigned_subwave") == "WAVE005_F"


def test_wf058_remaining_population_zero():
    rp = get_remaining_population()
    assert rp.get("remaining_after_wave005f") == 0


def test_wf059_all_entries_owner_subsystem():
    for e in get_entries():
        assert e.get("owner_subsystem") == "BRODY_LEGACY_ARCHIVE_TOOLING_AND_REVIEW"


def test_wf060_all_entries_status_indexed():
    for e in get_entries():
        assert e.get("status") == "INDEXED"
        assert e.get("current_status") == "INDEXED"


# ---------------------------------------------------------------------------
# WF-061 to WF-080: GROUP_RULE_D — freeze reports
# ---------------------------------------------------------------------------

def test_wf061_group_rule_d_exists():
    rules = get_group_rules()
    assert "GROUP_RULE_D" in rules


def test_wf062_group_rule_d_count_42():
    rules = get_group_rules()
    assert rules["GROUP_RULE_D"]["members_checked"] == 42


def test_wf063_group_rule_d_relation_type():
    rules = get_group_rules()
    assert rules["GROUP_RULE_D"]["relation_type"] == "FREEZE_REPORT_LINKED_TO_ARCHIVE_INDEX"


def test_wf064_group_rule_d_git_anchor():
    rules = get_group_rules()
    assert "48ea81a" in rules["GROUP_RULE_D"]["git_anchor"]


def test_wf065_freeze_reports_in_docs_freeze():
    for e in get_freeze_report_entries():
        assert e["path"].startswith("docs/freeze/"), f"Freeze report not in docs/freeze/: {e['path']}"


def test_wf066_freeze_reports_are_md():
    for e in get_freeze_report_entries():
        assert e["path"].endswith(".md"), f"Freeze report not .md: {e['path']}"


def test_wf067_freeze_reports_not_foundation():
    for e in get_freeze_report_entries():
        assert "FOUNDATION_A" not in e["path"]
        assert "FOUNDATION_B" not in e["path"]
        assert "FOUNDATION_C" not in e["path"]


def test_wf068_freeze_report_evidence_references_group_rule_d():
    for e in get_freeze_report_entries():
        assert "GROUP_RULE_D" in e["evidence"], f"Missing GROUP_RULE_D in evidence: {e['path']}"


def test_wf069_freeze_report_relation_type():
    for e in get_freeze_report_entries():
        assert e["relation_type"] == "FREEZE_REPORT_LINKED_TO_ARCHIVE_INDEX"


def test_wf070_specific_freeze_reports_present():
    paths = {e["path"] for e in get_freeze_report_entries()}
    assert "docs/freeze/BRODY_FULL_LIVE_RUNTIME_CLOSE_REPORT.md" in paths
    assert "docs/freeze/FINAL_BRODY_FULL_CLOSE_REPORT.md" in paths
    assert "docs/freeze/V5B_PLUS_BRODY_RESPONSE_MODULE_AUDIT.md" in paths
    assert "docs/freeze/BRODY_V1_4_12A_FULL_INTEGRATION_CLOSE_REPORT.md" in paths


# ---------------------------------------------------------------------------
# WF-071 to WF-090: Foundation docs, manifests, recovery artifacts
# ---------------------------------------------------------------------------

def test_wf071_foundation_docs_status_headers():
    entries = get_freeze_foundation_doc_entries()
    statuses = {e.get("freeze_status") for e in entries}
    assert "FOUNDATION_A_PARTIAL" in statuses
    assert "FOUNDATION_B_READY" in statuses
    assert "FOUNDATION_C_READY" in statuses


def test_wf072_foundation_docs_have_json_pair():
    for e in get_freeze_foundation_doc_entries():
        assert "json_pair" in e, f"Missing json_pair: {e['path']}"
        assert e["json_pair"].endswith(".json")


def test_wf073_foundation_json_have_md_pair():
    entries = [e for e in get_freeze_manifest_entries() if e["relation_type"] == "FREEZE_MANIFEST_LINKED_TO_FOUNDATION_DOC"]
    assert len(entries) == 3
    for e in entries:
        assert "md_pair" in e, f"Missing md_pair: {e['path']}"


def test_wf074_foundation_json_paths():
    entries = [e for e in get_freeze_manifest_entries() if e["relation_type"] == "FREEZE_MANIFEST_LINKED_TO_FOUNDATION_DOC"]
    paths = {e["path"] for e in entries}
    assert "docs/freeze/BRODY_FOUNDATION_A_PROJECT_MEMORY_FREEZE.json" in paths
    assert "docs/freeze/BRODY_FOUNDATION_B_SESSION_MEMORY_FOLLOWUP_FREEZE.json" in paths
    assert "docs/freeze/BRODY_FOUNDATION_C_TRUE_RESPONSE_STRUCTURE_FREEZE.json" in paths


def test_wf075_group_rule_e_exists():
    rules = get_group_rules()
    assert "GROUP_RULE_E" in rules


def test_wf076_group_rule_e_count_5():
    rules = get_group_rules()
    assert rules["GROUP_RULE_E"]["members_checked"] == 5


def test_wf077_group_rule_f_exists():
    rules = get_group_rules()
    assert "GROUP_RULE_F" in rules


def test_wf078_group_rule_f_count_7():
    rules = get_group_rules()
    assert rules["GROUP_RULE_F"]["members_checked"] == 7


def test_wf079_recovery_artifacts_in_recovery_dir():
    for e in get_freeze_recovery_artifact_entries():
        assert "BRODY_RIGHTS_AUTHORITY_FINAL_VALIDATION_RECOVERY_20260520_064234" in e["path"]
        assert e["path"].endswith(".txt")


def test_wf080_recovery_artifact_evidence_references_group_rule_f():
    for e in get_freeze_recovery_artifact_entries():
        assert "GROUP_RULE_F" in e["evidence"]


# ---------------------------------------------------------------------------
# WF-081 to WF-100: Tooling, UI, tests individual proofs
# ---------------------------------------------------------------------------

def test_wf081_audit_brody_py_role():
    entries = get_tooling_module_entries()
    e = next((x for x in entries if x["path"] == "apps/obsidia-workbench/audit_brody.py"), None)
    assert e is not None
    assert e["role"] == "BRODY_TOOLING_MODULE"
    assert e["executability_status"] == "NOT_A_TEST"


def test_wf082_audit_brody_py_evidence():
    entries = get_tooling_module_entries()
    e = next(x for x in entries if x["path"] == "apps/obsidia-workbench/audit_brody.py")
    assert "8c38f54" in e["evidence"] or "requests" in e["evidence"]


def test_wf083_brody_panel_tsx_role():
    entries = get_ui_component_entries()
    assert len(entries) == 1
    e = entries[0]
    assert e["path"] == "apps/obsidia-workbench/src/components/BrodyPanel.tsx"
    assert e["role"] == "BRODY_UI_COMPONENT"
    assert e["executability_status"] == "NOT_EXECUTABLE"


def test_wf084_brody_panel_tsx_evidence():
    entries = get_ui_component_entries()
    e = entries[0]
    assert "7495ca4" in e["evidence"]


def test_wf085_brody_response_composer_role():
    entries = get_ui_fallback_module_entries()
    assert len(entries) == 1
    e = entries[0]
    assert e["path"] == "apps/obsidia-workbench/src/lib/brodyResponseComposer.ts"
    assert e["role"] == "BRODY_UI_FALLBACK_MODULE"


def test_wf086_brody_response_composer_evidence():
    entries = get_ui_fallback_module_entries()
    e = entries[0]
    assert "FALLBACK ONLY" in e["evidence"] or "7495ca4" in e["evidence"]


def test_wf087_test_conscience_role():
    entries = get_legacy_test_entries()
    assert len(entries) == 1
    e = entries[0]
    assert e["path"] == "tests/legacy_root/brody_api/test_conscience.py"
    assert e["role"] == "BRODY_LEGACY_TEST"
    assert e["executability_status"] == "EXECUTABLE_PASSES"


def test_wf088_test_conscience_evidence():
    entries = get_legacy_test_entries()
    e = entries[0]
    assert "cdb636d" in e["evidence"]
    assert "CI" in e["evidence"] or "TestClient" in e["evidence"]


def test_wf089_test_chatview_role():
    entries = get_ui_test_entries()
    assert len(entries) == 1
    e = entries[0]
    assert e["path"] == "tests/ui/test_chatview_brody_terminal_view.py"
    assert e["role"] == "BRODY_UI_TEST"
    assert e["executability_status"] == "EXECUTABLE_PASSES"


def test_wf090_test_chatview_evidence():
    entries = get_ui_test_entries()
    e = entries[0]
    assert "5c07997" in e["evidence"] or "ChatView" in e["evidence"]


# ---------------------------------------------------------------------------
# WF-091 to WF-100: brody_chat.py and tools
# ---------------------------------------------------------------------------

def test_wf091_brody_chat_py_role():
    entries = get_tooling_module_entries()
    e = next((x for x in entries if x["path"] == "tools/brody_chat.py"), None)
    assert e is not None
    assert e["role"] == "BRODY_TOOLING_MODULE"
    assert e["executability_status"] == "NOT_A_TEST"


def test_wf092_brody_chat_py_evidence():
    entries = get_tooling_module_entries()
    e = next(x for x in entries if x["path"] == "tools/brody_chat.py")
    assert "fe4a0b5" in e["evidence"] or "CLI" in e["evidence"]


def test_wf093_tooling_relation_type():
    for e in get_tooling_module_entries():
        assert e["relation_type"] == "TOOLING_MODULE_LINKED_TO_RUNTIME_API"


def test_wf094_ui_component_relation_type():
    for e in get_ui_component_entries():
        assert e["relation_type"] == "UI_COMPONENT_LINKED_TO_WORKBENCH_APP"


def test_wf095_ui_fallback_relation_type():
    for e in get_ui_fallback_module_entries():
        assert e["relation_type"] == "UI_FALLBACK_MODULE_LINKED_TO_RUNTIME_API"


def test_wf096_legacy_test_relation_type():
    for e in get_legacy_test_entries():
        assert e["relation_type"] == "LEGACY_TEST_LINKED_TO_BRODY_API"


def test_wf097_ui_test_relation_type():
    for e in get_ui_test_entries():
        assert e["relation_type"] == "UI_TEST_LINKED_TO_UI_COMPONENT"


def test_wf098_json_artifacts_not_executable():
    for e in get_json_artifact_entries():
        assert e["executability_status"] == "NOT_EXECUTABLE"


def test_wf099_txt_artifacts_not_executable():
    for e in get_txt_artifact_entries():
        assert e["executability_status"] == "NOT_EXECUTABLE"


def test_wf100_tsx_ts_not_executable():
    for e in get_tsx_entries() + get_ts_entries():
        assert e["executability_status"] == "NOT_EXECUTABLE"


# ---------------------------------------------------------------------------
# WF-101 to WF-120: Union recalculation
# ---------------------------------------------------------------------------

def test_wf101_union_recalculation_exists():
    u = get_union_recalculation()
    assert u, "union_recalculation must be present"


def test_wf102_prior_unique_1691():
    u = get_union_recalculation()
    assert u["prior_unique_primary_paths"] == 1691


def test_wf103_wave005f_new_66():
    u = get_union_recalculation()
    assert u["wave005f_new_primary_paths"] == 66


def test_wf104_overlap_zero():
    u = get_union_recalculation()
    assert u["cross_wave_overlap_with_prior"] == 0


def test_wf105_new_unique_total_1757():
    u = get_union_recalculation()
    assert u["new_unique_primary_total"] == 1757


def test_wf106_formula_verification():
    u = get_union_recalculation()
    computed = u["prior_unique_primary_paths"] + u["wave005f_new_primary_paths"] - u["cross_wave_overlap_with_prior"]
    assert computed == u["new_unique_primary_total"]


def test_wf107_prior_gross_1858():
    u = get_union_recalculation()
    assert u["prior_gross"] == 1858


def test_wf108_new_gross_total_1924():
    u = get_union_recalculation()
    assert u["new_gross_total"] == 1924


def test_wf109_gross_formula_verification():
    u = get_union_recalculation()
    assert u["prior_gross"] + u["wave005f_gross"] == u["new_gross_total"]


def test_wf110_silent_double_count_zero():
    u = get_union_recalculation()
    assert u["silent_double_count"] == 0


# ---------------------------------------------------------------------------
# WF-111 to WF-130: Relation evidence audit
# ---------------------------------------------------------------------------

def test_wf111_relation_evidence_audit_exists():
    audit = get_relation_evidence_audit()
    assert audit, "relation_evidence_audit must be present"


def test_wf112_primary_summary_proved_66():
    audit = get_relation_evidence_audit()
    assert audit["primary_summary"]["files_with_proved_relation"] == 66


def test_wf113_primary_summary_blocker_0():
    audit = get_relation_evidence_audit()
    assert audit["primary_summary"]["files_with_blocker"] == 0


def test_wf114_primary_summary_unresolved_0():
    audit = get_relation_evidence_audit()
    assert audit["primary_summary"]["files_unresolved"] == 0


def test_wf115_primary_summary_forbidden_sole_proofs_0():
    audit = get_relation_evidence_audit()
    assert audit["primary_summary"]["forbidden_sole_proofs_used"] == 0


def test_wf116_freeze_report_audit_count_42():
    audit = get_relation_evidence_audit()
    assert audit["freeze_report_audit"]["count"] == 42


def test_wf117_freeze_manifest_audit_total_8():
    audit = get_relation_evidence_audit()
    assert audit["freeze_manifest_audit"]["total_json_accounted"] == 8


def test_wf118_freeze_manifest_audit_foundation_3():
    audit = get_relation_evidence_audit()
    assert audit["freeze_manifest_audit"]["foundation_json_count"] == 3


def test_wf119_freeze_recovery_audit_count_7():
    audit = get_relation_evidence_audit()
    assert audit["freeze_recovery_audit"]["count"] == 7


def test_wf120_tooling_audit_individually_proved_4():
    audit = get_relation_evidence_audit()
    assert audit["tooling_audit"]["individually_proved"] == 4


# ---------------------------------------------------------------------------
# WF-121 to WF-130: Foundation doc consistency
# ---------------------------------------------------------------------------

def test_wf121_foundation_doc_audit_count_3():
    audit = get_relation_evidence_audit()
    assert audit["freeze_foundation_doc_audit"]["count"] == 3
    assert audit["freeze_foundation_doc_audit"]["individually_proved"] == 3


def test_wf122_test_audit_individually_proved_2():
    audit = get_relation_evidence_audit()
    assert audit["test_audit"]["individually_proved"] == 2


def test_wf123_test_audit_legacy_test():
    audit = get_relation_evidence_audit()
    assert audit["test_audit"]["legacy_test_path"] == "tests/legacy_root/brody_api/test_conscience.py"


def test_wf124_test_audit_ui_test():
    audit = get_relation_evidence_audit()
    assert audit["test_audit"]["ui_test_path"] == "tests/ui/test_chatview_brody_terminal_view.py"


def test_wf125_all_entries_have_required_fields():
    required = {"path", "sha256", "role", "canonicality_status", "relation_type",
                "owner_subsystem", "status", "semantic_verdict", "executability_status"}
    for e in get_entries():
        missing = required - set(e.keys())
        assert not missing, f"Missing fields in {e['path']}: {missing}"


def test_wf126_all_entries_have_evidence():
    for e in get_entries():
        ev = e.get("evidence", "")
        assert ev and len(ev) > 20, f"Evidence too short in {e['path']}: {ev!r}"


def test_wf127_recovery_dir_timestamp_in_evidence():
    for e in get_freeze_recovery_artifact_entries():
        assert "2026-05-20" in e["evidence"] or "20260520" in e["evidence"]


def test_wf128_freeze_report_evidence_references_date():
    for e in get_freeze_report_entries():
        ev = e["evidence"]
        assert "2026" in ev, f"No date reference in evidence: {e['path']}"


def test_wf129_foundation_doc_relation_type_correct():
    for e in get_freeze_foundation_doc_entries():
        assert e["relation_type"] == "FREEZE_FOUNDATION_DOC_LINKED_TO_CANONICAL_SPEC"


def test_wf130_recovery_txt_files_in_txt_list():
    txt_paths = {e["path"] for e in get_txt_artifact_entries()}
    recovery_paths = {e["path"] for e in get_freeze_recovery_artifact_entries()}
    assert recovery_paths == txt_paths


# ---------------------------------------------------------------------------
# WF-131 to WF-160: No-false-authority and governance compliance
# ---------------------------------------------------------------------------

def test_wf131_no_decision_authority_claimed():
    idx = get_index()
    assert idx.get("can_decide") is False
    for e in get_entries():
        assert "DECIDES" not in str(e)
        assert "AUTHORIZES" not in str(e)


def test_wf132_no_brody_authority_in_entries():
    for e in get_entries():
        assert e.get("role") != "BRODY_AUTHORITY"
        assert "BRODY_AUTHORITY" not in e.get("evidence", "")


def test_wf133_no_memory_write_claimed():
    idx = get_index()
    assert idx.get("memory_write") is False


def test_wf134_no_acts_emitted():
    idx = get_index()
    assert idx.get("emits_act") is False


def test_wf135_wave005f_closes_brody_primary_census():
    rp = get_remaining_population()
    assert rp.get("remaining_after_wave005f") == 0


def test_wf136_scope_reconciliation_prior_waves():
    sr = get_scope_reconciliation()
    prior = sr.get("prior_waves_covered", [])
    for w in ["WAVE005_A", "WAVE005_B", "WAVE005_C", "WAVE005_D", "WAVE005_E"]:
        assert w in prior


def test_wf137_recovery_empty_file_indexed():
    txt_paths = {e["path"] for e in get_txt_artifact_entries()}
    assert "docs/freeze/BRODY_RIGHTS_AUTHORITY_FINAL_VALIDATION_RECOVERY_20260520_064234/protected_files_diff.txt" in txt_paths


def test_wf138_freeze_manifest_linked_archive_count_5():
    entries = get_entries_by_relation_type("FREEZE_MANIFEST_LINKED_TO_ARCHIVE_INDEX")
    assert len(entries) == 5


def test_wf139_freeze_manifest_linked_foundation_count_3():
    entries = get_entries_by_relation_type("FREEZE_MANIFEST_LINKED_TO_FOUNDATION_DOC")
    assert len(entries) == 3


def test_wf140_relation_type_distribution_total_66():
    idx = get_index()
    dist = idx.get("relation_type_distribution", {})
    total = sum(v for k, v in dist.items() if k != "total")
    assert total == 66
    assert dist.get("total") == 66


def test_wf141_role_distribution_total_66():
    idx = get_index()
    dist = idx.get("role_distribution", {})
    total = sum(v for k, v in dist.items() if k != "total")
    assert total == 66
    assert dist.get("total") == 66


def test_wf142_executability_distribution_total_66():
    idx = get_index()
    dist = idx.get("executability_distribution", {})
    total = sum(v for k, v in dist.items() if k != "total")
    assert total == 66
    assert dist.get("total") == 66


def test_wf143_file_type_distribution_total_66():
    idx = get_index()
    dist = idx.get("file_type_distribution", {})
    total = sum(v for k, v in dist.items() if k != "total")
    assert total == 66
    assert dist.get("total") == 66


def test_wf144_summary_total_66():
    s = summary()
    assert s["total"] == 66


def test_wf145_summary_md_count():
    s = summary()
    assert s["md_count"] == 45


def test_wf146_summary_json_count():
    s = summary()
    assert s["json_count"] == 8


def test_wf147_summary_txt_count():
    s = summary()
    assert s["txt_count"] == 7


def test_wf148_summary_py_count():
    s = summary()
    assert s["py_count"] == 4


def test_wf149_summary_tsx_count():
    s = summary()
    assert s["tsx_count"] == 1


def test_wf150_summary_ts_count():
    s = summary()
    assert s["ts_count"] == 1


def test_wf151_summary_not_executable_count():
    s = summary()
    assert s["not_executable_count"] == 62


def test_wf152_summary_not_a_test_count():
    s = summary()
    assert s["not_a_test_count"] == 2


def test_wf153_summary_executable_passes_count():
    s = summary()
    assert s["executable_passes_count"] == 2


def test_wf154_get_entries_returns_list():
    entries = get_entries()
    assert isinstance(entries, list)
    assert len(entries) == 66


def test_wf155_get_entries_returns_deep_copy():
    entries1 = get_entries()
    entries1[0]["path"] = "MUTATED"
    entries2 = get_entries()
    assert entries2[0]["path"] != "MUTATED"


def test_wf156_get_index_returns_deep_copy():
    idx1 = get_index()
    idx1["final_status"] = "MUTATED"
    idx2 = get_index()
    assert idx2["final_status"] != "MUTATED"


def test_wf157_all_py_files_correct():
    py_paths = {e["path"] for e in get_py_source_entries()}
    assert "apps/obsidia-workbench/audit_brody.py" in py_paths
    assert "tests/legacy_root/brody_api/test_conscience.py" in py_paths
    assert "tests/ui/test_chatview_brody_terminal_view.py" in py_paths
    assert "tools/brody_chat.py" in py_paths


def test_wf158_tsx_path_correct():
    entries = get_tsx_entries()
    assert entries[0]["path"] == "apps/obsidia-workbench/src/components/BrodyPanel.tsx"


def test_wf159_ts_path_correct():
    entries = get_ts_entries()
    assert entries[0]["path"] == "apps/obsidia-workbench/src/lib/brodyResponseComposer.ts"


def test_wf160_recovery_audit_empty_file_note():
    audit = get_relation_evidence_audit()
    note = audit["freeze_recovery_audit"].get("note_empty_file", "")
    assert "protected_files_diff" in note
    assert "0-byte" in note or "empty" in note.lower()
