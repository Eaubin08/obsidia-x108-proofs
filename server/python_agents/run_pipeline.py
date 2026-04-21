#!/usr/bin/env python3
"""
OS4 Canonical Agent Pipeline CLI Bridge
Usage: python3 run_pipeline.py <domain> <json_state>
Output: JSON CanonicalDecisionEnvelope to stdout
"""
import sys
import json
import dataclasses
from pathlib import Path

# Ensure package is importable
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from python_agents.contracts import TradingState, BankState, EcomState
from python_agents.protocols import run_trading_pipeline, run_bank_pipeline, run_ecom_pipeline

def envelope_to_dict(env) -> dict:
    """Convert CanonicalDecisionEnvelope dataclass to JSON-serializable dict."""
    return dataclasses.asdict(env)

def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: run_pipeline.py <domain> <json_state>"}), file=sys.stderr)
        sys.exit(1)

    domain = sys.argv[1].lower()
    try:
        state_data = json.loads(sys.argv[2])
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON state: {e}"}), file=sys.stderr)
        sys.exit(1)

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

        print(json.dumps(envelope_to_dict(result)))
    except TypeError as e:
        print(json.dumps({"error": f"State construction error: {e}"}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Pipeline error: {e}"}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
