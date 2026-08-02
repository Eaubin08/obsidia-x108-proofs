import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "hackathons" / "nativebuilder-gps-defense" / "rf_attack_benchmark"
REPORT = ROOT / "hackathons" / "nativebuilder-gps-defense" / "RECORDED_RF_ATTACK_REPORT.md"


def load_json(name: str):
    return json.loads((BENCH / name).read_text(encoding="utf-8"))


def test_recorded_rf_attack_manifest_does_not_claim_pass():
    manifest = load_json("dataset_manifest.json")

    assert manifest["status"] == "BLOCKED_RECORDED_RF_ATTACK"
    assert manifest["recorded_rf_attack_pass"] is False
    assert manifest["mocks_used"] is False
    assert manifest["proof_level_reached"] == "RECORDED_REAL_RF"
    assert manifest["proof_level_requested"] == "RECORDED_RF_ATTACK"


def test_blind_attack_manifests_contain_no_executed_or_labeled_cases():
    public_manifest = load_json("blind_input_manifest.json")
    truth_manifest = load_json("private_truth_manifest.json")

    assert public_manifest["cases"] == []
    assert truth_manifest["cases"] == []
    assert public_manifest["truth_manifest_read_before_decisions"] is False
    assert public_manifest["eligible_for_recorded_rf_attack"] is False


def test_metrics_and_receipts_are_not_fabricated():
    metrics = load_json("metrics.json")
    confusion = load_json("confusion_matrix.json")
    decisions = (BENCH / "decisions.jsonl").read_text(encoding="utf-8")

    assert metrics["status"] == "NOT_COMPUTED_NO_EXECUTED_CASES"
    assert metrics["receipt_coverage"] == 0
    assert confusion["status"] == "NOT_COMPUTED_NO_EXECUTED_CASES"
    assert '"x108_live_called":false' in decisions.replace(" ", "")


def test_report_forbids_overclaiming():
    report = REPORT.read_text(encoding="utf-8")

    assert "Status: `BLOCKED_RECORDED_RF_ATTACK`" in report
    assert "`RECORDED_RF_ATTACK` is **not reached**" in report
    assert "RESISTANT_TO_SPOOFING" in report
    assert "PRODUCTION" in report
