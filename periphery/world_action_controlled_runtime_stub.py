from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

_BLOCKED_CAPABILITIES = [
    "PAYMENT",
    "TRADE_EXECUTION",
    "API_MUTATION",
    "POSTING",
    "EMAIL",
    "MEMORY_WRITE",
    "KERNEL_BYPASS",
    "NEO4J_WRITE",
    "GRAPHITI_WRITE",
    "BRODY_MEMORY_WRITE",
]


@dataclass
class WorldActionDryRunPacket:
    action_id: str
    domain: str
    x108_gate: str
    os3_valid: bool
    gencoin_candidate: float
    dry_run_only: bool = True
    world_action_allowed: bool = False
    consent_checkpoint_required: bool = True
    requires_human_takeover: bool = True
    blocked_capabilities: list[str] = field(default_factory=lambda: list(_BLOCKED_CAPABILITIES))
    reason: str = "V4_CONTROLLED_RUNTIME_DRY_RUN_ONLY"

    def assert_no_real_action(self) -> None:
        if self.world_action_allowed:
            raise AssertionError("WORLD_ACTION_FORBIDDEN_DRY_RUN_ONLY")
        if not self.dry_run_only:
            raise AssertionError("DRY_RUN_ONLY_VIOLATED")

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "domain": self.domain,
            "x108_gate": self.x108_gate,
            "os3_valid": self.os3_valid,
            "gencoin_candidate": self.gencoin_candidate,
            "dry_run_only": self.dry_run_only,
            "world_action_allowed": self.world_action_allowed,
            "consent_checkpoint_required": self.consent_checkpoint_required,
            "requires_human_takeover": self.requires_human_takeover,
            "blocked_capabilities": self.blocked_capabilities,
            "reason": self.reason,
        }


def run_world_action_stub(
    action_candidate: Any,
    ticket: Any,
    gencoin_candidate: float,
) -> WorldActionDryRunPacket:
    gate = str(getattr(ticket, "x108_gate", "UNKNOWN")).upper()
    os3_valid = bool(
        getattr(ticket, "input_hash", "") and
        getattr(ticket, "output_hash", "") and
        getattr(ticket, "trace_hash", "")
    )

    pkt = WorldActionDryRunPacket(
        action_id=action_candidate.action_id,
        domain=action_candidate.domain,
        x108_gate=gate,
        os3_valid=os3_valid,
        gencoin_candidate=gencoin_candidate,
        dry_run_only=True,
        world_action_allowed=False,
        consent_checkpoint_required=True,
        requires_human_takeover=True,
        blocked_capabilities=list(_BLOCKED_CAPABILITIES),
        reason="V4_CONTROLLED_RUNTIME_DRY_RUN_ONLY",
    )
    pkt.assert_no_real_action()
    return pkt
