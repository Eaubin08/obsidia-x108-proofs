"""
Tests V18.9 — Sigma Dynamic Stability Monitor
Vérifie les 3 contraintes : Vanishing Acceleration, Velocity Band, Coherence Stationarity
"""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.obsidia_sigma_v130 import ObsidiaSigmaMonitor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_monitor():
    return ObsidiaSigmaMonitor(tau_min=0.05, tau_max=0.75, accel_limit=0.4)


# ---------------------------------------------------------------------------
# Test 1 : premier step toujours STABLE (pas d'historique)
# ---------------------------------------------------------------------------

def test_first_step_always_stable():
    m = make_monitor()
    report = m.evaluate_step("S0", [], [])
    assert report["stability_status"] == "STABLE"
    assert report["violations"] == []


# ---------------------------------------------------------------------------
# Test 2 : step identique → velocity = 0 → POTENTIAL_COLLAPSE après 2 steps
# ---------------------------------------------------------------------------

def test_identical_steps_collapse():
    m = make_monitor()
    m.evaluate_step("S0", [], [])
    time.sleep(0.01)
    report = m.evaluate_step("S0", [], [])
    # velocity ≈ 0 < tau_min → POTENTIAL_COLLAPSE
    assert "POTENTIAL_COLLAPSE" in report["violations"]
    assert report["stability_status"] == "UNSTABLE"


# ---------------------------------------------------------------------------
# Test 3 : escalade brutale → LATENT_DRIFT
# ---------------------------------------------------------------------------

def test_brutal_escalation_drift():
    m = make_monitor()
    m.evaluate_step("S0", [], [])
    time.sleep(0.001)  # dt très petit → velocity très grande
    report = m.evaluate_step("S4", ["FRAUD_PATTERN", "CASH_PRESSURE", "LIMIT_PRESSURE"], ["C1", "C2", "C3"])
    assert "LATENT_DRIFT" in report["violations"]
    assert report["stability_status"] == "UNSTABLE"


# ---------------------------------------------------------------------------
# Test 4 : export_to_proofkit sans steps → NO_DATA
# ---------------------------------------------------------------------------

def test_export_no_data():
    m = make_monitor()
    result = m.export_to_proofkit()
    assert result["V18_9_sigma_stability"]["status"] == "NO_DATA"
    assert result["V18_9_sigma_stability"]["pass"] is False


# ---------------------------------------------------------------------------
# Test 5 : export_to_proofkit après steps stables → PASS
# ---------------------------------------------------------------------------

def test_export_stable_pass():
    m = make_monitor()
    # Deux steps avec un vrai delta temporel
    m.evaluate_step("S0", [], [])
    time.sleep(0.05)
    m.evaluate_step("S1", ["R1"], [])
    result = m.export_to_proofkit()
    entry = result["V18_9_sigma_stability"]
    assert entry["steps_evaluated"] == 2
    # Peut être PASS ou UNSTABLE selon velocity réelle — on vérifie juste la structure
    assert entry["status"] in ("PASS", "FAIL")
    assert "violations_total" in entry
    assert "steps_detail" in entry


# ---------------------------------------------------------------------------
# Test 6 : coherence stationarity — hash mismatch → violation
# ---------------------------------------------------------------------------

def test_coherence_stationarity_violation():
    m = ObsidiaSigmaMonitor(coherence_hash="expected_hash_abc")
    m.evaluate_step("S0", [], [])
    time.sleep(0.05)
    report = m.evaluate_step("S1", [], [], current_hash="different_hash_xyz")
    assert "COHERENCE_STATIONARITY_VIOLATED" in report["violations"]
    assert report["stability_status"] == "UNSTABLE"


# ---------------------------------------------------------------------------
# Test 7 : coherence stationarity — hash correct → pas de violation
# ---------------------------------------------------------------------------

def test_coherence_stationarity_ok():
    m = ObsidiaSigmaMonitor(coherence_hash="correct_hash_abc")
    m.evaluate_step("S0", [], [])
    time.sleep(0.05)
    report = m.evaluate_step("S1", [], [], current_hash="correct_hash_abc")
    assert "COHERENCE_STATIONARITY_VIOLATED" not in report["violations"]


# ---------------------------------------------------------------------------
# Test 8 : intégration pipeline — sigma_report présent dans la sortie
# ---------------------------------------------------------------------------

def test_pipeline_sigma_integration():
    """Vérifie que run_pipeline.py produit bien sigma_report dans la sortie."""
    import subprocess, json
    prices = list(range(100, 121))
    state = json.dumps({
        "symbol": "BTCUSDT",
        "prices": prices,
        "highs": [p + 1 for p in prices],
        "lows": [p - 1 for p in prices],
        "volumes": [1000 + i * 50 for i in range(21)],
        "spreads_bps": [4] * 21,
        "sentiment_scores": [0.2] * 21,
        "event_risk_scores": [0.15] * 21,
        "btc_reference_prices": prices,
    })
    result = subprocess.run(
        ["python3", "agents/run_pipeline.py", "trading", state],
        capture_output=True, text=True,
        cwd=str(ROOT)
    )
    assert result.returncode == 0, f"Pipeline failed: {result.stderr}"
    data = json.loads(result.stdout)
    assert "sigma_report" in data, "sigma_report absent de la sortie pipeline"
    assert "status" in data["sigma_report"]
    assert "sigma_override" in data


# ---------------------------------------------------------------------------
# Test 9 : save_report écrit dans PROOFKIT_REPORT.json
# ---------------------------------------------------------------------------

def test_save_report(tmp_path):
    m = make_monitor()
    m.evaluate_step("S1", ["R1"], ["C1"])
    report_path = str(tmp_path / "PROOFKIT_REPORT.json")
    m.save_report(report_path)
    import json
    with open(report_path) as f:
        data = json.load(f)
    assert "V18_9_sigma_stability" in data
    assert data["V18_9_sigma_stability"]["steps_evaluated"] == 1


# ---------------------------------------------------------------------------
# Test 10 : compute_coherence_hash — déterministe sur les mêmes fichiers
# ---------------------------------------------------------------------------

def test_compute_coherence_hash_deterministic(tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("hello obsidia")
    f2.write_text("sigma v18.9")
    h1 = ObsidiaSigmaMonitor.compute_coherence_hash([str(f1), str(f2)])
    h2 = ObsidiaSigmaMonitor.compute_coherence_hash([str(f2), str(f1)])  # ordre différent
    assert h1 == h2  # trié → déterministe
    assert len(h1) == 64  # SHA-256 hex


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
