"""
apps/obsidia_api/bus/message.py — Bus message schema (P61 DRY_RUN_ONLY adapter).

Adapted from engine/bus/message.py.
Pure data model — no runtime activation, no ACT emission.
DRY_RUN_ONLY = True enforced at module level.
ACTION intents and ACT decisions blocked in dry-run context.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

DRY_RUN_ONLY: bool = True

# Only BLOCK and HOLD are permitted decisions in DRY_RUN_ONLY mode.
ALLOWED_DECISIONS = frozenset({"BLOCK", "HOLD"})


class MsgIntentType(str, Enum):
    PROPOSE = "PROPOSE"
    # ACTION is present in the data model but blocked when DRY_RUN_ONLY=True.
    ACTION = "ACTION"


@dataclass
class IntentMsg:
    type: MsgIntentType
    name: str
    payload: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if DRY_RUN_ONLY and self.type == MsgIntentType.ACTION:
            raise ValueError("ACTION intent is disabled in DRY_RUN_ONLY mode")


@dataclass
class ContextMsg:
    state: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    resources: Dict[str, Any] = field(default_factory=dict)
    history_ref: Optional[str] = None


@dataclass
class GovernanceMsg:
    irreversible: bool = False
    x108_enabled: bool = True
    x108_min_wait_s: int = 108
    x108_elapsed_s: int = 0


@dataclass
class ActorMsg:
    agent_id: Optional[str] = None
    human_id: Optional[str] = None


@dataclass
class MetaMsg:
    request_id: str
    timestamp: str
    domain: str
    mode: str  # "proof" or "simu" — "live" is blocked in DRY_RUN_ONLY context
    actor: ActorMsg = field(default_factory=ActorMsg)

    def __post_init__(self) -> None:
        if DRY_RUN_ONLY and self.mode == "live":
            raise ValueError("mode='live' is disabled in DRY_RUN_ONLY context")


@dataclass
class DecisionMsg:
    decision: str  # BLOCK or HOLD only — ACT is blocked in DRY_RUN_ONLY context
    trace_id: str
    reason_code: str
    reason_message: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    artifacts_hash: Optional[str] = None

    def __post_init__(self) -> None:
        if DRY_RUN_ONLY and self.decision not in ALLOWED_DECISIONS:
            raise ValueError(
                f"Decision '{self.decision}' is not allowed in DRY_RUN_ONLY mode. "
                f"Allowed: {sorted(ALLOWED_DECISIONS)}"
            )
