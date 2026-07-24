"""agents.contracts — compatibility shim for sigma.contracts.

Re-exports all public types from sigma.contracts so that imports of the form
`from agents.contracts import TradingState` continue to work.

No IO. No network. No ACT. DECISION_AUTHORITY=KX108_ONLY.
"""
from sigma.contracts import (  # noqa: F401
    AgentVote,
    BankState,
    CanonicalDecisionEnvelope,
    Domain,
    DomainAggregate,
    EcomState,
    GpsDefenseAviationState,
    Layer,
    Severity,
    SmartAttribute,
    SourceTag,
    TradingState,
    UniversalBase,
    X108Gate,
)
