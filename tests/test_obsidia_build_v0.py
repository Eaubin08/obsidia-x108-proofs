"""
tests/test_obsidia_build_v0.py
Suite de tests du moteur de build borne TERMINAL_BUILD_BOUNDED_V1

Invariants obligatoires:
- Aucun artefact dans le depot apres pytest (ni _BUILD_SESSIONS, ni worktree, ni branche)
- OBSIDIA_BUILD_STATE_DIR surcharge vers tmp_path
- Depots Git temporaires pour les tests Phase 2
- Aucun subprocess dans obsidia_cli.py (verifie via AST)

Groupes:
  A  - Fonctions pures (detect_domain, is_protected, compute_manifest_hash,
       compute_session_id, estimate_risk, compute_plan, format_plan_proposed,
       validate_approval_token)
  B  - Phase 1: zero ecriture, determinisme
  C  - Phase 2: validation token (echecs attendus)
  D  - Phase 2: execution dans depot temporaire (cycle complet)
  E  - Securite: aucun commit, push, merge; receipt hors depot
  F  - Terminal CLI: integration obsidia_cli.py sans subprocess
  G  - Artefacts et nettoyage post-test
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

# ── Paths ────────────────────────────────────────────────────────────────────
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import obsidia_build as B


# ── Fixture: depot git temporaire ────────────────────────────────────────────

def _make_tmp_repo(base: Path) -> Path:
    """
    Cree un depot Git minimal dans base/repo avec:
    - scripts/gates/ (copies des gates reelles)
    - tests/fixtures/terminal_build_bounded/target.txt
    - tests/fixtures/terminal_build_bounded/test_target_content.py
    - proofs/LEAN_PROOF_SURFACE_MANIFEST.json (copie ou stub)
    - commit initial
    """
    repo = base / "repo"
    repo.mkdir(parents=True)

    subprocess.run(["git", "init", "-b", "main"], cwd=repo,
                   capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=repo,
                   capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo,
                   capture_output=True, check=True)

    # Copier les gates reelles
    real_gates = B.REPO_ROOT / "scripts" / "gates"
    gates_dir = repo / "scripts" / "gates"
    gates_dir.mkdir(parents=True)
    if real_gates.exists():
        for g in real_gates.glob("obsidia_*.py"):
            shutil.copy(g, gates_dir / g.name)

    # Copier le manifest Lean (ou stub)
    proofs_dir = repo / "proofs"
    proofs_dir.mkdir()
    real_manifest = B.REPO_ROOT / "proofs" / "LEAN_PROOF_SURFACE_MANIFEST.json"
    if real_manifest.exists():
        shutil.copy(real_manifest, proofs_dir / "LEAN_PROOF_SURFACE_MANIFEST.json")
    else:
        stub = {
            "manifest_id": "STUB", "total_entries": 0, "layers": {},
            "decision_authority": "KX108_ONLY", "lean_decides": False,
            "runtime_bound": True, "attestation_only": True,
            "lean_ok": True, "forbidden_ok": True,
        }
        (proofs_dir / "LEAN_PROOF_SURFACE_MANIFEST.json").write_text(
            json.dumps(stub), encoding="utf-8"
        )

    # Cible synthetique
    tbd = repo / "tests" / "fixtures" / "terminal_build_bounded"
    tbd.mkdir(parents=True)
    (tbd / "target.txt").write_text(
        "TERMINAL_BUILD_BOUNDED_V1_TARGET_V0\nSynthetic target.\n",
        encoding="utf-8",
    )
    (tbd / "test_target_content.py").write_text(
        textwrap.dedent("""\
            from pathlib import Path
            def test_build_session_applied():
                target = Path(__file__).parent / "target.txt"
                content = target.read_text(encoding="utf-8")
                assert "BUILD_SESSION_APPLIED" in content
        """),
        encoding="utf-8",
    )

    # Commit initial
    subprocess.run(["git", "add", "."], cwd=repo, capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo,
                   capture_output=True, check=True)
    return repo


def _cleanup_repo(repo: Path) -> None:
    """Supprime les worktrees et branches de test, puis le depot."""
    if not repo.exists():
        return
    r = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        cwd=repo, capture_output=True, text=True,
    )
    for line in r.stdout.splitlines():
        if line.startswith("worktree "):
            wt = line[9:].strip()
            if Path(wt) != repo:
                subprocess.run(
                    ["git", "worktree", "remove", "--force", wt],
                    cwd=repo, capture_output=True,
                )
    r2 = subprocess.run(
        ["git", "branch", "--list", "feat/build-*"],
        cwd=repo, capture_output=True, text=True,
    )
    for br in r2.stdout.splitlines():
        br = br.strip().lstrip("* ")
        if br:
            subprocess.run(["git", "branch", "-D", br], cwd=repo, capture_output=True)


@pytest.fixture
def repo(tmp_path):
    """Depot Git temporaire par test. Nettoye automatiquement."""
    r = _make_tmp_repo(tmp_path)
    yield r
    _cleanup_repo(r)


@pytest.fixture
def state_dir(tmp_path):
    """Repertoire d'etat hors depot pour les receipts."""
    d = tmp_path / "state"
    d.mkdir()
    return d


# =============================================================================
# Groupe A — Fonctions pures
# =============================================================================

class TestDetectDomain:
    def test_bank(self):
        assert B.detect_domain("Ajouter un champ bancaire") == "BANK"

    def test_trading(self):
        assert B.detect_domain("Corriger le module trading") == "TRADING"

    def test_gps(self):
        assert B.detect_domain("Mettre a jour le connecteur GPS") == "GPS"

    def test_lean(self):
        assert B.detect_domain("Prouver un theoreme Lean 4") == "LEAN"

    def test_sigma(self):
        assert B.detect_domain("Verifier le gate sigma") == "SIGMA"

    def test_peripheral(self):
        assert B.detect_domain("Appliquer le marqueur synthetique") == "PERIPHERAL"

    def test_deterministe(self):
        obj = "Un objectif quelconque"
        assert B.detect_domain(obj) == B.detect_domain(obj)


class TestIsProtected:
    def test_sealed_cjs(self):
        assert B.is_protected("server.kernel.sealed.cjs")

    def test_proofs(self):
        assert B.is_protected("proofs/lean/Obsidia/SomeTheorem.lean")

    def test_merkle(self):
        assert B.is_protected("merkle_seal.json")

    def test_sigma(self):
        assert B.is_protected("sigma/contracts.py")

    def test_not_protected_target(self):
        assert not B.is_protected(B.SYNTHETIC_TARGET)

    def test_not_protected_connectors(self):
        assert not B.is_protected("connectors/bank_normal_flow.py")


class TestComputeManifestHash:
    def test_determinisme(self, tmp_path):
        (tmp_path / "a.txt").write_text("x", encoding="utf-8")
        h1 = B.compute_manifest_hash(["a.txt"], tmp_path)
        h2 = B.compute_manifest_hash(["a.txt"], tmp_path)
        assert h1 == h2

    def test_change_de_taille(self, tmp_path):
        (tmp_path / "a.txt").write_text("x", encoding="utf-8")
        h1 = B.compute_manifest_hash(["a.txt"], tmp_path)
        (tmp_path / "a.txt").write_text("xy", encoding="utf-8")
        h2 = B.compute_manifest_hash(["a.txt"], tmp_path)
        assert h1 != h2

    def test_longueur_16(self, tmp_path):
        h = B.compute_manifest_hash(["inexistant.py"], tmp_path)
        assert len(h) == 16

    def test_fichier_absent_stable(self, tmp_path):
        h1 = B.compute_manifest_hash(["absent.py"], tmp_path)
        h2 = B.compute_manifest_hash(["absent.py"], tmp_path)
        assert h1 == h2


class TestComputeSessionId:
    def test_deterministe(self):
        s1 = B.compute_session_id("obj", "sha123", "abc")
        s2 = B.compute_session_id("obj", "sha123", "abc")
        assert s1 == s2

    def test_longueur_8(self):
        s = B.compute_session_id("obj", "sha", "mhash")
        assert len(s) == 8

    def test_objectif_different(self):
        s1 = B.compute_session_id("obj1", "sha", "mhash")
        s2 = B.compute_session_id("obj2", "sha", "mhash")
        assert s1 != s2

    def test_sha_different(self):
        s1 = B.compute_session_id("obj", "sha1", "mhash")
        s2 = B.compute_session_id("obj", "sha2", "mhash")
        assert s1 != s2

    def test_mhash_different(self):
        s1 = B.compute_session_id("obj", "sha", "mhash1")
        s2 = B.compute_session_id("obj", "sha", "mhash2")
        assert s1 != s2

    def test_correspond_sha256(self):
        obj, sha, mhash = "Objectif", "shaXXX", "manifest00"
        raw = f"{obj}\x00{sha}\x00{mhash}"
        expected = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:8]
        assert B.compute_session_id(obj, sha, mhash) == expected


class TestValidateApprovalToken:
    def test_valide(self):
        sid, mhash = B.validate_approval_token(
            "HUMAN_APPROVED_BUILD_SESSION=abc12345:0123456789abcdef"
        )
        assert sid == "abc12345"
        assert mhash == "0123456789abcdef"

    def test_mauvais_prefixe(self):
        with pytest.raises(ValueError):
            B.validate_approval_token("WRONG=abc:def")

    def test_sans_manifest_hash(self):
        with pytest.raises(ValueError):
            B.validate_approval_token("HUMAN_APPROVED_BUILD_SESSION=abc12345")

    def test_session_id_vide(self):
        with pytest.raises(ValueError):
            B.validate_approval_token("HUMAN_APPROVED_BUILD_SESSION=:mhash")

    def test_manifest_hash_vide(self):
        with pytest.raises(ValueError):
            B.validate_approval_token("HUMAN_APPROVED_BUILD_SESSION=sid:")

    def test_format_session_id_manifest(self):
        tok = "HUMAN_APPROVED_BUILD_SESSION=12345678:abcdef0123456789"
        sid, mh = B.validate_approval_token(tok)
        assert sid == "12345678"
        assert mh == "abcdef0123456789"


class TestComputePlan:
    def test_retourne_dict(self, repo):
        plan = B.compute_plan("Objectif test", "sha123", repo)
        assert isinstance(plan, dict)

    def test_champs_obligatoires(self, repo):
        plan = B.compute_plan("Objectif", "sha", repo)
        for field in ("session_id", "objective", "domain", "risk", "base_sha",
                      "candidate_files", "approved_scope_proposal",
                      "manifest_hash", "worktree_proposal", "branch_proposal",
                      "tests_required", "gates_required",
                      "decision_authority", "next_human_action",
                      "auto_commit", "auto_push", "status"):
            assert field in plan, f"Champ manquant: {field}"

    def test_session_id_deterministe(self, repo):
        p1 = B.compute_plan("Objectif stable", "sha1", repo)
        p2 = B.compute_plan("Objectif stable", "sha1", repo)
        assert p1["session_id"] == p2["session_id"]

    def test_session_id_change_si_sha_change(self, repo):
        p1 = B.compute_plan("Objectif", "sha1", repo)
        p2 = B.compute_plan("Objectif", "sha2", repo)
        assert p1["session_id"] != p2["session_id"]

    def test_status_plan_proposed(self, repo):
        plan = B.compute_plan("Objectif", "sha", repo)
        assert plan["status"] == "PLAN_PROPOSED"

    def test_auto_commit_never(self, repo):
        plan = B.compute_plan("Objectif", "sha", repo)
        assert plan["auto_commit"] == "NEVER"

    def test_auto_push_never(self, repo):
        plan = B.compute_plan("Objectif", "sha", repo)
        assert plan["auto_push"] == "NEVER"

    def test_token_format_session_manifest(self, repo):
        plan = B.compute_plan("Objectif", "sha", repo)
        token = plan["next_human_action"]
        assert token.startswith("HUMAN_APPROVED_BUILD_SESSION=")
        rest = token.split("=", 1)[1]
        assert ":" in rest
        sid, mhash = rest.split(":", 1)
        assert sid == plan["session_id"]
        assert mhash == plan["manifest_hash"]

    def test_worktree_proposal_contient_session_id(self, repo):
        plan = B.compute_plan("Objectif", "sha", repo)
        assert plan["session_id"] in plan["worktree_proposal"]

    def test_branch_proposal_contient_session_id(self, repo):
        plan = B.compute_plan("Objectif", "sha", repo)
        assert plan["session_id"] in plan["branch_proposal"]


# =============================================================================
# Groupe A2 — explicit_scope (IMPLEMENT_EXPLICIT_CHILD_SESSION_SCOPE_V0)
# =============================================================================

class TestExplicitChildScope:
    """compute_plan(explicit_scope=[...]) : portee AUTORITAIRE, additive au
    mode heuristique historique (explicit_scope=None inchange)."""

    def test_legacy_mode_unchanged_when_none(self, repo):
        plan = B.compute_plan("Appliquer le marqueur synthetique TERMINAL_BUILD_BOUNDED_V1", "sha", repo)
        assert plan["scope_mode"] == "HEURISTIC_LEGACY"
        assert plan["requested_explicit_scope"] is None
        assert plan["status"] == "PLAN_PROPOSED"

    def test_explicit_single_target(self, repo):
        plan = B.compute_plan(
            "objectif", "sha", repo,
            explicit_scope=["tests/fixtures/terminal_build_bounded/target.txt"],
        )
        assert plan["scope_mode"] == "EXPLICIT_CHILD_TARGET"
        assert plan["approved_scope_proposal"] == ["tests/fixtures/terminal_build_bounded/target.txt"]
        assert plan["status"] == "PLAN_PROPOSED"

    def test_objective_cannot_widen_explicit_scope(self, repo):
        wide_objective = "target_b common constants energy all peripheral files bank trading gps"
        plan = B.compute_plan(
            wide_objective, "sha", repo,
            explicit_scope=["tests/fixtures/terminal_build_bounded/target.txt"],
        )
        assert plan["approved_scope_proposal"] == ["tests/fixtures/terminal_build_bounded/target.txt"]

    def test_two_children_never_share_scope(self, repo):
        (repo / "periphery").mkdir(exist_ok=True)
        (repo / "periphery" / "target_a.py").write_text("a\n", encoding="utf-8")
        (repo / "periphery" / "target_b.py").write_text("b\n", encoding="utf-8")
        plan_a = B.compute_plan("obj", "sha", repo, explicit_scope=["periphery/target_a.py"])
        plan_b = B.compute_plan("obj", "sha", repo, explicit_scope=["periphery/target_b.py"])
        assert plan_a["approved_scope_proposal"] == ["periphery/target_a.py"]
        assert plan_b["approved_scope_proposal"] == ["periphery/target_b.py"]
        assert "periphery/target_b.py" not in plan_a["approved_scope_proposal"]
        assert "periphery/target_a.py" not in plan_b["approved_scope_proposal"]

    def test_dependency_does_not_widen_scope(self, repo):
        (repo / "periphery").mkdir(exist_ok=True)
        (repo / "periphery" / "dep_a.py").write_text("a\n", encoding="utf-8")
        (repo / "periphery" / "dep_b.py").write_text("b\n", encoding="utf-8")
        # A depend de B mais la portee explicite d'ecriture de A reste [A]
        plan_a = B.compute_plan("A depends on B", "sha", repo, explicit_scope=["periphery/dep_a.py"])
        assert plan_a["approved_scope_proposal"] == ["periphery/dep_a.py"]

    def test_test_files_not_added_to_write_scope(self, repo):
        plan = B.compute_plan("obj", "sha", repo, explicit_scope=["tests/fixtures/terminal_build_bounded/target.txt"])
        assert plan["approved_scope_proposal"] == ["tests/fixtures/terminal_build_bounded/target.txt"]
        assert "tests/fixtures/terminal_build_bounded/test_target_content.py" not in plan["approved_scope_proposal"]

    def test_cwd_independent_identity(self, repo, monkeypatch):
        p1 = B.compute_plan("obj", "sha", repo, explicit_scope=["tests/fixtures/terminal_build_bounded/target.txt"])
        monkeypatch.chdir(repo.parent)
        p2 = B.compute_plan("obj", "sha", repo, explicit_scope=["tests/fixtures/terminal_build_bounded/target.txt"])
        assert p1["approved_scope_proposal"] == p2["approved_scope_proposal"]
        assert p1["approved_scope_hash"] == p2["approved_scope_hash"]

    def test_absolute_in_repo_target_resolves_same_identity(self, repo):
        rel = "tests/fixtures/terminal_build_bounded/target.txt"
        abs_path = str((repo / rel).resolve())
        p_rel = B.compute_plan("obj", "sha", repo, explicit_scope=[rel])
        p_abs = B.compute_plan("obj", "sha", repo, explicit_scope=[abs_path])
        assert p_rel["approved_scope_proposal"] == p_abs["approved_scope_proposal"] == [rel]
        assert p_rel["approved_scope_hash"] == p_abs["approved_scope_hash"]

    def test_traversal_alias_rejected(self, repo):
        plan = B.compute_plan("obj", "sha", repo, explicit_scope=["periphery/../proofs/x.json"])
        assert plan["status"] == "PLAN_REJECTED"
        assert plan["scope_error"] == "EXPLICIT_SCOPE_PROTECTED_REJECTED"

    def test_relative_dot_protected_alias_rejected(self, repo):
        plan = B.compute_plan("obj", "sha", repo, explicit_scope=["./proofs/x.json"])
        assert plan["status"] == "PLAN_REJECTED"
        assert plan["scope_error"] == "EXPLICIT_SCOPE_PROTECTED_REJECTED"

    def test_outside_repo_relative_rejected(self, repo):
        plan = B.compute_plan("obj", "sha", repo, explicit_scope=["../outside.py"])
        assert plan["status"] == "PLAN_REJECTED"
        assert plan["scope_error"] == "EXPLICIT_SCOPE_OUTSIDE_REPO"

    def test_outside_repo_absolute_rejected(self, repo, tmp_path):
        outside = tmp_path / "elsewhere.py"
        outside.write_text("x\n", encoding="utf-8")
        plan = B.compute_plan("obj", "sha", repo, explicit_scope=[str(outside)])
        assert plan["status"] == "PLAN_REJECTED"
        assert plan["scope_error"] == "EXPLICIT_SCOPE_OUTSIDE_REPO"

    def test_protected_kernel_sealed_rejected(self, repo):
        plan = B.compute_plan(
            "obj", "sha", repo,
            explicit_scope=["runtime_terrain_bank_trading_gps/server.kernel.sealed.cjs"],
        )
        assert plan["status"] == "PLAN_REJECTED"
        assert plan["scope_error"] == "EXPLICIT_SCOPE_PROTECTED_REJECTED"

    def test_wildcard_rejected(self, repo):
        plan = B.compute_plan("obj", "sha", repo, explicit_scope=["periphery/*.py"])
        assert plan["status"] == "PLAN_REJECTED"
        assert plan["scope_error"] == "EXPLICIT_SCOPE_WILDCARD_REJECTED"

    def test_empty_target_rejected(self, repo):
        plan = B.compute_plan("obj", "sha", repo, explicit_scope=[""])
        assert plan["status"] == "PLAN_REJECTED"
        assert plan["scope_error"] == "EXPLICIT_SCOPE_EMPTY_TARGET"

    def test_directory_scope_rejected(self, repo):
        plan = B.compute_plan("obj", "sha", repo, explicit_scope=["tests/fixtures/terminal_build_bounded"])
        assert plan["status"] == "PLAN_REJECTED"
        assert plan["scope_error"] == "EXPLICIT_SCOPE_DIRECTORY_REJECTED"

    def test_new_not_yet_existing_target_supported(self, repo):
        plan = B.compute_plan("obj", "sha", repo, explicit_scope=["periphery/new_module.py"])
        assert plan["status"] == "PLAN_PROPOSED"
        assert plan["approved_scope_proposal"] == ["periphery/new_module.py"]
        assert not (repo / "periphery" / "new_module.py").exists()  # aucune ecriture pendant la planification

    def test_no_fallback_to_heuristic_on_rejection(self, repo):
        plan = B.compute_plan(
            "Appliquer le marqueur synthetique TERMINAL_BUILD_BOUNDED_V1",
            "sha", repo, explicit_scope=["../outside.py"],
        )
        # meme si l'objectif matcherait normalement des fichiers heuristiques,
        # un rejet explicite ne retombe jamais sur la decouverte heuristique
        assert plan["approved_scope_proposal"] == []
        assert plan["status"] == "PLAN_REJECTED"

    def test_approved_scope_hash_changes_with_target(self, repo):
        p1 = B.compute_plan("obj", "sha", repo, explicit_scope=["tests/fixtures/terminal_build_bounded/target.txt"])
        p2 = B.compute_plan("obj", "sha", repo, explicit_scope=["periphery/new_module.py"])
        assert p1["approved_scope_hash"] != p2["approved_scope_hash"]

    def test_scope_error_never_populated_on_success(self, repo):
        plan = B.compute_plan("obj", "sha", repo, explicit_scope=["tests/fixtures/terminal_build_bounded/target.txt"])
        assert plan["scope_error"] is None

    def test_decision_authority_kx108_only(self, repo):
        plan = B.compute_plan("obj", "sha", repo, explicit_scope=["tests/fixtures/terminal_build_bounded/target.txt"])
        assert plan["decision_authority"] == "KX108_ONLY"


# =============================================================================
# Groupe B — Phase 1: zero ecriture
# =============================================================================

class TestPlanProposedZeroWrite:
    def test_aucun_fichier_cree(self, repo):
        before = set(str(p) for p in repo.rglob("*"))
        B.cmd_plan("Objectif synthetique", repo_root=repo)
        after = set(str(p) for p in repo.rglob("*"))
        assert before == after, f"Fichiers crees pendant PLAN_PROPOSED: {after - before}"

    def test_git_status_inchange(self, repo):
        r_before = subprocess.run(
            ["git", "status", "--short"], cwd=repo, capture_output=True, text=True
        )
        B.cmd_plan("Objectif", repo_root=repo)
        r_after = subprocess.run(
            ["git", "status", "--short"], cwd=repo, capture_output=True, text=True
        )
        assert r_before.stdout == r_after.stdout

    def test_aucun_build_sessions_dans_repo(self, repo):
        B.cmd_plan("Objectif", repo_root=repo)
        assert not (repo / "_BUILD_SESSIONS").exists()

    def test_plan_proposed_affiche(self, repo, capsys):
        B.cmd_plan("Objectif synthetique", repo_root=repo)
        out = capsys.readouterr().out
        assert "PLAN_PROPOSED" in out

    def test_aucune_ecriture_affiche(self, repo, capsys):
        B.cmd_plan("Objectif synthetique", repo_root=repo)
        out = capsys.readouterr().out
        assert "AUCUNE ECRITURE" in out

    def test_token_contient_deux_parties(self, repo, capsys):
        B.cmd_plan("Objectif synthetique", repo_root=repo)
        out = capsys.readouterr().out
        assert "HUMAN_APPROVED_BUILD_SESSION=" in out
        import re
        match = re.search(r"HUMAN_APPROVED_BUILD_SESSION=(\w+):(\w+)", out)
        assert match, f"Token incomplet dans: {out}"

    def test_code_retour_zero(self, repo):
        rc = B.cmd_plan("Objectif synthetique", repo_root=repo)
        assert rc == 0

    def test_plan_regenere_identique(self, repo):
        sha = B.get_base_sha(repo)
        p1 = B.compute_plan("Objectif stable", sha, repo)
        p2 = B.compute_plan("Objectif stable", sha, repo)
        assert p1["session_id"] == p2["session_id"]
        assert p1["manifest_hash"] == p2["manifest_hash"]


# =============================================================================
# Groupe C — Phase 2: validation token (echecs attendus)
# =============================================================================

class TestPhase2TokenValidation:
    def _token(self, repo: Path, obj: str):
        sha = B.get_base_sha(repo)
        plan = B.compute_plan(obj, sha, repo)
        return plan["next_human_action"], plan["session_id"], plan["manifest_hash"]

    def test_mauvais_prefixe_bloque(self, repo, state_dir):
        rc = B.cmd_execute(
            "Objectif", "WRONG_PREFIX=abc:def", repo_root=repo, state_dir=state_dir
        )
        assert rc == 2

    def test_token_sans_manifest_hash_bloque(self, repo, state_dir):
        _, sid, _ = self._token(repo, "Objectif")
        rc = B.cmd_execute(
            "Objectif",
            f"HUMAN_APPROVED_BUILD_SESSION={sid}",
            repo_root=repo, state_dir=state_dir,
        )
        assert rc == 2

    def test_objectif_different_bloque(self, repo, state_dir):
        token, _, _ = self._token(repo, "Objectif A")
        rc = B.cmd_execute(
            "Objectif B", token, repo_root=repo, state_dir=state_dir
        )
        assert rc == 2

    def test_manifest_hash_tampered_bloque(self, repo, state_dir):
        _, sid, _ = self._token(repo, "Objectif")
        bad_token = f"HUMAN_APPROVED_BUILD_SESSION={sid}:0000000000000000"
        rc = B.cmd_execute(
            "Objectif", bad_token, repo_root=repo, state_dir=state_dir
        )
        assert rc == 2

    def test_base_sha_change_bloque(self, repo, state_dir):
        sha1 = B.get_base_sha(repo)
        plan = B.compute_plan("Objectif stable", sha1, repo)
        token = plan["next_human_action"]
        (repo / "dummy_change.txt").write_text("change\n", encoding="utf-8")
        subprocess.run(["git", "add", "dummy_change.txt"], cwd=repo, capture_output=True)
        subprocess.run(["git", "commit", "-m", "change"], cwd=repo, capture_output=True)
        rc = B.cmd_execute(
            "Objectif stable", token, repo_root=repo, state_dir=state_dir
        )
        assert rc == 2

    def test_token_session_id_vide_bloque(self, repo, state_dir):
        rc = B.cmd_execute(
            "Objectif",
            "HUMAN_APPROVED_BUILD_SESSION=:mhash",
            repo_root=repo, state_dir=state_dir,
        )
        assert rc == 2

    def test_token_manifest_hash_vide_bloque(self, repo, state_dir):
        rc = B.cmd_execute(
            "Objectif",
            "HUMAN_APPROVED_BUILD_SESSION=sid:",
            repo_root=repo, state_dir=state_dir,
        )
        assert rc == 2


# =============================================================================
# Groupe D — Phase 2: cycle complet (depot temporaire)
# =============================================================================

class TestPhase2Execute:
    OBJ = "Appliquer le marqueur synthetique TERMINAL_BUILD_BOUNDED_V1"

    def _run(self, repo: Path, state_dir: Path):
        sha = B.get_base_sha(repo)
        plan = B.compute_plan(self.OBJ, sha, repo)
        token = plan["next_human_action"]
        wt_name = plan["worktree_proposal"]
        wt_path = repo.parent / wt_name
        rc = B.cmd_execute(self.OBJ, token, repo_root=repo, state_dir=state_dir)
        return rc, wt_path, plan

    def test_worktree_cree_apres_approbation(self, repo, state_dir):
        rc, wt, _ = self._run(repo, state_dir)
        assert wt.exists(), f"Worktree non cree: {wt}"
        _cleanup_repo(repo)

    def test_worktree_absent_avant_approbation(self, repo):
        sha = B.get_base_sha(repo)
        plan = B.compute_plan(self.OBJ, sha, repo)
        wt_path = repo.parent / plan["worktree_proposal"]
        assert not wt_path.exists()

    def test_patch_applique_dans_worktree(self, repo, state_dir):
        _, wt, _ = self._run(repo, state_dir)
        if wt.exists():
            tgt = wt / B.SYNTHETIC_TARGET
            assert tgt.exists()
            content = tgt.read_text(encoding="utf-8")
            assert B.SYNTHETIC_MARKER in content
        _cleanup_repo(repo)

    def test_target_non_modifie_dans_depot_principal(self, repo, state_dir):
        tgt_before = (repo / B.SYNTHETIC_TARGET).read_text(encoding="utf-8")
        self._run(repo, state_dir)
        tgt_after = (repo / B.SYNTHETIC_TARGET).read_text(encoding="utf-8")
        assert tgt_before == tgt_after
        _cleanup_repo(repo)

    def test_receipt_hors_depot(self, repo, state_dir):
        _, _, plan = self._run(repo, state_dir)
        receipt_path = state_dir / plan["session_id"] / "receipt.json"
        assert receipt_path.exists(), f"Receipt absent: {receipt_path}"
        _cleanup_repo(repo)

    def test_receipt_contient_not_committed(self, repo, state_dir):
        _, _, plan = self._run(repo, state_dir)
        receipt_path = state_dir / plan["session_id"] / "receipt.json"
        if receipt_path.exists():
            data = json.loads(receipt_path.read_text(encoding="utf-8"))
            assert data["commit_status"] == "NOT_COMMITTED"
            assert data["push_status"] == "NOT_PUSHED"
            assert data["merge_status"] == "NOT_MERGED"
        _cleanup_repo(repo)

    def test_receipt_pas_dans_depot(self, repo, state_dir):
        before_files = set(str(p) for p in repo.rglob("receipt.json"))
        self._run(repo, state_dir)
        after_files = set(str(p) for p in repo.rglob("receipt.json"))
        assert before_files == after_files
        _cleanup_repo(repo)

    def test_aucun_commit_auto(self, repo, state_dir):
        sha_before = B.get_base_sha(repo)
        self._run(repo, state_dir)
        sha_after = B.get_base_sha(repo)
        assert sha_before == sha_after
        _cleanup_repo(repo)

    def test_receipt_champs_obligatoires(self, repo, state_dir):
        _, _, plan = self._run(repo, state_dir)
        receipt_path = state_dir / plan["session_id"] / "receipt.json"
        if receipt_path.exists():
            data = json.loads(receipt_path.read_text(encoding="utf-8"))
            for field in ("session_id", "objective", "base_sha", "manifest_hash",
                          "approval_token_hash", "worktree", "branch",
                          "approved_scope", "actual_touched_files",
                          "tests_commands", "tests_results",
                          "gates_commands", "gates_results",
                          "kx108_request", "kx108_decision",
                          "first_failure", "diff_hash",
                          "commit_status", "push_status", "merge_status",
                          "decision_authority", "auto_commit", "auto_push"):
                assert field in data, f"Champ receipt manquant: {field}"
        _cleanup_repo(repo)

    def test_kx108_decision_valide(self, repo, state_dir):
        _, _, plan = self._run(repo, state_dir)
        receipt_path = state_dir / plan["session_id"] / "receipt.json"
        if receipt_path.exists():
            data = json.loads(receipt_path.read_text(encoding="utf-8"))
            decision = data.get("kx108_decision", "")
            valid = {
                "ACT", "HOLD", "BLOCK",
                "BLOCKED_KX108_CONTRACT_UNAVAILABLE",
                "BLOCKED_KX108_UNAVAILABLE",
            }
            assert decision in valid, f"Decision KX108 inconnue: {decision}"
        _cleanup_repo(repo)

    def test_scope_exact(self, repo, state_dir):
        sha = B.get_base_sha(repo)
        plan = B.compute_plan(self.OBJ, sha, repo)
        token = plan["next_human_action"]
        wt_name = plan["worktree_proposal"]
        wt_path = repo.parent / wt_name
        B.cmd_execute(self.OBJ, token, repo_root=repo, state_dir=state_dir)
        if wt_path.exists():
            r = subprocess.run(
                ["git", "diff", "--name-only"], cwd=wt_path,
                capture_output=True, text=True
            )
            touched = [f.strip() for f in r.stdout.splitlines() if f.strip()]
            for f in touched:
                assert f in plan["approved_scope_proposal"], f"SCOPE_DRIFT: {f}"
        _cleanup_repo(repo)


# =============================================================================
# Groupe D2 — Liaison session explicite (depot temporaire, JAMAIS le vrai repo)
# =============================================================================

class TestExplicitScopeSessionBinding:
    """Preuve que compute_plan(explicit_scope=...) -> cmd_execute(explicit_scope=...)
    -> receipt conservent la MEME identite de portee canonique, dans un
    depot Git temporaire totalement isole. Chaine complete :
    child.target_path -> plan explicite -> approved_scope de session ->
    receipt/lifecycle -- une seule identite de cible canonique inchangee."""

    TARGET = "tests/fixtures/terminal_build_bounded/target.txt"

    def test_explicit_scope_binds_through_to_receipt(self, repo, state_dir):
        sha = B.get_base_sha(repo)
        plan = B.compute_plan("explicit e2e binding", sha, repo, explicit_scope=[self.TARGET])
        assert plan["status"] == "PLAN_PROPOSED"
        assert plan["scope_mode"] == "EXPLICIT_CHILD_TARGET"
        token = plan["next_human_action"]

        B.cmd_execute(
            "explicit e2e binding", token,
            repo_root=repo, state_dir=state_dir, explicit_scope=[self.TARGET],
        )

        receipt_path = state_dir / plan["session_id"] / "receipt.json"
        assert receipt_path.exists(), f"Receipt absent: {receipt_path}"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        assert receipt["approved_scope"] == [self.TARGET]
        assert receipt["scope_mode"] == "EXPLICIT_CHILD_TARGET"
        assert receipt["approved_scope_hash"] == plan["approved_scope_hash"]
        _cleanup_repo(repo)

    def test_execute_without_explicit_scope_rejects_token_from_explicit_plan(self, repo, state_dir):
        """Si le plan a ete approuve en mode explicite sur une cible que
        l'heuristique ne decouvrirait jamais (hors tests/fixtures/...),
        re-executer SANS explicit_scope doit regenerer un plan heuristique
        different -> session_id/manifest_hash divergent -> token rejete
        (fail-closed, pas de fallback silencieux)."""
        (repo / "periphery").mkdir(exist_ok=True)
        (repo / "periphery" / "not_heuristically_found.py").write_text("x\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=repo, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "add target"], cwd=repo, capture_output=True, check=True)

        sha = B.get_base_sha(repo)
        plan = B.compute_plan("obj", sha, repo, explicit_scope=["periphery/not_heuristically_found.py"])
        token = plan["next_human_action"]
        rc = B.cmd_execute("obj", token, repo_root=repo, state_dir=state_dir)  # sans explicit_scope
        assert rc == 2
        _cleanup_repo(repo)

    def test_two_children_produce_two_independent_sessions(self, repo, state_dir):
        (repo / "periphery").mkdir(exist_ok=True)
        (repo / "periphery" / "e2e_a.py").write_text("a\n", encoding="utf-8")
        (repo / "periphery" / "e2e_b.py").write_text("b\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=repo, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "add e2e targets"], cwd=repo, capture_output=True, check=True)

        sha = B.get_base_sha(repo)
        plan_a = B.compute_plan("obj a", sha, repo, explicit_scope=["periphery/e2e_a.py"])
        plan_b = B.compute_plan("obj b", sha, repo, explicit_scope=["periphery/e2e_b.py"])
        assert plan_a["session_id"] != plan_b["session_id"]

        B.cmd_execute("obj a", plan_a["next_human_action"], repo_root=repo, state_dir=state_dir, explicit_scope=["periphery/e2e_a.py"])
        B.cmd_execute("obj b", plan_b["next_human_action"], repo_root=repo, state_dir=state_dir, explicit_scope=["periphery/e2e_b.py"])

        receipt_a = json.loads((state_dir / plan_a["session_id"] / "receipt.json").read_text(encoding="utf-8"))
        receipt_b = json.loads((state_dir / plan_b["session_id"] / "receipt.json").read_text(encoding="utf-8"))
        assert receipt_a["approved_scope"] == ["periphery/e2e_a.py"]
        assert receipt_b["approved_scope"] == ["periphery/e2e_b.py"]
        _cleanup_repo(repo)


# =============================================================================
# Groupe E — Securite: invariants absolus
# =============================================================================

class TestSecurityInvariants:
    def test_auto_commit_never_dans_plan(self, repo):
        plan = B.compute_plan("Objectif", "sha", repo)
        assert plan["auto_commit"] == "NEVER"

    def test_auto_push_never_dans_plan(self, repo):
        plan = B.compute_plan("Objectif", "sha", repo)
        assert plan["auto_push"] == "NEVER"

    def test_auto_merge_never_dans_plan(self, repo):
        plan = B.compute_plan("Objectif", "sha", repo)
        assert plan.get("auto_merge") == "NEVER"

    def test_decision_authority_kx108_only(self, repo):
        plan = B.compute_plan("Objectif", "sha", repo)
        assert plan["decision_authority"] == "KX108_ONLY"

    def test_protected_files_listes(self, repo):
        plan = B.compute_plan("Objectif", "sha", repo)
        pf = plan.get("protected_files", [])
        assert any("merkle_seal.json" in f for f in pf)
        assert any("proofs" in f for f in pf)

    def test_synthetic_target_non_protege(self):
        assert not B.is_protected(B.SYNTHETIC_TARGET)

    def test_proofs_protege(self):
        assert B.is_protected("proofs/lean/test.lean")

    def test_kernel_protege(self):
        assert B.is_protected("server.kernel.sealed.cjs")

    def test_token_lie_session_et_manifest(self, repo):
        sha = B.get_base_sha(repo)
        plan = B.compute_plan("Objectif", sha, repo)
        token = plan["next_human_action"]
        sid, mhash = B.validate_approval_token(token)
        assert sid == plan["session_id"]
        assert mhash == plan["manifest_hash"]

    def test_aucun_build_sessions_dans_vrai_depot(self):
        assert not (B.REPO_ROOT / "_BUILD_SESSIONS").exists()


# =============================================================================
# Groupe F — Terminal CLI sans subprocess
# =============================================================================

class TestTerminalCLIBuild:
    def test_aucun_subprocess_dans_handle_build_plan(self):
        """_handle_build_plan ne doit pas appeler subprocess.*"""
        cli_path = SCRIPTS_DIR / "obsidia_cli.py"
        source = cli_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(cli_path))

        class SubprocessInBuildChecker(ast.NodeVisitor):
            def __init__(self):
                self.violations: list[str] = []
                self._in_build = False

            def visit_FunctionDef(self, node):
                if node.name == "_handle_build_plan":
                    self._in_build = True
                    self.generic_visit(node)
                    self._in_build = False
                else:
                    self.generic_visit(node)

            def visit_Call(self, node):
                if self._in_build:
                    fn = node.func
                    if isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name):
                        if fn.value.id == "subprocess":
                            self.violations.append(
                                f"subprocess.{fn.attr} ligne {node.lineno}"
                            )
                self.generic_visit(node)

        checker = SubprocessInBuildChecker()
        checker.visit(tree)
        assert not checker.violations, f"subprocess dans _handle_build_plan: {checker.violations}"

    def test_handle_build_plan_utilise_importlib(self):
        cli_path = SCRIPTS_DIR / "obsidia_cli.py"
        source = cli_path.read_text(encoding="utf-8")
        assert "importlib" in source or "import_module" in source

    def test_handle_build_plan_present_dans_cli(self):
        cli_path = SCRIPTS_DIR / "obsidia_cli.py"
        source = cli_path.read_text(encoding="utf-8")
        assert "_handle_build_plan" in source

    def test_cmd0_build_dans_main(self):
        cli_path = SCRIPTS_DIR / "obsidia_cli.py"
        source = cli_path.read_text(encoding="utf-8")
        assert 'cmd0 == "build"' in source or "cmd0 == 'build'" in source

    def test_format_plan_proposed_pure(self, repo):
        plan = B.compute_plan("Objectif deterministe", "sha_fixe", repo)
        out1 = B.format_plan_proposed(plan, "API_DOWN")
        out2 = B.format_plan_proposed(plan, "API_DOWN")
        assert out1 == out2

    def test_aucun_artefact_apres_phase1(self, repo):
        before = set(str(p) for p in repo.rglob("*"))
        B.cmd_plan("Objectif synthetique", repo_root=repo)
        after = set(str(p) for p in repo.rglob("*"))
        assert before == after, f"Artefacts crees: {after - before}"

    def test_plan_proposed_retour_zero(self, repo):
        rc = B.cmd_plan("Objectif", repo_root=repo)
        assert rc == 0


# =============================================================================
# Groupe G — Artefacts et nettoyage post-test
# =============================================================================

class TestNoArtifacts:
    def test_aucun_build_sessions_apres_tests(self):
        assert not (B.REPO_ROOT / "_BUILD_SESSIONS").exists()

    def _worktrees_created_by_pytest(self) -> list[str]:
        """
        Retourne les worktrees de build NON legitimes (non couverts par un receipt hors depot).
        Le worktree du test runtime est exclu: il est intentionnellement conserve pour revue humaine.
        """
        import os
        r = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=B.REPO_ROOT, capture_output=True, text=True
        )
        build_lines = [
            line for line in r.stdout.splitlines()
            if "obsidia-x108-proofs_BUILD_" in line
        ]
        # Filtrer les worktrees couverts par un receipt hors depot (runtime legitime)
        lad = os.environ.get("LOCALAPPDATA", "")
        state_base = Path(lad) / "Obsidia" / "build_sessions" if lad else None
        illegitimate = []
        for line in build_lines:
            wt_path_str = line.split("obsidia-x108-proofs_BUILD_")[-1]
            sid_candidate = wt_path_str.strip()[:8]
            has_receipt = (
                state_base is not None
                and (state_base / sid_candidate / "receipt.json").exists()
            )
            if not has_receipt:
                illegitimate.append(line)
        return illegitimate

    def test_aucun_worktree_build_dans_repo_reel(self):
        """
        Verifie qu'aucun worktree build n'a ete cree par les tests unitaires.
        Les worktrees du test runtime (couverts par un receipt hors depot) sont exclus.
        """
        illegitimate = self._worktrees_created_by_pytest()
        assert not illegitimate, f"Worktrees build sans receipt: {illegitimate}"

    def test_aucune_branche_build_dans_repo_reel(self):
        """
        Verifie qu'aucune branche feat/build-* illégitime n'existe dans le depot reel.
        Les branches correspondant a des sessions avec receipt hors depot sont tolerees.
        """
        import os
        r = subprocess.run(
            ["git", "branch", "--list", "feat/build-*"],
            cwd=B.REPO_ROOT, capture_output=True, text=True
        )
        lad = os.environ.get("LOCALAPPDATA", "")
        state_base = Path(lad) / "Obsidia" / "build_sessions" if lad else None
        branches = []
        for b in r.stdout.splitlines():
            b = b.strip().lstrip("+ * ")
            if not b:
                continue
            # Extraire session_id depuis feat/build-<sid>
            if b.startswith("feat/build-"):
                sid = b[len("feat/build-"):][:8]
                has_receipt = (
                    state_base is not None
                    and (state_base / sid / "receipt.json").exists()
                )
                if has_receipt:
                    continue
            branches.append(b)
        assert not branches, f"Branches build sans receipt: {branches}"

    def test_worktree_principal_protege_inchange(self):
        r = subprocess.run(
            ["git", "diff", "--", "proofs/", "formal/",
             "runtime_terrain_bank_trading_gps/server.kernel.sealed.cjs",
             "merkle_seal.json"],
            cwd=B.REPO_ROOT, capture_output=True, text=True
        )
        assert not r.stdout.strip(), f"Fichiers proteges modifies: {r.stdout[:200]}"


# =============================================================================
# Groupe H — Mécanisme de reprise KX108 (cmd_resume_kx108)
# =============================================================================

def _make_phase2_state(repo: Path, state_dir: Path, obj: str):
    """Exécute Phase 2 et retourne (session_id, worktree_path, plan)."""
    sha = B.get_base_sha(repo)
    plan = B.compute_plan(obj, sha, repo)
    token = plan["next_human_action"]
    B.cmd_execute(obj, token, repo_root=repo, state_dir=state_dir)
    wt_path = repo.parent / plan["worktree_proposal"]
    return plan["session_id"], wt_path, plan


# Fixture HTTP mock léger pour simuler les réponses KX108
import http.server
import threading
import urllib.request


class _KX108MockServer:
    """Serveur HTTP minimal simulant /kernel/ragnarok pour les tests."""

    def __init__(self, response_body: dict, status: int = 200):
        self._response_body = json.dumps(response_body).encode("utf-8")
        self._status = status
        self._server: http.server.HTTPServer | None = None
        self._port: int = 0
        self._thread: threading.Thread | None = None

    def start(self) -> int:
        response_body = self._response_body
        status = self._status

        class _Handler(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(response_body)

            def log_message(self, fmt, *args):
                pass  # silence

        self._server = http.server.HTTPServer(("127.0.0.1", 0), _Handler)
        self._port = self._server.server_address[1]
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        return self._port

    def stop(self):
        if self._server:
            self._server.shutdown()


class TestResumeKX108:
    OBJ = "Appliquer le marqueur synthetique TERMINAL_BUILD_BOUNDED_V1"

    def _phase2(self, repo: Path, state_dir: Path):
        return _make_phase2_state(repo, state_dir, self.OBJ)

    def _resume(self, session_id: str, repo: Path, state_dir: Path) -> int:
        return B.cmd_resume_kx108(session_id, repo_root=repo, state_dir=state_dir)

    # -- R1: session inexistante --
    def test_session_inexistante_bloquee(self, repo, state_dir):
        rc = self._resume("00000000", repo, state_dir)
        assert rc == 2

    # -- R2: receipt absent --
    def test_receipt_absent_bloque(self, repo, state_dir):
        fake_sid = "aaaabbbb"
        (state_dir / fake_sid).mkdir()
        rc = self._resume(fake_sid, repo, state_dir)
        assert rc == 2

    # -- R3: worktree absent --
    def test_mauvais_worktree_bloque(self, tmp_path, state_dir):
        # Créer un receipt pointant vers un worktree inexistant
        fake_sid = "bbbbcccc"
        sd = state_dir / fake_sid
        sd.mkdir()
        receipt = {
            "session_id": fake_sid,
            "base_sha": "deadbeef",
            "manifest_hash": "abcd1234abcd1234",
            "approved_scope": ["tests/fixtures/terminal_build_bounded/target.txt"],
            "worktree": str(tmp_path / "nonexistent_worktree"),
            "branch": "feat/build-bbbbcccc",
            "diff_hash": "0000000000000000",
            "commit_status": "NOT_COMMITTED",
            "push_status": "NOT_PUSHED",
            "merge_status": "NOT_MERGED",
        }
        (sd / "receipt.json").write_text(json.dumps(receipt), encoding="utf-8")
        rc = B.cmd_resume_kx108(fake_sid, repo_root=tmp_path, state_dir=state_dir)
        assert rc == 2

    # -- R4: mauvaise branche --
    def test_mauvaise_branche_bloque(self, repo, state_dir):
        sid, wt, plan = self._phase2(repo, state_dir)
        # Modifier le receipt pour indiquer une mauvaise branche
        rpath = state_dir / sid / "receipt.json"
        r = json.loads(rpath.read_text(encoding="utf-8"))
        r["branch"] = "feat/build-wrongbranch"
        rpath.write_text(json.dumps(r), encoding="utf-8")
        rc = self._resume(sid, repo, state_dir)
        assert rc == 2
        _cleanup_repo(repo)

    # -- R5: base_sha modifié --
    def test_base_sha_modifie_bloque(self, repo, state_dir):
        sha_orig = B.get_base_sha(repo)
        plan = B.compute_plan(self.OBJ, sha_orig, repo)
        token = plan["next_human_action"]
        sid = plan["session_id"]
        B.cmd_execute(self.OBJ, token, repo_root=repo, state_dir=state_dir)
        # Créer un commit pour changer HEAD
        (repo / "extra_file.txt").write_text("extra\n", encoding="utf-8")
        subprocess.run(["git", "add", "extra_file.txt"], cwd=repo, capture_output=True)
        subprocess.run(["git", "commit", "-m", "extra"], cwd=repo, capture_output=True)
        rc = self._resume(sid, repo, state_dir)
        assert rc == 2
        _cleanup_repo(repo)

    # -- R6: manifest_hash modifié --
    def test_manifest_hash_modifie_bloque(self, repo, state_dir):
        sid, wt, plan = self._phase2(repo, state_dir)
        # Modifier la taille du fichier candidat dans le repo principal
        tgt = repo / B.SYNTHETIC_TARGET
        tgt.write_text("MODIFIE\n", encoding="utf-8")
        rc = self._resume(sid, repo, state_dir)
        assert rc == 2
        _cleanup_repo(repo)

    # -- R7: scope drift --
    def test_scope_drift_bloque(self, repo, state_dir):
        sid, wt, plan = self._phase2(repo, state_dir)
        if wt.exists():
            # Ajouter un fichier hors scope au staged du worktree
            extra = wt / "tests" / "fixtures" / "terminal_build_bounded" / "extra.txt"
            extra.write_text("drift\n", encoding="utf-8")
            subprocess.run(["git", "add", str(extra)], cwd=wt, capture_output=True)
        rc = self._resume(sid, repo, state_dir)
        assert rc == 2
        _cleanup_repo(repo)

    # -- R8: diff_hash modifié (ET marqueur absent) --
    def test_diff_hash_modifie_et_marqueur_absent_bloque(self, repo, state_dir):
        sid, wt, plan = self._phase2(repo, state_dir)
        if wt.exists():
            tgt = wt / B.SYNTHETIC_TARGET
            # Écraser le contenu (supprimer le marqueur)
            tgt.write_text("CONTENU_SANS_MARQUEUR\n", encoding="utf-8")
            subprocess.run(["git", "add", str(tgt)], cwd=wt, capture_output=True)
        rc = self._resume(sid, repo, state_dir)
        assert rc == 2
        _cleanup_repo(repo)

    # -- R9: fichier protégé dans staged --
    def test_fichier_protege_bloque(self, repo, state_dir):
        sid, wt, plan = self._phase2(repo, state_dir)
        if wt.exists():
            # Creer un fichier dans proofs/ (protégé) et le stager
            prot = wt / "proofs" / "test_prot.txt"
            prot.write_text("prot\n", encoding="utf-8")
            subprocess.run(["git", "add", str(prot)], cwd=wt, capture_output=True)
        rc = self._resume(sid, repo, state_dir)
        assert rc == 2
        _cleanup_repo(repo)

    # -- R10: commit déjà présent --
    def test_commit_existant_bloque(self, repo, state_dir):
        sid, wt, plan = self._phase2(repo, state_dir)
        if wt.exists():
            # Stager et committer dans le worktree
            subprocess.run(
                ["git", "commit", "-m", "unauthorized_commit"],
                cwd=wt, capture_output=True,
            )
        rc = self._resume(sid, repo, state_dir)
        assert rc == 2
        _cleanup_repo(repo)

    # -- R11: test ciblé en échec --
    def test_test_cible_echec_bloque_kx108(self, repo, state_dir):
        sid, wt, plan = self._phase2(repo, state_dir)
        if wt.exists():
            # Supprimer le marqueur du target → test FAIL
            tgt = wt / B.SYNTHETIC_TARGET
            tgt.write_text("CONTENU_SANS_MARQUEUR_MAIS_STAGED\n", encoding="utf-8")
            subprocess.run(["git", "add", str(tgt)], cwd=wt, capture_output=True)
            # Laisser le marqueur absent pour que le test fail
        rc = self._resume(sid, repo, state_dir)
        assert rc == 2
        _cleanup_repo(repo)

    # -- R12: gate en échec bloque KX108 --
    def test_gate_echec_bloque_kx108(self, repo, state_dir, monkeypatch):
        """Une gate qui échoue doit bloquer avant l'appel KX108."""
        sid, wt, plan = self._phase2(repo, state_dir)
        # Garder trace de si KX108 a été appelé
        kx108_called = []
        monkeypatch.setattr(B, "_call_kx108", lambda p, **kw: (kx108_called.append(1), ("ACT", {}))[1])
        # Faire échouer scope_guard en remplaçant la gate par un script qui sort avec code 1
        gate_path = repo / "scripts" / "gates" / "obsidia_commit_scope_guard.py"
        if gate_path.exists():
            original = gate_path.read_text(encoding="utf-8")
            gate_path.write_text(
                "import sys\nprint('GATE_FAIL_INJECTED')\nsys.exit(1)\n",
                encoding="utf-8"
            )
        rc = self._resume(sid, repo, state_dir)
        if gate_path.exists():
            gate_path.write_text(original, encoding="utf-8")
        assert rc == 2, "Une gate en echec doit bloquer"
        assert not kx108_called, "KX108 ne doit pas etre appele si une gate echoue"
        _cleanup_repo(repo)

    # -- R13: réponse ACT reconnue (mock) --
    def test_reponse_act_reconnue(self, repo, state_dir, monkeypatch):
        sid, wt, plan = self._phase2(repo, state_dir)
        monkeypatch.setattr(B, "_call_kx108",
                            lambda p, **kw: ("ACT", {"action": "ACT", "mock": True}))
        rc = self._resume(sid, repo, state_dir)
        assert rc == 0
        r = json.loads((state_dir / sid / "receipt.json").read_text(encoding="utf-8"))
        assert r["kx108_decision"] == "ACT"
        _cleanup_repo(repo)

    # -- R14: réponse HOLD reconnue (mock) --
    def test_reponse_hold_reconnue(self, repo, state_dir, monkeypatch):
        sid, wt, plan = self._phase2(repo, state_dir)
        monkeypatch.setattr(B, "_call_kx108",
                            lambda p, **kw: ("HOLD", {"decision": "HOLD", "mock": True}))
        rc = self._resume(sid, repo, state_dir)
        assert rc == 0
        r = json.loads((state_dir / sid / "receipt.json").read_text(encoding="utf-8"))
        assert r["kx108_decision"] == "HOLD"
        _cleanup_repo(repo)

    # -- R15: réponse BLOCK reconnue (mock) --
    def test_reponse_block_reconnue(self, repo, state_dir, monkeypatch):
        sid, wt, plan = self._phase2(repo, state_dir)
        monkeypatch.setattr(B, "_call_kx108",
                            lambda p, **kw: ("BLOCK", {"verdict": "BLOCK", "mock": True}))
        rc = self._resume(sid, repo, state_dir)
        assert rc == 2
        r = json.loads((state_dir / sid / "receipt.json").read_text(encoding="utf-8"))
        assert r["kx108_decision"] == "BLOCK"
        _cleanup_repo(repo)

    # -- R16: réponse inconnue → fail-closed --
    def test_reponse_inconnue_fail_closed(self, repo, state_dir, monkeypatch):
        sid, wt, plan = self._phase2(repo, state_dir)
        monkeypatch.setattr(B, "_call_kx108",
                            lambda p, **kw: ("BLOCKED_KX108_CONTRACT_UNAVAILABLE", {"error": "unknown"}))
        rc = self._resume(sid, repo, state_dir)
        assert rc == 2
        r = json.loads((state_dir / sid / "receipt.json").read_text(encoding="utf-8"))
        assert r["kx108_decision"] == "BLOCKED_KX108_CONTRACT_UNAVAILABLE"
        _cleanup_repo(repo)

    # -- R17: kernel inaccessible → fail-closed --
    def test_kernel_inaccessible_fail_closed(self, repo, state_dir, monkeypatch):
        sid, wt, plan = self._phase2(repo, state_dir)
        monkeypatch.setattr(B, "_call_kx108",
                            lambda p, **kw: ("BLOCKED_KX108_UNAVAILABLE", {"error": "conn refused"}))
        rc = self._resume(sid, repo, state_dir)
        assert rc == 2
        r = json.loads((state_dir / sid / "receipt.json").read_text(encoding="utf-8"))
        assert r["kx108_decision"] == "BLOCKED_KX108_UNAVAILABLE"
        _cleanup_repo(repo)

    # -- R18: aucun patch réappliqué --
    def test_aucun_patch_reapplique(self, repo, state_dir, monkeypatch):
        monkeypatch.setattr(B, "_call_kx108",
                            lambda p, **kw: ("ACT", {"action": "ACT"}))
        sid, wt, plan = self._phase2(repo, state_dir)
        if wt.exists():
            content_before = (wt / B.SYNTHETIC_TARGET).read_text(encoding="utf-8")
        self._resume(sid, repo, state_dir)
        if wt.exists():
            content_after = (wt / B.SYNTHETIC_TARGET).read_text(encoding="utf-8")
            # Le marqueur ne doit pas être dupliqué
            marker = f"{B.SYNTHETIC_MARKER}: {sid}"
            assert content_after.count(marker) == 1, "Marqueur duplique!"
        _cleanup_repo(repo)

    # -- R19: aucun nouveau worktree --
    def test_aucun_nouveau_worktree(self, repo, state_dir, monkeypatch):
        monkeypatch.setattr(B, "_call_kx108", lambda p, **kw: ("ACT", {}))
        sid, wt, _ = self._phase2(repo, state_dir)
        wt_before = set(str(p) for p in repo.parent.iterdir() if "BUILD_" in str(p))
        self._resume(sid, repo, state_dir)
        wt_after = set(str(p) for p in repo.parent.iterdir() if "BUILD_" in str(p))
        assert wt_before == wt_after, f"Nouveaux worktrees: {wt_after - wt_before}"
        _cleanup_repo(repo)

    # -- R20: aucune nouvelle branche --
    def test_aucune_nouvelle_branche(self, repo, state_dir, monkeypatch):
        monkeypatch.setattr(B, "_call_kx108", lambda p, **kw: ("ACT", {}))
        sid, wt, _ = self._phase2(repo, state_dir)
        r = subprocess.run(["git", "branch", "--list"], cwd=repo,
                           capture_output=True, text=True)
        branches_before = set(r.stdout.splitlines())
        self._resume(sid, repo, state_dir)
        r2 = subprocess.run(["git", "branch", "--list"], cwd=repo,
                             capture_output=True, text=True)
        branches_after = set(r2.stdout.splitlines())
        assert branches_before == branches_after
        _cleanup_repo(repo)

    # -- R21: aucun commit --
    def test_aucun_commit_lors_reprise(self, repo, state_dir, monkeypatch):
        monkeypatch.setattr(B, "_call_kx108", lambda p, **kw: ("ACT", {}))
        sha_before = B.get_base_sha(repo)
        sid, wt, _ = self._phase2(repo, state_dir)
        self._resume(sid, repo, state_dir)
        sha_after = B.get_base_sha(repo)
        assert sha_before == sha_after
        _cleanup_repo(repo)

    # -- R22: aucun push --
    def test_aucun_push_lors_reprise(self, repo, state_dir, monkeypatch):
        monkeypatch.setattr(B, "_call_kx108", lambda p, **kw: ("ACT", {}))
        sid, wt, _ = self._phase2(repo, state_dir)
        self._resume(sid, repo, state_dir)
        r = subprocess.run(["git", "remote", "-v"], cwd=repo,
                           capture_output=True, text=True)
        assert not r.stdout.strip()
        _cleanup_repo(repo)

    # -- R23: aucun merge --
    def test_aucun_merge_lors_reprise(self, repo, state_dir, monkeypatch):
        monkeypatch.setattr(B, "_call_kx108", lambda p, **kw: ("ACT", {}))
        sid, wt, _ = self._phase2(repo, state_dir)
        sha_wt_before = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=wt,
            capture_output=True, text=True
        ).stdout.strip()
        self._resume(sid, repo, state_dir)
        sha_wt_after = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=wt,
            capture_output=True, text=True
        ).stdout.strip()
        assert sha_wt_before == sha_wt_after
        _cleanup_repo(repo)

    # -- R24: receipt mis à jour hors dépôt --
    def test_receipt_mis_a_jour_hors_depot(self, repo, state_dir, monkeypatch):
        monkeypatch.setattr(B, "_call_kx108", lambda p, **kw: ("ACT", {"action": "ACT"}))
        sid, wt, _ = self._phase2(repo, state_dir)
        self._resume(sid, repo, state_dir)
        r = json.loads((state_dir / sid / "receipt.json").read_text(encoding="utf-8"))
        assert "resume_kx108" in str(r.get("timestamps", {}))
        assert r["kx108_decision"] == "ACT"
        # Receipt hors dépôt: pas dans le repo
        assert not any((repo / sid).exists() for _ in [1])
        _cleanup_repo(repo)

    # -- R25: obsidia_cli.py reste sans subprocess --
    def test_obsidia_cli_sans_subprocess_apres_resume(self):
        cli_path = SCRIPTS_DIR / "obsidia_cli.py"
        source = cli_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(cli_path))

        class SubprocessChecker(ast.NodeVisitor):
            def __init__(self):
                self.violations: list[str] = []
                self._in_build = False

            def visit_FunctionDef(self, node):
                if node.name == "_handle_build_plan":
                    self._in_build = True
                    self.generic_visit(node)
                    self._in_build = False
                else:
                    self.generic_visit(node)

            def visit_Call(self, node):
                if self._in_build:
                    fn = node.func
                    if isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name):
                        if fn.value.id == "subprocess":
                            self.violations.append(f"L{node.lineno}")
                self.generic_visit(node)

        checker = SubprocessChecker()
        checker.visit(tree)
        assert not checker.violations
