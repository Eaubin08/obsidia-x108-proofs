#!/usr/bin/env python3
"""
OS4 Canonical Agent Pipeline CLI Bridge — P1 public
Usage:
  python sigma/run_pipeline.py <domain> <json_state_or_json_file>
"""
import sys
import json
import dataclasses
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sigma.contracts import TradingState, BankState, EcomState, GpsDefenseAviationState
from sigma.protocols import run_trading_pipeline, run_bank_pipeline, run_ecom_pipeline, run_gps_defense_aviation_pipeline
from sigma.obsidia_sigma_v130 import ObsidiaSigmaMonitor


REQUIRED_BANK_FIELDS = {
    "transaction_type",
    "amount",
    "channel",
    "counterparty_known",
    "counterparty_age_days",
    "account_balance",
    "available_cash",
    "historical_avg_amount",
    "behavior_shift_score",
    "fraud_score",
    "policy_limit",
    "affordability_score",
    "urgency_score",
    "identity_mismatch_score",
    "narrative_conflict_score",
    "device_trust_score",
}

ALLOWED_BANK_FIELDS = {f.name for f in dataclasses.fields(BankState)}


def load_state(arg: str) -> dict:
    p = Path(arg)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return json.loads(arg)


def validate_bank_payload(state_data: dict) -> None:
    if not isinstance(state_data, dict):
        raise ValueError("Bank payload must be a JSON object")

    missing = sorted(REQUIRED_BANK_FIELDS - set(state_data.keys()))
    if missing:
        raise ValueError(f"Missing required bank fields: {', '.join(missing)}")

    unknown = sorted(set(state_data.keys()) - ALLOWED_BANK_FIELDS)
    if unknown:
        raise ValueError(f"Unknown bank fields: {', '.join(unknown)}")


def apply_sigma(result_dict: dict, sigma: ObsidiaSigmaMonitor) -> dict:
    step_report = sigma.evaluate_step(
        severity=result_dict.get("severity", "S0"),
        risks=result_dict.get("risk_flags", []),
        contras=result_dict.get("contradictions", []),
    )
    sigma_report = sigma.export_to_proofkit()
    stability = sigma_report["V18_9_sigma_stability"]["status"]

    if stability == "FAIL":
        result_dict["market_verdict"] = "HOLD_STABILITY_ALERT"
        result_dict["severity"] = "S4"
        result_dict["sigma_override"] = True
    else:
        result_dict["sigma_override"] = False

    result_dict["sigma_step"] = step_report
    result_dict["sigma_report"] = sigma_report["V18_9_sigma_stability"]
    return result_dict


def envelope_to_dict(env) -> dict:
    return dataclasses.asdict(env)


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: run_pipeline.py <domain> <json_state_or_json_file>"}), file=sys.stderr)
        sys.exit(1)

    domain = sys.argv[1].lower()
    try:
        state_data = load_state(sys.argv[2])
    except Exception as e:
        print(json.dumps({"error": f"Invalid JSON input: {e}"}), file=sys.stderr)
        sys.exit(1)

    sigma = ObsidiaSigmaMonitor(config_path=str(ROOT / "sigma" / "sigma_config.json"))

    try:
        if domain == "trading":
            state = TradingState(**state_data)
            result = run_trading_pipeline(state)
        elif domain == "bank":
            validate_bank_payload(state_data)
            state = BankState(**state_data)
            result = run_bank_pipeline(state)
        elif domain == "ecom":
            state = EcomState(**state_data)
            result = run_ecom_pipeline(state)
        elif domain == "gps_defense_aviation":
            state = GpsDefenseAviationState(**state_data)
            result = run_gps_defense_aviation_pipeline(state)
        else:
            print(json.dumps({"error": f"Unknown domain: {domain}. Use trading|bank|ecom|gps_defense_aviation"}), file=sys.stderr)
            sys.exit(1)

        result_dict = envelope_to_dict(result)
        result_dict = apply_sigma(result_dict, sigma)
        print(json.dumps(result_dict, ensure_ascii=False))
    except (TypeError, ValueError) as e:
        print(json.dumps({"error": f"State validation error: {e}"}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Pipeline error: {e}"}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()