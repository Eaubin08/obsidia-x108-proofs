import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "gps" / "p5_reference_truth_support.py"
INPUT_PATH = (
    ROOT
    / "hackathons"
    / "nativebuilder-gps-defense"
    / "rf_attack_benchmark"
    / "p5_reference_truth_input_v0.json"
)

SPEC = importlib.util.spec_from_file_location("p5_reference_truth_support", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

assess = MODULE.assess


def test_p5_reference_truth_supports_pre_stable_post_displaced():
    payload = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    result = assess(payload)

    assert result["classification"] == "REFERENCE_TRUTH_SUPPORTS_PRE_STABLE_POST_DISPLACED"
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["emits_verdict"] is False
    assert result["p3_independent_physical_source_proven"] is False
    assert result["causal_attribution_closed"] is False

    assert result["checks"]["pre_onset_receivers_close_to_reference"] is True
    assert result["checks"]["post_onset_receivers_far_from_reference"] is True

    assert result["results"]["gnss_sdr_pre"]["distance_to_stationary_reference_m"] < 20.0
    assert result["results"]["gsrx_pre"]["distance_to_stationary_reference_m"] < 20.0
    assert result["results"]["gnss_sdr_post"]["distance_to_stationary_reference_m"] > 14000.0
    assert result["results"]["gsrx_post"]["distance_to_stationary_reference_m"] > 14000.0
