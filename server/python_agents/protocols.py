from __future__ import annotations

from .aggregation import aggregate_bank, aggregate_ecom, aggregate_trading
from .contracts import BankState, CanonicalDecisionEnvelope, EcomState, TradingState
from .domains.bank_agents import build_bank_agents
from .domains.ecom_agents import build_ecom_agents
from .domains.meta_agents import build_meta_agents
from .domains.trading_agents import build_trading_agents
from .guard import GuardX108
from .registry import build_agent_registry as _build_registry


def build_agent_registry():
    return _build_registry()


def _apply_meta_agents(aggregate):
    for meta_agent in build_meta_agents():
        meta_vote = meta_agent.evaluate(aggregate)
        aggregate.contradictions.extend(meta_vote.contradictions)
        aggregate.unknowns.extend(meta_vote.unknowns)
        aggregate.risk_flags.extend(meta_vote.risk_flags)
        aggregate.evidence_refs.append(f"meta:{meta_vote.agent_id}")
    return aggregate


def run_trading_pipeline(state: TradingState) -> CanonicalDecisionEnvelope:
    aggregate = aggregate_trading([a.evaluate(state) for a in build_trading_agents()])
    aggregate = _apply_meta_agents(aggregate)
    return GuardX108().decide(aggregate)


def run_bank_pipeline(state: BankState) -> CanonicalDecisionEnvelope:
    aggregate = aggregate_bank([a.evaluate(state) for a in build_bank_agents()])
    aggregate = _apply_meta_agents(aggregate)
    return GuardX108().decide(aggregate)


def run_ecom_pipeline(state: EcomState) -> CanonicalDecisionEnvelope:
    aggregate = aggregate_ecom([a.evaluate(state) for a in build_ecom_agents()])
    aggregate = _apply_meta_agents(aggregate)
    return GuardX108().decide(aggregate)
