import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def run_example(name: str):
    cmd = [
        sys.executable,
        str(ROOT / "sigma" / "run_pipeline.py"),
        "gps_defense_aviation",
        str(ROOT / "sigma" / "examples" / name),
    ]
    out = subprocess.check_output(cmd, text=True)
    return json.loads(out)

def test_nominal_market_verdict():
    result = run_example("gps_nominal.json")
    assert result["market_verdict"] == "TRAJECTORY_VALID"
    assert result["x108_gate"] == "ALLOW"

def test_no_source_market_verdict():
    result = run_example("gps_no_source.json")
    assert result["market_verdict"] == "RECALC_TRAJECTORY"
    assert result["x108_gate"] == "HOLD"

def test_source_conflict_market_verdict():
    result = run_example("gps_source_conflict.json")
    assert result["market_verdict"] == "ABORT_TRAJECTORY"
    # HISTORICAL ORACLE (commit 7e47d2b2): assert result["x108_gate"] == "BLOCK"
    # Justification réconciliation Phase 5A:
    # 1. En présence d'un conflit de capteurs (source_conflict_score=0.84 >= 0.80) sans dérive critique
    #    (trajectory_drift_score=0.30 < 0.85), le contrat RULE_GPS_SENSOR_FUSION (sigma/contracts.py:130)
    #    spécifie obligation=ObligationDirective.MUST_HOLD (mise en quarantaine / recalcul de trajectoire).
    # 2. Le verdict du domaine reste ABORT_TRAJECTORY, mais la porte souveraine X-108 est HOLD.
    # 3. En cas de dérive critique confirmée (drift >= 0.85), l'invariant impératif INV_GPS_DRIFT_MAX
    #    (MANDATORY_VETO, MUST_BLOCK) s'applique en priorité absolue et impose BLOCK (validé par test_red_5).
    assert result["x108_gate"] == "HOLD"

def test_brownout_market_verdict():
    result = run_example("gps_brownout.json")
    assert result["market_verdict"] == "DEGRADED_NAVIGATION"
    assert result["x108_gate"] == "HOLD"

def test_time_skew_market_verdict():
    result = run_example("gps_time_skew.json")
    assert result["market_verdict"] == "RECALC_TRAJECTORY"
    assert result["x108_gate"] == "HOLD"