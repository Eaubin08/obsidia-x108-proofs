#!/usr/bin/env python3
"""
J5 Jarvis -> governed mutation seam V0.

This module owns no execution authority and implements no mutation primitive.

PREPARE:
    verified J3 cognitive proposal
    -> existing governed execution driver PREPARE
    -> reveal exact EAH
    -> STOP before human approval / KX108 / mutation.

EXECUTE:
    explicit human-authorized exact EAH + human reference
    -> existing governed execution driver EXECUTE.

The driver remains owner of:
- HumanApproval persistence,
- KX108_PRE,
- governed content apply,
- sealed rollback evidence,
- sealed apply receipt,
- KX108_POST,
- rollback / disposition.

Jarvis is never authority.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import obsidia_cognitive_governed_runtime_handoff_v0 as J3
import obsidia_governed_execution_driver_v0 as DRV


SCHEMA_VERSION = 1
DOMAIN_TAG = "OBSIDIA_J5_JARVIS_GOVERNED_MUTATION_SEAM_V0"

DECISION_AUTHORITY = "KX108_ONLY"
JARVIS_AUTHORITY = "NONE"

CAPABILITY_ID = "GOVERNED_UPDATE_TARGET_FROM_SOURCE"
ACTION_TYPE = "UPDATE_TARGET_FROM_SOURCE"

PREPARE_PHASE = "PREPARE"
EXECUTE_PHASE = "EXECUTE"

_REQUIRED_PAYLOAD_FIELDS = frozenset(
    {
        "source_git_commit",
        "source_historical_path",
        "target_path",
        "test_contract",
    }
)

_ALLOWED_PAYLOAD_FIELDS = frozenset(
    {
        *_REQUIRED_PAYLOAD_FIELDS,
        "objective",
    }
)

# Runtime / authority locations must never come from cognition.
_FORBIDDEN_COGNITIVE_RUNTIME_FIELDS = frozenset(
    {
        "execution_worktree_path",
        "main_worktree_path",
        "ledger_dir",
        "selector_dir",
        "execution_dir",
        "pre_execution_context_dir",
        "kx108_pre_decision_dir",
        "kx108_post_decision_dir",
        "test_contract_results_dir",
        "sealed_receipt_dir",
        "sealed_rollback_evidence_dir",
        "rollback_result_dir",
        "approval_dir",
        "mission_store_dir",
        "human_authorized_execution_authority_hash",
        "human_authorization_reference",
        "authority_mode",
    }
)


class JarvisGovernedMutationSeamError(ValueError):
    pass


def _require_text(name: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise JarvisGovernedMutationSeamError(
            f"{name.upper()}_REQUIRED"
        )
    return value.strip()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _verify_proposal(
    proposal: dict[str, Any],
) -> dict[str, Any]:
    ok, reason = J3.verify_cognitive_governed_handoff(
        proposal
    )

    if not ok:
        raise JarvisGovernedMutationSeamError(
            f"J3_PROPOSAL_INVALID:{reason}"
        )

    if proposal.get("capability") != CAPABILITY_ID:
        raise JarvisGovernedMutationSeamError(
            "CAPABILITY_NOT_ALLOWED"
        )

    if proposal.get("action_type") != ACTION_TYPE:
        raise JarvisGovernedMutationSeamError(
            "ACTION_TYPE_NOT_ALLOWED"
        )

    if proposal.get("irreversible") is not False:
        raise JarvisGovernedMutationSeamError(
            "IRREVERSIBLE_ACTION_NOT_ALLOWED_V0"
        )

    payload = proposal.get("payload")

    if not isinstance(payload, dict):
        raise JarvisGovernedMutationSeamError(
            "PAYLOAD_MUST_BE_DICT"
        )

    keys = set(payload)

    forbidden = keys & _FORBIDDEN_COGNITIVE_RUNTIME_FIELDS
    if forbidden:
        raise JarvisGovernedMutationSeamError(
            "COGNITIVE_RUNTIME_AUTHORITY_FIELDS_FORBIDDEN:"
            + ",".join(sorted(forbidden))
        )

    unknown = keys - _ALLOWED_PAYLOAD_FIELDS
    if unknown:
        raise JarvisGovernedMutationSeamError(
            "PAYLOAD_SCOPE_NOT_ALLOWED:"
            + ",".join(sorted(unknown))
        )

    missing = _REQUIRED_PAYLOAD_FIELDS - keys
    if missing:
        raise JarvisGovernedMutationSeamError(
            "PAYLOAD_FIELDS_REQUIRED:"
            + ",".join(sorted(missing))
        )

    for field in (
        "source_git_commit",
        "source_historical_path",
        "target_path",
    ):
        _require_text(field, payload.get(field))

    if not isinstance(payload.get("test_contract"), dict):
        raise JarvisGovernedMutationSeamError(
            "TEST_CONTRACT_REQUIRED"
        )

    return payload


def prepare_jarvis_governed_mutation(
    proposal: dict[str, Any],
    *,
    execution_worktree_path: str | Path,
    main_worktree_path: str | Path,
    branch_name: str,
    base_sha: str,
    ledger_dir: str | Path,
    selector_dir: str | Path,
    execution_dir: str | Path,
    pre_execution_context_dir: str | Path,
    repository_identity: str | None = None,
) -> dict[str, Any]:
    """
    Prepare only.

    No HumanApproval.
    No KX108 invocation.
    No target mutation.
    No execution authorization.
    """
    payload = _verify_proposal(proposal)

    exec_root = Path(
        execution_worktree_path
    ).resolve()

    target_rel = payload["target_path"]
    target_abs = (
        exec_root
        / target_rel.replace("\\", "/")
    ).resolve()

    if not target_abs.exists() or not target_abs.is_file():
        raise JarvisGovernedMutationSeamError(
            "TARGET_NOT_AVAILABLE_FOR_PREPARE"
        )

    before = target_abs.read_bytes()
    before_sha = _sha256(before)

    driver = DRV.prepare_governed_execution(
        source_git_commit=payload[
            "source_git_commit"
        ],
        source_historical_path=payload[
            "source_historical_path"
        ],
        target_path=target_rel,
        test_contract=payload["test_contract"],
        execution_worktree_path=exec_root,
        main_worktree_path=Path(
            main_worktree_path
        ).resolve(),
        branch_name=_require_text(
            "branch_name",
            branch_name,
        ),
        base_sha=_require_text(
            "base_sha",
            base_sha,
        ),
        repository_identity=(
            repository_identity
            if repository_identity is not None
            else str(exec_root)
        ),
        objective=str(
            payload.get("objective") or ""
        ),
        ledger_dir=Path(ledger_dir),
        selector_dir=Path(selector_dir),
        execution_dir=Path(execution_dir),
        pre_execution_context_dir=Path(
            pre_execution_context_dir
        ),
    )

    after = target_abs.read_bytes()
    after_sha = _sha256(after)

    if before_sha != after_sha or before != after:
        raise JarvisGovernedMutationSeamError(
            "PREPARE_MUTATED_TARGET"
        )

    # Successful PREPARE must preserve the driver's
    # own non-authority invariants.
    if (
        driver.get("status")
        == DRV.PREPARED_AWAITING_HUMAN_APPROVAL
    ):
        if driver.get("target_mutated") is not False:
            raise JarvisGovernedMutationSeamError(
                "DRIVER_PREPARE_TARGET_MUTATION_FLAG"
            )

        if driver.get("kx108_invocations") != 0:
            raise JarvisGovernedMutationSeamError(
                "DRIVER_PREPARE_KX108_INVOCATION"
            )

        if (
            driver.get("human_approval_created")
            is not False
        ):
            raise JarvisGovernedMutationSeamError(
                "DRIVER_PREPARE_CREATED_HUMAN_APPROVAL"
            )

        if (
            driver.get("decision_authority")
            != DECISION_AUTHORITY
        ):
            raise JarvisGovernedMutationSeamError(
                "DRIVER_DECISION_AUTHORITY_INVALID"
            )

    out = dict(driver)

    out.update(
        {
            "j5_schema_version": SCHEMA_VERSION,
            "j5_domain_tag": DOMAIN_TAG,
            "j5_phase": PREPARE_PHASE,
            "j5_capability": CAPABILITY_ID,
            "j5_action_type": ACTION_TYPE,
            "j5_plan_hash": proposal["plan_hash"],
            "jarvis_authority": JARVIS_AUTHORITY,
            "decision_authority": DECISION_AUTHORITY,
            "execution_authorization": False,
            "human_authorization_consumed": False,
            "j5_target_pre_sha256": before_sha,
            "j5_target_post_prepare_sha256": after_sha,
        }
    )

    return out


def execute_jarvis_governed_mutation(
    prepared: dict[str, Any],
    *,
    human_authorized_execution_authority_hash: str,
    human_authorization_reference: str,
    execution_dir: str | Path,
    pre_execution_context_dir: str | Path,
    selector_dir: str | Path,
    ledger_dir: str | Path,
    kx108_pre_decision_dir: str | Path,
    kx108_post_decision_dir: str | Path,
    test_contract_results_dir: str | Path,
    sealed_receipt_dir: str | Path,
    sealed_rollback_evidence_dir: str | Path,
    rollback_result_dir: str | Path,
    repo_root: str | Path,
    approval_dir: str | Path | None = None,
) -> dict[str, Any]:
    """
    Explicit second phase.

    This function cannot manufacture or infer human
    authorization. The exact EAH revealed by PREPARE
    must be supplied again by the caller.
    """
    if not isinstance(prepared, dict):
        raise JarvisGovernedMutationSeamError(
            "PREPARED_RESULT_REQUIRED"
        )

    if prepared.get("j5_phase") != PREPARE_PHASE:
        raise JarvisGovernedMutationSeamError(
            "J5_PREPARE_PHASE_REQUIRED"
        )

    if (
        prepared.get("status")
        != DRV.PREPARED_AWAITING_HUMAN_APPROVAL
    ):
        raise JarvisGovernedMutationSeamError(
            "PREPARED_AWAITING_HUMAN_APPROVAL_REQUIRED"
        )

    expected_eah = _require_text(
        "execution_authority_hash",
        prepared.get("execution_authority_hash"),
    )

    supplied_eah = _require_text(
        "human_authorized_execution_authority_hash",
        human_authorized_execution_authority_hash,
    )

    if supplied_eah != expected_eah:
        raise JarvisGovernedMutationSeamError(
            "HUMAN_AUTHORIZED_EAH_MISMATCH_BEFORE_DRIVER"
        )

    human_ref = _require_text(
        "human_authorization_reference",
        human_authorization_reference,
    )

    result = DRV.execute_governed_remediation(
        _require_text(
            "batch_execution_id",
            prepared.get("batch_execution_id"),
        ),
        _require_text(
            "child_execution_id",
            prepared.get("child_execution_id"),
        ),
        human_authorized_execution_authority_hash=(
            supplied_eah
        ),
        human_authorization_reference=human_ref,
        execution_dir=Path(execution_dir),
        pre_execution_context_dir=Path(
            pre_execution_context_dir
        ),
        selector_dir=Path(selector_dir),
        ledger_dir=Path(ledger_dir),
        kx108_pre_decision_dir=Path(
            kx108_pre_decision_dir
        ),
        kx108_post_decision_dir=Path(
            kx108_post_decision_dir
        ),
        test_contract_results_dir=Path(
            test_contract_results_dir
        ),
        sealed_receipt_dir=Path(
            sealed_receipt_dir
        ),
        sealed_rollback_evidence_dir=Path(
            sealed_rollback_evidence_dir
        ),
        rollback_result_dir=Path(
            rollback_result_dir
        ),
        repo_root=Path(repo_root).resolve(),
        approval_dir=(
            Path(approval_dir)
            if approval_dir is not None
            else None
        ),
        authority_mode=(
            DRV.AUTHORITY_MODE_PER_ACTION_HUMAN_EAH
        ),
        mission_id=None,
        mission_store_dir=None,
    )

    out = dict(result)

    out.update(
        {
            "j5_schema_version": SCHEMA_VERSION,
            "j5_domain_tag": DOMAIN_TAG,
            "j5_phase": EXECUTE_PHASE,
            "j5_capability": CAPABILITY_ID,
            "j5_plan_hash": prepared.get(
                "j5_plan_hash"
            ),
            "jarvis_authority": JARVIS_AUTHORITY,
            "decision_authority": DECISION_AUTHORITY,
            "human_authorization_consumed": True,
            "human_authorization_reference": human_ref,
        }
    )

    return out
