import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "hackathons" / "nativebuilder-gps-defense" / "physical_signal_periphery.py"
SAMPLE = ROOT / "hackathons" / "nativebuilder-gps-defense" / "samples" / "synthetic_observation.json"
BENCH = ROOT / "hackathons" / "nativebuilder-gps-defense" / "samples" / "blind_manifest.json"
REAL_RINEX = ROOT / "hackathons" / "nativebuilder-gps-defense" / "data" / "rinex" / "noaa_ab02_2026_210" / "ab022100.26o.gz"
REAL_STATION_LOG = ROOT / "hackathons" / "nativebuilder-gps-defense" / "data" / "rinex" / "noaa_ab02_2026_210" / "ab02.log.txt"


def load_module():
    spec = importlib.util.spec_from_file_location("physical_signal_periphery", MODULE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_synthetic_observation_is_not_eligible_for_physical_claim():
    mod = load_module()
    envelope = mod.load_observation(SAMPLE)
    gate = mod.physical_reality_gate(envelope)

    assert envelope["proof_level"] == "SYNTHETIC_TEST_ONLY"
    assert envelope["eligible_for_physical_claim"] is False
    assert gate.emits_verdict is False
    assert "SYNTHETIC_TEST_ONLY_NOT_PHYSICAL" in gate.reason_codes


def test_physical_observation_can_reach_p3_05_but_remains_claim_bounded():
    mod = load_module()
    result = mod.run_observation(SAMPLE)

    assert result["physical_gate"]["decision_authority"] == "KX108_ONLY"
    assert result["physical_gate"]["emits_verdict"] is False
    assert result["x108_result"]["domain"] == "gps_defense_aviation"
    assert result["x108_result"]["receipt"]["os3_ticket"]["replay_status"] == "NOT_RUN"


def test_live_passive_without_hardware_is_blocked_not_mocked():
    mod = load_module()
    result = mod.run_live_passive()

    assert result["mode"] == "LIVE_PASSIVE_ADAPTER"
    if result["blocked"]:
        assert result["status"] == "NO_HARDWARE_DETECTED"
        assert result["envelope"]["eligible_for_physical_claim"] is False
        assert "NO_HARDWARE_DETECTED" in result["physical_gate"]["reason_codes"]


def test_blind_benchmark_keeps_truth_out_of_pipeline():
    mod = load_module()
    result = mod.run_blind_benchmark(BENCH)

    assert result["mode"] == "BLIND_BENCHMARK"
    assert result["truth_manifest_used_by_pipeline"] is False
    assert result["case_count"] == 1


def test_real_rinex_parser_extracts_noaa_ab02_observations_when_present():
    if not REAL_RINEX.exists():
        return
    mod = load_module()
    parsed = mod.parse_rinex_observation_file(REAL_RINEX, REAL_STATION_LOG)

    assert parsed["header"]["marker_name"] == "AB02"
    assert parsed["epoch_count"] > 0
    assert "G" in parsed["observed_constellations"]
    assert len(parsed["unique_satellites"]) > 0
