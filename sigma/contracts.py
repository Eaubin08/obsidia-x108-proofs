from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Domain(str, Enum):
    TRADING = "trading"
    BANK = "bank"
    ECOM = "ecom"
    META = "meta"


class Layer(str, Enum):
    OBSERVATION = "observation"
    INTERPRETATION = "interpretation"
    CONTRADICTION = "contradiction"
    PROOF = "proof"
    AGGREGATION = "aggregation"
    GOVERNANCE = "governance"


class SourceTag(str, Enum):
    PYTHON = "python"
    DB_REAL = "db_real"
    WS_REAL = "ws_real"
    PREVIEW_LOCAL = "preview_local"
    OS4_LOCAL_FALLBACK = "os4_local_fallback"
    CANONICAL_FRAMEWORK = "canonical_framework"


class Severity(str, Enum):
    S0 = "S0"
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"
    S4 = "S4"


class X108Gate(str, Enum):
    ALLOW = "ALLOW"
    HOLD = "HOLD"
    BLOCK = "BLOCK"


@dataclass
class AgentVote:
    agent_id: str
    domain: Domain
    layer: Layer
    claim: str
    confidence: float
    severity_hint: Severity
    contradictions: List[str] = field(default_factory=list)
    unknowns: List[str] = field(default_factory=list)
    risk_flags: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    proposed_verdict: str = "HOLD"
    source: SourceTag = SourceTag.CANONICAL_FRAMEWORK
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DomainAggregate:
    domain: Domain
    market_verdict: str
    confidence: float
    contradictions: List[str] = field(default_factory=list)
    unknowns: List[str] = field(default_factory=list)
    risk_flags: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    source: SourceTag = SourceTag.CANONICAL_FRAMEWORK
    agent_votes: List[AgentVote] = field(default_factory=list)
    extra_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CanonicalDecisionEnvelope:
    domain: str
    market_verdict: str
    confidence: float
    contradictions: List[str]
    unknowns: List[str]
    risk_flags: List[str]
    x108_gate: str
    reason_code: str
    severity: str
    decision_id: str
    trace_id: str
    ticket_required: bool
    ticket_id: Optional[str]
    attestation_ref: Optional[str]
    source: str
    evidence_refs: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    raw_engine: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TradingState:
    symbol: str
    prices: List[float]
    highs: List[float]
    lows: List[float]
    volumes: List[float]
    spreads_bps: List[float]
    sentiment_scores: List[float]
    event_risk_scores: List[float]
    btc_reference_prices: List[float]
    exposure: float = 0.0
    drawdown: float = 0.0
    order_book_imbalance: float = 0.0
    order_book_depth: float = 1.0
    slippage_bps: float = 3.0


@dataclass
class BankState:
    transaction_type: str
    amount: float
    channel: str
    counterparty_known: bool
    counterparty_age_days: int
    account_balance: float
    available_cash: float
    historical_avg_amount: float
    behavior_shift_score: float
    fraud_score: float
    policy_limit: float
    affordability_score: float
    urgency_score: float
    identity_mismatch_score: float
    narrative_conflict_score: float
    device_trust_score: float = 1.0
    recent_failed_attempts: int = 0
    elapsed_s: float = 0.0
    min_required_elapsed_s: float = 108.0


@dataclass
class EcomState:
    session_id: str
    traffic_quality: float
    basket_intent_score: float
    stock_ok: bool
    margin_rate: float
    roas: float
    conversion_readiness: float
    fulfillment_risk: float
    customer_trust: float
    intent_conflict_score: float
    checkout_friction_score: float
    merchant_policy_score: float
    basket_value: float
    ad_spend: float
    order_value: float
    x108_compliance_rate: float
