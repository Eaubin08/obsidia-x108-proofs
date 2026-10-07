"""Bounded connector executor contract V0.

Universal executor boundary after LIVE_PREFLIGHT_READY.

V0 intentionally accepts only deterministic sandbox adapters:
- external_network_capable must be False
- side_effect_free must be True
- execution_mode must be SANDBOX_DETERMINISTIC

No real connector/network call can pass this executor in V0.

The module proves:
- exact Gateway revalidation
- exact connector-call hash binding
- append-only execution receipts
- receipt replay
- duplicate confirmed-execution blocking
- unknown-outcome reconciliation blocking
- confirmed-no-effect retry semantics

decision_authority = KX108_ONLY
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Optional, Protocol

from .external_runtime_activation_policy_v0 import (
    ExternalRuntimeActivationPolicyV0,
)
from .live_sovereign_ticket_v0 import (
    LiveSovereignTicketV0,
)
from .obsidia_live_gateway_v0 import (
    ObsidiaLiveGatewayV0,
)

SCHEMA = "WORLD_ACTION_EXECUTION_RECEIPT_V0"
DECISION_AUTHORITY = "KX108_ONLY"
EXECUTION_MODE_SANDBOX = "SANDBOX_DETERMINISTIC"

OUTCOME_CONFIRMED_SUCCESS = "CONFIRMED_SUCCESS"
OUTCOME_CONFIRMED_NO_EFFECT = "CONFIRMED_NO_EFFECT"
OUTCOME_UNKNOWN = "UNKNOWN_OUTCOME"
OUTCOME_PROVIDER_REJECTED = "PROVIDER_REJECTED"

VALID_OUTCOMES = {
    OUTCOME_CONFIRMED_SUCCESS,
    OUTCOME_CONFIRMED_NO_EFFECT,
    OUTCOME_UNKNOWN,
    OUTCOME_PROVIDER_REJECTED,
}

RECOVERY_COMPLETED = "COMPLETED"
RECOVERY_CONFIRMED_NO_EFFECT = "CONFIRMED_NO_EFFECT"
RECOVERY_RECONCILIATION_REQUIRED = "RECONCILIATION_REQUIRED"
RECOVERY_NEW_DECISION_REQUIRED = "NEW_DECISION_REQUIRED"

STATUS_EXECUTED = "SANDBOX_EXECUTED_RECEIPT_STORED"
STATUS_BLOCKED = "BLOCKED"

RECEIPT_DIR = (
    Path(os.environ.get("LOCALAPPDATA", ""))
    / "Obsidia"
    / "world_action_execution_receipts"
)
RECONCILIATION_DIR = (
    Path(os.environ.get("LOCALAPPDATA", ""))
    / "Obsidia"
    / "world_action_reconciliations"
)

RECONCILIATION_SCHEMA = "WORLD_ACTION_RECONCILIATION_V0"
RECONCILIATION_CONFIRMED_SUCCESS = "CONFIRMED_SUCCESS"
RECONCILIATION_CONFIRMED_NO_EFFECT = "CONFIRMED_NO_EFFECT"

_RECEIPT_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
_RECONCILIATION_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")


def _hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            ensure_ascii=False,
            default=str,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def compute_connector_call_hash(
    *,
    connector_id: str,
    connector_action: str,
    connector_args: Mapping[str, Any],
) -> str:
    return _hash(
        {
            "connector_id": connector_id,
            "connector_action": connector_action,
            "connector_args": dict(connector_args),
        }
    )


@dataclass(frozen=True)
class ConnectorProviderOutcomeV0:
    status: str
    provider_receipt_ref: str
    provider_state_ref: str
    detail_digest: str
    observed_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ConnectorAdapterV0(Protocol):
    connector_id: str
    connector_action: str
    required_scope: str
    provider_id: str
    execution_mode: str
    external_network_capable: bool
    side_effect_free: bool
    retry_after_confirmed_no_effect: bool

    def execute(
        self,
        connector_args: Mapping[str, Any],
    ) -> ConnectorProviderOutcomeV0:
        ...


@dataclass(frozen=True)
class WorldActionExecutionReceiptV0:
    schema: str
    receipt_id: str
    created_at: str
    action_id: str
    source_domain: str
    sovereign_ticket_id: str
    sovereign_ticket_hash: str
    activation_policy_hash: str
    world_action_request_hash: str
    connector_id: str
    connector_action: str
    connector_call_hash: str
    target_ref: str
    target_prestate_hash: str
    required_scope: str
    idempotency_key: str
    provider_id: str
    provider_outcome_status: str
    provider_receipt_ref: str
    provider_state_ref: str
    provider_detail_digest: str
    execution_mode: str
    sandbox_execution: bool
    real_external_effect: bool
    retry_allowed: bool
    recovery_state: str
    decision_authority: str
    receipt_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class WorldActionReconciliationV0:
    schema: str
    reconciliation_id: str
    created_at: str
    unknown_receipt_id: str
    unknown_receipt_hash: str
    idempotency_key: str
    resolution: str
    provider_verification_ref: str
    human_review_ref: str
    decision_authority: str
    is_execution_authority: bool
    reconciliation_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BoundedExecutorResultV0:
    status: str
    reason: str
    gateway_result: str
    adapter_called: bool
    network_call_performed: bool
    real_external_effect: bool
    receipt: Optional[WorldActionExecutionReceiptV0] = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if self.receipt is not None:
            data["receipt"] = self.receipt.to_dict()
        return data


def _receipt_payload(receipt_like: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: receipt_like[key]
        for key in (
            "schema",
            "receipt_id",
            "created_at",
            "action_id",
            "source_domain",
            "sovereign_ticket_id",
            "sovereign_ticket_hash",
            "activation_policy_hash",
            "world_action_request_hash",
            "connector_id",
            "connector_action",
            "connector_call_hash",
            "target_ref",
            "target_prestate_hash",
            "required_scope",
            "idempotency_key",
            "provider_id",
            "provider_outcome_status",
            "provider_receipt_ref",
            "provider_state_ref",
            "provider_detail_digest",
            "execution_mode",
            "sandbox_execution",
            "real_external_effect",
            "retry_allowed",
            "recovery_state",
            "decision_authority",
        )
    }


def verify_execution_receipt_v0(
    receipt: WorldActionExecutionReceiptV0 | Mapping[str, Any] | None,
) -> tuple[bool, Optional[str]]:
    if receipt is None:
        return False, "EXECUTION_RECEIPT_MISSING"
    data = (
        receipt.to_dict()
        if isinstance(receipt, WorldActionExecutionReceiptV0)
        else dict(receipt)
    )
    if data.get("schema") != SCHEMA:
        return False, "EXECUTION_RECEIPT_SCHEMA_INVALID"
    if data.get("decision_authority") != DECISION_AUTHORITY:
        return False, "EXECUTION_RECEIPT_AUTHORITY_INVALID"
    if data.get("provider_outcome_status") not in VALID_OUTCOMES:
        return False, "EXECUTION_RECEIPT_OUTCOME_INVALID"
    if data.get("execution_mode") != EXECUTION_MODE_SANDBOX:
        return False, "EXECUTION_RECEIPT_MODE_INVALID"
    if data.get("sandbox_execution") is not True:
        return False, "EXECUTION_RECEIPT_SANDBOX_FLAG_INVALID"
    if data.get("real_external_effect") is not False:
        return False, "EXECUTION_RECEIPT_REAL_EFFECT_FORBIDDEN_V0"
    expected = _hash(_receipt_payload(data))
    if data.get("receipt_hash") != expected:
        return False, "EXECUTION_RECEIPT_HASH_MISMATCH"
    return True, None


def _receipt_path(
    receipt_id: str,
    store_dir: Optional[Path] = None,
) -> Path:
    if not receipt_id or not _RECEIPT_ID_RE.match(receipt_id):
        raise ValueError("INVALID_EXECUTION_RECEIPT_ID")
    return (store_dir or RECEIPT_DIR) / f"{receipt_id}.json"


def store_execution_receipt_v0(
    receipt: WorldActionExecutionReceiptV0,
    store_dir: Optional[Path] = None,
) -> dict[str, Any]:
    ok, reason = verify_execution_receipt_v0(receipt)
    if not ok:
        return {"status": "REJECTED", "reason": reason}
    path = _receipt_path(receipt.receipt_id, store_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(receipt.to_dict(), ensure_ascii=False, indent=2)
    tmp = path.parent / (
        f".{path.name}.{os.getpid()}."
        f"{hashlib.sha256((payload + str(id(receipt))).encode('utf-8')).hexdigest()[:16]}.tmp"
    )
    tmp.write_text(payload, encoding="utf-8")
    try:
        os.link(tmp, path)
        return {"status": "STORED", "receipt_id": receipt.receipt_id}
    except FileExistsError:
        if path.read_text(encoding="utf-8") == payload:
            return {
                "status": "IDEMPOTENT_EXISTING_IDENTICAL",
                "receipt_id": receipt.receipt_id,
            }
        return {
            "status": "IMMUTABILITY_VIOLATION",
            "receipt_id": receipt.receipt_id,
        }
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass


def load_execution_receipt_v0(
    receipt_id: str,
    store_dir: Optional[Path] = None,
) -> Optional[dict[str, Any]]:
    try:
        path = _receipt_path(receipt_id, store_dir)
    except ValueError:
        return None
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def replay_execution_receipt_v0(
    receipt_id: str,
    *,
    store_dir: Optional[Path] = None,
    expected_ticket_hash: str,
    expected_connector_call_hash: str,
    expected_idempotency_key: str,
) -> tuple[bool, Optional[str]]:
    receipt = load_execution_receipt_v0(receipt_id, store_dir)
    ok, reason = verify_execution_receipt_v0(receipt)
    if not ok:
        return False, reason
    if receipt["sovereign_ticket_hash"] != expected_ticket_hash:
        return False, "EXECUTION_RECEIPT_TICKET_HASH_MISMATCH"
    if receipt["connector_call_hash"] != expected_connector_call_hash:
        return False, "EXECUTION_RECEIPT_CONNECTOR_CALL_HASH_MISMATCH"
    if receipt["idempotency_key"] != expected_idempotency_key:
        return False, "EXECUTION_RECEIPT_IDEMPOTENCY_KEY_MISMATCH"
    return True, None


def _reconciliation_payload(
    value: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        key: value[key]
        for key in (
            "schema",
            "reconciliation_id",
            "created_at",
            "unknown_receipt_id",
            "unknown_receipt_hash",
            "idempotency_key",
            "resolution",
            "provider_verification_ref",
            "human_review_ref",
            "decision_authority",
            "is_execution_authority",
        )
    }


def verify_reconciliation_v0(
    reconciliation: WorldActionReconciliationV0 | Mapping[str, Any] | None,
) -> tuple[bool, Optional[str]]:
    if reconciliation is None:
        return False, "RECONCILIATION_MISSING"
    data = (
        reconciliation.to_dict()
        if isinstance(reconciliation, WorldActionReconciliationV0)
        else dict(reconciliation)
    )
    if data.get("schema") != RECONCILIATION_SCHEMA:
        return False, "RECONCILIATION_SCHEMA_INVALID"
    if data.get("decision_authority") != DECISION_AUTHORITY:
        return False, "RECONCILIATION_AUTHORITY_INVALID"
    if data.get("is_execution_authority") is not False:
        return False, "RECONCILIATION_CANNOT_AUTHORIZE_EXECUTION"
    if data.get("resolution") not in {
        RECONCILIATION_CONFIRMED_SUCCESS,
        RECONCILIATION_CONFIRMED_NO_EFFECT,
    }:
        return False, "RECONCILIATION_RESOLUTION_INVALID"
    if not data.get("provider_verification_ref"):
        return False, "RECONCILIATION_PROVIDER_VERIFICATION_REQUIRED"
    if not data.get("human_review_ref"):
        return False, "RECONCILIATION_HUMAN_REVIEW_REQUIRED"
    expected = _hash(_reconciliation_payload(data))
    if data.get("reconciliation_hash") != expected:
        return False, "RECONCILIATION_HASH_MISMATCH"
    return True, None


def _reconciliation_path(
    reconciliation_id: str,
    store_dir: Optional[Path] = None,
) -> Path:
    if (
        not reconciliation_id
        or not _RECONCILIATION_ID_RE.match(reconciliation_id)
    ):
        raise ValueError("INVALID_RECONCILIATION_ID")
    return (
        store_dir or RECONCILIATION_DIR
    ) / f"{reconciliation_id}.json"


def store_reconciliation_v0(
    reconciliation: WorldActionReconciliationV0,
    store_dir: Optional[Path] = None,
) -> dict[str, Any]:
    ok, reason = verify_reconciliation_v0(reconciliation)
    if not ok:
        return {"status": "REJECTED", "reason": reason}
    path = _reconciliation_path(
        reconciliation.reconciliation_id,
        store_dir,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        reconciliation.to_dict(),
        ensure_ascii=False,
        indent=2,
    )
    tmp = path.parent / (
        f".{path.name}.{os.getpid()}."
        f"{hashlib.sha256((payload + str(id(reconciliation))).encode('utf-8')).hexdigest()[:16]}.tmp"
    )
    tmp.write_text(payload, encoding="utf-8")
    try:
        os.link(tmp, path)
        return {
            "status": "STORED",
            "reconciliation_id": reconciliation.reconciliation_id,
        }
    except FileExistsError:
        if path.read_text(encoding="utf-8") == payload:
            return {
                "status": "IDEMPOTENT_EXISTING_IDENTICAL",
                "reconciliation_id": reconciliation.reconciliation_id,
            }
        return {
            "status": "IMMUTABILITY_VIOLATION",
            "reconciliation_id": reconciliation.reconciliation_id,
        }
    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass


def reconcile_unknown_outcome_v0(
    *,
    unknown_receipt_id: str,
    resolution: str,
    provider_verification_ref: str,
    human_review_ref: str,
    receipt_store_dir: Optional[Path] = None,
    reconciliation_store_dir: Optional[Path] = None,
    now: str | None = None,
) -> WorldActionReconciliationV0:
    receipt = load_execution_receipt_v0(
        unknown_receipt_id,
        receipt_store_dir,
    )
    ok, reason = verify_execution_receipt_v0(receipt)
    if not ok:
        raise ValueError(f"UNKNOWN_RECEIPT_INVALID:{reason}")
    if receipt.get("provider_outcome_status") != OUTCOME_UNKNOWN:
        raise ValueError("RECONCILIATION_REQUIRES_UNKNOWN_OUTCOME")
    if resolution not in {
        RECONCILIATION_CONFIRMED_SUCCESS,
        RECONCILIATION_CONFIRMED_NO_EFFECT,
    }:
        raise ValueError("RECONCILIATION_RESOLUTION_INVALID")
    if not provider_verification_ref:
        raise ValueError("RECONCILIATION_PROVIDER_VERIFICATION_REQUIRED")
    if not human_review_ref:
        raise ValueError("RECONCILIATION_HUMAN_REVIEW_REQUIRED")

    observed = datetime.datetime.fromisoformat(
        now or datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    if observed.tzinfo is None:
        raise ValueError("RECONCILIATION_TIME_MUST_BE_TIMEZONE_AWARE")

    seed = {
        "unknown_receipt_hash": receipt["receipt_hash"],
        "resolution": resolution,
        "provider_verification_ref": provider_verification_ref,
        "human_review_ref": human_review_ref,
        "created_at": observed.isoformat(),
    }
    reconciliation_id = f"wareconcile-{_hash(seed)[:32]}"
    payload = {
        "schema": RECONCILIATION_SCHEMA,
        "reconciliation_id": reconciliation_id,
        "created_at": observed.isoformat(),
        "unknown_receipt_id": receipt["receipt_id"],
        "unknown_receipt_hash": receipt["receipt_hash"],
        "idempotency_key": receipt["idempotency_key"],
        "resolution": resolution,
        "provider_verification_ref": provider_verification_ref,
        "human_review_ref": human_review_ref,
        "decision_authority": DECISION_AUTHORITY,
        "is_execution_authority": False,
    }
    payload["reconciliation_hash"] = _hash(
        _reconciliation_payload(payload)
    )
    reconciliation = WorldActionReconciliationV0(**payload)
    stored = store_reconciliation_v0(
        reconciliation,
        reconciliation_store_dir,
    )
    if stored.get("status") not in {
        "STORED",
        "IDEMPOTENT_EXISTING_IDENTICAL",
    }:
        raise ValueError(
            f"RECONCILIATION_STORE_FAILED:{stored.get('status')}"
        )
    return reconciliation


def _reconciliations_for_receipt(
    receipt_id: str,
    store_dir: Optional[Path],
) -> list[dict[str, Any]]:
    root = store_dir or RECONCILIATION_DIR
    if not root.exists():
        return []
    matches: list[dict[str, Any]] = []
    for path in sorted(root.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if data.get("unknown_receipt_id") != receipt_id:
            continue
        ok, _ = verify_reconciliation_v0(data)
        if ok:
            matches.append(data)
    return matches


def _receipts_for_idempotency(
    idempotency_key: str,
    store_dir: Optional[Path],
) -> list[dict[str, Any]]:
    root = store_dir or RECEIPT_DIR
    if not root.exists():
        return []
    matches: list[dict[str, Any]] = []
    for path in sorted(root.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if data.get("idempotency_key") != idempotency_key:
            continue
        ok, _ = verify_execution_receipt_v0(data)
        if ok:
            matches.append(data)
    return matches


def _prior_execution_block_reason(
    idempotency_key: str,
    receipt_store_dir: Optional[Path],
    reconciliation_store_dir: Optional[Path],
) -> Optional[str]:
    previous = _receipts_for_idempotency(
        idempotency_key,
        receipt_store_dir,
    )
    if any(
        item.get("provider_outcome_status") == OUTCOME_CONFIRMED_SUCCESS
        for item in previous
    ):
        return "DUPLICATE_CONFIRMED_EXECUTION_BLOCK"

    for item in previous:
        if item.get("provider_outcome_status") != OUTCOME_UNKNOWN:
            continue
        reconciliations = _reconciliations_for_receipt(
            item["receipt_id"],
            reconciliation_store_dir,
        )
        if not reconciliations:
            return "UNKNOWN_PRIOR_OUTCOME_RECONCILIATION_REQUIRED"
        if any(
            rec.get("resolution") == RECONCILIATION_CONFIRMED_SUCCESS
            for rec in reconciliations
        ):
            return "RECONCILED_CONFIRMED_EXECUTION_DUPLICATE_BLOCK"
        # CONFIRMED_NO_EFFECT clears the unknown-outcome retry block.

    if any(
        item.get("provider_outcome_status") == OUTCOME_PROVIDER_REJECTED
        for item in previous
    ):
        return "PROVIDER_REJECTED_NEW_DECISION_REQUIRED"
    return None


def _normalize_outcome(
    outcome: ConnectorProviderOutcomeV0,
    *,
    retry_after_confirmed_no_effect: bool,
) -> tuple[bool, str]:
    if outcome.status == OUTCOME_CONFIRMED_SUCCESS:
        return False, RECOVERY_COMPLETED
    if outcome.status == OUTCOME_CONFIRMED_NO_EFFECT:
        return (
            bool(retry_after_confirmed_no_effect),
            RECOVERY_CONFIRMED_NO_EFFECT,
        )
    if outcome.status == OUTCOME_UNKNOWN:
        return False, RECOVERY_RECONCILIATION_REQUIRED
    if outcome.status == OUTCOME_PROVIDER_REJECTED:
        return False, RECOVERY_NEW_DECISION_REQUIRED
    raise ValueError("CONNECTOR_PROVIDER_OUTCOME_INVALID")


def execute_bounded_connector_v0(
    *,
    ticket: LiveSovereignTicketV0,
    activation_policy: ExternalRuntimeActivationPolicyV0,
    connector_args: Mapping[str, Any],
    observed_target_ref: str,
    observed_target_prestate_hash: str,
    adapter: ConnectorAdapterV0,
    receipt_store_dir: Optional[Path] = None,
    reconciliation_store_dir: Optional[Path] = None,
    now: str | None = None,
) -> BoundedExecutorResultV0:
    """Execute only a deterministic sandbox adapter after exact revalidation."""
    observed_call_hash = compute_connector_call_hash(
        connector_id=ticket.connector_id,
        connector_action=ticket.connector_action,
        connector_args=connector_args,
    )

    gateway = ObsidiaLiveGatewayV0().check(
        ticket=ticket,
        activation_policy=activation_policy,
        observed_connector_id=ticket.connector_id,
        observed_connector_action=ticket.connector_action,
        observed_connector_call_hash=observed_call_hash,
        observed_target_ref=observed_target_ref,
        observed_target_prestate_hash=observed_target_prestate_hash,
        observed_required_scope=ticket.required_scope,
        observed_idempotency_key=ticket.idempotency_key,
        now=now,
    )
    if gateway.gate_result != "LIVE_PREFLIGHT_READY":
        return BoundedExecutorResultV0(
            status=STATUS_BLOCKED,
            reason=f"GATEWAY_NOT_READY:{gateway.reason}",
            gateway_result=gateway.gate_result,
            adapter_called=False,
            network_call_performed=False,
            real_external_effect=False,
        )

    if adapter.execution_mode != EXECUTION_MODE_SANDBOX:
        return BoundedExecutorResultV0(
            status=STATUS_BLOCKED,
            reason="REAL_CONNECTOR_EXECUTOR_NOT_BOUND_V0",
            gateway_result=gateway.gate_result,
            adapter_called=False,
            network_call_performed=False,
            real_external_effect=False,
        )
    if adapter.external_network_capable is not False:
        return BoundedExecutorResultV0(
            status=STATUS_BLOCKED,
            reason="EXTERNAL_NETWORK_ADAPTER_FORBIDDEN_V0",
            gateway_result=gateway.gate_result,
            adapter_called=False,
            network_call_performed=False,
            real_external_effect=False,
        )
    if adapter.side_effect_free is not True:
        return BoundedExecutorResultV0(
            status=STATUS_BLOCKED,
            reason="SIDE_EFFECTING_ADAPTER_FORBIDDEN_V0",
            gateway_result=gateway.gate_result,
            adapter_called=False,
            network_call_performed=False,
            real_external_effect=False,
        )

    exact_adapter = (
        adapter.connector_id == ticket.connector_id
        and adapter.connector_action == ticket.connector_action
        and adapter.required_scope == ticket.required_scope
    )
    if not exact_adapter:
        return BoundedExecutorResultV0(
            status=STATUS_BLOCKED,
            reason="CONNECTOR_ADAPTER_BINDING_MISMATCH",
            gateway_result=gateway.gate_result,
            adapter_called=False,
            network_call_performed=False,
            real_external_effect=False,
        )

    prior_block = _prior_execution_block_reason(
        ticket.idempotency_key,
        receipt_store_dir,
        reconciliation_store_dir,
    )
    if prior_block:
        return BoundedExecutorResultV0(
            status=STATUS_BLOCKED,
            reason=prior_block,
            gateway_result=gateway.gate_result,
            adapter_called=False,
            network_call_performed=False,
            real_external_effect=False,
        )

    outcome = adapter.execute(connector_args)
    if not isinstance(outcome, ConnectorProviderOutcomeV0):
        return BoundedExecutorResultV0(
            status=STATUS_BLOCKED,
            reason="CONNECTOR_OUTCOME_TYPE_INVALID",
            gateway_result=gateway.gate_result,
            adapter_called=True,
            network_call_performed=False,
            real_external_effect=False,
        )
    if outcome.status not in VALID_OUTCOMES:
        return BoundedExecutorResultV0(
            status=STATUS_BLOCKED,
            reason="CONNECTOR_PROVIDER_OUTCOME_INVALID",
            gateway_result=gateway.gate_result,
            adapter_called=True,
            network_call_performed=False,
            real_external_effect=False,
        )

    retry_allowed, recovery_state = _normalize_outcome(
        outcome,
        retry_after_confirmed_no_effect=(
            adapter.retry_after_confirmed_no_effect
        ),
    )

    observed = datetime.datetime.fromisoformat(
        now or datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    if observed.tzinfo is None:
        return BoundedExecutorResultV0(
            status=STATUS_BLOCKED,
            reason="EXECUTOR_TIME_MUST_BE_TIMEZONE_AWARE",
            gateway_result=gateway.gate_result,
            adapter_called=True,
            network_call_performed=False,
            real_external_effect=False,
        )

    seed = {
        "ticket_hash": ticket.ticket_hash,
        "idempotency_key": ticket.idempotency_key,
        "provider_id": adapter.provider_id,
        "provider_outcome_status": outcome.status,
        "provider_receipt_ref": outcome.provider_receipt_ref,
        "provider_state_ref": outcome.provider_state_ref,
        "observed_at": outcome.observed_at,
        "created_at": observed.isoformat(),
    }
    receipt_id = f"wareceipt-{_hash(seed)[:32]}"

    payload = {
        "schema": SCHEMA,
        "receipt_id": receipt_id,
        "created_at": observed.isoformat(),
        "action_id": ticket.action_id,
        "source_domain": ticket.source_domain,
        "sovereign_ticket_id": ticket.ticket_id,
        "sovereign_ticket_hash": ticket.ticket_hash,
        "activation_policy_hash": ticket.activation_policy_hash,
        "world_action_request_hash": ticket.world_action_request_hash,
        "connector_id": ticket.connector_id,
        "connector_action": ticket.connector_action,
        "connector_call_hash": ticket.connector_call_hash,
        "target_ref": ticket.target_ref,
        "target_prestate_hash": ticket.target_prestate_hash,
        "required_scope": ticket.required_scope,
        "idempotency_key": ticket.idempotency_key,
        "provider_id": adapter.provider_id,
        "provider_outcome_status": outcome.status,
        "provider_receipt_ref": outcome.provider_receipt_ref,
        "provider_state_ref": outcome.provider_state_ref,
        "provider_detail_digest": outcome.detail_digest,
        "execution_mode": adapter.execution_mode,
        "sandbox_execution": True,
        "real_external_effect": False,
        "retry_allowed": retry_allowed,
        "recovery_state": recovery_state,
        "decision_authority": DECISION_AUTHORITY,
    }
    payload["receipt_hash"] = _hash(_receipt_payload(payload))
    receipt = WorldActionExecutionReceiptV0(**payload)

    stored = store_execution_receipt_v0(receipt, receipt_store_dir)
    if stored.get("status") not in {
        "STORED",
        "IDEMPOTENT_EXISTING_IDENTICAL",
    }:
        return BoundedExecutorResultV0(
            status=STATUS_BLOCKED,
            reason=f"EXECUTION_RECEIPT_STORE_FAILED:{stored.get('status')}",
            gateway_result=gateway.gate_result,
            adapter_called=True,
            network_call_performed=False,
            real_external_effect=False,
        )

    return BoundedExecutorResultV0(
        status=STATUS_EXECUTED,
        reason="SANDBOX_CONNECTOR_EXECUTED_RECEIPT_PROVEN",
        gateway_result=gateway.gate_result,
        adapter_called=True,
        network_call_performed=False,
        real_external_effect=False,
        receipt=receipt,
    )
