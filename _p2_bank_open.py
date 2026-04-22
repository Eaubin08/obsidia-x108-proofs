from pathlib import Path
import json

X = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs")

def w(rel_path: str, content: str):
    p = X / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

bank_blocked = {
    "transaction_type": "transfer",
    "amount": 90000.0,
    "channel": "web",
    "counterparty_known": False,
    "counterparty_age_days": 0,
    "account_balance": 95000.0,
    "available_cash": 94000.0,
    "historical_avg_amount": 150.0,
    "behavior_shift_score": 0.99,
    "fraud_score": 0.99,
    "policy_limit": 1000.0,
    "affordability_score": 0.02,
    "urgency_score": 0.99,
    "identity_mismatch_score": 0.98,
    "narrative_conflict_score": 0.97,
    "device_trust_score": 0.01,
    "recent_failed_attempts": 8,
    "elapsed_s": 2.0,
    "min_required_elapsed_s": 108.0
}

w("sigma/examples/bank_blocked.json", json.dumps(bank_blocked, indent=2))

p2_scope = """# P2 Bank Scope

## Status

P2 BANK OPENING

## Purpose

P2 Bank opens the first governed business world on top of the closed public P1 perimeter.

The source material for this opening is explicitly transplanted in:
- `docs/sources/Obsidia-lab-trad/X108_STANDARD.md`
- `docs/sources/obsidia-engine-proof-core/REAL_CASES.md`
- `docs/sources/bank-robo/README.md`
- `docs/sources/bank-robo/bankingEngine.ts`

## What P2 Bank shows

P2 Bank shows that the public perimeter can expose a first governed banking world with:
- structured bank inputs
- governed outputs
- X-108 gate reading
- trace and attestation fields
- public Sigma interpretation

## What P2 Bank does not claim

P2 Bank does not claim:
- a full production banking system
- a licensed banking platform
- a final institutional cockpit
- full proprietary engine publication
- complete business deployment

## Canonical reading rule

Read P2 Bank in this order:
1. business context
2. `x108_gate`
3. `severity`
4. `reason_code`
5. trace / attestation
6. Sigma stability

The sovereign field is:
- `x108_gate`

The business-facing field is:
- `market_verdict`

If the two appear softer/harder than each other, the sovereign reading remains `x108_gate`.

## Public entry points

- `python .\\sigma\\run_pipeline.py bank .\\sigma\\examples\\bank_normal.json`
- `python .\\sigma\\run_pipeline.py bank .\\sigma\\examples\\bank_suspicious.json`
- `python .\\sigma\\run_pipeline.py bank .\\sigma\\examples\\bank_blocked.json`
- `python -W ignore -m pytest .\\sigma\\tests\\test_bank_world.py -v`

## Files added by P2 Bank opening

- `docs/P2_BANK_SCOPE.md`
- `docs/BANK_SCENARIOS.md`
- `docs/BANK_OUTPUTS.md`
- `sigma/examples/bank_blocked.json`
- `sigma/tests/test_bank_world.py`

## Closure target

P2 Bank is structurally open when:
- 3 canonical bank scenarios exist
- the reader can understand the outputs
- the reader can reproduce the scenarios locally
- the world is readable without oral explanation
"""
w("docs/P2_BANK_SCOPE.md", p2_scope)

bank_scenarios = """# Bank Scenarios

## Purpose

This file defines the canonical P2 Bank scenarios using the current public bank schema.

## Source anchors

These scenarios are derived from:
- `docs/sources/obsidia-engine-proof-core/REAL_CASES.md`
- `docs/sources/bank-robo/README.md`
- `docs/sources/bank-robo/bankingEngine.ts`

## Scenario 1 — Normal

File:
- `sigma/examples/bank_normal.json`

Profile:
- known counterparty
- mature elapsed time
- low contradiction profile
- low fraud profile

Expected reading:
- direct path admissible
- `x108_gate = ALLOW`
- Sigma stable

## Scenario 2 — Suspicious

File:
- `sigma/examples/bank_suspicious.json`

Profile:
- immature elapsed time
- high contradiction pressure
- high fraud pressure
- unstable trust profile

Expected reading:
- no direct authorization path
- current validated public build should not return `ALLOW`
- Sigma stable

## Scenario 3 — Blocked Hard

File:
- `sigma/examples/bank_blocked.json`

Profile:
- extreme contradiction profile
- extreme fraud pressure
- near-zero trust profile
- extreme temporal immaturity
- strongest public refusal profile in P2 Bank

Expected reading:
- `x108_gate = BLOCK`
- `severity = S4`
- Sigma stable

## Reading discipline

Do not reduce the interpretation to `market_verdict` alone.
The sovereign interpretation remains:
- `x108_gate`
"""
w("docs/BANK_SCENARIOS.md", bank_scenarios)

bank_outputs = """# Bank Outputs

## Purpose

This file explains how to read the public outputs of P2 Bank.

## Core fields

### `market_verdict`
Business-facing reading.

Typical values in public bank runs:
- `AUTHORIZE`
- `ANALYZE`

### `x108_gate`
Sovereign governance reading.

Typical values:
- `ALLOW`
- `HOLD`
- `BLOCK`

This is the primary field.

### `reason_code`
Compact explanation of the exposed decision path.

### `severity`
Severity class of the case.

### `decision_id`
Public decision identifier.

### `trace_id`
Public trace identifier.

### `ticket_required`
Whether a controlled ticket path is required.

### `ticket_id`
Ticket reference when present.

### `attestation_ref`
Attestation reference exposed by the public path.

### `sigma_report`
Public Sigma stability output.

## Interpretation hierarchy

Read in this order:
1. `x108_gate`
2. `severity`
3. `reason_code`
4. `market_verdict`
5. `decision_id`
6. `trace_id`
7. `attestation_ref`
8. `sigma_report`

## Critical rule

If `market_verdict` appears softer than the sovereign reading, the canonical interpretation remains:
- `x108_gate`

## Practical reading

### Normal case
- gate allows
- low severity
- trace present
- Sigma stable

### Suspicious case
- direct path must not be freely admissible
- elevated severity or contradiction pressure
- Sigma stable

### Blocked hard case
- sovereign block
- S4 severity
- strongest public refusal profile in P2 Bank
"""
w("docs/BANK_OUTPUTS.md", bank_outputs)

test_bank_world = r'''import json
import subprocess
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

def _env():
    e = os.environ.copy()
    e["PYTHONUTF8"] = "1"
    e["PYTHONIOENCODING"] = "utf-8"
    e["PYTHONWARNINGS"] = "ignore"
    return e

def _run_case(filename: str):
    p = subprocess.run(
        [sys.executable, str(ROOT / "sigma" / "run_pipeline.py"), "bank", str(ROOT / "sigma" / "examples" / filename)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=20,
        env=_env(),
    )
    assert p.returncode == 0, f"{filename}\nSTDERR:\n{p.stderr}"
    return json.loads(p.stdout)

def test_bank_normal_allow():
    d = _run_case("bank_normal.json")
    assert d["x108_gate"] == "ALLOW", d
    assert d["sigma_report"]["pass"] is True
    assert d["metrics"]["deterministic"] is True

def test_bank_suspicious_not_allow():
    d = _run_case("bank_suspicious.json")
    assert d["x108_gate"] in ("HOLD", "BLOCK"), d
    assert d["sigma_report"]["pass"] is True

def test_bank_blocked_hard_block():
    d = _run_case("bank_blocked.json")
    assert d["x108_gate"] == "BLOCK", d
    assert d["severity"] == "S4", d
    assert d["sigma_report"]["pass"] is True
    assert d["metrics"]["deterministic"] is True

def test_bank_outputs_present():
    d = _run_case("bank_normal.json")
    assert "decision_id" in d
    assert "trace_id" in d
    assert "attestation_ref" in d
    assert "sigma_report" in d

def test_bank_all_sigma_pass():
    for f in ("bank_normal.json", "bank_suspicious.json", "bank_blocked.json"):
        d = _run_case(f)
        assert d["sigma_report"]["pass"] is True, f
'''
w("sigma/tests/test_bank_world.py", test_bank_world)

print("OK")
for rel in [
    "sigma/examples/bank_blocked.json",
    "docs/P2_BANK_SCOPE.md",
    "docs/BANK_SCENARIOS.md",
    "docs/BANK_OUTPUTS.md",
    "sigma/tests/test_bank_world.py",
]:
    print(rel, "OK" if (X / rel).exists() else "MISSING")