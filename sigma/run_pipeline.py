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

from sigma.contracts import TradingState, BankState, EcomState
from sigma.protocols import run_trading_pipeline, run_bank_pipeline, run_ecom_pipeline
from sigma.obsidia_sigma_v130 import ObsidiaSigmaMonitor


def load_state(arg: str) -> dict:
    p = Path(arg)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return json.loads(arg)


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
            state = BankState(**state_data)
            result = run_bank_pipeline(state)
        elif domain == "ecom":
            state = EcomState(**state_data)
            result = run_ecom_pipeline(state)
        else:
            print(json.dumps({"error": f"Unknown domain: {domain}. Use trading|bank|ecom"}), file=sys.stderr)
            sys.exit(1)

        result_dict = envelope_to_dict(result)
        result_dict = apply_sigma(result_dict, sigma)
        print(json.dumps(result_dict, ensure_ascii=False))
    except TypeError as e:
        print(json.dumps({"error": f"State construction error: {e}"}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Pipeline error: {e}"}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()