"""
Transaction Simulator — dry-run only. No real transactions sent.
Simulates gas estimate, risk, outcome. Never broadcasts to any chain.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TransactionSimulationResult:
    tx_id: str
    chain_id: str
    action_type: str
    simulated: bool = True
    broadcast_attempted: bool = False
    real_tx_sent: bool = False
    estimated_gas: int = 0
    estimated_cost_usd: float = 0.0
    risk_score: float = 0.0
    risk_flags: list[str] = field(default_factory=list)
    simulation_status: str = "DRY_RUN_ONLY"

    def to_dict(self) -> dict[str, Any]:
        return {
            "tx_id": self.tx_id,
            "chain_id": self.chain_id,
            "action_type": self.action_type,
            "simulated": self.simulated,
            "broadcast_attempted": self.broadcast_attempted,
            "real_tx_sent": self.real_tx_sent,
            "estimated_gas": self.estimated_gas,
            "estimated_cost_usd": self.estimated_cost_usd,
            "risk_score": self.risk_score,
            "risk_flags": self.risk_flags,
            "simulation_status": self.simulation_status,
        }


def simulate_transaction(
    tx_id: str,
    chain_id: str,
    action_type: str,
    value_eth: float = 0.0,
    gas_limit: int = 21000,
) -> TransactionSimulationResult:
    risk_flags = []
    risk_score = 0.0

    if action_type.upper() in ("DEPLOY", "SMART_CONTRACT_DEPLOY"):
        risk_flags.append("CONTRACT_DEPLOY_HIGH_RISK")
        risk_score = max(risk_score, 0.9)

    if value_eth > 1.0:
        risk_flags.append("HIGH_VALUE_TRANSFER")
        risk_score = max(risk_score, 0.7)

    if chain_id.lower() in ("mainnet", "ethereum", "1"):
        risk_flags.append("MAINNET_BLOCKED_V4")
        risk_score = max(risk_score, 1.0)

    estimated_cost = (gas_limit / 1_000_000) * 50 * value_eth if value_eth > 0 else 0.0

    return TransactionSimulationResult(
        tx_id=tx_id,
        chain_id=chain_id,
        action_type=action_type,
        simulated=True,
        broadcast_attempted=False,
        real_tx_sent=False,
        estimated_gas=gas_limit,
        estimated_cost_usd=estimated_cost,
        risk_score=risk_score,
        risk_flags=risk_flags,
        simulation_status="DRY_RUN_ONLY",
    )
