from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_p56d_sigma_is_post_guard_veto_only():
    runner = (ROOT / "sigma" / "run_pipeline.py").read_text(encoding="utf-8")

    assert "POST_GUARD_VETO_ONLY" in runner
    assert "Sigma never authorizes" in runner
    assert "Sigma never promotes HOLD/BLOCK to ACT/ALLOW" in runner
    assert '"sigma_authority"] = "VETO_ONLY"' in runner
    assert '"sigma_authority"] = "REPORT_ONLY"' in runner


def test_p56d_sigma_preserves_pre_sigma_decision_trace():
    runner = (ROOT / "sigma" / "run_pipeline.py").read_text(encoding="utf-8")

    assert "pre_sigma_market_verdict" in runner
    assert "pre_sigma_severity" in runner
    assert '"sigma_override_policy"] = "POST_GUARD_VETO_ONLY"' in runner


def test_p56d_sigma_fail_only_downgrades_to_hold_alert():
    runner = (ROOT / "sigma" / "run_pipeline.py").read_text(encoding="utf-8")

    assert 'stability == "FAIL"' in runner
    assert 'result_dict["market_verdict"] = "HOLD_STABILITY_ALERT"' in runner
    assert 'result_dict["severity"] = "S4"' in runner
    assert 'result_dict["sigma_override"] = True' in runner
