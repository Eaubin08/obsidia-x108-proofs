"""
CG9 Provider Cognitive Binder
Provider Lifecycle Manager V0

Bounded provider lifecycle state machine.

Invariant:
- Provider lifecycle only
- No execution authority
- No decision authority
- No memory write
- No kernel mutation
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict
import uuid


class ProviderLifecycleError(Exception):
    pass


class ProviderLifecycleState:
    INSTALLED = "INSTALLED"
    DECLARED = "DECLARED"
    VALIDATED = "VALIDATED"
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    REMOVED = "REMOVED"


_ALLOWED_TRANSITIONS = {
    ProviderLifecycleState.INSTALLED: {
        ProviderLifecycleState.DECLARED,
    },
    ProviderLifecycleState.DECLARED: {
        ProviderLifecycleState.VALIDATED,
    },
    ProviderLifecycleState.VALIDATED: {
        ProviderLifecycleState.ENABLED,
    },
    ProviderLifecycleState.ENABLED: {
        ProviderLifecycleState.DISABLED,
    },
    ProviderLifecycleState.DISABLED: {
        ProviderLifecycleState.ENABLED,
        ProviderLifecycleState.REMOVED,
    },
    ProviderLifecycleState.REMOVED: set(),
}


@dataclass
class ProviderLifecycleManager:
    provider_id: str

    lifecycle_id: str = field(
        default_factory=lambda: f"lifecycle-{uuid.uuid4().hex[:16]}"
    )

    state: str = ProviderLifecycleState.INSTALLED

    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    history: list = field(default_factory=list)

    execution_authority: bool = False
    decision_authority: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False


    def transition(self, target_state: str):
        allowed = _ALLOWED_TRANSITIONS.get(
            self.state,
            set()
        )

        if target_state not in allowed:
            raise ProviderLifecycleError(
                f"Invalid lifecycle transition {self.state} -> {target_state}"
            )

        self.history.append(
            {
                "from": self.state,
                "to": target_state,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        self.state = target_state


    def declare(self):
        self.transition(
            ProviderLifecycleState.DECLARED
        )


    def validate(self):
        self.transition(
            ProviderLifecycleState.VALIDATED
        )


    def enable(self):
        self.transition(
            ProviderLifecycleState.ENABLED
        )


    def disable(self):
        self.transition(
            ProviderLifecycleState.DISABLED
        )


    def remove(self):
        self.transition(
            ProviderLifecycleState.REMOVED
        )


    def can_invoke(self) -> bool:
        return self.state == ProviderLifecycleState.ENABLED


    def to_dict(self) -> Dict:
        return {
            "lifecycle_id": self.lifecycle_id,
            "provider_id": self.provider_id,
            "state": self.state,
            "execution_authority": self.execution_authority,
            "decision_authority": self.decision_authority,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
        }
