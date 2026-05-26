"""
ObsidiaGateway — verifies sovereign ticket, scope, expiration, policy.
Controls egress. Always dry-run in V4.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .sovereign_ticket import SovereignTicket, require_ticket_or_block
from .world_call_classifier import WorldCallClass, is_blocked
from .secret_boundary import assert_no_secret_in_agent_payload


@dataclass
class GatewayDecision:
    action_id: str
    sovereign_ticket_id: str
    world_call_class: str
    gate_result: str
    reason: str
    dry_run_only: bool = True
    egress_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "sovereign_ticket_id": self.sovereign_ticket_id,
            "world_call_class": self.world_call_class,
            "gate_result": self.gate_result,
            "reason": self.reason,
            "dry_run_only": self.dry_run_only,
            "egress_allowed": self.egress_allowed,
        }


class ObsidiaGateway:
    def check(
        self,
        ticket: SovereignTicket | None,
        world_call_class: WorldCallClass,
        required_scope: str,
        agent_payload: dict | None = None,
    ) -> GatewayDecision:
        if ticket is None:
            return GatewayDecision(
                action_id="UNKNOWN",
                sovereign_ticket_id="NONE",
                world_call_class=str(world_call_class),
                gate_result="BLOCK",
                reason="NO_SOVEREIGN_TICKET_NO_WORLD_CALL",
                egress_allowed=False,
            )

        if ticket.is_expired():
            return GatewayDecision(
                action_id=ticket.action_id,
                sovereign_ticket_id=ticket.ticket_id,
                world_call_class=str(world_call_class),
                gate_result="BLOCK",
                reason="TICKET_EXPIRED",
                egress_allowed=False,
            )

        if not ticket.is_valid_scope(required_scope):
            return GatewayDecision(
                action_id=ticket.action_id,
                sovereign_ticket_id=ticket.ticket_id,
                world_call_class=str(world_call_class),
                gate_result="BLOCK",
                reason=f"INVALID_SCOPE:{required_scope}",
                egress_allowed=False,
            )

        if is_blocked(world_call_class):
            return GatewayDecision(
                action_id=ticket.action_id,
                sovereign_ticket_id=ticket.ticket_id,
                world_call_class=str(world_call_class),
                gate_result="BLOCK",
                reason=f"WORLD_CALL_CLASS_BLOCKED:{world_call_class}",
                egress_allowed=False,
            )

        if agent_payload:
            assert_no_secret_in_agent_payload(agent_payload)

        return GatewayDecision(
            action_id=ticket.action_id,
            sovereign_ticket_id=ticket.ticket_id,
            world_call_class=str(world_call_class),
            gate_result="DRY_RUN_PASS",
            reason="V4_DRY_RUN_ONLY",
            dry_run_only=True,
            egress_allowed=False,
        )
