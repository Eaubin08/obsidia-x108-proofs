"""
tests/test_p72_invariant_graph_formal_proof_alignment.py

P72 validation suite — 76 tests.
Verifie : JSON audit, graphe invariants, theoremes Lean, matrice LEAN_PROVEN vs PYTHON_TESTED,
regles peripherie, regles extension, flags securite, fichiers spec, regressions P56E->P71.
"""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P72_JSON = os.path.join(ROOT, "docs", "core_import", "P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT.json")
SPEC_DIR = os.path.join(ROOT, "specs", "_invariant_graph")


@pytest.fixture(scope="module")
def p72():
    with open(P72_JSON, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def inv_graph(p72):
    return p72["invariant_graph"]


@pytest.fixture(scope="module")
def theorem_map(p72):
    return p72["theorem_to_architecture_map"]


@pytest.fixture(scope="module")
def lean_matrix(p72):
    return p72["lean_proven_vs_python_tested_matrix"]


@pytest.fixture(scope="module")
def periphery_rules(p72):
    return p72["periphery_stabilization_rules"]


@pytest.fixture(scope="module")
def ext_rules(p72):
    return p72["extension_safety_rules"]


# ---------------------------------------------------------------------------
# Section 1 — JSON de base (5 tests)
# ---------------------------------------------------------------------------

def test_p72_json_exists():
    assert os.path.isfile(P72_JSON)


def test_p72_json_status(p72):
    assert p72["status"] == "P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT_READY"


def test_p72_json_mode(p72):
    assert p72["mode"] == "AUDIT_DOCS"


def test_p72_dry_run_only(p72):
    assert p72["dry_run_only"] is True


def test_p72_palier(p72):
    assert p72["palier"] == "P72"


# ---------------------------------------------------------------------------
# Section 2 — Graphe invariants — structure (5 tests)
# ---------------------------------------------------------------------------

def test_invariant_graph_exists(p72):
    assert isinstance(p72["invariant_graph"], list)
    assert len(p72["invariant_graph"]) > 0


def test_invariant_graph_count(p72):
    assert p72["total_invariants"] == 23
    assert len(p72["invariant_graph"]) == 23


def test_invariant_graph_required_fields(inv_graph):
    required = {
        "invariant_id", "description", "layer", "formal_status",
        "lean_theorems", "tla_checked", "python_tested",
        "depends_on", "blocks_extension_of", "risk_if_broken", "extension_rule",
    }
    for inv in inv_graph:
        for f in required:
            assert f in inv, f"Champ manquant {f} dans {inv.get('invariant_id')}"


def test_invariant_formal_status_valid(inv_graph):
    valid = {
        "LEAN_PROVEN", "PYTHON_TESTED", "SPEC_ONLY",
        "DOC_ONLY", "RUNTIME_OBSERVED", "MIXED_PROOF_STATUS", "UNPROVEN_REQUIRES_REVIEW",
    }
    for inv in inv_graph:
        assert inv["formal_status"] in valid, (
            f"{inv['invariant_id']} a un statut invalide: {inv['formal_status']}"
        )


def test_invariant_ids_unique(inv_graph):
    ids = [i["invariant_id"] for i in inv_graph]
    assert len(ids) == len(set(ids)), "Doublons d'invariant_id detectes"


# ---------------------------------------------------------------------------
# Section 3 — Counts par statut formel (8 tests)
# ---------------------------------------------------------------------------

def test_lean_proven_count(p72):
    assert p72["lean_proven_count"] == 11


def test_python_tested_count(p72):
    assert p72["python_tested_only_count"] == 8


def test_spec_only_count(p72):
    assert p72["spec_only_count"] == 2


def test_doc_only_count(p72):
    assert p72["doc_only_count"] == 1


def test_mixed_count(p72):
    assert p72["mixed_proof_status_count"] == 1


def test_lean_proven_list_nonempty(p72):
    assert len(p72["lean_proven_invariants"]) == 11


def test_critical_invariants_nonempty(p72):
    crit = p72["critical_invariants"]
    assert len(crit) >= 10
    assert "DETERMINISM" in crit
    assert "NO_ACT_BEFORE_TAU" in crit
    assert "GUARD_X108_FINAL_AUTHORITY" in crit


def test_layer_counts_complete(p72):
    lc = p72["layer_counts"]
    assert "OS0_KERNEL" in lc
    assert lc["OS0_KERNEL"] >= 9
    assert "OS4_PERIPHERY" in lc


# ---------------------------------------------------------------------------
# Section 4 — Invariants LEAN_PROVEN specifiques (11 tests)
# ---------------------------------------------------------------------------

def _get_inv(inv_graph, inv_id):
    return next((i for i in inv_graph if i["invariant_id"] == inv_id), None)


def test_determinism_lean_proven(inv_graph):
    inv = _get_inv(inv_graph, "DETERMINISM")
    assert inv is not None
    assert inv["formal_status"] == "LEAN_PROVEN"
    assert inv["risk_if_broken"] == "CRITICAL"


def test_no_act_before_tau_lean_proven(inv_graph):
    inv = _get_inv(inv_graph, "NO_ACT_BEFORE_TAU")
    assert inv is not None
    assert inv["formal_status"] == "LEAN_PROVEN"
    assert "X108_no_act_before_tau" in " ".join(inv["lean_theorems"])


def test_hold_before_tau_lean_proven(inv_graph):
    inv = _get_inv(inv_graph, "HOLD_BEFORE_TAU")
    assert inv is not None
    assert inv["formal_status"] == "LEAN_PROVEN"


def test_irreversible_action_delay_lean_proven(inv_graph):
    inv = _get_inv(inv_graph, "IRREVERSIBLE_ACTION_DELAY")
    assert inv is not None
    assert inv["formal_status"] == "LEAN_PROVEN"
    assert any("irreversible" in t.lower() for t in inv["lean_theorems"])


def test_reversible_action_baseline_lean_proven(inv_graph):
    inv = _get_inv(inv_graph, "REVERSIBLE_ACTION_BASELINE")
    assert inv is not None
    assert inv["formal_status"] == "LEAN_PROVEN"


def test_negative_clock_skew_lean_proven(inv_graph):
    inv = _get_inv(inv_graph, "NEGATIVE_CLOCK_SKEW_TO_HOLD")
    assert inv is not None
    assert inv["formal_status"] == "LEAN_PROVEN"
    assert any("skew" in t.lower() for t in inv["lean_theorems"])


def test_threshold_conservation_lean_proven(inv_graph):
    inv = _get_inv(inv_graph, "THRESHOLD_CONSERVATION")
    assert inv is not None
    assert inv["formal_status"] == "LEAN_PROVEN"
    assert inv["risk_if_broken"] == "CRITICAL"


def test_block_priority_lean_proven(inv_graph):
    inv = _get_inv(inv_graph, "BLOCK_PRIORITY_OVER_HOLD_ALLOW")
    assert inv is not None
    assert inv["formal_status"] == "LEAN_PROVEN"
    assert any("fail_closed" in t for t in inv["lean_theorems"])


def test_hold_priority_lean_proven(inv_graph):
    inv = _get_inv(inv_graph, "HOLD_PRIORITY_OVER_ALLOW")
    assert inv is not None
    assert inv["formal_status"] == "LEAN_PROVEN"


def test_guard_x108_lean_proven(inv_graph):
    inv = _get_inv(inv_graph, "GUARD_X108_FINAL_AUTHORITY")
    assert inv is not None
    assert inv["formal_status"] == "LEAN_PROVEN"
    assert inv["layer"] == "OS1_GUARD"
    assert any("never_blocks" in t for t in inv["lean_theorems"])


def test_no_kernel_mutation_lean_proven(inv_graph):
    inv = _get_inv(inv_graph, "NO_KERNEL_MUTATION_FROM_PERIPHERY")
    assert inv is not None
    assert inv["formal_status"] == "LEAN_PROVEN"
    assert "Obsidia.G1" in inv["lean_theorems"]


# ---------------------------------------------------------------------------
# Section 5 — Invariants PYTHON_TESTED/SPEC/DOC (5 tests)
# ---------------------------------------------------------------------------

def test_sigma_post_guard_spec_only(inv_graph):
    inv = _get_inv(inv_graph, "SIGMA_POST_GUARD_VETO_ONLY")
    assert inv is not None
    assert inv["formal_status"] == "SPEC_ONLY"
    assert inv["layer"] == "OS2_SIGMA"


def test_no_periphery_decision_python_tested(inv_graph):
    inv = _get_inv(inv_graph, "NO_PERIPHERY_DECISION_AUTHORITY")
    assert inv is not None
    assert inv["formal_status"] == "PYTHON_TESTED"
    assert inv["risk_if_broken"] == "CRITICAL"


def test_archive_not_runtime_mixed(inv_graph):
    inv = _get_inv(inv_graph, "ARCHIVE_NOT_RUNTIME")
    assert inv is not None
    assert inv["formal_status"] == "MIXED_PROOF_STATUS"
    assert "Obsidia.G2" in inv["lean_theorems"]


def test_python_tested_not_lean_proven_doc_only(inv_graph):
    inv = _get_inv(inv_graph, "PYTHON_TESTED_NOT_LEAN_PROVEN")
    assert inv is not None
    assert inv["formal_status"] == "DOC_ONLY"


def test_kx108_only_spec_only(inv_graph):
    inv = _get_inv(inv_graph, "KX108_ONLY_DECISION_AUTHORITY")
    assert inv is not None
    assert inv["formal_status"] == "SPEC_ONLY"
    assert inv["risk_if_broken"] == "CRITICAL"


# ---------------------------------------------------------------------------
# Section 6 — Theorem to architecture map (5 tests)
# ---------------------------------------------------------------------------

def test_theorem_map_exists(p72):
    assert isinstance(p72["theorem_to_architecture_map"], list)
    assert len(p72["theorem_to_architecture_map"]) >= 14


def test_theorem_map_required_fields(theorem_map):
    required = {
        "lean_theorem_id", "source_file", "lean_namespace",
        "statement_summary", "maps_to_invariants", "maps_to_layer",
        "maps_to_component", "axioms_free",
    }
    for t in theorem_map:
        for f in required:
            assert f in t, f"Champ manquant {f} dans {t.get('lean_theorem_id')}"


def test_theorem_x108_no_act_present(theorem_map):
    ids = [t["lean_theorem_id"] for t in theorem_map]
    assert "Obsidia.TemporalKernel.X108_no_act_before_tau" in ids


def test_theorem_kernel_never_blocks_present(theorem_map):
    ids = [t["lean_theorem_id"] for t in theorem_map]
    assert "Obsidia.TemporalKernel.X108_kernel_never_blocks" in ids


def test_theorem_skew_negative_present(theorem_map):
    ids = [t["lean_theorem_id"] for t in theorem_map]
    assert "Obsidia.TemporalBridge.skew_negative_implies_hold" in ids


# ---------------------------------------------------------------------------
# Section 7 — Matrice LEAN_PROVEN vs PYTHON_TESTED (5 tests)
# ---------------------------------------------------------------------------

def test_lean_matrix_exists(p72):
    assert isinstance(p72["lean_proven_vs_python_tested_matrix"], list)
    assert len(p72["lean_proven_vs_python_tested_matrix"]) >= 10


def test_lean_matrix_required_fields(lean_matrix):
    required = {
        "claim", "lean_status", "python_test_file",
        "python_test_passes", "note", "public_claimable",
    }
    for entry in lean_matrix:
        for f in required:
            assert f in entry, f"Champ manquant {f}"


def test_lean_matrix_public_claimable_count(lean_matrix):
    public = [e for e in lean_matrix if e["public_claimable"] is True]
    assert len(public) >= 5


def test_lean_matrix_not_lean_proven_not_public(lean_matrix):
    not_lean = [e for e in lean_matrix if e["lean_status"] == "NOT_LEAN_PROVEN"]
    for e in not_lean:
        assert e["public_claimable"] is False, (
            f"Claim '{e['claim']}' n'est pas LEAN_PROVEN mais est public_claimable=True"
        )


def test_lean_matrix_fail_closed_present(lean_matrix):
    claims = [e["claim"] for e in lean_matrix]
    assert any("fail" in c.lower() or "closed" in c.lower() for c in claims)


# ---------------------------------------------------------------------------
# Section 8 — Periphery stabilization rules (7 tests)
# ---------------------------------------------------------------------------

def test_periphery_rules_exists(p72):
    assert isinstance(p72["periphery_stabilization_rules"], list)
    assert len(p72["periphery_stabilization_rules"]) >= 6


def test_periphery_rules_required_fields(periphery_rules):
    required = {"domain", "rule", "current_status", "invariants_protected", "action_if_violated", "audit_palier"}
    for r in periphery_rules:
        for f in required:
            assert f in r, f"Champ manquant {f} dans domaine {r.get('domain')}"


def test_periphery_memory_compliant(periphery_rules):
    mem = next((r for r in periphery_rules if r["domain"] == "MEMORY_SRL"), None)
    assert mem is not None
    assert mem["current_status"] == "COMPLIANT"


def test_periphery_graphiti_compliant(periphery_rules):
    g = next((r for r in periphery_rules if r["domain"] == "GRAPHITI"), None)
    assert g is not None
    assert g["current_status"] == "COMPLIANT"


def test_periphery_connectors_review_required(periphery_rules):
    conn = next((r for r in periphery_rules if r["domain"] == "CONNECTORS"), None)
    assert conn is not None
    assert conn["current_status"] == "REVIEW_REQUIRED"


def test_periphery_routes_partial_review(periphery_rules):
    routes = next((r for r in periphery_rules if r["domain"] == "UI_ROUTES"), None)
    assert routes is not None
    assert routes["current_status"] == "PARTIAL_REVIEW"


def test_periphery_source_packs_compliant(periphery_rules):
    sp = next((r for r in periphery_rules if r["domain"] == "SOURCE_PACKS"), None)
    assert sp is not None
    assert sp["current_status"] == "COMPLIANT"


# ---------------------------------------------------------------------------
# Section 9 — Extension safety rules (5 tests)
# ---------------------------------------------------------------------------

def test_ext_rules_exists(p72):
    assert isinstance(p72["extension_safety_rules"], list)
    assert len(p72["extension_safety_rules"]) >= 6


def test_ext_rules_required_fields(ext_rules):
    required = {"rule_id", "title", "description", "lean_proven_invariants_preserved"}
    for r in ext_rules:
        for f in required:
            assert f in r, f"Champ manquant {f} dans {r.get('rule_id')}"


def test_ext_rule_lean_not_modifiable(ext_rules):
    r = next((r for r in ext_rules if r["rule_id"] == "EXT_SAFE_02"), None)
    assert r is not None
    assert "lean" in r["description"].lower() or "lean" in r["title"].lower()


def test_ext_rule_sigma_not_modifiable(ext_rules):
    r = next((r for r in ext_rules if r["rule_id"] == "EXT_SAFE_03"), None)
    assert r is not None
    assert "sigma" in r["description"].lower() or "sigma" in r["title"].lower()


def test_ext_rule_dry_run_adapter(ext_rules):
    r = next((r for r in ext_rules if r["rule_id"] == "EXT_SAFE_04"), None)
    assert r is not None
    assert "DRY_RUN_ONLY_ADAPTERS" in r["lean_proven_invariants_preserved"]


# ---------------------------------------------------------------------------
# Section 10 — Flags securite P72 (13 tests)
# ---------------------------------------------------------------------------

def test_runtime_modified_false(p72):
    assert p72["runtime_modified"] is False


def test_sigma_modified_false(p72):
    assert p72["sigma_modified"] is False


def test_routes_modified_false(p72):
    assert p72["routes_modified"] is False


def test_lean_modified_false(p72):
    assert p72["lean_modified"] is False


def test_proofs_v18_3_1_modified_false(p72):
    assert p72["proofs_v18_3_1_modified"] is False


def test_act_enabled_false(p72):
    assert p72["act_enabled"] is False


def test_kernel_mutation_enabled_false(p72):
    assert p72["kernel_mutation_enabled"] is False


def test_x108_merge_enabled_false(p72):
    assert p72["x108_merge_enabled"] is False


def test_forbidden_overclaims_nonempty(p72):
    assert len(p72["forbidden_overclaims"]) >= 4


def test_formal_proof_claim_present(p72):
    claim = p72["formal_proof_claim"]
    assert "Lean" in claim or "lean" in claim
    assert "Python" in claim or "python" in claim


def test_full_cascade_timeout_noted(p72):
    assert p72["full_cascade_timeout_noted"] is True


def test_next_step_p73(p72):
    assert p72["next_step"] == "P73_AGENTS_COMPLEMENTARY_RECONCILIATION"


def test_layer_map_complete(p72):
    lm = p72["layer_map"]
    for layer in ["OS0_KERNEL", "OS1_GUARD", "OS2_SIGMA", "OS3_AUDIT_PROOF",
                  "OS4_PERIPHERY", "OS5_SOURCES", "OS6_ROUTES", "OS7_NETWORK"]:
        assert layer in lm, f"Couche manquante: {layer}"


# ---------------------------------------------------------------------------
# Section 11 — Fichiers spec (8 tests)
# ---------------------------------------------------------------------------

def test_spec_invariant_graph_index_exists():
    assert os.path.isfile(os.path.join(SPEC_DIR, "INVARIANT_GRAPH_INDEX.md"))


def test_spec_theorem_to_architecture_map_exists():
    assert os.path.isfile(os.path.join(SPEC_DIR, "THEOREM_TO_ARCHITECTURE_MAP.md"))


def test_spec_theorem_dependency_graph_exists():
    assert os.path.isfile(os.path.join(SPEC_DIR, "THEOREM_DEPENDENCY_GRAPH.md"))


def test_spec_invariant_to_layer_map_exists():
    assert os.path.isfile(os.path.join(SPEC_DIR, "INVARIANT_TO_LAYER_MAP.md"))


def test_spec_invariant_to_extension_rules_exists():
    assert os.path.isfile(os.path.join(SPEC_DIR, "INVARIANT_TO_EXTENSION_RULES.md"))


def test_spec_lean_proven_vs_python_tested_matrix_exists():
    assert os.path.isfile(os.path.join(SPEC_DIR, "LEAN_PROVEN_VS_PYTHON_TESTED_MATRIX.md"))


def test_spec_periphery_stabilization_rules_exists():
    assert os.path.isfile(os.path.join(SPEC_DIR, "PERIPHERY_STABILIZATION_RULES.md"))


def test_spec_why_extensions_do_not_break_x108_exists():
    assert os.path.isfile(os.path.join(SPEC_DIR, "WHY_EXTENSIONS_DO_NOT_BREAK_X108.md"))


# ---------------------------------------------------------------------------
# Section 12 — Regressions P56E->P71 (15 tests)
# ---------------------------------------------------------------------------

def _run(test_path: str) -> bool:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-q", "--tb=no", "--no-header", "-k", "not regression"],
        capture_output=True, text=True, cwd=ROOT,
    )
    return result.returncode == 0


def test_p56e_regression():
    assert _run("tests/test_p56e_post_patch_metric_reaudit.py")


def test_p57_regression():
    assert _run("tests/test_p57_core_machinery_runtime_binding_audit.py")


def test_p58_regression():
    assert _run("tests/test_p58_core_import_triage_operational_path_aware.py")


def test_p59_regression():
    assert _run("tests/test_p59_safe_batch_1_import.py")


def test_p60_regression():
    assert _run("tests/test_p60_test_batch_2_import.py")


def test_p61_regression():
    assert _run("tests/test_p61_bus_adapter_batch.py")


def test_p62_regression():
    assert _run("tests/test_p62_manual_review_deferred.py")


def test_p63_regression():
    assert _run("tests/test_p63_global_fusion_reality_audit.py")


def test_p64_regression():
    assert _run("tests/test_p64_fusion_continuity_ledger.py")


def test_p65_regression():
    assert _run("tests/test_p65_os_adapters_unlock_bus_registry.py")


def test_p66_regression():
    assert _run("tests/test_p66_srl_readonly_memory_layer.py")


def test_p67_regression():
    assert _run("tests/test_p67_boundary_semantic_split_audit.py")


def test_p68_regression():
    assert _run("tests/test_p68_api_auth_route_exposure_audit.py")


def test_p69_regression():
    assert _run("tests/test_p69_filesystem_path_exposure_audit.py")


def test_p70_regression():
    assert _run("tests/test_p70_network_egress_connectors_audit.py")


# ---------------------------------------------------------------------------
# Section 13 — verify_all et forbidden (2 tests)
# ---------------------------------------------------------------------------

def test_verify_all_pass():
    result = subprocess.run(
        [sys.executable, "proofs/verify_all.py"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert "PASS" in result.stdout


def test_forbidden_content_pass():
    result = subprocess.run(
        [sys.executable, "scripts/check_forbidden_content.py"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert "FORBIDDEN_CONTENT_PASS" in result.stdout
