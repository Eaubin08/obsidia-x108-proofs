"""
tests/test_source_content_apply_bridge_v0.py
===============================================
Suite GENERIC_SOURCE_CONTENT_APPLY_BRIDGE_V0.

Prouve, sur des cibles/dépôts synthétiques UNIQUEMENT (jamais ACD-01
réel, jamais le Ledger/Selector réels) :

  A. Résolution de source (filesystem + Git blob), TOCTOU
  B. Cible canonique — confinement, protection, portée
  C. Écriture atomique bas niveau — octets exacts, échecs simulés
  D. Preuve de rollback — octets exacts récupérables
  E. Orchestration complète de production (approbation obligatoire)
  F. Ref mobile ne peut jamais changer les octets appliqués
  G. Dérive de cible / source au moment de l'écriture → refus fermé
  H. Idempotence / rejeu
  I. apply n'émet jamais ACT
  J. Non-régression filesystem
"""
from __future__ import annotations

import base64
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import obsidia_branching_ledger as L  # noqa: E402
import obsidia_batch_selector as S  # noqa: E402
import obsidia_batch_execution as E  # noqa: E402
import obsidia_content_apply as C  # noqa: E402


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

    (repo / "src").mkdir()
    (repo / "src" / "module.py").write_bytes(b"NEW_SOURCE_CONTENT\n")
    _git(repo, "add", "src/module.py")
    _git(repo, "commit", "-q", "-m", "C1: new content")
    c1 = _git(repo, "rev-parse", "HEAD")

    (repo / "src" / "module.py").write_bytes(b"LATER_CONTENT_UNUSED\n")
    _git(repo, "add", "src/module.py")
    _git(repo, "commit", "-q", "-m", "C2: later content")

    _git(repo, "branch", "candidate", c1)

    # cible reelle, distincte de src/ pour eviter toute ambiguite
    (repo / "dst").mkdir()
    (repo / "dst" / "target.py").write_bytes(b"OLD_TARGET_CONTENT\n")

    # sentinelle pour prouver l'absence de mutation collaterale
    (repo / "sentinel.txt").write_bytes(b"SENTINEL\n")

    return repo


# ─── Helper test-only : frontière d'approbation externe simulée ─────────────

def _build_synthetic_approval_record(envelope: dict, approval_id: str = "test-approval") -> dict:
    record = {
        "approval_id": approval_id,
        "approval_schema_version": E.SCHEMA_VERSION,
        "created_at": "2026-01-01T00:00:00+00:00",
        "batch_execution_id": envelope["batch_execution_id"],
        "batch_id": envelope["batch_id"],
        "batch_hash": envelope["batch_hash"],
        "candidate_scope_hash": envelope["candidate_scope_hash"],
        "approved_by": "HUMAN",
        "approval_status": E.APPROVED_FOR_BOUNDED_EXECUTION,
        "decision_authority": E.DECISION_AUTHORITY,
    }
    record["approval_record_hash"] = E.compute_approval_record_hash(record)
    return record


def _create_synthetic_approval(envelope: dict, execution_dir: Path, approval_id: str = "test-approval") -> str:
    record = _build_synthetic_approval_record(envelope, approval_id)
    result = E.store_approval_artifact(record, execution_dir)
    assert result["status"] == "STORED"
    return record["approval_id"]


def _prepare_git_flow(synthetic_repo, tmp_path, target_rel="dst/target.py"):
    """Ledger réel -> proposal réelle -> envelope réelle -> approbation synthétique. Tout isolé."""
    ledger_dir = tmp_path / "ledger"
    selector_dir = tmp_path / "selector"
    execution_dir = tmp_path / "exec"

    reg = L.register_git_blob_source(
        "candidate", "src/module.py", target_path=target_rel,
        target_domain="TOOLING", reason="synthetic apply bridge test",
        provenance_refs={"operation_type": "UPDATE_TARGET_FROM_SOURCE"},
        repo_root=synthetic_repo, ledger_dir=ledger_dir,
    )
    assert reg["status"] == "DISCOVERED"

    proposal = S.propose_batch(
        objective="synthetic apply", max_batch_size=1,
        ledger_dir=ledger_dir, selector_dir=selector_dir,
        candidate_entry_ids=[reg["ledger_entry_id"]],
    )
    assert proposal["selected_count"] == 1

    envelope = E.prepare_execution(
        proposal["batch_id"], ledger_dir=ledger_dir, selector_dir=selector_dir,
        execution_dir=execution_dir, repo_root=synthetic_repo,
    )
    assert envelope["integrity_verified"] is True
    child = envelope["children"][0]
    assert child["execution_status"] == E.PLANNED

    approval_id = _create_synthetic_approval(envelope, execution_dir)

    return {
        "ledger_dir": ledger_dir, "selector_dir": selector_dir, "execution_dir": execution_dir,
        "envelope": envelope, "child": child, "approval_id": approval_id, "reg": reg,
        "proposal": proposal,
    }


def _prepare_filesystem_flow(tmp_path, source_content=b"NEW_FS_CONTENT\n", target_content=b"OLD_FS_TARGET\n"):
    repo_root = tmp_path / "fs_repo"
    repo_root.mkdir()
    src = repo_root / "source.py"
    src.write_bytes(source_content)
    dst = repo_root / "target.py"
    dst.write_bytes(target_content)

    ledger_dir = tmp_path / "ledger"
    selector_dir = tmp_path / "selector"
    execution_dir = tmp_path / "exec"

    reg = L.register_source(
        str(src), target_path="target.py", target_domain="TOOLING",
        reason="synthetic fs apply", ledger_dir=ledger_dir,
    )
    assert reg["status"] == "DISCOVERED"

    # operation_type doit etre porte par l'entree — injecte directement
    # (lecture reelle, pas de fabrication de decision KX108).
    import json as _json
    entries = L._load_entries(ledger_dir)
    entries[0]["provenance_refs"] = {"operation_type": "UPDATE_TARGET_FROM_SOURCE"}
    (ledger_dir / "entries.jsonl").write_text(
        "\n".join(_json.dumps(e, ensure_ascii=False) for e in entries) + "\n", encoding="utf-8",
    )

    proposal = S.propose_batch(
        objective="synthetic fs apply", max_batch_size=1,
        ledger_dir=ledger_dir, selector_dir=selector_dir,
        candidate_entry_ids=[reg["ledger_entry_id"]],
    )
    assert proposal["selected_count"] == 1

    envelope = E.prepare_execution(
        proposal["batch_id"], ledger_dir=ledger_dir, selector_dir=selector_dir,
        execution_dir=execution_dir, repo_root=repo_root,
    )
    assert envelope["integrity_verified"] is True
    child = envelope["children"][0]
    assert child["execution_status"] == E.PLANNED

    approval_id = _create_synthetic_approval(envelope, execution_dir)

    return {
        "repo_root": repo_root, "ledger_dir": ledger_dir, "selector_dir": selector_dir,
        "execution_dir": execution_dir, "envelope": envelope, "child": child,
        "approval_id": approval_id, "dst": dst, "src": src,
    }


# ─── A/E. Résolution de source + orchestration complète — filesystem ───────

class TestFilesystemApplyEndToEnd:
    def test_filesystem_apply_success(self, tmp_path):
        ctx = _prepare_filesystem_flow(tmp_path)
        result = C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            ctx["approval_id"], execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=ctx["repo_root"],
            evidence_dir=tmp_path / "evidence",
        )
        assert result["status"] == C.CONTENT_APPLIED
        assert ctx["dst"].read_bytes() == b"NEW_FS_CONTENT\n"
        assert result["target_post_sha256"] == result["source_full_sha256"]
        # aucune emission de decision KX108
        assert "kx108_decision" not in result

    def test_filesystem_source_drift_before_write_rejected(self, tmp_path):
        ctx = _prepare_filesystem_flow(tmp_path)
        ctx["src"].write_bytes(b"MUTATED_AFTER_PREPARE\n")
        result = C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            ctx["approval_id"], execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=ctx["repo_root"],
            evidence_dir=tmp_path / "evidence",
        )
        assert result["status"] == C.SOURCE_INTEGRITY_MISMATCH
        assert ctx["dst"].read_bytes() == b"OLD_FS_TARGET\n"


# ─── E/F. Orchestration complète — Git blob ──────────────────────────────────

class TestGitBlobApplyEndToEnd:
    def test_git_blob_apply_success(self, synthetic_repo, tmp_path):
        ctx = _prepare_git_flow(synthetic_repo, tmp_path)
        result = C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            ctx["approval_id"], execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo,
            evidence_dir=tmp_path / "evidence",
        )
        assert result["status"] == C.CONTENT_APPLIED
        target = synthetic_repo / "dst" / "target.py"
        assert target.read_bytes() == b"NEW_SOURCE_CONTENT\n"
        assert result["source_full_sha256"] == result["target_post_sha256"]

        # aucun autre fichier touche
        assert (synthetic_repo / "sentinel.txt").read_bytes() == b"SENTINEL\n"
        assert (synthetic_repo / "src" / "module.py").read_bytes() == b"LATER_CONTENT_UNUSED\n"

    def test_moving_ref_cannot_change_applied_bytes(self, synthetic_repo, tmp_path):
        ctx = _prepare_git_flow(synthetic_repo, tmp_path)
        # deplacement de la branche APRES enregistrement/preparation
        c2 = _git(synthetic_repo, "rev-parse", "HEAD")
        _git(synthetic_repo, "branch", "-f", "candidate", c2)

        result = C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            ctx["approval_id"], execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo,
            evidence_dir=tmp_path / "evidence",
        )
        assert result["status"] == C.CONTENT_APPLIED
        target = synthetic_repo / "dst" / "target.py"
        # les octets ecrits viennent de C1 (immuable), jamais de C2
        assert target.read_bytes() == b"NEW_SOURCE_CONTENT\n"


# ─── G. Dérive au moment de l'écriture ────────────────────────────────────────

class TestDriftAtWriteTime:
    def test_target_drift_after_prepare_rejected(self, synthetic_repo, tmp_path):
        ctx = _prepare_git_flow(synthetic_repo, tmp_path)
        target = synthetic_repo / "dst" / "target.py"
        target.write_bytes(b"EXTERNALLY_MUTATED\n")

        result = C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            ctx["approval_id"], execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo,
            evidence_dir=tmp_path / "evidence",
        )
        assert result["status"] == C.TARGET_PRECONDITION_MISMATCH
        assert target.read_bytes() == b"EXTERNALLY_MUTATED\n"

    def test_tampered_git_commit_sha_rejected(self, synthetic_repo, tmp_path):
        ctx = _prepare_git_flow(synthetic_repo, tmp_path)
        ctx["child"]["source_git_commit_sha"] = "0" * 40
        # Ecrit l'enveloppe modifiee pour que l'orchestration la relise telle quelle
        E._save_execution(ctx["envelope"], ctx["execution_dir"])

        result = C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            ctx["approval_id"], execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo,
            evidence_dir=tmp_path / "evidence",
        )
        # Detecte par l'empreinte d'integrite precondition/provenance
        # (verifiee plus tot que le TOCTOU source specifique) — meme
        # propriete de securite (aucune ecriture), gate plus generique.
        assert result["status"] == C.BATCH_BINDING_MISMATCH
        assert result["reason"] == "PRECONDITION_INTEGRITY_HASH_MISMATCH"
        target = synthetic_repo / "dst" / "target.py"
        assert target.read_bytes() == b"OLD_TARGET_CONTENT\n"

    def test_tampered_full_sha256_rejected(self, synthetic_repo, tmp_path):
        ctx = _prepare_git_flow(synthetic_repo, tmp_path)
        ctx["child"]["source_content_sha256"] = "0" * 64
        E._save_execution(ctx["envelope"], ctx["execution_dir"])

        result = C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            ctx["approval_id"], execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo,
            evidence_dir=tmp_path / "evidence",
        )
        assert result["status"] == C.BATCH_BINDING_MISMATCH
        assert result["reason"] == "PRECONDITION_INTEGRITY_HASH_MISMATCH"


# ─── B. Confinement de cible — protégé / hors dépôt / racine ────────────────

class TestTargetConfinement:
    def test_protected_target_rejected(self):
        abs_path, reason = C.canonicalize_write_target("proofs/x.py")
        assert abs_path is None
        assert reason == "REFUSED_PROTECTED_TARGET"

    def test_formal_protected_target_rejected(self):
        abs_path, reason = C.canonicalize_write_target("formal/x.txt")
        assert abs_path is None
        assert reason == "REFUSED_PROTECTED_TARGET"

    def test_merkle_seal_protected_rejected(self):
        abs_path, reason = C.canonicalize_write_target("merkle_seal.json")
        assert abs_path is None
        assert reason == "REFUSED_PROTECTED_TARGET"

    def test_sealed_kernel_protected_rejected(self):
        abs_path, reason = C.canonicalize_write_target(
            "runtime_terrain_bank_trading_gps/server.kernel.sealed.cjs"
        )
        assert abs_path is None
        assert reason == "REFUSED_PROTECTED_TARGET"

    def test_traversal_outside_repo_rejected(self):
        abs_path, reason = C.canonicalize_write_target("../outside.py")
        assert abs_path is None
        assert reason == "TARGET_OUTSIDE_REPO_NAMESPACE"

    def test_absolute_outside_repo_rejected(self, tmp_path):
        abs_path, reason = C.canonicalize_write_target(str(tmp_path / "outside.py"))
        assert abs_path is None
        assert reason == "TARGET_OUTSIDE_REPO_NAMESPACE"

    def test_valid_target_accepted(self):
        abs_path, reason = C.canonicalize_write_target("scripts/check_forbidden_content.py")
        assert reason is None
        assert abs_path == (_REPO_ROOT / "scripts" / "check_forbidden_content.py").resolve()


class TestScopeEscape:
    def test_bridge_refuses_target_outside_approved_scope(self, synthetic_repo, tmp_path):
        ctx = _prepare_git_flow(synthetic_repo, tmp_path, target_rel="dst/target.py")
        # tentative de detournement vers une autre cible que celle approuvee
        ctx["child"]["target_path"] = "dst/other.py"
        E._save_execution(ctx["envelope"], ctx["execution_dir"])

        result = C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            ctx["approval_id"], execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo,
            evidence_dir=tmp_path / "evidence",
        )
        # Detecte par l'empreinte d'integrite precondition (target_path en
        # fait partie) avant meme d'atteindre la verification de portee.
        assert result["status"] == C.BATCH_BINDING_MISMATCH
        assert result["reason"] == "PRECONDITION_INTEGRITY_HASH_MISMATCH"
        assert not (synthetic_repo / "dst" / "other.py").exists()
        assert (synthetic_repo / "dst" / "target.py").read_bytes() == b"OLD_TARGET_CONTENT\n"


# ─── C. Écriture atomique bas niveau — octets exacts ─────────────────────────

class TestAtomicWriteExactBytes:
    @pytest.mark.parametrize("content", [
        b"line1\r\nline2\r\n",              # CRLF
        b"line1\nline2\n",                   # LF
        "café éè 中文\n".encode("utf-8"),  # UTF-8 non-ASCII
        b"before\x00after\n",                 # octet nul
        b"",                                    # vide
    ])
    def test_exact_byte_preservation(self, tmp_path, content):
        target = tmp_path / "target.bin"
        target.write_bytes(b"OLD\n")
        pre_sha = C._full_sha256(b"OLD\n")
        result = C.atomic_replace_with_bytes(target, content, pre_sha)
        assert result["status"] == C.CONTENT_APPLIED
        assert target.read_bytes() == content  # aucune normalisation

    def test_target_precondition_mismatch_no_write(self, tmp_path):
        target = tmp_path / "target.txt"
        target.write_bytes(b"ACTUAL\n")
        result = C.atomic_replace_with_bytes(target, b"NEW\n", C._full_sha256(b"WRONG_EXPECTED\n"))
        assert result["status"] == C.TARGET_PRECONDITION_MISMATCH
        assert target.read_bytes() == b"ACTUAL\n"

    def test_missing_target_precondition_none_allows_create(self, tmp_path):
        target = tmp_path / "new_target.txt"
        assert not target.exists()
        result = C.atomic_replace_with_bytes(target, b"BRAND_NEW\n", None)
        assert result["status"] == C.CONTENT_APPLIED
        assert target.read_bytes() == b"BRAND_NEW\n"

    def test_missing_target_but_precondition_expects_existing_rejected(self, tmp_path):
        target = tmp_path / "absent.txt"
        result = C.atomic_replace_with_bytes(target, b"X\n", C._full_sha256(b"anything\n"))
        assert result["status"] == C.TARGET_PRECONDITION_MISMATCH
        assert not target.exists()

    def test_no_temp_file_left_behind_on_success(self, tmp_path):
        target = tmp_path / "target.txt"
        target.write_bytes(b"OLD\n")
        C.atomic_replace_with_bytes(target, b"NEW\n", C._full_sha256(b"OLD\n"))
        leftovers = list(tmp_path.glob(".*obsidia_apply*"))
        assert leftovers == []


# ─── D. Preuve de rollback ────────────────────────────────────────────────────

class TestRollbackEvidence:
    def test_rollback_evidence_contains_exact_pre_write_bytes(self, synthetic_repo, tmp_path):
        ctx = _prepare_git_flow(synthetic_repo, tmp_path)
        evidence_dir = tmp_path / "evidence"
        result = C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            ctx["approval_id"], execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo, evidence_dir=evidence_dir,
        )
        assert result["status"] == C.CONTENT_APPLIED

        rollback = C.load_rollback_evidence(ctx["child"]["child_execution_id"], evidence_dir)
        assert rollback is not None
        restored = base64.b64decode(rollback["pre_write_bytes_b64"])
        assert restored == b"OLD_TARGET_CONTENT\n"
        assert rollback["pre_write_sha256"] == C._full_sha256(b"OLD_TARGET_CONTENT\n")
        assert rollback["operation_type"] == "UPDATE_TARGET_FROM_SOURCE"
        assert rollback["decision_authority"] == "KX108_ONLY"


# ─── H. Idempotence / rejeu ───────────────────────────────────────────────────

class TestIdempotence:
    def test_replay_same_child_returns_already_applied(self, synthetic_repo, tmp_path):
        ctx = _prepare_git_flow(synthetic_repo, tmp_path)
        evidence_dir = tmp_path / "evidence"
        r1 = C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            ctx["approval_id"], execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo, evidence_dir=evidence_dir,
        )
        assert r1["status"] == C.CONTENT_APPLIED

        # Reinvocation exacte (child toujours PLANNED dans l'enveloppe stockee,
        # car cette orchestration ne mute pas execution_status de l'enveloppe).
        r2 = C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            ctx["approval_id"], execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo, evidence_dir=evidence_dir,
        )
        assert r2["status"] == C.ALREADY_APPLIED_SAME_CONTENT

        target = synthetic_repo / "dst" / "target.py"
        assert target.read_bytes() == b"NEW_SOURCE_CONTENT\n"

    def test_replay_still_verifies_approval_and_integrity(self, synthetic_repo, tmp_path):
        ctx = _prepare_git_flow(synthetic_repo, tmp_path)
        evidence_dir = tmp_path / "evidence"
        C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            ctx["approval_id"], execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo, evidence_dir=evidence_dir,
        )
        # rejeu avec un approval_id invalide -> refuse malgre l'idempotence potentielle
        result = C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            "nonexistent-approval", execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo, evidence_dir=evidence_dir,
        )
        assert result["status"] == C.APPROVAL_INVALID


# ─── E. Approbation obligatoire ────────────────────────────────────────────────

class TestApprovalBoundary:
    def test_missing_approval_refuses_write(self, synthetic_repo, tmp_path):
        ctx = _prepare_git_flow(synthetic_repo, tmp_path)
        result = C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            "does-not-exist", execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo,
            evidence_dir=tmp_path / "evidence",
        )
        assert result["status"] == C.APPROVAL_INVALID
        target = synthetic_repo / "dst" / "target.py"
        assert target.read_bytes() == b"OLD_TARGET_CONTENT\n"

    def test_wrong_batch_binding_approval_refuses_write(self, synthetic_repo, tmp_path):
        ctx = _prepare_git_flow(synthetic_repo, tmp_path)
        forged = _build_synthetic_approval_record(ctx["envelope"], approval_id="forged")
        forged["batch_hash"] = "wrong-hash"
        forged["approval_record_hash"] = E.compute_approval_record_hash(forged)
        E.store_approval_artifact(forged, ctx["execution_dir"])

        result = C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            "forged", execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo,
            evidence_dir=tmp_path / "evidence",
        )
        assert result["status"] == C.APPROVAL_INVALID
        target = synthetic_repo / "dst" / "target.py"
        assert target.read_bytes() == b"OLD_TARGET_CONTENT\n"


# ─── I. apply n'émet jamais ACT ───────────────────────────────────────────────

class TestApplyNeverEmitsAct:
    def test_content_applied_result_has_no_kx108_decision(self, synthetic_repo, tmp_path):
        ctx = _prepare_git_flow(synthetic_repo, tmp_path)
        result = C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            ctx["approval_id"], execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo,
            evidence_dir=tmp_path / "evidence",
        )
        assert result["status"] == C.CONTENT_APPLIED
        assert "kx108_decision" not in result
        assert result.get("decision_authority") == "KX108_ONLY"

        # l'enveloppe elle-meme reste inchangee (le pont ne mute pas
        # execution_status/kx108_decision de l'enveloppe stockee).
        reloaded = E._load_execution(ctx["envelope"]["batch_execution_id"], ctx["execution_dir"])
        stored_child = reloaded["children"][0]
        assert stored_child["execution_status"] == E.PLANNED
        assert stored_child.get("kx108_decision") is None


# ─── J. Non-régression filesystem ────────────────────────────────────────────

class TestFilesystemNonRegression:
    def test_resolve_source_bytes_filesystem_kind_default(self, tmp_path):
        f = tmp_path / "plain.py"
        f.write_bytes(b"PLAIN\n")
        child = {"source_path": "plain.py"}  # pas de source_kind — legacy
        data, reason = C.resolve_source_bytes(child, tmp_path)
        assert reason is None
        assert data == b"PLAIN\n"

    def test_resolve_source_bytes_missing_file_fails_closed(self, tmp_path):
        child = {"source_kind": "FILESYSTEM_FILE", "source_path": "absent.py"}
        data, reason = C.resolve_source_bytes(child, tmp_path)
        assert data is None
        assert reason == "SOURCE_FILE_MISSING"


# ─── K. HARDEN_CONTENT_APPLY_PRECONDITION_AND_IDEMPOTENCE_V0 ────────────────

class TestFullTargetPreconditionPersisted:
    def test_prepare_execution_captures_full_target_pre_sha256(self, synthetic_repo, tmp_path):
        ctx = _prepare_git_flow(synthetic_repo, tmp_path)
        expected_full = C._full_sha256(b"OLD_TARGET_CONTENT\n")
        assert ctx["child"]["target_pre_sha256"] == expected_full
        assert ctx["child"]["target_pre_hash"] == expected_full[:16]

    def test_full_target_pre_sha256_survives_persistence_and_reload(self, synthetic_repo, tmp_path):
        ctx = _prepare_git_flow(synthetic_repo, tmp_path)
        reloaded = E._load_execution(ctx["envelope"]["batch_execution_id"], ctx["execution_dir"])
        reloaded_child = reloaded["children"][0]
        assert reloaded_child["target_pre_sha256"] == ctx["child"]["target_pre_sha256"]
        assert reloaded_child["precondition_integrity_hash"] == ctx["child"]["precondition_integrity_hash"]

    def test_precondition_integrity_hash_binds_target_pre_sha256(self, synthetic_repo, tmp_path):
        ctx = _prepare_git_flow(synthetic_repo, tmp_path)
        # Falsification isolee du SEUL champ target_pre_sha256 (le préfixe
        # tronqué de compatibilité reste, lui, correct) — l'empreinte
        # d'intégrité doit quand même détecter la divergence.
        ctx["child"]["target_pre_sha256"] = "f" * 64
        E._save_execution(ctx["envelope"], ctx["execution_dir"])

        result = C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            ctx["approval_id"], execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo,
            evidence_dir=tmp_path / "evidence",
        )
        assert result["status"] == C.BATCH_BINDING_MISMATCH
        assert result["reason"] == "PRECONDITION_INTEGRITY_HASH_MISMATCH"
        target = synthetic_repo / "dst" / "target.py"
        assert target.read_bytes() == b"OLD_TARGET_CONTENT\n"


class TestTruncatedHashNotSufficientAuthority:
    def test_correct_truncated_prefix_but_wrong_full_sha256_rejected(self, synthetic_repo, tmp_path):
        """
        §7 — construit un child ou le prefixe tronque de compatibilite
        (target_pre_hash) est EXACT, mais le SHA256 complet est
        volontairement faux, ET l'empreinte d'integrite est recalculee
        pour rester coherente avec ce faux SHA256 complet (simulant un
        attaquant capable de maintenir cette coherence interne). Le
        SHA256 complet reste neanmoins l'autorite : le prefixe tronque
        correct seul ne peut jamais suffire.
        """
        ctx = _prepare_git_flow(synthetic_repo, tmp_path)
        real_full = C._full_sha256(b"OLD_TARGET_CONTENT\n")
        forged_full = real_full[:16] + "0" * 48  # meme prefixe 16, fin fausse
        assert forged_full != real_full

        ctx["child"]["target_pre_sha256"] = forged_full
        # target_pre_hash (prefixe) reste correct/inchange
        assert ctx["child"]["target_pre_hash"] == real_full[:16]
        ctx["child"]["precondition_integrity_hash"] = E.compute_child_precondition_integrity_hash(ctx["child"])
        E._save_execution(ctx["envelope"], ctx["execution_dir"])

        result = C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            ctx["approval_id"], execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo,
            evidence_dir=tmp_path / "evidence",
        )
        # L'empreinte d'integrite est maintenant coherente (recalculee) —
        # c'est le SHA256 complet, comparé aux octets REELS de la cible,
        # qui refuse l'ecriture.
        assert result["status"] == C.TARGET_PRECONDITION_MISMATCH
        assert result["expected_target_pre_sha256"] == forged_full
        assert result["actual_target_sha256"] == real_full
        target = synthetic_repo / "dst" / "target.py"
        assert target.read_bytes() == b"OLD_TARGET_CONTENT\n"


class TestLegacyExecutionMissingFullPrecondition:
    def test_legacy_child_without_target_pre_sha256_refused(self, synthetic_repo, tmp_path):
        ctx = _prepare_git_flow(synthetic_repo, tmp_path)
        # Simule une enveloppe créée AVANT ce durcissement : le champ
        # target_pre_sha256 (et l'empreinte qui en dépend) est absent.
        del ctx["child"]["target_pre_sha256"]
        del ctx["child"]["precondition_integrity_hash"]
        E._save_execution(ctx["envelope"], ctx["execution_dir"])

        result = C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            ctx["approval_id"], execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo,
            evidence_dir=tmp_path / "evidence",
        )
        assert result["status"] == C.NOT_READY_STRONG_PRECONDITION_REQUIRED
        target = synthetic_repo / "dst" / "target.py"
        assert target.read_bytes() == b"OLD_TARGET_CONTENT\n"


class TestExactReplaySemantics:
    def test_replay_performs_no_second_atomic_replace(self, synthetic_repo, tmp_path):
        ctx = _prepare_git_flow(synthetic_repo, tmp_path)
        evidence_dir = tmp_path / "evidence"
        r1 = C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            ctx["approval_id"], execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo, evidence_dir=evidence_dir,
        )
        assert r1["status"] == C.CONTENT_APPLIED
        target = synthetic_repo / "dst" / "target.py"
        mtime_after_first = target.stat().st_mtime_ns
        inode_after_first = target.stat().st_ino if hasattr(target.stat(), "st_ino") else None

        r2 = C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            ctx["approval_id"], execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo, evidence_dir=evidence_dir,
        )
        assert r2["status"] == C.ALREADY_APPLIED_SAME_CONTENT
        assert target.read_bytes() == b"NEW_SOURCE_CONTENT\n"
        # Aucun second remplacement atomique n'a eu lieu — mtime inchange.
        assert target.stat().st_mtime_ns == mtime_after_first
        if inode_after_first is not None:
            assert target.stat().st_ino == inode_after_first

    def test_replay_preserves_original_rollback_baseline(self, synthetic_repo, tmp_path):
        ctx = _prepare_git_flow(synthetic_repo, tmp_path)
        evidence_dir = tmp_path / "evidence"
        C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            ctx["approval_id"], execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo, evidence_dir=evidence_dir,
        )
        rollback_after_first = C.load_rollback_evidence(ctx["child"]["child_execution_id"], evidence_dir)
        assert base64.b64decode(rollback_after_first["pre_write_bytes_b64"]) == b"OLD_TARGET_CONTENT\n"

        C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            ctx["approval_id"], execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo, evidence_dir=evidence_dir,
        )
        rollback_after_replay = C.load_rollback_evidence(ctx["child"]["child_execution_id"], evidence_dir)
        # La baseline de rollback reste celle du PREMIER apply (OLD), jamais
        # remplacee par NEW malgre le rejeu.
        assert base64.b64decode(rollback_after_replay["pre_write_bytes_b64"]) == b"OLD_TARGET_CONTENT\n"
        assert rollback_after_replay == rollback_after_first

    def test_replay_does_not_produce_duplicate_success_receipt_with_different_evidence(
        self, synthetic_repo, tmp_path,
    ):
        ctx = _prepare_git_flow(synthetic_repo, tmp_path)
        evidence_dir = tmp_path / "evidence"
        r1 = C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            ctx["approval_id"], execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo, evidence_dir=evidence_dir,
        )
        receipt_after_first = C.load_apply_receipt(ctx["child"]["child_execution_id"], evidence_dir)

        C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            ctx["approval_id"], execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo, evidence_dir=evidence_dir,
        )
        receipt_after_replay = C.load_apply_receipt(ctx["child"]["child_execution_id"], evidence_dir)
        # Le rejeu (statut ALREADY_APPLIED_SAME_CONTENT) n'ecrit pas de
        # nouveau receipt CONTENT_APPLIED — l'historique reste celui du
        # premier succes reel.
        assert receipt_after_replay == receipt_after_first
        assert receipt_after_first["status"] == C.CONTENT_APPLIED


class TestCrossChildReceiptIsolation:
    def test_different_child_cannot_reuse_receipt(self, synthetic_repo, tmp_path):
        ctx = _prepare_git_flow(synthetic_repo, tmp_path)
        evidence_dir = tmp_path / "evidence"
        C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            ctx["approval_id"], execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo, evidence_dir=evidence_dir,
        )
        # Aucun receipt n'existe pour un child_execution_id different, meme
        # cible/source — l'isolation est structurelle (cle = child_execution_id).
        other_receipt = C.load_apply_receipt("some-other-child-id-never-applied", evidence_dir)
        assert other_receipt is None


class TestNoReceiptNoIdempotentSuccess:
    def test_target_already_equals_source_without_receipt_is_not_idempotent_success(
        self, synthetic_repo, tmp_path,
    ):
        """
        §14 — la cible vaut déjà les octets source (par coïncidence, pas
        via ce pont) mais aucun receipt CONTENT_APPLIED n'existe pour ce
        child : ne doit JAMAIS retourner ALREADY_APPLIED_SAME_CONTENT.
        La précondition stricte (capturée à prepare_execution, sur
        l'ancien contenu) doit refuser fermé.
        """
        ctx = _prepare_git_flow(synthetic_repo, tmp_path)
        evidence_dir = tmp_path / "evidence"
        assert C.load_apply_receipt(ctx["child"]["child_execution_id"], evidence_dir) is None

        # La cible se retrouve DEJA a la valeur source, hors de ce pont.
        target = synthetic_repo / "dst" / "target.py"
        target.write_bytes(b"NEW_SOURCE_CONTENT\n")

        result = C.apply_validated_source_content(
            ctx["envelope"]["batch_execution_id"], ctx["child"]["child_execution_id"],
            ctx["approval_id"], execution_dir=ctx["execution_dir"], selector_dir=ctx["selector_dir"],
            ledger_dir=ctx["ledger_dir"], repo_root=synthetic_repo, evidence_dir=evidence_dir,
        )
        assert result["status"] != C.ALREADY_APPLIED_SAME_CONTENT
        assert result["status"] == C.TARGET_PRECONDITION_MISMATCH
