from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .os3_ticket import ticket_is_valid

@dataclass
class WorldActionReadiness:
    action_id: str
    dry_run_only: bool
    ready_for_controlled_execution: bool
    world_action_allowed: bool
    reason: str

def evaluate_world_action_readiness(action: Any, envelope: Any, ticket: Any, gencoin_candidate: Any | None = None) -> WorldActionReadiness:
    # Gateway ACT en mode dry-run. Il ne déclenche aucune action monde réelle.
    gate = getattr(envelope, "x108_gate", "UNKNOWN")
    if gate != "ALLOW":
        return WorldActionReadiness(action.action_id, True, False, False, f"X108_NOT_ALLOW:{gate}")

    if not ticket_is_valid(ticket):
        return WorldActionReadiness(action.action_id, True, False, False, "OS3_TICKET_INVALID")

    return WorldActionReadiness(action.action_id, True, True, False, "READY_DRY_RUN_ONLY_RUNTIME_CONSENT_REQUIRED")
