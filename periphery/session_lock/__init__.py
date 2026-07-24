"""periphery.session_lock — heartbeat session lock manager (V17 PART_A).

Isolated component. Disabled by default. No runtime wiring.
DECISION_AUTHORITY=KX108_ONLY. No ACT. No real reclaim.
"""
from periphery.session_lock.heartbeat_lock_manager import (  # noqa: F401
    FailureCode,
    HeartbeatConfig,
    HeartbeatLockManager,
    HeartbeatRuntimeState,
    LockClassification,
    OperationResult,
)
