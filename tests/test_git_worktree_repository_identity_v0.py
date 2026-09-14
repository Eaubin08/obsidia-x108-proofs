"""
tests/test_git_worktree_repository_identity_v0.py
===============================================
Suite CLOSE_ACD02_GIT_WORKTREE_SOURCE_REPOSITORY_IDENTITY_GAP_V0.

Prouve que la résolution de source GIT_BLOB distingue correctement :

  MÊME dépôt Git, worktree lié différent  -> autorisé (si tous les
                                              autres faits exacts matchent)
  dépôt INDÉPENDANT (clone séparé)        -> refusé, même à contenu
                                              byte-identique (commit/blob/
                                              SHA256 identiques)

L'identité de dépôt (GIT_COMMON_REPOSITORY_IDENTITY_V0) est DÉRIVÉE de
`git rev-parse --git-common-dir` — jamais assertée par l'appelant,
jamais déduite du seul contenu (commit/blob/SHA/remote URL).

Tout synthétique (tmp_path, dépôts/worktrees/clones Git temporaires
réels) — jamais le vrai ACD-01/ACD-02 réel.
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

import obsidia_content_apply as C  # noqa: E402


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    assert result.returncode == 0, f"git {args} failed: {result.stderr}"
    return result.stdout.strip()


@pytest.fixture
def main_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "main_repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    (repo / "src").mkdir()
    (repo / "src" / "module.py").write_bytes(b"SOURCE_CONTENT_V0\n")
    _git(repo, "add", "src/module.py")
    _git(repo, "commit", "-q", "-m", "C1")
    return repo


def _source_child(main_repo: Path, commit_sha: str) -> dict:
    blob_sha = _git(main_repo, "rev-parse", f"{commit_sha}:src/module.py")
    content_sha256 = __import__("hashlib").sha256(b"SOURCE_CONTENT_V0\n").hexdigest()
    return {
        "source_kind": "GIT_BLOB",
        "source_repository_identity": str(main_repo.resolve()),
        "source_git_commit_sha": commit_sha,
        "source_git_historical_path": "src/module.py",
        "source_git_blob_sha": blob_sha,
        "source_content_sha256": content_sha256,
    }


# ─── 1. Faits d'identité de dépôt (git-common-dir) ──────────────────────────

class TestGitRepositoryIdentityFacts:
    def test_linked_worktree_shares_common_dir(self, main_repo, tmp_path):
        worktree = tmp_path / "linked_worktree"
        _git(main_repo, "worktree", "add", str(worktree), "-b", "linked-branch", "HEAD")
        assert main_repo.resolve() != worktree.resolve()
        assert C.same_git_repository(main_repo, worktree) is True

    def test_independent_clone_has_different_common_dir(self, main_repo, tmp_path):
        clone = tmp_path / "independent_clone"
        subprocess.run(["git", "clone", "-q", str(main_repo), str(clone)], check=True, capture_output=True)
        assert C.same_git_repository(main_repo, clone) is False

    def test_non_git_path_derives_none(self, tmp_path):
        not_a_repo = tmp_path / "not_a_repo"
        not_a_repo.mkdir()
        assert C.derive_git_repository_identity(not_a_repo) is None

    def test_nonexistent_path_derives_none(self, tmp_path):
        nowhere = tmp_path / "does_not_exist_at_all"
        assert C.derive_git_repository_identity(nowhere) is None

    def test_same_git_repository_false_if_either_side_not_git(self, main_repo, tmp_path):
        not_a_repo = tmp_path / "not_a_repo"
        not_a_repo.mkdir()
        assert C.same_git_repository(main_repo, not_a_repo) is False
        assert C.same_git_repository(not_a_repo, main_repo) is False


# ─── 2. Résolution positive via worktree lié ────────────────────────────────

class TestLinkedWorktreePositiveResolution:
    def test_resolve_source_bytes_succeeds_from_linked_worktree(self, main_repo, tmp_path):
        commit_sha = _git(main_repo, "rev-parse", "HEAD")
        worktree = tmp_path / "linked_worktree"
        _git(main_repo, "worktree", "add", str(worktree), "-b", "linked-branch-2", commit_sha)

        child = _source_child(main_repo, commit_sha)
        data, reason = C.resolve_source_bytes(child, worktree)
        assert reason is None
        assert data == b"SOURCE_CONTENT_V0\n"

    def test_resolve_source_bytes_exact_path_match_still_fast_path(self, main_repo):
        commit_sha = _git(main_repo, "rev-parse", "HEAD")
        child = _source_child(main_repo, commit_sha)
        data, reason = C.resolve_source_bytes(child, main_repo)
        assert reason is None
        assert data == b"SOURCE_CONTENT_V0\n"


# ─── 3. Rejet négatif : clone indépendant, même contenu ─────────────────────

class TestIndependentCloneNegativeResolution:
    def test_independent_clone_rejected_despite_identical_commit_blob_sha(self, main_repo, tmp_path):
        commit_sha = _git(main_repo, "rev-parse", "HEAD")
        clone = tmp_path / "independent_clone"
        subprocess.run(["git", "clone", "-q", str(main_repo), str(clone)], check=True, capture_output=True)

        # Verifie prealablement que le clone a bien EXACTEMENT le meme
        # commit/blob/contenu — le rejet ne doit PAS venir d'une divergence
        # de contenu, uniquement de l'identite de depot.
        clone_commit = _git(clone, "rev-parse", "HEAD")
        assert clone_commit == commit_sha

        child = _source_child(main_repo, commit_sha)
        data, reason = C.resolve_source_bytes(child, clone)
        assert data is None
        assert reason == "SOURCE_REPOSITORY_IDENTITY_MISMATCH"

    def test_clone_with_same_content_imported_as_new_commit_still_rejected(self, main_repo, tmp_path):
        commit_sha = _git(main_repo, "rev-parse", "HEAD")
        clone = tmp_path / "clone_new_commit"
        subprocess.run(["git", "clone", "-q", str(main_repo), str(clone)], check=True, capture_output=True)
        # Reecrit le meme contenu dans un NOUVEAU commit du clone (meme blob sha possible).
        (clone / "src" / "module.py").write_bytes(b"SOURCE_CONTENT_V0\n")
        _git(clone, "commit", "-q", "--allow-empty", "-m", "reimport")

        child = _source_child(main_repo, commit_sha)
        data, reason = C.resolve_source_bytes(child, clone)
        assert data is None
        assert reason == "SOURCE_REPOSITORY_IDENTITY_MISMATCH"


# ─── 4. Cas de rejet supplementaires (fermeture par defaut) ─────────────────

class TestAdditionalFailClosedCases:
    def test_malformed_stored_repository_path_rejected(self, main_repo, tmp_path):
        commit_sha = _git(main_repo, "rev-parse", "HEAD")
        worktree = tmp_path / "linked_worktree"
        _git(main_repo, "worktree", "add", str(worktree), "-b", "linked-branch-3", commit_sha)

        child = _source_child(main_repo, commit_sha)
        child["source_repository_identity"] = str(tmp_path / "never_existed_repo_path")
        data, reason = C.resolve_source_bytes(child, worktree)
        assert data is None
        assert reason == "SOURCE_REPOSITORY_IDENTITY_MISMATCH"

    def test_non_git_repo_root_rejected(self, main_repo, tmp_path):
        commit_sha = _git(main_repo, "rev-parse", "HEAD")
        not_a_repo = tmp_path / "plain_dir"
        not_a_repo.mkdir()
        child = _source_child(main_repo, commit_sha)
        data, reason = C.resolve_source_bytes(child, not_a_repo)
        assert data is None
        assert reason == "SOURCE_REPOSITORY_IDENTITY_MISMATCH"

    def test_wrong_blob_sha_rejected_even_within_same_repository(self, main_repo, tmp_path):
        commit_sha = _git(main_repo, "rev-parse", "HEAD")
        worktree = tmp_path / "linked_worktree"
        _git(main_repo, "worktree", "add", str(worktree), "-b", "linked-branch-4", commit_sha)
        child = _source_child(main_repo, commit_sha)
        child["source_git_blob_sha"] = "0" * 40
        data, reason = C.resolve_source_bytes(child, worktree)
        assert data is None
        assert reason == "GIT_SOURCE_BLOB_SHA_MISMATCH"

    def test_wrong_full_sha256_rejected_even_within_same_repository(self, main_repo, tmp_path):
        commit_sha = _git(main_repo, "rev-parse", "HEAD")
        worktree = tmp_path / "linked_worktree"
        _git(main_repo, "worktree", "add", str(worktree), "-b", "linked-branch-5", commit_sha)
        child = _source_child(main_repo, commit_sha)
        child["source_content_sha256"] = "1" * 64
        data, reason = C.resolve_source_bytes(child, worktree)
        assert data is None
        assert reason == "GIT_SOURCE_FULL_SHA256_MISMATCH"

    def test_wrong_historical_source_path_rejected(self, main_repo, tmp_path):
        commit_sha = _git(main_repo, "rev-parse", "HEAD")
        worktree = tmp_path / "linked_worktree"
        _git(main_repo, "worktree", "add", str(worktree), "-b", "linked-branch-6", commit_sha)
        child = _source_child(main_repo, commit_sha)
        child["source_git_historical_path"] = "src/does_not_exist.py"
        data, reason = C.resolve_source_bytes(child, worktree)
        assert data is None
        assert reason in ("GIT_SOURCE_BLOB_SHA_MISMATCH", "GIT_SOURCE_BLOB_UNREADABLE")
