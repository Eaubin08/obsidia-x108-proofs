"""
tests/test_git_blob_source_registration_v0.py
===============================================
Suite GIT_BLOB_SOURCE_REGISTRATION_V0.

Un blob Git est un matériau source réel et immuable. Ces tests prouvent
que le Ledger peut l'enregistrer honnêtement — sans jamais checkout,
sans jamais matérialiser le blob dans le dépôt réel, et sans jamais
laisser une branche/ref mutable devenir l'autorité de la source
enregistrée.

Toute la suite opère sur un dépôt Git SYNTHÉTIQUE, temporaire, isolé
(tmp_path) — jamais sur le vrai dépôt.

Couvre :
  A. Enregistrement d'un blob valide (commit exact, blob, SHA256)
  B. Résolution de ref/branche → commit immuable
  C. Ref mutable ne peut jamais muter une source déjà enregistrée
  D. Rejets fail-closed (commit inconnu, chemin absent, tree, mismatch)
  E. Validation de chemin historique (traversal, absolu, wildcard, protégé)
  F. Compatibilité Selector (pas d'exigence d'existence filesystem)
  G. Intégrité d'exécution (Gate 6 source-kind-aware)
  H. Matérialité (source_path == target_path n'implique plus no-op pour GIT_BLOB)
  I. Dédup / identité d'entrée vs identité de contenu
  J. Non-régression filesystem (comportement inchangé)
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
from obsidia_batch_execution import (  # noqa: E402
    assess_materiality,
    resolve_source_bytes_hash,
    MEANINGFUL_DELTA,
    NO_MEANINGFUL_DELTA,
)
from obsidia_batch_selector import (  # noqa: E402
    build_candidates_from_ledger,
    _check_eligibility,
)


# ─── Fixture : dépôt Git synthétique isolé ───────────────────────────────────

def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=str(repo), capture_output=True, text=True,
    )
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
    c1_sha = _git(repo, "rev-parse", "HEAD")

    (src / "module.py").write_bytes(b"CONTENT_B\n")
    _git(repo, "add", "src/module.py")
    _git(repo, "commit", "-q", "-m", "C2: content B")
    c2_sha = _git(repo, "rev-parse", "HEAD")

    _git(repo, "branch", "candidate", c1_sha)

    return repo


def _c1(repo: Path) -> str:
    return _git(repo, "rev-parse", "candidate")  # branch initially at C1


def _resolve_commit(repo: Path, ref: str) -> str:
    return _git(repo, "rev-parse", ref)


def _blob_sha(repo: Path, commit: str, path: str) -> str:
    line = _git(repo, "ls-tree", commit, "--", path)
    return line.split()[2]


# ─── A. Enregistrement valide ───────────────────────────────────────────────

class TestValidRegistration:
    def test_register_valid_blob(self, synthetic_repo, tmp_path):
        ledger_dir = tmp_path / "ledger"
        c1 = _resolve_commit(synthetic_repo, "candidate")
        blob = _blob_sha(synthetic_repo, c1, "src/module.py")

        result = L.register_git_blob_source(
            "candidate", "src/module.py",
            target_path="dst/module.py",
            repo_root=synthetic_repo, ledger_dir=ledger_dir,
        )
        assert result["status"] == "DISCOVERED"
        assert result["source_git_commit_sha"] == c1
        assert result["source_git_blob_sha"] == blob

        entries = L._load_entries(ledger_dir)
        assert len(entries) == 1
        e = entries[0]
        assert e["source_kind"] == "GIT_BLOB"
        assert e["source_git_commit_sha"] == c1
        assert e["source_git_blob_sha"] == blob
        assert e["source_git_historical_path"] == "src/module.py"
        assert e["source_git_ref_hint"] == "candidate"
        assert e["lifecycle_status"] == "DISCOVERED"
        assert e["kx108_decision"] is None
        assert e["proposal_id"] is None
        assert e["commit_sha"] is None  # commit d'application, jamais fabriqué

    def test_content_sha256_matches_real_bytes(self, synthetic_repo, tmp_path):
        import hashlib
        ledger_dir = tmp_path / "ledger"
        result = L.register_git_blob_source(
            "candidate", "src/module.py",
            repo_root=synthetic_repo, ledger_dir=ledger_dir,
        )
        expected = hashlib.sha256(b"CONTENT_A\n").hexdigest()
        assert result["source_content_sha256"] == expected

    def test_expected_hashes_accepted_as_precondition(self, synthetic_repo, tmp_path):
        c1 = _resolve_commit(synthetic_repo, "candidate")
        blob = _blob_sha(synthetic_repo, c1, "src/module.py")
        import hashlib
        content_sha256 = hashlib.sha256(b"CONTENT_A\n").hexdigest()

        result = L.register_git_blob_source(
            "candidate", "src/module.py",
            expected_blob_sha=blob,
            expected_content_sha256=content_sha256,
            repo_root=synthetic_repo, ledger_dir=Path(str(synthetic_repo) + "_ledger"),
        )
        assert result["status"] == "DISCOVERED"


# ─── B. Résolution ref → commit immuable ─────────────────────────────────────

class TestRefResolution:
    def test_branch_ref_resolves_to_exact_commit(self, synthetic_repo, tmp_path):
        c1 = _resolve_commit(synthetic_repo, "candidate")
        result = L.register_git_blob_source(
            "candidate", "src/module.py",
            repo_root=synthetic_repo, ledger_dir=tmp_path / "ledger",
        )
        assert result["source_git_commit_sha"] == c1
        assert result["source_git_commit_sha"] != "candidate"

    def test_full_commit_sha_accepted_directly(self, synthetic_repo, tmp_path):
        c2 = _resolve_commit(synthetic_repo, "main") if _git(synthetic_repo, "branch", "--list", "main") else _resolve_commit(synthetic_repo, "HEAD")
        result = L.register_git_blob_source(
            c2, "src/module.py",
            repo_root=synthetic_repo, ledger_dir=tmp_path / "ledger",
        )
        assert result["status"] == "DISCOVERED"
        assert result["source_git_commit_sha"] == c2


# ─── C. Ref mutable ne peut jamais muter une source enregistrée ─────────────

class TestMovingRefCannotMutate:
    def test_moving_ref_cannot_mutate_registered_source(self, synthetic_repo, tmp_path):
        ledger_dir = tmp_path / "ledger"
        c1 = _resolve_commit(synthetic_repo, "candidate")

        result = L.register_git_blob_source(
            "candidate", "src/module.py",
            target_path="dst/module.py",
            repo_root=synthetic_repo, ledger_dir=ledger_dir,
        )
        assert result["status"] == "DISCOVERED"
        entry_id = result["ledger_entry_id"]

        entries = {e["ledger_entry_id"]: e for e in L._load_entries(ledger_dir)}
        registered_commit = entries[entry_id]["source_git_commit_sha"]
        registered_blob = entries[entry_id]["source_git_blob_sha"]
        assert registered_commit == c1

        # La branche "candidate" avance maintenant vers C2.
        c2 = _resolve_commit(synthetic_repo, "main") if False else _git(synthetic_repo, "rev-parse", "HEAD")
        _git(synthetic_repo, "branch", "-f", "candidate", c2)
        assert _resolve_commit(synthetic_repo, "candidate") == c2
        assert c2 != c1

        # L'entrée déjà enregistrée reste liée à C1, jamais réécrite.
        entries_after = {e["ledger_entry_id"]: e for e in L._load_entries(ledger_dir)}
        assert entries_after[entry_id]["source_git_commit_sha"] == c1
        assert entries_after[entry_id]["source_git_commit_sha"] != c2

        # L'intégrité d'exécution relit C1, jamais la pointe courante de "candidate".
        child = {
            "source_kind": "GIT_BLOB",
            "source_git_commit_sha": registered_commit,
            "source_git_historical_path": "src/module.py",
            "source_git_blob_sha": registered_blob,
        }
        rehash = resolve_source_bytes_hash(child, synthetic_repo)
        assert rehash == entries_after[entry_id]["source_hash"]


# ─── D. Rejets fail-closed ────────────────────────────────────────────────────

class TestFailClosedRejections:
    def test_unknown_commit_rejected(self, synthetic_repo, tmp_path):
        result = L.register_git_blob_source(
            "0" * 40, "src/module.py",
            repo_root=synthetic_repo, ledger_dir=tmp_path / "ledger",
        )
        assert result["status"] == "REJECTED"
        assert result["reason"] == "GIT_SOURCE_UNKNOWN_COMMIT"

    def test_missing_path_at_commit_rejected(self, synthetic_repo, tmp_path):
        result = L.register_git_blob_source(
            "candidate", "src/does_not_exist.py",
            repo_root=synthetic_repo, ledger_dir=tmp_path / "ledger",
        )
        assert result["status"] == "REJECTED"
        assert result["reason"] == "GIT_SOURCE_PATH_NOT_FOUND_AT_COMMIT"

    def test_tree_object_rejected_not_blob(self, synthetic_repo, tmp_path):
        result = L.register_git_blob_source(
            "candidate", "src",
            repo_root=synthetic_repo, ledger_dir=tmp_path / "ledger",
        )
        assert result["status"] == "REJECTED"
        assert result["reason"] == "GIT_SOURCE_PATH_NOT_FOUND_AT_COMMIT"

    def test_expected_blob_sha_mismatch_rejected(self, synthetic_repo, tmp_path):
        result = L.register_git_blob_source(
            "candidate", "src/module.py",
            expected_blob_sha="f" * 40,
            repo_root=synthetic_repo, ledger_dir=tmp_path / "ledger",
        )
        assert result["status"] == "REJECTED"
        assert result["reason"] == "GIT_SOURCE_BLOB_SHA_MISMATCH"

    def test_expected_content_sha256_mismatch_rejected(self, synthetic_repo, tmp_path):
        result = L.register_git_blob_source(
            "candidate", "src/module.py",
            expected_content_sha256="0" * 64,
            repo_root=synthetic_repo, ledger_dir=tmp_path / "ledger",
        )
        assert result["status"] == "REJECTED"
        assert result["reason"] == "GIT_SOURCE_CONTENT_SHA256_MISMATCH"

    def test_empty_commit_ref_rejected(self, synthetic_repo, tmp_path):
        result = L.register_git_blob_source(
            "", "src/module.py",
            repo_root=synthetic_repo, ledger_dir=tmp_path / "ledger",
        )
        assert result["status"] == "REJECTED"
        assert result["reason"] == "GIT_SOURCE_EMPTY_COMMIT_REF"


# ─── E. Validation du chemin historique ──────────────────────────────────────

class TestHistoricalPathValidation:
    def test_empty_path_rejected(self, synthetic_repo, tmp_path):
        result = L.register_git_blob_source(
            "candidate", "", repo_root=synthetic_repo, ledger_dir=tmp_path / "ledger",
        )
        assert result["status"] == "REJECTED"
        assert result["reason"] == "GIT_SOURCE_EMPTY_PATH"

    def test_wildcard_path_rejected(self, synthetic_repo, tmp_path):
        result = L.register_git_blob_source(
            "candidate", "src/*.py", repo_root=synthetic_repo, ledger_dir=tmp_path / "ledger",
        )
        assert result["status"] == "REJECTED"
        assert result["reason"] == "GIT_SOURCE_WILDCARD_REJECTED"

    def test_absolute_path_rejected(self, synthetic_repo, tmp_path):
        result = L.register_git_blob_source(
            "candidate", "/etc/passwd", repo_root=synthetic_repo, ledger_dir=tmp_path / "ledger",
        )
        assert result["status"] == "REJECTED"
        assert result["reason"] == "GIT_SOURCE_ABSOLUTE_PATH_REJECTED"

    def test_traversal_outside_repo_rejected(self, synthetic_repo, tmp_path):
        result = L.register_git_blob_source(
            "candidate", "../../../../etc/passwd",
            repo_root=synthetic_repo, ledger_dir=tmp_path / "ledger",
        )
        assert result["status"] == "REJECTED"
        assert result["reason"] in ("GIT_SOURCE_OUTSIDE_REPO_NAMESPACE", "GIT_SOURCE_PATH_NOT_FOUND_AT_COMMIT")

    def test_historical_path_absent_at_head_but_present_at_commit_succeeds(self, synthetic_repo, tmp_path):
        # src/module.py existe à "candidate" (C1) — n'a pas besoin d'exister
        # dans l'arbre de travail courant du process appelant.
        result = L.register_git_blob_source(
            "candidate", "src/module.py",
            repo_root=synthetic_repo, ledger_dir=tmp_path / "ledger",
        )
        assert result["status"] == "DISCOVERED"

    def test_protected_target_rejected(self, synthetic_repo, tmp_path):
        result = L.register_git_blob_source(
            "candidate", "src/module.py",
            target_path="proofs/x.py",
            repo_root=synthetic_repo, ledger_dir=tmp_path / "ledger",
        )
        assert result["status"] == "REJECTED_PROTECTED"


# ─── F. Compatibilité Selector ────────────────────────────────────────────────

class TestSelectorCompatibility:
    def test_git_blob_entry_selectable_without_filesystem_existence(self, synthetic_repo, tmp_path):
        ledger_dir = tmp_path / "ledger"
        result = L.register_git_blob_source(
            "candidate", "src/module.py",
            target_path="dst/module_selector_test.py",
            repo_root=synthetic_repo, ledger_dir=ledger_dir,
        )
        entries = L._load_entries(ledger_dir)
        entry = next(e for e in entries if e["ledger_entry_id"] == result["ledger_entry_id"])

        status, reasons = _check_eligibility(entry)
        # DISCOVERED avec source_hash + target_path connus → ELIGIBLE malgré
        # kx108_decision absent (stage-aware, NOT_YET_APPLICABLE) — surtout
        # AUCUNE exigence d'existence filesystem de source_path.
        assert status == "ELIGIBLE"
        assert "source_hash_missing" not in reasons
        assert "target_path_unknown" not in reasons

        candidates = build_candidates_from_ledger(ledger_dir, [entry])
        cand = next(c for c in candidates if c["ledger_entry_id"] == entry["ledger_entry_id"])
        assert cand["source_kind"] == "GIT_BLOB"
        assert cand["source_git_commit_sha"] == entry["source_git_commit_sha"]


# ─── G. Intégrité d'exécution (Gate 6 source-kind-aware) ─────────────────────

class TestExecutionSourceIntegrity:
    def test_git_blob_integrity_reads_immutable_commit_not_filesystem(self, synthetic_repo, tmp_path):
        c1 = _resolve_commit(synthetic_repo, "candidate")
        blob = _blob_sha(synthetic_repo, c1, "src/module.py")

        child = {
            "source_kind": "GIT_BLOB",
            "source_git_commit_sha": c1,
            "source_git_historical_path": "src/module.py",
            "source_git_blob_sha": blob,
        }
        rehash = resolve_source_bytes_hash(child, synthetic_repo)
        import hashlib
        assert rehash == hashlib.sha256(b"CONTENT_A\n").hexdigest()[:16]

    def test_filesystem_source_unchanged_behavior(self, tmp_path):
        f = tmp_path / "real.py"
        f.write_bytes(b"HELLO\n")
        child = {"source_kind": "FILESYSTEM_FILE", "source_path": "real.py"}
        rehash = resolve_source_bytes_hash(child, tmp_path)
        import hashlib
        assert rehash == hashlib.sha256(b"HELLO\n").hexdigest()[:16]

    def test_legacy_child_without_source_kind_treated_as_filesystem(self, tmp_path):
        f = tmp_path / "legacy.py"
        f.write_bytes(b"LEGACY\n")
        child = {"source_path": "legacy.py"}  # pas de source_kind — legacy
        rehash = resolve_source_bytes_hash(child, tmp_path)
        import hashlib
        assert rehash == hashlib.sha256(b"LEGACY\n").hexdigest()[:16]

    def test_git_blob_missing_commit_field_fails_closed(self, synthetic_repo):
        child = {"source_kind": "GIT_BLOB", "source_git_historical_path": "src/module.py"}
        assert resolve_source_bytes_hash(child, synthetic_repo) is None

    def test_git_blob_wrong_expected_blob_sha_fails_closed(self, synthetic_repo):
        c1 = _resolve_commit(synthetic_repo, "candidate")
        child = {
            "source_kind": "GIT_BLOB",
            "source_git_commit_sha": c1,
            "source_git_historical_path": "src/module.py",
            "source_git_blob_sha": "0" * 40,
        }
        assert resolve_source_bytes_hash(child, synthetic_repo) is None


# ─── H. Matérialité — source==target ne veut plus dire no-op pour GIT_BLOB ──

class TestMaterialityGitBlobPathEquality:
    def test_filesystem_source_equals_target_still_no_op(self):
        status, detail = assess_materiality(
            "same/path.py", "same/path.py", "abc123", source_kind="FILESYSTEM_FILE",
        )
        assert status == NO_MEANINGFUL_DELTA
        assert detail["reason"] == "source_equals_target_path"

    def test_git_blob_source_equals_target_path_string_but_content_differs(self, tmp_path):
        target = tmp_path / "scripts" / "check_forbidden_content.py"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"CURRENT_HEAD_CONTENT\n")
        import hashlib
        historical_hash = hashlib.sha256(b"HISTORICAL_CONTENT\n").hexdigest()[:16]

        status, detail = assess_materiality(
            "scripts/check_forbidden_content.py",
            "scripts/check_forbidden_content.py",
            historical_hash,
            repo_root=tmp_path,
            source_kind="GIT_BLOB",
        )
        # ACD-01 exact scenario : chemins identiques, contenu réellement
        # différent — DOIT être MEANINGFUL_DELTA, jamais un no-op déduit
        # d'une simple égalité de chaîne de chemin.
        assert status == MEANINGFUL_DELTA
        assert detail["reason"] == "target_content_differs"

    def test_git_blob_source_equals_target_path_string_and_content_identical(self, tmp_path):
        target = tmp_path / "same.py"
        target.write_bytes(b"SAME\n")
        import hashlib
        same_hash = hashlib.sha256(b"SAME\n").hexdigest()[:16]

        status, detail = assess_materiality(
            "same.py", "same.py", same_hash, repo_root=tmp_path, source_kind="GIT_BLOB",
        )
        assert status == NO_MEANINGFUL_DELTA
        assert detail["reason"] == "target_content_equals_source"


# ─── I. Dédup — identité d'entrée != identité de contenu ─────────────────────

class TestDedupSemantics:
    def test_same_commit_same_path_idempotent(self, synthetic_repo, tmp_path):
        ledger_dir = tmp_path / "ledger"
        r1 = L.register_git_blob_source(
            "candidate", "src/module.py", repo_root=synthetic_repo, ledger_dir=ledger_dir,
        )
        r2 = L.register_git_blob_source(
            "candidate", "src/module.py", repo_root=synthetic_repo, ledger_dir=ledger_dir,
        )
        assert r1["status"] == "DISCOVERED"
        assert r2["status"] == "ALREADY_REGISTERED"
        assert r2["ledger_entry_id"] == r1["ledger_entry_id"]

    def test_different_commit_same_path_distinct_entries(self, synthetic_repo, tmp_path):
        ledger_dir = tmp_path / "ledger"
        c2 = _git(synthetic_repo, "rev-parse", "HEAD")  # C2 (CONTENT_B)
        r1 = L.register_git_blob_source(
            "candidate", "src/module.py", repo_root=synthetic_repo, ledger_dir=ledger_dir,
        )
        r2 = L.register_git_blob_source(
            c2, "src/module.py", repo_root=synthetic_repo, ledger_dir=ledger_dir,
        )
        assert r1["status"] == "DISCOVERED"
        assert r2["status"] == "DISCOVERED"
        assert r1["ledger_entry_id"] != r2["ledger_entry_id"]
        entries = L._load_entries(ledger_dir)
        assert len(entries) == 2

    def test_filesystem_and_git_blob_same_bytes_stay_distinct_entries(self, synthetic_repo, tmp_path):
        ledger_dir = tmp_path / "ledger"
        fs_source = tmp_path / "fs_copy.py"
        fs_source.write_bytes(b"CONTENT_A\n")

        r_fs = L.register_source(str(fs_source), ledger_dir=ledger_dir)
        r_git = L.register_git_blob_source(
            "candidate", "src/module.py", repo_root=synthetic_repo, ledger_dir=ledger_dir,
        )
        assert r_fs["status"] == "DISCOVERED"
        assert r_git["status"] == "DISCOVERED"
        assert r_fs["ledger_entry_id"] != r_git["ledger_entry_id"]

        entries = {e["ledger_entry_id"]: e for e in L._load_entries(ledger_dir)}
        # Même contenu (CONTENT_A) mais chemins effectifs différents →
        # DISTINCT_CONTENT ou MOVED_SAME_CONTENT selon l'ordre, jamais fusionnées.
        assert entries[r_fs["ledger_entry_id"]]["source_hash"] == entries[r_git["ledger_entry_id"]]["source_hash"]
        assert len(entries) == 2


# ─── J. Non-régression filesystem ────────────────────────────────────────────

class TestFilesystemNonRegression:
    def test_register_source_unchanged(self, tmp_path):
        f = tmp_path / "plain.py"
        f.write_bytes(b"PLAIN\n")
        ledger_dir = tmp_path / "ledger"
        result = L.register_source(str(f), ledger_dir=ledger_dir)
        assert result["status"] == "DISCOVERED"
        entry = L._load_entries(ledger_dir)[0]
        assert "source_kind" not in entry  # legacy : champ absent, pas ajouté par erreur

    def test_legacy_entry_without_source_kind_defaults_filesystem_in_selector(self, tmp_path):
        f = tmp_path / "plain2.py"
        f.write_bytes(b"PLAIN2\n")
        ledger_dir = tmp_path / "ledger"
        result = L.register_source(str(f), target_path="dst/plain2.py", ledger_dir=ledger_dir)
        entry = L._load_entries(ledger_dir)[0]
        candidates = build_candidates_from_ledger(ledger_dir, [entry])
        cand = next(c for c in candidates if c["ledger_entry_id"] == result["ledger_entry_id"])
        assert cand["source_kind"] == "FILESYSTEM_FILE"

    def test_assess_materiality_default_kind_is_filesystem(self):
        status, detail = assess_materiality("x.py", "x.py", "abc")
        assert status == NO_MEANINGFUL_DELTA
        assert detail["reason"] == "source_equals_target_path"


# ─── K. Confinement du chemin cible (HARDEN_GIT_BLOB_SOURCE_BOUNDARIES_V0) ───

class TestTargetPathConfinement:
    def test_target_traversal_outside_repo_rejected(self, synthetic_repo, tmp_path):
        result = L.register_git_blob_source(
            "candidate", "src/module.py", target_path="../outside.py",
            repo_root=synthetic_repo, ledger_dir=tmp_path / "ledger",
        )
        assert result["status"] == "REJECTED"
        assert result["reason"] == "GIT_TARGET_OUTSIDE_REPO_NAMESPACE"

    def test_target_deep_traversal_outside_repo_rejected(self, synthetic_repo, tmp_path):
        result = L.register_git_blob_source(
            "candidate", "src/module.py", target_path="../../../../escape.py",
            repo_root=synthetic_repo, ledger_dir=tmp_path / "ledger",
        )
        assert result["status"] == "REJECTED"
        assert result["reason"] == "GIT_TARGET_OUTSIDE_REPO_NAMESPACE"

    def test_target_absolute_outside_repo_rejected(self, synthetic_repo, tmp_path):
        outside = tmp_path / "outside_dir" / "x.py"
        result = L.register_git_blob_source(
            "candidate", "src/module.py", target_path=str(outside),
            repo_root=synthetic_repo, ledger_dir=tmp_path / "ledger",
        )
        assert result["status"] == "REJECTED"
        assert result["reason"] == "GIT_TARGET_OUTSIDE_REPO_NAMESPACE"

    def test_target_traversal_into_protected_rejected(self, synthetic_repo, tmp_path):
        result = L.register_git_blob_source(
            "candidate", "src/module.py", target_path="periphery/../proofs/x.py",
            repo_root=synthetic_repo, ledger_dir=tmp_path / "ledger",
        )
        assert result["status"] == "REJECTED_PROTECTED"

    def test_target_dot_prefixed_protected_rejected(self, synthetic_repo, tmp_path):
        result = L.register_git_blob_source(
            "candidate", "src/module.py", target_path="./proofs/x.py",
            repo_root=synthetic_repo, ledger_dir=tmp_path / "ledger",
        )
        assert result["status"] == "REJECTED_PROTECTED"

    def test_target_real_active_file_accepted(self, synthetic_repo, tmp_path):
        result = L.register_git_blob_source(
            "candidate", "src/module.py", target_path="scripts/check_forbidden_content.py",
            repo_root=synthetic_repo, ledger_dir=tmp_path / "ledger",
        )
        assert result["status"] == "DISCOVERED"

    def test_target_with_spaces_accepted(self, synthetic_repo, tmp_path):
        result = L.register_git_blob_source(
            "candidate", "src/module.py", target_path="target dir/module with spaces.py",
            repo_root=synthetic_repo, ledger_dir=tmp_path / "ledger",
        )
        assert result["status"] == "DISCOVERED"
        entries = L._load_entries(tmp_path / "ledger")
        assert entries[0]["target_path"] == "target dir/module with spaces.py"

    def test_no_target_still_valid(self, synthetic_repo, tmp_path):
        result = L.register_git_blob_source(
            "candidate", "src/module.py",
            repo_root=synthetic_repo, ledger_dir=tmp_path / "ledger",
        )
        assert result["status"] == "DISCOVERED"

    def test_target_empty_string_rejected(self, synthetic_repo, tmp_path):
        result = L.register_git_blob_source(
            "candidate", "src/module.py", target_path="",
            repo_root=synthetic_repo, ledger_dir=tmp_path / "ledger",
        )
        assert result["status"] == "REJECTED"
        assert result["reason"] == "GIT_TARGET_EMPTY_PATH"


# ─── L. Bug d'autorité scindée sur historical_path (audit §4) ───────────────

class TestHistoricalPathNoSplitAuthority:
    def test_historical_path_namespace_checked_against_same_repo_as_plumbing(
        self, synthetic_repo, tmp_path,
    ):
        """
        historical_path pointant hors de synthetic_repo (mais théoriquement
        dans _REPO_ROOT réel) doit être rejeté comme hors-namespace — la
        validation de confinement utilise le MÊME repo_root que la lecture
        Git effective, jamais _REPO_ROOT implicitement.
        """
        # Un chemin qui remonterait hors de synthetic_repo entièrement.
        result = L.register_git_blob_source(
            "candidate", "../../../../../outside_of_synthetic_repo.py",
            repo_root=synthetic_repo, ledger_dir=tmp_path / "ledger",
        )
        assert result["status"] == "REJECTED"
        assert result["reason"] == "GIT_SOURCE_OUTSIDE_REPO_NAMESPACE"

    def test_historical_path_read_from_same_repo_root_used_for_validation(
        self, synthetic_repo, tmp_path,
    ):
        """Le blob effectivement lu correspond bien à repo_root — pas d'autre dépôt."""
        result = L.register_git_blob_source(
            "candidate", "src/module.py",
            repo_root=synthetic_repo, ledger_dir=tmp_path / "ledger",
        )
        assert result["status"] == "DISCOVERED"
        entries = L._load_entries(tmp_path / "ledger")
        assert entries[0]["source_repository_identity"] == str(synthetic_repo.resolve())


# ─── M. Identité de dépôt — fail-closed à la relecture d'exécution ──────────

class TestRepositoryIdentityBinding:
    def test_repository_mismatch_fails_closed(self, synthetic_repo, tmp_path):
        c1 = _resolve_commit(synthetic_repo, "candidate")
        blob = _blob_sha(synthetic_repo, c1, "src/module.py")

        # dépôt "autre" : une seconde copie synthétique distincte contenant
        # PAR COÏNCIDENCE un blob de même SHA (même octets, même arbre Git —
        # deux dépôts indépendants peuvent légitimement partager un blob_sha
        # identique pour un contenu identique).
        other_repo = tmp_path / "other_repo"
        other_repo.mkdir()
        _git(other_repo, "init", "-q")
        _git(other_repo, "config", "user.email", "test@example.com")
        _git(other_repo, "config", "user.name", "Test")
        (other_repo / "src").mkdir()
        (other_repo / "src" / "module.py").write_bytes(b"CONTENT_A\n")
        _git(other_repo, "add", "src/module.py")
        _git(other_repo, "commit", "-q", "-m", "same content, other repo")

        child = {
            "source_kind": "GIT_BLOB",
            "source_git_commit_sha": c1,
            "source_git_historical_path": "src/module.py",
            "source_git_blob_sha": blob,
            "source_repository_identity": str(synthetic_repo.resolve()),
        }

        # other_repo n'a jamais vu le commit c1 (object database distincte)
        # — même si son blob a, par coïncidence, les mêmes octets/SHA, la
        # relecture par commit échoue fermé (None), jamais un faux succès
        # basé sur une correspondance accidentelle de contenu.
        rehash_against_wrong_repo = resolve_source_bytes_hash(child, other_repo)
        assert rehash_against_wrong_repo is None

        # Le gate 5b explicite de run_execution (identité déclarée vs dépôt
        # réel d'exécution) est vérifié de bout en bout dans le test suivant.
        actual_repo = str(other_repo.resolve())
        expected_repo = child["source_repository_identity"]
        assert expected_repo != actual_repo  # préconditions du test

    def test_matching_repository_integrity_recheck_succeeds(self, synthetic_repo, tmp_path):
        c1 = _resolve_commit(synthetic_repo, "candidate")
        blob = _blob_sha(synthetic_repo, c1, "src/module.py")
        child = {
            "source_kind": "GIT_BLOB",
            "source_git_commit_sha": c1,
            "source_git_historical_path": "src/module.py",
            "source_git_blob_sha": blob,
            "source_repository_identity": str(synthetic_repo.resolve()),
        }
        rehash = resolve_source_bytes_hash(child, synthetic_repo)
        assert rehash is not None

    def test_run_execution_rejects_repository_mismatch_end_to_end(self, synthetic_repo, tmp_path):
        import obsidia_batch_execution as E

        c1 = _resolve_commit(synthetic_repo, "candidate")
        blob = _blob_sha(synthetic_repo, c1, "src/module.py")
        execution_dir = tmp_path / "exec"

        envelope = {
            "batch_execution_id": "test-repo-mismatch",
            "schema_version": E.SCHEMA_VERSION,
            "created_at": "now",
            "batch_id": "b1",
            "batch_hash": "h1",
            "candidate_scope_hash": "s1",
            "human_execution_approved": False,
            "decision_authority": E.DECISION_AUTHORITY,
            "execution_order": ["c1"],
            "dependency_edges": [],
            "children": [{
                "child_execution_id": "child1",
                "batch_execution_id": "test-repo-mismatch",
                "candidate_entry_id": "c1",
                "source_kind": "GIT_BLOB",
                "source_git_commit_sha": c1,
                "source_git_historical_path": "src/module.py",
                "source_git_blob_sha": blob,
                "source_repository_identity": str((tmp_path / "not_the_real_repo").resolve()),
                "source_hash": "irrelevant",
                "target_path": "dst/module.py",
                "target_pre_hash": None,
                "operation_type": "UPDATE_TARGET_FROM_SOURCE",
                "operation_reason": None,
                "materiality_status": E.MEANINGFUL_DELTA,
                "materiality_detail": {},
                "dependencies": [],
                "dependency_status": "NOT_APPLICABLE",
                "execution_position": 0,
                "session_id": None,
                "proposal_id": None,
                "kx108_decision": None,
                "execution_status": E.PLANNED,
                "decision_authority": E.DECISION_AUTHORITY,
            }],
            "aggregate_status": E.BATCH_PLANNED,
            "risk_flags": [],
            "unknowns": [],
            "source_batch_ref": {"batch_id": "b1", "batch_hash": "h1"},
            "integrity_verified": True,
            "integrity_error": None,
            "execution_approval_status": None,
            "execution_approval_id": None,
        }
        E._save_execution(envelope, execution_dir)

        approval = {
            "approval_id": "appr1",
            "approval_schema_version": E.SCHEMA_VERSION,
            "created_at": "2026-01-01T00:00:00+00:00",
            "batch_execution_id": "test-repo-mismatch",
            "batch_id": "b1",
            "batch_hash": "h1",
            "candidate_scope_hash": "s1",
            "approval_status": E.APPROVED_FOR_BOUNDED_EXECUTION,
            "approved_by": "HUMAN",
            "decision_authority": E.DECISION_AUTHORITY,
        }
        approval["approval_record_hash"] = E.compute_approval_record_hash(approval)
        store_result = E.store_approval_artifact(approval, execution_dir)
        assert store_result["status"] == "STORED"

        calls = []

        def _executor(child):
            calls.append(child)
            return {"session_id": "should-never-run", "kx108_decision": "ACT"}

        result = E.run_execution(
            "test-repo-mismatch", "appr1", _executor,
            execution_dir=execution_dir, repo_root=synthetic_repo,
        )
        child_out = result["children"][0]
        assert child_out["execution_status"] == E.SOURCE_REPOSITORY_IDENTITY_MISMATCH
        assert calls == []  # jamais appelé — refus AVANT tout executor


# ─── N. Relecture SHA256 complète (§9) ───────────────────────────────────────

class TestFullSha256Recheck:
    def test_full_sha256_mismatch_fails_closed_even_if_truncated_would_match(
        self, synthetic_repo, tmp_path,
    ):
        c1 = _resolve_commit(synthetic_repo, "candidate")
        blob = _blob_sha(synthetic_repo, c1, "src/module.py")
        import hashlib
        real_full = hashlib.sha256(b"CONTENT_A\n").hexdigest()

        child = {
            "source_kind": "GIT_BLOB",
            "source_git_commit_sha": c1,
            "source_git_historical_path": "src/module.py",
            "source_git_blob_sha": blob,
            # Préfixe tronqué correct, mais SHA256 complet volontairement faux.
            "source_content_sha256": real_full[:16] + "0" * 48,
        }
        assert resolve_source_bytes_hash(child, synthetic_repo) is None

    def test_full_sha256_match_succeeds(self, synthetic_repo, tmp_path):
        c1 = _resolve_commit(synthetic_repo, "candidate")
        blob = _blob_sha(synthetic_repo, c1, "src/module.py")
        import hashlib
        real_full = hashlib.sha256(b"CONTENT_A\n").hexdigest()

        child = {
            "source_kind": "GIT_BLOB",
            "source_git_commit_sha": c1,
            "source_git_historical_path": "src/module.py",
            "source_git_blob_sha": blob,
            "source_content_sha256": real_full,
        }
        rehash = resolve_source_bytes_hash(child, synthetic_repo)
        assert rehash == real_full[:16]


# ─── O. Liaison de l'identité source au batch_hash (§10) ────────────────────

class TestBatchHashBindsGitSourceIdentity:
    def test_different_entry_id_from_different_commit_changes_batch_hash(self):
        from obsidia_batch_selector import batch_hash_from_proposal

        h1 = batch_hash_from_proposal(
            ["entry-from-commit-A"], ["deadbeef00000001"], [], "obj", 10,
        )
        h2 = batch_hash_from_proposal(
            ["entry-from-commit-B"], ["deadbeef00000002"], [], "obj", 10,
        )
        assert h1 != h2

    def test_registering_same_blob_from_two_commits_yields_distinguishable_entries(
        self, synthetic_repo, tmp_path,
    ):
        ledger_dir = tmp_path / "ledger"
        c1 = _resolve_commit(synthetic_repo, "candidate")
        c2 = _git(synthetic_repo, "rev-parse", "HEAD")

        r1 = L.register_git_blob_source(
            c1, "src/module.py", ledger_dir=ledger_dir, repo_root=synthetic_repo,
        )
        r2 = L.register_git_blob_source(
            c2, "src/module.py", ledger_dir=ledger_dir, repo_root=synthetic_repo,
        )
        assert r1["ledger_entry_id"] != r2["ledger_entry_id"]

        from obsidia_batch_selector import batch_hash_from_proposal
        h1 = batch_hash_from_proposal([r1["ledger_entry_id"]], [], [], "obj", 10)
        h2 = batch_hash_from_proposal([r2["ledger_entry_id"]], [], [], "obj", 10)
        assert h1 != h2

    def test_same_source_different_target_stays_single_entry_no_silent_overwrite(
        self, synthetic_repo, tmp_path,
    ):
        """
        Caractéristique documentée (partagée avec le filesystem
        register_source existant) : l'identité d'entrée ne dépend pas de
        target_path. Réenregistrer le même (commit, chemin historique)
        avec une cible différente ne fabrique PAS silencieusement une
        seconde entrée avec la nouvelle cible — ALREADY_REGISTERED est
        retourné, l'entrée stockée garde sa cible d'origine. Documenté ici
        pour qu'aucune régression future ne le change sans le remarquer.
        """
        ledger_dir = tmp_path / "ledger"
        r1 = L.register_git_blob_source(
            "candidate", "src/module.py", target_path="dst/a.py",
            ledger_dir=ledger_dir, repo_root=synthetic_repo,
        )
        r2 = L.register_git_blob_source(
            "candidate", "src/module.py", target_path="dst/b.py",
            ledger_dir=ledger_dir, repo_root=synthetic_repo,
        )
        assert r1["status"] == "DISCOVERED"
        assert r2["status"] == "ALREADY_REGISTERED"
        entries = L._load_entries(ledger_dir)
        assert len(entries) == 1
        assert entries[0]["target_path"] == "dst/a.py"


# ─── P. CLI réel — arguments cités/multi-mots, environnement synthétique ────

class TestCLIRegisterGitSource:
    def test_cli_quoted_multiword_args_synthetic_only(self, synthetic_repo, tmp_path, monkeypatch):
        import obsidia_cli

        src_dir = synthetic_repo / "path with spaces"
        src_dir.mkdir()
        (src_dir / "module.py").write_bytes(b"SPACED\n")
        _git(synthetic_repo, "add", "path with spaces/module.py")
        _git(synthetic_repo, "commit", "-q", "-m", "spaced path")
        c_sha = _git(synthetic_repo, "rev-parse", "HEAD")

        ledger_dir = tmp_path / "cli_ledger"
        monkeypatch.setattr(L, "LEDGER_DIR", ledger_dir)
        monkeypatch.setattr(L, "_REPO_ROOT", synthetic_repo)

        raw_tokens = [
            "register-git-source",
            "--commit", c_sha,
            "--path", "path with spaces/module.py",
            "--target", "target path/module.py",
            "--reason", "multi word reason",
        ]
        result = obsidia_cli._dispatch_ledger("register-git-source", raw_tokens=raw_tokens)
        import json as _json
        parsed = _json.loads(result)
        assert parsed["status"] == "DISCOVERED"

        entries = L._load_entries(ledger_dir)
        assert len(entries) == 1
        assert entries[0]["source_git_historical_path"] == "path with spaces/module.py"
        assert entries[0]["target_path"] == "target path/module.py"
        assert entries[0]["objective"] == "multi word reason"

        # Aucune mutation du Ledger réel (LOCALAPPDATA) — isolation confirmée
        # par construction (LEDGER_DIR monkeypatché avant tout appel CLI).

    def test_cli_unknown_flag_fails_closed(self, synthetic_repo, tmp_path, monkeypatch):
        import obsidia_cli

        ledger_dir = tmp_path / "cli_ledger"
        monkeypatch.setattr(L, "LEDGER_DIR", ledger_dir)
        monkeypatch.setattr(L, "_REPO_ROOT", synthetic_repo)

        raw_tokens = ["register-git-source", "--commit", "candidate", "--bogus", "x"]
        result = obsidia_cli._dispatch_ledger("register-git-source", raw_tokens=raw_tokens)
        assert result.startswith("[LEDGER_CLI_ERROR]")
        assert L._load_entries(ledger_dir) == []

    def test_cli_missing_required_flags_fails_closed(self, synthetic_repo, tmp_path, monkeypatch):
        import obsidia_cli

        ledger_dir = tmp_path / "cli_ledger"
        monkeypatch.setattr(L, "LEDGER_DIR", ledger_dir)
        monkeypatch.setattr(L, "_REPO_ROOT", synthetic_repo)

        raw_tokens = ["register-git-source", "--commit", "candidate"]  # --path manquant
        result = obsidia_cli._dispatch_ledger("register-git-source", raw_tokens=raw_tokens)
        assert result.startswith("GUIDE:")
        assert L._load_entries(ledger_dir) == []
