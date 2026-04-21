from __future__ import annotations

import hashlib
from collections import defaultdict
from typing import Iterable

from .contracts import AgentVote, Domain, DomainAggregate


def _hash_ref(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _common(votes: list[AgentVote]):
    contradictions = []
    unknowns = []
    risk_flags = []
    evidence_refs = []
    for v in votes:
        contradictions.extend(v.contradictions)
        unknowns.extend(v.unknowns)
        risk_flags.extend(v.risk_flags)
        evidence_refs.append(_hash_ref(f"{v.agent_id}:{v.claim}:{v.proposed_verdict}"))
    return contradictions, unknowns, risk_flags, evidence_refs


def aggregate_trading(votes: Iterable[AgentVote]) -> DomainAggregate:
    votes = list(votes)
    scores = defaultdict(float)
    for v in votes:
        scores[v.proposed_verdict] += v.confidence
    buy = scores.get("BUY", 0.0)
    sell = scores.get("SELL", 0.0)
    hold = scores.get("HOLD", 0.0)
    market_verdict = "EXECUTE_LONG" if buy > max(sell, hold) else "EXECUTE_SHORT" if sell > max(buy, hold) else "REVIEW"
    confidence = max(buy, sell, hold) / max(1.0, sum(scores.values()))
    contradictions, unknowns, risk_flags, evidence_refs = _common(votes)
    extra_metrics = {"buy_score": buy, "sell_score": sell, "hold_score": hold, "proof_ready": True, "deterministic": True}
    return DomainAggregate(Domain.TRADING, market_verdict, confidence, contradictions, unknowns, risk_flags, evidence_refs, agent_votes=votes, extra_metrics=extra_metrics)


def aggregate_bank(votes: Iterable[AgentVote]) -> DomainAggregate:
    votes = list(votes)
    scores = defaultdict(float)
    for v in votes:
        scores[v.proposed_verdict] += v.confidence
    auth = scores.get("AUTHORIZE", 0.0)
    analyze = scores.get("ANALYZE", 0.0)
    block = scores.get("BLOCK", 0.0)
    market_verdict = "BLOCK" if block > max(auth, analyze) else "AUTHORIZE" if auth > analyze else "ANALYZE"
    confidence = max(auth, analyze, block) / max(1.0, sum(scores.values()))
    contradictions, unknowns, risk_flags, evidence_refs = _common(votes)
    extra_metrics = {"authorize_score": auth, "analyze_score": analyze, "block_score": block, "proof_ready": True, "deterministic": True}
    return DomainAggregate(Domain.BANK, market_verdict, confidence, contradictions, unknowns, risk_flags, evidence_refs, agent_votes=votes, extra_metrics=extra_metrics)


def aggregate_ecom(votes: Iterable[AgentVote]) -> DomainAggregate:
    votes = list(votes)
    scores = defaultdict(float)
    for v in votes:
        scores[v.proposed_verdict] += v.confidence
    pay = scores.get("PAY", 0.0)
    wait = scores.get("WAIT", 0.0)
    refuse = scores.get("REFUSE", 0.0)
    market_verdict = "REFUSE" if refuse > max(pay, wait) else "PAY" if pay > wait else "WAIT"
    confidence = max(pay, wait, refuse) / max(1.0, sum(scores.values()))
    contradictions, unknowns, risk_flags, evidence_refs = _common(votes)
    extra_metrics = {"pay_score": pay, "wait_score": wait, "refuse_score": refuse, "proof_ready": True, "deterministic": True}
    return DomainAggregate(Domain.ECOM, market_verdict, confidence, contradictions, unknowns, risk_flags, evidence_refs, agent_votes=votes, extra_metrics=extra_metrics)
