"""
Shared, honest domain fixtures for the R7 multi-domain proofs.

Every state here is a REAL sigma domain state producing a REAL GuardX108
verdict. Nothing is monkeypatched and no verdict is forced: where a domain
cannot naturally reach a gate, that is recorded as a fact rather than
engineered around.

Observed capability of each canonical bridge:

    bank     ALLOW / HOLD / BLOCK
    gps      ALLOW / HOLD          (no GPS agent emits a contradiction,
                                    so BLOCK is unreachable from the domain)
    trading  ALLOW / HOLD          (idem)
    ecom     HOLD only             (EcomState carries only session_id while
                                    EcomProofAgent reads x108_compliance_rate
                                    and order_value — the contract cannot be
                                    satisfied, so the domain fails closed)
"""

from __future__ import annotations

from periphery.common import ActionCandidate
from sigma.contracts import (
    BankState,
    EcomState,
    GpsDefenseAviationState,
    TradingState,
)

# Gates each domain can actually reach through its real agents.
DOMAIN_REACHABLE_GATES = {
    "bank": ("ALLOW", "HOLD", "BLOCK"),
    "gps_defense_aviation": ("ALLOW", "HOLD"),
    "trading": ("ALLOW", "HOLD"),
    "ecom": ("HOLD",),
}


def action_for(domain: str, action_id: str, gross_value: float = 500.0) -> ActionCandidate:
    intents = {
        "bank": ("transfer_review", "transfer"),
        "gps_defense_aviation": ("route_review", "navigation"),
        "trading": ("order_review", "order"),
        "ecom": ("order_review", "order"),
    }
    intent, action_type = intents[domain]
    return ActionCandidate(
        action_id=action_id,
        domain=domain,
        actor_id="r7-integration",
        intent=intent,
        action_type=action_type,
        irreversible=False,
        timestamp_plan="2026-09-03T00:00:00Z",
        payload={"gross_value": gross_value},
    )


# ── BANK ────────────────────────────────────────────────────────────────────


def bank_state(**over) -> BankState:
    base = dict(
        transaction_type="TRANSFER", amount=200.0, channel="web",
        counterparty_known=True, counterparty_age_days=90,
        account_balance=1000.0, available_cash=800.0,
        historical_avg_amount=150.0, behavior_shift_score=0.1,
        fraud_score=0.05, policy_limit=5000.0, affordability_score=0.85,
        urgency_score=0.2, identity_mismatch_score=0.0,
        narrative_conflict_score=0.0, device_trust_score=0.9,
        recent_failed_attempts=0, elapsed_s=200.0,
    )
    base.update(over)
    return BankState(**base)


def bank_allow() -> BankState:
    return bank_state()


def bank_hold() -> BankState:
    """Genuinely over-committed: cash and limit pressure."""
    return bank_state(
        amount=99999.0, available_cash=1.0, account_balance=1.0,
        affordability_score=0.01,
    )


def bank_block() -> BankState:
    """Genuinely fraudulent: fraud pattern plus contradictions."""
    return bank_state(
        fraud_score=0.99, identity_mismatch_score=0.9,
        narrative_conflict_score=0.9, recent_failed_attempts=9,
    )


# ── GPS ─────────────────────────────────────────────────────────────────────


def gps_state(**over) -> GpsDefenseAviationState:
    base = dict(
        mission_id="R7_MISSION_001", flight_id="R7_FLIGHT_001",
        altitude=10000.0, ground_speed=850.0, gps_status="ACTIVE",
        satellites_count=12, signal_noise_ratio=48.0, gps_available=True,
        inertial_available=True, radio_available=True,
        trajectory_drift_score=0.01,
        attestation_ready=True, rollback_possible=True,
    )
    base.update(over)
    return GpsDefenseAviationState(**base)


def gps_allow() -> GpsDefenseAviationState:
    return gps_state()


def gps_hold() -> GpsDefenseAviationState:
    """Genuinely degraded navigation: signal lost, drift high."""
    return gps_state(
        gps_status="OFFLINE", satellites_count=0, signal_noise_ratio=1.0,
        gps_available=False, inertial_available=False, radio_available=False,
        trajectory_drift_score=0.99,
    )


# ── TRADING ─────────────────────────────────────────────────────────────────


def _series(n: int = 70):
    return [1.080 + i * 0.001 for i in range(n)]


def trading_allow() -> TradingState:
    prices = _series()
    return TradingState(
        symbol="EURUSD",
        prices=prices,
        highs=[p + 0.002 for p in prices],
        lows=[p - 0.002 for p in prices],
        volumes=[1000.0] * 70,
        spreads_bps=[5.0] * 70,
        sentiment_scores=[0.6] * 10,
        event_risk_scores=[0.1] * 10,
        btc_reference_prices=[30000.0] * 70,
    )


def trading_hold() -> TradingState:
    """Genuinely unreadable market: no series at all."""
    return TradingState(
        symbol="R7EMPTY", prices=[], highs=[], lows=[], volumes=[],
        spreads_bps=[], sentiment_scores=[], event_risk_scores=[],
        btc_reference_prices=[],
    )


# ── ECOM ────────────────────────────────────────────────────────────────────


def ecom_state() -> EcomState:
    """
    The only state EcomState can express. Its proof agent reads fields the
    contract does not carry, so the domain fails closed on HOLD. Nothing is
    fabricated to move it.
    """
    return EcomState(session_id="r7-ecom-session")
