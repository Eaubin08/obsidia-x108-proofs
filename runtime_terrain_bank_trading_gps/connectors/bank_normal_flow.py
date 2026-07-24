from __future__ import annotations

import os
import random
import time
from typing import Any

import requests


DEFAULT_API_BASE = os.environ.get("OBSIDIA_API_BASE", "http://127.0.0.1:8000")
BANK_ENDPOINT = "/api/periphery/monitoring/adapters/bank"


def build_bank_payload() -> dict[str, Any]:
    return {
        "payload": {
            "action_id": "bank-normal-flow",
            "actor_id": "bank-connector",
            "intent": "bank_transaction_review",
            "action_type": "payment_or_transfer",
            "irreversible": True,
            "account_balance": 5000.0,
            "affordability_score": 0.85,
            "amount": round(random.uniform(10, 500), 2),
            "available_cash": 4500.0,
            "behavior_shift_score": 0.0,
            "channel": "MOBILE",
            "counterparty_age_days": 365,
            "counterparty_known": True,
            "device_trust_score": 0.98,
            "fraud_score": 0.02,
            "historical_avg_amount": 150.0,
            "identity_mismatch_score": 0.0,
            "narrative_conflict_score": 0.0,
            "policy_limit": 1000.0,
            "transaction_type": "TRANSFER",
            "urgency_score": 0.05,
        }
    }


def send_bank_payload(api_base: str = DEFAULT_API_BASE, timeout: int = 10):
    url = f"{api_base.rstrip('/')}{BANK_ENDPOINT}"
    return requests.post(url, json=build_bank_payload(), timeout=timeout)


def run_normal_bank(api_base: str = DEFAULT_API_BASE):
    print(f"🏦 [BANK-FULL] Flux certifié vers {api_base}{BANK_ENDPOINT}")

    while True:
        try:
            res = send_bank_payload(api_base=api_base, timeout=10)
            if res.status_code == 200:
                data = res.json().get("data", res.json())
                env = data.get("domain_sigma_envelope", {})
                print(
                    "✅ [BANK] Sigma envelope | "
                    f"domain={env.get('domain')} gate={env.get('x108_gate')} "
                    f"authority={env.get('decision_authority')} emits_act={env.get('emits_act')}"
                )
            else:
                print(f"⚠️ [BANK] API error: {res.status_code} {res.text[:250]}")
        except Exception as e:
            print(f"❌ [BANK] Connection error: {e}")

        time.sleep(10)


if __name__ == "__main__":
    run_normal_bank()
