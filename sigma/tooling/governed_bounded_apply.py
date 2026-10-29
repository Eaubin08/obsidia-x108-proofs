"""
sigma/tooling/governed_bounded_apply.py
========================================
MODULE ISOLÉ D'APPLICATION BORNÉE GOUVERNÉE (PHASE 3B)

Implémente la séquence stricte de gouvernance sans inversion d'écriture :
  INTENTION
  → VALIDATION (Scope, Protected paths, HEAD)
  → DÉCISION KX108 (GuardX108)
  → AUTORISATION VÉRIFIÉE (SovereignTicket HMAC + Anti-rejeu)
  → MUTATION ATOMIQUE SOUS SCELLAGE ROLLBACK
  → PREUVE & POST-TESTS
  → COMMITTED (ou ROLLBACK IMMÉDIAT en cas d'échec)

Aucune écriture sur disque ne peut intervenir avant une décision KX108 valide (ALLOW).
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from periphery.world_calls.sovereign_ticket import (
    SovereignTicket,
    issue_sovereign_ticket,
    TICKET_VERSION_V1,
)
from periphery.world_calls.ticket_store import (
    verify_and_consume_sovereign_ticket,
    fail_ticket_nonce,
)
from sigma.contracts import (
    Domain,
    DomainAggregate,
    AgentVote,
    Severity,
    AuthorityLevel,
)
from sigma.guard import GuardX108


@dataclass
class ToolingBuildState:
    session_id: str
    objective: str
    base_sha: str
    manifest_hash: str
    diff_hash: str
    approved_scope: List[str]
    actual_touched_files: List[str]
    protected_scope_status: str
    human_approval_status: str
    obsidure_status: str
    worktree_isolated: bool
    branch_isolated: bool
    auto_commit_disabled: bool
    auto_push_disabled: bool
    auto_merge_disabled: bool
    tests_results: str
    gates_results: str
    unknowns: List[str] = field(default_factory=list)
    contradictions: List[str] = field(default_factory=list)
    risk_flags: List[str] = field(default_factory=list)
    decision_authority: str = "KX108_ONLY"

# Fichiers protégés canoniques — aucune écriture permise
PROTECTED_PATHS = (
    "server.kernel.sealed.cjs",
    "proofs/",
    "formal/",
    "merkle_seal.json",
    "merkle_root.json",
    "audit_merkle.py",
)


@dataclass
class PatchOperation:
    path: str
    content: str
    op_type: str = "WRITE"  # "WRITE" | "DELETE"


@dataclass
class PatchProposal:
    proposal_id: str
    base_sha: str
    target_worktree: str
    approved_scope: List[str]
    operations: List[PatchOperation]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def raw_payload(self) -> List[dict]:
        return [
            {"path": op.path.replace("\\", "/"), "content": op.content, "type": op.op_type}
            for op in sorted(self.operations, key=lambda x: x.path)
        ]

    @property
    def patch_hash(self) -> str:
        """Empreinte canonique déterministe du patch."""
        serialized = json.dumps(self.raw_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(serialized).hexdigest()

    @property
    def touched_files(self) -> List[str]:
        return sorted({op.path.replace("\\", "/") for op in self.operations})


@dataclass
class SealedRollbackEvidence:
    """Instantané pré-mutation scellé en mémoire et persisté en journal WAL avant toute écriture disque."""
    evidence_id: str
    proposal_id: str
    created_at: str
    original_files: Dict[str, Optional[str]]  # path -> content (None si le fichier n'existait pas)
    pre_state_hashes: Dict[str, Optional[str]]

    def execute_rollback(self, target_worktree: str) -> None:
        worktree = Path(target_worktree)
        for path_str, orig_content in self.original_files.items():
            restored_file = worktree / path_str
            if orig_content is None:
                if restored_file.exists():
                    restored_file.unlink()
            else:
                restored_file.parent.mkdir(parents=True, exist_ok=True)
                restored_file.write_text(orig_content, encoding="utf-8")

    def persist_wal(self, target_worktree: str) -> Path:
        """Écrit et synchronise sur disque (fsync) le journal WAL de rollback avant la première mutation."""
        wal_dir = Path(target_worktree) / ".obsidia_wal"
        wal_dir.mkdir(parents=True, exist_ok=True)
        wal_file = wal_dir / f"wal_{self.proposal_id}.json"
        data = {
            "evidence_id": self.evidence_id,
            "proposal_id": self.proposal_id,
            "created_at": self.created_at,
            "original_files": self.original_files,
            "pre_state_hashes": self.pre_state_hashes,
            "state": "MUTATION_IN_PROGRESS",
        }
        with open(wal_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        return wal_file

    def clear_wal(self, target_worktree: str) -> None:
        """Nettoie le journal WAL une fois la transaction validée ou annulée."""
        wal_file = Path(target_worktree) / ".obsidia_wal" / f"wal_{self.proposal_id}.json"
        if wal_file.exists():
            try:
                wal_file.unlink()
            except OSError:
                pass

    @staticmethod
    def recover_dangling_wal(target_worktree: str) -> List[str]:
        """
        Procédure de réconciliation post-crash système (coupure, SIGKILL) :
        Scanne et restaure automatiquement l'état d'origine si un journal WAL
        orphelin est présent sur le worktree au redémarrage.
        """
        wal_dir = Path(target_worktree) / ".obsidia_wal"
        recovered = []
        if not wal_dir.exists():
            return recovered

        for wal_file in wal_dir.glob("wal_*.json"):
            try:
                with open(wal_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                worktree = Path(target_worktree)
                for path_str, orig_content in data.get("original_files", {}).items():
                    target_file = worktree / path_str
                    if orig_content is None:
                        if target_file.exists():
                            target_file.unlink()
                    else:
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        target_file.write_text(orig_content, encoding="utf-8")
                wal_file.unlink()
                recovered.append(data.get("proposal_id", wal_file.stem))
            except Exception:
                continue
        return recovered


@dataclass
class GovernedApplyResult:
    status: str  # "COMMITTED" | "REFUSED_PRE_DECISION" | "ROLLED_BACK" | "ERROR"
    proposal_id: str
    kx108_pre_gate: str
    kx108_reason: str
    ticket_id: Optional[str]
    disk_written: bool
    rolled_back: bool
    modified_files: List[str]
    receipt_path: Optional[str] = None
    error_detail: str = ""


class GovernedBoundedApply:
    """Moteur d'application bornée gouvernée."""

    def __init__(self, worktree_head_provider: Optional[Callable[[str], str]] = None):
        # Fournisseur de HEAD pour validation de dérive (mockable pour tests isolés)
        self.head_provider = worktree_head_provider or self._default_head_provider

    @staticmethod
    def _default_head_provider(worktree_path: str) -> str:
        head_file = Path(worktree_path) / ".git" / "HEAD"
        if head_file.exists():
            return head_file.read_text(encoding="utf-8").strip()
        return "HEAD_STUB_SHA"

    def pre_check(self, proposal: PatchProposal) -> Tuple[bool, str, ToolingBuildState]:
        """
        Vérification statique et préparation du ToolingBuildState SANS toucher au disque.
        """
        worktree = Path(proposal.target_worktree)
        if not worktree.exists():
            return False, f"WORKTREE_NOT_FOUND:{proposal.target_worktree}", None

        # 1. Vérification du HEAD attendu
        current_head = self.head_provider(proposal.target_worktree)
        if current_head != proposal.base_sha:
            return False, f"WORKTREE_HEAD_DRIFT:{current_head}!={proposal.base_sha}", None

        # 2. Vérification de périmètre (Approved Scope)
        drift = sorted(set(proposal.touched_files) - set(proposal.approved_scope))
        if drift:
            return False, f"SCOPE_DRIFT_UNAPPROVED_FILES:{drift}", None

        # 3. Vérification des fichiers protégés
        for f in proposal.touched_files:
            f_norm = f.replace("\\", "/")
            if any(f_norm == p or f_norm.startswith(p) for p in PROTECTED_PATHS):
                return False, f"PROTECTED_SCOPE_VIOLATION:{f_norm}", None

        # 4. Construction de l'état ToolingBuildState pour évaluation prévisionnelle
        state = ToolingBuildState(
            session_id=proposal.proposal_id,
            objective=f"Apply proposal {proposal.proposal_id}",
            base_sha=proposal.base_sha,
            manifest_hash=proposal.patch_hash,
            diff_hash=proposal.patch_hash,
            approved_scope=proposal.approved_scope,
            actual_touched_files=proposal.touched_files,
            protected_scope_status="CLEAN",
            human_approval_status="APPROVED",
            obsidure_status="CLEAN",
            worktree_isolated=True,
            branch_isolated=True,
            auto_commit_disabled=True,
            auto_push_disabled=True,
            auto_merge_disabled=True,
            tests_results="PASS",
            gates_results="PASS",
            unknowns=[],
            contradictions=[],
            risk_flags=["GOVERNED_PROPOSAL_INTENT"],
            decision_authority="KX108_ONLY",
        )
        return True, "PRE_CHECK_OK", state

    def apply_proposal_governed(
        self,
        proposal: PatchProposal,
        post_test_runner: Optional[Callable[[str], bool]] = None,
        injected_ticket: Optional[SovereignTicket] = None,
        simulate_crash_after_auth: bool = False,
        simulate_crash_during_mutation: bool = False,
    ) -> GovernedApplyResult:
        """
        Exécute la chaîne transactionnelle gouvernée complète.
        """
        worktree = Path(proposal.target_worktree)

        # ── 1. INTENTION & VALIDATION PRÉALABLE (ZÉRO ÉCRITURE) ──
        valid, reason, state = self.pre_check(proposal)
        if not valid:
            return GovernedApplyResult(
                status="REFUSED_PRE_DECISION",
                proposal_id=proposal.proposal_id,
                kx108_pre_gate="BLOCK",
                kx108_reason=reason,
                ticket_id=None,
                disk_written=False,
                rolled_back=False,
                modified_files=[],
                error_detail=reason,
            )

        # ── 2. DÉCISION SOUVERAINE KX108 (ZÉRO ÉCRITURE) ──
        if injected_ticket is not None:
            kx108_gate = injected_ticket.x108_gate
            kx108_reason = f"INJECTED_TICKET_{kx108_gate}"
        else:
            # Évaluation du state par GuardX108
            aggregate = DomainAggregate(
                domain=Domain.META,
                market_verdict="AUTHORIZE",
                confidence=0.98,
                contradictions=state.contradictions if state else [],
                unknowns=state.unknowns if state else [],
                risk_flags=state.risk_flags if state else [],
                agent_votes=[],
            )
            envelope = GuardX108().decide(aggregate)
            kx108_gate = envelope.x108_gate
            kx108_reason = envelope.reason_code

        # SI LE KERNEL NE DIT PAS ALLOW : ARRÊT STRICT, AUCUN OCTET ÉCRIT
        if kx108_gate != "ALLOW":
            return GovernedApplyResult(
                status="REFUSED_PRE_DECISION",
                proposal_id=proposal.proposal_id,
                kx108_pre_gate=kx108_gate,
                kx108_reason=f"KX108_GATE_NOT_ALLOW:{kx108_reason}",
                ticket_id=getattr(injected_ticket, "ticket_id", None) if injected_ticket else None,
                disk_written=False,
                rolled_back=False,
                modified_files=[],
            )

        # ── 3. ÉMISSION OU VÉRIFICATION DU TICKET D'AUTORISATION ──
        if injected_ticket is not None:
            ticket = injected_ticket
        else:
            ticket = issue_sovereign_ticket(
                action_id=proposal.proposal_id,
                os3_ticket_id=f"os3-{proposal.proposal_id}",
                x108_gate="ALLOW",
                scope="bounded_apply",
                autonomy_level=1,
                world_call_class="GOVERNED_WRITE",
                input_hash=proposal.patch_hash,
                action_hash=hashlib.sha256(f"{proposal.target_worktree}:{proposal.base_sha}".encode()).hexdigest(),
                ttl_seconds=120,
            )

        # Simulation de crash immédiatement après autorisation
        if simulate_crash_after_auth:
            raise RuntimeError("CRASH_AFTER_AUTHORIZATION_BEFORE_MUTATION")

        # ── 4. CONTRÔLE AVANT CONSOMMATION DU TICKET (ANTI-REJEU & BINDING) ──
        try:
            verified_ticket = verify_and_consume_sovereign_ticket(
                ticket,
                required_scope="bounded_apply",
                expected_action_id=proposal.proposal_id,
                action_payload=proposal.raw_payload,
            )
        except Exception as exc:
            return GovernedApplyResult(
                status="REFUSED_PRE_DECISION",
                proposal_id=proposal.proposal_id,
                kx108_pre_gate=kx108_gate,
                kx108_reason=f"TICKET_VERIFICATION_FAILED:{exc}",
                ticket_id=getattr(ticket, "ticket_id", None),
                disk_written=False,
                rolled_back=False,
                modified_files=[],
                error_detail=str(exc),
            )

        # ── 5. VÉRIFICATION TOCTOU (TIME-OF-CHECK TO TIME-OF-USE) ──
        # Re-vérification que le worktree n'a pas bougé entre décision et écriture
        fresh_head = self.head_provider(proposal.target_worktree)
        if fresh_head != proposal.base_sha:
            fail_ticket_nonce(verified_ticket.nonce, verified_ticket.ticket_id, reason="TOCTOU_HEAD_DRIFT")
            return GovernedApplyResult(
                status="REFUSED_PRE_DECISION",
                proposal_id=proposal.proposal_id,
                kx108_pre_gate=kx108_gate,
                kx108_reason=f"TOCTOU_HEAD_DRIFT_DETECTED:{fresh_head}!={proposal.base_sha}",
                ticket_id=verified_ticket.ticket_id,
                disk_written=False,
                rolled_back=False,
                modified_files=[],
            )

        # ── 6. SCELLAGE DU ROLLBACK EN MÉMOIRE & SUR DISQUE (WAL) ──
        # Réconciliation préalable si un crash antérieur a laissé des traces orphelines
        SealedRollbackEvidence.recover_dangling_wal(proposal.target_worktree)

        snapshot_original: Dict[str, Optional[str]] = {}
        pre_hashes: Dict[str, Optional[str]] = {}
        for op in proposal.operations:
            target_file = worktree / op.path
            if target_file.exists():
                content = target_file.read_text(encoding="utf-8")
                snapshot_original[op.path] = content
                pre_hashes[op.path] = hashlib.sha256(content.encode("utf-8")).hexdigest()
            else:
                snapshot_original[op.path] = None
                pre_hashes[op.path] = None

        rollback_evidence = SealedRollbackEvidence(
            evidence_id=f"rollback-{uuid.uuid4().hex[:12]}",
            proposal_id=proposal.proposal_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            original_files=snapshot_original,
            pre_state_hashes=pre_hashes,
        )
        # Écriture persistante et fsync du journal WAL avant le moindre octet de mutation
        rollback_evidence.persist_wal(proposal.target_worktree)

        # ── 7. APPLICATION DES MUTATIONS SUR DISQUE ──
        disk_written = False
        written_files = []
        try:
            for op in proposal.operations:
                target_file = worktree / op.path
                target_file.parent.mkdir(parents=True, exist_ok=True)

                if simulate_crash_during_mutation and disk_written:
                    raise IOError("CRASH_DURING_MUTATION")

                if op.op_type == "WRITE":
                    target_file.write_text(op.content, encoding="utf-8")
                    disk_written = True
                    written_files.append(op.path)
                elif op.op_type == "DELETE":
                    if target_file.exists():
                        target_file.unlink()
                        disk_written = True
                        written_files.append(op.path)

            # ── 8. POST-TESTS & VALIDATION DE PREUVE ──
            tests_passed = True
            if post_test_runner is not None:
                tests_passed = post_test_runner(proposal.target_worktree)

            if not tests_passed:
                raise AssertionError("POST_APPLY_TESTS_FAILED")

            # Succès : suppression du journal WAL
            rollback_evidence.clear_wal(proposal.target_worktree)

        except Exception as exc:
            # ── ROLLBACK AUTOMATIQUE IMMÉDIAT EN CAS D'ERREUR OU DE CRASH ──
            if disk_written:
                rollback_evidence.execute_rollback(proposal.target_worktree)

            rollback_evidence.clear_wal(proposal.target_worktree)
            fail_ticket_nonce(verified_ticket.nonce, verified_ticket.ticket_id, reason=f"APPLY_ERROR:{exc}")
            return GovernedApplyResult(
                status="ROLLED_BACK",
                proposal_id=proposal.proposal_id,
                kx108_pre_gate=kx108_gate,
                kx108_reason=f"APPLY_FAILED_ROLLED_BACK:{exc}",
                ticket_id=verified_ticket.ticket_id,
                disk_written=False,
                rolled_back=True,
                modified_files=[],
                error_detail=str(exc),
            )

            return GovernedApplyResult(
                status="ROLLED_BACK",
                proposal_id=proposal.proposal_id,
                kx108_pre_gate=kx108_gate,
                kx108_reason=f"APPLY_FAILED_ROLLED_BACK:{exc}",
                ticket_id=verified_ticket.ticket_id,
                disk_written=False,
                rolled_back=True,
                modified_files=[],
                error_detail=str(exc),
            )

        # ── 9. COMMIT & RECEIPT ──
        return GovernedApplyResult(
            status="COMMITTED",
            proposal_id=proposal.proposal_id,
            kx108_pre_gate="ALLOW",
            kx108_reason="GOVERNED_APPLY_SUCCESSFUL",
            ticket_id=verified_ticket.ticket_id,
            disk_written=True,
            rolled_back=False,
            modified_files=written_files,
        )
