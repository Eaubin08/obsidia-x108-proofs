import requests
import time
import random

def run_normal_bank():
    url = "http://localhost:3001/kernel/ragnarok"
    print("🏦 [BANK-FULL] Lancement du flux certifié...")

    while True:
        payload = {
            "domain": "bank",
            "state": {
                "account_balance": 5000.0,
                "affordability_score": 85,
                "amount": round(random.uniform(10, 500), 2),
                "available_cash": 4500.0,
                "behavior_shift_score": 0,
                "channel": "MOBILE",
                "counterparty_age_days": 365,
                "counterparty_known": True,
                "device_trust_score": 98,
                "fraud_score": 2,
                "historical_avg_amount": 150.0,
                "identity_mismatch_score": 0,
                "narrative_conflict_score": 0,
                "policy_limit": 1000.0,
                "transaction_type": "TRANSFER",
                "urgency_score": 5
            }
        }

        try:
            res = requests.post(url, json=payload, timeout=10)
            if res.status_code == 200:
                print(f"✅ [BANK] Transaction validée : {payload['state']['amount']}€")
            else:
                print(f"⚠️ [BANK] Erreur Kernel : {res.text}")
        except Exception as e:
            print(f"❌ [BANK] Erreur : {e}")

        time.sleep(10)

if __name__ == "__main__":
    run_normal_bank()