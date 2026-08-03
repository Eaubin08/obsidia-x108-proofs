import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "hackathons" / "nativebuilder-gps-defense" / "rf_attack_benchmark"
REPORT = ROOT / "hackathons" / "nativebuilder-gps-defense" / "RECORDED_RF_ATTACK_REPORT.md"


def load_json(name: str):
    return json.loads((BENCH / name).read_text(encoding="utf-8"))


def test_recorded_rf_attack_manifest_does_not_claim_pass():
    manifest = load_json("dataset_manifest.json")

    assert manifest["status"] == "FGI_HOSTILE_RF_OBTAINED_GNSS_SDR_BLOCKED"
    assert manifest["recorded_rf_attack_pass"] is False
    assert manifest["mocks_used"] is False
    assert manifest["primary_corpus_obtained"]["extracted_l1_e1_sha256_matches_metax"] is True
    assert manifest["receiver_execution"]["gnss_sdr_available"] is False
    assert manifest["proof_level_reached"] == "RECORDED_REAL_RF"
    assert manifest["proof_level_requested"] == "RECORDED_RF_ATTACK"


def test_blind_attack_manifests_keep_truth_out_of_pipeline():
    public_manifest = load_json("blind_input_manifest.json")
    truth_manifest = load_json("private_truth_manifest.json")

    assert public_manifest["status"] == "HOSTILE_RF_AVAILABLE_NOT_EXECUTED_GNSS_SDR_BLOCKED"
    assert public_manifest["cases"] == []
    assert public_manifest["available_but_not_executed_inputs"]
    assert truth_manifest["cases"] == []
    assert public_manifest["truth_manifest_read_before_decisions"] is False
    assert public_manifest["eligible_for_recorded_rf_attack"] is False


def test_metrics_and_receipts_are_not_fabricated():
    metrics = load_json("metrics.json")
    confusion = load_json("confusion_matrix.json")
    decisions = (BENCH / "decisions.jsonl").read_text(encoding="utf-8")

    assert metrics["status"] == "NOT_COMPUTED_GNSS_SDR_BLOCKED_WITH_REAL_HOSTILE_RF"
    assert metrics["receipt_coverage"] == 0
    assert confusion["status"] == "NOT_COMPUTED_GNSS_SDR_BLOCKED_WITH_REAL_HOSTILE_RF"
    assert '"x108_live_called":false' in decisions.replace(" ", "")


def test_report_forbids_overclaiming():
    report = REPORT.read_text(encoding="utf-8")

    assert "Status: `FGI_HOSTILE_RF_OBTAINED_GNSS_SDR_BLOCKED`" in report
    assert "`RECORDED_RF_ATTACK` is **not reached**" in report
    assert "FGI-SpoofRepo" in report
    assert "RESISTANT_TO_SPOOFING" in report
    assert "PRODUCTION" in report


def test_temporal_benchmark_blocks_without_pre_attack_pvt():
    nominal = load_json("nominal_result.json")
    pre_attack = load_json("pre_attack_baseline.json")
    temporal = load_json("temporal_detection_report.json")
    truth = load_json("truth_alignment_report.json")
    compatibility = (BENCH / "receiver_compatibility_report.md").read_text(encoding="utf-8")

    assert nominal["proof_level_reached"] == "BLOCKED_RECEIVER_CONFIGURATION"
    assert nominal["receiver_prerequisite"]["satisfied"] is False
    assert pre_attack["status"] == "PRE_ATTACK_RECEIVER_FAILURE"
    assert pre_attack["receiver_prerequisite_satisfied"] is False
    assert all(run["pvt_position_count"] == 0 for run in pre_attack["runs"])
    assert all(run["nav_message_count"] == 0 for run in pre_attack["runs"])
    assert temporal["status"] == "BLOCKED_RECEIVER_CONFIGURATION"
    assert "loss of lock at 14 s" in temporal["do_not_use_as_attack_evidence"]
    assert truth["alignment_result"] == "NOT_SCORED"
    assert "PRE_ATTACK_RECEIVER_FAILURE" in compatibility
