import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = (
    ROOT
    / "hackathons"
    / "nativebuilder-gps-defense"
    / "rf_attack_benchmark"
    / "p6_first_heldout_pair_reservation_v0.json"
)


def _load():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_first_pair_is_reserved_but_not_admitted():
    m = _load()
    assert m["status"] == "PAIR_RESERVED_NOT_DOWNLOADED_NOT_ADMITTED"
    assert m["pair_ready_for_download"] is True
    assert m["pair_ready_for_matrix"] is False
    assert m["certification_status"] == "NOT_CERTIFIED"


def test_positive_is_ss33_and_still_sealed_from_classifier_path():
    p = _load()["positive_reservation"]
    assert p["reservation_id"] == "TUNI2025_POSITIVE_SS33"
    assert p["zenodo_record_id"] == "15624648"
    assert p["source_md5_public"] == "2320ab15af06dd66bfe459094e24381e"
    assert p["classifier_facing_name"] is None
    assert p["rf_artifact_sha256"] is None
    assert p["downloaded"] is False
    assert p["classifier_executed"] is False
    assert p["reference_unsealed"] is False
    assert p["admitted"] is False


def test_negative_is_c5_and_still_sealed_from_classifier_path():
    n = _load()["negative_reservation"]
    assert n["reservation_id"] == "TUNI2025_NEGATIVE_C5"
    assert n["zenodo_record_id"] == "15572976"
    assert n["source_md5_public"] == "a03dedd79ac4208f6d60b4c916484dba"
    assert n["classifier_facing_name"] is None
    assert n["rf_artifact_sha256"] is None
    assert n["downloaded"] is False
    assert n["classifier_executed"] is False
    assert n["reference_unsealed"] is False
    assert n["admitted"] is False


def test_pair_preserves_kx108_and_no_authority():
    m = _load()
    assert m["decision_authority"] == "KX108_ONLY"
    assert m["allowed_to_decide"] is False
    assert m["allowed_to_act"] is False
    assert m["emits_act"] is False
    assert m["emits_verdict"] is False
    assert m["kernel_mutation"] is False
    assert m["x108_mutation"] is False
