"""
periphery/tests/test_obsidure_reasoning_e2e.py
==============================================
Tests E2E — cycle de réparation complet, bout en bout.

    Obsidure échec → ErrorContext → RepairRequest(origin=OBSIDURE)
        → Brody diagnostic/raisonnement → RepairProposal
            → test_repair_proposal (sandbox) → RepairVerdict

Le test E2E utilise un défaut DÉTERMINISTE ARTIFICIEL monté dans un tmpdir :
un module qui appelle un symbole exporté par un module voisin sans l'importer,
avec un `NameError` réellement observé. Aucun fichier du repo n'est écrit.

Couvre aussi :
  - la requête insuffisamment spécifiée → NEEDS_DIAGNOSTIC_CONTEXT
    (jamais de réparation inventée) ;
  - le short-circuit après T1 sur échec non évolutif, et la conservation de
    MAX_ATTEMPTS pour les erreurs qui peuvent évoluer ;
  - le fallback EXTERNAL_REASONING : déclaré, non automatique, ne produit
    jamais de proposition.

Frontières vérifiées à chaque étape.
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from periphery.agents.obsidure_reasoning_provider import (  # noqa: E402
    DiagnosisStatus,
    ExternalReasoningProvider,
    ReasoningProvider,
    RepairDiagnosis,
    available_providers,
    get_provider,
    run_reasoning_cycle,
)
from periphery.agents.obsidure_repair_contract import (  # noqa: E402
    ErrorContextRecord,
    FailureMode,
    RepairCandidateFile,
    RepairProposal,
    RepairRequest,
)
from periphery.agents.obsidure_repair_bridge import (  # noqa: E402
    cleanup_repair_sandbox,
    resume_objective_from_verdict,
    test_repair_proposal as run_repair_sandbox_test,
)


# ===========================================================================
# Fixture : défaut déterministe artificiel, hors du repo
# ===========================================================================

_HELPER_SRC = '''"""Module fournisseur du symbole."""
from __future__ import annotations


def compute_signature(value: int) -> int:
    """Retourne une signature entière déterministe."""
    return (value * 31) % 97
'''

# Défaut : `compute_signature` est appelé sans être importé → NameError.
_BROKEN_SRC = '''"""Module consommateur — import manquant (défaut artificiel)."""
from __future__ import annotations

from typing import Any


def build_record(value: int) -> dict[str, Any]:
    """Construit un enregistrement à partir de la signature."""
    return {"value": value, "signature": compute_signature(value)}
'''

_BROKEN_REL = "periphery/math_core/zzz_e2e_consumer.py"
_HELPER_REL = "periphery/math_core/zzz_e2e_provider.py"


@pytest.fixture
def fake_repo(tmp_path: Path) -> Path:
    """Mini-repo isolé portant le défaut déterministe."""
    for rel, src in ((_HELPER_REL, _HELPER_SRC), (_BROKEN_REL, _BROKEN_SRC)):
        f = tmp_path / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(src, encoding="utf-8")
    return tmp_path


def _obsidure_request(fake_repo: Path) -> RepairRequest:
    """
    RepairRequest tel qu'Obsidure l'émettrait après un échec, avec un
    NameError réellement observé.
    """
    return RepairRequest(
        origin="OBSIDURE",
        objective="Réparer le défaut de résolution de symbole du module consommateur.",
        failure_mode=FailureMode.BUILD_ERROR,
        summary="failure_mode=BUILD_ERROR | patches_count=0 | error_contexts=1",
        error_contexts=[ErrorContextRecord(
            attempt=1,
            error_type="RUNTIME_NAME_ERROR",
            raw_details="NameError: name 'compute_signature' is not defined",
            target_path=_BROKEN_REL,
            first_error_line="NameError: name 'compute_signature' is not defined",
            mutation_directive="ESCALATE_TO_EXTERNAL_REPAIR",
            recommended_strategy="EXTERNAL_REASONING",
        )],
        repo_targets=[_BROKEN_REL],
        target_excerpts={_BROKEN_REL: (fake_repo / _BROKEN_REL).read_text(encoding="utf-8")},
        attempts_spent=1,
    )


# ===========================================================================
# E2E — la chaîne complète
# ===========================================================================

def test_e2e_obsidure_request_to_repair_verdict(fake_repo: Path):
    """
    Preuve du cycle complet, sans aucune écriture dans le repo réel.
    """
    request = _obsidure_request(fake_repo)
    assert request.origin == "OBSIDURE"

    # ── Brody raisonne ────────────────────────────────────────────────────
    outcome = run_reasoning_cycle(request, repo_root=fake_repo)

    assert outcome.providers_tried == ["BRODY"], "Brody doit être la route principale"
    assert outcome.status == DiagnosisStatus.PROPOSAL_READY
    assert outcome.diagnosis.defect_class == "UNRESOLVED_NAME"
    assert outcome.external_fallback_offered is False, "pas de fallback automatique"

    proposal = outcome.proposal
    assert proposal is not None
    assert proposal.engine == "BRODY"
    assert len(proposal.candidate_files) == 1

    cand = proposal.candidate_files[0]
    assert cand.path == _BROKEN_REL
    assert cand.change_kind == "MODIFY"
    assert cand.base_sha256, "la base doit être ancrée pour détecter la dérive"
    # La réparation est bien l'import manquant, et rien d'autre.
    assert "import compute_signature" in cand.full_content
    assert "def build_record" in cand.full_content, "la logique existante est préservée"

    # ── Obsidure teste en sandbox ─────────────────────────────────────────
    verdict = run_repair_sandbox_test(
        proposal, request, run_tests=False, repo_root=fake_repo
    )
    try:
        assert verdict.status == "PARTIAL", f"erreurs: {verdict.errors}"
        assert verdict.errors == []
        assert _BROKEN_REL in verdict.compiled_files
        assert verdict.request_id == request.request_id
        assert verdict.proposal_id == proposal.proposal_id
        # L'objectif initial est reprenable.
        assert resume_objective_from_verdict(verdict, request) == request.objective
        # Le candidat vit dans la sandbox, pas dans le mini-repo.
        assert (Path(verdict.sandbox_dir) / _BROKEN_REL).is_file()
        assert "compute_signature" not in (
            fake_repo / _BROKEN_REL
        ).read_text(encoding="utf-8").split("def build_record")[0]
    finally:
        cleanup_repair_sandbox(verdict, repo_root=fake_repo)

    # ── Le repo réel n'a rien reçu ────────────────────────────────────────
    assert not (REPO_ROOT / _BROKEN_REL).exists()
    assert not (REPO_ROOT / _HELPER_REL).exists()


def test_e2e_patched_module_actually_executes(fake_repo: Path):
    """
    Le correctif proposé n'est pas seulement syntaxique : le module réparé
    s'exécute et produit le bon résultat.
    """
    request = _obsidure_request(fake_repo)
    outcome = run_reasoning_cycle(request, repo_root=fake_repo)
    assert outcome.proposal is not None

    patched = outcome.proposal.candidate_files[0].full_content

    # Exécution dans un sous-processus réellement isolé : le package
    # `periphery` du repo est déjà chargé dans ce processus, sys.path ne
    # pourrait pas le masquer.
    import subprocess

    sandbox = fake_repo / "_exec_probe"
    (sandbox / "periphery" / "math_core").mkdir(parents=True)
    for pkg in (sandbox / "periphery", sandbox / "periphery" / "math_core"):
        (pkg / "__init__.py").write_text("", encoding="utf-8")
    (sandbox / _HELPER_REL).write_text(_HELPER_SRC, encoding="utf-8")
    (sandbox / _BROKEN_REL).write_text(patched, encoding="utf-8")

    probe = sandbox / "probe.py"
    probe.write_text(
        "from periphery.math_core.zzz_e2e_consumer import build_record\n"
        "assert build_record(4) == {'value': 4, 'signature': (4 * 31) % 97}\n"
        "print('EXEC_OK')\n",
        encoding="utf-8",
    )

    proc = subprocess.run(
        [sys.executable, "probe.py"],
        cwd=str(sandbox),
        capture_output=True,
        text=True,
        timeout=60,
        env={"PATH": "", "SYSTEMROOT": "", "PYTHONPATH": str(sandbox)},
    )
    assert proc.returncode == 0, f"stdout={proc.stdout} stderr={proc.stderr}"
    assert "EXEC_OK" in proc.stdout


def test_e2e_boundaries_hold_end_to_end(fake_repo: Path):
    """Aucune frontière n'est relâchée sur toute la chaîne."""
    request = _obsidure_request(fake_repo)
    outcome = run_reasoning_cycle(request, repo_root=fake_repo)
    verdict = run_repair_sandbox_test(
        outcome.proposal, request, run_tests=False, repo_root=fake_repo
    )
    try:
        for obj in (request, outcome.diagnosis, outcome.proposal, verdict, outcome):
            b = obj.boundary
            assert b["decision_authority"] == "KX108_ONLY"
            assert b["emits_act"] is False
            assert b["emits_verdict"] is False
            assert b["kernel_mutation"] is False
            assert b["memory_write"] is False
            assert b["canonical_write"] is False
            assert b["auto_apply"] is False
            assert b["auto_commit"] is False
            assert b["auto_push"] is False
            assert b["sandbox_mode"] == "HUMAN_APPROVED_WRITE"
    finally:
        cleanup_repair_sandbox(verdict, repo_root=fake_repo)


# ===========================================================================
# Requête insuffisamment spécifiée → aucune réparation inventée
# ===========================================================================

def _underspecified_request(fake_repo: Path) -> RepairRequest:
    """Cible valide, aucun défaut fonctionnel décrit — cas de la fixture réelle."""
    return RepairRequest(
        origin="OBSIDURE",
        objective="répare le défaut de code dans le module consommateur",
        failure_mode=FailureMode.SEMANTIC_REPAIR_REQUIRED,
        summary="failure_mode=SEMANTIC_REPAIR_REQUIRED | patches_count=1",
        error_contexts=[ErrorContextRecord(
            attempt=1,
            error_type="SEMANTIC_REPAIR_REQUIRED",
            raw_details="le fichier existe déjà",
            target_path=_HELPER_REL,
            mutation_directive="ESCALATE_TO_EXTERNAL_REPAIR",
            recommended_strategy="EXTERNAL_REASONING",
        )],
        repo_targets=[_HELPER_REL],
        target_excerpts={_HELPER_REL: _HELPER_SRC},
        attempts_spent=1,
    )


def test_underspecified_request_needs_diagnostic_context(fake_repo: Path):
    """Un défaut non défini ne produit JAMAIS de réparation."""
    outcome = run_reasoning_cycle(_underspecified_request(fake_repo), repo_root=fake_repo)

    assert outcome.status == DiagnosisStatus.NEEDS_DIAGNOSTIC_CONTEXT
    assert outcome.proposal is None
    assert outcome.diagnosis.defect_class == "UNDETERMINED"
    assert outcome.diagnosis.confidence == "NONE"
    assert outcome.diagnosis.missing_information, "il faut DIRE ce qui manque"


def test_underspecified_request_does_not_touch_target(fake_repo: Path):
    """Le fichier cité n'est pas modifié au seul motif d'être cité."""
    before = (fake_repo / _HELPER_REL).read_text(encoding="utf-8")
    run_reasoning_cycle(_underspecified_request(fake_repo), repo_root=fake_repo)
    assert (fake_repo / _HELPER_REL).read_text(encoding="utf-8") == before


def test_request_without_targets_needs_context():
    request = RepairRequest(
        origin="OBSIDURE",
        objective="ça ne marche pas",
        failure_mode=FailureMode.ROUTE_INCAPABLE,
    )
    outcome = run_reasoning_cycle(request)
    assert outcome.status == DiagnosisStatus.NEEDS_DIAGNOSTIC_CONTEXT
    assert outcome.diagnosis.defect_class == "NO_INSPECTABLE_TARGET"
    assert outcome.proposal is None


def test_real_fixture_is_underspecified():
    """
    La fixture réelle rr_2dfcf0c52e45 doit être classée NEEDS_DIAGNOSTIC_CONTEXT :
    aucun défaut fonctionnel concret n'y est fourni.
    """
    fixture = REPO_ROOT / "_PATCH_PROPOSALS" / "_repair_requests" / "rr_2dfcf0c52e45.json"
    if not fixture.is_file():
        pytest.skip("fixture rr_2dfcf0c52e45 absente de ce worktree")

    data = json.loads(fixture.read_text(encoding="utf-8"))
    request = RepairRequest(
        request_id=data["request_id"],
        origin=data["origin"],
        objective=data["objective"],
        failure_mode=data["failure_mode"],
        summary=data["summary"],
        error_contexts=[ErrorContextRecord(**c) for c in data["error_contexts"]],
        repo_targets=data["repo_targets"],
        target_excerpts=data["target_excerpts"],
        attempts_spent=data["attempts_spent"],
        tests_hint=data["tests_hint"],
    )
    target = REPO_ROOT / "periphery" / "math_core" / "omega_space.py"
    before = target.read_text(encoding="utf-8") if target.is_file() else None

    outcome = run_reasoning_cycle(request)

    assert outcome.status == DiagnosisStatus.NEEDS_DIAGNOSTIC_CONTEXT
    assert outcome.proposal is None
    # omega_space.py n'est pas touché au seul motif d'être cité.
    if before is not None:
        assert target.read_text(encoding="utf-8") == before


# ===========================================================================
# Fallback EXTERNAL_REASONING — déclaré, non automatique, stérile
# ===========================================================================

def test_external_fallback_is_not_automatic(fake_repo: Path):
    outcome = run_reasoning_cycle(_underspecified_request(fake_repo), repo_root=fake_repo)
    assert outcome.external_fallback_offered is False
    assert "EXTERNAL_REASONING" not in outcome.providers_tried


def test_external_fallback_when_explicitly_allowed(fake_repo: Path):
    outcome = run_reasoning_cycle(
        _underspecified_request(fake_repo), allow_external=True, repo_root=fake_repo
    )
    assert outcome.external_fallback_offered is True
    assert "EXTERNAL_REASONING" in outcome.providers_tried
    assert outcome.status == DiagnosisStatus.NEEDS_EXTERNAL_ENGINE
    assert outcome.proposal is None, "le fallback ne fabrique jamais de proposition"


def test_external_provider_never_proposes():
    provider = ExternalReasoningProvider()
    request = RepairRequest(objective="x")
    diagnosis = provider.diagnose(request)
    assert diagnosis.status == DiagnosisStatus.NEEDS_EXTERNAL_ENGINE
    assert provider.propose(request, diagnosis) is None


def test_brody_is_registered_as_primary():
    assert "BRODY" in available_providers()
    assert get_provider("BRODY") is not None
    assert get_provider("BRODY").name == "BRODY"


# ===========================================================================
# Le cycle rejette une proposition non conforme, même venue d'un provider
# ===========================================================================

class _RogueProvider(ReasoningProvider):
    """Provider hostile : tente de proposer un fichier protégé."""

    name = "ROGUE"

    def diagnose(self, request, repo_root=None):
        return RepairDiagnosis(
            provider=self.name,
            request_id=request.request_id,
            status=DiagnosisStatus.PROPOSAL_READY,
            defect_class="UNRESOLVED_NAME",
            confidence="HIGH",
        )

    def propose(self, request, diagnosis, repo_root=None):
        return RepairProposal(
            request_id=request.request_id,
            engine=self.name,
            candidate_files=[RepairCandidateFile(
                path="proofs/V18_bundle/P01.py",
                full_content="x = 1\n",
                change_kind="CREATE",
            )],
        )


class _EmptyProvider(ReasoningProvider):
    """Provider qui annonce puis ne produit rien."""

    name = "EMPTY"

    def diagnose(self, request, repo_root=None):
        return RepairDiagnosis(
            provider=self.name,
            request_id=request.request_id,
            status=DiagnosisStatus.PROPOSAL_READY,
            defect_class="UNRESOLVED_NAME",
        )

    def propose(self, request, diagnosis, repo_root=None):
        return None


def test_rogue_proposal_is_rejected_by_cycle():
    outcome = run_reasoning_cycle(
        RepairRequest(objective="x"), providers=[_RogueProvider()]
    )
    assert outcome.proposal is None
    assert outcome.status == DiagnosisStatus.NEEDS_EXTERNAL_ENGINE
    assert outcome.diagnosis.defect_class == "PROVIDER_PROPOSAL_REJECTED"


def test_provider_returning_none_is_recorded():
    outcome = run_reasoning_cycle(
        RepairRequest(objective="x"), providers=[_EmptyProvider()]
    )
    assert outcome.proposal is None
    assert outcome.status == DiagnosisStatus.NEEDS_EXTERNAL_ENGINE
    assert "aucun candidat" in outcome.diagnosis.notes


def test_provider_exception_does_not_break_cycle():
    class _Boom(ReasoningProvider):
        name = "BOOM"

        def diagnose(self, request, repo_root=None):
            raise RuntimeError("panne interne")

        def propose(self, request, diagnosis, repo_root=None):
            return None

    outcome = run_reasoning_cycle(RepairRequest(objective="x"), providers=[_Boom()])
    assert outcome.proposal is None
    assert outcome.diagnosis.defect_class == "PROVIDER_ERROR"


# ===========================================================================
# Short-circuit — échec non évolutif arrêté après T1
# ===========================================================================

def test_non_evolving_context_predicate():
    from periphery.agents.agent_obsidure import ErrorContext, _is_non_evolving_context

    escalating = ErrorContext(
        attempt=1, error_type="SEMANTIC_REPAIR_REQUIRED", raw_details="",
        mutation_directive="ESCALATE_TO_EXTERNAL_REPAIR",
        recommended_strategy="EXTERNAL_REASONING",
    )
    evolving = ErrorContext(
        attempt=1, error_type="LEAN_BUILD_ERROR", raw_details="",
        mutation_directive="CHANGE_THEOREM_STRUCTURE",
        recommended_strategy="SEMANTIC",
    )
    assert _is_non_evolving_context(escalating) is True
    assert _is_non_evolving_context(evolving) is False


def test_mixed_contexts_do_not_short_circuit():
    """Une seule erreur corrigible suffit à conserver max_attempts."""
    from periphery.agents.agent_obsidure import ErrorContext, _all_contexts_non_evolving

    escalating = ErrorContext(
        attempt=1, error_type="SEMANTIC_REPAIR_REQUIRED", raw_details="",
        mutation_directive="ESCALATE_TO_EXTERNAL_REPAIR",
        recommended_strategy="EXTERNAL_REASONING",
    )
    evolving = ErrorContext(
        attempt=1, error_type="FORBIDDEN_KEYWORD", raw_details="",
        mutation_directive="SANITIZE_AND_RESTRUCTURE_CODE",
        recommended_strategy="CLEAN_PERIPHERAL",
    )
    assert _all_contexts_non_evolving([escalating]) is True
    assert _all_contexts_non_evolving([escalating, evolving]) is False
    assert _all_contexts_non_evolving([]) is False


def test_semantic_repair_short_circuits_after_t1():
    """
    Régression directe de rr_2dfcf0c52e45 : 5 ErrorContext identiques.
    Le cycle doit désormais s'arrêter à T1.
    """
    import periphery.agents.agent_obsidure as ao

    agent = ao.AgentObsidure(verbose=False)
    os_trad = ao.OSTradResult(intent="PYTHON_PATCH_PROPOSAL", source="OFFLINE")

    patches, lean_result, sandbox_dir, stab = agent.phase_d_disruption(
        objective="Repare periphery/math_core/omega_space.py",
        os_trad=os_trad,
        max_attempts=5,
    )
    try:
        assert stab.attempts == 1, "la boucle doit sortir dès T1"
        assert stab.max_attempts == 5, "max_attempts reste inchangé"
        assert stab.final_status == "ESCALATED_TO_EXTERNAL_REPAIR"
        assert stab.passed is False
        assert len(agent._last_error_contexts) == 1, "un seul ErrorContext, pas cinq"
        assert len(stab.errors_history) == 1
    finally:
        shutil.rmtree(sandbox_dir, ignore_errors=True)


def test_evolving_errors_still_use_max_attempts(monkeypatch):
    """
    Les erreurs susceptibles d'évoluer conservent l'intégralité des tentatives.
    """
    import periphery.agents.agent_obsidure as ao

    def _forbidden_patch(objective, os_trad, sandbox_dir, brancher, lean_sb, **kwargs):
        out = Path(sandbox_dir) / "periphery" / "math_core" / "zzz_probe.py"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("# git push origin main\n", encoding="utf-8")
        return ([{
            "path": "periphery/math_core/zzz_probe.py",
            "action": "CREATE_PYTHON_PERIPHERAL",
            "sandbox_path": str(out),
        }], None)

    monkeypatch.setattr(ao, "generate_patches", _forbidden_patch)

    agent = ao.AgentObsidure(verbose=False)
    os_trad = ao.OSTradResult(intent="PYTHON_PATCH_PROPOSAL", source="OFFLINE")

    patches, lean_result, sandbox_dir, stab = agent.phase_d_disruption(
        objective="Cree periphery/math_core/zzz_probe.py",
        os_trad=os_trad,
        max_attempts=3,
    )
    try:
        assert stab.attempts == 3, "un mot-clé interdit peut être corrigé — on rejoue"
        assert stab.final_status == "MAX_ATTEMPTS_REACHED"
        assert stab.passed is False
    finally:
        shutil.rmtree(sandbox_dir, ignore_errors=True)


def test_target_hint_survives_serialization():
    """Régression : le chemin cible ne doit plus se perdre à la sérialisation."""
    from periphery.agents.agent_obsidure import ErrorContext

    ctx = ErrorContext(
        attempt=1, error_type="SEMANTIC_REPAIR_REQUIRED", raw_details="",
        target_hint="periphery/math_core/x.py",
    )
    record = ErrorContextRecord.from_obj(ctx)
    assert record.target_path == "periphery/math_core/x.py"


# ===========================================================================
# Analyse structurelle — pas de logique métier
# ===========================================================================

def test_analyze_detects_unresolved_name():
    from apps.obsidia_api.brody_repair_reasoning import analyze_module_symbols

    a = analyze_module_symbols(_BROKEN_SRC, _BROKEN_REL)
    assert a.parsed is True
    assert "compute_signature" in a.unresolved
    assert "build_record" in a.defined


def test_analyze_reports_syntax_error():
    from apps.obsidia_api.brody_repair_reasoning import analyze_module_symbols

    a = analyze_module_symbols("def f(:\n", "x.py")
    assert a.parsed is False
    assert "line" in a.syntax_error


def test_syntax_error_is_diagnosed_but_not_repaired(fake_repo: Path):
    """Défaut identifié avec certitude, réparation hors capacité — on le dit."""
    broken = fake_repo / "periphery" / "math_core" / "zzz_syntax.py"
    broken.write_text("def f(:\n", encoding="utf-8")

    request = RepairRequest(
        origin="OBSIDURE",
        objective="corrige la syntaxe",
        failure_mode=FailureMode.BUILD_ERROR,
        repo_targets=["periphery/math_core/zzz_syntax.py"],
        target_excerpts={"periphery/math_core/zzz_syntax.py": "def f(:\n"},
    )
    outcome = run_reasoning_cycle(request, repo_root=fake_repo)
    assert outcome.status == DiagnosisStatus.NEEDS_EXTERNAL_ENGINE
    assert outcome.diagnosis.defect_class == "SYNTAX_ERROR"
    assert outcome.diagnosis.confidence == "HIGH"
    assert outcome.proposal is None


def test_unresolvable_symbol_is_not_invented(fake_repo: Path):
    """Un symbole signalé mais introuvable ne donne pas lieu à un import inventé."""
    request = RepairRequest(
        origin="OBSIDURE",
        objective="répare",
        failure_mode=FailureMode.BUILD_ERROR,
        error_contexts=[ErrorContextRecord(
            attempt=1,
            error_type="RUNTIME_NAME_ERROR",
            raw_details="NameError: name 'symbole_totalement_absent' is not defined",
        )],
        repo_targets=[_BROKEN_REL],
        target_excerpts={
            _BROKEN_REL: "def g():\n    return symbole_totalement_absent()\n"
        },
    )
    outcome = run_reasoning_cycle(request, repo_root=fake_repo)
    assert outcome.status == DiagnosisStatus.NEEDS_EXTERNAL_ENGINE
    assert outcome.diagnosis.defect_class == "UNRESOLVED_NAME_UNRESOLVABLE"
    assert outcome.proposal is None


# ===========================================================================
# Conformité des patches Python — trou fermé
# ===========================================================================

def _py_patch(tmp_path: Path, content: str) -> list:
    f = tmp_path / "periphery" / "math_core" / "zzz_conf.py"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")
    return [{
        "path": "periphery/math_core/zzz_conf.py",
        "action": "CREATE_PYTHON_PERIPHERAL",
        "sandbox_path": str(f),
    }]


def test_python_patch_forbidden_keyword_is_caught(tmp_path: Path):
    """
    Régression : la branche CREATE_PYTHON_PERIPHERAL faisait `continue` avant
    l'analyse statique — les mots-clés interdits passaient sans contrôle.
    """
    from periphery.agents.agent_obsidure import _test_patches_conformity

    errors = _test_patches_conformity(
        _py_patch(tmp_path, "import os\nos.system('git push origin main')\n"),
        None, tmp_path,
    )
    assert "FORBIDDEN_KEYWORD" in [e["type"] for e in errors]


def test_python_patch_kernel_replica_is_caught(tmp_path: Path):
    from periphery.agents.agent_obsidure import _test_patches_conformity

    errors = _test_patches_conformity(
        _py_patch(tmp_path, "def decide(x):\n    return 'ALLOW' or 'HOLD' or 'BLOCK'\n"),
        None, tmp_path,
    )
    assert "KERNEL_LOGIC_REPLICA" in [e["type"] for e in errors]


def test_python_patch_clean_content_still_passes(tmp_path: Path):
    """Le durcissement ne doit pas créer de faux positif."""
    from periphery.agents.agent_obsidure import _test_patches_conformity

    errors = _test_patches_conformity(
        _py_patch(tmp_path, "def helper():\n    return {'status': 'STUB'}\n"),
        None, tmp_path,
    )
    assert errors == []


def test_python_patch_outside_periphery_short_circuits(tmp_path: Path):
    """Un chemin hors zone est rejeté sans passer à l'analyse de contenu."""
    from periphery.agents.agent_obsidure import _test_patches_conformity

    errors = _test_patches_conformity(
        [{"path": "docs/x.py", "action": "CREATE_PYTHON_PERIPHERAL", "sandbox_path": ""}],
        None, tmp_path,
    )
    assert [e["type"] for e in errors] == ["PYTHON_OUTPUT_OUTSIDE_PERIPHERY"]


def test_error_extraction_ignores_objective_text():
    """
    Une phrase d'intention n'est pas une observation : le nom cité dans
    l'objectif seul ne doit pas déclencher de réparation.
    """
    from apps.obsidia_api.brody_repair_reasoning import extract_unresolved_names_from_errors

    request = RepairRequest(
        objective="NameError: name 'piege' is not defined",
        summary="",
    )
    assert extract_unresolved_names_from_errors(request) == set()
