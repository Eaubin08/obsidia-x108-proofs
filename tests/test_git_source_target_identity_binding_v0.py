"""
tests/test_git_source_target_identity_binding_v0.py
=====================================================
Suite BIND_GIT_SOURCE_AND_TARGET_IDENTITY_TO_BATCH_V0.

Distingue explicitement trois identités qui doivent rester
composables mais jamais confondues :

  A. Identité de CONTENU source (blob_sha, content_sha256)
  B. Identité de PROVENANCE source (dépôt, commit, chemin historique)
  C. Identité d'INTENTION D'INTÉGRATION (target_path, opération)

Couvre :
  1. batch_hash lie explicitement target_path ET la provenance Git
     complète (dépôt, commit, blob, chemin historique, SHA256 complet)
     — pas seulement le source_hash tronqué à 16 caractères.
  2. verify_batch_integrity détecte la dérive de CHAQUE champ Git lié,
     et de l'intention d'opération, dans une proposition stockée altérée.
  3. Compatibilité ascendante : batch_hash_version=1 (formule historique)
     reste inchangée et reproductible pour les appelants qui ne passent
     pas les nouveaux paramètres.
  4. Non-régression filesystem.
  5. Forme ACD-01 : chemin historique == chemin cible (même chaîne),
     octets réellement différents — identité d'entrée et batch valides,
     cible incluse dans l'identité, aucun raccourci no-op.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import obsidia_branching_ledger as L  # noqa: E402
from obsidia_batch_selector import (  # noqa: E402
    batch_hash_from_proposal,
    propose_batch,
    _load_batch,
    _save_batch,
)
from obsidia_batch_execution import (  # noqa: E402
    verify_batch_integrity,
    assess_materiality,
    MEANINGFUL_DELTA,
)


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    assert result.returncode == 0, f"git {args} failed: {result.stderr}"
    return result.stdout.strip()


@pytest.fixture
def synthetic_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "synthetic_repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")

    src = repo / "src"
    src.mkdir()
    (src / "module.py").write_bytes(b"CONTENT_A\n")
    _git(repo, "add", "src/module.py")
    _git(repo, "commit", "-q", "-m", "C1: content A")
    c1 = _git(repo, "rev-parse", "HEAD")

    (src / "module.py").write_bytes(b"CONTENT_B\n")
    _git(repo, "add", "src/module.py")
    _git(repo, "commit", "-q", "-m", "C2: content B")

    _git(repo, "branch", "candidate", c1)
    return repo


def _register(repo, ledger_dir, target_path=None, commit="candidate", path="src/module.py"):
    return L.register_git_blob_source(
        commit, path, target_path=target_path, repo_root=repo, ledger_dir=ledger_dir,
    )


def _propose(ledger_dir, selector_dir, entry_id):
    return propose_batch(
        objective="test", ledger_dir=ledger_dir, selector_dir=selector_dir,
        candidate_entry_ids=[entry_id],
    )


# ─── 1. batch_hash lie la provenance Git complète (unitaire, sans I/O) ──────

class TestBatchHashBindsFullGitIdentity:
    def _base_identity(self):
        return {
            "source_kind": "GIT_BLOB",
            "source_repository_identity": "/repo/A",
            "source_git_commit_sha": "c" * 40,
            "source_git_blob_sha": "b" * 40,
            "source_git_historical_path": "src/module.py",
            "source_content_sha256": "f" * 64,
            "target_path": "dst/module.py",
        }

    def test_target_path_bound(self):
        base = self._base_identity()
        alt = dict(base, target_path="dst/other.py")
        h1 = batch_hash_from_proposal(["e1"], ["hash1"], [], "obj", 5, git_source_identities=[base])
        h2 = batch_hash_from_proposal(["e1"], ["hash1"], [], "obj", 5, git_source_identities=[alt])
        assert h1 != h2

    def test_repository_identity_bound(self):
        base = self._base_identity()
        alt = dict(base, source_repository_identity="/repo/B")
        h1 = batch_hash_from_proposal(["e1"], ["hash1"], [], "obj", 5, git_source_identities=[base])
        h2 = batch_hash_from_proposal(["e1"], ["hash1"], [], "obj", 5, git_source_identities=[alt])
        assert h1 != h2

    def test_commit_sha_bound(self):
        base = self._base_identity()
        alt = dict(base, source_git_commit_sha="d" * 40)
        h1 = batch_hash_from_proposal(["e1"], ["hash1"], [], "obj", 5, git_source_identities=[base])
        h2 = batch_hash_from_proposal(["e1"], ["hash1"], [], "obj", 5, git_source_identities=[alt])
        assert h1 != h2

    def test_blob_sha_bound(self):
        base = self._base_identity()
        alt = dict(base, source_git_blob_sha="e" * 40)
        h1 = batch_hash_from_proposal(["e1"], ["hash1"], [], "obj", 5, git_source_identities=[base])
        h2 = batch_hash_from_proposal(["e1"], ["hash1"], [], "obj", 5, git_source_identities=[alt])
        assert h1 != h2

    def test_historical_path_bound(self):
        base = self._base_identity()
        alt = dict(base, source_git_historical_path="src/other.py")
        h1 = batch_hash_from_proposal(["e1"], ["hash1"], [], "obj", 5, git_source_identities=[base])
        h2 = batch_hash_from_proposal(["e1"], ["hash1"], [], "obj", 5, git_source_identities=[alt])
        assert h1 != h2

    def test_full_sha256_bound_not_only_truncated(self):
        """
        §9 — deux candidats partageant le MÊME source_hash tronqué
        (compatibilité) mais un SHA256 complet différent ne doivent
        JAMAIS produire une autorité Git indistinguable.
        """
        base = self._base_identity()
        base["source_content_sha256"] = "aaaa000000000000" + "0" * 48  # X
        alt = dict(base)
        alt["source_content_sha256"] = "aaaa000000000000" + "1" * 48  # Y (même préfixe 16, fin différente)

        same_truncated = ["aaaa000000000000"]
        h1 = batch_hash_from_proposal(
            ["e1"], same_truncated, [], "obj", 5, git_source_identities=[base],
        )
        h2 = batch_hash_from_proposal(
            ["e1"], same_truncated, [], "obj", 5, git_source_identities=[alt],
        )
        assert h1 != h2

    def test_same_source_different_target_batch_hash_differs(self):
        base = self._base_identity()
        alt_target = dict(base, target_path="dst/other.py")
        h1 = batch_hash_from_proposal(
            ["e1"], ["hash1"], [], "obj", 5,
            target_paths=["dst/module.py"], git_source_identities=[base],
        )
        h2 = batch_hash_from_proposal(
            ["e1"], ["hash1"], [], "obj", 5,
            target_paths=["dst/other.py"], git_source_identities=[alt_target],
        )
        assert h1 != h2


# ─── 2. Compatibilité ascendante — batch_hash_version=1 inchangé ────────────

class TestLegacyBatchHashCompatibility:
    def test_legacy_call_without_new_params_stays_version_1_and_reproducible(self):
        h1 = batch_hash_from_proposal(["e01"], ["abcd"], [], "obj", 5)
        h2 = batch_hash_from_proposal(["e01"], ["abcd"], [], "obj", 5)
        assert h1 == h2  # reproductible — même formule historique

    def test_legacy_and_v2_calls_with_identical_base_args_differ(self):
        """
        Ajouter des champs v2 (même vides) change la version et donc le
        hash — comportement attendu, ne casse jamais une proposition déjà
        stockée (jamais recalculée pour comparaison ailleurs dans le code).
        """
        h_legacy = batch_hash_from_proposal(["e01"], ["abcd"], [], "obj", 5)
        h_v2_empty = batch_hash_from_proposal(
            ["e01"], ["abcd"], [], "obj", 5, target_paths=[], git_source_identities=[],
        )
        assert h_legacy != h_v2_empty

    def test_stored_legacy_proposal_round_trips_unchanged(self, tmp_path):
        """
        Une proposition déjà persistée garde son batch_hash tel quel —
        jamais recalculé pour comparaison (aucune fonction du code de
        production ne recalcule batch_hash pour le comparer à un objet
        stocké ; seule une comparaison valeur-stockée == valeur-stockée
        existe, ex. liaison approval/enveloppe).
        """
        selector_dir = tmp_path / "selector"
        legacy_hash = batch_hash_from_proposal(["e01"], ["abcd"], [], "obj", 5)
        proposal = {
            "batch_id": "legacy-batch-1",
            "batch_hash": legacy_hash,
            "selected_entries": [],
            "candidate_scope_mode": "GLOBAL",
        }
        _save_batch(proposal, selector_dir)
        loaded = _load_batch("legacy-batch-1", selector_dir)
        assert loaded["batch_hash"] == legacy_hash


# ─── 3. verify_batch_integrity — dérive détectée pour chaque champ Git ──────

class TestVerifyBatchIntegrityGitDrift:
    def _propose_real(self, synthetic_repo, tmp_path, target_path="dst/module.py"):
        ledger_dir = tmp_path / "ledger"
        selector_dir = tmp_path / "selector"
        reg = _register(synthetic_repo, ledger_dir, target_path=target_path)
        assert reg["status"] == "DISCOVERED"
        proposal = _propose(ledger_dir, selector_dir, reg["ledger_entry_id"])
        assert proposal["status"] in ("BATCH_PROPOSED", "PROPOSED")
        return ledger_dir, selector_dir, proposal

    def test_baseline_verifies_true(self, synthetic_repo, tmp_path):
        ledger_dir, _sel, proposal = self._propose_real(synthetic_repo, tmp_path)
        ok, reason = verify_batch_integrity(proposal, ledger_dir)
        assert ok is True
        assert reason is None

    def test_tampered_target_path_rejected(self, synthetic_repo, tmp_path):
        ledger_dir, _sel, proposal = self._propose_real(synthetic_repo, tmp_path)
        proposal["selected_entries"][0]["target_path"] = "dst/tampered.py"
        ok, reason = verify_batch_integrity(proposal, ledger_dir)
        assert ok is False
        assert reason.startswith("TARGET_PATH_DRIFT")

    def test_tampered_commit_sha_rejected(self, synthetic_repo, tmp_path):
        ledger_dir, _sel, proposal = self._propose_real(synthetic_repo, tmp_path)
        proposal["selected_entries"][0]["source_git_commit_sha"] = "0" * 40
        ok, reason = verify_batch_integrity(proposal, ledger_dir)
        assert ok is False
        assert reason.startswith("GIT_SOURCE_COMMIT_DRIFT")

    def test_tampered_blob_sha_rejected(self, synthetic_repo, tmp_path):
        ledger_dir, _sel, proposal = self._propose_real(synthetic_repo, tmp_path)
        proposal["selected_entries"][0]["source_git_blob_sha"] = "0" * 40
        ok, reason = verify_batch_integrity(proposal, ledger_dir)
        assert ok is False
        assert reason.startswith("GIT_SOURCE_BLOB_SHA_DRIFT")

    def test_tampered_historical_path_rejected(self, synthetic_repo, tmp_path):
        ledger_dir, _sel, proposal = self._propose_real(synthetic_repo, tmp_path)
        proposal["selected_entries"][0]["source_git_historical_path"] = "src/other.py"
        ok, reason = verify_batch_integrity(proposal, ledger_dir)
        assert ok is False
        assert reason.startswith("GIT_SOURCE_HISTORICAL_PATH_DRIFT")

    def test_tampered_full_sha256_rejected(self, synthetic_repo, tmp_path):
        ledger_dir, _sel, proposal = self._propose_real(synthetic_repo, tmp_path)
        proposal["selected_entries"][0]["source_content_sha256"] = "0" * 64
        ok, reason = verify_batch_integrity(proposal, ledger_dir)
        assert ok is False
        assert reason.startswith("GIT_SOURCE_FULL_SHA256_DRIFT")

    def test_tampered_repository_identity_rejected(self, synthetic_repo, tmp_path):
        ledger_dir, _sel, proposal = self._propose_real(synthetic_repo, tmp_path)
        proposal["selected_entries"][0]["source_repository_identity"] = "/somewhere/else"
        ok, reason = verify_batch_integrity(proposal, ledger_dir)
        assert ok is False
        assert reason.startswith("GIT_SOURCE_REPOSITORY_IDENTITY_DRIFT")

    def test_tampered_operation_intent_rejected(self, synthetic_repo, tmp_path):
        ledger_dir = tmp_path / "ledger"
        selector_dir = tmp_path / "selector"
        reg = _register(synthetic_repo, ledger_dir, target_path="dst/module.py")
        # Injecte une operation_type via provenance_refs directement dans
        # l'entrée Ledger (lecture réelle, pas de fabrication de decision).
        entries = L._load_entries(ledger_dir)
        assert len(entries) == 1
        entries[0]["provenance_refs"] = {"operation_type": "UPDATE_TARGET_FROM_SOURCE"}
        entries_path = ledger_dir / "entries.jsonl"
        import json as _json
        entries_path.write_text(
            "\n".join(_json.dumps(e, ensure_ascii=False) for e in entries) + "\n",
            encoding="utf-8",
        )
        proposal = _propose(ledger_dir, selector_dir, reg["ledger_entry_id"])
        assert proposal["selected_entries"][0]["provenance_refs"]["operation_type"] == "UPDATE_TARGET_FROM_SOURCE"

        proposal["selected_entries"][0]["provenance_refs"]["operation_type"] = "REPLACE_TARGET"
        ok, reason = verify_batch_integrity(proposal, ledger_dir)
        assert ok is False
        assert reason.startswith("OPERATION_INTENT_DRIFT")


# ─── 4. Non-régression filesystem ────────────────────────────────────────────

class TestFilesystemNonRegression:
    def test_filesystem_proposal_verifies_without_git_checks(self, tmp_path):
        ledger_dir = tmp_path / "ledger"
        selector_dir = tmp_path / "selector"
        src = tmp_path / "plain.py"
        src.write_bytes(b"PLAIN\n")
        reg = L.register_source(str(src), target_path="dst/plain.py", ledger_dir=ledger_dir)
        assert reg["status"] == "DISCOVERED"
        proposal = _propose(ledger_dir, selector_dir, reg["ledger_entry_id"])
        ok, reason = verify_batch_integrity(proposal, ledger_dir)
        assert ok is True
        assert reason is None
        assert proposal["selected_entries"][0]["source_kind"] == "FILESYSTEM_FILE"

    def test_filesystem_batch_hash_still_computed(self, tmp_path):
        ledger_dir = tmp_path / "ledger"
        selector_dir = tmp_path / "selector"
        src = tmp_path / "plain2.py"
        src.write_bytes(b"PLAIN2\n")
        reg = L.register_source(str(src), target_path="dst/plain2.py", ledger_dir=ledger_dir)
        proposal = _propose(ledger_dir, selector_dir, reg["ledger_entry_id"])
        assert proposal["batch_hash"] is not None


# ─── 5. Forme ACD-01 — chemin historique == chemin cible, octets différents ──

class TestACD01Shape:
    def test_same_path_string_different_bytes_is_meaningful_delta(self, synthetic_repo, tmp_path):
        target = tmp_path / "target_repo" / "scripts" / "check_forbidden_content.py"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"CURRENT_HEAD_VERSION\n")

        c1 = _git(synthetic_repo, "rev-parse", "candidate")
        blob = _git(synthetic_repo, "ls-tree", c1, "--", "src/module.py").split()[2]
        import hashlib
        historical_content = b"CONTENT_A\n"
        historical_hash16 = hashlib.sha256(historical_content).hexdigest()[:16]

        status, detail = assess_materiality(
            "scripts/check_forbidden_content.py",  # historical_path == target
            "scripts/check_forbidden_content.py",
            historical_hash16,
            repo_root=target.parent.parent,
            source_kind="GIT_BLOB",
        )
        assert status == MEANINGFUL_DELTA
        assert detail["reason"] == "target_content_differs"

    def test_acd01_shape_registration_entry_and_batch_include_target(
        self, synthetic_repo, tmp_path,
    ):
        """
        Enregistrement synthétique reproduisant la FORME d'ACD-01 (chemin
        historique == chemin cible en tant que chaîne) : l'entrée Ledger
        et le batch_hash lient malgré tout explicitement la cible — pas
        de raccourci d'identité basé sur l'égalité de chaîne de chemin.
        """
        ledger_dir = tmp_path / "ledger"
        selector_dir = tmp_path / "selector"

        # Chemin historique et cible partagent la même chaîne, comme pour
        # scripts/check_forbidden_content.py dans le vrai cas ACD-01.
        reg = L.register_git_blob_source(
            "candidate", "src/module.py",
            target_path="src/module.py",
            repo_root=synthetic_repo, ledger_dir=ledger_dir,
        )
        assert reg["status"] == "DISCOVERED"
        entries = L._load_entries(ledger_dir)
        assert entries[0]["target_path"] == entries[0]["source_git_historical_path"]

        proposal = _propose(ledger_dir, selector_dir, reg["ledger_entry_id"])
        assert proposal["batch_hash"] is not None
        selected = proposal["selected_entries"][0]
        assert selected["target_path"] == "src/module.py"
        assert selected["source_git_historical_path"] == "src/module.py"

        # Enregistrer la MÊME source vers une cible DIFFÉRENTE (toujours
        # forme ACD-01-like en amont) doit rester distinguable.
        reg2 = L.register_git_blob_source(
            "candidate", "src/module.py",
            target_path="dst/elsewhere.py",
            repo_root=synthetic_repo, ledger_dir=ledger_dir,
        )
        assert reg2["status"] == "DISCOVERED"
        assert reg2["ledger_entry_id"] != reg["ledger_entry_id"]
