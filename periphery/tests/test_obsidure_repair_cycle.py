"""
periphery/tests/test_obsidure_repair_cycle.py
=============================================
Tests de non-régression — cycle de réparation externe.

Couvre les quatre échecs observés qui ont motivé cette correction :

  E1  `code_debug` renvoyé par le backend mais non converti en route capable
      de produire un patch.
  E2  Cycle Obsidure déclarant STABILIZED avec patches_count=0 hors route Lean.
  E3  Route PYTHON_PATCH_PROPOSAL incapable de réparer sémantiquement un
      fichier existant (elle l'écrasait par un stub).
  E4  Brody classant une question Lean en OPERATOR_LOOP à cause de mots
      génériques ("boucle", "opérateur").

Plus les invariants de frontière :
      decision_authority=KX108_ONLY, emits_act=False, kernel_mutation=False,
      memory_write=False, canonical_write=False, auto_apply/commit/push=False.

Aucun test n'applique quoi que ce soit au repo. Les sandboxes créées sont
nettoyées en fin de test.
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from periphery.agents.obsidure_repair_contract import (  # noqa: E402
    ALLOWED_REPAIR_EXTS,
    ALLOWED_REPAIR_PREFIXES,
    PROTECTED_INFIXES_REPAIR,
    REPAIR_BOUNDARY,
    ErrorContextRecord,
    FailureMode,
    RepairCandidateFile,
    RepairProposal,
    RepairRequest,
    RepairVerdict,
    assert_repair_boundary,
    is_protected_repair_path,
    repair_proposal_from_dict,
    validate_repair_proposal,
)
from periphery.agents.obsidure_repair_bridge import (  # noqa: E402
    REPAIR_SANDBOX_PREFIX,
    build_repair_request_from_cycle,
    cleanup_repair_sandbox,
    resume_objective_from_verdict,
    test_repair_proposal as run_repair_sandbox_test,
)


# ===========================================================================
# Frontières — invariants absolus
# ===========================================================================

@pytest.mark.parametrize("key,expected", [
    ("decision_authority", "KX108_ONLY"),
    ("emits_act", False),
    ("kernel_mutation", False),
    ("memory_write", False),
    ("canonical_write", False),
    ("auto_apply", False),
    ("auto_commit", False),
    ("auto_push", False),
])
def test_repair_boundary_invariants(key, expected):
    assert REPAIR_BOUNDARY[key] == expected


def test_boundary_violation_is_fail_closed():
    with pytest.raises(ValueError):
        assert_repair_boundary({"auto_apply": True})


def test_repair_structures_carry_boundary():
    for obj in (RepairRequest(), RepairProposal(), RepairVerdict()):
        assert obj.boundary["decision_authority"] == "KX108_ONLY"
        assert obj.boundary["auto_apply"] is False


def test_protected_infixes_in_sync():
    """Le miroir du contrat ne doit pas diverger de la liste d'Obsidure."""
    from periphery.agents.agent_obsidure import PROTECTED_INFIXES
    assert set(PROTECTED_INFIXES_REPAIR) == set(PROTECTED_INFIXES)


# ===========================================================================
# E2 — Un cycle sans artefact ne peut plus déclarer STABILIZED
# ===========================================================================

def test_objective_requires_artifact_true_on_creation():
    from periphery.agents.agent_obsidure import _objective_requires_artifact
    assert _objective_requires_artifact("Cree un module periphery/math_core/x.py") is True


def test_objective_requires_artifact_true_on_repair_verb():
    from periphery.agents.agent_obsidure import _objective_requires_artifact
    assert _objective_requires_artifact("Repare le calcul de tension") is True


def test_objective_requires_artifact_false_on_audit_only():
    from periphery.agents.agent_obsidure import OSTradResult, _objective_requires_artifact
    os_trad = OSTradResult(intent="AUDIT_ONLY")
    assert _objective_requires_artifact("Audit du module", os_trad) is False


def test_objective_requires_artifact_true_on_python_intent():
    from periphery.agents.agent_obsidure import OSTradResult, _objective_requires_artifact
    os_trad = OSTradResult(intent="PYTHON_PATCH_PROPOSAL")
    assert _objective_requires_artifact("quelque chose", os_trad) is True


def test_no_stabilized_with_zero_patches_outside_lean(monkeypatch):
    """
    E2 — régression centrale.

    Une route NON-Lean qui ne produit aucun patch alors que l'objectif exige
    un artefact ne doit JAMAIS ressortir en STABILIZED/passed=True.
    """
    import periphery.agents.agent_obsidure as ao

    monkeypatch.setattr(ao, "generate_patches", lambda *a, **k: ([], None))

    agent = ao.AgentObsidure(verbose=False)
    os_trad = ao.OSTradResult(intent="PYTHON_PATCH_PROPOSAL", source="OFFLINE")

    patches, lean_result, sandbox_dir, stab = agent.phase_d_disruption(
        objective="Cree un module periphery/math_core/zzz_nonexistent_probe.py",
        os_trad=os_trad,
        max_attempts=2,
    )
    try:
        assert patches == []
        assert stab.passed is False
        assert stab.final_status != "STABILIZED"
        # L'échec doit être matérialisé, pas silencieux.
        all_types = [
            e["type"]
            for entry in stab.errors_history
            for e in entry["errors"]
        ]
        assert "EMPTY_PATCH_PROPOSAL" in all_types
        # …et converti en ErrorContext exploitable.
        assert any(
            c.mutation_directive == "ESCALATE_TO_EXTERNAL_REPAIR"
            for c in agent._last_error_contexts
        )
    finally:
        shutil.rmtree(sandbox_dir, ignore_errors=True)


def test_error_analyzer_escalates_empty_patch():
    from periphery.agents.agent_obsidure import ErrorAnalyzer
    ctxs = ErrorAnalyzer().analyze_errors(
        raw_errors=[{"type": "EMPTY_PATCH_PROPOSAL", "path": "", "details": "rien"}],
        lean_result=None,
        attempt=1,
    )
    assert ctxs[0].mutation_directive == "ESCALATE_TO_EXTERNAL_REPAIR"
    assert ctxs[0].recommended_strategy == "EXTERNAL_REASONING"


def test_error_analyzer_escalates_semantic_repair():
    from periphery.agents.agent_obsidure import ErrorAnalyzer
    ctxs = ErrorAnalyzer().analyze_errors(
        raw_errors=[{
            "type": "SEMANTIC_REPAIR_REQUIRED",
            "path": "periphery/math_core/omega_space.py",
            "details": "existe déjà",
        }],
        lean_result=None,
        attempt=1,
    )
    assert ctxs[0].mutation_directive == "ESCALATE_TO_EXTERNAL_REPAIR"
    assert ctxs[0].target_hint == "periphery/math_core/omega_space.py"


# ===========================================================================
# E3 — Un fichier existant n'est plus écrasé par un stub
# ===========================================================================

def test_existing_file_is_not_overwritten_by_stub():
    from periphery.agents.agent_obsidure import _generate_python_peripheral_patches

    target = "periphery/math_core/omega_space.py"
    assert (REPO_ROOT / target).is_file(), "fixture: le fichier cible doit exister"
    original = (REPO_ROOT / target).read_text(encoding="utf-8")

    with tempfile.TemporaryDirectory() as td:
        patches = _generate_python_peripheral_patches(
            f"Repare {target}", Path(td), attempt=1
        )
        assert len(patches) == 1
        patch = patches[0]
        assert patch["action"] == "SEMANTIC_REPAIR_REQUIRED"
        assert patch["base_sha256"]
        # La sandbox contient la BASE réelle, pas un stub.
        sandbox_content = Path(patch["sandbox_path"]).read_text(encoding="utf-8")
        assert sandbox_content == original
        assert "STUB" not in sandbox_content

    # Le repo n'a pas bougé.
    assert (REPO_ROOT / target).read_text(encoding="utf-8") == original


def test_semantic_repair_required_blocks_conformity():
    from periphery.agents.agent_obsidure import _test_patches_conformity
    errors = _test_patches_conformity(
        [{
            "path": "periphery/math_core/omega_space.py",
            "action": "SEMANTIC_REPAIR_REQUIRED",
            "sandbox_path": "",
        }],
        None,
        Path("."),
    )
    assert [e["type"] for e in errors] == ["SEMANTIC_REPAIR_REQUIRED"]


def test_new_target_still_produces_stub():
    """Non-régression : une cible neuve garde le comportement historique."""
    from periphery.agents.agent_obsidure import _generate_python_peripheral_patches
    with tempfile.TemporaryDirectory() as td:
        patches = _generate_python_peripheral_patches(
            "Cree periphery/math_core/zzz_brand_new_probe.py", Path(td), attempt=1
        )
    assert patches[0]["action"] == "CREATE_PYTHON_PERIPHERAL"


# ===========================================================================
# Contrat — validation d'un RepairProposal
# ===========================================================================

def _cand(path: str, content: str = "x = 1\n", kind: str = "CREATE"):
    return RepairCandidateFile(path=path, full_content=content, change_kind=kind)


def test_empty_proposal_is_never_a_success():
    errors = validate_repair_proposal(RepairProposal())
    assert [e["type"] for e in errors] == ["REPAIR_NO_CANDIDATE"]


def test_protected_path_rejected():
    p = RepairProposal(candidate_files=[_cand("proofs/V18_bundle/P01.py")])
    assert "REPAIR_PROTECTED_PATH" in [e["type"] for e in validate_repair_proposal(p)]


def test_sealed_kernel_rejected():
    p = RepairProposal(candidate_files=[_cand("server.kernel.sealed.cjs.py")])
    assert "REPAIR_PROTECTED_PATH" in [e["type"] for e in validate_repair_proposal(p)]


def test_out_of_scope_path_rejected():
    p = RepairProposal(candidate_files=[_cand("docs/investor/note.py")])
    assert "REPAIR_PATH_OUT_OF_SCOPE" in [e["type"] for e in validate_repair_proposal(p)]


def test_path_escape_rejected():
    p = RepairProposal(candidate_files=[_cand("periphery/../../evil.py")])
    assert "REPAIR_PATH_ESCAPE" in [e["type"] for e in validate_repair_proposal(p)]


def test_bad_extension_rejected():
    p = RepairProposal(candidate_files=[_cand("periphery/x.exe")])
    assert "REPAIR_INVALID_EXTENSION" in [e["type"] for e in validate_repair_proposal(p)]


def test_empty_content_rejected():
    p = RepairProposal(candidate_files=[_cand("periphery/x.py", content="   ")])
    assert "REPAIR_EMPTY_CONTENT" in [e["type"] for e in validate_repair_proposal(p)]


def test_duplicate_path_rejected():
    p = RepairProposal(candidate_files=[_cand("periphery/x.py"), _cand("periphery/x.py")])
    assert "REPAIR_DUPLICATE_PATH" in [e["type"] for e in validate_repair_proposal(p)]


def test_valid_proposal_passes_validation():
    p = RepairProposal(candidate_files=[_cand("periphery/math_core/zzz_probe.py")])
    assert validate_repair_proposal(p) == []


def test_proposal_from_dict_roundtrip():
    p = repair_proposal_from_dict({
        "request_id": "rr_x",
        "candidate_files": [
            {"path": "periphery/a.py", "full_content": "y = 2\n", "change_kind": "CREATE"}
        ],
        "tests_to_run": ["periphery/tests/test_obsidure_python_route.py"],
        "boundary": {"auto_apply": True},  # tentative de relâchement
    })
    # Le relâchement est ignoré : seules les valeurs canoniques sont conservées.
    assert p.boundary["auto_apply"] is False
    assert p.candidate_files[0].path == "periphery/a.py"


# ===========================================================================
# Pont — test sandbox d'un RepairProposal
# ===========================================================================

def test_sandbox_rejects_empty_proposal():
    v = run_repair_sandbox_test(RepairProposal(), run_tests=False)
    assert v.status == "NO_CANDIDATE"
    assert resume_objective_from_verdict(v) is None


def test_sandbox_rejects_syntax_error():
    p = RepairProposal(candidate_files=[_cand("periphery/math_core/zzz_probe.py", "def f(:\n")])
    v = run_repair_sandbox_test(p, run_tests=False)
    try:
        assert v.status == "BLOCKED"
        assert "REPAIR_PY_COMPILE_ERROR" in [e["type"] for e in v.errors]
    finally:
        cleanup_repair_sandbox(v)


def test_sandbox_rejects_invalid_json():
    p = RepairProposal(candidate_files=[_cand("periphery/math_core/zzz.json", "{not json")])
    v = run_repair_sandbox_test(p, run_tests=False)
    try:
        assert v.status == "BLOCKED"
        assert "REPAIR_JSON_PARSE_ERROR" in [e["type"] for e in v.errors]
    finally:
        cleanup_repair_sandbox(v)


def test_sandbox_rejects_forbidden_keyword():
    """La conformité Obsidure s'applique aussi aux candidats externes."""
    p = RepairProposal(candidate_files=[
        _cand("periphery/math_core/zzz_probe.py", "import os\nos.system('git push')\n")
    ])
    v = run_repair_sandbox_test(p, run_tests=False)
    try:
        assert v.status == "BLOCKED"
        assert "FORBIDDEN_KEYWORD" in [e["type"] for e in v.errors]
    finally:
        cleanup_repair_sandbox(v)


def test_sandbox_flags_modify_on_missing_target():
    p = RepairProposal(candidate_files=[
        _cand("periphery/math_core/zzz_absent.py", "z = 1\n", kind="MODIFY")
    ])
    v = run_repair_sandbox_test(p, run_tests=False)
    try:
        assert "REPAIR_MODIFY_MISSING_TARGET" in [e["type"] for e in v.errors]
    finally:
        cleanup_repair_sandbox(v)


def test_sandbox_flags_create_on_existing_target():
    p = RepairProposal(candidate_files=[
        _cand("periphery/math_core/omega_space.py", "z = 1\n", kind="CREATE")
    ])
    v = run_repair_sandbox_test(p, run_tests=False)
    try:
        assert "REPAIR_CREATE_OVERWRITES_EXISTING" in [e["type"] for e in v.errors]
    finally:
        cleanup_repair_sandbox(v)


def test_sandbox_valid_candidate_is_partial_without_tests():
    """Compile + conforme mais sans test : PARTIAL, jamais PASS."""
    p = RepairProposal(candidate_files=[
        _cand("periphery/math_core/zzz_probe.py", "def probe():\n    return 1\n")
    ])
    v = run_repair_sandbox_test(p, run_tests=False)
    try:
        assert v.status == "PARTIAL"
        assert v.errors == []
        assert "periphery/math_core/zzz_probe.py" in v.compiled_files
    finally:
        cleanup_repair_sandbox(v)


def test_sandbox_never_writes_to_repo():
    """Le candidat n'est écrit QUE dans la sandbox."""
    rel = "periphery/math_core/zzz_never_written.py"
    assert not (REPO_ROOT / rel).exists()
    p = RepairProposal(candidate_files=[_cand(rel, "a = 1\n")])
    v = run_repair_sandbox_test(p, run_tests=False)
    try:
        assert not (REPO_ROOT / rel).exists()
        assert (Path(v.sandbox_dir) / rel).is_file()
    finally:
        cleanup_repair_sandbox(v)
        assert not (REPO_ROOT / rel).exists()


def test_cleanup_refuses_foreign_directory():
    """Le nettoyage ne peut cibler qu'une sandbox de réparation."""
    v = RepairVerdict(sandbox_dir=str(REPO_ROOT / "periphery"))
    assert cleanup_repair_sandbox(v) is False
    assert (REPO_ROOT / "periphery").is_dir()


def test_sandbox_dir_prefix_is_ephemeral():
    p = RepairProposal(candidate_files=[_cand("periphery/math_core/zzz_probe.py")])
    v = run_repair_sandbox_test(p, run_tests=False)
    try:
        assert Path(v.sandbox_dir).name.startswith(REPAIR_SANDBOX_PREFIX)
    finally:
        cleanup_repair_sandbox(v)


# ===========================================================================
# RepairRequest depuis un cycle Obsidure
# ===========================================================================

def test_repair_request_from_cycle_no_artifact():
    from periphery.agents.agent_obsidure import ErrorContext, StabilizationResult

    ctx = ErrorContext(
        attempt=1,
        error_type="EMPTY_PATCH_PROPOSAL",
        raw_details="aucun patch",
        mutation_directive="ESCALATE_TO_EXTERNAL_REPAIR",
        recommended_strategy="EXTERNAL_REASONING",
    )
    stab = StabilizationResult(
        attempts=2, max_attempts=2, final_status="MAX_ATTEMPTS_REACHED", passed=False
    )
    req = build_repair_request_from_cycle(
        objective="Cree periphery/math_core/x.py",
        stabilization=stab,
        error_contexts=[ctx],
        patches=[],
    )
    assert req.failure_mode == FailureMode.NO_ARTIFACT_PRODUCED
    assert req.origin == "OBSIDURE"
    assert req.error_contexts[0].mutation_directive == "ESCALATE_TO_EXTERNAL_REPAIR"
    assert "zero erreur n'est PAS un succes" in req.summary


def test_repair_request_from_cycle_semantic():
    from periphery.agents.agent_obsidure import ErrorContext

    ctx = ErrorContext(
        attempt=1,
        error_type="SEMANTIC_REPAIR_REQUIRED",
        raw_details="existe",
        target_hint="periphery/math_core/omega_space.py",
    )
    req = build_repair_request_from_cycle(
        objective="Repare omega_space",
        error_contexts=[ctx],
        patches=[{"path": "periphery/math_core/omega_space.py"}],
    )
    assert req.failure_mode == FailureMode.SEMANTIC_REPAIR_REQUIRED
    assert "periphery/math_core/omega_space.py" in req.repo_targets
    # Le moteur externe reçoit le code RÉEL, pas un résumé.
    assert len(req.target_excerpts["periphery/math_core/omega_space.py"]) > 100


def test_repair_request_excludes_protected_targets():
    from periphery.agents.agent_obsidure import ErrorContext
    ctx = ErrorContext(
        attempt=1,
        error_type="X",
        raw_details="",
        target_hint="proofs/V18_bundle/P01.lean",
    )
    req = build_repair_request_from_cycle(objective="o", error_contexts=[ctx], patches=[])
    assert req.repo_targets == []


# ===========================================================================
# E1 — Brody : code_debug devient une route capable
# ===========================================================================

def test_brody_code_debug_emits_repair_request():
    from apps.obsidia_api.brody_repair_request_router import build_repair_request_from_message
    req = build_repair_request_from_message(
        "pytest FAILED periphery/math_core/omega_space.py::test_x — AssertionError: mismatch",
        ir_intent="code_debug",
    )
    assert req is not None
    assert req.origin == "BRODY"
    assert req.failure_mode == FailureMode.BUILD_ERROR
    assert "periphery/math_core/omega_space.py" in req.repo_targets
    assert req.error_contexts, "les signaux d'erreur observés doivent être extraits"


def test_brody_non_debug_message_emits_nothing():
    from apps.obsidia_api.brody_repair_request_router import build_repair_request_from_message
    assert build_repair_request_from_message("bonjour, ou en est le projet") is None


def test_brody_debug_without_signal_is_route_incapable():
    """Pas de trace, pas de cible → on le dit, on n'invente pas."""
    from apps.obsidia_api.brody_repair_request_router import build_repair_request_from_message
    req = build_repair_request_from_message("il y a un bug quelque part", ir_intent="code_debug")
    assert req.failure_mode == FailureMode.ROUTE_INCAPABLE
    assert req.repo_targets == []


def test_brody_repair_request_excludes_protected_paths():
    from apps.obsidia_api.brody_repair_request_router import extract_repo_targets
    assert extract_repo_targets("erreur dans proofs/V18_bundle/P01.lean") == []


def test_brody_repair_request_ignores_nonexistent_paths():
    from apps.obsidia_api.brody_repair_request_router import extract_repo_targets
    assert extract_repo_targets("erreur dans periphery/zzz/does_not_exist.py") == []


def test_brody_pipeline_attaches_repair_request():
    from apps.obsidia_api.brody_real_response_pipeline import run_brody_real_response_pipeline
    r = run_brody_real_response_pipeline(
        "traceback pytest sur periphery/math_core/omega_space.py : AssertionError"
    )
    assert r["repair_route_status"] == "REPAIR_REQUEST_EMITTED"
    assert r["repair_request"]["origin"] == "BRODY"
    # Les frontières du pipeline restent intactes.
    assert r["decision_authority"] == "KX108_ONLY"
    assert r["emits_act"] is False
    assert r["kernel_mutation"] is False
    assert r["memory_write"] is False


def test_brody_pipeline_non_debug_is_unchanged():
    from apps.obsidia_api.brody_real_response_pipeline import run_brody_real_response_pipeline
    r = run_brody_real_response_pipeline("ou on en est sur le projet")
    assert r["repair_route_status"] == "NOT_A_REPAIR_INTENT"
    assert r["repair_request"] is None
    assert r["response_md"]  # la réponse normale est toujours produite


# ===========================================================================
# E4 — Lean ne tombe plus dans OPERATOR_LOOP
# ===========================================================================

@pytest.mark.parametrize("message", [
    "explique la boucle Lean de P38",
    "la boucle de preuve Lean ne converge pas",
    "boucle infinie dans le theoreme lean",
])
def test_lean_question_routes_to_proof_query(message):
    from apps.obsidia_api.brody_semantic_query_router import build_semantic_query
    assert build_semantic_query(message)["topic"] == "PROOF_QUERY"


@pytest.mark.parametrize("message", [
    "operator loop status",
    "command gate receipt handoff",
    "la boucle operateur est bloquee",
])
def test_operator_loop_still_routes(message):
    from apps.obsidia_api.brody_semantic_query_router import build_semantic_query
    assert build_semantic_query(message)["topic"] == "OPERATOR_LOOP"


def test_generic_boucle_falls_back_to_operator_loop():
    """"boucle" seul, sans autre marqueur, reste OPERATOR_LOOP (repli tardif)."""
    from apps.obsidia_api.brody_semantic_query_router import build_semantic_query
    r = build_semantic_query("pourquoi la boucle ne se termine pas")
    assert r["topic"] == "OPERATOR_LOOP"
    assert r["route"] == "LATE_GENERIC_MATCH"


def test_merkle_question_routes_to_proof_query():
    from apps.obsidia_api.brody_semantic_query_router import build_semantic_query
    assert build_semantic_query("merkle seal mismatch")["topic"] == "PROOF_QUERY"
