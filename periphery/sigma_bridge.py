from __future__ import annotations

from typing import Any

from .common import PeripheralSignalPacket

from sigma.aggregation import (
    aggregate_bank,
    aggregate_trading,
    aggregate_ecom,
    aggregate_gps_defense_aviation,
)
from sigma.domains.bank_agents import build_bank_agents
from sigma.domains.trading_agents import build_trading_agents
from sigma.domains.ecom_agents import build_ecom_agents
from sigma.domains.gps_defense_aviation_agents import build_gps_defense_aviation_agents
from sigma.domains.meta_agents import THERMO_CANONICAL_KEYS, build_meta_agents
from sigma.guard import GuardX108


def _merge_periphery_into_aggregate(aggregate: Any, packet: PeripheralSignalPacket) -> Any:
    packet.assert_non_sovereign()

    if "truth_score" in aggregate.extra_metrics and "domain_truth_score" not in aggregate.extra_metrics:
        aggregate.extra_metrics["domain_truth_score"] = float(aggregate.extra_metrics["truth_score"])
    if "sigma_score" in aggregate.extra_metrics and "domain_sigma_score" not in aggregate.extra_metrics:
        aggregate.extra_metrics["domain_sigma_score"] = float(aggregate.extra_metrics["sigma_score"])

    thermo_packet_keys = [k for k in THERMO_CANONICAL_KEYS if k in packet.extra_metrics]
    if thermo_packet_keys:
        aggregate.extra_metrics["thermo_packet_keys"] = thermo_packet_keys

    aggregate.contradictions.extend(packet.contradictions)
    aggregate.unknowns.extend(packet.unknowns)
    aggregate.risk_flags.extend(packet.risk_flags)
    aggregate.evidence_refs.extend(packet.evidence_refs)
    aggregate.evidence_refs.append(f"periphery:{packet.action_id}:{packet.recommended_gate}")
    aggregate.extra_metrics.update(packet.extra_metrics)
    aggregate.extra_metrics["periphery_recommended_gate"] = packet.recommended_gate
    aggregate.extra_metrics["periphery_can_emit_act"] = packet.can_emit_act

    if packet.recommended_gate == "HOLD":
        aggregate.unknowns.append("PERIPHERY_RECOMMENDS_HOLD")
    elif packet.recommended_gate == "BLOCK_CANDIDATE":
        aggregate.contradictions.append("PERIPHERY_BLOCK_CANDIDATE")

    aggregate.unknowns = sorted(set(aggregate.unknowns))
    aggregate.risk_flags = sorted(set(aggregate.risk_flags))
    aggregate.contradictions = sorted(set(aggregate.contradictions))
    aggregate.evidence_refs = sorted(set(aggregate.evidence_refs))
    return aggregate


def _apply_meta_agents(aggregate: Any) -> Any:
    for meta_agent in build_meta_agents():
        meta_vote = meta_agent.evaluate(aggregate)
        aggregate.contradictions.extend(meta_vote.contradictions)
        aggregate.unknowns.extend(meta_vote.unknowns)
        aggregate.risk_flags.extend(meta_vote.risk_flags)
        aggregate.evidence_refs.append(f"meta:{meta_vote.agent_id}")

    thermo_eval = aggregate.extra_metrics.get("sigma_thermo_evaluation")
    if isinstance(thermo_eval, dict):
        status = thermo_eval.get("status")
        if status and status != "NOT_PRESENT":
            aggregate.evidence_refs.append(f"thermo_sigma:{status}")

    aggregate.unknowns = sorted(set(aggregate.unknowns))
    aggregate.risk_flags = sorted(set(aggregate.risk_flags))
    aggregate.contradictions = sorted(set(aggregate.contradictions))
    aggregate.evidence_refs = sorted(set(aggregate.evidence_refs))
    return aggregate


def run_bank_with_periphery(state: Any, packet: PeripheralSignalPacket) -> Any:
    aggregate = aggregate_bank([agent.evaluate(state) for agent in build_bank_agents()])
    aggregate = _merge_periphery_into_aggregate(aggregate, packet)
    aggregate = _apply_meta_agents(aggregate)
    return GuardX108().decide(aggregate)


def run_trading_with_periphery(state: Any, packet: PeripheralSignalPacket) -> Any:
    aggregate = aggregate_trading([agent.evaluate(state) for agent in build_trading_agents()])
    aggregate = _merge_periphery_into_aggregate(aggregate, packet)
    aggregate = _apply_meta_agents(aggregate)
    return GuardX108().decide(aggregate)


def run_ecom_with_periphery(state: Any, packet: PeripheralSignalPacket) -> Any:
    aggregate = aggregate_ecom([agent.evaluate(state) for agent in build_ecom_agents()])
    aggregate = _merge_periphery_into_aggregate(aggregate, packet)
    aggregate = _apply_meta_agents(aggregate)
    return GuardX108().decide(aggregate)


def run_gps_with_periphery(state: Any, packet: PeripheralSignalPacket) -> Any:
    aggregate = aggregate_gps_defense_aviation(
        [agent.evaluate(state) for agent in build_gps_defense_aviation_agents()]
    )
    aggregate = _merge_periphery_into_aggregate(aggregate, packet)
    aggregate = _apply_meta_agents(aggregate)
    return GuardX108().decide(aggregate)
