import json
import subprocess
import sys
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
RUN_PIPELINE = ROOT / "sigma" / "run_pipeline.py"

RANK = {
    "ALLOW": 0,
    "HOLD": 1,
    "BLOCK": 2,
}

def _env():
    e = os.environ.copy()
    e["PYTHONUTF8"] = "1"
    e["PYTHONIOENCODING"] = "utf-8"
    e["PYTHONWARNINGS"] = "ignore"
    return e

def gate_rank(gate: str) -> int:
    return RANK.get(gate, 99)

def load_fixture(name: str) -> dict:
    return json.loads((ROOT / "sigma" / "examples" / name).read_text(encoding="utf-8"))

def run_payload(payload: dict) -> dict:
    p = subprocess.run(
        [sys.executable, str(RUN_PIPELINE), "bank", json.dumps(payload)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=20,
        env=_env(),
    )
    assert p.returncode == 0, f"STDERR:\\n{p.stderr}\\nPAYLOAD:\\n{json.dumps(payload, indent=2)}"
    return json.loads(p.stdout)

def assert_core_fields(d: dict):
    assert "x108_gate" in d
    assert "decision_id" in d
    assert "trace_id" in d
    assert "attestation_ref" in d
    assert "sigma_report" in d
    assert d["sigma_report"]["pass"] is True

def test_canonical_baselines():
    normal = run_payload(load_fixture("bank_normal.json"))
    suspicious = run_payload(load_fixture("bank_suspicious.json"))
    blocked = run_payload(load_fixture("bank_blocked.json"))

    assert normal["x108_gate"] == "ALLOW", normal
    assert suspicious["x108_gate"] in ("HOLD", "BLOCK"), suspicious
    assert blocked["x108_gate"] == "BLOCK", blocked
    assert blocked["severity"] == "S4", blocked

    assert_core_fields(normal)
    assert_core_fields(suspicious)
    assert_core_fields(blocked)

@pytest.mark.parametrize("elapsed_s", [2.0, 5.0, 20.0, 60.0, 107.0])
def test_temporal_immaturity_does_not_soften(elapsed_s):
    base = load_fixture("bank_suspicious.json")
    immature = dict(base)
    mature = dict(base)

    immature["elapsed_s"] = elapsed_s
    mature["elapsed_s"] = max(base["min_required_elapsed_s"] + 20.0, 180.0)

    d_immature = run_payload(immature)
    d_mature = run_payload(mature)

    assert gate_rank(d_immature["x108_gate"]) >= gate_rank(d_mature["x108_gate"]), {
        "elapsed_s": elapsed_s,
        "immature": d_immature,
        "mature": d_mature,
    }

@pytest.mark.parametrize(
    "field,safe_value,risky_value",
    [
        ("fraud_score", 0.02, 0.95),
        ("behavior_shift_score", 0.05, 0.95),
        ("identity_mismatch_score", 0.01, 0.95),
        ("narrative_conflict_score", 0.01, 0.95),
        ("urgency_score", 0.05, 0.95),
        ("recent_failed_attempts", 0, 8),
    ],
)
def test_risk_escalation_does_not_soften(field, safe_value, risky_value):
    base = load_fixture("bank_normal.json")
    low = dict(base)
    high = dict(base)

    low[field] = safe_value
    high[field] = risky_value

    d_low = run_payload(low)
    d_high = run_payload(high)

    assert gate_rank(d_high["x108_gate"]) >= gate_rank(d_low["x108_gate"]), {
        "field": field,
        "low": d_low,
        "high": d_high,
    }

def test_trust_degradation_does_not_soften():
    base = load_fixture("bank_normal.json")

    strong = dict(base)
    strong["counterparty_known"] = True
    strong["counterparty_age_days"] = 240
    strong["device_trust_score"] = 0.98

    weak = dict(base)
    weak["counterparty_known"] = False
    weak["counterparty_age_days"] = 0
    weak["device_trust_score"] = 0.02

    d_strong = run_payload(strong)
    d_weak = run_payload(weak)

    assert gate_rank(d_weak["x108_gate"]) >= gate_rank(d_strong["x108_gate"]), {
        "strong": d_strong,
        "weak": d_weak,
    }

def test_output_integrity_on_canonical_cases():
    for name in ("bank_normal.json", "bank_suspicious.json", "bank_blocked.json"):
        d = run_payload(load_fixture(name))
        assert_core_fields(d)
        assert d["metrics"]["deterministic"] is True
        assert d["metrics"]["proof_ready"] is True

def test_24_case_batch_reproducibility():
    base = load_fixture("bank_normal.json")
    elapsed_values = [2.0, 20.0, 60.0, 108.0]
    fraud_values = [0.05, 0.40, 0.85]
    trust_values = [0.98, 0.35]

    count = 0
    for elapsed_s in elapsed_values:
        for fraud_score in fraud_values:
            for device_trust_score in trust_values:
                payload = dict(base)
                payload["elapsed_s"] = elapsed_s
                payload["fraud_score"] = fraud_score
                payload["device_trust_score"] = device_trust_score
                payload["counterparty_known"] = device_trust_score >= 0.5
                payload["counterparty_age_days"] = 240 if payload["counterparty_known"] else 0

                d = run_payload(payload)
                assert_core_fields(d)
                assert d["metrics"]["deterministic"] is True
                count += 1

    assert count == 24