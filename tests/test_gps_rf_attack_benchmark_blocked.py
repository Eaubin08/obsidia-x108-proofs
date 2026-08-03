import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "hackathons" / "nativebuilder-gps-defense" / "rf_attack_benchmark"
REPORT = ROOT / "hackathons" / "nativebuilder-gps-defense" / "RECORDED_RF_ATTACK_REPORT.md"


def load_json(name: str):
    return json.loads((BENCH / name).read_text(encoding="utf-8"))


def test_recorded_rf_attack_manifest_does_not_claim_pass():
    manifest = load_json("dataset_manifest.json")

    assert manifest["status"] == "FGI_HOSTILE_RF_PARTIAL_CHAIN_NO_PVT"
    assert manifest["recorded_rf_attack_pass"] is False
    assert manifest["mocks_used"] is False
    assert manifest["primary_corpus_obtained"]["extracted_l1_e1_sha256_matches_metax"] is True
    assert manifest["receiver_execution"]["gnss_sdr_version"] == "0.0.21.git-next-2a7214a4f"
    assert manifest["receiver_execution"]["runs"][-1]["result"] == "TRACKING_OBSERVABLES_NO_NAV_NO_PVT_X108_HOLD"
    assert manifest["proof_level_reached"] == "RECORDED_REAL_RF_HOSTILE_PARTIAL_CHAIN"
    assert manifest["proof_level_requested"] == "RECORDED_RF_ATTACK"


def test_blind_attack_manifests_keep_truth_out_of_pipeline():
    public_manifest = load_json("blind_input_manifest.json")
    truth_manifest = load_json("private_truth_manifest.json")

    assert public_manifest["status"] == "EXECUTED_WITH_OPAQUE_INPUT_NO_PVT"
    assert public_manifest["cases"][0]["case_id"] == "case_0001_l1e1_real8"
    assert public_manifest["cases"][0]["truth_label_visible_to_pipeline"] is False
    assert truth_manifest["status"] == "EXECUTED_OPAQUE_CASE_LABELS_NOT_COMMITTED"
    assert truth_manifest["cases"] == []
    assert public_manifest["truth_manifest_read_before_decisions"] is False
    assert public_manifest["eligible_for_recorded_rf_attack"] is False


def test_metrics_and_receipts_are_not_fabricated():
    metrics = load_json("metrics.json")
    confusion = load_json("confusion_matrix.json")
    decisions = (BENCH / "decisions.jsonl").read_text(encoding="utf-8")

    assert metrics["status"] == "PARTIAL_COMPUTED_NO_PVT_NO_ATTACK_CLASSIFICATION"
    assert metrics["x108_governance_decision"] == "HOLD"
    assert metrics["receipt_coverage"] == 1
    assert metrics["detection_delay_seconds"] is None
    assert confusion["status"] == "NOT_COMPUTED_NO_NOMINAL_PAIR_NO_PVT_NO_ATTACK_CLASSIFICATION"
    assert '"x108_live_called":true' in decisions.replace(" ", "")
    assert '"x108_verdict":"HOLD"' in decisions.replace(" ", "")


def test_report_forbids_overclaiming():
    report = REPORT.read_text(encoding="utf-8")

    assert "Status: `FGI_HOSTILE_RF_FULL_CHAIN_NO_PVT`" in report
    assert "`RECORDED_RF_ATTACK` is **not reached**" in report
    assert "FGI-SpoofRepo" in report
    assert "no NAV messages and no PVT solution" in report
    assert "RESISTANT_TO_SPOOFING" in report
    assert "PRODUCTION" in report
