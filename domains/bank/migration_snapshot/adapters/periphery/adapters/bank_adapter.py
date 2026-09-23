from __future__ import annotations

from periphery.common import ActionCandidate
from sigma.contracts import BankState

BANK_STATE_KEYS = {
    "transaction_type", "amount", "channel", "counterparty_known", "counterparty_age_days",
    "account_balance", "available_cash", "historical_avg_amount", "behavior_shift_score",
    "fraud_score", "policy_limit", "affordability_score", "urgency_score",
    "identity_mismatch_score", "narrative_conflict_score", "device_trust_score",
    "recent_failed_attempts", "elapsed_s", "min_required_elapsed_s",
}

DEFAULT_BANK_STATE = {
    "transaction_type": "transfer",
    "amount": 10.0,
    "channel": "demo",
    "counterparty_known": True,
    "counterparty_age_days": 60,
    "account_balance": 1000.0,
    "available_cash": 1000.0,
    "historical_avg_amount": 25.0,
    "behavior_shift_score": 0.1,
    "fraud_score": 0.05,
    "policy_limit": 1000.0,
    "affordability_score": 0.9,
    "urgency_score": 0.1,
    "identity_mismatch_score": 0.0,
    "narrative_conflict_score": 0.0,
    "device_trust_score": 1.0,
    "recent_failed_attempts": 0,
    "elapsed_s": 108.0,
    "min_required_elapsed_s": 108.0,
}

def build_bank_action(payload: dict) -> ActionCandidate:
    return ActionCandidate(
        action_id=payload.get("action_id", "bank-action"),
        domain="bank",
        actor_id=payload.get("actor_id", "bank-agent"),
        intent=payload.get("intent", "bank_transaction_review"),
        action_type=payload.get("action_type", "payment_or_transfer"),
        irreversible=bool(payload.get("irreversible", True)),
        timestamp_plan=payload.get("timestamp_plan", ""),
        timestamp_exec=payload.get("timestamp_exec"),
        payload=payload,
    )

def build_bank_state(payload: dict) -> BankState:
    data = dict(DEFAULT_BANK_STATE)
    data.update({k: v for k, v in payload.items() if k in BANK_STATE_KEYS})
    return BankState(**data)
