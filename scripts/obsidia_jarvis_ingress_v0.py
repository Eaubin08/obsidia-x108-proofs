#!/usr/bin/env python3
"""OBSIDIA — Jarvis V0 READ_ONLY ingress.

This module does NOT create a second mission system.

It validates an explicit Jarvis request and projects it into the existing
Relay-First mission path:

    Jarvis request
      -> explicit repository allowlist
      -> before-state
      -> relay_submit_mission(GIT_STATE_READ)
      -> existing capability graph
      -> existing stack-native read_git_state
      -> existing relay receipts
      -> after-state
      -> non-sovereign Jarvis egress bundle

No Sigma/KX import.
No Native Memory import.
No repository mutation.
No OpenJarvis execution in V0.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


_SCRIPTS = Path(__file__).resolve().parent

if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))


import obsidia_relay_v0 as _RELAY
import obsidia_stack_native_routes_v0 as _NATIVE
import obsidia_terminal as _TERMINAL


SCHEMA_VERSION = "OBSIDIA_JARVIS_INGRESS_V0"
DECISION_AUTHORITY = "KX108_ONLY"

JARVIS_IS_AUTHORITY = False
JARVIS_MEMORY_WRITE = False
JARVIS_EMITS_ACT = False
JARVIS_KERNEL_MUTATION = False
OPENJARVIS_CONNECTED = False

MODE_READ_ONLY = "READ_ONLY"


@dataclass(frozen=True)
class JarvisRequest:
    command_id: str
    correlation_id: str
    issued_at: str
    requested_outcome: str
    repo_root: str
    source: str = "HUMAN_TERMINAL"
    requested_execution_mode: str = MODE_READ_ONLY
    mission_kind: str = _RELAY.KIND_GIT_STATE_READ


def _canon_path(value) -> str:
    return os.path.normcase(
        str(Path(value).expanduser().resolve(strict=False))
    )


def _is_inside(candidate, root) -> bool:
    candidate = _canon_path(candidate)
    root = _canon_path(root)

    try:
        return os.path.commonpath([candidate, root]) == root
    except ValueError:
        return False


def _canonical_json(value) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _sha256(value) -> str:
    return hashlib.sha256(
        _canonical_json(value).encode("utf-8")
    ).hexdigest()


def _state_projection(evidence: dict) -> dict:
    return {
        "head": evidence.get("head"),
        "branch": evidence.get("branch"),
        "working_tree_clean": evidence.get("working_tree_clean"),
        "changed_paths": list(evidence.get("changed_paths") or []),
        "untracked_paths": list(evidence.get("untracked_paths") or []),
        "staged_paths": list(evidence.get("staged_paths") or []),
        "diff_name_status_head": list(
            evidence.get("diff_name_status_head") or []
        ),
    }


def _reject(reason: str, **extra) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "JARVIS_REJECTED",
        "reason": reason,
        "decision_authority": DECISION_AUTHORITY,
        "is_execution_authority": False,
        "is_kx_authority": False,
        "memory_write": False,
        "emits_act": False,
        "kernel_mutation": False,
        **extra,
    }


def _terminal_envelope(
    request: JarvisRequest,
    *,
    repo_root: str,
    store_dir: str,
) -> dict:
    """Projection only.

    We reuse the TERMINAL_COMMAND_ENVELOPE_V1 field vocabulary but do not call
    T2 validate_envelope(), because mission/git are intentionally not active
    Terminal T2 commands.
    """

    envelope = {
        "schema_version": _TERMINAL.ENVELOPE_SCHEMA_VERSION,
        "command_id": request.command_id,
        "command_name": "jarvis.git_state_read",
        "command_args": {
            "repo_root": repo_root,
            "mission_kind": request.mission_kind,
        },
        "requested_output_format": "JSON",
        "requested_execution_mode": request.requested_execution_mode,
        "correlation_id": request.correlation_id,
        "issued_at": request.issued_at,
        "working_directory_ref": repo_root,
        "state_dir_ref": store_dir,
    }

    missing = [
        key
        for key in _TERMINAL.ENVELOPE_REQUIRED_FIELDS
        if key not in envelope
    ]

    if missing:
        raise ValueError(
            "TERMINAL_ENVELOPE_PROJECTION_MISSING:"
            + ",".join(missing)
        )

    return envelope


def submit_readonly_git_state(
    request: JarvisRequest,
    *,
    allowed_repositories: Iterable[str],
    store_dir,
) -> dict:

    if request.requested_execution_mode != MODE_READ_ONLY:
        return _reject("READ_ONLY_MODE_REQUIRED")

    if request.requested_execution_mode not in _TERMINAL.VALID_EXECUTION_MODES:
        return _reject("INVALID_EXECUTION_MODE")

    if request.mission_kind != _RELAY.KIND_GIT_STATE_READ:
        return _reject("MISSION_KIND_NOT_ALLOWED_IN_V0")

    if not (
        isinstance(request.requested_outcome, str)
        and request.requested_outcome.strip()
    ):
        return _reject("REQUESTED_OUTCOME_REQUIRED")

    repo_root = _canon_path(request.repo_root)

    allowlist = {
        _canon_path(path)
        for path in (allowed_repositories or [])
    }

    # Fail closed.
    if not allowlist:
        return _reject("REPOSITORY_ALLOWLIST_EMPTY")

    if repo_root not in allowlist:
        return _reject(
            "REPOSITORY_NOT_ALLOWLISTED",
            repo_root=repo_root,
        )

    store_dir = _canon_path(store_dir)

    # Mission state / receipts must stay outside the repository.
    if _is_inside(store_dir, repo_root):
        return _reject(
            "STORE_DIR_INSIDE_REPOSITORY",
            repo_root=repo_root,
            store_dir=store_dir,
        )

    before = _NATIVE.read_git_state(repo_root=repo_root)

    if not before.get("ok"):
        return _reject(
            "BEFORE_STATE_UNAVAILABLE",
            native_evidence=before,
        )

    envelope = _terminal_envelope(
        request,
        repo_root=repo_root,
        store_dir=store_dir,
    )

    relay_result = _RELAY.relay_submit_mission(
        requested_outcome=request.requested_outcome,
        mission_kind=_RELAY.KIND_GIT_STATE_READ,
        repo_root=repo_root,
        store_dir=store_dir,
    )

    relay_mission_id = relay_result.get("relay_mission_id")

    if not relay_mission_id:
        return _reject(
            "RELAY_MISSION_NOT_CREATED",
            relay_result=relay_result,
        )

    after = _NATIVE.read_git_state(repo_root=repo_root)

    if not after.get("ok"):
        return _reject(
            "AFTER_STATE_UNAVAILABLE",
            relay_mission_id=relay_mission_id,
            relay_result=relay_result,
        )

    before_projected = _state_projection(before)
    after_projected = _state_projection(after)

    mutated_measured = (
        before_projected != after_projected
    )

    relay_status = _RELAY.relay_get_status(
        relay_mission_id,
        store_dir=store_dir,
    )

    receipt_ids = list(
        relay_status.get("receipt_ids") or []
    )

    receipt_hashes = []
    missing_receipts = []

    for receipt_id in receipt_ids:
        receipt = _RELAY.relay_get_receipt(
            receipt_id,
            store_dir=store_dir,
        )

        if receipt is None:
            missing_receipts.append(receipt_id)
            continue

        receipt_hash = receipt.get("receipt_hash")

        if receipt_hash:
            receipt_hashes.append(receipt_hash)
        else:
            missing_receipts.append(receipt_id)

    receipt_integrity_complete = (
        len(receipt_ids) > 0
        and not missing_receipts
        and len(receipt_hashes) == len(receipt_ids)
    )

    receipts_digest = (
        _sha256(receipt_hashes)
        if receipt_integrity_complete
        else None
    )

    status = (
        "JARVIS_READ_ONLY_COMPLETE"
        if (
            relay_result.get("mission_state")
            == _RELAY.MISSION_COMPLETE
            and receipt_integrity_complete
            and not mutated_measured
        )
        else "JARVIS_HOLD"
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,

        "command_id": request.command_id,
        "correlation_id": request.correlation_id,

        "terminal_envelope": envelope,

        "ingress_provenance": {
            "source": request.source,
            "issued_at": request.issued_at,
            "command_id": request.command_id,
            "correlation_id": request.correlation_id,
        },

        "repo_root": repo_root,
        "mission_kind": request.mission_kind,
        "requested_execution_mode": request.requested_execution_mode,

        "relay_mission_id": relay_mission_id,
        "relay_status": relay_status.get("mission_state"),

        "receipt_ids": receipt_ids,
        "receipt_hashes": receipt_hashes,
        "receipts_digest": receipts_digest,
        "receipt_integrity_complete": receipt_integrity_complete,
        "missing_receipts": missing_receipts,

        "before_state": before_projected,
        "after_state": after_projected,
        "before_state_digest": _sha256(before_projected),
        "after_state_digest": _sha256(after_projected),

        "mutated_measured": mutated_measured,

        "kx108_invoked": False,
        "kx108_reason": "READ_ONLY_AUTHORITY_CLASS_NONE",

        "decision_authority": DECISION_AUTHORITY,
        "is_execution_authority": False,
        "is_kx_authority": False,

        "openjarvis_connected": False,
        "memory_write": False,
        "emits_act": False,
        "kernel_mutation": False,
        "scope_expanded": False,
    }