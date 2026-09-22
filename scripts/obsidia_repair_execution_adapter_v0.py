"""
obsidia_repair_execution_adapter_v0.py
======================================
REPAIR_EXECUTION_ADAPTER_V0

Adaptateur READ-ONLY reliant un RepairVerdict/handoff Obsidure v?rifi?
au rail canonique d'ex?cution.

Cha?ne :

    verified repair handoff
    -> exact execution-worktree target precondition
    -> register_filesystem_source()
    -> BatchProposal
    -> canonical TestContract
    -> canonical PreExecutionContext
    -> prepare_execution()
    -> exact ChildExecutionRecord + execution_authority_hash

STOP avant HumanApproval / KX108_PRE / mutation.

decision_authority = KX108_ONLY
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from typing import Optional

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import obsidia_branching_ledger as _L
import obsidia_batch_selector as _S
import obsidia_batch_execution as _E
import obsidia_pre_execution_context as _PEC
import obsidia_test_contract as _TC


STATUS_EXEC_READY = "PREPARED_AWAITING_HUMAN_APPROVAL"
STATUS_PREP_HOLD = "PREP_HOLD"

DECISION_AUTHORITY = "KX108_ONLY"
OPERATION_TYPE = "UPDATE_TARGET_FROM_SOURCE"

_HEX40_OR_64 = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _prep_hold(reason: str, **extra) -> dict:
    return {
        "status": STATUS_PREP_HOLD,
        "reason": reason,
        "authority": "NON_SOVEREIGN",
        "decision_authority": DECISION_AUTHORITY,
        "write_capability": False,
        "target_mutated": False,
        "kx108_invoked": False,
        "human_approval_present": False,
        **extra,
    }


def _is_full_sha256(value) -> bool:
    return isinstance(value, str) and bool(_HEX64.fullmatch(value))


def _is_git_commit_sha(value) -> bool:
    return isinstance(value, str) and bool(_HEX40_OR_64.fullmatch(value))


def _resolve_target(exec_root: Path, target_path: str):
    rel = Path(str(target_path).replace("\\", "/"))

    if rel.is_absolute():
        return None, "TARGET_PATH_MUST_BE_RELATIVE"

    lexical = exec_root / rel

    try:
        if lexical.is_symlink():
            return None, "TARGET_IS_SYMLINK"

        resolved = lexical.resolve()
        resolved.relative_to(exec_root)
    except (OSError, ValueError):
        return None, "TARGET_PATH_ESCAPES_EXECUTION_WORKTREE"

    if not resolved.exists():
        return None, "TARGET_MISSING_IN_EXECUTION_WORKTREE"

    if not resolved.is_file():
        return None, "TARGET_NOT_REGULAR_FILE"

    return resolved, None



def prepare_repair_verdict_in_work_unit(
    *,
    request,
    proposal,
    c278_evidence,
    verdict,
    work_unit,
    repository_identity: Optional[str] = None,
    test_checks: Optional[list[dict]] = None,
    ledger_dir: Optional[Path] = None,
    selector_dir: Optional[Path] = None,
    execution_dir: Optional[Path] = None,
    pre_execution_context_dir: Optional[Path] = None,
) -> dict:
    """
    Pont execution-side strict :

        RepairRequest
        + RepairProposal
        + C278 CONTINUOUS
        + RepairVerdict PASS
        + IsolatedWorkUnit explicite
        -> repair handoff mat?riel
        -> prepare_repair_governed_execution()
        -> PEC / Child PLANNED / EAH
        -> STOP avant HumanApproval / KX108 / mutation.

    Ce wrapper :
      - ne cr?e PAS de worktree ;
      - ne d?couvre PAS HEAD / branche / base implicitement ;
      - ne duplique PAS la validation Git du PEC ;
      - ne cr?e PAS HumanApproval ;
      - n'invoque PAS KX108 ;
      - ne mute PAS la cible.

    IsolatedWorkUnit est seulement la poign?e de contexte fournie
    explicitement par l'appelant. Les faits Git restent rev?rifi?s par
    le rail canonique R3A / PreExecutionContext.
    """

    import obsidia_isolated_work_unit_v0 as _WU

    from periphery.agents.obsidure_repair_execution_handoff import (
        STATUS_READY as _HANDOFF_READY,
        build_repair_execution_handoff,
    )

    if not isinstance(work_unit, _WU.IsolatedWorkUnit):
        return _prep_hold(
            "WORK_UNIT_HANDLE_REQUIRED",
        )

    handoff = build_repair_execution_handoff(
        request=request,
        proposal=proposal,
        c278_evidence=c278_evidence,
        verdict=verdict,

        # IMPORTANT:
        # la pr?condition mat?rielle est observ?e sur LA cible du vrai
        # worktree d'ex?cution, pas sur REPO_ROOT ni sur le main worktree.
        repo_root=Path(work_unit.worktree_path),
    )

    if not isinstance(handoff, dict):
        return _prep_hold(
            "REPAIR_HANDOFF_MALFORMED",
            work_unit_id=work_unit.work_unit_id,
        )

    if handoff.get("status") != _HANDOFF_READY:
        return _prep_hold(
            "REPAIR_HANDOFF_NOT_READY",
            work_unit_id=work_unit.work_unit_id,
            handoff_status=handoff.get("status"),
            handoff_reason=handoff.get("reason"),
        )

    result = prepare_repair_governed_execution(
        handoff=handoff,

        # Aucun contexte Git fabriqu? ici :
        # les quatre coordonn?es viennent de la poign?e canonique.
        execution_worktree_path=work_unit.worktree_path,
        main_worktree_path=work_unit.main_worktree_path,
        branch_name=work_unit.branch_name,
        base_sha=work_unit.base_sha,

        repository_identity=repository_identity,
        test_checks=test_checks,
        ledger_dir=ledger_dir,
        selector_dir=selector_dir,
        execution_dir=execution_dir,
        pre_execution_context_dir=pre_execution_context_dir,
    )

    out = dict(result)

    # Provenance de raccord uniquement.
    # Aucune nouvelle autorit?.
    out["work_unit_id"] = work_unit.work_unit_id
    out["repair_handoff_status"] = handoff.get("status")
    out["repair_request_id"] = handoff.get("request_id")
    out["repair_proposal_id"] = handoff.get("proposal_id")
    out["repair_verdict_id"] = handoff.get("verdict_id")
    out["repair_source_content_sha256"] = handoff.get(
        "source_content_sha256"
    )

    return out


def prepare_repair_runtime_snapshot_in_work_unit(
    *,
    snapshot,
    work_unit,
    repository_identity: Optional[str] = None,
    test_checks: Optional[list[dict]] = None,
    ledger_dir: Optional[Path] = None,
    selector_dir: Optional[Path] = None,
    execution_dir: Optional[Path] = None,
    pre_execution_context_dir: Optional[Path] = None,
) -> dict:
    """
    Execution-side ingress for the readonly Obsidure repair snapshot.

    Expected transport:

        RepairRequest
        + RepairProposal
        + C278 PROPOSAL_MEANING
        + RepairVerdict
        + explicit IsolatedWorkUnit
        -> prepare_repair_verdict_in_work_unit()
        -> canonical governed PREPARE rail
        -> EAH
        -> STOP.

    This function does NOT:
      - create or discover a worktree;
      - discover HEAD / branch / base;
      - re-run reasoning, C278, or sandbox;
      - create HumanApproval;
      - invoke KX108;
      - mutate a target.

    It validates only the readonly snapshot envelope and delegates
    repair provenance/material validation to the existing R3D seam.
    """

    if not isinstance(snapshot, dict):
        return _prep_hold(
            "REPAIR_RUNTIME_SNAPSHOT_REQUIRED",
        )

    if snapshot.get("status") != "REPAIR_RUNTIME_EVIDENCE_SNAPSHOT":
        return _prep_hold(
            "REPAIR_RUNTIME_SNAPSHOT_STATUS_INVALID",
            snapshot_status=snapshot.get("status"),
        )

    expected_boundary = {
        "readonly": True,
        "authority": "NON_SOVEREIGN",
        "decision_authority": DECISION_AUTHORITY,
        "execution_authority": False,
        "work_unit_bound": False,
        "human_approval_present": False,
        "kx108_invoked": False,
        "target_mutated": False,
    }

    for field, expected in expected_boundary.items():
        actual = snapshot.get(field)

        # bools are checked by identity so 0/1 are not accepted as
        # authority-boundary substitutes.
        if isinstance(expected, bool):
            ok = actual is expected
        else:
            ok = actual == expected

        if not ok:
            return _prep_hold(
                "REPAIR_RUNTIME_SNAPSHOT_BOUNDARY_INVALID",
                field=field,
                expected=expected,
                actual=actual,
            )

    # Execution context MUST enter through the explicit work_unit
    # argument, never be smuggled inside the Obsidure snapshot.
    forbidden_execution_context = {
        "work_unit",
        "execution_worktree_path",
        "main_worktree_path",
        "branch_name",
        "base_sha",
        "execution_authority_hash",
        "human_authorization_reference",
    }

    embedded = sorted(
        key
        for key in forbidden_execution_context
        if key in snapshot
    )

    if embedded:
        return _prep_hold(
            "REPAIR_RUNTIME_SNAPSHOT_CONTAINS_EXECUTION_CONTEXT",
            forbidden_fields=embedded,
        )

    artifacts = {}

    for name in (
        "request",
        "proposal",
        "c278_evidence",
        "verdict",
    ):
        value = snapshot.get(name)

        if not isinstance(value, dict):
            return _prep_hold(
                "REPAIR_RUNTIME_SNAPSHOT_ARTIFACT_MISSING_OR_MALFORMED",
                artifact=name,
            )

        artifacts[name] = value

    # R3D remains the sole repair-material/work-unit seam.
    # It rechecks C278, request/proposal/verdict IDs, PASS status,
    # tested sandbox SHA, target drift, and canonical work-unit context.
    return prepare_repair_verdict_in_work_unit(
        request=artifacts["request"],
        proposal=artifacts["proposal"],
        c278_evidence=artifacts["c278_evidence"],
        verdict=artifacts["verdict"],
        work_unit=work_unit,
        repository_identity=repository_identity,
        test_checks=test_checks,
        ledger_dir=ledger_dir,
        selector_dir=selector_dir,
        execution_dir=execution_dir,
        pre_execution_context_dir=pre_execution_context_dir,
    )

def prepare_repair_governed_execution(
    *,
    handoff: dict,
    execution_worktree_path: "str | Path | None" = None,
    main_worktree_path: "str | Path | None" = None,
    branch_name: str = "",
    base_sha: str = "",
    repository_identity: Optional[str] = None,
    test_checks: Optional[list[dict]] = None,
    ledger_dir: Optional[Path] = None,
    selector_dir: Optional[Path] = None,
    execution_dir: Optional[Path] = None,
    pre_execution_context_dir: Optional[Path] = None,
) -> dict:
    """
    Pr?pare l'autorit? exacte d'ex?cution pour un artefact sandbox Obsidure.

    Ne cr?e aucune HumanApproval.
    N'invoque jamais KX108.
    Ne mute jamais la cible.
    """

    from periphery.agents.obsidure_repair_execution_handoff import (
        STATUS_READY as _HANDOFF_READY,
    )

    # ------------------------------------------------------------
    # 0. Handoff strict
    # ------------------------------------------------------------

    if not isinstance(handoff, dict):
        return _prep_hold("HANDOFF_MALFORMED")

    if handoff.get("status") != _HANDOFF_READY:
        return _prep_hold(
            "HANDOFF_NOT_READY",
            handoff_status=handoff.get("status"),
        )

    sandbox_artifact_path = handoff.get("sandbox_artifact_path")
    target_path = handoff.get("target_path")
    handoff_sha256 = handoff.get("source_content_sha256")
    handoff_target_pre_sha256 = handoff.get("target_pre_sha256")
    operation_reason = handoff.get("operation_reason") or ""
    provenance_refs = dict(handoff.get("provenance_refs") or {})

    if not sandbox_artifact_path:
        return _prep_hold("SANDBOX_ARTIFACT_PATH_ABSENT")

    if not target_path:
        return _prep_hold("TARGET_PATH_ABSENT")

    if not _is_full_sha256(handoff_sha256):
        return _prep_hold("HANDOFF_SHA256_INVALID")

    # R3A = REPLACE/UPDATE route only.
    # CREATE requires its own explicitly governed precondition semantics.
    if not _is_full_sha256(handoff_target_pre_sha256):
        return _prep_hold("TARGET_PRE_SHA256_REQUIRED_REPLACE_ONLY")

    if handoff.get("operation_type") != OPERATION_TYPE:
        return _prep_hold(
            "HANDOFF_OPERATION_UNSUPPORTED",
            operation_type=handoff.get("operation_type"),
        )

    if provenance_refs.get("operation_type") != OPERATION_TYPE:
        return _prep_hold(
            "PROVENANCE_OPERATION_MISMATCH",
            operation_type=provenance_refs.get("operation_type"),
        )

    # ------------------------------------------------------------
    # 1. Vrai execution worktree + pr?condition cible
    # ------------------------------------------------------------

    if execution_worktree_path is None:
        return _prep_hold("EXECUTION_WORKTREE_PATH_ABSENT")

    if main_worktree_path is None:
        return _prep_hold("MAIN_WORKTREE_PATH_ABSENT")

    if not branch_name:
        return _prep_hold("BRANCH_NAME_ABSENT")

    if not _is_git_commit_sha(base_sha):
        return _prep_hold("BASE_SHA_NOT_GIT_COMMIT_SHA")

    exec_root = Path(execution_worktree_path).resolve()
    main_root = Path(main_worktree_path).resolve()

    if not exec_root.exists() or not exec_root.is_dir():
        return _prep_hold("EXECUTION_WORKTREE_NOT_DIRECTORY")

    if not main_root.exists() or not main_root.is_dir():
        return _prep_hold("MAIN_WORKTREE_NOT_DIRECTORY")

    target_abs, target_error = _resolve_target(exec_root, target_path)
    if target_error:
        return _prep_hold(target_error, target_path=target_path)

    try:
        target_pre_sha256 = hashlib.sha256(target_abs.read_bytes()).hexdigest()
    except OSError as exc:
        return _prep_hold(f"TARGET_UNREADABLE:{exc}")

    # Le handoff avait d?j? observ? la pr?condition.
    # Toute mutation entre handoff et PREPARE ferme le rail.
    if target_pre_sha256 != handoff_target_pre_sha256:
        return _prep_hold(
            "TARGET_PRECONDITION_DRIFT_AFTER_HANDOFF",
            expected=handoff_target_pre_sha256,
            actual=target_pre_sha256,
        )

    if target_pre_sha256 == handoff_sha256:
        return _prep_hold("NO_OP_TARGET_ALREADY_EQUALS_SOURCE")

    # ------------------------------------------------------------
    # 2. Source filesystem exacte -> Ledger
    # ------------------------------------------------------------

    sandbox_abs = Path(sandbox_artifact_path)

    # L'identit? de source est le sandbox contenant r?ellement l'artefact,
    # pas le d?p?t cible.
    source_repository_identity = str(sandbox_abs.resolve().parent)

    reg = _L.register_filesystem_source(
        source_path=sandbox_artifact_path,
        target_path=target_path,
        reason=operation_reason,
        provenance_refs=provenance_refs,
        expected_content_sha256=handoff_sha256,
        repo_root=Path(source_repository_identity),
        ledger_dir=ledger_dir,
    )

    if reg.get("status") not in ("DISCOVERED", "ALREADY_REGISTERED"):
        return _prep_hold(
            "LEDGER_REGISTRATION_FAILED",
            reason_detail=reg.get("reason"),
            ledger_result=reg,
        )

    entry_id = reg.get("ledger_entry_id")
    ledger_sha256 = reg.get("source_content_sha256")
    ledger_source_path = reg.get("source_path")
    ledger_source_kind = reg.get("source_kind")
    ledger_source_repository_identity = reg.get("source_repository_identity")

    if not entry_id:
        return _prep_hold("LEDGER_ENTRY_ID_ABSENT")

    if ledger_sha256 != handoff_sha256:
        return _prep_hold(
            "SHA256_TRIPLE_ASSERT_FAILED",
            handoff=handoff_sha256,
            ledger=ledger_sha256,
        )

    if ledger_source_kind != _L.SOURCE_KIND_FILESYSTEM:
        return _prep_hold(
            "LEDGER_SOURCE_KIND_MISMATCH",
            source_kind=ledger_source_kind,
        )

    if not ledger_source_path:
        return _prep_hold("LEDGER_SOURCE_PATH_ABSENT")

    if not ledger_source_repository_identity:
        return _prep_hold("LEDGER_SOURCE_REPOSITORY_IDENTITY_ABSENT")

    # ------------------------------------------------------------
    # 3. BatchProposal canonique ? exactement 1 candidat
    # ------------------------------------------------------------

    batch = _S.propose_batch(
        objective=operation_reason or f"repair: {target_path}",
        candidate_entry_ids=[entry_id],
        ledger_dir=ledger_dir,
        selector_dir=selector_dir,
    )

    if (
        batch.get("status") != _S.BATCH_PROPOSED
        or int(batch.get("selected_count") or 0) != 1
    ):
        return _prep_hold(
            "BATCH_PROPOSAL_NOT_SINGLE_READY",
            batch_status=batch.get("status"),
            selected_count=batch.get("selected_count"),
            hold_count=batch.get("hold_count"),
            scope_error=batch.get("scope_error"),
        )

    batch_id = batch.get("batch_id")
    if not batch_id:
        return _prep_hold("BATCH_ID_ABSENT")

    # ------------------------------------------------------------
    # 4. TestContract canonique
    # ------------------------------------------------------------

    if test_checks is None:
        test_checks = []

    if not isinstance(test_checks, list) or any(
        not isinstance(check, dict) for check in test_checks
    ):
        return _prep_hold("TEST_CHECKS_MALFORMED")

    # Toujours lier la postcondition mat?rielle minimale :
    # apr?s apply, la cible doit ?tre EXACTEMENT les octets sandbox gouvern?s.
    target_postcondition_check = _TC.build_check(
        check_id="repair-target-postcondition-sha256",
        check_type=_TC.CHECK_TYPE_TARGET_SHA256,
        required=True,
        target_path=target_path,
        expected_target_sha256=handoff_sha256,
    )

    exact_checks = [target_postcondition_check, *test_checks]

    contract_seed = (
        f"{entry_id}:{batch_id}:{target_path}:{handoff_sha256}"
    )
    contract_id = (
        "repair-tc-"
        + hashlib.sha256(contract_seed.encode("utf-8")).hexdigest()[:24]
    )

    test_contract = _TC.build_test_contract(
        contract_id=contract_id,
        candidate_entry_id=entry_id,
        batch_id=batch_id,
        target_path=target_path,
        checks=exact_checks,
    )

    test_contract_hash = _TC.compute_test_contract_hash(test_contract)

    if not _is_full_sha256(test_contract_hash):
        return _prep_hold("TEST_CONTRACT_HASH_INVALID")

    # ------------------------------------------------------------
    # 5. PreExecutionContext canonique
    # ------------------------------------------------------------

    repo_ident = repository_identity or str(exec_root)

    pec = _PEC.create_pre_execution_context(
        execution_worktree_path=exec_root,
        branch_name=branch_name,
        base_sha=base_sha,
        main_worktree_path=main_root,
        repository_identity=repo_ident,
        target_path=target_path,
        target_pre_sha256=target_pre_sha256,
        source_kind=_L.SOURCE_KIND_FILESYSTEM,
        source_repository_identity=ledger_source_repository_identity,
        # Non applicable pour une source filesystem.
        # Valeurs explicitement vides plut?t qu'une identit? Git fabriqu?e.
        source_commit="",
        source_blob_sha="",
        source_path=ledger_source_path,
        source_sha256=ledger_sha256,
        operation=OPERATION_TYPE,
        approved_scope=[target_path],
        protected_scope_status="CLEAN",
        test_contract_hash=test_contract_hash,
        store_dir=pre_execution_context_dir,
    )

    if not pec.get("verify_ok") or not pec.get("context_id"):
        return _prep_hold(
            "PRE_EXECUTION_CONTEXT_NOT_VERIFIED",
            pec_status=pec.get("status"),
            pec_reason=pec.get("reason") or pec.get("verify_reason"),
        )

    context_id = pec["context_id"]
    context_record_hash = (pec.get("record") or {}).get(
        "context_record_hash"
    )

    if not context_record_hash:
        return _prep_hold("PRE_EXECUTION_CONTEXT_RECORD_HASH_ABSENT")

    # ------------------------------------------------------------
    # 6. ExecutionEnvelope canonique
    # ------------------------------------------------------------

    envelope = _E.prepare_execution(
        batch_id=batch_id,
        ledger_dir=ledger_dir,
        selector_dir=selector_dir,
        execution_dir=execution_dir,
        repo_root=exec_root,
        test_contract=test_contract,
        pre_execution_context={
            "context_id": context_id,
            "context_record_hash": context_record_hash,
        },
        pre_execution_context_dir=pre_execution_context_dir,
    )

    if not envelope.get("integrity_verified"):
        return _prep_hold(
            "EXECUTION_ENVELOPE_NOT_INTEGRITY_VERIFIED",
            integrity_error=envelope.get("integrity_error"),
            aggregate_status=envelope.get("aggregate_status"),
        )

    eah = envelope.get("execution_authority_hash")
    recomputed_eah = _E.compute_execution_authority_hash(envelope)

    if not _is_full_sha256(eah):
        return _prep_hold("EAH_MALFORMED")

    if recomputed_eah != eah:
        return _prep_hold("EXECUTION_AUTHORITY_HASH_DRIFT_AT_PREPARE")

    children = envelope.get("children") or []
    if len(children) != 1:
        return _prep_hold(
            "UNEXPECTED_CHILD_COUNT",
            child_count=len(children),
        )

    child = children[0]

    if child.get("execution_status") != _E.PLANNED:
        return _prep_hold(
            "CHILD_NOT_PLANNED",
            execution_status=child.get("execution_status"),
            materiality_status=child.get("materiality_status"),
        )

    if child.get("operation_type") != OPERATION_TYPE:
        return _prep_hold(
            "CHILD_OPERATION_MISMATCH",
            operation_type=child.get("operation_type"),
        )

    if child.get("source_kind") != _L.SOURCE_KIND_FILESYSTEM:
        return _prep_hold(
            "CHILD_SOURCE_KIND_MISMATCH",
            source_kind=child.get("source_kind"),
        )

    if child.get("source_content_sha256") != handoff_sha256:
        return _prep_hold("CHILD_SOURCE_SHA256_MISMATCH")

    if child.get("target_pre_sha256") != target_pre_sha256:
        return _prep_hold("CHILD_TARGET_PRE_SHA256_MISMATCH")

    if child.get("target_path") != target_path:
        return _prep_hold("CHILD_TARGET_PATH_MISMATCH")

    if child.get("source_path") != ledger_source_path:
        return _prep_hold("CHILD_SOURCE_PATH_MISMATCH")

    if envelope.get("pre_execution_context_id") != context_id:
        return _prep_hold("ENVELOPE_PEC_ID_MISMATCH")

    if (
        envelope.get("pre_execution_context_record_hash")
        != context_record_hash
    ):
        return _prep_hold("ENVELOPE_PEC_HASH_MISMATCH")

    if envelope.get("test_contract_hash") != test_contract_hash:
        return _prep_hold("ENVELOPE_TEST_CONTRACT_HASH_MISMATCH")

    # ------------------------------------------------------------
    # 7. PREPARED ? aucune autorit? consomm?e
    # ------------------------------------------------------------

    return {
        "status": STATUS_EXEC_READY,
        "reason": None,
        "authority": "NON_SOVEREIGN",
        "decision_authority": DECISION_AUTHORITY,
        "write_capability": False,
        "target_mutated": False,
        "human_approval_required": True,
        "human_approval_present": False,
        "kx108_required": True,
        "kx108_invoked": False,

        "batch_id": batch_id,
        "batch_execution_id": envelope.get("batch_execution_id"),
        "child_execution_id": child.get("child_execution_id"),
        "ledger_entry_id": entry_id,

        "execution_authority_hash": eah,

        "pre_execution_context_id": context_id,
        "pre_execution_context_record_hash": context_record_hash,

        "test_contract": test_contract,
        "test_contract_hash": test_contract_hash,

        "target_path": target_path,
        "target_pre_sha256": target_pre_sha256,

        "source_kind": child.get("source_kind"),
        "source_path": child.get("source_path"),
        "source_content_sha256": handoff_sha256,
        "ledger_source_content_sha256": ledger_sha256,
        "sha256_triple_assert": "PASS",

        "provenance_refs": provenance_refs,

        "next_required_action": (
            "HUMAN_REVIEW_EXACT_EXECUTION_AUTHORITY_HASH"
        ),
    }


__all__ = [
    "STATUS_EXEC_READY",
    "STATUS_PREP_HOLD",
    "prepare_repair_governed_execution",
]
