"""Controlled LIVE gateway preflight V0.

This gateway is live-capable but does not own an executor. It verifies an exact
LiveSovereignTicketV0 against current pre-state/call identity and activation
policy. A successful result means the action is eligible to be handed to a
future bound executor; it does not perform egress itself.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .external_runtime_activation_policy_v0 import (
    ExternalRuntimeActivationPolicyV0,
    operation_allowed_v0,
)
from .live_sovereign_ticket_v0 import (
    LiveSovereignTicketV0,
    verify_live_sovereign_ticket_v0,
)

DECISION_AUTHORITY = "KX108_ONLY"


@dataclass(frozen=True)
class LiveGatewayDecisionV0:
    action_id: str
    sovereign_ticket_id: str
    gate_result: str
    reason: str
    connector_id: str
    connector_action: str
    required_scope: str
    egress_preflight_allowed: bool
    egress_allowed: bool
    executor_bound: bool
    network_call_performed: bool
    decision_authority: str = DECISION_AUTHORITY

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ObsidiaLiveGatewayV0:
    def _block(
        self,
        *,
        ticket: LiveSovereignTicketV0 | None,
        reason: str,
    ) -> LiveGatewayDecisionV0:
        return LiveGatewayDecisionV0(
            action_id=ticket.action_id if ticket else "UNKNOWN",
            sovereign_ticket_id=ticket.ticket_id if ticket else "NONE",
            gate_result="BLOCK",
            reason=reason,
            connector_id=ticket.connector_id if ticket else "UNKNOWN",
            connector_action=(
                ticket.connector_action if ticket else "UNKNOWN"
            ),
            required_scope=(
                ticket.required_scope if ticket else "UNKNOWN"
            ),
            egress_preflight_allowed=False,
            egress_allowed=False,
            executor_bound=False,
            network_call_performed=False,
        )

    def check(
        self,
        *,
        ticket: LiveSovereignTicketV0 | None,
        activation_policy: ExternalRuntimeActivationPolicyV0,
        observed_connector_id: str,
        observed_connector_action: str,
        observed_connector_call_hash: str,
        observed_target_ref: str,
        observed_target_prestate_hash: str,
        observed_required_scope: str,
        observed_idempotency_key: str,
        now: str | None = None,
    ) -> LiveGatewayDecisionV0:
        if ticket is None:
            return self._block(
                ticket=None,
                reason="NO_LIVE_SOVEREIGN_TICKET_NO_WORLD_CALL",
            )

        ok, reason = verify_live_sovereign_ticket_v0(ticket, now=now)
        if not ok:
            return self._block(
                ticket=ticket,
                reason=f"LIVE_TICKET_INVALID:{reason}",
            )

        if ticket.activation_policy_id != activation_policy.policy_id:
            return self._block(
                ticket=ticket,
                reason="LIVE_TICKET_ACTIVATION_POLICY_ID_MISMATCH",
            )
        if ticket.activation_policy_hash != activation_policy.policy_hash:
            return self._block(
                ticket=ticket,
                reason="LIVE_TICKET_ACTIVATION_POLICY_HASH_MISMATCH",
            )

        allowed, reason = operation_allowed_v0(
            activation_policy,
            connector_id=ticket.connector_id,
            connector_action=ticket.connector_action,
            required_scope=ticket.required_scope,
            world_call_class=ticket.world_call_class,
            action_risk_class=ticket.action_risk_class,
            autonomy_level=ticket.autonomy_level,
        )
        if not allowed:
            return self._block(
                ticket=ticket,
                reason=f"LIVE_GATEWAY_POLICY_BLOCK:{reason}",
            )

        observed = {
            "connector_id": observed_connector_id,
            "connector_action": observed_connector_action,
            "connector_call_hash": observed_connector_call_hash,
            "target_ref": observed_target_ref,
            "target_prestate_hash": observed_target_prestate_hash,
            "required_scope": observed_required_scope,
            "idempotency_key": observed_idempotency_key,
        }
        expected = {
            "connector_id": ticket.connector_id,
            "connector_action": ticket.connector_action,
            "connector_call_hash": ticket.connector_call_hash,
            "target_ref": ticket.target_ref,
            "target_prestate_hash": ticket.target_prestate_hash,
            "required_scope": ticket.required_scope,
            "idempotency_key": ticket.idempotency_key,
        }

        for field, expected_value in expected.items():
            if observed[field] != expected_value:
                return self._block(
                    ticket=ticket,
                    reason=f"LIVE_GATEWAY_BINDING_MISMATCH:{field}",
                )

        # V0 stops HERE. No executor is bound and no network call exists.
        return LiveGatewayDecisionV0(
            action_id=ticket.action_id,
            sovereign_ticket_id=ticket.ticket_id,
            gate_result="LIVE_PREFLIGHT_READY",
            reason="KX108_PRE_AND_ACTIVATION_POLICY_VERIFIED_EXECUTOR_NOT_BOUND",
            connector_id=ticket.connector_id,
            connector_action=ticket.connector_action,
            required_scope=ticket.required_scope,
            egress_preflight_allowed=True,
            egress_allowed=False,
            executor_bound=False,
            network_call_performed=False,
        )
