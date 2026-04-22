import json
import subprocess
import sys
import os
from pathlib import Path

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
        timeout=25,
        env=_env(),
    )
    assert p.returncode == 0, f"STDERR:\n{p.stderr}\nPAYLOAD:\n{json.dumps(payload, indent=2)}"
    return json.loads(p.stdout)

def assert_core(d: dict):
    assert "x108_gate" in d
    assert "decision_id" in d
    assert "trace_id" in d
    assert "attestation_ref" in d
    assert "sigma_report" in d
    assert d["sigma_report"]["pass"] is True
    assert d["metrics"]["deterministic"] is True

def test_repeatability_same_normal_profile_keeps_same_sovereign_reading():
    payload = load_fixture("bank_normal.json")
    outputs = [run_payload(payload) for _ in range(8)]

    gates = {d["x108_gate"] for d in outputs}
    severities = {d["severity"] for d in outputs}
    reasons = {d["reason_code"] for d in outputs}

    assert gates == {"ALLOW"}
    assert len(severities) == 1
    assert len(reasons) == 1

    for d in outputs:
        assert_core(d)

def test_suspicious_boundary_never_softens_before_and_around_maturity():
    base = load_fixture("bank_suspicious.json")
    values = [2.0, 5.0, 20.0, 60.0, 107.0, 108.0, 109.0, 140.0]
    results = []

    for elapsed_s in values:
        p = dict(base)
        p["elapsed_s"] = elapsed_s
        d = run_payload(p)
        assert_core(d)
        results.append((elapsed_s, d["x108_gate"]))

    ranks = {elapsed: gate_rank(gate) for elapsed, gate in results}

    assert ranks[2.0] >= ranks[140.0]
    assert ranks[5.0] >= ranks[109.0]
    assert ranks[20.0] >= ranks[108.0]
    assert ranks[107.0] >= ranks[109.0]

def test_fraud_ladder_on_normal_profile_never_softens():
    base = load_fixture("bank_normal.json")
    ladder = [0.02, 0.10, 0.30, 0.60, 0.90]
    ranks = []

    for fraud_score in ladder:
        p = dict(base)
        p["fraud_score"] = fraud_score
        d = run_payload(p)
        assert_core(d)
        ranks.append(gate_rank(d["x108_gate"]))

    assert ranks == sorted(ranks)

def test_trust_ladder_on_normal_profile_never_softens():
    base = load_fixture("bank_normal.json")
    ladder = [0.99, 0.80, 0.50, 0.20, 0.02]
    ranks = []

    for trust in ladder:
        p = dict(base)
        p["device_trust_score"] = trust
        p["counterparty_known"] = trust >= 0.5
        p["counterparty_age_days"] = 240 if trust >= 0.5 else 0
        d = run_payload(p)
        assert_core(d)
        ranks.append(gate_rank(d["x108_gate"]))

    assert ranks == sorted(ranks)

def test_identity_mismatch_ladder_never_softens():
    base = load_fixture("bank_normal.json")
    ladder = [0.01, 0.10, 0.30, 0.70, 0.95]
    ranks = []

    for mismatch in ladder:
        p = dict(base)
        p["identity_mismatch_score"] = mismatch
        d = run_payload(p)
        assert_core(d)
        ranks.append(gate_rank(d["x108_gate"]))

    assert ranks == sorted(ranks)

def test_combined_high_pressure_profile_is_never_allow():
    p = load_fixture("bank_suspicious.json")
    p["amount"] = 75000.0
    p["historical_avg_amount"] = 120.0
    p["fraud_score"] = 0.97
    p["behavior_shift_score"] = 0.95
    p["urgency_score"] = 0.98
    p["identity_mismatch_score"] = 0.94
    p["narrative_conflict_score"] = 0.93
    p["device_trust_score"] = 0.03
    p["recent_failed_attempts"] = 8
    p["elapsed_s"] = 6.0
    p["counterparty_known"] = False
    p["counterparty_age_days"] = 0

    d = run_payload(p)
    assert_core(d)
    assert d["x108_gate"] in ("HOLD", "BLOCK")
    assert d["x108_gate"] != "ALLOW"

def test_adversarial_mini_batch_18_cases():
    base_normal = load_fixture("bank_normal.json")
    base_suspicious = load_fixture("bank_suspicious.json")
    cases = []

    for fraud_score in [0.02, 0.20, 0.60]:
        for trust in [0.98, 0.40, 0.05]:
            p = dict(base_normal)
            p["fraud_score"] = fraud_score
            p["device_trust_score"] = trust
            p["counterparty_known"] = trust >= 0.5
            p["counterparty_age_days"] = 240 if trust >= 0.5 else 0
            cases.append(p)

    for elapsed_s in [2.0, 20.0, 107.0]:
        for mismatch in [0.40, 0.75, 0.95]:
            p = dict(base_suspicious)
            p["elapsed_s"] = elapsed_s
            p["identity_mismatch_score"] = mismatch
            cases.append(p)

    assert len(cases) == 18

    seen = 0
    for payload in cases:
        d = run_payload(payload)
        assert_core(d)
        seen += 1

    assert seen == 18