from pathlib import Path

from scripts.gps.p6_prepare_heldout_candidate import prepare_candidate, sha256_file


def test_prepare_candidate_hides_source_filename(tmp_path: Path):
    source = tmp_path / "SS-33 obvious spoof label.bin"
    source.write_bytes(b"abc123")

    out = prepare_candidate(source, tmp_path / "opaque")

    assert out["status"] == "OPAQUE_CANDIDATE_PREPARED_NOT_ADMITTED"
    assert out["truth_or_reference_present"] is False
    assert out["truth_or_reference_visible_to_classifier"] is False
    assert out["reference_condition"] is None
    assert "spoof" not in out["classifier_input_path"].lower()
    assert "ss-33" not in out["classifier_input_path"].lower()
    assert out["rf_artifact_sha256"] == sha256_file(source)
    assert out["decision_authority"] == "KX108_ONLY"


def test_prepare_candidate_is_stable_for_same_bytes(tmp_path: Path):
    source = tmp_path / "clear-sky.bin"
    source.write_bytes(b"same")

    first = prepare_candidate(source, tmp_path / "opaque")
    second = prepare_candidate(source, tmp_path / "opaque")

    assert first["opaque_case_id"] == second["opaque_case_id"]
    assert first["rf_artifact_sha256"] == second["rf_artifact_sha256"]
    assert second["link_mode"] == "EXISTING_MATCH"
