"""
WorldExecutorDryRun — simulates world actions only. Never executes real actions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .obsidia_gateway import GatewayDecision


@dataclass
class DryRunResult:
    action_id: str
    simulated: bool = True
    executed: bool = False
    reason: str = "DRY_RUN_ONLY_V4"
    gateway_result: str = ""

    def assert_not_executed(self) -> None:
        if self.executed:
            raise AssertionError("WORLD_EXECUTOR_REAL_EXECUTION_FORBIDDEN")


def execute_dry_run(action_id: str, gateway_decision: GatewayDecision) -> DryRunResult:
    result = DryRunResult(
        action_id=action_id,
        simulated=True,
        executed=False,
        reason="DRY_RUN_ONLY_V4",
        gateway_result=gateway_decision.gate_result,
    )
    result.assert_not_executed()
    return result
