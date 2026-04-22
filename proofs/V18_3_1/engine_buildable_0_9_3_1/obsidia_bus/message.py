from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from enum import Enum

class MsgIntentType(str, Enum):
    PROPOSE = "PROPOSE"
    ACTION = "ACTION"

@dataclass
class IntentMsg:
    type: MsgIntentType
    name: str
    payload: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContextMsg:
    state: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    resources: Dict[str, Any] = field(default_factory=dict)
    history_ref: Optional[str] = None

@dataclass
class GovernanceMsg:
    irreversible: bool = False
    # Internal knobs (optional)
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
    mode: str  # proof|simu|live
    actor: ActorMsg = field(default_factory=ActorMsg)

@dataclass
class DecisionMsg:
    decision: str  # BLOCK|HOLD|ACT
    trace_id: str
    reason_code: str
    reason_message: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    artifacts_hash: Optional[str] = None
