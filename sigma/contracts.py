from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Domain(str, Enum):
    TRADING = "trading"
    BANK = "bank"
    ECOM = "ecom"
    META = "meta"
    GPS_DEFENSE_AVIATION = "gps_defense_aviation"


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

    def __post_init__(self) -> None:
        def require_text(name: str, value: Any) -> str:
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
            return value.strip()

        def require_bool(name: str, value: Any) -> bool:
            if not isinstance(value, bool):
                raise ValueError(f"{name} must be a boolean")
            return value

        def require_int_ge(name: str, value: Any, minimum: int = 0) -> int:
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{name} must be an integer")
            if value < minimum:
                raise ValueError(f"{name} must be >= {minimum}")
            return value

        def require_number(
            name: str,
            value: Any,
            minimum: float | None = None,
            maximum: float | None = None,
            strict_min: bool = False,
        ) -> float:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{name} must be a number")
            value = float(value)
            if math.isnan(value) or math.isinf(value):
                raise ValueError(f"{name} must be finite")
            if minimum is not None:
                if strict_min:
                    if value <= minimum:
                        raise ValueError(f"{name} must be > {minimum}")
                elif value < minimum:
                    raise ValueError(f"{name} must be >= {minimum}")
            if maximum is not None and value > maximum:
                raise ValueError(f"{name} must be <= {maximum}")
            return value

        self.transaction_type = require_text("transaction_type", self.transaction_type)
        self.channel = require_text("channel", self.channel)
        self.counterparty_known = require_bool("counterparty_known", self.counterparty_known)
        self.counterparty_age_days = require_int_ge("counterparty_age_days", self.counterparty_age_days, 0)
        self.recent_failed_attempts = require_int_ge("recent_failed_attempts", self.recent_failed_attempts, 0)

        self.amount = require_number("amount", self.amount, minimum=0.0, strict_min=True)
        self.account_balance = require_number("account_balance", self.account_balance, minimum=0.0)
        self.available_cash = require_number("available_cash", self.available_cash, minimum=0.0)
        self.historical_avg_amount = require_number("historical_avg_amount", self.historical_avg_amount, minimum=0.0)
        self.policy_limit = require_number("policy_limit", self.policy_limit, minimum=0.0, strict_min=True)

        self.behavior_shift_score = require_number("behavior_shift_score", self.behavior_shift_score, minimum=0.0, maximum=1.0)
        self.fraud_score = require_number("fraud_score", self.fraud_score, minimum=0.0, maximum=1.0)
        self.affordability_score = require_number("affordability_score", self.affordability_score, minimum=0.0, maximum=1.0)
        self.urgency_score = require_number("urgency_score", self.urgency_score, minimum=0.0, maximum=1.0)
        self.identity_mismatch_score = require_number("identity_mismatch_score", self.identity_mismatch_score, minimum=0.0, maximum=1.0)
        self.narrative_conflict_score = require_number("narrative_conflict_score", self.narrative_conflict_score, minimum=0.0, maximum=1.0)
        self.device_trust_score = require_number("device_trust_score", self.device_trust_score, minimum=0.0, maximum=1.0)

        self.elapsed_s = require_number("elapsed_s", self.elapsed_s, minimum=0.0)
        self.min_required_elapsed_s = require_number("min_required_elapsed_s", self.min_required_elapsed_s, minimum=0.0)


@dataclass

@dataclass
class GpsDefenseAviationState:
    mission_id: str
    gps_available: bool
    inertial_available: bool
    radio_available: bool
    elapsed_s: float = 0.0
    min_required_elapsed_s: float = 108.0
    position_confidence: float = 1.0
    trajectory_drift_score: float = 0.0
    source_conflict_score: float = 0.0
    brownout_score: float = 0.0
    time_skew_score: float = 0.0
    environment_risk_score: float = 0.0
    rollback_possible: bool = True
    attestation_ready: bool = True


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