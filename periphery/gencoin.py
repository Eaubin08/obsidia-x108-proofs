from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .os3_ticket import ticket_is_valid

@dataclass
class GencoinMintCandidate:
    action_id: str
    os3_ticket_id: str
    x108_gate: str
    proof_valid: bool
    data_ok: bool
    memory_stable: bool
    energy_stable: bool
    oc_stable: bool
    permission_ok: bool
    economic_ok: bool
    gross_value: float
    total_debt: float
    gencoin_candidate: float
    mint_allowed: bool


def compute_gencoin(action_candidate: Any, packet: Any, ticket: Any) -> GencoinMintCandidate:
    m = packet.extra_metrics

    gate_value = str(ticket.x108_gate).upper()
    x108_allow = gate_value == "ALLOW"
    proof_valid = ticket_is_valid(ticket)

    data_ok = m.get("freshness_score", 1.0) >= 0.75
    memory_stable = m.get("memory_status", "STABLE") == "STABLE"
    energy_stable = (
        m.get("energy_efficiency", 1.0) >= 0.2
        and m.get("thermo_debt", 0.0) <= 1.0
    )
    oc_stable = bool(m.get("oc_stable", True))
    permission_ok = bool(m.get("permission_ok", True))
    economic_ok = bool(m.get("economic_ok", True))

    gross_value = float(action_candidate.payload.get("gross_value", 0.0))
    total_debt = float(action_candidate.payload.get("total_debt", 0.0))
    net = max(0.0, gross_value - total_debt)

    hard_ok = all([
        x108_allow,
        proof_valid,
        data_ok,
        memory_stable,
        energy_stable,
        oc_stable,
        permission_ok,
        economic_ok,
    ])

    gc = net if hard_ok else 0.0

    return GencoinMintCandidate(
        action_id=action_candidate.action_id,
        os3_ticket_id=ticket.ticket_id,
        x108_gate=gate_value,
        proof_valid=proof_valid,
        data_ok=data_ok,
        memory_stable=memory_stable,
        energy_stable=energy_stable,
        oc_stable=oc_stable,
        permission_ok=permission_ok,
        economic_ok=economic_ok,
        gross_value=gross_value,
        total_debt=total_debt,
        gencoin_candidate=gc,
        mint_allowed=gc > 0.0,
    )
