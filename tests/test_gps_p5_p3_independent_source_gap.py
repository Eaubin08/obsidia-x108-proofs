import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "gps" / "p5_p3_independent_source_gap_assessment.py"

SPEC = importlib.util.spec_from_file_location("p5_p3_independent_source_gap_assessment", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

assess = MODULE.assess


def test_p5_cross_receiver_reproducibility_does_not_close_p3_physical_independence():
    result = assess()

    assert result["classification"] == "CROSS_RECEIVER_REPRODUCIBILITY_NOT_PHYSICAL_INDEPENDENCE"
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["emits_verdict"] is False
    assert result["same_recorded_rf_source"] is True
    assert result["different_receiver_implementations"] is True

    p3 = result["p3"]
    assert p3["p2_live_gnss_verified"] is False
    assert p3["source_independence_proven"] is False
    assert p3["multi_source_corroboration_proven"] is False
    assert p3["causal_attribution_proven"] is False
    assert p3["physical_truth_proven"] is False
    assert "P2_REAL_PASSIVE_GNSS_NOT_VERIFIED" in p3["blockers"]
    assert "INDEPENDENT_PHYSICAL_SOURCE_NOT_PROVEN" in p3["blockers"]
