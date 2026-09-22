"""
CG9 Provider Cognitive Binder
Provider Execution Session V0

Bounded execution lifecycle container.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid


class ProviderExecutionSessionError(Exception):
    pass


class ExecutionState:
    CREATED = "CREATED"
    AUTHORIZED = "AUTHORIZED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    CLOSED = "CLOSED"


_ALLOWED_TRANSITIONS = {
    ExecutionState.CREATED: {
        ExecutionState.AUTHORIZED,
    },
    ExecutionState.AUTHORIZED: {
        ExecutionState.RUNNING,
    },
    ExecutionState.RUNNING: {
        ExecutionState.COMPLETED,
    },
    ExecutionState.COMPLETED: {
        ExecutionState.CLOSED,
    },
    ExecutionState.CLOSED: set(),
}


@dataclass
class ProviderExecutionSession:
    mission_submission_id: str
    authorization_receipt_id: str
    provider_id: str
    adapter_id: str
    capability: str

    session_id: str = field(
        default_factory=lambda: f"exec-{uuid.uuid4().hex[:16]}"
    )

    state: str = ExecutionState.CREATED

    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    closed_at: Optional[str] = None

    result_ref: Optional[str] = None

    execution_authority: bool = False
    kx_authority: bool = True
    memory_write: bool = False
    emits_act: bool = False
    kernel_mutation: bool = False


    def transition(self, target_state: str):
        allowed = _ALLOWED_TRANSITIONS.get(
            self.state,
            set()
        )

        if target_state not in allowed:
            raise ProviderExecutionSessionError(
                f"Invalid transition {self.state} -> {target_state}"
            )

        self.state = target_state

        now = datetime.now(timezone.utc).isoformat()

        if target_state == ExecutionState.RUNNING:
            self.started_at = now

        elif target_state == ExecutionState.COMPLETED:
            self.completed_at = now

        elif target_state == ExecutionState.CLOSED:
            self.closed_at = now


    def authorize(self):
        self.transition(
            ExecutionState.AUTHORIZED
        )


    def start(self):
        self.transition(
            ExecutionState.RUNNING
        )


    def complete(self, result_ref: str):
        if not result_ref:
            raise ProviderExecutionSessionError(
                "result_ref required"
            )

        self.result_ref = result_ref

        self.transition(
            ExecutionState.COMPLETED
        )


    def close(self):
        self.transition(
            ExecutionState.CLOSED
        )


    def to_dict(self):
        return {
            "session_id": self.session_id,
            "mission_submission_id": self.mission_submission_id,
            "authorization_receipt_id": self.authorization_receipt_id,
            "provider_id": self.provider_id,
            "adapter_id": self.adapter_id,
            "capability": self.capability,
            "state": self.state,
            "result_ref": self.result_ref,
            "execution_authority": self.execution_authority,
            "kx_authority": self.kx_authority,
            "memory_write": self.memory_write,
            "emits_act": self.emits_act,
            "kernel_mutation": self.kernel_mutation,
        }
